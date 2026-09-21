import re

from playwright.sync_api import Page, expect

PASSWORD = "secret_sauce"

BACKPACK = "Sauce Labs Backpack"
ONESIE = "Sauce Labs Onesie"
RED_TSHIRT = "Test.allTheThings() T-Shirt (Red)"

INVENTORY_URL = re.compile(r"/inventory\.html$")
COMPLETE_URL = re.compile(r"/checkout-complete\.html$")
LOGIN_URL = re.compile(r"saucedemo\.com/?$")
CONFIRMATION = "Thank you for your order!"


def log_in(page: Page, username: str) -> None:
    """Log in with a given user."""
    page.get_by_test_id("username").fill(username)
    page.get_by_test_id("password").fill(PASSWORD)
    page.get_by_role("button", name="Login").click()


def fill_checkout_form(page: Page) -> None:
    """Fill the customer information and continue to the overview."""
    page.get_by_placeholder("First Name").fill("Ruben")
    page.get_by_placeholder("Last Name").fill("Tester")
    page.get_by_placeholder("Zip/Postal Code").fill("35390")
    page.get_by_role("button", name="Continue").click()

def test_complete_purchase_journey(login_page: Page) -> None:
    """Login, sort, detail page, cart, checkout, confirmation and logout."""
    log_in(login_page, "standard_user")
    expect(login_page).to_have_url(INVENTORY_URL)

    login_page.get_by_role("combobox", name="Sort products").select_option("lohi")
    expect(login_page.get_by_test_id("inventory-item-price").first).to_have_text("$7.99")

    login_page.get_by_role(
        "button", name=f"View details for {ONESIE}"
    ).last.click()
    login_page.get_by_role("button", name="Add to cart").click()
    login_page.get_by_role("button", name="Back to products").click()

    login_page.get_by_test_id("add-to-cart-sauce-labs-backpack").click()
    expect(login_page.get_by_test_id("shopping-cart-badge")).to_have_text("2")

    login_page.get_by_test_id("shopping-cart-link").click()
    expect(login_page.locator(".cart_item")).to_have_count(2)

    login_page.get_by_role("button", name="Checkout").click()
    fill_checkout_form(login_page)

    expect(login_page.locator(".summary_subtotal_label")).to_contain_text("$37.98")

    login_page.get_by_role("button", name="Finish").click()
    expect(login_page).to_have_url(COMPLETE_URL)
    expect(login_page.get_by_test_id("complete-header")).to_have_text(CONFIRMATION)
    expect(login_page.get_by_test_id("shopping-cart-badge")).to_have_count(0)

    login_page.get_by_role("button", name="Open Menu").click()
    login_page.get_by_test_id("logout-sidebar-link").click()
    expect(login_page).to_have_url(LOGIN_URL)

def test_product_with_special_characters_can_be_ordered(login_page: Page) -> None:
    """A product name containing dots, parentheses and mixed case must work."""
    log_in(login_page, "standard_user")

    login_page.get_by_test_id("add-to-cart-test.allthethings()-t-shirt-(red)").click()
    login_page.get_by_test_id("shopping-cart-link").click()

    expect(login_page.locator(".cart_item .inventory_item_name")).to_have_text([RED_TSHIRT])

    login_page.get_by_role("button", name="Checkout").click()
    fill_checkout_form(login_page)

    expect(login_page.locator(".cart_item .inventory_item_name")).to_have_text([RED_TSHIRT])

    login_page.get_by_role("button", name="Finish").click()
    expect(login_page.get_by_test_id("complete-header")).to_have_text(CONFIRMATION)

def test_slow_user_can_complete_a_purchase(login_page: Page) -> None:
    """performance_glitch_user must complete the purchase despite the latency."""
    log_in(login_page, "performance_glitch_user")
    expect(login_page).to_have_url(INVENTORY_URL)

    login_page.get_by_test_id("add-to-cart-sauce-labs-backpack").click()
    login_page.get_by_test_id("shopping-cart-link").click()
    login_page.get_by_role("button", name="Checkout").click()
    fill_checkout_form(login_page)
    login_page.get_by_role("button", name="Finish").click()

    expect(login_page.get_by_test_id("complete-header")).to_have_text(CONFIRMATION)

    