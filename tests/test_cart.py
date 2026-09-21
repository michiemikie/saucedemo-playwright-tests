import re
from playwright.sync_api import Page, expect
import pytest

BACKPACK =  "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"

BACKPACK_PRICE =  "$29.99"
BIKE_LIGHT_PRICE = "$9.99"

BADGE = ".shopping_cart_badge"
CART_ITEM = ".cart_item"
CART_ITEM_NAME = ".cart_item .inventory_item_name"
CART_QUANTITY = ".cart_quantity"

def add_to_cart(page: Page, *products: str) -> None:
    for product in products:
        card = page.locator(".inventory_item").filter(has_text=product)
        card.get_by_role("button", name="Add to cart").click()

def open_cart(page: Page) -> None:
    page.locator(".shopping_cart_link").click()


def test_cart_shows_added_products_with_quantity_and_price(inventory_page: Page) -> None:
    add_to_cart(inventory_page, BACKPACK, BIKE_LIGHT)
    open_cart(inventory_page)

    expect(inventory_page.locator(CART_ITEM)).to_have_count(2)
    expect(inventory_page.locator(CART_ITEM_NAME)).to_have_text([BACKPACK, BIKE_LIGHT])

    backpack_row = inventory_page.locator(CART_ITEM).filter(has_text=BACKPACK)
    expect(backpack_row.locator(CART_QUANTITY)).to_have_text("1")
    expect(backpack_row.locator(".inventory_item_price")).to_have_text(BACKPACK_PRICE)

def test_removing_a_product_updates_cart_and_badge(inventory_page: Page) -> None:
    add_to_cart(inventory_page, BACKPACK, BIKE_LIGHT)
    open_cart(inventory_page)
    expect(inventory_page.locator(BADGE)).to_have_text("2")

    row = inventory_page.locator(CART_ITEM).filter(has_text=BACKPACK)
    row.get_by_role("button", name="Remove").click()

    expect(inventory_page.locator(CART_ITEM)).to_have_count(1)
    expect(inventory_page.locator(CART_ITEM_NAME)).to_have_text(BIKE_LIGHT)
    expect(inventory_page.locator(BADGE)).to_have_text("1")


def test_continue_shopping_keeps_the_cart(inventory_page: Page) -> None:
    add_to_cart(inventory_page, BACKPACK)
    open_cart(inventory_page)

    inventory_page.get_by_role("button", name="Continue Shopping").click()

    expect(inventory_page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(inventory_page.locator(BADGE)).to_have_text("1")

    card = inventory_page.locator(".inventory_item").filter(has_text=BACKPACK)
    expect(card.get_by_role("button", name="Remove")).to_be_visible()


def test_checkout_opens_the_first_step(inventory_page: Page) -> None:
    add_to_cart(inventory_page, BACKPACK)
    open_cart(inventory_page)

    inventory_page.get_by_role("button", name="Checkout").click()

    expect(inventory_page).to_have_url(re.compile(r"/checkout-step-one\.html$"))

    expect(inventory_page.get_by_placeholder("First Name")).to_be_visible()


