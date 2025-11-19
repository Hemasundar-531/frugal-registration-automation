# test_registration.py
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# --- CONFIG ---
# Path to your chromedriver executable (change if needed)
CHROMEDRIVER_PATH = "chromedriver.exe"   # <-- set this path
PAGE_URL = "file://" + os.path.abspath("index.html")
SCREEN_DIR = os.path.abspath("screens")
os.makedirs(SCREEN_DIR, exist_ok=True)

# Chrome options
opts = Options()
opts.add_argument("--start-maximized")

service = ChromeService(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=opts)

def take(name):
    path = os.path.join(SCREEN_DIR, name)
    driver.save_screenshot(path)
    print("Saved screenshot:", path)

try:
    # Open page
    driver.get(PAGE_URL)
    print("URL:", driver.current_url, "Title:", driver.title)
    time.sleep(1)

    # ---------- Negative Flow A ----------
    # Fill required fields but skip Last Name
    driver.find_element(By.ID, "firstName").send_keys("Hemasundar")
    # skip lastName
    driver.find_element(By.ID, "email").send_keys("hemasundar@example.com")
    driver.find_element(By.ID, "phone").send_keys("+919999999999")
    # select gender
    driver.find_element(By.CSS_SELECTOR, "input[name='gender'][value='Male']").click()
    # fill password mismatch scenario
    driver.find_element(By.ID, "password").send_keys("Test@123")
    driver.find_element(By.ID, "confirmPassword").send_keys("Test@124")
    # accept terms
    driver.find_element(By.ID, "terms").click()
    # try to submit
    submit = driver.find_element(By.ID, "submitBtn")
    # Wait for form validation to run
    time.sleep(0.8)
    # Submit should be disabled due to missing last name or mismatch
    take("error-state.png")
    print("Submit enabled:", submit.is_enabled())
    # (We expect disabled or error shown)
    # Capture error message for Last Name
    err_last = driver.find_element(By.ID, "errLastName")
    print("Last name error visible text:", err_last.text)
    time.sleep(1)

    # ---------- Positive Flow B ----------
    # Fill missing last name and fix confirm password
    driver.find_element(By.ID, "lastName").send_keys("Sanapathi")
    driver.find_element(By.ID, "confirmPassword").clear()
    driver.find_element(By.ID, "confirmPassword").send_keys("Test@123")
    # ensure submit is enabled
    time.sleep(0.8)
    take("before-submit.png")
    # Click submit (form will show success)
    submit.click()
    # wait for success message
    time.sleep(1.0)
    take("success-state.png")
    # print success text
    success_txt = driver.find_element(By.ID, "success").text
    print("Success text:", success_txt)

    # ---------- Flow C - Form Logic Validation ----------
    # Refresh to reset the form
    driver.refresh()
    time.sleep(0.6)
    # Change country and verify states update
    country = driver.find_element(By.ID, "country")
    country.click()
    for opt in country.find_elements(By.TAG_NAME, "option"):
        if opt.get_attribute("value") == "IN":
            opt.click()
            break
    time.sleep(0.6)
    # Now check state options
    state = driver.find_element(By.ID, "state")
    states = [o.text for o in state.find_elements(By.TAG_NAME,"option")]
    print("States for selected country:", states)
    # choose a state
    for o in state.find_elements(By.TAG_NAME,"option"):
        if o.text == "Gujarat":
            o.click()
            break
    time.sleep(0.6)
    # Check cities updated
    city = driver.find_element(By.ID, "city")
    cities = [o.text for o in city.find_elements(By.TAG_NAME,"option")]
    print("Cities for chosen state:", cities)

    # Test wrong confirm password again => error
    driver.find_element(By.ID, "firstName").send_keys("A")
    driver.find_element(By.ID, "lastName").send_keys("B")
    driver.find_element(By.ID, "email").send_keys("a.b@example.com")
    driver.find_element(By.ID, "phone").send_keys("+911234567890")
    driver.find_element(By.CSS_SELECTOR, "input[name='gender'][value='Male']").click()
    driver.find_element(By.ID, "password").send_keys("abc123")
    driver.find_element(By.ID, "confirmPassword").send_keys("wrong")
    driver.find_element(By.ID, "terms").click()
    time.sleep(0.6)
    take("confirm-wrong.png")
    # End of tests

finally:
    print("Test finished. Screenshots in:", SCREEN_DIR)
    driver.quit()
