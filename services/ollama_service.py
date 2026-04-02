import logging
import requests

from .prompt_builder import build_summary_prompt

logger = logging.getLogger(__name__)


class OllamaService:
    def __init__(self, host="http://localhost:11434", model="llama3.2:3b"):
        self.host = host.rstrip("/")
        self.model = model

    def summarize_emails(self, emails: list[dict]) -> str:
        prompt = build_summary_prompt(emails)
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 500},
                },
                timeout=300,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out (60s)")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to Ollama at {self.host}")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise
