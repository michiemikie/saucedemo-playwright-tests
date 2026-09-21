import re
from playwright.sync_api import Page, expect
import pytest

BASE_URL = "https://www.saucedemo.com/"

PASSWORD = "secret_sauce"

INVENTORY_URL = re.compile(r"/inventory\.html$")
LOGIN_URL = re.compile(r"saucedemo\.com/?$")
BACK_BUTTON_ERROR = "Epic sadface: You can only access '/inventory.html' when you are logged in."

AKTIVE_BENUTZER = [
    "standard_user",
    "problem_user",
    "performance_glitch_user",
    "error_user",
    "visual_user"
]
FEHLERHAFTE_LOGINS = [
    ("standard_user", "falsches_passwort", "Epic sadface: Username and password do not match any user in this service"),
    ("nicht_registrierter_user", PASSWORD, "Epic sadface: Username and password do not match any user in this service"),
    ("", PASSWORD, "Epic sadface: Username is required"),
    ("standard_user", "", "Epic sadface: Password is required"),
]

LOCKED_OUT_USER = "locked_out_user"
LOCKED_OUT_ERROR = "Epic sadface: Sorry, this user has been locked out."

PROTECTED_PAGES = [
    "/inventory.html",
    "/cart.html",
    "/checkout-step-one.html",
    "/checkout-step-two.html",
    "/checkout-complete.html",
]

def test_standard_user_login_successful(login_page: Page) -> None:
    login_page.get_by_test_id("username").fill(STANDARD_USER)
    login_page.get_by_test_id("password").fill(PASSWORD)

    login_page.get_by_role("button", name="Login").click()

    expect(login_page).to_have_url(INVENTORY_URL)
    expect(login_page.get_by_test_id("title")).to_have_text("Products")

@pytest.mark.parametrize("username", AKTIVE_BENUTZER)
def test_active_users_can_login(login_page: Page, username: str) -> None:
    login_page.get_by_test_id("username").fill(username)
    login_page.get_by_test_id("password").fill(PASSWORD)

    login_page.get_by_role("button", name="Login").click()

    expect(login_page).to_have_url(INVENTORY_URL)
    expect(login_page.locator(".title")).to_have_text("Products")

def test_locked_out_user_is_rejected(login_page: Page) -> None:
    login_page.get_by_test_id("username").fill(LOCKED_OUT_USER)
    login_page.get_by_test_id("password").fill(PASSWORD)

    login_page.get_by_role("button", name="Login").click()

    expect(login_page.get_by_test_id("error")).to_have_text(LOCKED_OUT_ERROR)
    expect(login_page).to_have_url(LOGIN_URL)

@pytest.mark.parametrize("username, password, expected_message", FEHLERHAFTE_LOGINS)
def test_invalid_logins_are_rejected(login_page: Page, username: str, password: str, expected_message: str) -> None:
    login_page.get_by_test_id("username").fill(username)
    login_page.get_by_test_id("password").fill(password)

    login_page.get_by_role("button", name="Login").click()

    expect(login_page.get_by_test_id("error")).to_have_text(expected_message)
    expect(login_page).to_have_url(LOGIN_URL)

def test_error_message_is_dismissible(login_page: Page) -> None:
    login_page.get_by_role("button", name="Login").click()
    expect(login_page.get_by_test_id("error")).to_be_visible()

    login_page.get_by_test_id("error-button").click()

    expect(login_page.get_by_test_id("error")).not_to_be_visible()


def test_input_fields_are_marked_invalid(login_page: Page) -> None:
    login_page.get_by_role("button", name="Login").click()

    expect(login_page.get_by_test_id("username")).to_have_class(re.compile("error"))
    expect(login_page.get_by_test_id("password")).to_have_class(re.compile("error"))

def test_logout_ends_session(login_page: Page) -> None:
    login_page.get_by_test_id("username").fill("standard_user")
    login_page.get_by_test_id("password").fill(PASSWORD)
    login_page.get_by_role("button", name="Login").click()

    expect(login_page).to_have_url(INVENTORY_URL)

    login_page.locator("#react-burger-menu-btn").click()
    login_page.locator("#logout_sidebar_link").click()

    expect(login_page).to_have_url(LOGIN_URL)

    login_page.goto(BASE_URL + "inventory.html")
    expect(login_page.get_by_test_id("error")).to_be_visible()
    expect(login_page.get_by_test_id("error")).to_contain_text("Epic sadface: You can only access '/inventory.html' when you are logged in.")

@pytest.mark.parametrize("path", PROTECTED_PAGES)
def test_protected_pages_require_login(login_page: Page, path: str) -> None:
    login_page.goto(BASE_URL.rstrip("/") + path)

    expect(login_page.get_by_test_id("error")).to_be_visible()
    expect(login_page.get_by_test_id("error")).to_contain_text(f"Epic sadface: You can only access '{path}' when you are logged in.")
    expect(login_page).to_have_url(LOGIN_URL)    


def test_password_field_is_masked(login_page: Page) -> None:
    password_input = login_page.get_by_test_id("password")

    expect(password_input).to_have_attribute("type", "password")

@pytest.mark.parametrize("username", AKTIVE_BENUTZER)
def test_back_button_after_logout_does_not_restore_access(login_page: Page, username: str) -> None:
    login_page.get_by_test_id("username").fill(username)
    login_page.get_by_test_id("password").fill(PASSWORD)
    login_page.get_by_role("button", name="Login").click()

    expect(login_page).to_have_url(INVENTORY_URL)

    login_page.locator("#react-burger-menu-btn").click()
    login_page.locator("#logout_sidebar_link").click()

    expect(login_page).to_have_url(LOGIN_URL)

    login_page.go_back()

    expect(login_page.get_by_test_id("error")).to_have_text(BACK_BUTTON_ERROR)
    expect(login_page).to_have_url(LOGIN_URL)

def test_login_with_enter_key(login_page: Page) -> None:
    login_page.get_by_test_id("username").fill("standard_user")
    login_page.get_by_test_id("password").fill(PASSWORD)
    login_page.get_by_test_id("password").press("Enter")

    expect(login_page).to_have_url(INVENTORY_URL)
    expect(login_page.locator(".title")).to_have_text("Products")


