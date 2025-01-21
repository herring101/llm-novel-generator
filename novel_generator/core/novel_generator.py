"""小説生成の中核機能を提供するモジュール"""

from typing import Dict, Any
import logging

from ..logging.log_manager import LogManager
from ..logging.logger import setup_logging
from .prompt_manager import PromptManager
from .parser import ResponseParser
from .story_manager import StoryManager
from ..llm.factory import LLMFactory

logger = logging.getLogger(__name__)


class NovelGenerator:
    """小説生成を統括するメインクラス"""

    def __init__(self, config: Dict[str, Any]):
        """初期化

        Args:
            config (Dict[str, Any]): 設定情報

        Raises:
            ValueError: 必須の設定が不足している場合
        """
        self.config = config
        self._validate_config()

        # 出力ディレクトリの設定
        self.output_dir = "output" + "/" + self.config["output_dir"]

        # ロギングの設定
        setup_logging(self.output_dir)
        logger.info("=== 小説生成システムを初期化 ===")

        # コンポーネントの初期化
        self._initialize_components()

        logger.info("初期化が完了しました")

    def _validate_config(self) -> None:
        """設定の検証

        Raises:
            ValueError: 必須の設定が不足している場合
        """
        required_keys = [
            "output_dir",
            "llm_type",
            "llm_config",
            "story_setting",
        ]

        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"必須の設定 '{key}' が不足しています")

    def _initialize_components(self) -> None:
        """各コンポーネントの初期化"""
        # LLMの初期化
        llm_type = self.config["llm_type"]
        llm_config = self.config["llm_config"]
        self.llm = LLMFactory.create(llm_type, llm_config)
        logger.info(f"LLM '{llm_type}' を初期化しました")

        # パーサーを先に初期化
        self.parser = ResponseParser()
        
        # 各マネージャーの初期化（パーサーを渡す）
        self.log_manager = LogManager(self.output_dir, self.parser)
        self.prompt_manager = PromptManager()

        # StoryManagerの初期化
        self.story_manager = StoryManager(
            config=self.config,
            llm=self.llm,
            log_manager=self.log_manager,
            prompt_manager=self.prompt_manager,
            parser=self.parser,
        )

    def generate_story(
        self,
        max_sections: int = 20,
        total_length: str = "中編（3万字程度）",
    ) -> str:
        """物語を生成

        Args:
            max_sections (int): 最大セクション数. デフォルトは20.
            total_length (str): 想定される物語の長さ.

        Returns:
            str: 生成された物語

        Raises:
            Exception: 物語生成に失敗した場合
        """
        try:
            logger.info("=== 物語生成を開始 ===")
            story = self.story_manager.generate_full_story(max_sections, total_length)
            logger.info("=== 物語生成が完了 ===")
            return story

        except Exception as e:
            logger.error(f"物語生成中にエラー: {str(e)}")
            raise

    def get_current_length(self) -> int:
        """現在の文字数を取得

        Returns:
            int: 現在の総文字数
        """
        return self.story_manager.get_current_length()

    def get_generation_status(self) -> Dict[str, Any]:
        """生成状況の取得

        Returns:
            Dict[str, Any]: 生成状況の情報
        """
        return self.story_manager.get_generation_status()