"""
LLM Service — Gemini integration for chat assistant ONLY.

Uses the google-genai SDK for Gemini 2.5 Flash.
All CV analysis and skill gap functions have been replaced by
Viora NER (ONNX) + O*NET taxonomy which run locally.

Gemini is now used ONLY for the AI chat assistant.
"""
import json
from typing import Dict, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Check SDK availability ──────────────────────────────────────

try:
    from google import genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-genai not installed — run: pip install google-genai")



# ── Gemini model configuration ──────────────────────────────────

GEMINI_MODEL = "gemini-2.5-flash"


class LLMService:
    """LLM service — used ONLY for the AI chat assistant."""

    def __init__(self):
        self.gemini_client = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazily initialize API clients on first use."""
        if self._initialized:
            return
        self._initialized = True

        # Gemini (primary) — using new google-genai SDK
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Gemini client initialized (%s)", GEMINI_MODEL)
            except Exception as e:
                logger.error("Failed to initialize Gemini client: %s", e)

        if not self.gemini_client:
            logger.warning(
                "No LLM API keys configured — chat assistant will be unavailable. "
                "Add GEMINI_API_KEY to .env"
            )

    @property
    def is_available(self) -> bool:
        """Check if Gemini API is configured."""
        self._ensure_initialized()
        return bool(self.gemini_client)

    # ── Chat Assistant (ONLY remaining Gemini use) ──────────────

    async def chat_assistant(
        self,
        user_message: str,
        context: Optional[Dict] = None,
    ) -> str:
        """AI Assistant chat interface using Gemini."""
        self._ensure_initialized()

        context_text = ""
        if context:
            context_text = f"\nUser Context: {json.dumps(context, default=str)}"

        prompt = f"""You are Viora AI, a specialized career guidance counselor and learning coach.

Your role:
- Analyze career gaps and recommend actionable next steps
- Suggest specific learning resources (courses, projects, certifications)
- Help users prepare for job interviews in their target field
- Provide personalized advice based on the user's actual skills and career stage
- Motivate and encourage continuous learning

Rules:
- Give thorough, complete, and detailed answers. Do NOT cut off or abbreviate your response.
- If the user has context below, reference their actual skills and target job
- Respond in the SAME language the user writes in (Arabic or English)
- When suggesting learning, mention specific platforms (Coursera, Udemy, YouTube)
- NEVER use markdown formatting: no asterisks (*), no bold (**), no headers (#), no bullet symbols. Use plain text only. Use line breaks and numbered lists (1. 2. 3.) for structure.
- Always finish your complete thought. Never stop mid-sentence or mid-paragraph.
{context_text}

User Question: {user_message}
"""
        return await self._call_llm(prompt, temperature=0.7)

    # ── Core LLM Call ───────────────────────────────────────────

    async def _call_llm(
        self, prompt: str, temperature: float = 1.0
    ) -> str:
        """Call Gemini API with auto-continuation for truncated responses."""
        self._ensure_initialized()

        if self.gemini_client:
            try:
                logger.debug("Calling Gemini API (%s)...", GEMINI_MODEL)

                gemini_config = {
                    "temperature": temperature,
                    "max_output_tokens": 65536,
                }

                response = await self.gemini_client.aio.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config=gemini_config,
                )

                full_text = response.text or ""

                # Auto-continuation: if response was truncated, ask to continue
                MAX_CONTINUATIONS = 2
                for i in range(MAX_CONTINUATIONS):
                    finish = getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None
                    # finish_reason values: STOP (complete), MAX_TOKENS (truncated)
                    if finish and str(finish).upper() in ('MAX_TOKENS', 'FINISH_REASON_MAX_TOKENS', '2'):
                        logger.info("Response truncated (attempt %d), requesting continuation...", i + 1)
                        response = await self.gemini_client.aio.models.generate_content(
                            model=GEMINI_MODEL,
                            contents=f"{prompt}\n\nAssistant (continued from previous):\n{full_text}\n\nContinue from where you stopped. Do not repeat what you already said.",
                            config=gemini_config,
                        )
                        full_text += "\n" + (response.text or "")
                    else:
                        break

                return _clean_markdown(full_text)
            except Exception as e:
                logger.error("Gemini API error: %s", e)

        # No API available
        logger.warning("No LLM API available for chat")
        return "I'm sorry, the AI assistant is currently unavailable. Please try again later."


def _clean_markdown(text: str) -> str:
    """Strip markdown formatting that Gemini may include despite instructions."""
    import re
    # Remove bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Remove italic: *text* or _text_ (single)
    text = re.sub(r'(?<!\w)\*([^*]+?)\*(?!\w)', r'\1', text)
    # Remove headers: ### text → text
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bullet markers: - item → item (keep numbered lists)
    text = re.sub(r'^\s*[-•]\s+', '', text, flags=re.MULTILINE)
    return text.strip()


# ── Singleton & DI ──────────────────────────────────────────────

llm_service = LLMService()


def get_llm_service() -> LLMService:
    """Dependency injection factory for LLMService."""
    return llm_service
