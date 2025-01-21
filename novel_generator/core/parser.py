# novel_generator/core/parser.py に以下の変更を適用してください

import re
from typing import List, Dict
from ..models.data_models import (
    Character,
    StoryBaseSettings,
    StorySection,
    StoryPlan,
    Progress,
    SectionData,
)
import logging

logger = logging.getLogger(__name__)


class ResponseParser:
    """LLMの応答を解析するクラス"""

    def extract_tag_content(self, text: str, tag: str) -> str:
        """XMLタグの内容を抽出"""
        if not text or not isinstance(text, str):
            logger.debug(f"無効な入力テキスト: {text}")
            return ""

        # タグを含むかどうかの簡易チェック
        if f"<{tag}>" not in text or f"</{tag}>" not in text:
            logger.debug(f"タグ {tag} が見つかりません")
            return ""

        try:
            # デバッグ用に検索パターンとテキストの一部を出力
            pattern = rf"<{tag}>\s*(.*?)\s*</{tag}>"
            logger.debug(f"検索パターン: {pattern}")
            logger.debug(f"テキストの一部: {text[:200]}...")  # 最初の200文字のみ

            matches = list(re.finditer(pattern, text, re.DOTALL))

            if not matches:
                logger.debug(f"タグ {tag} の内容を抽出できません")
                logger.debug(f"テキスト内のタグ位置: 開始={text.find(f'<{tag}>')}, 終了={text.find(f'</{tag}>')}")
                return ""

            content = matches[0].group(1).strip()
            return content

        except Exception as e:
            logger.error(f"タグ {tag} の抽出中にエラー: {str(e)}")
            return ""
            
    def extract_content_tag(self, text: str) -> str:
        """コンテントタグの内容を特別な方法で抽出

        Args:
            text (str): 対象テキスト

        Returns:
            str: 抽出された内容
        """
        if not text or not isinstance(text, str):
            return ""

        start_tag = "<content>"
        if start_tag not in text:
            # DEBUGレベルに変更（或いはログ自体を削除）
            logger.debug("content タグが見つかりません")
            return text  # タグがない場合はテキスト全体を返す

        # 開始位置を見つける
        start_pos = text.find(start_tag) + len(start_tag)
        
        # 以降のテキストを検索
        remaining_text = text[start_pos:]
        
        # 次の '<' を探す（他のタグの開始）
        next_tag_pos = remaining_text.find('<')
        
        # 明示的な終了タグを探す
        end_tag_pos = remaining_text.find('</content>')
        
        # 終了位置の決定
        if end_tag_pos != -1:
            # 明示的な終了タグが見つかった場合
            content = remaining_text[:end_tag_pos]
        elif next_tag_pos != -1:
            # 次のタグが見つかった場合
            content = remaining_text[:next_tag_pos]
        else:
            # どちらも見つからない場合は残りすべて
            content = remaining_text
        
        return content.strip()

    def extract_percentage(self, text: str) -> float:
        """進行度を表す数値を抽出

        Args:
            text (str): 対象テキスト

        Returns:
            float: 抽出された進行度。抽出失敗時は推定値を返す
        """
        # まず、数値のみを抽出してみる
        number_match = re.search(r"(\d+(?:\.\d+)?)", text)
        if number_match:
            try:
                value = float(number_match.group(1))
                if 0 <= value <= 100:
                    return value
            except ValueError:
                pass

        # 数値の抽出に失敗した場合、テキストから進行度を推定
        logger.warning(f"進行度の抽出に失敗しました。テキスト: {text}")
        if any(word in text.lower() for word in ["完了", "終了", "完結"]):
            return 100.0
        elif any(word in text.lower() for word in ["開始", "始め"]):
            return 0.0
        elif any(word in text.lower() for word in ["中盤", "半ば"]):
            return 50.0
        else:
            return 25.0  # デフォルト値

    def parse_section_data(self, response_text: str, thinking: str) -> SectionData:
        """セクションデータの解析

        Args:
            response_text (str): LLMからの応答テキスト
            thinking (str): 思考プロセス

        Returns:
            SectionData: 解析されたセクションデータ
        """
        # デフォルト値の設定
        default_content = "物語は続きます。次の展開に向けて..."
        default_preview = "次のセクションに続く"
        default_thinking = "物語の展開を考慮しています"

        try:
            # まず応答テキストの妥当性をチェック
            if not response_text or not isinstance(response_text, str):
                logger.error("無効な応答テキスト")
                raise ValueError("無効な応答テキスト")

            # thinkingの抽出と検証
            if not thinking:
                thinking = self.extract_tag_content(response_text, "thinking")
                if thinking:
                    logger.info("応答テキストから思考プロセスを抽出しました")

            if not thinking:
                logger.warning("思考プロセスが見つかりません")
                thinking = "物語の展開を考慮しています"  # デフォルト値

            # セクションの抽出
            section = self.extract_tag_content(response_text, "section")
            if not section:
                logger.warning(
                    "セクションタグが見つかりません。応答全体をコンテンツとして使用します"
                )
                section = response_text

            # 特別な content 抽出メソッドを使用
            content = self.extract_content_tag(section)
            if not content:
                logger.warning("コンテンツが抽出できません。セクション全体を使用します")
                content = section

            # 最低限の長さチェック
            if len(content.strip()) < 10:  # 極端に短い場合
                content = default_content
                logger.warning("コンテンツが極端に短いためデフォルト値を使用")

            # プログレス情報の抽出と解析
            progress_text = self.extract_tag_content(section, "progress")
            percentage = self.extract_percentage(
                self.extract_tag_content(progress_text, "percentage")
            )

            # 達成点と残り要素の抽出
            achieved_points = [
                point.strip()
                for point in self.extract_tag_content(
                    progress_text, "achieved_points"
                ).split("\n")
                if point.strip()
            ] or ["基本的な展開を達成"]

            remaining_points = [
                point.strip()
                for point in self.extract_tag_content(
                    progress_text, "remaining_points"
                ).split("\n")
                if point.strip()
            ] or ["さらなる展開"]

            # プログレスオブジェクトの作成
            progress = Progress(
                percentage=percentage,
                achieved_points=achieved_points,
                remaining_points=remaining_points,
            )

            # 次のプレビューの抽出
            next_preview = (
                self.extract_tag_content(section, "next_preview") or default_preview
            )

            # 最終的なSectionDataオブジェクトの作成
            return SectionData(
                content=content,
                progress=progress,
                next_preview=next_preview,
                thinking=thinking or default_thinking,
            )

        except Exception as e:
            logger.error(f"セクションデータの解析中にエラー: {str(e)}")
            # エラー時は最小限の情報でSectionDataを作成
            return SectionData(
                content=default_content,
                progress=Progress(
                    percentage=25.0,
                    achieved_points=["基本的な展開"],
                    remaining_points=["今後の展開"],
                ),
                next_preview=default_preview,
                thinking=default_thinking,
            )

    def parse_characters(self, text: str) -> List[Character]:
        """キャラクター情報のパース

        Args:
            text (str): キャラクター情報を含むテキスト

        Returns:
            List[Character]: キャラクター情報のリスト
        """
        characters = []
        character_blocks = re.findall(r"<character>(.*?)</character>", text, re.DOTALL)

        for block in character_blocks:
            character = Character(
                name=self.extract_tag_content(block, "name"),
                role=self.extract_tag_content(block, "role"),
                personality=self.extract_tag_content(block, "personality"),
            )
            characters.append(character)

        return characters

    def parse_base_settings(self, response_text: str) -> StoryBaseSettings:
        """基本設定の解析

        Args:
            response_text (str): LLMからの応答テキスト

        Returns:
            StoryBaseSettings: 解析された基本設定
        """
        story_base = self.extract_tag_content(response_text, "story_base")
        thinking = self.extract_tag_content(response_text, "thinking")

        themes = self.extract_tag_content(story_base, "themes").split("\n")
        characters = self.parse_characters(story_base)
        world_setting = self.extract_tag_content(story_base, "world_setting")
        tone = self.extract_tag_content(story_base, "tone")

        return StoryBaseSettings(
            themes=themes,
            characters=characters,
            world_setting=world_setting,
            tone=tone,
            thinking_process=thinking,
        )

    def parse_story_plan(self, response_text: str) -> StoryPlan:
        """展開計画の解析

        Args:
            response_text (str): LLMからの応答テキスト

        Returns:
            StoryPlan: 解析された展開計画
        """
        story_plan = self.extract_tag_content(response_text, "story_plan")
        thinking = self.extract_tag_content(response_text, "thinking")

        # 各要素の抽出
        outline = self.extract_tag_content(story_plan, "outline")
        major_points = self._parse_major_points(story_plan)
        sections = self._parse_planned_sections(story_plan)
        foreshadowing = self._parse_foreshadowing(story_plan)

        return StoryPlan(
            outline=outline,
            major_points=major_points,
            sections=sections,
            foreshadowing=foreshadowing,
            thinking_process=thinking,
        )

    def _parse_major_points(self, text: str) -> List[str]:
        """重要な展開点のパース

        Args:
            text (str): 展開点情報を含むテキスト

        Returns:
            List[str]: 展開点のリスト
        """
        major_points_text = self.extract_tag_content(text, "major_points")
        points = re.findall(r"<point>(.*?)</point>", major_points_text, re.DOTALL)
        return [point.strip() for point in points]

    def _parse_planned_sections(self, text: str) -> List[StorySection]:
        """計画されたセクションのパース

        Args:
            text (str): セクション情報を含むテキスト

        Returns:
            List[StorySection]: セクション情報のリスト
        """
        sections = []
        section_blocks = re.findall(r"<section>(.*?)</section>", text, re.DOTALL)

        for block in section_blocks:
            section = StorySection(
                content=self.extract_tag_content(block, "content"),
                goals=self.extract_tag_content(block, "goals"),
            )
            sections.append(section)

        return sections

    def parse_plan_review(self, response_text: str) -> Dict[str, str]:
        """計画見直しの結果をパース

        Args:
            response_text (str): LLMからの応答テキスト

        Returns:
            Dict[str, str]: 解析された計画見直し結果
            {
                "analysis": "現状の分析結果",
                "adjustments": "必要な調整事項",
                "future_plans": "今後の展開方針",
                "thinking_process": "思考プロセス"
            }
        """
        try:
            # plan_reviewブロックを取得
            plan_review_block = self.extract_tag_content(response_text, "plan_review")
            if not plan_review_block:
                logger.warning("plan_reviewタグが見つかりません")
                plan_review_block = response_text

            # 各要素の抽出
            analysis = self.extract_tag_content(plan_review_block, "analysis")
            adjustments = self.extract_tag_content(plan_review_block, "adjustments")
            future_plans = self.extract_tag_content(plan_review_block, "future_plans")
            thinking = self.extract_tag_content(response_text, "thinking")

            # 結果の構築
            result = {
                "analysis": analysis or "分析情報なし",
                "adjustments": adjustments or "調整不要",
                "future_plans": future_plans or "計画の継続",
                "thinking_process": thinking or "思考プロセスなし",
            }

            # 結果の検証
            if not any([analysis, adjustments, future_plans]):
                logger.warning("計画見直しの結果が不完全です")

            return result

        except Exception as e:
            logger.error(f"計画見直しの解析中にエラー: {str(e)}")
            # 最小限の情報を持つ結果を返す
            return {
                "analysis": "解析エラー",
                "adjustments": "調整不要",
                "future_plans": "計画を継続",
                "thinking_process": "エラーにより解析不可",
            }

    def _parse_foreshadowing(self, text: str) -> List[str]:
        """伏線要素のパース

        Args:
            text (str): 伏線情報を含むテキスト

        Returns:
            List[str]: 伏線要素のリスト
        """
        foreshadowing_text = self.extract_tag_content(text, "foreshadowing")
        elements = re.findall(
            r"<element>(.*?)</element>", foreshadowing_text, re.DOTALL
        )
        return [element.strip() for element in elements]
