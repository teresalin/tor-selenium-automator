import importlib
import random
import string
import time
import traceback
import os

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from stem import Signal
from stem.control import Controller

from datetime import datetime, timedelta
from unidecode import unidecode


# ----------------- Data Generation Functions -----------------


def generate_random_name(locale='en_US'):
    """
    Dynamically generate a name based on the locale parameter.
    :param locale: The locale to load names from (e.g., 'en_US', 'fr_FR', 'de_DE').
    :return: A tuple with first names and last names list.
    """
    try:
        # TODO add more locales
        module = importlib.import_module(f'locale_names.{locale}')

        first_names = getattr(module, 'first_names', [])
        last_names = getattr(module, 'last_names', [])

        if not first_names or not last_names:
            raise ValueError(
                f"First names or last names not found for locale '{locale}'.")

        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        return first_name, last_name

    except ModuleNotFoundError:
        print(f"Error: No names found for the locale '{locale}'.")
        return None, None
    except AttributeError:
        print(
            f"Error: The locale '{locale}' does not contain 'first_names' or 'last_names'.")
        return None, None
    except ValueError as ve:
        print(ve)
        return None, None


def generate_random_birthday():
    """
    Randomly generate a birthday between 1980 and 2002 and returns it in dd m yyyy format.
    """
    start_date = datetime(1980, 1, 1)
    end_date = datetime(2002, 12, 31)

    random_days = random.randint(0, (end_date - start_date).days)
    birthday = start_date + timedelta(days=random_days)

    # Format day as two digits and month as a single digit
    day = birthday.strftime("%d")
    month = birthday.strftime("%m").lstrip('0')
    year = birthday.strftime("%Y")

    return f"{day} {month} {year}"


def generate_random_password(length=12):
    """
    Randomly generate a password of a given length.

    Keyword arguments:
    length -- the length of the password (default 12)
    """
    # Define the characters you want to use (letters, digits, special characters)
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = ''.join(random.choice(characters) for i in range(length))
    return password


def generate_username(first_name, last_name):
    random_number = random.randint(1000, 9999)
    first_name_lowercase = unidecode(first_name).lower()
    last_name_lowercase = unidecode(last_name).lower()
    return f"{first_name_lowercase}.{last_name_lowercase}{random_number}"


def random_sleep(min_time=1.5, max_time=4.5):
    """
    Pauses execution for a random amount of time between min_time and max_time.
    This helps mimic human-like behavior during automation.
    """
    sleep_time = random.uniform(min_time, max_time)
    print(f"Sleeping for {round(sleep_time, 2)} seconds...")
    time.sleep(sleep_time)


# ----------------- Tor IP Renewal Function -----------------


def renew_tor_ip():
    """
    Sends a NEWNYM signal to the Tor network to request a new circuit, effectively
    assigning a new exit node (and thus a new IP address) for the current session.

    How it works:
    - The Tor network routes traffic through multiple relays to anonymize your connection.
    - Each relay chain (or circuit) has an exit node, which is the final relay that
      connects to the public internet, determining your apparent IP address.
    - By sending a 'NEWNYM' (New Identity) signal, we tell the Tor process to close
      the current circuit and create a new one with a different exit node, resulting
      in a new public-facing IP address.

    When to use this function:
    - **Long-running sessions**: If your script runs for a long period and you want
      to periodically change your IP without restarting the browser, calling this function
      will give you a fresh IP during the session.
    - **Multiple actions in a single session**: If you're performing multiple automated tasks
      in one browser session and want to use a different IP address for each action to avoid
      detection or rate-limiting, you can use this function to request a new IP between tasks.
    - **Avoiding IP bans or throttling**: Some websites may detect multiple actions
      from the same IP and temporarily block or throttle traffic. Renewing the IP frequently
      can help bypass these restrictions.
    - **Anonymous web scraping**: If you're scraping content from websites and want to
      avoid using the same IP address for too many requests, you can renew the Tor IP to
      rotate through multiple exit nodes, making it harder for websites to detect the scraping activity.

    When not to use:
    - **For every new session**: If you're closing and reopening the Tor Browser with each
      script execution, Tor automatically assigns a new IP, so manually renewing the IP is
      unnecessary in this case.

    """
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()  # Authenticate the Tor connection
        controller.signal(Signal.NEWNYM)  # Request a new identity


# ----------------- Browser Setup and Configuration Functions -----------------


def create_torbrowser_webdriver_instance():
    options = Options()
    options.headless = False
    # By default, Selenium looks for the browser's executable (e.g., Firefox, Chrome)
    # in the system's standard installation directories to launch the browser.
    #
    # However, since we are using the Tor Browser—a customized version of Firefox
    # that is not installed in a standard location—Selenium needs to be explicitly
    # instructed where to find the Tor Browser's Firefox binary.
    #
    # The Tor Browser comes with its own customized version of Firefox (Firefox ESR),
    # and specifying the binary location ensures Selenium launches this specific
    # version instead of the system-installed Firefox.
    #
    # Specify the path to your Tor Browser's Firefox executable
    # Note: Replace the path below with the actual location of your Tor Browser's Firefox binary
    # Example: '/Applications/Tor Browser.app/Contents/MacOS/firefox' on Mac
    # and 'C:/Users/teresalin/Desktop/Tor Browser/Browser/firefox.exe' on Windows
    binary = 'C:/path/to/your/Tor Browser/Browser/firefox.exe'
    if os.path.exists(binary) is False:
        raise ValueError("The binary path to Tor firefox does not exist.")
    options.binary_location = binary

    # Disable and remove WebDriver flags and attributes

    # 1. Disables the `dom.webdriver.enabled` attribute to avoid detection:
    #    When Selenium is used to automate a browser, the browser sets a special
    #    `navigator.webdriver` attribute to `true`. Many websites check this flag
    #    to detect automation (bot-like behavior) and block access or show CAPTCHAs.
    #    Setting this preference to `False` helps prevent websites from detecting
    #    that the browser is being controlled by Selenium, making the automation
    #    appear more like regular browsing.
    options.set_preference("dom.webdriver.enabled", False)

    # 2. Disables the `useAutomationExtension` to remove Selenium automation flags:
    #    Firefox has a built-in automation extension that Selenium uses to communicate
    #    with the browser. This extension is automatically loaded when Selenium starts
    #    a browser, and its presence can be detected by some websites. By setting
    #    `useAutomationExtension` to `False`, you prevent Firefox from loading this
    #    extension, reducing the chance of detection that the browser is being controlled
    #    by automation.
    options.set_preference('useAutomationExtension', False)

    # 3. Disables browser notifications (web push notifications):
    #    Websites often request permission to show notifications (e.g., updates, news).
    #    Allowing or blocking these notifications could reveal that the browser is automated,
    #    as bots tend to always deny or block notifications. By disabling the notifications
    #    altogether using `dom.webnotifications.enabled = False`, you prevent any notifications
    #    from appearing during the automated browsing session, helping to avoid detection.
    options.set_preference('dom.webnotifications.enabled', False)

    # Set up the SOCKS proxy to route traffic through Tor
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.socks_proxy = '127.0.0.1:9150'  # Default SOCKS proxy for Tor
    proxy.socks_version = 5
    options.proxy = proxy

    # Disable WebRTC to prevent leaking the real IP
    options.set_preference("media.peerconnection.enabled", False)

    # Create WebDriver instance using GeckoDriverManager and Firefox options
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=options
    )

    # Set a common screen size
    driver.set_window_size(1366, 768)

    # Reduce WebGL fingerprintability without fully disabling it
    driver.execute_script('''
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'NVIDIA';  // Spoof GPU vendor
            if (parameter === 37446) return 'GeForce GTX';  // Spoof GPU renderer
            return getParameter.call(this, parameter);
        };
    ''')

    return driver


def click_connect_button(driver):
    try:
        # Wait for the "Connect" button to appear on the Tor startup page
        wait = WebDriverWait(driver, 20)
        connect_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@id='connectButton' or text()='Connect']"))
        )
        print("Connect button detected, connecting...")
        connect_button.click()

        # Wait for the Tor network to complete connecttion (you may need to adjust the wait time)
        time.sleep(10)

    except TimeoutException:
        print("Error: Connect button not found or connection failed.")
        traceback.print_exc()


def verify_tor_connection(driver):
    try:
        # Navigate to the Tor project's check page to verify if traffic is routed through the Tor network.
        # This page displays a confirmation message if the connection is successfully using Tor.
        driver.get("https://check.torproject.org")

        # Set up a wait condition to allow time for the page to load.
        # The function waits for up to 30 seconds for an element containing the text "Congratulations"
        # to appear, which is Tor's indication that the browser is successfully connected to the network.
        wait = WebDriverWait(driver, 30)
        confirmation_text = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(), 'Congratulations')]"))
        )

        print("Tor is connected: ", confirmation_text.text)
        return True
    except TimeoutException:
        print("Error: Tor is unable to establish a connection.")
        traceback.print_exc()
        return False


# ----------------- Account Creation Workflow Functions -----------------


def enter_username_flow(driver, wait, your_username):
    try:
        username_field = wait.until(
            EC.element_to_be_clickable((By.NAME, "Username"))
        )
        username_field.clear()
        username_field.send_keys(your_username)
        next_button = driver.find_element(By.CLASS_NAME, "VfPpkd-LgbsSe")
        next_button.click()
    except TimeoutException:
        print("Error: Failed to enter username or click next.")


def create_gmail_account(driver):
    your_first_name, your_last_name = generate_random_name()
    your_birthday = generate_random_birthday()

    # Enter your own phone number here
    # Note: Replace '+11234567890' with your actual phone number
    your_phone_number = '+11234567890'

    your_password = generate_random_password()

    gender_options = ["1", "2", "3"]
    your_gender = random.choice(gender_options)

    try:
        # Ensure Tor Browser is started and the connect button is clicked
        click_connect_button(driver)

        if verify_tor_connection(driver):
            print("Tor is successfully connected. Proceeding to Google sign-up page.")
            driver.get(
                "https://accounts.google.com/signup/v2/createaccount?flowName=GlifWebSignIn&flowEntry=SignUp")
        else:
            print("Error: Tor connection failed. Cannot proceed to Google sign-up page.")
            return

        # Fill in first name and last name fields
        first_name_field = driver.find_element(By.NAME, "firstName")
        last_name_field = driver.find_element(By.NAME, "lastName")
        first_name_field.clear()
        random_sleep()
        first_name_field.send_keys(your_first_name)
        last_name_field.clear()
        random_sleep()
        last_name_field.send_keys(your_last_name)
        random_sleep()
        next_button = driver.find_element(By.CLASS_NAME, "VfPpkd-LgbsSe")
        next_button.click()

        # Wait for birthday fields to be visible
        wait = WebDriverWait(driver, 20)
        day = wait.until(EC.visibility_of_element_located((By.NAME, "day")))

        # Fill in birthday fields
        birthday_elements = your_birthday.split()
        wait.until(EC.invisibility_of_element_located(
            (By.CLASS_NAME, "kPY6ve")))
        random_sleep()
        month_dropdown = Select(driver.find_element(By.ID, "month"))
        random_sleep()
        month_dropdown.select_by_value(birthday_elements[1])
        day_field = driver.find_element(By.ID, "day")
        day_field.clear()
        random_sleep()
        day_field.send_keys(birthday_elements[0])
        year_field = driver.find_element(By.ID, "year")
        year_field.clear()
        random_sleep()
        year_field.send_keys(birthday_elements[2])

        random_sleep()

        # Select gender
        gender_dropdown = Select(driver.find_element(By.ID, "gender"))
        random_sleep()
        gender_dropdown.select_by_value(your_gender)
        random_sleep()
        next_button = driver.find_element(By.CLASS_NAME, "VfPpkd-LgbsSe")
        next_button.click()
        random_sleep()

        try:
            your_username = generate_username(your_first_name, your_last_name)

            # Scenario 1: Three selections present with the last to create your own Gmail address
            if driver.find_elements(By.ID, "selectionc4"):
                create_own_option = wait.until(
                    EC.element_to_be_clickable((By.ID, "selectionc4")))
                create_own_option.click()
                enter_username_flow(driver, wait, your_username)
            # Scenario 2: No selection present. Enter value into username field.
            elif driver.find_elements(By.NAME, "Username"):
                enter_username_flow(driver, wait, your_username)
            # Scenario 3: Two selections present with the first one to create your own Gmail address
            elif driver.find_elements(By.XPATH, "//div[text()='Create a Gmail address']"):
                # Select the radio button by its data-value attribute
                radio_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//div[@role='radio' and @data-value='1']"))
                )
                radio_button.click()

                next_button = driver.find_element(
                    By.CLASS_NAME, "VfPpkd-LgbsSe")
                next_button.click()

                try:
                    # Check if the 'Create your own Gmail address' option becomes visible
                    create_your_own_gmail = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "selectionc7")))
                    if create_your_own_gmail:
                        create_your_own_gmail.click()
                        enter_username_flow(driver, wait, your_username)
                except TimeoutException:
                    # If the 'Create your own Gmail address' is not visible, check for Username field
                    try:
                        username_field = wait.until(
                            EC.visibility_of_element_located((By.NAME, "Username")))
                        if username_field:
                            enter_username_flow(driver, wait, your_username)
                    except TimeoutException:
                        print(
                            "Error: Neither 'Create your own Gmail address' nor 'Username' field is visible.")
                        return
            else:
                # TODO handle unexpected account creation scenario
                print('Unable to detect a valid account creation scenario.')
                return
        except TimeoutException:
            print(
                "Error: Operation timed out while attempting to find a suitable account creation flow.")
            return

        # Enter and confirm password
        password_field = wait.until(
            EC.visibility_of_element_located((By.NAME, "Passwd")))
        password_field.clear()
        random_sleep()
        password_field.send_keys(your_password)
        confirm_passwd_div = driver.find_element(By.ID, "confirm-passwd")
        password_confirmation_field = confirm_passwd_div.find_element(
            By.NAME, "PasswdAgain")
        password_confirmation_field.clear()
        random_sleep()
        password_confirmation_field.send_keys(your_password)
        random_sleep()
        next_button = driver.find_element(By.CLASS_NAME, "VfPpkd-LgbsSe")
        next_button.click()

        random_sleep()

        # Enter phone number
        phone_number_field = wait.until(
            EC.element_to_be_clickable((By.ID, "phoneNumberId")))
        phone_number_field.clear()
        random_sleep()
        phone_number_field.send_keys(your_phone_number)
        random_sleep()
        next_button = driver.find_element(By.CLASS_NAME, "VfPpkd-LgbsSe")
        next_button.click()

        random_sleep()

        # Agree to terms
        agree_button = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "button span.VfPpkd-vQzf8d")))
        agree_button.click()

        print(
            f"Gmail account created successfully:\n{{\ngmail address: {your_username}@gmail.com\npassword: {your_password}\n}}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()


# ----------------- Main Execution Block -----------------

if __name__ == '__main__':
    driver = create_torbrowser_webdriver_instance()
    create_gmail_account(driver)
    driver.close()
