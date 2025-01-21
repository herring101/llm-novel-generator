# Novel Generator

AIを活用した小説生成システム

## 概要

このシステムは、大規模言語モデル（LLM）を活用して、設定に基づいた小説を自動生成します。以下の特徴があります：

- 複数のLLMに対応（現在はGemini APIをサポート）
- 物語の設定から展開までを体系的に生成
- 進行状況のモニタリングと調整機能
- 詳細なログ出力とエラーハンドリング

## インストール
uv が必要です。https://docs.astral.sh/uv/getting-started/installation/#standalone-installer

```bash
git clone [repository-url]
cd novel-generator
uv sync
```

## 必要なパッケージ

- google-generativeai
- pyyaml
- logging

## 使い方

### 1. 設定ファイルの準備

`config.yaml`を作成し、必要な設定を記述します：
もともと書かれている設定を参考に、必要な項目を追加・変更してください。
基本的に①`output_dir`、②`api_key`、③`story_setting`、④`generation`の4つの項目を設定設定すれば、物語の生成が可能です。
```yaml
# 基本設定
output_dir: "novel_output" # ①出力ディレクトリ
llm_type: "gemini"

# LLMの設定
llm_config:
  api_key: "YOUR-GEMINI-API-KEY" # ②APIキー
  model_name: "gemini-1.5-pro"
  model:
    temperature: 0.9
    top_p: 0.95
    top_k: 64
    max_output_tokens: 8192

# 物語の設定
story_setting: | # ③物語の設定
  近未来の日本を舞台に、自然との繋がりを失いつつある世界で、
  高校生の主人公が古い伝説に導かれながら神秘的な森の秘密を探る物語。
  主人公は両親の離婚後、祖母と暮らしており、古い伝承に強い興味を持っている。

# 生成設定
generation:
  max_sections: 30
  length: "中編（3万字程度）" # ④物語の長さ
```

### 2. プログラムの実行

基本的にmain.pyを実行すれば大丈夫です。
インストールの作業を行った後
```sh
python main.py
```

### 3. カスタマイズ

#### 物語の長さ指定
```python
story = generator.generate_story(
    max_sections=15,
    total_length="短編（1万字程度）"
)
```

#### 生成状況の確認
```python
status = generator.get_generation_status()
print(f"生成状況: {status['status']}")
print(f"進行度: {status['progress']}%")
```

## 出力ファイル

生成された物語とログは`output_dir`で指定したディレクトリに出力されます：

- `story.txt`: 生成された物語本文
- `metadata.json`: 生成状況のメタデータ
- `novel_generation.log`: 詳細なログ
- `raw_llm_output.log`: LLMとのやり取りログ
- `thinking_process.txt`: 思考プロセスのログ
- `generation_log.jsonl`: 構造化されたログデータ

## エラーハンドリング

主なエラーとその対処方法：

1. API Key関連
```python
ValueError: Invalid API key
# -> llm_configのapi_keyを正しく設定してください
```

2. 設定不足
```python
ValueError: 必須の設定 'xxx' が不足しています
# -> config.yamlの必須項目を確認してください
```

3. 生成エラー
```python
Exception: セクション生成中にエラー
# -> ログを確認し、エラーの詳細を確認してください
```

## 拡張

### 新しいLLMの追加

1. `novel_generator/llm/`に新しいLLMクラスを作成：
```python
from .base import BaseLLM

class NewLLM(BaseLLM):
    def initialize(self) -> None:
        # 初期化処理
        pass
        
    def generate(self, prompt: str) -> str:
        # 生成処理
        pass
```

2. `LLMFactory`に新しいLLMを登録：
```python
SUPPORTED_LLMS = {
    "gemini": GeminiLLM,
    "new_llm": NewLLM,  # 追加
}
```

## ライセンス

MITライセンス

## 貢献

バグ報告や機能改善の提案は、Issueやプルリクエストでお願いします。
