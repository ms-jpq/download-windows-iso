"""
Drive the official Microsoft Windows download page and return the direct,
signed ISO URL.

Microsoft does not expose a stable public API for this: the page builds a
signed URL in the browser (through its ``software-download-connector`` API)
after the user picks a product edition and a language. The browser also passes
Microsoft's bot protection (Sentinel), so a plain HTTP request to that API is
rejected. We therefore automate the real page with Playwright.

Flow (verified against the live pages):

1. Open the Windows 10/11 download page.
2. Choose the product edition and submit.
3. Wait for the language list (populated dynamically) and choose a language.
4. Submit and read the signed ISO link rendered on the page.
"""

import json
import re

from playwright.async_api import async_playwright

from .logging import log

# Host that serves the signed ISO files.
ISO_HOST = "software.download.prss.microsoft.com"

# The Windows 10 "Media Creation Tool" page has no ISO selector; the ISO page
# is the dedicated windows10ISO path.
PAGES = {
    "10": "https://www.microsoft.com/software-download/windows10ISO",
    "11": "https://www.microsoft.com/software-download/windows11",
}

# Lifecycle information, verified against Microsoft sources (checked 2026-10).
# Windows 10 reached end of support on 2025-10-14; consumer ESU run through
# 2027-10-12. Windows 11 has no ESU program and is serviced per version.
SUPPORT = {
    "10": [
        "Windows 10 reached end of support on October 14, 2025.",
        "Consumer Extended Security Updates (ESU) run through October 12, 2027.",
        "After that date Windows 10 no longer receives security updates.",
        "Microsoft may withdraw Windows 10 ISO downloads at any time.",
    ],
    "11": [
        "Windows 11 has no ESU program; support depends on the installed version.",
        "Home/Pro end of updates: 24H2 -> October 13, 2026; "
        "25H2 -> October 13, 2027; 26H2 -> October 10, 2028.",
        "Enterprise/Education versions receive updates for longer.",
        "Microsoft may withdraw Windows 11 ISO downloads at any time.",
    ],
}


def _log_support(windows_version: str) -> None:
    for line in SUPPORT[windows_version]:
        log.warning(line)


def _canonical_language(value: str) -> str | None:
    """Extract the canonical language name from a ``#product-languages`` value.

    The option values are JSON objects such as
    ``{"id":"27160","language":"English"}``. The ``language`` field is the
    locale-independent name, unlike the visible (localized) option label.
    """
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        return None
    if isinstance(parsed, dict):
        language = parsed.get("language")
        if isinstance(language, str) and language:
            return language
    return None


async def _first_edition_index(page) -> int:
    """Return the index of the first real (non-placeholder) edition option."""
    options = await page.eval_on_selector_all(
        "#product-edition option",
        "els => els.map(e => e.value)",
    )
    for index, value in enumerate(options):
        if value and value.strip().lower() not in ("null", "undefined", ""):
            return index
    raise RuntimeError("No selectable Windows edition was found")


async def _find_language_index(page, language: str) -> int:
    """Find the option index matching ``language`` (canonical or localized).

    Matching is intentionally tolerant because the visible labels are
    localized (the page may render in Spanish, etc.) while the canonical names
    live inside the option values. ``"English International"`` (a legacy name
    used by older versions of this script) still resolves to ``English``.
    """
    options = await page.eval_on_selector_all(
        "#product-languages option",
        "els => els.map(e => [e.value, (e.textContent || '').trim()])",
    )
    wanted = (language or "English").strip().lower()

    # 1. Exact canonical match.
    for index, (value, _label) in enumerate(options):
        canonical = _canonical_language(value)
        if canonical and canonical.lower() == wanted:
            return index

    # 2. Canonical contains / is contained by the requested name.
    for index, (value, _label) in enumerate(options):
        canonical = _canonical_language(value)
        if canonical and (wanted in canonical.lower() or canonical.lower() in wanted):
            return index

    # 3. Localized label exact match.
    for index, (_value, label) in enumerate(options):
        if label and label.lower() == wanted:
            return index

    # 4. Localized label contains the requested word (e.g. "English" in
    #    "Inglés" will not match, but "Inglés (Estados Unidos)" will match a
    #    request for "Inglés").
    for index, (_value, label) in enumerate(options):
        if label and wanted in label.lower():
            return index

    raise RuntimeError(
        f"Language {language!r} is not offered for this Windows version"
    )


async def _wait_for_iso_link(page, timeout: float) -> str:
    """Wait for the rendered ISO link and return the best (x64) candidate."""
    selector = f'a[href*="{ISO_HOST}"], a[href*=".iso"]'
    await page.wait_for_selector(selector, timeout=timeout)
    hrefs = await page.eval_on_selector_all(
        selector,
        "els => els.map(e => e.getAttribute('href')).filter(Boolean)",
    )

    # De-duplicate while preserving order.
    seen: list[str] = []
    for href in hrefs:
        if href not in seen:
            seen.append(href)

    # Prefer the 64-bit image when Microsoft offers several (Windows 10).
    for href in seen:
        if re.search(r"x64|x86_64|_64|64-bit", href, re.IGNORECASE):
            return href
    if seen:
        return seen[0]
    raise RuntimeError("The download page did not render an ISO link")


async def down(*, lang: str, timeout: float, windows_version: str = "11") -> str:
    """Return the direct download URL of a Windows ISO.

    Args:
        lang: Language name, canonical (``"English"``) or localized
            (``"Español"``). ``"English International"`` is accepted for
            backwards compatibility.
        timeout: Timeout in milliseconds for element waits.
        windows_version: ``"10"`` or ``"11"`` (default ``"11"``).
    """
    if windows_version not in PAGES:
        raise ValueError("windows_version must be '10' or '11'")

    page_url = PAGES[windows_version]
    _log_support(windows_version)

    async with async_playwright() as ctx:
        browser = await ctx.chromium.launch(headless=True)
        try:
            context = await browser.new_context(
                locale="en-US",
                extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
            )
            page = await context.new_page()

            log.info("Opening %s", page_url)
            await page.goto(page_url, wait_until="domcontentloaded", timeout=timeout)
            await page.wait_for_selector("#product-edition", timeout=timeout)

            edition_index = await _first_edition_index(page)
            await page.select_option("#product-edition", index=edition_index)
            await page.click("#submit-product-edition")
            log.info("Selected product edition")

            # The language list is populated asynchronously by the page.
            await page.wait_for_function(
                "document.querySelectorAll('#product-languages option').length > 1",
                timeout=timeout,
            )
            language_index = await _find_language_index(page, lang)
            await page.select_option("#product-languages", index=language_index)
            await page.click("#submit-sku")
            log.info("Selected language %r", lang)

            uri = await _wait_for_iso_link(page, timeout)
            log.info("Found ISO link: %s", uri)
            return uri
        finally:
            await browser.close()
