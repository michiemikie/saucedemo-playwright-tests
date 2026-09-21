import re

import pytest
from playwright.sync_api import Page, expect

BACKPACK = "Sauce Labs Backpack"
BADGE = ".shopping_cart_badge"

PRODUCTS = {
    "Sauce Labs Backpack": "$29.99",
    "Sauce Labs Bike Light": "$9.99",
    "Sauce Labs Bolt T-Shirt": "$15.99",
    "Sauce Labs Fleece Jacket": "$49.99",
    "Sauce Labs Onesie": "$7.99",
    "Test.allTheThings() T-Shirt (Red)": "$15.99",
}

DETAIL_NAME = ".inventory_details_name"
DETAIL_DESCRIPTION = ".inventory_details_desc"
DETAIL_PRICE = ".inventory_details_price"
DETAIL_IMAGE = ".inventory_details_img"

DETAIL_URL = re.compile(r"/inventory-item\.html")
INVENTORY_URL = re.compile(r"/inventory\.html$")


def open_detail_page(page: Page, product: str) -> None:
    """Open the detail page of a product and wait until it is rendered."""
    page.get_by_role("button", name=f"View details for {product}").last.click()

    expect(page).to_have_url(DETAIL_URL)
    expect(page.locator(DETAIL_NAME)).to_have_text(product)


@pytest.mark.parametrize(("name", "price"), list(PRODUCTS.items()), ids=list(PRODUCTS))
def test_detail_page_shows_matching_data(inventory_page: Page, name: str, price: str) -> None:
    open_detail_page(inventory_page, name)

    expect(inventory_page).to_have_url(re.compile(r"/inventory-item\.html\?id=\d+$"))
    expect(inventory_page.locator(DETAIL_PRICE)).to_have_text(price)
    expect(inventory_page.locator(DETAIL_DESCRIPTION)).not_to_be_empty()
    expect(inventory_page.locator(DETAIL_IMAGE)).to_be_visible()


def test_product_can_be_added_from_detail_page(inventory_page: Page) -> None:
    open_detail_page(inventory_page, BACKPACK)

    inventory_page.get_by_role("button", name="Add to cart").click()

    expect(inventory_page.locator(BADGE)).to_have_text("1")
    expect(inventory_page.get_by_role("button", name="Remove")).to_be_visible()
    expect(inventory_page.get_by_role("button", name="Add to cart")).to_have_count(0)


def test_product_can_be_removed_from_detail_page(inventory_page: Page) -> None:
    open_detail_page(inventory_page, BACKPACK)

    inventory_page.get_by_role("button", name="Add to cart").click()
    expect(inventory_page.locator(BADGE)).to_have_text("1")

    inventory_page.get_by_role("button", name="Remove").click()

    expect(inventory_page.locator(BADGE)).to_have_count(0)
    expect(inventory_page.get_by_role("button", name="Add to cart")).to_be_visible()


def test_cart_state_is_shared_with_the_catalogue(inventory_page: Page) -> None:
    open_detail_page(inventory_page, BACKPACK)
    inventory_page.get_by_role("button", name="Add to cart").click()

    inventory_page.get_by_role("button", name="Back to products").click()

    expect(inventory_page).to_have_url(INVENTORY_URL)

    card = inventory_page.locator(".inventory_item").filter(has_text=BACKPACK)
    expect(card.get_by_role("button", name="Remove")).to_be_visible()
    expect(inventory_page.locator(BADGE)).to_have_text("1")


def test_back_to_products_returns_to_the_catalogue(inventory_page: Page) -> None:
    open_detail_page(inventory_page, BACKPACK)

    inventory_page.get_by_role("button", name="Back to products").click()

    expect(inventory_page).to_have_url(INVENTORY_URL)
    expect(inventory_page.locator(".inventory_item")).to_have_count(6)