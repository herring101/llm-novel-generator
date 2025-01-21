from novel_generator.config.settings import load_config
from novel_generator.core.novel_generator import NovelGenerator

def main():
    # 設定の読み込み
    config = load_config()

    # 生成器の初期化
    generator = NovelGenerator(config)

    # 物語の生成
    story = generator.generate_story(
        max_sections=config["generation"]["max_sections"],
        total_length=config["generation"]["length"],
    )
    print(story)

    # 文字数の最終表示
    print(f"\n=== 最終文字数: {generator.get_current_length()}文字 ===")

if __name__ == "__main__":
    main()