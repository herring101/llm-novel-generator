"""Gemini APIを使用するLLM実装"""

import google.generativeai as genai
import logging
from .base import BaseLLM

logger = logging.getLogger(__name__)


class GeminiLLM(BaseLLM):
    """Gemini LLMの実装クラス"""

    def initialize(self) -> None:
        """Geminiの初期化

        Raises:
            ValueError: API keyが不正な場合
        """
        # 必須設定の確認
        self._validate_config(["api_key"])

        api_key = self.config["api_key"]
        if not api_key or api_key == "YOUR-API-KEY":
            logger.error("Gemini API keyが設定されていません")
            raise ValueError("Invalid API key")

        # Gemini APIの設定
        genai.configure(api_key=api_key)

        # モデルの初期化
        model_name = self._get_config_value("model_name", "gemini-1.5-pro")
        generation_config = self._get_config_value("model", {})

        logger.info(f"Geminiモデル '{model_name}' を初期化します")
        self.model = genai.GenerativeModel(
            model_name=model_name, generation_config=generation_config
        )
        logger.info("Geminiモデルの初期化が完了しました")

    def generate(self, prompt: str) -> str:
        """テキスト生成を行う

        Args:
            prompt (str): 入力プロンプト

        Returns:
            str: 生成されたテキスト

        Raises:
            Exception: 生成処理に失敗した場合
        """
        try:
            logger.debug(f"プロンプト長: {len(prompt)} 文字")
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                raise ValueError("空の応答が返されました")

            return response.text

        except Exception as e:
            logger.error(f"Geminiでの生成中にエラー: {str(e)}")
            raise
