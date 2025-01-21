import logging
import os


def setup_logging(output_dir: str, log_level: int = logging.INFO) -> None:
    """ロギングの初期設定

    Args:
        output_dir (str): ログファイル出力ディレクトリ
        log_level (int): ログレベル（デフォルト: logging.INFO）
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                os.path.join(output_dir, "novel_generation.log"), encoding="utf-8"
            ),
        ],
    )
