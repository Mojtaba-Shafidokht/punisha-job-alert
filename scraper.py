from math import ceil
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as ec
from utils import clean_count, extract_id, build_page_url

PONISHA_HOME_URL = "https://ponisha.ir/"
PONISHA_LOGIN_URL = "https://ponisha.ir/users/login"
PONISHA_PROJECTS_URL = "https://ponisha.ir/search/projects"

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / "chrome_profile"
PROFILE_DIR.mkdir(exist_ok=True)


def _clear_stale_lock():
    lock_file = PROFILE_DIR / "SingletonLock"
    if lock_file.exists():
        try:
            lock_file.unlink()
            print("Removed stale profile lock.")

        except Exception as e:
            print(f"Could not remove stale lock: {e}")


def _setup_driver(headless=True):
    _clear_stale_lock()
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument(f"user-data-dir={PROFILE_DIR}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")

    try:
        driver = webdriver.Chrome(
            service=Service("./chromedriver.exe"),
            options=options
        )

    except NoSuchDriverException:
        driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 5)

    return driver, wait


def _teardown(step_result):
    if not step_result:
        return False

    else:
        return True


def _visible_texts(element, locator):
    found = element.find_elements(By.XPATH, locator)
    return [el.text for el in found if el.is_displayed()]


def _first_visible_text(element, locator):
    texts = _visible_texts(element, locator)
    return texts[0] if texts else None


def _field_text(element, locator, error_message="Could not find this element."):
    el = _safe_find(element, locator, error_message)
    return el.text if el else None


def _safe_find(element, locator, error_message="Could not find this element."):
    try:
        return element.find_element(By.XPATH, locator)

    except NoSuchElementException:
        print(f"{error_message}")
        return None


def _safe_get(driver, url):
    try:
        print(f"Loading {url}...")
        driver.get(url)

    except TimeoutException:
        print("Timeout error occurred — Check your internet connection.")
        return None


def _safe_wait(
        wait,
        condition,
        exception_type=TimeoutException,
        error_message="Could not find this element."):

    try:
        return wait.until(condition)

    except exception_type:
        print(f"{error_message}")
        return None


def _page_loaded(wait):
    print("Checking header...")
    header_el = _safe_wait(
        wait,
        ec.presence_of_element_located((By.XPATH, "//a[@aria-label='صفحه اصلی پونیشا']")),
        error_message="Could not find header element — "
                      "Check website accessibility or your internet connection."
    )

    if not header_el:
        return None

    return True


def _get_total_pages(wait):
    total_count_raw = _safe_wait(
        wait,
        ec.presence_of_element_located((By.XPATH, "//span[contains(@class, 'MuiTypography-h5')]")),
        error_message="Could not find total projects count element."
    )
    total_projects_count = clean_count(total_count_raw.text) if total_count_raw else None

    if not total_projects_count:
        return None

    print(f"{total_projects_count} projects have been found.")

    return ceil(total_projects_count/20)


def _login_check(wait):
    print("Logging check...")
    login_btn_el_status = _safe_wait(
        wait,
        ec.presence_of_element_located(
            (By.XPATH, "//button[@aria-label='باز و بسته کردن منوی کناری']")
        ),
        error_message="Could not find login button element."
    )

    return login_btn_el_status


def _manual_login(driver):
    print("You are not signed in — redirecting to login page...")
    print("Please log in during (180s)")
    long_wait = WebDriverWait(driver, 180)
    _safe_get(driver, PONISHA_LOGIN_URL)

    profile_menu_el = _safe_wait(
        long_wait,
        ec.presence_of_element_located(
            (By.XPATH, "//button[@aria-label='باز و بسته کردن منوی کناری']")
        ),
        error_message="Could not find login element again."
    )

    if not profile_menu_el:
        print("You could not sign in to 'Ponisha' — Try again!")
        return None

    return True


def _checkbox_status(wait):
    check_box_el = _safe_wait(
        wait,
        ec.presence_of_element_located((By.XPATH, "//input[@type='checkbox']")),
        error_message="Could not find checkbox element."
    )

    if not check_box_el:
        return None

    if not check_box_el.is_selected():
        old_project = _safe_wait(
            wait,
            ec.presence_of_element_located((By.XPATH, "//article"))
        )

        check_box_el.click()
        print("Clicked checkbox")

        if old_project:
            _safe_wait(
                wait,
                ec.staleness_of(old_project),
                error_message="Projects list did not refresh in time."
            )

    else:
        print("Checkbox is already selected.")

    return True


def _retrieve_projects(wait):
    all_projects = _safe_wait(
        wait,
        ec.presence_of_all_elements_located(
            (By.XPATH, "//main//article")
        ),
        error_message="Could not find projects counter element."
    )

    if not all_projects:
        return None

    projects_elements = [el for el in all_projects if el.is_displayed()]

    projects = {}
    for project in projects_elements:
        title = _field_text(project, ".//span[contains(@class, 'MuiTypography-h4')]")
        desc = _field_text(project, ".//span[contains(@class, 'MuiTypography-subtitle1')]")
        skills = _visible_texts(project, ".//span[contains(@class, 'MuiTypography-subtitle2')][position()>1]")

        deadline = _first_visible_text(
            project,
            ".//div[contains(@aria-label, 'فرصت انتخاب')]//span[contains(@class, 'MuiTypography-subtitle1')]"
        )

        # No aria-label or stable class available for bids count — positional fallback.
        # If this breaks, re-inspect the DOM structure around the bids' element.
        project_bids = _field_text(
            project,
            ".//span[contains(@class, 'MuiTypography-subtitle1') and "
            "contains(., 'پیشنهاد') and string-length(normalize-space(.)) < 20]"
        )

        budget = _field_text(
            project,
            ".//div[contains(@aria-label, 'بودجه کارفرما')]"
            "//span[contains(@class, 'MuiTypography-subtitle1')]"
        )

        project_url_el = _safe_find(
            project,
            ".//a[starts-with(@href, '/project/')]"
        )
        project_url = project_url_el.get_attribute('href') if project_url_el else None
        project_id = extract_id(project_url)

        projects[project_id] = {
            "title": title,
            "description": desc,
            "skills": skills,
            "deadline": deadline,
            "bids": project_bids,
            "budget": budget,
            "url": project_url
        }

    return projects


def login_only(headless=False):
    driver, wait = _setup_driver(headless)
    try:
        _safe_get(driver, PONISHA_HOME_URL)
        if _login_check(wait):
            print("You are already signed in - run program once again to scrape jobs.")
            return True

        else:
            if _teardown(_manual_login(driver)):
                print("Signed up successfully - run program once again to scrape jobs.")
                return True

            else:
                print("Login process failed - try again!")
                return None

    finally:
        driver.quit()


def scrape(headless=True):
    driver, wait = _setup_driver(headless)
    try:
        _safe_get(driver, PONISHA_HOME_URL)

        if not _teardown(_page_loaded(wait)):
            return None

        if not _login_check(wait):
            if not headless:
                if not _teardown(_manual_login(driver)):
                    return None

            else:
                print("Login required but driver is headless")
                return "LoginRequiredError"

        else:
            print("You are already signed up.")

        _safe_get(driver, PONISHA_PROJECTS_URL)

        if not _teardown(_page_loaded(wait)):
            return None

        if not _teardown(_checkbox_status(wait)):
            return None

        current_url = driver.current_url

        all_results = {}
        total_pages = _get_total_pages(wait)
        if not _teardown(total_pages):
            return None

        for page_num in range(1, total_pages + 1):
            if page_num > 1:
                page_url = build_page_url(current_url, page_num)
                _safe_get(driver, page_url)

                if not _teardown(_page_loaded(wait)):
                    return None

            else:
                page_url = current_url

            print(f"Retrieving projects from {page_url}")
            page_results = _retrieve_projects(wait)
            if page_results is None:
                return None

            all_results.update(page_results)

        return all_results

    finally:
        driver.quit()
