"""LLMインスタンスを生成するファクトリークラス"""

from typing import Dict, Any
import logging
from .base import BaseLLM
from .gemini import GeminiLLM

logger = logging.getLogger(__name__)


class LLMFactory:
    """LLMファクトリークラス"""

    # サポートされているLLMの一覧
    SUPPORTED_LLMS = {
        "gemini": GeminiLLM,
        # 今後、他のLLMを追加する場合はここに追加
        # "gpt4": GPT4LLM,
        # "claude": ClaudeLLM,
    }

    @classmethod
    def create(cls, llm_type: str, config: Dict[str, Any]) -> BaseLLM:
        """LLMインスタンスを生成

        Args:
            llm_type (str): LLMの種類
            config (Dict[str, Any]): 設定情報

        Returns:
            BaseLLM: LLMインスタンス

        Raises:
            ValueError: サポートされていないLLM種別の場合
        """
        llm_type = llm_type.lower()

        if llm_type not in cls.SUPPORTED_LLMS:
            supported = ", ".join(cls.SUPPORTED_LLMS.keys())
            raise ValueError(
                f"未サポートのLLM種別: {llm_type}. サポートされている種別: {supported}"
            )

        logger.info(f"LLM '{llm_type}' のインスタンスを生成します")
        llm_class = cls.SUPPORTED_LLMS[llm_type]
        return llm_class(config)

    @classmethod
    def get_supported_llms(cls) -> list:
        """サポートされているLLMの一覧を取得

        Returns:
            list: サポートされているLLM種別のリスト
        """
        return list(cls.SUPPORTED_LLMS.keys())
