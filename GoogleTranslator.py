# Phawin Prongpaophan

# This program provide a naive way to get a translation from Google Translate,
# without a cost of using Google Translate API.
# Selenium and Chromedriver are used to get a translation.

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime as dt
from datetime import timedelta
import time

# Basic Constant Declaration

# You NEED to change CHROMEDRIVER_PATH, otherwise this program may not work for you
CHROMEDRIVER_PATH = "C:\\Users\\Phawin_p\\Documents\\chromedriver"
BASE_TRANSLATION_URL = "https://translate.google.com/#view=home&op=translate&sl=[SOURCE_LANGUAGE]&tl=[TARGET_LANGUAGE]"
GOOGLE_TRANSLATE_URL = "https://translate.google.com"


class SimpleTranslator:
    
    # Construct a translator
    def __init__(self, source_language = "auto", target_language = "th", debug = False):
        self.MY_URL = self.getURL(source_language, target_language)
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)
        self.driver.get(self.MY_URL)
        if debug:
            print("Chromedriver ready!")
        time.sleep(0.5)
        
    def __str__(self):
        return "Translation Machine with [%s]" % self.MY_URL
    
    # Return a string s (in source_language) in target_language
    # the length of a string cannot exceed 5000 (raise ValueError otherwise)
    # If it fail to get a translation, it will raise RuntimeError
    def translate(self, s, attempt = 3):
        if len(s) > 5000:
            raise ValueError('Your string is too long.')
        if self.driver.current_url == self.MY_URL:
            self.driver.get(self.MY_URL)
            time.sleep(0.5)
        #Send Key
        blank = False
        for i in range(attempt):
            try:
                ct = 0.05
                if i > 0:
                    ct = 1
                self.submitRequest(s)
                time.sleep(ct)
                self.checkForButton()
                time.sleep(ct)
                res = self.getOutput()
                time.sleep(0.05)
                if res == "":
                    self.driver.get(self.MY_URL)
                    time.sleep(0.5)
                    blank = True
                else:
                    return res
            except:
                self.driver.get(self.MY_URL)
                time.sleep(0.5)
        if blank:
            return ""
        raise RuntimeError('Failed to get it!')

    def __del__(self):
        self.driver.close()

    # Helper Methods
    def getURL(self,source_language = "auto", target_language = "en"):
        ret = BASE_TRANSLATION_URL.replace("[SOURCE_LANGUAGE]", source_language)
        ret = ret.replace("[TARGET_LANGUAGE]", target_language)
        return ret

    # Get a Translation
    def submitRequest(self,src):
        tb = self.driver.find_element_by_css_selector(".orig.tlid-source-text-input.goog-textarea")
        tb.clear()
        tb.send_keys(src)
        
    # In the case that your screen has a submit button, we will try to press it
    def checkForButton(self):
        try:
            submitButton = self.driver.find_element_by_css_selector(".go.jfk-button-action")
            submitButton.click()
            #print("Submit Pressed")
        except:
            #print("Failed to submit")
            return
        
    def getOutput(self):
        outputBox = self.driver.find_element_by_css_selector(".tlid-translation.translation")
        tb = outputBox.find_elements_by_tag_name("span")
        #print(len(tb))
        res = []
        for item in tb:
            res.append(item.text)
            #print("[%s]"%item.text)
        return " ".join(res).strip()

    
# General Helper Functions
def writeFile(fn, s):
    with open(fn, "w", encoding="utf-8") as f:
        f.write(s)
        
def readFile(fn):
    with open(fn, "r", encoding="utf-8") as f:
        return f.read()