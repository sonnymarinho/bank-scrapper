import argparse
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class Crawler(object):
    DEFAULT_AWAIT_TIMEOUT_SECONDS = 5

    driver = None

    def __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()

    def wait_user_choice_to_quit(self):
        user_choice = input('Please click ENTER button to close application')
        if not user_choice:
            print("ABORTED")
            self.driver.quit()

    def go_to_page(self, url):
        self.driver.get(url)


class ServiceCrawler(Crawler):
    def __init__(self):
        super().__init__()

    def extract_itau_data(self, agencia_value, conta_value, password_value):
        url = "https://www.itau.com.br/"
        self.go_to_page(url)

        self.sign_to_page(agencia_value, conta_value)
        self.submit_password(password_value)

        self.wait_user_choice_to_quit()

    def sign_to_page(self, agencia_value, conta_value):
        agencia = self.driver.find_element(By.ID, "agencia")
        conta = self.driver.find_element(By.ID, "conta")
        login = self.driver.find_element(By.ID, "loginButton")

        agencia.send_keys(agencia_value)
        conta.send_keys(conta_value)
        login.click()

    def submit_password(self, password_value):
        pass


def get_credentials():
    config = configparser.ConfigParser()

    agencia = config["bank.credentials"]["agencia"]
    conta = config["bank.credentials"]["conta"]
    password = config["bank.credentials"]["password"]

    return agencia, conta, password


if __name__ == '__main__':
    agencia, conta, password = get_credentials()

    crawler_service = ServiceCrawler()

    crawler_service.extract_itau_data(agencia, conta, password)
