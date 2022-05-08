import json
import configparser
from collections import OrderedDict

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class JSScriptHandler:
    driver = None

    def __init__(self, driver):
        self.driver = driver
        pass

    def click_on_element_by_xpath(self, xpath):
        js_script_rendered = f'''
            document.evaluate(
                '{xpath}',
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            ).singleNodeValue.click();
        '''

        self.driver.execute_script(js_script_rendered)


class Crawler(JSScriptHandler):
    DEFAULT_AWAIT_TIMEOUT_SECONDS = 5
    MAX_AWAIT_TIMEOUT_SECONDS = 60

    driver = None

    def __init__(self, setup_driver=True):
        super().__init__(self.driver)

        if setup_driver:
            self.setup_driver()

    def setup_driver(self):
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

    def hover_element(self, element):
        ActionChains(self.driver).move_to_element(element).perform()


class ServiceCrawler(Crawler):
    def __init__(self, setup_driver=True):
        super().__init__(setup_driver)

    def extract_itau_data(self, agencia_value, conta_value, password_value):
        url = "https://www.itau.com.br/"
        self.go_to_page(url)

        self.sign_to_page(agencia_value, conta_value)
        self.submit_password(password_value)
        self.access_itau_account_data_information()
        data = self.extract_data_from_page()

        print(json.dumps(data, indent=2, sort_keys=True))

        self.wait_user_choice_to_quit()

    def sign_to_page(self, agencia_value, conta_value):
        agencia_page_element = self.driver.find_element(By.ID, "agencia")
        conta_page_element = self.driver.find_element(By.ID, "conta")
        login_page_element = self.driver.find_element(By.ID, "loginButton")

        agencia_page_element.send_keys(agencia_value)
        conta_page_element.send_keys(conta_value)
        login_page_element.click()

    def submit_password(self, password_value):
        WebDriverWait(self.driver, self.MAX_AWAIT_TIMEOUT_SECONDS).until(
            presence_of_all_elements_located((By.CLASS_NAME, "campoTeclado"))
        )

        password_tuple_keys = self.driver.find_elements(By.CLASS_NAME, "campoTeclado")

        for password_number in str(password_value):
            tuple_key = next(filter(lambda tuple_element: password_number in tuple_element.text, password_tuple_keys))
            tuple_key.click()

        self.driver.find_element(By.ID, "acessar").click()

    def access_itau_account_data_information(self):
        account_information_xpath = '//*[contains(text(),"saldo e extrato")]'

        WebDriverWait(self.driver, self.MAX_AWAIT_TIMEOUT_SECONDS).until(
            presence_of_all_elements_located((By.XPATH, account_information_xpath))
        )

        account_information_xpath = '//*[contains(text(),"saldo e extrato")]'

        self.click_on_element_by_xpath(account_information_xpath)

    def extract_data_from_page(self):
        data_position = dict(
            date=0,
            description=1,
            opt_value_1=2,
            opt_value_2=3
        )

        content_grid_id = 'corpoTabela-gridLancamentos-pessoa-fisica'
        content_row_class = 'linha-tabela-lancamentos-pf-sem-categoria'

        WebDriverWait(self.driver, self.MAX_AWAIT_TIMEOUT_SECONDS).until(
            presence_of_all_elements_located((By.ID, content_grid_id))
        )

        html = self.driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        grid = soup.find(id=content_grid_id)
        rows = grid.find_all(class_=content_row_class)

        data = []
        for row in rows:
            row_data = {}

            cells = row.find_all('td')
            value = str(cells[data_position["opt_value_1"]].text).strip() or str(cells[data_position["opt_value_2"]].text).strip()

            row_data["date"] = str(cells[data_position["date"]].text).strip()
            row_data["description"] = str(cells[data_position["description"]].text).strip()
            row_data["value"] = value

            data.append(row_data)

        return data


def get_credentials():
    config = configparser.ConfigParser()
    config.read('properties.ini')

    agencia_config_value = config['bank.credentials']['agencia']
    conta_config_value = config['bank.credentials']['conta']
    password_config_value = config['bank.credentials']['password']

    return agencia_config_value, conta_config_value, password_config_value


if __name__ == '__main__':
    agencia, conta, password = get_credentials()

    crawler_service = ServiceCrawler()

    crawler_service.extract_itau_data(agencia, conta, password)
