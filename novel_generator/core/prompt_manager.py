"""プロンプト管理を行うメインクラスを提供するモジュール"""

from typing import Dict, Any
import json
import logging
from dataclasses import asdict

from .prompts.templates import TEMPLATES
from .prompts.exceptions import (
    TemplateNotFoundError,
    RequiredParameterError,
    TemplateFormatError,
)
from ..models.data_models import StoryContext, StoryBaseSettings

logger = logging.getLogger(__name__)


class PromptManager:
    """プロンプト管理クラス"""

    def __init__(self):
        """PromptManagerの初期化"""
        self.templates = TEMPLATES

    def _validate_required_params(
        self, template_name: str, params: Dict[str, Any], required_params: list
    ) -> None:
        """必須パラメータの存在確認

        Args:
            template_name (str): テンプレート名
            params (Dict[str, Any]): パラメータ辞書
            required_params (list): 必須パラメータのリスト

        Raises:
            RequiredParameterError: 必須パラメータが不足している場合
        """
        for param in required_params:
            if param not in params or params[param] is None:
                raise RequiredParameterError(param, template_name)

    def _format_template(
        self, template_name: str, template: str, params: Dict[str, Any]
    ) -> str:
        """テンプレートの書式設定

        Args:
            template_name (str): テンプレート名
            template (str): テンプレート文字列
            params (Dict[str, Any]): パラメータ辞書

        Returns:
            str: 書式設定されたプロンプト

        Raises:
            TemplateFormatError: テンプレートの書式設定に失敗した場合
        """
        try:
            return template.format(**params)
        except Exception as e:
            raise TemplateFormatError(template_name, e)

    def get_base_settings_prompt(self, story_setting: str, total_length: str) -> str:
        """基本設定生成用プロンプトの取得

        Args:
            story_setting (str): 物語の設定
            total_length (str): 想定される物語の長さ

        Returns:
            str: 生成用プロンプト

        Raises:
            TemplateNotFoundError: テンプレートが見つからない場合
            RequiredParameterError: 必須パラメータが不足している場合
            TemplateFormatError: テンプレートの書式設定に失敗した場合
        """
        template_name = "base_settings"
        if template_name not in self.templates:
            raise TemplateNotFoundError(template_name)

        params = {
            "story_setting": story_setting,
            "total_length": total_length,
        }

        self._validate_required_params(
            template_name, params, ["story_setting", "total_length"]
        )

        return self._format_template(
            template_name, self.templates[template_name], params
        )

    def get_story_plan_prompt(
        self,
        base_settings: StoryBaseSettings,
        story_setting: str,
    ) -> str:
        """展開計画生成用プロンプトの取得

        Args:
            base_settings (StoryBaseSettings): 基本設定情報
            story_setting (str): 物語の設定

        Returns:
            str: 生成用プロンプト

        Raises:
            TemplateNotFoundError: テンプレートが見つからない場合
            RequiredParameterError: 必須パラメータが不足している場合
            TemplateFormatError: テンプレートの書式設定に失敗した場合
        """
        template_name = "story_plan"
        if template_name not in self.templates:
            raise TemplateNotFoundError(template_name)

        # 基本設定をJSON形式に変換
        base_settings_dict = asdict(base_settings)
        base_settings_json = json.dumps(
            base_settings_dict, ensure_ascii=False, indent=2
        )

        params = {
            "story_setting": story_setting,
            "base_settings": base_settings_json,
        }

        self._validate_required_params(
            template_name, params, ["story_setting", "base_settings"]
        )

        return self._format_template(
            template_name, self.templates[template_name], params
        )

    def get_section_generation_prompt(
        self, story_context: StoryContext, section_count: int
    ) -> str:
        """セクション生成用プロンプトの取得（計画調整を反映）"""
        template_name = "section_generation"
        if template_name not in self.templates:
            raise TemplateNotFoundError(template_name)

        # 基本設定をJSON形式に変換
        base_settings_json = json.dumps(
            asdict(story_context.base_settings), ensure_ascii=False, indent=2
        )

        # 最新の計画状態を取得（調整履歴を含む）
        current_plan = story_context.story_plan.get_current_plan_state()
        story_plan_json = json.dumps(current_plan, ensure_ascii=False, indent=2)

        # これまでの内容を取得
        current_content = "\n\n".join([
            section.content for section in story_context.sections
        ])

        # 現在の文字数を計算
        current_length = sum(len(section.content) for section in story_context.sections)

        # 最新の計画調整を取得
        latest_adjustment = story_context.story_plan.get_latest_adjustment()
        adjustment_info = ""
        if latest_adjustment:
            adjustment_info = f"""
    直近の計画調整:
    - 分析: {latest_adjustment.analysis}
    - 調整内容: {latest_adjustment.adjustments}
    - 今後の展開方針: {latest_adjustment.future_plans}
    """

        params = {
            "base_settings": base_settings_json,
            "story_plan": story_plan_json,
            "current_content": current_content,
            "section_number": section_count,
            "current_length": current_length,
            "total_length": story_context.total_length,
            "plan_adjustments": adjustment_info
        }

        self._validate_required_params(
            template_name, 
            params, 
            ["base_settings", "story_plan", "section_number", "total_length"]
        )

        return self._format_template(
            template_name, self.templates[template_name], params
        )

    def get_plan_review_prompt(
        self, story_context: StoryContext, section_count: int
    ) -> str:
        """計画見直し用プロンプトの取得

        Args:
            story_context (StoryContext): 物語のコンテキスト
            section_count (int): 現在のセクション番号

        Returns:
            str: 生成用プロンプト
        """
        template_name = "plan_review"
        if template_name not in self.templates:
            raise TemplateNotFoundError(template_name)

        # 各要素をJSON形式に変換
        base_settings_json = json.dumps(
            asdict(story_context.base_settings), ensure_ascii=False, indent=2
        )

        story_plan_json = json.dumps(
            asdict(story_context.story_plan), ensure_ascii=False, indent=2
        )

        # 直近のセクションのサマリーを生成
        current_content = self._generate_content_summary(story_context.sections)

        # 文字数情報の追加
        length_info = {
            "current_length": story_context.current_length,
            "total_length_setting": story_context.total_length,
            "sections_completed": len(story_context.sections),
            "average_section_length": (
                story_context.current_length / len(story_context.sections)
                if story_context.sections
                else 0
            )
        }
        length_info_json = json.dumps(length_info, ensure_ascii=False, indent=2)

        params = {
            "base_settings": base_settings_json,
            "story_plan": story_plan_json,
            "section_count": section_count,
            "current_content": current_content,
            "length_info": length_info_json,
        }

        self._validate_required_params(
            template_name,
            params,
            ["base_settings", "story_plan", "section_count", "current_content", "length_info"]
        )

        return self._format_template(
            template_name, self.templates[template_name], params
        )

    def _generate_content_summary(self, sections: list) -> str:
        """セクションの内容サマリーを生成

        Args:
            sections (list): セクションのリスト

        Returns:
            str: サマリー文字列
        """
        # 最新の3セクションのみを使用
        recent_sections = sections[-3:]
        summaries = []

        for i, section in enumerate(recent_sections):
            section_num = len(sections) - len(recent_sections) + i + 1
            # 各セクションの最初の200文字を使用
            content_preview = section.content[:200] + "..."
            summaries.append(f"セクション{section_num}:\n{content_preview}")

        return "\n\n".join(summaries)

    def add_template(self, name: str, template: str) -> None:
        """新しいテンプレートを追加

        Args:
            name (str): テンプレート名
            template (str): テンプレート文字列

        Raises:
            ValueError: 既存のテンプレート名が指定された場合
        """
        if name in self.templates:
            raise ValueError(f"テンプレート '{name}' は既に存在します")

        self.templates[name] = template
        logger.info(f"新しいテンプレート '{name}' を追加しました")

    def update_template(self, name: str, template: str) -> None:
        """既存のテンプレートを更新

        Args:
            name (str): テンプレート名
            template (str): 新しいテンプレート文字列

        Raises:
            TemplateNotFoundError: 指定されたテンプレートが存在しない場合
        """
        if name not in self.templates:
            raise TemplateNotFoundError(name)

        self.templates[name] = template
        logger.info(f"テンプレート '{name}' を更新しました")
