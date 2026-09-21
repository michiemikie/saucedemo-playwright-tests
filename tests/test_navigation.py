import re
from playwright.sync_api import Page, expect
import pytest


INVENTORY_URL = re.compile(r"/inventory\.html$")
CART_URL = re.compile(r"/cart\.html$")
LOGIN_URL = re.compile(r"saucedemo\.com/?$")

BACKPACK =  "Sauce Labs Backpack"

def open_menu(page: Page) -> None: 
    page.get_by_role("button", name ="Open Menu").click()


def close_menu(page: Page) -> None: 
    page.get_by_role("button", name ="Close Menu").click()


def test_burger_menu_opens_and_closes(inventory_page: Page) -> None: 
    logout_link = inventory_page.get_by_test_id("logout-sidebar-link")

    expect(logout_link).not_to_be_visible()

    open_menu(inventory_page)
    expect(logout_link).to_be_visible()

    close_menu(inventory_page)
    expect(logout_link).not_to_be_visible()

def test_menu_contains_all_entries(inventory_page: Page) -> None: 
    open_menu(inventory_page)

    expect(inventory_page.get_by_test_id("inventory-sidebar-link")).to_have_text("All Items")
    expect(inventory_page.get_by_test_id("dynamic-catalog-sidebar-link")).to_have_text("Dynamic Catalog")
    expect(inventory_page.get_by_test_id("about-sidebar-link")).to_have_text("About")
    expect(inventory_page.get_by_test_id("logout-sidebar-link")).to_have_text("Logout")
    expect(inventory_page.get_by_test_id("reset-sidebar-link")).to_have_text("Reset App State")

def test_all_items_returns_to_the_catalogue(inventory_page: Page) -> None: 
    inventory_page.get_by_test_id("shopping-cart-link").click()
    expect(inventory_page).to_have_url(CART_URL)

    open_menu(inventory_page)
    inventory_page.get_by_test_id("inventory-sidebar-link").click()

    expect(inventory_page).to_have_url(INVENTORY_URL)
    expect(inventory_page.get_by_test_id("inventory-item")).to_have_count(6)

def test_about_points_to_sauce_labs(inventory_page: Page) -> None: 
    open_menu(inventory_page)

    expect(inventory_page.get_by_role("link", name="About")).to_have_attribute("href", "https://saucelabs.com/")

def test_reset_app_state_clears_the_cart(inventory_page: Page) -> None: 
    inventory_page.get_by_test_id("add-to-cart-sauce-labs-backpack").click()
    expect(inventory_page.get_by_test_id("shopping-cart-badge")).to_have_text("1")

    open_menu(inventory_page)
    inventory_page.get_by_test_id("reset-sidebar-link").click()
    close_menu(inventory_page)

    expect(inventory_page.get_by_test_id("shopping-cart-badge")).to_have_count(0)

SOCIAL_LINKS = [

    pytest.param("social-x", "https://x.com/saucelabs", id="x"),
    pytest.param("social-facebook", "https://www.facebook.com/saucelabs", id="facebook"),
    pytest.param("social-linkedin", "https://www.linkedin.com/company/sauce-labs/", id="linkedin"),
]

@pytest.mark.parametrize(("test_id", "url"), SOCIAL_LINKS)
def test_footer_links_to_social_networks(inventory_page: Page, test_id: str, url: str) -> None: 
    link = inventory_page.get_by_test_id(test_id)

    expect(link).to_have_attribute("href", url)
    expect(link).to_have_attribute("target", "_blank")

def test_footer_shows_the_copyright(inventory_page: Page) -> None: 
    expect(inventory_page.get_by_test_id("footer-copy")).to_contain_text("Sauce Labs")