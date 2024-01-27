from selenium import webdriver
import string, random, time
from playsound import playsound
from typing import Union
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Defaullt = 9
ONETIME_EXECUTE_AMOUNT = 1
# Default = 5; Chill mode: 135-180
GENERATION_COOLDOWN = 180
# Default = True
FOCUS_ON_REVERSE_CHECKING = True
# Default = False
MINIMIZE_TABS = False

options = Options()
options.add_argument("start-minimized")
PATH = 'C:/Path/To/Chromedriver/Projects/RobloxAccountGenerator/chromedriver'

def closeDriver(drvr: webdriver.Chrome):
	drvr.close()
	drvr.quit()
def waitForElementAppear(strategy, locator, driver, timeout=10) -> Union[WebElement, bool]:
	try:
		element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((strategy, locator)))
	except (TimeoutException, NoSuchElementException):
		return False
	return element
def waitForElementClickable(strategy, locator, driver, timeout=10) -> Union[WebElement, bool]:
	try:
		element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((strategy, locator)))
	except (TimeoutException, NoSuchElementException):
		return False
	return element
def waitForElementDisappear(strategy, locator, driver, timeout=10) -> Union[WebElement, bool]:
	try:
		element = WebDriverWait(driver, timeout).until_not(EC.presence_of_element_located((strategy, locator)))
	except (TimeoutException, NoSuchElementException):
		return False
	return element
def generateUserPass(chars=string.ascii_lowercase+string.digits):
	length = random.randint(10, 16)
	# Password gotta be between 6 and 20
	passwordLength = 18
	user = password = ""
	for i in range(length):
		char = random.choice(chars)
		user += char.upper() if random.randint(0,1) == 1 else char if char.isalpha() else char
	for i in range(passwordLength):
		char = random.choice(chars)
		password += char.upper() if random.randint(0,1) == 1 else char if char.isalpha() else char
	# password = user[::-1]
	return { "username": user, "password": password }
def windowFocus(driver: webdriver.Chrome):
	driver.maximize_window()
	driver.switch_to.window(driver.current_window_handle)


def main():
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
	if MINIMIZE_TABS == True:
		driver.minimize_window()
	drivers = [driver]
	for i in range(ONETIME_EXECUTE_AMOUNT - 1):
		drvr = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
		if MINIMIZE_TABS == True:
			drvr.minimize_window()
		drivers.append(drvr)

	for driver in reversed(drivers):
		# driver: webdriver.Chrome
		if FOCUS_ON_REVERSE_CHECKING == True:
			windowFocus(driver)
		driver.get('https://www.roblox.com/')

	for driver in drivers:
		# Accept Cookies
		print("\nNew Account.")
		if cookieButton := waitForElementClickable(By.CLASS_NAME, "btn-cta-lg", driver, 4):
			cookieButton.click()
			print("Cookies accepted")


		# Initialize elements
		months = Select(driver.find_element(By.ID, "MonthDropdown"))
		days = Select(driver.find_element(By.ID, "DayDropdown"))
		years = Select(driver.find_element(By.ID, "YearDropdown"))
		username = driver.find_element(By.ID, "signup-username")
		password = driver.find_element(By.ID, "signup-password")
		femaleButton = driver.find_element(By.ID, "FemaleButton")
		maleButton = driver.find_element(By.ID, "MaleButton")
		submitButton = waitForElementClickable(By.ID, "signup-button", driver)

		# Fill in the Form
		# Birthday
		months.select_by_value('Jul')
		days.select_by_value('09')
		years.select_by_value('2000')

		# Credentials
		credentials = generateUserPass()
		username.send_keys(credentials["username"])
		password.send_keys(credentials["password"])

		# Gender
		femaleButton.click() if random.randint(0,1) == 1 else maleButton.click()

		# Submit the Form
		time.sleep(0.5)
		submitButton.click()

		# Username validation
		if usernameWarning := driver.find_element(By.ID, "signup-usernameInputValidation"):
			retries = 0
			while usernameWarning.text == "Username not appropriate for Roblox.":
				if retries == 3:
					print("Error 602: Username not appropriate for Roblox - max. retries (3) exceeded. Could not fetch account information.")
					return closeDriver(driver)
				retries += 1

				credentials = generateUserPass()
				username.clear()
				password.clear()
				time.sleep(0.5)
				username.send_keys(credentials["username"])
				password.send_keys(credentials["password"])
				time.sleep(0.5)
				submitButton.click()


		# Handling captcha and awaiting menu
		captchaSuccess = False

		if waitForElementAppear(By.CLASS_NAME, "icon-nav-settings", driver, 7):
			captchaSuccess = True
			print("No FunCaptcha")
		else:
			# FunCaptcha or Menu loading too long
			if waitForElementAppear(By.CLASS_NAME, "modal-modern-challenge-captcha", driver, 4):
				print("FunCaptcha met")
				windowFocus(driver)
				playsound("alarm.wav")

				# If captcha was solved
				if waitForElementDisappear(By.CLASS_NAME, "modal-modern-challenge-captcha", driver, 20):
					captchaSuccess = True
				else:
					captchaSuccess = False
					playsound("error.wav")

			# Checking if menu is loading too long
			elif waitForElementAppear(By.CLASS_NAME, "icon-nav-settings", driver, 3):
				captchaSuccess = True
			else:
				print("Error 603: Timeout exceeded.")
				return closeDriver(driver)


		if captchaSuccess == True:
			print("Fetched account information")
			with open("alts.txt", "a", encoding="utf-8") as f:
				f.write(f"{credentials['username']}:{credentials['password']}\n")
		else:
			print("Error 601: Could not fetch account information.")
		return closeDriver(driver)


EXECUTION_START_TIME = time.time()
with open("alts.txt", "r", encoding="utf-8") as f:
	EXECUTION_START_ACCOUNTS_AMOUNT = len(f.readlines())

i = 0
while i <= 10:
	main()
	with open("alts.txt", "r", encoding="utf-8") as f:
		EXECUTION_END_ACCOUNTS_AMOUNT = len(f.readlines())
	print(f"\nALREADY CREATED {EXECUTION_END_ACCOUNTS_AMOUNT} ACCOUNTS")
	print(f"Created {EXECUTION_END_ACCOUNTS_AMOUNT - EXECUTION_START_ACCOUNTS_AMOUNT} accounts for {time.time() - EXECUTION_START_TIME} seconds")
	time.sleep(GENERATION_COOLDOWN)
