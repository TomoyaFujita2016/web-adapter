from typing import Union

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .logger import log
from .materials.element_hint import ElementHint
from .materials.html import HTML
from .materials.type import Type
from .materials.url import URL


class WebAdapter:
    """ブラウザ操作クラス


    Attributes:
        is_headless (bool): Chromeブラウザをヘッドレスモードで起動するかどうか

    """

    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    )

    def __init__(self, is_headless: bool = True, user_profile=None):
        self.options = Options()
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1000,1600")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument(f"--user-agent={WebAdapter.USER_AGENT}")
        self.options.add_argument("--verbose")
        
        if is_headless:
            self.options.add_argument("--headless")
        if user_profile:
            self.options.add_argument('--user-data-dir=UserProfile')
        self.__load_browser()

    def __del__(self) -> None:
        """ブラウザがBGに残らないようにquitする"""
        try:
            self.driver.quit()
        except Exception:
            pass

    def __load_browser(self) -> None:
        """ドライバの作成とChromeの起動"""
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=self.options
        )

    def __wait_for_element(self, element_hint: ElementHint, latency: int = 5) -> bool:
        """エレメントが表示されるまで待つ

        Args:
            element_hint (ElementHint): 表示を待つElementHint
            latency (int): 待機時間

        Returns:
            もし表示されれればTrue, 表示されなければFalse
        """
        log.debug(f"Elementの表示を待っています。({element_hint})")
        try:
            WebDriverWait(self.driver, latency).until(
                EC.presence_of_element_located(
                    (element_hint.type.value, element_hint.path)
                )
            )
        except TimeoutException:
            log.error(f"Elementが表示されませんでした...({element_hint}):TimeoutException")
            return False
        return True

    def get_page(self, url: URL) -> None:
        """URLをブラウザで開く

        Args:
            url (URL): URL
        """
        log.debug(f"Pageを読み込みます。{url}")
        self.driver.get(url.value)

    def find_element(self, element_hint: ElementHint) -> Union[WebElement, None]:
        """エレメントを見つける

        Args:
        element_hint (ElementHint): 見つけるElementHint

        Returns:
            見つかればWebElement, 見つからなければNone
        """
        log.debug(f"Elementを見つけています。({element_hint})")
        if not self.__wait_for_element(element_hint):
            # エレメントが表示されなければreturn
            return None

        if element_hint.type == Type.CSS_SELECTOR:
            return self.driver.find_element_by_css_selector(element_hint.path)

        log.error(f"対応するElement.typeが見つかりませんでした...({element_hint})")
        return None

    def click_this(self, element_hint: ElementHint) -> None:
        """エレメントをクリックする

        Args:
            element_hint (ElementHint): クリックするElementHint
        """
        log.debug(f"Elementをクリックします。({element_hint})")
        element = self.find_element(element_hint)
        if element is None:
            log.error(f"Elementをクリックできませんでした...({element_hint})")
            return
        element.click()
        log.debug(f"Elementをクリックしました！({element_hint})")

    def input_this(self, element_hint: ElementHint, value: str) -> None:
        """エレメントに入力する
        Args:
            element_hint (ElementHint): 入力先のElementHint
            value (str): 入力する文字列
        """
        log.debug(f"Elementに「{value}」を入力します。({element_hint})")
        element = self.find_element(element_hint)
        if element is None:
            log.error(f"Elementに「{value}」を入力できませんでした...({element_hint})")
            return
        # 既に何か入力されているかもしれないので一度clear
        element.clear()
        element.send_keys(value)
        log.debug(f"Elementに「{value}」を入力しました！({element_hint})")

    def select_this(self, element_hint: ElementHint, value: str) -> None:
        """Selectタグの要素を選択する
        Args:
            element_hint (ElementHint): 選択する先のElementHint
            value (str): 選択する文字列
        """
        log.debug(f"Selectから「{value}」を選択します。({element_hint})")
        element = self.find_element(element_hint)
        if element is None:
            log.debug(f"Selectから「{value}」を選択できませんでした...({element_hint})")
            return
        select = Select(element)
        select.select_by_visible_text(value)
        log.debug(f"Selectから「{value}」を選択しました！...({element_hint})")

    def get_html(self) -> HTML:
        """ブラウザから現在表示されているページソースを取得し、HTMLクラスに変換する

        Returns:
            html (HTML): HTML
        """
        return HTML(self.driver.page_source)
