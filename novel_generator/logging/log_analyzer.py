import os
import re
from typing import List, Dict, Any
from datetime import datetime


class LogAnalyzer:
    """ログ分析ユーティリティ"""

    def __init__(self, output_dir: str):
        """初期化

        Args:
            output_dir (str): ログファイルのあるディレクトリ
        """
        self.output_dir = output_dir
        self.raw_log_file = os.path.join(output_dir, "raw_llm_output.log")
        self.thinking_file = os.path.join(output_dir, "thinking_process.txt")
        self.structured_log = os.path.join(output_dir, "generation_log.jsonl")
        self.length_log_file = os.path.join(output_dir, "length_progress.log")

    def get_all_llm_interactions(self) -> List[Dict[str, str]]:
        """すべてのLLMとのやり取りを取得"""
        interactions = []
        with open(self.raw_log_file, "r", encoding="utf-8") as f:
            content = f.read()
            sections = content.split("=" * 50)

            for section in sections:
                if not section.strip():
                    continue

                # セクションからデータを抽出
                timestamp_match = re.search(r"Timestamp: (.*?)\n", section)
                prompt_match = re.search(
                    r"--- Prompt ---\n(.*?)\n--- Response ---", section, re.DOTALL
                )
                response_match = re.search(
                    r"--- Response ---\n(.*?)$", section, re.DOTALL
                )

                if timestamp_match and prompt_match and response_match:
                    interactions.append({
                        "timestamp": timestamp_match.group(1).strip(),
                        "prompt": prompt_match.group(1).strip(),
                        "response": response_match.group(1).strip(),
                    })

        return interactions

    def get_thinking_process_timeline(self) -> List[Dict[str, str]]:
        """思考プロセスのタイムラインを取得"""
        timeline = []
        with open(self.thinking_file, "r", encoding="utf-8") as f:
            content = f.read()
            sections = content.split("=" * 50)

            for section in sections:
                if not section.strip():
                    continue

                # セクションからデータを抽出
                phase_match = re.search(r"=== (.*?) ===", section)
                timestamp_match = re.search(r"Timestamp: (.*?)\n", section)
                thinking_match = re.search(r"思考プロセス:\n(.*?)$", section, re.DOTALL)

                if phase_match and timestamp_match and thinking_match:
                    timeline.append({
                        "phase": phase_match.group(1).strip(),
                        "timestamp": timestamp_match.group(1).strip(),
                        "thinking": thinking_match.group(1).strip(),
                    })

        return timeline

    def analyze_generation_process(self) -> Dict[str, Any]:
        """生成プロセスの分析"""
        interactions = self.get_all_llm_interactions()
        thinking_timeline = self.get_thinking_process_timeline()

        # 基本的な統計情報
        stats = {
            "total_interactions": len(interactions),
            "total_thinking_processes": len(thinking_timeline),
            "generation_duration": None,
            "phases": {},
        }

        # 時系列での分析
        if interactions:
            first_timestamp = datetime.strptime(
                interactions[0]["timestamp"], "%Y-%m-%d %H:%M:%S"
            )
            last_timestamp = datetime.strptime(
                interactions[-1]["timestamp"], "%Y-%m-%d %H:%M:%S"
            )
            stats["generation_duration"] = str(last_timestamp - first_timestamp)

        # フェーズごとの分析
        for entry in thinking_timeline:
            phase = entry["phase"]
            if phase not in stats["phases"]:
                stats["phases"][phase] = {"count": 0, "thinking_samples": []}
            stats["phases"][phase]["count"] += 1
            stats["phases"][phase]["thinking_samples"].append(entry["thinking"])

        return stats

    def analyze_length_progress(self) -> Dict[str, Any]:
        """文字数の進捗状況を分析

        Returns:
            Dict[str, Any]: 文字数の進捗分析結果
        """
        progress_data = []
        try:
            with open(self.length_log_file, "r", encoding="utf-8") as f:
                # ヘッダーをスキップ
                next(f)
                next(f)

                for line in f:
                    if line.strip():
                        timestamp, section, current, target, percentage = (
                            line.strip().split(",")
                        )
                        progress_data.append({
                            "timestamp": timestamp,
                            "section": int(section),
                            "current_length": int(current),
                            "target_length": int(target),
                            "percentage": float(percentage.strip("%")),
                        })

            if not progress_data:
                return {"error": "進捗データが見つかりません"}

            latest = progress_data[-1]

            # 分析結果の作成
            analysis = {
                "current_status": {
                    "current_length": latest["current_length"],
                    "target_length": latest["target_length"],
                    "completion_percentage": latest["percentage"],
                    "remaining_length": latest["target_length"]
                    - latest["current_length"],
                },
                "progress_history": progress_data,
                "section_analysis": {
                    "total_sections": len(progress_data),
                    "average_length_per_section": latest["current_length"]
                    / len(progress_data)
                    if progress_data
                    else 0,
                },
                "pace_analysis": {
                    "estimated_sections_needed": int(
                        (latest["target_length"] - latest["current_length"])
                        / (latest["current_length"] / len(progress_data))
                    )
                    if progress_data and latest["current_length"] > 0
                    else 0
                },
            }

            return analysis

        except Exception as e:
            return {"error": f"分析中にエラーが発生しました: {str(e)}"}

    def get_length_progress_summary(self) -> str:
        """文字数の進捗サマリーを取得

        Returns:
            str: 進捗サマリーテキスト
        """
        analysis = self.analyze_length_progress()
        if "error" in analysis:
            return f"エラー: {analysis['error']}"

        current = analysis["current_status"]

        summary = f"""
=== 文字数進捗サマリー ===
現在の文字数: {current["current_length"]} 文字
目標文字数: {current["target_length"]} 文字
達成率: {current["completion_percentage"]:.1f}%
残り必要文字数: {current["remaining_length"]} 文字

セクション情報:
- 合計セクション数: {analysis["section_analysis"]["total_sections"]}
- セクションあたりの平均文字数: {analysis["section_analysis"]["average_length_per_section"]:.1f}
- 推定残りセクション数: {analysis["pace_analysis"]["estimated_sections_needed"]}
"""
        return summary
