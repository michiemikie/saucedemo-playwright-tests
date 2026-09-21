import re
from playwright.sync_api import Page, expect
import pytest

STANDARD_USER = "standard_user"
PASSWORD = "secret_sauce"

BACKPACK =  "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"
BOLT_TSHIRT = "Sauce Labs Bolt T-Shirt"
FLEECE_JACKET = "Sauce Labs Fleece Jacket"
ONESIE = "Sauce Labs Onesie"
RED_TSHIRT = "Test.allTheThings() T-Shirt (Red)"
 
PRODUCTS = {
    BACKPACK : "$29.99",
    BIKE_LIGHT : "$9.99",
    BOLT_TSHIRT : "$15.99",
    FLEECE_JACKET : "$49.99",
    ONESIE : "$7.99",
    RED_TSHIRT : "$15.99",
}

PRICES_IN_DEFAULT_ORDER = [PRODUCTS[name] for name in sorted(PRODUCTS)]

ITEM = ".inventory_item"
PRICE = ".inventory_item_price"
DESCRIPTION = ".inventory_item_desc"
BADGE = ".shopping_cart_badge"

def card_of(page: Page, product: str):
    return page.locator(ITEM).filter(has_text=product)

def test_catalog_shows_six_products(inventory_page: Page) -> None: 
   expect(inventory_page.locator(ITEM)).to_have_count(6)

@pytest.mark.parametrize(("name", "price"), list(PRODUCTS.items()), ids=list(PRODUCTS))
def test_each_product_shows_name_description_price_and_image(inventory_page: Page, name: str, price: str ) -> None:
    card = card_of(inventory_page, name)

    expect(card).to_have_count(1)
    expect(card.locator(PRICE)).to_have_text(price)
    expect(card.locator(DESCRIPTION)).not_to_be_empty()
    expect(card.locator("img")).to_be_visible()


def test_prices_match_references_data(inventory_page: Page) -> None: 
    expect(inventory_page.locator(PRICE)).to_have_text(PRICES_IN_DEFAULT_ORDER)

def test_badge_is_absent_when_cart_is_empty(inventory_page: Page) -> None:
    expect(inventory_page.locator(BADGE)).to_have_count(0)

def test_cart_counter_increase_when_product_is_added(inventory_page: Page)-> None:
    badge = inventory_page.locator(BADGE)

    for expected, product in enumerate((BACKPACK, BIKE_LIGHT, ONESIE), start=1):
        card_of(inventory_page, product).get_by_role("button", name="Add to cart").click()
        expect(badge).to_have_text(str(expected))


def test_all_products_can_be_added(inventory_page: Page)-> None:
    for product in PRODUCTS:
        card_of(inventory_page, product).get_by_role("button", name="Add to cart").click()

    expect(inventory_page.locator(BADGE)).to_have_text("6")

def test_button_toggles_between_add_and_remove(inventory_page: Page) -> None:
    card = card_of(inventory_page, BACKPACK)
    add_button = card.get_by_role("button", name="Add to cart")
    remove_button = card.get_by_role("button", name="Remove")


    expect(add_button).to_be_visible()
    expect(remove_button).to_have_count(0)

    add_button.click()

    expect(remove_button).to_be_visible()
    expect(add_button).to_have_count(0)

    remove_button.click()

    expect(add_button).to_be_visible()
    expect(remove_button).to_have_count(0)


def test_badge_disappears_when_last_product_is_removed(inventory_page: Page) -> None:
    card = card_of(inventory_page, BACKPACK)

    card.get_by_role("button", name="Add to cart").click()
    expect(inventory_page.locator(BADGE)).to_have_text("1")

    card.get_by_role("button", name="Remove").click()
    expect(inventory_page.locator(BADGE)).to_have_count(0)


def test_cart_content_persists_after_reload(inventory_page: Page) -> None:
    card = card_of(inventory_page, BACKPACK)
    card.get_by_role("button", name="Add to cart").click()
    expect(inventory_page.locator(BADGE)).to_have_text("1")

    inventory_page.reload()

    expect(inventory_page.locator(BADGE)).to_have_text("1")
    expect(card.get_by_role("button", name="Remove")).to_be_visible()