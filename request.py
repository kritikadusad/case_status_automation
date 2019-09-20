from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import sys, os
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get("https://egov.uscis.gov/casestatus/landing.do")
assert "Case Status" in driver.title
elem = driver.find_element_by_name("appReceiptNum")
elem.clear()
elem.send_keys("EAC1990110956")
elem.send_keys(Keys.RETURN)
submit = driver.find_element_by_name("initCaseSearch").submit()
assert "Error." not in driver.page_source
form = driver.find_element_by_name("caseStatusForm")
case = form.text
case_processed = case.lstrip("x").split("\n")[1:3]
status = "".join(case_processed[0])
additional_details = "".join(case_processed[1])
to_send = "This is an automated message:" + "\n" + status + "\n" + additional_details
driver.close()

message = client.messages.create(body= to_send, from_= '+16072282950', to= '+16073798219')
