"""プロンプト関連の例外クラスを定義するモジュール"""


class PromptError(Exception):
    """プロンプト関連の基底例外クラス"""

    pass


class TemplateNotFoundError(PromptError):
    """テンプレートが見つからない場合の例外"""

    def __init__(self, template_name: str):
        self.template_name = template_name
        super().__init__(f"テンプレート '{template_name}' が見つかりません")


class RequiredParameterError(PromptError):
    """必須パラメータが不足している場合の例外"""

    def __init__(self, parameter_name: str, template_name: str):
        self.parameter_name = parameter_name
        self.template_name = template_name
        super().__init__(
            f"テンプレート '{template_name}' に必須パラメータ '{parameter_name}' が不足しています"
        )


class TemplateFormatError(PromptError):
    """テンプレートのフォーマットが不正な場合の例外"""

    def __init__(self, template_name: str, original_error: Exception):
        self.template_name = template_name
        self.original_error = original_error
        super().__init__(
            f"テンプレート '{template_name}' のフォーマットに問題があります: {str(original_error)}"
        )


class ParameterValidationError(PromptError):
    """パラメータの検証に失敗した場合の例外"""

    def __init__(self, parameter_name: str, reason: str):
        self.parameter_name = parameter_name
        self.reason = reason
        super().__init__(
            f"パラメータ '{parameter_name}' の検証に失敗しました: {reason}"
        )
