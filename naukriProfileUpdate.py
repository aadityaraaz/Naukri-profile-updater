"""
Naukri Resume Headline Toggler with persistent profile.

- Uses Chrome profile to maintain login.
- If not logged in, fills email/password automatically if provided.
- Toggles trailing '.' in resume headline.
"""

import os
import sys
import time
import argparse

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NAUKRI_PROFILE_URL = "https://www.naukri.com/mnjuser/profile"
NAUKRI_PROFILE_DIR = os.path.join(os.path.dirname(__file__), "naukri_profile1")


def log(msg: str) -> None:
    print(msg, flush=True)


def get_driver(binary_path: str | None = None) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-extensions")
    options.add_argument(f"user-data-dir={NAUKRI_PROFILE_DIR}")

    if binary_path:
        options.binary_location = binary_path
        log(f"Using Chrome binary at {binary_path}")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver


def wait(driver: webdriver.Chrome, timeout: int = 25) -> WebDriverWait:
    return WebDriverWait(driver, timeout)


def close_overlays(driver: webdriver.Chrome) -> None:
    selectors = [
        "//div[contains(@class,'lightbox')]//div[contains(@class,'crossLayer')]",
        "//div[contains(@class,'close') and contains(@class,'ltCont')]",
        "//button[contains(.,'Close') or contains(.,'Got it') or contains(.,'No, thanks') or contains(.,'Cancel')]",
        "//span[contains(.,'CrossLayer')]",
    ]
    for sel in selectors:
        try:
            elems = driver.find_elements(By.XPATH, sel)
            for el in elems:
                if el.is_displayed():
                    try:
                        el.click()
                        time.sleep(0.3)
                    except Exception:
                        driver.execute_script("arguments[0].click();", el)
        except Exception:
            pass


def is_logged_in(driver: webdriver.Chrome) -> bool:
    driver.get(NAUKRI_PROFILE_URL)
    time.sleep(3)
    close_overlays(driver)
    return "nlogin" not in driver.current_url


def attempt_login(driver: webdriver.Chrome, email: str, password: str) -> None:
    driver.get("https://www.naukri.com/nlogin/login")
    wait(driver, 10)

    # Try multiple possible email/password XPaths
    email_xpaths = [
        "//input[contains(@placeholder,'Email') or contains(@placeholder,'email')]",
        "//input[contains(@name,'email')]",
    ]
    password_xpaths = [
        "//input[@type='password']",
        "//input[contains(@name,'password')]",
    ]
    submit_xpaths = [
        "//button[@type='submit']",
        "//button[contains(.,'Login') or contains(.,'Sign in')]",
    ]

    def find_first(xpaths):
        for xp in xpaths:
            try:
                el = wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xp)))
                if el.is_displayed():
                    return el
            except TimeoutException:
                continue
        return None

    email_el = find_first(email_xpaths)
    pwd_el = find_first(password_xpaths)
    submit_el = find_first(submit_xpaths)

    if not email_el or not pwd_el or not submit_el:
        raise RuntimeError("Could not locate login fields. Login may require manual action.")

    email_el.clear()
    email_el.send_keys(email)
    pwd_el.clear()
    pwd_el.send_keys(password)

    try:
        submit_el.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", submit_el)

    # wait for profile page
    try:
        wait(driver, 20).until(EC.url_contains("mnjuser"))
        log("Login successful.")
    except TimeoutException:
        raise RuntimeError("Login failed or OTP required. Manual intervention needed.")


# ---- Original headline logic ----

def open_resume_headline_editor(driver: webdriver.Chrome) -> None:
    driver.get(NAUKRI_PROFILE_URL)
    wait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(2)
    close_overlays(driver)

    edit_xpaths = [
        "(//*[self::h2 or self::div or self::span][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'resume headline')])[1]/ancestor::*[self::section or self::div][1]//*[self::a or self::button or self::span][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit')][1]",
        "//div[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'resume') and contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'headline')]//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit')][1]",
        "(//button[contains(.,'Edit')] | //a[contains(.,'Edit')] | //span[contains(.,'Edit')])[1]",
    ]

    edit_btn = None
    for xp in edit_xpaths:
        try:
            candidate = wait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, xp)))
            if candidate and candidate.is_displayed():
                edit_btn = candidate
                break
        except TimeoutException:
            continue

    if not edit_btn:
        raise RuntimeError("Could not locate Resume headline edit button.")

    try:
        edit_btn.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", edit_btn)

    wait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'resumeHeadlineEdit') or contains(@class,'profileEditDrawer') or contains(@class,'lightbox')]")
        )
    )
    time.sleep(0.5)


def get_headline_field(driver: webdriver.Chrome):
    field_xpaths = [
        "(//div[contains(@class,'resumeHeadlineEdit') or contains(@class,'profileEditDrawer') or contains(@class,'lightbox')]//textarea)[1]",
        "(//textarea[contains(@placeholder,'headline') or contains(@id,'headline') or contains(@name,'headline')])[1]",
        "(//div[( @contenteditable='true' or contains(@role,'textbox')) and ancestor::div[contains(@class,'resumeHeadlineEdit') or contains(@class,'profileEditDrawer') or contains(@class,'lightbox')]])[1]",
    ]
    for xp in field_xpaths:
        try:
            el = wait(driver, 15).until(EC.presence_of_element_located((By.XPATH, xp)))
            if el.is_displayed():
                return el
        except TimeoutException:
            continue
    raise RuntimeError("Could not find headline input field.")


def read_field_value(driver: webdriver.Chrome, el) -> str:
    tag = el.tag_name.lower()
    if tag in ("textarea", "input"):
        return (el.get_attribute("value") or "").strip("\n")
    return (el.text or "").strip("\n")


def set_field_value(driver: webdriver.Chrome, el, value: str) -> None:
    tag = el.tag_name.lower()
    if tag in ("textarea", "input"):
        el.click()
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.DELETE)
        el.send_keys(value)
    else:
        driver.execute_script("arguments[0].innerText = arguments[1];", el, value)


def find_and_click_save(driver: webdriver.Chrome) -> None:
    save_xpaths = [
        "(//div[contains(@class,'resumeHeadlineEdit') or contains(@class,'profileEditDrawer') or contains(@class,'lightbox')]//button[normalize-space()='Save'])[1]",
        "(//button[contains(.,'Save')])[1]",
        "(//a[contains(.,'Save')])[1]",
    ]
    for xp in save_xpaths:
        try:
            btn = wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xp)))
            try:
                btn.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.8)
            return
        except TimeoutException:
            continue
    raise RuntimeError("Save button not found.")


def toggle_trailing_period(text: str) -> str:
    text = (text or "")
    stripped = text.rstrip()
    if stripped.endswith('.'):
        return stripped[:-1]
    return stripped + '.'


def run(email: str | None, password: str | None, binary: str | None) -> int:
    driver = get_driver(binary)
    try:
        if not is_logged_in(driver):
            if not email or not password:
                raise RuntimeError("Not logged in and no email/password provided.")
            log("Not logged in. Attempting login...")
            attempt_login(driver, email, password)
            time.sleep(2)

        log("Opening Resume headline editor...")
        open_resume_headline_editor(driver)

        field = get_headline_field(driver)
        current = read_field_value(driver, field)
        updated = toggle_trailing_period(current)

        if current == updated:
            log("No change needed.")
        else:
            log(f"Updating headline from: '{current}' -> '{updated}'")
            set_field_value(driver, field, updated)
            find_and_click_save(driver)
            time.sleep(1)
            log("Saved.")

        return 0
    except Exception as e:
        log(f"Error: {e}")
        return 1
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naukri Resume Headline Toggler")
    parser.add_argument("--email", dest="email", default=None, help="Naukri email")
    parser.add_argument("--password", dest="password", default=None, help="Naukri password")
    parser.add_argument("--binary", dest="binary", default=None, help="Optional Chrome binary path")
    args = parser.parse_args()

    sys.exit(run(args.email, args.password, args.binary))
