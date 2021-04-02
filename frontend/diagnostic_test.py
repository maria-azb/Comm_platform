import pytest
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from base_page import BasePage
from locators import Locators

link = "http://0.0.0.0:5585"
reports = [100, 200, 300, 400]

@pytest.fixture(scope="class")
def browser():
    browser = webdriver.Chrome()
    yield browser
    browser.quit()

class TestDiagnostic():

    @pytest.mark.parametrize('report', reports)
    def test_open_report(self, browser, report):
        """
            По очереди переходим на страницу диагностики для каждого устойства.
            В выпадающем окне выбираем отчет и загружаем. Проверяем, что появился какой-то текст.
            Формат отчета за отсутствием требований пока не проверяем.

            Повторяем тест для всех видов отчета (100, 200, 300, 400), согласно требованиям.

            В качестве улучшения, я бы разделила тесты для разных устройств.
        """

        report_select_xpath = f"//div[@label='{report}']"

        page = BasePage(browser, link)
        page.open()

        buttons = browser.find_elements_by_xpath(Locators.BUTTONS_DIAGNOSTIC)

        for i in range(len(buttons)):
            page.open()
            browser.find_element_by_xpath(f"//tr[{i+1}]/td/button/span[contains(text(), 'Diagnostics')]").click()

            select = browser.find_element_by_xpath(Locators.SELECT_REPORT_FIELD)
            select.click()

            try:
                WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, report_select_xpath)))
                report_select = browser.find_element_by_xpath(report_select_xpath)
                report_select.click()
            except TimeoutException:
                raise TimeoutException(f'Отсутствует возможность выбора отчета {report}')

            assert len(browser.find_element_by_xpath(Locators.REPORT).text) == 0, \
                "На странице присутствует текст до нажатия кнопки 'Load report'"
            button = browser.find_element_by_xpath(Locators.LOAD_REPORT_BUTTON)
            button.click()

            try:
                WebDriverWait(browser, 5).until(lambda wd: len(wd.find_element_by_xpath(Locators.REPORT).text) > 0)
            except TimeoutException:
                raise TimeoutException(f'В течение 5 секунд отчет {report} не отобразился')

