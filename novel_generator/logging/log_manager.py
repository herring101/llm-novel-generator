import os
from datetime import datetime
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class LogManager:
    def __init__(self, output_dir: str, parser):
        self.output_dir = output_dir
        self.parser = parser
        self._ensure_output_directory()

        self.raw_log_file = os.path.join(output_dir, "raw_llm_output.log")
        self.thinking_file = os.path.join(output_dir, "thinking_process.txt")
        self.structured_log_file = os.path.join(output_dir, "generation_log.jsonl")
        self._initialize_logs()

    def _initialize_logs(self) -> None:
        """ログファイルの初期化"""
        with open(self.raw_log_file, "w", encoding="utf-8") as f:
            f.write("=== LLM Raw Output Log ===\n\n")

        with open(self.thinking_file, "w", encoding="utf-8") as f:
            f.write("=== 思考プロセスログ ===\n\n")

    def log_thinking_process(self, phase: str, thinking: str) -> None:
        """思考プロセスの記録"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"""
=== {phase} ===
Timestamp: {timestamp}

思考プロセス:
{thinking}

{"=" * 50}
"""
        with open(self.thinking_file, "a", encoding="utf-8") as f:
            f.write(content)

    def log_llm_interaction(self, phase: str, prompt: str, response: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 思考プロセスの抽出と記録
        thinking = self.parser.extract_tag_content(response, "thinking")
        if thinking:
            self.log_thinking_process(phase, thinking)  # thinking_processの記録を追加

        log_content = f"""
=== {phase} ===
Timestamp: {timestamp}

--- Prompt ---
{prompt}

--- Response ---
{response}

{"=" * 50}
"""
        with open(self.raw_log_file, "a", encoding="utf-8") as f:
            f.write(log_content)

    def _ensure_output_directory(self) -> None:
        """出力ディレクトリの確保"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"出力ディレクトリを作成しました: {self.output_dir}")

    def log_structured_data(self, phase: str, data: Dict[str, Any]) -> None:
        """構造化データの記録

        Args:
            phase (str): 処理フェーズ名
            data (Dict[str, Any]): 記録するデータ
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "data": data,
        }
        with open(self.structured_log_file, "a", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write("\n\n")
