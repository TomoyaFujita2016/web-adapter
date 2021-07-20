from .type import Type


class ElementHint:
    """エレメントを見つけるためのヒントクラス

    Args:
        path (str): Typeに応じた値。 ``CSS_SELECTOR`` なら ``div.hoge > a``
        type (Type): ``CSS_SELECTOR`` など
    """

    def __init__(self, path: str, type: Type):
        self.__path = path
        self.__type = type

    @property
    def path(self) -> str:
        return self.__path

    @property
    def type(self) -> Type:
        return self.__type

    def __str__(self) -> str:
        return f"({self.__path}, {self.__type})"
