"""LLMの基底クラスを提供するモジュール"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """LLMの基底クラス"""

    def __init__(self, config: Dict[str, Any]):
        """初期化

        Args:
            config (Dict[str, Any]): LLMの設定情報
        """
        self.config = config
        self.model = None
        self.initialize()

    @abstractmethod
    def initialize(self) -> None:
        """LLMの初期化

        Raises:
            ValueError: 初期化に必要な設定が不足している場合
        """
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """テキスト生成を行う

        Args:
            prompt (str): 入力プロンプト

        Returns:
            str: 生成されたテキスト

        Raises:
            Exception: 生成処理に失敗した場合
        """
        pass

    def _validate_config(self, required_keys: list) -> None:
        """設定の検証

        Args:
            required_keys (list): 必須キーのリスト

        Raises:
            ValueError: 必須キーが不足している場合
        """
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"必須の設定キー '{key}' が不足しています")

    def _get_config_value(
        self, key: str, default: Any = None, required: bool = False
    ) -> Any:
        """設定値の取得

        Args:
            key (str): 設定キー
            default (Any, optional): デフォルト値. Defaults to None.
            required (bool, optional): 必須かどうか. Defaults to False.

        Returns:
            Any: 設定値

        Raises:
            ValueError: required=Trueで値が存在しない場合
        """
        value = self.config.get(key, default)
        if required and value is None:
            raise ValueError(f"必須の設定値 '{key}' が不足しています")
        return value
