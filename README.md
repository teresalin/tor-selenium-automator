# Tor-Selenium Automated Gmail Creator

An automated Gmail account creation tool designed for anonymity and anti-bot evasion, leveraging Python, Selenium, and the Tor Browser to provide secure and stealthy automation.

## Overview

This Python script automates the process of creating accounts using Selenium and the Tor Browser to ensure anonymity. It generates dynamic user data (names, birthdays, passwords, and usernames), handles browser interactions, and ensures that all traffic is routed through the Tor network for added privacy. The project uses webdriver_manager for managing the browser driver and incorporates various techniques to balance anonymity and bot detection avoidance.

To maintain anonymity, the script adheres to Tor's default settings wherever possible, including the user agent, fonts, language, and timezone, ensuring consistency with other Tor users and reducing the likelihood of being uniquely identified. At the same time, to avoid bot detection, the script includes specific human-like browsing behaviors—such as random delays between actions, WebGL attribute spoofing, and setting a common screen resolution—to make interactions appear more natural and less automated.

This careful balance allows the script to provide effective account automation while maintaining privacy and reducing the chances of being flagged by anti-bot systems.

## Features

1. **Automated Account Creation**

    - Generates dynamic user data (names, birthdays, usernames, passwords).
    - Automates form filling and navigation for account creation.

2. **Tor Browser Integration**

    - Routes all traffic through the Tor network for anonymity.
    - Configurable to run in headless mode for faster execution.

3. **Dynamic User Data Generation**

    - Locale-based name generation (e.g., 'en_US', 'fr_FR').
    - Randomized birthdays (1980 - 2002) and secure password generation.

4. **Human-Like Browsing Behavior**

    - Random delays between actions to mimic human interaction.

5. **Anti-Bot Detection Techniques**

    - **WebGL Spoofing**: Randomizes GPU vendor/renderer to avoid fingerprinting.
    - Disables Selenium detection flags (`dom.webdriver.enabled`, `useAutomationExtension`).
    - **WebRTC Disabled**: Prevents real IP exposure.

6. **Consistent Anonymity Features**

    - Maintains Tor's default user agent, language, and timezone for consistency.
    - Blocks web notifications to avoid interaction disruptions.

7. **IP Renewal on Demand**

    - Uses `NEWNYM` signal to request a new Tor circuit, providing a fresh IP during long sessions.

8. **Error Handling and Flow Management**

    - Manages unexpected scenarios with detailed logging and error messages.

9. **Custom Locale Support**

    - Configurable locale for generating culturally relevant names.

10. **Anonymity vs. Bot Detection Balance**
    - Carefully balances privacy features with anti-bot evasion techniques for effective automation.

## Usage

1. Download [Tor Browser](https://www.torproject.org/download/)

2. Clone this repository:

    ```
    git clone https://github.com/teresalin/tor-selenium-automator.git
    ```

3. Install the required libraries:

    ```
    pip install -r requirements.txt
    ```

4. Go through the code in <code>create_gmail_account.py</code> and update any necessary field values

5. Execute the Python script:

    ```
    python create_gmail_account.py
    ```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Disclaimer

This project is for educational purposes only. It demonstrates web automation using Python and Selenium, along with the Tor network for privacy. Automated interaction with websites may violate the terms of service of certain platforms, and unauthorized use of this script may lead to account suspension or legal action. The author assumes no responsibility for any misuse of this code.

Before using this script, ensure that your actions comply with the relevant legal and ethical guidelines, and always respect the terms of service of any platform you interact with.

## License

This project is released under the MIT License. See the bundled [LICENSE](https://github.com/teresalin/tor-selenium-automator/blob/main/LICENSE) file for details.
