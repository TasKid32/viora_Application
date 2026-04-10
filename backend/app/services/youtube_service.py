"""
YouTube API Integration — Educational video search.

Quality filters (production-grade):
1. relevanceLanguage + post-processing title filter for non-English
2. videoDefinition=high for HD quality
3. videoDuration=medium (4-20 min) to filter Shorts
4. videoCategoryId=27 (Education)
5. Comparison/review video exclusion

Uses structured logging. Returns empty list if API key is missing.
"""
from typing import List, Dict
import re
import requests

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Non-educational title patterns to exclude ────────────────
# These patterns indicate comparison/review videos, not tutorials
_EXCLUDE_TITLE_PATTERNS = re.compile(
    r"\b(vs\.?|versus|comparison|compared|review\b|unboxing|react|reaction)\b",
    re.IGNORECASE,
)


class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def search_videos(
        self,
        query: str,
        max_results: int = 5,
        language: str = "en",
        experience_level: str = "Mid-Level",
        job_context: str = "",
    ) -> List[Dict]:
        """Search for educational videos on YouTube.

        Adjusts search query based on experience level and job context:
        - Junior → "for beginners"
        - Mid-Level → "intermediate"
        - Senior → "advanced"
        - job_context → adds job title for relevance (e.g. "Docker Software Developers")

        Quality filters:
        - HD videos only (videoDefinition=high)
        - Medium duration (4-20 min — filters out Shorts)
        - Education category (videoCategoryId=27)
        - Post-processing: reject non-English titles and comparison videos
        """

        if not self.api_key:
            logger.warning("YouTube API key not configured — skipping video search")
            return []

        # Adjust query based on experience level
        level_suffix = {
            "Junior": "for beginners",
            "Mid-Level": "intermediate",
            "Senior": "advanced",
        }.get(experience_level, "tutorial")

        # Focused search query — job_context removed because it dilutes results.
        # "Docker intermediate tutorial" returns better results than
        # "Docker Software Developers intermediate tutorial"
        search_query = f"{query} {level_suffix} tutorial"

        try:
            url = f"{self.base_url}/search"
            # Request extra results to compensate for post-filtering
            fetch_count = min(max_results + 4, 10)
            params = {
                "part": "snippet",
                "q": search_query,
                "type": "video",
                "maxResults": fetch_count,
                "key": self.api_key,
                "videoCategoryId": "27",  # Education category
                "videoDuration": "medium",  # 4-20 min (filters out Shorts)
                "videoDefinition": "high",  # HD quality only
                "relevanceLanguage": language,
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                logger.error(
                    "YouTube API error: %d — %s",
                    response.status_code,
                    response.text[:200],
                )
                return []

            data = response.json()

            # Collect all video IDs for batch duration fetch
            video_ids = [
                item["id"]["videoId"]
                for item in data.get("items", [])
            ]

            # Batch fetch durations (single API call instead of N)
            durations = self._get_video_durations_batch(video_ids)

            videos = []
            for item in data.get("items", []):
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]

                # ── Post-processing quality filters ──────────────
                # Filter 1: Reject non-English titles (>30% non-Latin chars)
                if not self._is_english_title(title):
                    logger.debug("Skipping non-English video: %s", title[:80])
                    continue

                # Filter 2: Reject comparison/review videos
                if _EXCLUDE_TITLE_PATTERNS.search(title):
                    logger.debug("Skipping non-tutorial video: %s", title[:80])
                    continue

                videos.append(
                    {
                        "type": "video",
                        "platform": "YouTube",
                        "title": title,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                        "channel": item["snippet"]["channelTitle"],
                        "duration": durations.get(video_id, "Unknown"),
                        "description": item["snippet"]["description"][:200],
                    }
                )

                # Stop once we have enough quality results
                if len(videos) >= max_results:
                    break

            logger.info("YouTube: found %d videos for '%s'", len(videos), query)
            return videos

        except requests.RequestException as e:
            logger.error("YouTube API request failed: %s", e)
            return []
        except Exception as e:
            logger.error("YouTube API unexpected error: %s", e)
            return []

    @staticmethod
    def _is_english_title(title: str) -> bool:
        """Check if a title is primarily English (>60% Latin characters).

        Filters out videos in Malayalam, Arabic, Hindi, etc. that
        YouTube's relevanceLanguage parameter doesn't fully exclude.
        """
        if not title:
            return False
        latin_chars = len(re.findall(r'[a-zA-Z0-9\s\-\.\,\:\;\!\?\(\)\[\]\&\#\+\/]', title))
        return latin_chars / max(len(title), 1) > 0.6

    def _get_video_durations_batch(self, video_ids: list) -> dict:
        """Batch-fetch durations for multiple videos in a single API call.

        Returns:
            Dict mapping video_id -> formatted duration string.
        """
        if not video_ids:
            return {}

        try:
            url = f"{self.base_url}/videos"
            params = {
                "part": "contentDetails",
                "id": ",".join(video_ids),  # Batch: comma-separated IDs
                "key": self.api_key,
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            durations = {}
            for item in data.get("items", []):
                vid_id = item["id"]
                raw_duration = item["contentDetails"]["duration"]
                durations[vid_id] = self._parse_duration(raw_duration)

            return durations
        except (KeyError, requests.RequestException) as e:
            logger.debug("Could not batch-fetch durations: %s", e)
            return {}

    @staticmethod
    def _parse_duration(duration: str) -> str:
        """Parse ISO 8601 duration to HH:MM:SS."""
        hours = re.search(r"(\d+)H", duration)
        minutes = re.search(r"(\d+)M", duration)
        seconds = re.search(r"(\d+)S", duration)

        h = int(hours.group(1)) if hours else 0
        m = int(minutes.group(1)) if minutes else 0
        s = int(seconds.group(1)) if seconds else 0

        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        else:
            return f"{m}:{s:02d}"


# Singleton
youtube_service = YouTubeService()
