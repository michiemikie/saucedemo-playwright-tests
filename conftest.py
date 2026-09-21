import base64

import pytest
from playwright.sync_api import Page, Playwright, expect


expect.set_options(timeout=10_000)

STANDARD_USER = "standard_user"
PASSWORD = "secret_sauce"

BASE_URL = "https://www.saucedemo.com/"


@pytest.fixture(scope="session", autouse=True)
def configure_test_id(playwright: Playwright) -> None:
    """Sauce Demo uses data-test instead of Playwright's default data-testid."""
    playwright.selectors.set_test_id_attribute("data-test")

@pytest.fixture
def login_page(page: Page) -> Page:
    """Login page, already opened."""
    page.goto(BASE_URL)
    return page

@pytest.fixture
def inventory_page(login_page: Page) -> Page:
    """Logged in as standard_user, product catalogue loaded."""
    login_page.get_by_test_id("username").fill(STANDARD_USER)
    login_page.get_by_test_id("password").fill(PASSWORD)
    login_page.get_by_role("button", name="Login").click()
    login_page.wait_for_url("**/inventory.html")
    return login_page

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot and the URL to the HTML report on failure."""
    outcome = yield
    report = outcome.get_result()

    html_plugin = item.config.pluginmanager.getplugin("html")
    if html_plugin is None or report.when != "call" or not report.failed:
        return

    page = item.funcargs.get("page")
    extras = list(getattr(report, "extras", []))
    if page is not None:
        try:
            screenshot = base64.b64encode(page.screenshot(full_page=True)).decode()
            extras.append(html_plugin.extras.png(screenshot, name="Screenshot"))
            extras.append(html_plugin.extras.url(page.url, name="URL"))
        except Exception:  # page already closed - never block the report
            pass
    report.extras = extras


def pytest_html_report_title(report):
    report.title = "Sauce Demo - Regression Report"
