from __future__ import annotations


class HTML:
    def __init__(self, content: str):
        self.__content = content

    @property
    def content(self) -> str:
        return self.__content
