from datetime import datetime
import logging

from ..models.data_models import SectionData, StoryContext, PlanAdjustment
from ..logging.log_manager import LogManager
from .prompt_manager import PromptManager
from .parser import ResponseParser
from ..llm.base import BaseLLM

logger = logging.getLogger(__name__)

class SectionManager:
    """セクション生成を管理するクラス"""

    def __init__(
        self,
        llm: BaseLLM,
        log_manager: LogManager,
        prompt_manager: PromptManager,
        parser: ResponseParser,
        story_context: StoryContext,
    ):
        self.llm = llm
        self.log_manager = log_manager
        self.prompt_manager = prompt_manager
        self.parser = parser
        self.story_context = story_context

    def generate_section(self, section_count: int, max_retries: int = 3) -> SectionData:
        """セクションを生成

        Args:
            section_count (int): セクション番号
            max_retries (int, optional): 最大リトライ回数. デフォルトは3.

        Returns:
            SectionData: 生成されたセクションデータ
        """

        # 5セクションごとの計画見直し
        if section_count % 5 == 0 and section_count > 0:
            self._review_plan(section_count)

        # プロンプトの生成時に、最新の計画調整を反映
        prompt = self.prompt_manager.get_section_generation_prompt(
            self.story_context, 
            section_count
        )

        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.llm.generate(prompt)
                self.log_manager.log_llm_interaction(
                    f"セクション {section_count} 生成（試行 {attempt + 1}/{max_retries}）",
                    prompt,
                    response,
                )

                thinking = self.parser.extract_tag_content(response, "thinking")
                section_data = self.parser.parse_section_data(response, thinking)

                if not self._quality_check(section_data):
                    raise ValueError("生成されたセクションが品質基準を満たしていません")

                logger.info(
                    f"セクション {section_count} の生成が完了"
                    f"（進行度: {section_data.progress.percentage}%）"
                )
                return section_data

            except Exception as e:
                last_error = e
                logger.warning(
                    f"セクション {section_count} の生成が失敗"
                    f"（試行 {attempt + 1}/{max_retries}）: {str(e)}"
                )
                if attempt < max_retries - 1:
                    logger.info("リトライを実行します...")
                    continue

        error_msg = (
            f"セクション {section_count} の生成に失敗しました。"
            f"{max_retries}回の試行全てが失敗: {str(last_error)}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    def _quality_check(self, section_data: SectionData) -> bool:
        """品質チェック"""
        if not section_data.content or not section_data.progress or not section_data.next_preview:
            logger.warning("必要な要素が不足しています")
            return False

        if len(section_data.content) < 1000:
            logger.warning("セクションの長さが不足しています")
            return False

        if not (0 <= section_data.progress.percentage <= 100):
            logger.warning("進行度の値が不適切です")
            return False

        return True

    def _review_plan(self, section_count: int) -> None:
        """計画の見直しを実行し、結果を反映
        
        Args:
            section_count (int): 現在のセクション番号
        """
        logger.info(f"計画見直しを開始（セクション {section_count}）")

        prompt = self.prompt_manager.get_plan_review_prompt(
            self.story_context, section_count
        )

        try:
            # LLMからの応答を取得
            response = self.llm.generate(prompt)
            self.log_manager.log_llm_interaction(
                f"計画見直し（セクション {section_count}）", prompt, response
            )

            # 計画の見直し結果を解析
            review_result = self.parser.parse_plan_review(response)

            # PlanAdjustmentオブジェクトを作成
            adjustment = PlanAdjustment(
                timestamp=datetime.now(),
                analysis=review_result["analysis"],
                adjustments=review_result["adjustments"],
                future_plans=review_result["future_plans"],
                thinking_process=review_result["thinking_process"]
            )

            # StoryPlanに調整を適用
            self.story_context.story_plan.add_adjustment(adjustment)

            # ログに記録
            self.log_manager.log_structured_data("plan_review", {
                "section": section_count,
                "adjustment": adjustment.to_dict()
            })

            logger.info(f"計画見直しが完了し、更新を適用しました（セクション {section_count}）")

        except Exception as e:
            logger.error(f"計画見直し中にエラー: {str(e)}")
            raise