import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

from ..llm.base import BaseLLM
from ..logging.log_manager import LogManager
from ..models.data_models import (
    GenerationMetadata,
    StoryBaseSettings,
    StoryContext,
    StoryPlan,
)
from .parser import ResponseParser
from .prompt_manager import PromptManager
from .section_manager import SectionManager

logger = logging.getLogger(__name__)


class StoryManager:
    """物語生成の管理を行うクラス"""

    def __init__(
        self,
        config: Dict[str, Any],
        llm: BaseLLM,
        log_manager: LogManager,
        prompt_manager: PromptManager,
        parser: ResponseParser,
    ):
        """初期化

        Args:
            config (Dict[str, Any]): 設定情報
            llm (BaseLLM): LLMインスタンス
            log_manager (LogManager): ログ管理
            prompt_manager (PromptManager): プロンプト管理
            parser (ResponseParser): 応答解析
        """
        self.config = config
        self.llm = llm
        self.log_manager = log_manager
        self.prompt_manager = prompt_manager
        self.parser = parser

        # 出力ディレクトリの設定
        self.output_dir = "output" + "/" + self.config["output_dir"]
        self._ensure_output_directory()

        # 出力ファイルのパス設定
        self.story_file = os.path.join(self.output_dir, "story.txt")
        self.metadata_file = os.path.join(self.output_dir, "metadata.json")

        # ストーリーコンテキストの初期化
        self.story_context = StoryContext(
            story_setting=config["story_setting"],
            base_settings=None,
            story_plan=None,
            sections=[],
            progress=0.0,
            total_length="",
        )

        # セクションマネージャーの初期化
        self.section_manager = None  # initialize_storyで初期化

        # ファイルの初期化
        self._initialize_files()

    def _ensure_output_directory(self) -> None:
        """出力ディレクトリの確保"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"出力ディレクトリを作成しました: {self.output_dir}")

    def _initialize_files(self) -> None:
        """出力ファイルの初期化"""
        with open(self.story_file, "w", encoding="utf-8") as f:
            f.write("=== 物語 ===\n\n")
        logger.info(f"物語ファイルを初期化: {self.story_file}")

        self._save_metadata(
            GenerationMetadata(
                status="initialized",
                current_section=0,
                progress=0.0,
                timestamp=datetime.now(),
            )
        )

    def _save_metadata(self, metadata: GenerationMetadata) -> None:
        """メタデータの保存"""
        metadata_dict = {
            "status": metadata.status,
            "current_section": metadata.current_section,
            "progress": metadata.progress,
            "timestamp": metadata.timestamp.isoformat(),
            "current_length": self.get_current_length(),
        }
        if metadata.error_message:
            metadata_dict["error_message"] = metadata.error_message

        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata_dict, ensure_ascii=False, indent=2, fp=f)

    def _append_story(self, section_number: int, content: str) -> None:
        """物語本文の追記"""
        with open(self.story_file, "a", encoding="utf-8") as f:
            f.write(content.strip())
            f.write("\n\n")

    def _generate_base_settings(
        self, story_setting: str, total_length: str
    ) -> StoryBaseSettings:
        """基本設定を生成"""
        logger.info("基本設定の生成を開始")
        prompt = self.prompt_manager.get_base_settings_prompt(
            story_setting, total_length
        )

        try:
            response = self.llm.generate(prompt)
            self.log_manager.log_llm_interaction("基本設定生成", prompt, response)
            base_settings = self.parser.parse_base_settings(response)
            logger.info("基本設定の生成が完了")
            return base_settings

        except Exception as e:
            logger.error(f"基本設定の生成中にエラー: {str(e)}")
            raise

    def _generate_story_plan(self, base_settings: StoryBaseSettings) -> StoryPlan:
        """展開計画を生成"""
        logger.info("展開計画の生成を開始")
        prompt = self.prompt_manager.get_story_plan_prompt(
            base_settings, self.story_context.story_setting
        )

        try:
            response = self.llm.generate(prompt)
            self.log_manager.log_llm_interaction("展開計画生成", prompt, response)
            story_plan = self.parser.parse_story_plan(response)
            logger.info("展開計画の生成が完了")
            return story_plan

        except Exception as e:
            logger.error(f"展開計画の生成中にエラー: {str(e)}")
            raise

    def get_current_length(self) -> int:
        """現在の文字数を取得"""
        return sum(len(section.content) for section in self.story_context.sections)

    def generate_full_story(self, max_sections: int, total_length: str) -> str:
        """物語全体を生成"""
        logger.info("=== 物語生成開始 ===")

        # 物語の初期化
        self.initialize_story(total_length)

        section_count = 0
        while section_count < max_sections:
            section_count += 1
            logger.info(f"セクション {section_count} の生成を開始")

            try:
                # セクションの生成
                section_data = self.section_manager.generate_section(section_count)
                self.story_context.sections.append(section_data)
                self._append_story(section_count, section_data.content)

                # メタデータの更新
                self._save_metadata(
                    GenerationMetadata(
                        status="section_generated",
                        current_section=section_count,
                        progress=section_data.progress.percentage,
                        timestamp=datetime.now(),
                    )
                )

                # 進捗のログ出力
                current_length = self.get_current_length()
                logger.info(
                    f"セクション {section_count} 完了: 現在の文字数 {current_length}文字"
                )

                # 完了判定
                if section_data.progress.percentage >= 100:
                    logger.info("=== 物語が完結しました ===")
                    self._save_metadata(
                        GenerationMetadata(
                            status="completed",
                            current_section=section_count,
                            progress=100,
                            timestamp=datetime.now(),
                        )
                    )
                    break

            except Exception as e:
                logger.error(f"セクション {section_count} の生成中にエラー: {str(e)}")
                self._save_metadata(
                    GenerationMetadata(
                        status="error",
                        current_section=section_count,
                        error_message=str(e),
                        timestamp=datetime.now(),
                    )
                )
                raise

        # 生成された物語全体を返す
        with open(self.story_file, "r", encoding="utf-8") as f:
            return f.read()

    def initialize_story(self, total_length: str) -> None:
        """物語の初期化を行う"""
        logger.info("=== 物語の初期化を開始 ===")

        self.story_context = StoryContext(
            story_setting=self.config["story_setting"],
            total_length=total_length,  # これが確実に設定されているか確認
            base_settings=None,
            story_plan=None,
            sections=[],
            progress=0.0,
            current_length=0,
        )

        # 基本設定の生成
        self.story_context.base_settings = self._generate_base_settings(
            self.story_context.story_setting, total_length
        )

        # 展開計画の生成
        self.story_context.story_plan = self._generate_story_plan(
            self.story_context.base_settings
        )

        # セクションマネージャーの初期化
        self.section_manager = SectionManager(
            self.llm,
            self.log_manager,
            self.prompt_manager,
            self.parser,
            self.story_context,
        )

        self._save_metadata(
            GenerationMetadata(
                status="initialized",
                current_section=0,
                progress=0.0,
                timestamp=datetime.now(),
            )
        )

        logger.info("=== 物語の初期化が完了 ===")
