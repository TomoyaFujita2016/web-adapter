from __future__ import annotations

import re
from urllib.parse import urljoin


class URL:
    def __init__(self, absolute_url: str):
        assert absolute_url is not None, "Noneが指定されています。絶対パスを指定してください。"
        assert self.__is_absolute_url(
            absolute_url
        ), "{}は絶対パスではありません。絶対パスを指定してください。".format(absolute_url)
        self.__absolute_url = absolute_url

    @staticmethod
    def __is_absolute_url(url: str) -> bool:
        return re.match(r"^(https|http)?://[\w/:%#\$&\?\(\)~\.=\+\-]+", url) is not None

    @property
    def value(self) -> str:
        return self.__absolute_url

    def fvalue(self, **kwargs) -> str:
        try:
            absolute_url = self.__absolute_url.format(**kwargs)
        except KeyError:
            raise Exception("f-stringに渡す値がが多いです。")
        return absolute_url

    def __str__(self) -> str:
        return f"url: {self.__absolute_url}"
