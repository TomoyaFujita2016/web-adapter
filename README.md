# web-adapter
> Selenium Wrapper

## Usage
- `poetry add git+https://github.com/TomoyaFujita2016/web-adapter#main`


## Sample

```python

import time

from web_adapter import WebAdapter
from web_adapter.materials import URL, ElementHint, Type


def main():
    web_adapter = WebAdapter(is_headless=False)
    web_adapter.get_page(URL("https://www.google.com/"))
    web_adapter.input_this(ElementHint("input.gLFyf.gsfi", Type.CSS_SELECTOR), "poop")
    web_adapter.click_this(
        ElementHint("div.FPdoLc.lJ9FBc > center > input.gNO89b", Type.CSS_SELECTOR)
    )
    time.sleep(5)


if __name__ == "__main__":
    main() 
```
