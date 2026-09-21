import re
from playwright.sync_api import Page, expect
import pytest

PRODUCTS = {
    "Sauce Labs Backpack" : 29.99,
    "Sauce Labs Bike Light" : 9.99,
    "Sauce Labs Bolt T-Shirt" : 15.99,
    "Sauce Labs Fleece Jacket" : 49.99,
    "Sauce Labs Onesie" : 7.99,
    "Test.allTheThings() T-Shirt (Red)" : 15.99,
}

NAMES_ASC = sorted(PRODUCTS)
NAMES_DESC = list(reversed(NAMES_ASC))

PRICES_ASC = [f"${price:.2f}" for price in sorted(PRODUCTS.values())]
PRICES_DESC = list(reversed(PRICES_ASC))

ITEM = ".inventory_item"
NAME = ".inventory_item_name"
PRICE = ".inventory_item_price"
SORT_DROPDOWN = ".product_sort_container"

def test_default_sorting_is_name_ascending(inventory_page: Page) -> None: 
    expect(inventory_page.locator(NAME)).to_have_text(NAMES_ASC)
    expect(inventory_page.locator(SORT_DROPDOWN)).to_have_value("az")


@pytest.mark.parametrize(
    ("option", "expected_names"),
    [ 
        pytest.param("az", NAMES_ASC, id="name-a-z"),
        pytest.param("za", NAMES_DESC, id="name-z-a"),
    ],
)
def test_sorting_by_name(inventory_page: Page, option: str, expected_names: list[str]) -> None:
    inventory_page.locator(SORT_DROPDOWN).select_option(option)

    expect(inventory_page.locator(NAME)).to_have_text(expected_names)


@pytest.mark.parametrize(
    ("option", "expected_prices"),
    [ 
        pytest.param("lohi", PRICES_ASC, id="price-low-to-high"),
        pytest.param("hilo", PRICES_DESC, id="price-high-to-low"),
    ],
)
def test_sorting_by_price(inventory_page: Page, option: str, expected_prices: list[str]) -> None:
    inventory_page.locator(SORT_DROPDOWN).select_option(option)

    expect(inventory_page.locator(PRICE)).to_have_text(expected_prices)


@pytest.mark.parametrize("option", ["az", "za", "lohi", "hilo"])
def test_sorting_keeps_product_count(inventory_page: Page, option: str) -> None:
    inventory_page.locator(SORT_DROPDOWN).select_option(option)

    expect(inventory_page.locator(ITEM)).to_have_count(6)




