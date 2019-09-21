from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import sys, os
from twilio.rest import Client

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
URL = "https://egov.uscis.gov/casestatus/landing.do"


class Form:
    def __init__(self, form):
        self.content = form.text.lstrip("x").split("\n")[1:3]

    def status(self):
        return "".join(self.content[0])

    def additional_info(self):
        return "".join(self.content[1])


def invisible_driver(URL):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    assert "Case Status" in driver.title
    return driver


def submit_form(driver, receipt_num):
    elem = driver.find_element_by_name("appReceiptNum")
    elem.clear()
    elem.send_keys(receipt_num)
    elem.send_keys(Keys.RETURN)
    submit = driver.find_element_by_name("initCaseSearch").submit()
    assert "Error." not in driver.page_source


def check_case_status(URL, receipt_num):
    driver = invisible_driver(URL)
    submit_form(driver, receipt_num)
    form = Form(driver.find_element_by_name("caseStatusForm"))
    case_status = form.status() + "\n" + form.additional_info()
    driver.close()
    return case_status


def send_sms(case_status):
    sender = os.environ["SENDER"]
    receivers = os.environ["RECEIVERS"]
    client = Client(account_sid, auth_token)
    message_body = "Your USCIS case status is as follows" + "\n" + case_status
    for receiver in receivers:
        message = client.messages.create(
            body=message_body, from_=sender, to=receiver
        )


case_status = check_case_status(URL, os.environ["RECEIPT_NUM"])
send_sms(case_status)
