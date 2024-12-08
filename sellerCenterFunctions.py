# sellerCenterFunctions.py

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
import time
import json
import os

email = "jihodude@gmail.com"
password = "Uu107746!"
product = "Kiera"

usernames = set()
usernamesData = set()
newUsernames = set()
def getPage(driver):
    driver.get("https://affiliate-us.tiktok.com/product/sample-request?source_from=seller_affiliate_landing&shop_region=US")

def login(driver):
    getPage(driver)
    pageLoadComfirm = WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH, "//span[@class='theme-arco-tabs-header-title-text' and text()='Email']"))
    )
    Element = driver.find_element(By.CLASS_NAME, "theme-arco-tabs-header-title-text")
    Element.click()
    Element = driver.find_element(By.ID, "TikTok_Ads_SSO_Login_Email_Input")
    Element.send_keys(email)
    Element = driver.find_element(By.ID, "TikTok_Ads_SSO_Login_Pwd_Input")
    Element.send_keys(password)
    Element = driver.find_element(By.ID, "TikTok_Ads_SSO_Login_Btn")
    Element.click()

def twoFA(driver):
    verification_confirm = WebDriverWait(driver, 120).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "TUXButton-content"))
    )
    twoFAcode = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.ID, "TikTok_Ads_SSO_Login_Code_Input"))
    )
    verficationCode = input("Enter 2FA verification code: ")
    twoFAcode.send_keys(verficationCode)
    twoFAcode.send_keys(Keys.RETURN)

def checkLogin(driver, afterLogin):
    
    try:
        if(afterLogin):
            WebDriverWait(driver, 120).until(EC.url_contains("sample-request"))

        # Check for an element that confirms successful login
        if "sample-request" in driver.current_url:
            print("User logged in successfully.")
            return True
        else:
            print("User is NOT logged in. URL does not contain 'sample-request'.")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        print("finally")
        

def identifyProduct(section_name, driver):
    global sectionName
    sectionName = section_name
        
    print(f"Interacting with column: {section_name} for {product}")
    
    try:
        # Wait for the section to be clickable
        section = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[text()='{section_name}']"))
        )
        try:
            # Attempt to click the section
            section.click()
        except ElementClickInterceptedException:
            print("ElementClickInterceptedException: Retrying with JavaScript...")
            driver.execute_script("arguments[0].click();", section)  # Force the click with JS
        
        # Wait for rows to load after clicking the section
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//tr[@class='arco-table-tr']"))
        )
    except TimeoutException:
        print(f"Timeout: Unable to locate or click the section: {section_name}")
        return []
    except Exception as e:
        print(f"Unexpected error interacting with section: {e}")
        return []

    # Initialize filtered_rows to store rows matching the product
    filtered_rows = []
    time.sleep(2)

    # Locate all rows in the current section
    rows = driver.find_elements(By.XPATH, "//tr[@class='arco-table-tr']")
    if sectionName == "Completed":
        for row in rows:
            try:
                button = row.find_element(By.XPATH, './/div[@class="flex items-center justify-end" and @data-e2e]')
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="flex items-center justify-end" and @data-e2e]')))
                button.click()

                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, ".//tr[@class='arco-table-tr arco-table-expand-content']")))
                expandedRow = driver.find_element(By.XPATH, ".//tr[@class='arco-table-tr arco-table-expand-content']")
                product_name_element = expandedRow.find_element(By.XPATH, ".//span[@class='inline-block truncate']")
                
                if product in product_name_element.text:
                    filtered_rows.append(row)

                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="flex items-center justify-end" and @data-e2e]')))
                button.click()
            except Exception as e:
                print(f"Error clicking button: {e}")
            except NoSuchElementException:
                print("Product name element not found in row; skipping.")
    else:
        for row in rows:
            try:
                product_name_element = row.find_element(By.XPATH, ".//span[@class='inline-block truncate']")
                if product in product_name_element.text:
                    filtered_rows.append(row)
            except NoSuchElementException:
                print("Product name element not found in row; skipping.")
    print("\n")
    return filtered_rows


def getUsername(filtered):
    if not filtered:
        print("No rows to process.")
        return  # Avoid unnecessary calls to `nextPage`

    for row in filtered:
        userTagElement = None
        try:
            userTagElement = row.find_element(By.XPATH, ".//div[contains(@class, 'truncate') and contains(@class, 'text-neutral-text2')]")
        except:
            pass

        if userTagElement:
            print("username:", userTagElement.text)
            usernames.add(userTagElement.text)
        else:
            print("Could not find username.")

def safe_click(driver, xpath, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        try:
            element.click()
        except Exception:
            driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        print(f"Error clicking element {xpath}: {e}")
        return False
    
def nextPage(driver):
    try:
        # Re-fetch the "Next" button after each page load
        nextButton = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//li[@aria-label="Next"]'))
        )

        # Check if the button is disabled
        button_classes = nextButton.get_attribute("class")
        if "arco-pagination-item-disabled" in button_classes:
            print("Next button is disabled. No more pages.")
            return False

        # If the button is clickable, click it
        if(safe_click(driver,'//li[@aria-label="Next"]', 5)):
            print("Next button is clickable. Moving to the next page.")
              # Force click using JS
        else:
            print("Failed to click 'Next' button.")

        # Wait for the next page to load fresh elements
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//tr[@class='arco-table-tr']"))
        )
        time.sleep(2)
        return True
    except StaleElementReferenceException:
        print("Stale element reference detected. Retrying...")
        return nextPage(driver)  # Retry fetching the element
    except TimeoutException:
        print("TimeoutException: 'Next' button not clickable or not found.")
        return False
    except Exception as e:
        print(f"Unexpected pagination error: {e}")
        return False



def printUsernameAndLink():
    count = 0
    print("New Usernames:\n")
    for newUsername in newUsernames:
        count += 1
        print(newUsername)
    print(f"\n count:{count}")

    print("New Username Links: \n")
    for newUsername in newUsernames:
        print(f"https://www.tiktok.com/@{newUsername}")
    print("\n")
    print("\n")
    print("All of the usernames:")
    for username in usernames:
        print(username)

    print("\n")
    print("\n")
    print("usernames not in the excelsheet:")
    for username in usernames:
        strippedUsername = username.lstrip('@').strip()
        if strippedUsername not in productList:
            print(strippedUsername)

#manual check
#Dr.Percent
# productList = [
#     "lizethmartinez962",
#     "katanamisterio",
#     "christywhite3906",
#     "elizabethday66",
#     "officialevycruz",
#     "Queen_Deya02",
#     "wandita_la_bori",
#     "wesley_mendoza",
#     "ketokouple2022",
#     "umachhetri019",
#     "bulletlikeak47punjab",
#     "goodvibeswithmadison",
#     "paigerussell",
#     "_____janu______22",
#     "floxydiaba",
#     "mariacarrillo4796",
#     "perlas.shop",
#     "victoria_aldana7",
#     "mauricioelchapin",
#     "tejusapkota2",
#     "marioskingdom",
#     "lupita022166",
#     "avyfitness",
#     "ketobbwblondie",
#     "brendaa_cardenas",
#     "sarah.lou34",
#     "millenialmom92",
#     "ositanails",
#     "airwrecka23",
#     "singhsarus",
#     "chirlenakleshinsk",
#     "amaalalhabib.offcially",
#     "85negra1",
#     "oneclassybitchh",
#     "bhrunabm",
#     "shannonlynnboyce",
#     "sam.mom.shop",
#     "cookingwithpassion",
#     "rubendy31",
#     "vrodasargueta",
#     "estheryork2",
#     "umachhetri019",
#     "bulletlikeak47punjab",
#     "dieunelp",
#     "soberssmile",
#     "jooleemomi",
#     "tammyv48",
#     "_ebonydenise",
#     "shelbyrasnerd",
#     "fanmverite",
#     "manjitasingh2020",
#     "formidablyfrugal",
#     "mattcansell69",
#     "bestwiginfluencer97",
#     "viralfindzofficial",
#     "sabina.525",
#     "renaser04",
#     "laurapaniagua59",
#     "madhu_acharya123",
#     "lyndseydanielle3",
#     "mamacarrieb",
#     "kristie_kma.toseveral",
#     "willowandizzysmommy",
#     "tulasha013",
#     "cortneydawnecox",
#     "alexandraaa_moure",
#     "lifewithjennileegarner",
#     "tiffanychevelleofficial",
#     "empress.toniatte",
#     "jennifersgems",
#     "keep.it.korean",
#     "soberssmile",
#     "princessammi07",
#     "naomiveras",
#     "lamorenitaguerrera",
#     "lalisa777california",
#     "recovery_girl_glam",
#     "mistyparker64",
#     "sukifrench",
#     "moisturizedoverhere",
#     "amyfaulkner2021",
#     "myrosiedumpling",
#     "binakarki212",
#     "sherryfoxfairy12"
# ]

#ECOAND
# productList = [
#     "tiffanychevelleofficial",
#     "sippinbangz",
#     "summerangel98",
#     "prativa576",
#     "lamorenitaguerrera",
#     "naomiveras",
#     "recovery_girl_glam",
#     "amyfaulkner2021",
#     "yuri1050",
#     "anamrqz09",
#     "devikakoirala",
#     "laurapaniagua59",
#     "queenofhope51",
#     "soberssmile",
#     "tammiebrowning",
#     "sapnabhatta41",
#     "contentcreator000001",
#     "alpana740",
#     "la_____licenciada",
#     "nellysstores",
#     "candycrush91891",
#     "Lamamounia",
#     "its_me_ziya008",
#     "heerasharma26",
#     "lifewithjennileegarner",
#     "tiktoktrendshop300",
#     "ticamusulmana1",
#     "mamaevy3",
#     "mkettofficial",
#     "idoidoloubeau",
#     "rj_shabanu123",
#     "christinelindsay_beauty",
#     "justamy86",
#     "jordanferg4",
#     "themole2005_official",
#     "launica499",
#     "erikagutierrez359",
#     "jennifersgems",
#     "lyndseydanielle3",
#     "manjitasingh2020",
#     "viralfindzofficial",
#     "bestwiginfluencer97",
#     "sabina.525",
#     "salmar30",
#     "renaser04",
#     "madhu_acharya123",
#     "therealchelsiebeatty",
#     "mistyparker64",
#     "radhagautam244",
#     "bhein36",
#     "lalisa777california",
#     "wingwomanmc",
#     "justkelly33",
#     "jyotisankhar",
#     "keep.it.korean",
#     "empress.toniatte",
#     "cortneydawnecox",
#     "cocorixrealtor",
#     "princessammi07",
#     "mariacarrillo4796",
#     "estheryork2",
#     "teraneeka",
#     "momthatistrying",
#     "nikki.ruston",
#     "racheldoll86",
#     "tiersamv",
#     "kimberlymulgrew",
#     "fancybiggirl0",
#     "keiiwee93",
#     "elizabeth888a",
#     "nichole.coic",
#     "findsbygabby",
#     "singlerockinmommaof2",
#     "catlife669",
#     "sherryfoxfairy12",
#     "cocorixydixy"
# ]

#kiera
# productList = [
#     "princessammi07",
#     "lifewithjennileegarner",
#     "jyotisankhar",
#     "salmar30",
#     "onceuponatimeinprison",
#     "alexandraaa_moure",
#     "estheryork2",
#     "willowandizzysmommy",
#     "radhagautam244",
#     "erikagutierrez359",
#     "lalisa777california",
#     "soberssmile",
#     "jennifersgems",
#     "mariacarrillo4796",
#     "neh14002",
#     "binakarki212",
#     "simplysourced",
#     "recovery_girl_glam",
#     "devikakoirala",
#     "sadie__peach",
#     "mattcansell69",
#     "nostix1andonly",
#     "icantfindatiktok",
#     "vp.creativeusa",
#     "gayerenee",
#     "isabellachambers49",
#     "meg207",
#     "singlerockinmommaof2",
#     "zavalajuana",
#     "empress.toniatte",
#     "laurensarahart",
#     "greybegae",
#     "lamorenitaguerrera",
#     "ansleyrwelch",
#     "nikki.ruston",
#     "dabxrbiiee._"
# ]

#hands
productList = [
    "thuuiee",
    "litlikeliterature",
    "sourpatchgenxkid2.0",
    "krishnakp231",
    "keep.it.korean",
    "birdiesbestfinds",
    "heyyouguys129",
    "the_names_gale",
    "moomoojazzy",
    "he1lokittybaby",
    "bambiandjaxonyorkiesibs",
    "k.church08",
    "nanamarie70",
    "greybegae",
    "lovelysova5",
    "lupegarcia119",
    "iamjenniluv",
    "gigiarford",
    "mailinconcepcion1",
    "nottoday826",
    "_tranquilserenity_",
    "kati3.m",
    "rachel17173",
    "neiceycreationz",
    "royalreflections_hb",
    "pegbama",
    "jacquedavidson",
    "emilynicholexoxo",
    "ladyang",
    "wingsms4",
    "darlingdeeznutz",
    "brispomsvip",
    "oneandonlydestinymarie",
    "shobhapokhrel2",
    "kasspetrowitz",
    "living.the.dream.777",
    "icantfindatiktok",
    "jessicasshoppingspree",
    "aponi143",
    "kimberlysemien",
    "courtneytaschler13",
    "kristin_no_e",
    "meg207",
    "singlerockinmommaof2",
    "amykate8675309",
    "kausilabhattaraidahal596",
    "tara.linn",
    "mymarlie7",
    "mamiandminions",
    "soobyduby",
    "gene24170",
    "shantidahal40",
    "queenbitchhhhh_",
    "yulyc300",
    "overturning_cant",
    "landkremas",
    "missveee03",
    "user8073377650629",
    "smilingsher",
    "kelliemichelle",
    ".mamaholls",
    "ms.alisha75",
    "anaavila259",
    "kimcongrovewalker",
    "farianylopez",
    "areli78906",
    "westindianhottie",
    "in_my_forties_era",
    "my_cats_are_weirdos",
    "ramonamainit",
    "milorvecharles",
    "chikizxoxo",
    "notthatjessica",
    "seoulassassin",
    "tammiherr",
    "mamamaniaof2",
    "yesyoucansitwithus",
    "leaisabellabates",
    "cgilbert4131",
    "gladisemancia",
    "dumb.ah.bih",
    "alisprivatestory222",
    "letterstov_"
]



def getFilePath():

    script_dir = os.path.dirname(__file__)
    database_folder = os.path.join(script_dir, "ProductUsernameDatabase")

    if not os.path.exists(database_folder):
        os.makedirs(database_folder)
        
    filePath = os.path.join(database_folder, f"{product}.txt")
    return filePath

def loadProductUsernames(): #returns productFilePath
    global usernamesData
    global usernamesDict
    productFilePath = getFilePath()
    try:
        # Check if file exists, create if not
        if not os.path.exists(productFilePath):
            with open(productFilePath, "w") as file:
                # Initialize with an empty JSON object (dictionary)
                file.write("{}")

        with open(productFilePath, "r") as file:
            # Load JSON data as a dictionary
            global userDataDictionary 
            usernamesDict = json.loads(file.read() or "{}")
            userDataDictionary = usernamesDict
            # If needed, extract just the keys (usernames) into a set
            usernamesData = set(usernamesDict.keys())
            
        return productFilePath
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading usernames: {e}. Initializing empty dictionary.")
        usernamesData = set()
    
def findUniqueUserName():
  # Load existing usernames from the file into a set

    # Iterate through the `usernames` set and process them
    for name in usernames:
        # Remove "@" prefix and strip whitespace for comparison
        stripped_name = name.lstrip('@').strip()

        # Check if the cleaned username is not in the stored data
        if stripped_name not in usernamesData:
            newUsernames.add(stripped_name)  # Add to the `newUsernames` set


def updateUploadStatus(section):
    for username in usernames:
        stripped_name = username.lstrip('@').strip()
        current_update_status = usernamesDict.get(username, {}).get("update status")
        originalContentType = userDataDictionary.get(username, {}).get("content type", "video")
        usernamesDict[stripped_name] = {
            "upload status": "yes" if section == "Completed" else "no",
            "update status": current_update_status,
            "content type": originalContentType
        }





def saveUserData(update_status):  # Accept update_status as a parameter
    productFilePath = getFilePath()

    updateUploadStatus(sectionName)
    for username in usernames:
        # Check if the username exists in the dictionary already and preserve its original content type
        originalContentType = userDataDictionary.get(username, {}).get("content type", "video")
        originalUploadStatus = userDataDictionary.get(username, {}).get("upload status", "no")

        stripped_name = username.lstrip('@').strip()
        # Update or add data for the current username
        userDataDictionary[stripped_name] = {
            "upload status": originalUploadStatus,
            "update status": "yes" if update_status == "yes" else "no",
            "content type": originalContentType
        }

    # Save the updated dictionary to a JSON file
    with open(productFilePath, "w") as json_file:
        json.dump(userDataDictionary, json_file, indent=4)  # Write JSON with pretty formatting

    print(f"Data saved to {productFilePath}")
