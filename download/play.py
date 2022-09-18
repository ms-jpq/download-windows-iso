from contextlib import nullcontext

from playwright.async_api import async_playwright

from .logging import log


async def down(*, lang: str, timeout: float) -> str:
    async with async_playwright() as ctx:
        async with await ctx.chromium.launch() as chrome:
            async with await chrome.new_page() as page:
                with nullcontext():
                    s1 = await page.goto(
                        "https://www.microsoft.com/software-download/windows11"
                    )
                    log.info("%s", s1)

                with nullcontext():
                    selector = page.locator("#product-edition")
                    log.info("%s", selector)
                    await selector.select_option(index=1)

                with nullcontext():
                    selector = page.locator("#submit-product-edition")
                    log.info("%s", selector)
                    await selector.click()

                with nullcontext():
                    selector = page.locator("#product-languages")
                    log.info("%s", selector)
                    await selector.select_option(label=lang)

                with nullcontext():
                    selector = page.locator("#submit-sku")
                    log.info("%s", selector)
                    await selector.click()

                with nullcontext():
                    selector = page.locator(
                        "a", has=page.locator(".product-download-type")
                    )
                    log.info("%s", selector)
                    uri = await selector.get_attribute("href", timeout=timeout)
                    assert uri, "Missing Download Link!"
                    return uri
