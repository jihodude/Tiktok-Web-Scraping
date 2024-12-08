#chrome.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException
import sellerCenterFunctions as sc
from selenium.common.exceptions import NoSuchElementException



profile_path = "/Users/jihobae/Library/Application Support/Google/Chrome/Default"

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")


options.add_argument(f"user-data-dir={profile_path}")  # only works if the tiktok seller center is open on my default chrome.****
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Initialize ChromeDriver
service = Service(executable_path="/Users/jihobae/Documents/Programming/Selenium Tiktok Manager/Tiktok-Web-Scraping/Untitled/chromedriver")
#I am hoping this works

driver = webdriver.Chrome(service=service, options=options)



try:
    sc.getPage(driver)
    if (not sc.checkLogin(driver, False)):
        print("running...")
        sc.login(driver)
        sc.twoFA(driver)
        sc.checkLogin(driver, True) # this will return True

    
    sc.getFilePath()
    sc.loadProductUsernames()

    demographicSections = ["Ready to Ship", "Shipped", "In-progress"]
    contentSections = ["Completed"]

    for sectionName in demographicSections:
        print(f"Processing section: {sectionName}")
        rows = sc.identifyProduct(sectionName, driver)
        has_next_page = True
        page_count = 1
        while has_next_page:
            try:
                print(f"Processing page {page_count} for section: {sectionName}")  # Select section once
                
                # Section-specific logic
                if sectionName in contentSections:
                    print(f"Applying specific logic for content section: {sectionName}")
                    sc.getUsername(rows)


                else:
                    # Default logic for demographicSections
                    sc.getUsername(rows)

                has_next_page = sc.nextPage(driver)
                page_count += 1
            except TimeoutException as e:
                print(f"Timeout occurred during page {page_count} of section {sectionName}: {e}")
                break
            except NoSuchElementException as e:
                print(f"Element not found: {e}")
                break
            except Exception as e:
                print(f"Unexpected error during page {page_count} of section {sectionName}: {e}")
                break
        print(f"Completed pagination for section: {sectionName}")
        
        
    sc.findUniqueUserName()
    update_status = "no"  # Default value or retrieve from the GUI
    sc.saveUserData(update_status)                                       #find everyone
    sc.printUsernameAndLink()



except Exception as e:
    print(f"An error occurred in the main script: {e}")
    
finally:
    input("press enter to quit...")
    driver.quit()