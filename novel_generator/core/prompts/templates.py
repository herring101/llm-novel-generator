"""プロンプトテンプレートを管理するモジュール"""

# 基本設定生成用テンプレート
BASE_SETTINGS_TEMPLATE = """あなたは小説家です。以下の設定に基づいて、物語の基本設定を考えてください。

重要: 必ず以下の順序で回答を構築してください。各ステップは必須です：

1. まず<thinking>タグ内で、物語の方向性について具体的に考察を記述してください。
2. 次に、その思考プロセスに基づいて、<story_base>タグ内に具体的な設定を記述してください。

ユーザーからの依頼内容：
{story_setting}

想定の長さ：{total_length}

<thinking>
物語の基本設定について、以下の点を具体的に考察します：

1. 物語のテーマ：
   [選定した2-3個のテーマとその理由を具体的に記述]

2. キャラクター構成：
   [主要キャラクターの設定根拠とその狙いを具体的に記述]

3. 世界観とトーン：
   [選択した世界観・トーンの意図と期待される効果を具体的に記述]
</thinking>

<story_base>
<themes>
[上記の思考プロセスで選定したテーマを箇条書きで記述]
</themes>

<characters>
<character>
<name>[キャラクター名]</name>
<role>[役割]</role>
<personality>[性格・特徴]</personality>
</character>
[必要に応じて追加のキャラクター]
</characters>

<world_setting>[世界観の詳細]</world_setting>
<tone>[物語全体のトーンや雰囲気]</tone>
</story_base>"""

# 展開計画生成用テンプレート
STORY_PLAN_TEMPLATE = """以下の基本設定に基づいて、物語の展開計画を立ててください。

重要: 必ず以下の順序で回答を構築してください：

1. まず<thinking>タグ内で、展開計画の方針について具体的に考察を記述してください。
2. 次に、その思考プロセスに基づいて、<story_plan>タグ内に具体的な計画を記述してください。

ユーザーからの依頼内容：
{story_setting}

基本設定：
{base_settings}

<thinking>
展開計画について、以下の点を具体的に考察します：

1. 物語構造：
   [選択した物語構造とその理由を具体的に記述]

2. 重要な転換点：
   [主要な転換点の配置とその意図を具体的に記述]

3. 伏線計画：
   [伏線の配置計画とその回収方針を具体的に記述]

4. 展開の緩急：
   [テンポの設計と読者への効果を具体的に記述]
</thinking>

<story_plan>
<outline>[物語の概要：上記の思考プロセスを反映]</outline>

<major_points>
<point>[重要な展開点とその位置付け]</point>
[必要に応じて追加の展開点]
</major_points>

<sections>
<section>
<content>内容の概要</content>
<goals>達成すべき要素</goals>
</section>
[必要に応じて追加のセクション]
</sections>

<foreshadowing>
<element>[伏線要素と回収計画]</element>
[必要に応じて追加の伏線要素]
</foreshadowing>
</story_plan>"""

# セクション生成用テンプレート
SECTION_GENERATION_TEMPLATE = """以下の情報に基づいて、物語の次のセクションを書いてください。

重要: 必ず以下の順序で回答を構築してください：

1. まず<thinking>タグ内で、このセクションの執筆方針について具体的に考察を記述してください。
2. 次に、その思考プロセスに基づいて、<section>タグ内に具体的な内容を記述してください。

ユーザーからの依頼内容：
{story_setting}

基本設定：
{base_settings}

展開計画：
{story_plan}

これまでの内容：
{current_content}

想定の長さ：{total_length}
現在の文字数：{current_length}文字

<thinking>
このセクションについて、以下の点を具体的に考察します：

1. 展開方針：
   [このセクションでの展開内容とその意図を具体的に記述]

2. キャラクターの動き：
   [登場するキャラクターの行動理由と狙いを具体的に記述]

3. 前セクションからの接続：
   [前セクションからの展開の自然さと工夫を具体的に記述]

4. 伏線の扱い：
   [このセクションでの伏線の配置または回収方針を具体的に記述]
</thinking>

<section>
    <content>
[上記の思考プロセスに基づいて、セクションの本文を記述。
プレーンテキストで、設定等は含めない。
100行4000字程度で記述
**短い場合もう一度書くことになるので絶対に絶対に絶対に守ってください。20行とか許されません**]
    </content>

    <progress>
        <percentage>[物語全体の進行度（0-100）]</percentage>
        
        <achieved_points>
        [このセクションで達成した要素を箇条書きで記述]
        </achieved_points>
        
        <remaining_points>
        [今後達成すべき要素を箇条書きで記述]
        </remaining_points>
    </progress>

<next_preview>[次のセクションでの展開予定]</next_preview>
</section>"""

# 計画見直し用テンプレート
PLAN_REVIEW_TEMPLATE = """現在の進行状況に基づいて、計画の見直しを行ってください。

重要: 必ず以下の順序で回答を構築してください：

1. まず<thinking>タグ内で、計画の見直しポイントについて具体的に考察を記述してください。
2. 次に、その思考プロセスに基づいて、<plan_review>タグ内に具体的な見直し内容を記述してください。

ユーザーからの依頼内容：
{story_setting}

基本設定：
{base_settings}

現在の計画：
{story_plan}

現在の状況：
- セクション数: {section_count}
- これまでの内容: {current_content}

文字数の状況：
{length_info}

<thinking>
計画の見直しについて、以下の点を具体的に考察します：

1. 現状分析：
   [現在までの展開の評価と課題を具体的に記述]

2. 計画との差異：
   [当初の計画との違いとその理由を具体的に記述]

3. 調整の必要性：
   [必要な調整の内容と理由を具体的に記述]

4. 今後の方針：
   [調整を踏まえた今後の展開方針を具体的に記述]
</thinking>

<plan_review>
<analysis>[現状の詳細な分析]</analysis>
<adjustments>[必要な調整事項の具体的な内容]</adjustments>
<future_plans>[調整後の具体的な展開方針]</future_plans>
</plan_review>"""

# テンプレート辞書
TEMPLATES = {
    "base_settings": BASE_SETTINGS_TEMPLATE,
    "story_plan": STORY_PLAN_TEMPLATE,
    "section_generation": SECTION_GENERATION_TEMPLATE,
    "plan_review": PLAN_REVIEW_TEMPLATE,
}
