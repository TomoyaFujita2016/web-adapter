from typing import List, Union

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
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
    TIMEOUT = 5
    RETRIES = 4

    def __init__(
        self, is_headless: bool = True, user_data_dir=None, timeout=None, retries=None
    ):
        if timeout is None:
            self.timeout = self.TIMEOUT
        else:
            self.timeout = timeout

        if retries is None:
            self.retries = self.RETRIES
        else:
            self.retries = retries

        self.options = Options()
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument(f"--user-agent={WebAdapter.USER_AGENT}")
        self.options.add_argument("--verbose")
        self.options.page_load_strategy = "eager"

        if is_headless:
            self.options.add_argument("--headless")
        if user_data_dir:
            self.options.add_argument(f"--user-data-dir={user_data_dir}")

        self.__load_browser()

    def __del__(self) -> None:
        """ブラウザがBGに残らないようにquitする"""
        try:
            self.driver.quit()
        except Exception:
            pass

    def __load_browser(self) -> None:
        """ドライバの作成とChromeの起動, Actionの作成"""
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=self.options
        )
        self.driver.set_page_load_timeout(self.timeout)
        self.actions = ActionChains(self.driver)

    def wait_for_element(
        self,
        element_hint: ElementHint,
        root_element: Union[WebElement, None] = None,
        latency: int = 5,
    ) -> bool:
        """エレメントが表示されるまで待つ

        Args:
            element_hint (ElementHint): 表示を待つElementHint
            root_element (WebElement): 親エレメント
            latency (int): 待機時間

        Returns:
            もし表示されれればTrue, 表示されなければFalse
        """
        if root_element is None:
            root_element = self.driver
        log.debug(f"Elementの表示を待っています。({element_hint})")
        try:
            WebDriverWait(root_element, latency).until(
                # EC.element_to_be_clickable(
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
        for i in range(self.retries):
            try:
                self.driver.get(url.value)
                break
            except TimeoutException:
                log.debug(f"Timeout, Retrying... {i}/{self.retries}")
                continue

    def find_element(
        self,
        element_hint: ElementHint,
        root_element: Union[WebElement, None] = None,
        latency: int = 5,
    ) -> Union[WebElement, None]:
        """エレメントを見つける

        Args:
        element_hint (ElementHint): 見つけるElementHint
        root_element (WebElement): 親エレメント

        Returns:
            見つかればWebElement, 見つからなければNone
        """
        if root_element is None:
            root_element = self.driver
        log.debug(f"Elementを見つけています。({element_hint})")
        if not self.wait_for_element(
            element_hint, root_element=root_element, latency=latency
        ):
            # エレメントが表示されなければreturn
            return None

        if element_hint.type == Type.CSS_SELECTOR:
            return root_element.find_element_by_css_selector(element_hint.path)

        log.error(f"対応するElement.typeが見つかりませんでした...({element_hint})")
        return None

    def find_elements(
        self,
        element_hint: ElementHint,
        root_element: Union[WebElement, None] = None,
        latency: int = 5,
    ) -> List[Union[WebElement, None]]:
        """エレメントを見つける

        Args:
        element_hint (ElementHint): 見つけるElementHint

        Returns:
            見つかればWebElement, 見つからなければNone
        """
        if root_element is None:
            root_element = self.driver
        log.debug(f"Elementを見つけています。({element_hint})")
        if not self.wait_for_element(
            element_hint, root_element=root_element, latency=latency
        ):
            # エレメントが表示されなければreturn
            return []

        if element_hint.type == Type.CSS_SELECTOR:
            return root_element.find_elements_by_css_selector(element_hint.path)

        log.error(f"対応するElement.typeが見つかりませんでした...({element_hint})")
        return []

    def click_this(
        self,
        element_hint: ElementHint,
        root_element: Union[WebElement, None] = None,
        latency=5,
    ) -> bool:
        """エレメントをクリックする
        Args:
            element_hint (ElementHint): クリックするElementHint
            root_element (WebElement): 親エレメント
        """
        log.debug(f"Elementをクリックします。({element_hint})")
        element = self.find_element(
            element_hint, root_element=root_element, latency=latency
        )
        if element is None:
            log.error(f"Elementをクリックできませんでした...({element_hint})")
            return False
        element.click()
        log.debug(f"Elementをクリックしました！({element_hint})")
        return True

    def input_this(
        self,
        element_hint: ElementHint,
        value: str,
        root_element: Union[WebElement, None] = None,
    ) -> bool:
        """エレメントに入力する
        Args:
            element_hint (ElementHint): 入力先のElementHint
            root_element (WebElement): 親エレメント
            value (str): 入力する文字列
        """
        log.debug(f"Elementに「{value}」を入力します。({element_hint})")
        element = self.find_element(element_hint, root_element=root_element)
        if element is None:
            log.error(f"Elementに「{value}」を入力できませんでした...({element_hint})")
            return False
        # 既に何か入力されているかもしれないので一度clear
        element.clear()
        element.send_keys(value)
        log.debug(f"Elementに「{value}」を入力しました！({element_hint})")
        return True

    def select_this(self, element_hint: ElementHint, value: str) -> bool:
        """Selectタグの要素を選択する
        Args:
            element_hint (ElementHint): 選択する先のElementHint
            value (str): 選択する文字列
        """
        log.debug(f"Selectから「{value}」を選択します。({element_hint})")
        element = self.find_element(element_hint)
        if element is None:
            log.debug(f"Selectから「{value}」を選択できませんでした...({element_hint})")
            return False
        select = Select(element)
        select.select_by_visible_text(value)
        log.debug(f"Selectから「{value}」を選択しました！...({element_hint})")
        return True

    def move_mouse_to_this(
        self, element_hint: Union[ElementHint, None] = None, element=None
    ) -> bool:
        """エレメントへマウスカーソルを移動

        Args:
        element_hint (ElementHint): 見つけるElementHint

        Returns:
            成功すればTrue, 失敗すればFalse
        """
        if all([element_hint, element]):
            raise Exception("element_hintとelementの両方を指定することはできません")

        log.debug("マウスカーソルを移動します")
        if element_hint:
            _element = self.find_element(element_hint)
            if _element is None:
                log.debug(f"移動失敗...({element_hint})")
                return False
            self.actions.move_to_element(_element).perform()
            return True
        if element:
            try:
                self.actions.move_to_element(element).perform()
            except ElementNotInteractableException:
                log.debug(f"移動失敗...({element})")
                return False
        return True
        log.debug("マウスカーソルを移動しました！")

    def get_html(self) -> HTML:
        """ブラウザから現在表示されているページソースを取得し、HTMLクラスに変換する

        Returns:
            html (HTML): HTML
        """
        return HTML(self.driver.page_source)

    def find_shadow_root(
        self, root_element: WebElement, retry: int = 5, latency: float = 0.1
    ) -> Union[WebElement, None]:
        for i in range(retry):
            try:
                shadow_root = self.driver.execute_script(
                    "return arguments[0].shadowRoot", root_element
                )
                return shadow_root
            except Exception as e:
                log.warn(str(e))
        return None
