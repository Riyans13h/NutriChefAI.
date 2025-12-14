"""
LLM Service
-----------
Responsible for:
- Interacting with the OpenAI API
- Generating controlled, grounded text
- Acting as a single gateway to the LLM
"""

from langchain_openai import ChatOpenAI
from flask import current_app


class LLMService:
    """
    Wrapper around OpenAI chat models.
    """

    _llm = None

    @classmethod
    def _initialize_llm(cls):
        """
        Initializes the LLM client once.
        """
        if cls._llm is None:
            cls._llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.2,
                api_key=current_app.config["OPENAI_API_KEY"]
            )

    @classmethod
    def generate_text(cls, prompt: str) -> str:
        """
        Generates text from the LLM.

        Args:
            prompt (str): grounded prompt

        Returns:
            str: generated text
        """

        if not prompt:
            return ""

        cls._initialize_llm()

        response = cls._llm.invoke(prompt)

        return response.content.strip()
