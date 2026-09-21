import re
from playwright.sync_api import Page, expect
import pytest

PASSWORD = "secret_sauce"
BACKPACK = "Sauce Labs Backpack"

NAMES_DESC = [
    "Test.allTheThings() T-Shirt (Red)",
    "Sauce Labs Onesie",
    "Sauce Labs Fleece Jacket",
    "Sauce Labs Bolt T-Shirt",
    "Sauce Labs Bike Light",
    "Sauce Labs Backpack",
]

CONFIRMATION = "Thank you for your order!"

pytestmark = pytest.mark.known_issue


@pytest.fixture
def login_as(login_page: Page):
    """Factory for logging in as an arbitrary user."""
    def _login(username: str) -> Page:
        login_page.get_by_test_id("username").fill(username)
        login_page.get_by_test_id("password").fill(PASSWORD)
        login_page.get_by_role("button", name="Login").click()
        return login_page

    return _login

@pytest.mark.xfail(reason="problem_user gets the same image for every product.", strict=False)
def test_problem_user_sees_individual_product_images(login_as) -> None:
    """Every product must show its own image."""
    page = login_as("problem_user")
    images = page.locator(".inventory_item_img img")
    expect(images).to_have_count(6)

    sources = [images.nth(i).get_attribute("src") for i in range(6)]

    assert len(set(sources)) == 6, "each product needs its own image"

@pytest.mark.xfail(reason="Sorting is broken for problem_user.", strict=False)
def test_problem_user_can_sort_products(login_as) -> None:
    """Selecting Z to A must reorder the catalogue."""
    page = login_as("problem_user")

    page.get_by_role("combobox", name="Sort products").select_option("za")

    expect(page.get_by_test_id("inventory-item-name")).to_have_text(NAMES_DESC)

@pytest.mark.xfail(reason="problem_user cannot fill the Last Name field.", strict=False)
def test_problem_user_can_fill_the_checkout_form(login_as) -> None:
    """All three customer fields must accept input."""
    page = login_as("problem_user")
    page.get_by_test_id("add-to-cart-sauce-labs-backpack").click()
    page.get_by_test_id("shopping-cart-link").click()
    page.get_by_role("button", name="Checkout").click()

    page.get_by_placeholder("Last Name").fill("Lovelace")

    expect(page.get_by_placeholder("Last Name")).to_have_value("Lovelace")

@pytest.mark.xfail(
    reason="Sauce Demo allows checkout with an empty cart.", strict=False
)
def test_checkout_with_an_empty_cart_is_blocked(inventory_page: Page) -> None:
    """Starting a checkout without any product must not be possible."""
    inventory_page.get_by_test_id("shopping-cart-link").click()
    expect(inventory_page.locator(".cart_item")).to_have_count(0)

    inventory_page.get_by_role("button", name="Checkout").click()

    expect(inventory_page).to_have_url(re.compile(r"/cart\.html$"))

@pytest.mark.xfail(
    reason="Finish throws 'cesetRart is not a function' (misspelt resetCart); "
    "no navigation to the confirmation page.",
    strict=False,
)
def test_error_user_can_complete_the_checkout(login_as) -> None:
    """Finishing the order must reach the confirmation page."""
    page = login_as("error_user")
    page.get_by_test_id("add-to-cart-sauce-labs-backpack").click()
    page.get_by_test_id("shopping-cart-link").click()
    page.get_by_role("button", name="Checkout").click()

    page.get_by_placeholder("First Name").fill("Ada")
    page.get_by_placeholder("Last Name").fill("Lovelace")
    page.get_by_placeholder("Zip/Postal Code").fill("35390")
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("button", name="Finish").click()

    expect(page.get_by_test_id("complete-header")).to_have_text(CONFIRMATION)


@pytest.mark.xfail(
    reason="Sorting is broken for error_user: 'Sorting is broken! This error has been "
    "reported to Backtrace.'",
    strict=False,
)
def test_error_user_can_sort_products(login_as) -> None:
    """Selecting Z to A must reorder the catalogue."""
    page = login_as("error_user")

    page.get_by_role("combobox", name="Sort products").select_option("za")

    expect(page.get_by_test_id("inventory-item-name")).to_have_text(NAMES_DESC)


def test_finish_triggers_a_javascript_error_for_error_user(login_as) -> None:
    """Documents the root cause: a call to a non-existent function."""
    page = login_as("error_user")
    errors: list[str] = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))

    page.get_by_test_id("add-to-cart-sauce-labs-backpack").click()
    page.get_by_test_id("shopping-cart-link").click()
    page.get_by_role("button", name="Checkout").click()
    page.get_by_placeholder("First Name").fill("Ada")
    page.get_by_placeholder("Last Name").fill("Lovelace")
    page.get_by_placeholder("Zip/Postal Code").fill("35390")
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("button", name="Finish").click()

    expect(page.get_by_test_id("complete-header")).to_have_count(0)
    assert any("is not a function" in error for error in errors), errors