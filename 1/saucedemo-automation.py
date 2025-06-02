import pytest
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()

    # ✅ Disable Chrome password manager popups and other unwanted UI
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-save-password-bubble")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--user-data-dir=/tmp/temporary-profile")  # Fresh user profile

    # chrome_options.add_argument("--headless")  # Enable for headless mode

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


def test_search_add_to_cart_and_checkout(driver):
    wait = WebDriverWait(driver, 10)

    # 1️⃣ Open the login page
    driver.get("https://www.saucedemo.com/")
    time.sleep(2)

    # 2️⃣ Login with standard user credentials
    wait.until(EC.element_to_be_clickable((By.ID, "user-name"))).send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()
    time.sleep(3)

    # 3️⃣ Wait for inventory page to load
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "inventory_item")))
    time.sleep(2)

    # 4️⃣ Find "Sauce Labs Fleece Jacket" in product list
    products = driver.find_elements(By.CLASS_NAME, "inventory_item")
    fleece_jacket = next(
        (product for product in products
         if product.find_element(By.CLASS_NAME, "inventory_item_name").text == "Sauce Labs Fleece Jacket"),
        None
    )
    assert fleece_jacket is not None, "Product 'Sauce Labs Fleece Jacket' not found"
    time.sleep(2)

    # 5️⃣ Navigate to product detail page and add to cart
    fleece_jacket.find_element(By.CLASS_NAME, "inventory_item_name").click()
    add_to_cart_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_primary.btn_inventory"))
    )
    add_to_cart_btn.click()
    time.sleep(2)

    # 6️⃣ Go to cart and start checkout
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    time.sleep(2)
    checkout_btn = wait.until(EC.element_to_be_clickable((By.ID, "checkout")))
    checkout_btn.click()
    time.sleep(2)

    # 7️⃣ Fill in checkout information
    wait.until(EC.visibility_of_element_located((By.ID, "first-name"))).send_keys("John")
    driver.find_element(By.ID, "last-name").send_keys("Doe")
    driver.find_element(By.ID, "postal-code").send_keys("12345")
    driver.find_element(By.ID, "continue").click()
    time.sleep(2)

    # 8️⃣ Verify payment and total info
    payment_info = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "summary_info_label"))
    ).text
    total_price = driver.find_element(By.CLASS_NAME, "summary_total_label").text
    print(f"Payment Information: {payment_info}")
    print(f"Total Price: {total_price}")
    time.sleep(2)

    # 9️⃣ Finish the order
    finish_btn = wait.until(EC.element_to_be_clickable((By.ID, "finish")))
    finish_btn.click()

    # 🔟 Verify order confirmation
    complete_header = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "complete-header"))
    ).text
    assert complete_header == "Thank you for your order!"
