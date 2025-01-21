from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field

@dataclass
class Progress:
    """進行状況を表すデータクラス"""
    percentage: float
    achieved_points: List[str]
    remaining_points: List[str]

@dataclass
class SectionData:
    """セクションデータを表すデータクラス"""
    content: str
    progress: Progress
    next_preview: str
    thinking: str

@dataclass
class Character:
    """キャラクター情報を表すデータクラス"""
    name: str
    role: str
    personality: str

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return asdict(self)

@dataclass
class StoryBaseSettings:
    """物語の基本設定を表すデータクラス"""
    themes: List[str]
    characters: List[Character]
    world_setting: str
    tone: str
    thinking_process: str

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "themes": self.themes,
            "characters": [c.to_dict() for c in self.characters],
            "world_setting": self.world_setting,
            "tone": self.tone,
            "thinking_process": self.thinking_process,
        }

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field

@dataclass
class PlanAdjustment:
    """計画の調整内容を表すデータクラス"""
    timestamp: datetime
    analysis: str
    adjustments: str
    future_plans: str
    thinking_process: str

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "analysis": self.analysis,
            "adjustments": self.adjustments,
            "future_plans": self.future_plans,
            "thinking_process": self.thinking_process,
        }

@dataclass
class StoryPlan:
    """物語の展開計画を表すデータクラス"""
    outline: str
    major_points: List[str]
    sections: List["StorySection"]
    foreshadowing: List[str]
    thinking_process: str
    adjustments: List[PlanAdjustment] = field(default_factory=list)
    
    def add_adjustment(self, adjustment: PlanAdjustment) -> None:
        """計画の調整を追加"""
        self.adjustments.append(adjustment)
        self._apply_adjustment(adjustment)
    
    def _apply_adjustment(self, adjustment: PlanAdjustment) -> None:
        """調整内容を現在の計画に適用"""
        # 将来の展開計画を更新
        remaining_sections = len(self.sections)
        if remaining_sections > 0:
            # 残りのセクションの目標を調整
            for section in self.sections[-remaining_sections:]:
                section.update_goals(adjustment.future_plans)
        
        # 主要な展開ポイントを更新（必要に応じて）
        if adjustment.adjustments:
            self._update_major_points(adjustment.adjustments)
    
    def _update_major_points(self, adjustments: str) -> None:
        """主要な展開ポイントを更新"""
        # 既存の展開ポイントを保持しながら、新しい要素を追加
        new_points = [point.strip() for point in adjustments.split("\n") if point.strip()]
        self.major_points.extend(new_points)

    def get_latest_adjustment(self) -> Optional[PlanAdjustment]:
        """最新の調整内容を取得"""
        return self.adjustments[-1] if self.adjustments else None

    def get_current_plan_state(self) -> Dict[str, Any]:
        """現在の計画状態を取得"""
        return {
            "outline": self.outline,
            "major_points": self.major_points,
            "sections": [s.to_dict() for s in self.sections],
            "foreshadowing": self.foreshadowing,
            "thinking_process": self.thinking_process,
            "latest_adjustment": self.get_latest_adjustment().to_dict() if self.get_latest_adjustment() else None
        }

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "outline": self.outline,
            "major_points": self.major_points,
            "sections": [s.to_dict() for s in self.sections],
            "foreshadowing": self.foreshadowing,
            "thinking_process": self.thinking_process,
            "adjustments": [adj.to_dict() for adj in self.adjustments],
        }

@dataclass
class StorySection:
    """計画されたセクションを表すデータクラス"""
    content: str
    goals: str
    adjusted_goals: List[str] = field(default_factory=list)

    def update_goals(self, new_goals: str) -> None:
        """目標を更新"""
        self.adjusted_goals.append(new_goals)

    def get_current_goals(self) -> str:
        """現在の目標を取得"""
        return self.adjusted_goals[-1] if self.adjusted_goals else self.goals

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "content": self.content,
            "goals": self.goals,
            "adjusted_goals": self.adjusted_goals,
        }

@dataclass
class GenerationMetadata:
    """生成メタデータを表すデータクラス"""
    status: str
    current_section: int
    timestamp: datetime
    progress: float = 0.0
    error_message: Optional[str] = None

@dataclass
class StoryContext:
    """物語のコンテキストを表すデータクラス"""
    story_setting: str
    total_length: str
    base_settings: Optional[StoryBaseSettings] = None
    story_plan: Optional[StoryPlan] = None
    sections: List[SectionData] = field(default_factory=list)
    progress: float = 0.0
    current_length: int = 0