"""
Web Search Service — Search articles, documentation, and tutorials.

Uses Google Custom Search API or Bing Search API as primary.
Falls back to DuckDuckGo (free, no API key required) when no keys configured.
"""
from typing import List, Dict
from urllib.parse import urlparse

import requests

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class WebSearchService:
    def __init__(self):
        self.google_api_key = getattr(settings, "GOOGLE_SEARCH_API_KEY", None)
        self.google_cx = getattr(settings, "GOOGLE_SEARCH_CX", None)
        self.bing_api_key = getattr(settings, "BING_SEARCH_API_KEY", None)
        self._google_circuit_open = False  # Circuit Breaker

    # ── public ───────────────────────────────────────────────────
    def search_tutorials(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for tutorials and articles.

        Priority: Google → Bing → DuckDuckGo (free fallback).
        Circuit Breaker: skip Google if it returned 403/429 previously.
        """
        if self.google_api_key and self.google_cx and not self._google_circuit_open:
            return self._search_google(query, max_results)
        if self.bing_api_key:
            return self._search_bing(query, max_results)
        # Free fallback: DuckDuckGo (no API key required)
        return self._search_duckduckgo(query, max_results)

    # ── Blocked domains — never educational ─────────────────────
    _BLOCKED_DOMAINS = frozenset({
        "wikipedia.org", "en.wikipedia.org",
        "pinterest.com", "pinterest.co.uk",
        "quora.com",
        "reddit.com",   # too noisy for learning resources
        "facebook.com", "twitter.com", "x.com",
        "instagram.com", "tiktok.com",
        "amazon.com",   # product pages, not tutorials
        "ebay.com",
        "bing.com",     # tracking redirects
    })

    _MAX_SNIPPET_LEN = 300

    def search_courses(
        self, topic: str, max_results: int = 2, experience_level: str = ""
    ) -> List[Dict]:
        """Smart search for real courses + official documentation.

        Strategy — ordered by quality:
        1. Google CSE (if key configured) with site: operators → highest quality
        2. DuckDuckGo fallback → free, no key needed

        Post-processing:
        - URL cleaning: strip Bing/DDG tracking redirects
        - Domain blacklist: reject Wikipedia, Pinterest, etc.
        - Snippet trimming: max 300 chars
        """
        if not topic or not topic.strip():
            return []

        level_suffix = {
            "Junior": "beginner",
            "Mid-Level": "intermediate",
            "Senior": "advanced",
        }.get(experience_level, "")

        results = []

        # ── Query 1: Educational platform courses ──
        edu_query = f"{topic} {level_suffix} course tutorial".strip()
        edu_sites = (
            "site:coursera.org OR site:udemy.com OR site:edx.org "
            "OR site:alison.com OR site:khanacademy.org "
            "OR site:linkedin.com/learning"
        )
        try:
            if self.google_api_key and self.google_cx and not self._google_circuit_open:
                edu_results = self._search_google_raw(
                    f"{edu_query} {edu_sites}", max_results=1
                )
            else:
                edu_results = self._search_duckduckgo_raw(
                    f"{edu_query} {edu_sites}", max_results=1
                )
            results.extend(edu_results)
        except Exception as exc:
            logger.debug("Course search failed: %s", exc)

        # ── Query 2: Official documentation / training ──
        doc_query = f"{topic} official tutorial training getting started"
        try:
            if self.google_api_key and self.google_cx and not self._google_circuit_open:
                doc_results = self._search_google_raw(doc_query, max_results=1)
            else:
                doc_results = self._search_duckduckgo_raw(doc_query, max_results=1)
            results.extend(doc_results)
        except Exception as exc:
            logger.debug("Doc search failed: %s", exc)

        # Post-process all results
        cleaned = []
        for r in results:
            r["url"] = self._clean_url(r.get("url", ""))
            r["snippet"] = (r.get("snippet", "") or "")[:self._MAX_SNIPPET_LEN]
            domain = self._extract_domain(r["url"])
            r["source"] = domain

            # Skip blocked domains
            if domain in self._BLOCKED_DOMAINS:
                logger.debug("Skipping blocked domain: %s", domain)
                continue
            # Skip if URL is still a tracking redirect after cleaning
            if "bing.com/aclick" in r["url"] or "duckduckgo.com/l/" in r["url"]:
                logger.debug("Skipping tracking redirect: %s", r["url"][:80])
                continue

            cleaned.append(r)

        return cleaned[:max_results]

    def _search_google_raw(self, query: str, max_results: int) -> List[Dict]:
        """Google Custom Search — highest quality results."""
        try:
            resp = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": self.google_api_key,
                    "cx": self.google_cx,
                    "q": query,
                    "num": min(max_results + 3, 10),
                    "lr": "lang_en",
                    "hl": "en",
                },
                timeout=10,
            )

            if resp.status_code in (403, 429):
                self._google_circuit_open = True
                logger.warning("Google CSE %d — circuit breaker OPEN", resp.status_code)
                return self._search_duckduckgo_raw(query, max_results)

            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("items", []):
                title = item.get("title", "")
                if not self._is_english_title(title):
                    continue
                results.append({
                    "type": "article",
                    "platform": "Web",
                    "title": title,
                    "url": item.get("link", ""),
                    "snippet": (item.get("snippet", "") or "")[:self._MAX_SNIPPET_LEN],
                    "source": self._extract_domain(item.get("link", "")),
                    "thumbnail": item.get("pagemap", {})
                        .get("cse_thumbnail", [{}])[0]
                        .get("src", ""),
                })
                if len(results) >= max_results:
                    break

            return results

        except requests.RequestException as exc:
            logger.error("Google CSE raw error: %s", exc)
            return self._search_duckduckgo_raw(query, max_results)

    def _search_duckduckgo_raw(self, query: str, max_results: int) -> List[Dict]:
        """DuckDuckGo search with URL cleaning and English filtering."""
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                raw = list(ddgs.text(
                    query,
                    region="us-en",
                    max_results=max_results + 8,
                ))

            results = []
            for r in raw:
                title = r.get("title", "")
                if not self._is_english_title(title):
                    continue

                url = self._clean_url(r.get("href", ""))
                domain = self._extract_domain(url)

                # Skip blocked domains
                if domain in self._BLOCKED_DOMAINS:
                    continue
                # Skip tracking redirects
                if "bing.com/aclick" in url or "duckduckgo.com/l/" in url:
                    continue

                results.append({
                    "type": "article",
                    "platform": "Web",
                    "title": title,
                    "url": url,
                    "snippet": (r.get("body", "") or "")[:self._MAX_SNIPPET_LEN],
                    "source": domain,
                    "thumbnail": "",
                })
                if len(results) >= max_results:
                    break

            return results

        except Exception as exc:
            logger.debug("DuckDuckGo raw search error: %s", exc)
            return []

    # ── Google ───────────────────────────────────────────────────
    def _search_google(self, query: str, max_results: int) -> List[Dict]:
        try:
            resp = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": self.google_api_key,
                    "cx": self.google_cx,
                    "q": f"{query} tutorial guide documentation",
                    "num": max_results,
                    "lr": "lang_en",   # Restrict results to English content
                    "hl": "en",        # English interface (improves ranking)
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "type": "article",
                    "platform": "Web",
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": self._extract_domain(item.get("link", "")),
                    "thumbnail": item.get("pagemap", {})
                    .get("cse_thumbnail", [{}])[0]
                    .get("src", ""),
                }
                for item in data.get("items", [])
            ]
        except requests.RequestException as exc:
            if "403" in str(exc) or "429" in str(exc):
                self._google_circuit_open = True
                logger.error("Google Search error: %s — circuit breaker OPEN", exc)
            else:
                logger.error("Google Search error: %s", exc)
            return self._search_duckduckgo(query, max_results)

    # ── Bing ─────────────────────────────────────────────────────
    def _search_bing(self, query: str, max_results: int) -> List[Dict]:
        try:
            resp = requests.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers={"Ocp-Apim-Subscription-Key": self.bing_api_key},
                params={
                    "q": f"{query} tutorial guide documentation",
                    "count": max_results,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "type": "article",
                    "platform": "Web",
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", ""),
                    "source": self._extract_domain(item.get("url", "")),
                    "thumbnail": "",
                }
                for item in data.get("webPages", {}).get("value", [])
            ]
        except requests.RequestException as exc:
            logger.error("Bing Search error: %s", exc)
            return self._search_duckduckgo(query, max_results)

    # ── DuckDuckGo (free fallback) ───────────────────────────────
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """Free web search via DuckDuckGo (no API key required).

        Quality filters:
        1. region="us-en" — bias towards English results
        2. _is_english_title() — reject non-Latin titles
        3. _clean_url() — strip Bing/DDG tracking redirects
        4. _BLOCKED_DOMAINS — reject Wikipedia, Pinterest, etc.
        5. Snippet trimming — max 300 chars
        """
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.text(
                    f"{query} tutorial guide",
                    region="us-en",
                    max_results=max_results + 10,
                ))

            formatted = []
            for r in results:
                title = r.get("title", "")
                if not self._is_english_title(title):
                    continue

                url = self._clean_url(r.get("href", ""))
                domain = self._extract_domain(url)

                if domain in self._BLOCKED_DOMAINS:
                    continue
                if "bing.com/aclick" in url or "duckduckgo.com/l/" in url:
                    continue

                formatted.append({
                    "type": "article",
                    "platform": "Web",
                    "title": title,
                    "url": url,
                    "snippet": (r.get("body", "") or "")[:self._MAX_SNIPPET_LEN],
                    "source": domain,
                    "thumbnail": "",
                })
                if len(formatted) >= max_results:
                    break

            logger.info("DuckDuckGo: found %d results for '%s'", len(formatted), query)
            return formatted

        except ImportError:
            logger.error(
                "DuckDuckGo search not installed. "
                "Run: pip install ddgs"
            )
            return []
        except Exception as exc:
            logger.error("DuckDuckGo search error: %s", exc)
            return []

    # ── helpers ──────────────────────────────────────────────────
    @staticmethod
    def _clean_url(url: str) -> str:
        """Strip tracking redirects from URLs.

        Handles:
        - DuckDuckGo redirects: duckduckgo.com/l/?uddg=REAL_URL
        - Bing ad clicks:       bing.com/aclick?...&u=BASE64(REAL_URL)
        """
        from urllib.parse import parse_qs, unquote

        if not url:
            return url

        parsed = urlparse(url)

        # DuckDuckGo redirect: extract 'uddg' param
        if "duckduckgo.com" in parsed.netloc and "/l/" in parsed.path:
            params = parse_qs(parsed.query)
            if "uddg" in params:
                return unquote(params["uddg"][0])

        # Bing ad redirect: extract 'u' param (base64-encoded URL)
        if "bing.com" in parsed.netloc and "aclick" in parsed.path:
            params = parse_qs(parsed.query)
            if "u" in params:
                try:
                    import base64
                    decoded = base64.b64decode(params["u"][0] + "==").decode("utf-8", errors="ignore")
                    # The decoded value is sometimes the URL directly
                    if decoded.startswith("http"):
                        return decoded
                except Exception:
                    pass
            # If decoding fails, reject the URL entirely
            return ""

        return url

    @staticmethod
    def _extract_domain(url: str) -> str:
        try:
            return urlparse(url).netloc.replace("www.", "")
        except ValueError:
            return "Web"

    @staticmethod
    def _is_english_title(title: str) -> bool:
        """Reject titles containing CJK, Arabic, Cyrillic, or Devanagari.

        Returns True if the title is primarily Latin/English script.
        This catches Chinese (zhihu.com), Arabic, Russian, Hindi pages
        that slip through DuckDuckGo's region filter.
        """
        import re
        non_latin = re.compile(
            r'[\u4e00-\u9fff'   # CJK Unified Ideographs (Chinese)
            r'\u3040-\u309f'    # Hiragana (Japanese)
            r'\u30a0-\u30ff'    # Katakana (Japanese)
            r'\u0600-\u06ff'    # Arabic
            r'\u0400-\u04ff'    # Cyrillic (Russian)
            r'\u0900-\u097f'    # Devanagari (Hindi)
            r'\uac00-\ud7af]'   # Hangul (Korean)
        )
        return not bool(non_latin.search(title))


# Singleton
web_search_service = WebSearchService()
