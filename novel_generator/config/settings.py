from typing import Dict
import yaml
import os
import logging
from logging import getLogger

logger = getLogger(__name__)


def get_default_config() -> Dict:
    """デフォルト設定の取得"""
    return {
        "api_key": os.environ.get("GEMINI_API_KEY", "YOUR-API-KEY"),
        "output_dir": "novel_output",
        "generation": {"max_sections": 20, "length": "中編（3万字程度）"},
        "story_setting": """
        近未来の日本を舞台に、自然との繋がりを失いつつある世界で、
        高校生の主人公が古い伝説に導かれながら神秘的な森の秘密を探る物語。
        主人公は両親の離婚後、祖母と暮らしており、古い伝承に強い興味を持っている。
        クラスメイトの女子生徒は、科学者の家庭で育ったが、
        理屈では説明できない現象に惹かれている。
        """,
        "model": {
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        },
    }


def load_config(config_path: str = "config.yaml") -> Dict:
    """設定ファイルの読み込み（デフォルト設定対応版）"""
    default_config = get_default_config()

    if not os.path.exists(config_path):
        logger.warning(f"設定ファイルが見つかりません: {config_path}")
        logger.info("デフォルト設定を使用します")
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logger.info("設定ファイルを読み込みました")

            # デフォルト設定とマージ
            merged_config = default_config.copy()
            merged_config.update(config)
            return merged_config

    except Exception as e:
        logger.error(f"設定ファイルの読み込み中にエラー: {str(e)}")
        logger.info("デフォルト設定を使用します")
        return default_config
