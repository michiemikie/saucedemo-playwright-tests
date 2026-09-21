import re
from playwright.sync_api import Page, expect
import pytest

BACKPACK =  "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"

BACKPACK_PRICE =  29.99
BIKE_LIGHT_PRICE =  9.99
TAX_RATE = 0.08

SUBTOTAL= ".summary_subtotal_label"
TAX = ".summary_tax_label"
TOTAL = ".summary_total_label"


FIRST_NAME_REQUIRED = "Error: First Name is required"
LAST_NAME_REQUIRED = "Error: Last Name is required"
POSTAL_CODE_REQUIRED =  "Error: Postal Code is required"

STEP_ONE_URL = (re.compile(r"/checkout-step-one\.html$"))
STEP_TWO_URL = (re.compile(r"/checkout-step-two\.html$"))

CART_URL = re.compile(r"/cart\.html$")
INVENTORY_URL = re.compile(r"/inventory\.html$")

SUMMARY_VALUE = ".summary_value_label"

COMPLETE_URL = re.compile(r"/checkout-complete\.html$")
CONFIRMATION = "Thank you for your order!"

COMPLETE_HEADER = ".complete-header"
COMPLETE_TEXT = ".complete-text"

@pytest.fixture
def checkout_step_one(inventory_page: Page) -> Page:
    for product in (BACKPACK, BIKE_LIGHT):
        card = inventory_page.locator(".inventory_item").filter(has_text=product)
        card.get_by_role("button", name="Add to cart").click()

    inventory_page.locator(".shopping_cart_link").click()
    inventory_page.get_by_role("button", name="Checkout").click()
    return inventory_page

@pytest.fixture
def checkout_step_two(checkout_step_one: Page) -> Page:
    checkout_step_one.get_by_placeholder("First Name").fill("Muster")
    checkout_step_one.get_by_placeholder("Last Name").fill("Musterfrau")
    checkout_step_one.get_by_placeholder("Zip/Postal Code").fill("35394")
    checkout_step_one.get_by_role("button", name="Continue").click()
    return checkout_step_one


@pytest.mark.parametrize(
        ("first_name", "last_name", "postal_code", "expected_error"),
        [
            pytest.param("", "Musterfrau", "35394", FIRST_NAME_REQUIRED, id="first-name-missing"),
            pytest.param("Muster", "", "35394", LAST_NAME_REQUIRED, id="last-name-missing"),
            pytest.param("Muster", "Musterfrau", "", POSTAL_CODE_REQUIRED, id="postal-code-missing"),
            pytest.param("", "", "", FIRST_NAME_REQUIRED, id="all-fields-empty"),
        ],
)
def test_mandatory_fields_are_validated(
    checkout_step_one: Page,
    first_name : str,
    last_name : str,
    postal_code: str, 
    expected_error: str, 
) -> None:
    checkout_step_one.get_by_placeholder("First Name").fill(first_name)
    checkout_step_one.get_by_placeholder("Last Name").fill(last_name)
    checkout_step_one.get_by_placeholder("Zip/Postal Code").fill(postal_code)
    checkout_step_one.get_by_role("button", name="Continue").click()

    expect(checkout_step_one.get_by_test_id("error")).to_have_text(expected_error)
    expect(checkout_step_one).to_have_url(STEP_ONE_URL)

def test_cancel_in_step_one_returns_to_the_cart(checkout_step_one: Page) -> None:
    checkout_step_one.get_by_role("button", name="cancel").click()

    expect(checkout_step_one).to_have_url(CART_URL)
    expect(checkout_step_one.locator(".cart_item")).to_have_count(2)
    expect(checkout_step_one.locator(".shopping_cart_badge")).to_have_text("2")


def test_cancel_in_step_two_returns_to_the_catalogue(checkout_step_one: Page) -> None:
    checkout_step_one.get_by_placeholder("First Name").fill("Muster")
    checkout_step_one.get_by_placeholder("Last Name").fill("Musterfrau")
    checkout_step_one.get_by_placeholder("Zip/Postal Code").fill("35394")
    checkout_step_one.get_by_role("button", name="Continue").click()
    expect(checkout_step_one).to_have_url(STEP_TWO_URL)

    checkout_step_one.get_by_role("button", name="Cancel").click()

    expect(checkout_step_one).to_have_url(INVENTORY_URL)
    expect(checkout_step_one.locator(".inventory_item")).to_have_count(6)
    expect(checkout_step_one.locator(".shopping_cart_badge")).to_have_text("2")

def test_overview_lists_the_selected_products(checkout_step_two: Page) -> None:
    expect(checkout_step_two.locator(".cart_item")).to_have_count(2)
    expect(checkout_step_two.locator(".cart_item .inventory_item_name")).to_have_text([BACKPACK, BIKE_LIGHT])

    backpack_row = checkout_step_two.locator(".cart_item").filter(has_text=BACKPACK)
    expect(backpack_row.locator(".inventory_item_price")).to_have_text(f"${BACKPACK_PRICE:.2f}")
    expect(backpack_row.locator(".cart_quantity")).to_have_text("1")

def test_overview_shows_payment_and_shipping_information(checkout_step_two: Page) -> None:
    values = checkout_step_two.locator(SUMMARY_VALUE)

    expect(values).to_have_count(2)
    expect(values.first).not_to_be_empty()
    expect(values.last).not_to_be_empty()

def test_subtotal_equals_sum_of_the_item_prices(checkout_step_two: Page) -> None:
    expected = round(BACKPACK_PRICE + BIKE_LIGHT_PRICE, 2)

    expect(checkout_step_two.locator(SUBTOTAL)).to_contain_text(f"${expected:.2f}")

def test_tax_is_eight_percent_of_the_subtotal(checkout_step_two: Page) -> None:
    subtotal = round(BACKPACK_PRICE + BIKE_LIGHT_PRICE, 2)
    expected_tax = round(subtotal * TAX_RATE, 2)

    expect(checkout_step_two.locator(TAX)).to_contain_text(f"${expected_tax:.2f}")

def test_total_equals_subtotal_plus_tax(checkout_step_two: Page) -> None:
    subtotal = round(BACKPACK_PRICE + BIKE_LIGHT_PRICE, 2)
    expected_total = round(subtotal + round(subtotal * TAX_RATE, 2), 2)

    expect(checkout_step_two.locator(TOTAL)).to_contain_text(f"${expected_total:.2f}")

def test_finishing_order_shows_the_confirmation(checkout_step_two: Page) -> None:
    checkout_step_two.get_by_role("button", name="Finish").click()

    expect(checkout_step_two).to_have_url(COMPLETE_URL)
    expect(checkout_step_two.locator(COMPLETE_HEADER)).to_have_text(CONFIRMATION)
    expect(checkout_step_two.locator(COMPLETE_TEXT)).not_to_be_empty()


def test_finishing_the_order_empties_the_cart(checkout_step_two: Page) -> None:
    checkout_step_two.get_by_role("button", name="Finish").click()
    expect(checkout_step_two).to_have_url(COMPLETE_URL)

    expect(checkout_step_two.locator(".shopping_cart_badge")).to_have_count(0)

    checkout_step_two.locator(".shopping_cart_link").click()
    expect(checkout_step_two.locator(".cart_item")).to_have_count(0)

def test_back_home_returns_to_the_catalogue(checkout_step_two: Page) -> None:
    checkout_step_two.get_by_role("button", name="Finish").click()

    checkout_step_two.get_by_role("button", name="Back Home").click()

    expect(checkout_step_two).to_have_url(INVENTORY_URL)
    expect(checkout_step_two.locator(".inventory_item")).to_have_count(6)

def test_generate_pdf_order_downloads_a_file(checkout_step_two: Page) -> None:
    checkout_step_two.get_by_role("button", name="Finish").click()
    expect(checkout_step_two.get_by_test_id("complete-header")).to_be_visible()

    with checkout_step_two.expect_download() as download_info:
        checkout_step_two.get_by_role("button", name="Generate PDF order").click()

    assert download_info.value.suggested_filename.endswith(".pdf")

def test_generated_pdf_is_a_valid_file(checkout_step_two: Page, tmp_path) -> None:
    checkout_step_two.get_by_role("button", name="Finish").click()

    with checkout_step_two.expect_download() as download_info:
        checkout_step_two.get_by_role("button", name="Generate PDF order").click()

    target = tmp_path / "order.pdf"
    download_info.value.save_as(target)

    assert target.stat().st_size > 0
    assert target.read_bytes().startswith(b"%PDF")

