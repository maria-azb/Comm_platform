import time
import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from base_page import BasePage
from locators import Locators

link = "http://0.0.0.0:5585"
valid_freq_values = [1, 2, 5, 10, 20, 50, 100, 200, 500]


def prepare_data():
    """
        Метод по очереди пытается перейти на страницу мониторинга для каждого устойства и сохраняет ссылку.
        Возвращает список ссылок.
    """

    driver = webdriver.Chrome()
    page = BasePage(driver, link)
    page.open()
    buttons = driver.find_elements_by_xpath(Locators.BUTTONS_MONITORING)
    monitoring_links = []
    for i in range(len(buttons)):
        driver.get(link)
        driver.find_element_by_xpath(f"//tr[{i + 1}]/td/button/span[contains(text(), 'Monitoring')]").click()
        if page.is_element_present(*Locators.HEADER_MONITORING):
            monitoring_links.append(driver.current_url)
    driver.quit()
    return monitoring_links


monitoring_links = prepare_data()


@pytest.fixture(scope="function")
def browser():
    browser = webdriver.Chrome()
    yield browser
    browser.quit()


class TestMonitoring:

    @pytest.mark.parametrize('mlink', monitoring_links)
    @pytest.mark.parametrize('pin', [2, 3])
    def test_pins_duty(self, browser, mlink, pin):
        """
            Проверяем наличие и корректность параметра duty для pin 2 и pin 3 для каждого устройства,
            на страницу мониторинга которого можно зайти с основной страницы.
            В качестве параметров передаём список ссылок для каждого устройства
            и номер пина (2 и 3).

            Параметр должен быть числом с указанием единицы измерения % (диапазон значений 0-100)
        """

        page = BasePage(browser, mlink)
        page.open()

        duty_xpath = f"//div[{pin}]//div[contains(@class, 'ant-card-body')]//div[1]/article"
        try:
            WebDriverWait(browser, 10).until(lambda wd: wd.find_element_by_xpath(duty_xpath).text != "%")
        except TimeoutException:
            raise TimeoutException(f'В течение 10 секунд для Pin {pin} значение duty(%) не появилось!')
        pin_duty = browser.find_element_by_xpath(duty_xpath)
        try:
            value = int(pin_duty.text[:-1])
        except ValueError:
            raise ValueError(f'Некорректное значение duty для Pin {pin}')
        assert value in range(0, 101), f'Значение duty ({value}) для Pin {pin} не лежит в диапазоне (0,100)%'

    @pytest.mark.parametrize('mlink', monitoring_links)
    @pytest.mark.parametrize('pin', [2, 3])
    def test_pins_freq(self, browser, mlink, pin):
        """
            Проверяем параметр frequency для pin 2 и pin 3 для каждого устройства,
            на страницу мониторинга которого можно зайти с основной страницы.
            В качестве параметров передаём список ссылок для каждого устройства
            и номер пина (2 и 3)
        """

        page = BasePage(browser, mlink)
        page.open()

        freq_xpath = f"//div[@class='ant-row']/div[{pin}]//div[@class='ant-row']/div[3]/article"
        try:
            WebDriverWait(browser, 10).until(lambda wd: wd.find_element_by_xpath(freq_xpath).text != "Hz")
        except TimeoutException:
            raise TimeoutException(f'В течение 10 секунд для Pin {pin} значение frequency(Hz) не появилось!')
        pin_freq = browser.find_element_by_xpath(freq_xpath)
        value = pin_freq.text[:-2]
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f'{pin_freq.text} - некорректное значение frequency для Pin {pin}. '
                             f'Допустимые значения: 1, 2, 5, 10, 20, 50, 100, 200, 500')
        assert value in valid_freq_values, f'{value} - некорректное значение frequency для Pin {pin}. ' \
                                           f'Допустимые значения: 1, 2, 5, 10, 20, 50, 100, 200, 500'

    @pytest.mark.parametrize(['value', 'positive'], [[100, True], [50, True], [0, True], [-1, False],
                                                     [101, False], ['2.5', False], ['aa', False], ['-', False]])
    @pytest.mark.parametrize('link', monitoring_links)
    def test_change_duty_pin2(self, browser, link, value, positive):
        """
            Проверяем возможность изменить duty для pin 2 для каждого устройства,
            на страницу мониторинга которого можно зайти с основной страницы.
            В качестве параметров передаём:
            1. список ссылок для каждого устройства
            2. список пар: значение duty + булевый параметр 'positive' (является ли это значение допустимым)
            Параметр duty должен измениться в случае, если значение находится в диапазоне (0; 100)
        """

        page = BasePage(browser, link)
        page.open()

        duty_field = browser.find_element_by_xpath(Locators.DUTY_FIELD_PIN_2)
        duty_value = duty_field.get_attribute("value")

        for i in range(len(duty_value)):
            duty_field.send_keys(Keys.BACK_SPACE)

        duty_field.send_keys(value)
        button = browser.find_element_by_xpath(Locators.SAVE_BTN_PIN_2)
        button.click()

        try:
            WebDriverWait(browser, 3).until(lambda wd: wd.find_element_by_xpath(Locators.DUTY_VALUE_PIN_2).text == str(value) + '%')
            success = True
        except TimeoutException:
            success = False

        assert success == positive, f'Pin 2: Неправильное поведение при значении duty={value}'


    @pytest.mark.parametrize(['value', 'positive'], [[100, True], [50, True], [0, True], [-1, False],
                                                     [101, False], ['2.5', False], ['aa', False], ['-', False]])
    @pytest.mark.parametrize('link', monitoring_links)
    def test_change_duty_pin3(self, browser, link, value, positive):
        """
            Проверяем возможность изменить duty для pin 3 для каждого устройства,
            на страницу мониторинга которого можно зайти с основной страницы.
            В качестве параметров передаём:
            1. список ссылок для каждого устройства
            2. список пар: значение duty + булевый параметр 'positive' (является ли это значение допустимым)
            Параметр duty должен измениться в случае, если значение находится в диапазоне (0; 100)
        """

        page = BasePage(browser, link)
        page.open()

        duty_field = browser.find_element_by_xpath(Locators.DUTY_FIELD_PIN_3)
        duty_value = duty_field.get_attribute("value")

        for i in range(len(duty_value)):
            duty_field.send_keys(Keys.BACK_SPACE)

        duty_field.send_keys(value)
        button = browser.find_element_by_xpath(Locators.SAVE_BTN_PIN_3)
        button.click()

        try:
            WebDriverWait(browser, 3).until(lambda wd: wd.find_element_by_xpath(Locators.DUTY_VALUE_PIN_3).text == str(value) + '%')
            success = True
        except TimeoutException:
            success = False

        assert success == positive, f'Pin 3: Неправильное поведение при значении duty={value}'

    @pytest.mark.parametrize('link', monitoring_links)
    @pytest.mark.parametrize('freq', [1, 2, 5, 10, 20, 50, 100, 200, 500])
    def test_change_freq_pin2(self, browser, link, freq):
        """
            Проверяем возможность изменить frequency для pin 2 для каждого устройства,
            на страницу мониторинга которого можно зайти с основной страницы.
            В качестве параметров передаём:
            1. список ссылок для каждого устройства
            2. список значений frequency, которые должны быть доступны для выбора в выпадающем списке.
        """

        page = BasePage(browser, link)
        page.open()

        try:
            WebDriverWait(browser, 3).until(lambda wd: wd.find_element_by_xpath(Locators.FREQ_VALUE_PIN_2).text != "Hz")
            current_freq = browser.find_element_by_xpath(Locators.FREQ_VALUE_PIN_2).text
            freq_field = browser.find_element_by_xpath(Locators.FREQ_FIELD_PIN_2)
            freq_field.click()
        except TimeoutException:
            raise TimeoutException(f'Отсутствует текущее значение частоты (freq, Hz).')

        try:
            ActionChains(browser).move_to_element(browser.find_element_by_xpath(f"//div[@label='{freq}']")).perform()
            freq_select = browser.find_elements_by_xpath(f"//div[@label='{freq}']")[0]
            freq_select.click()
        except TimeoutException:
            raise TimeoutException(f'Не получилось нажать на значение {freq}')

        button = browser.find_element_by_xpath(Locators.SAVE_BTN_PIN_2)
        button.click()

        if freq != current_freq:
            try:
                WebDriverWait(browser, 3).until(lambda wd: wd.find_element_by_xpath(Locators.FREQ_VALUE_PIN_2).text != current_freq)
            except TimeoutException:
                raise TimeoutException(f'В течение 3 секунд для Pin 2 значение frequency(Hz) не появилось!')
        else:
            time.sleep(1)    # по-хорошему это другой кейс, и надо это значение перепроверить еще раз, пока так

        pin_freq = browser.find_element_by_xpath(Locators.FREQ_VALUE_PIN_2).text
        value = pin_freq[:-2]  # отрезаем единицу измерения Hz
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f'{pin_freq.text} - некорректное значение frequency для Pin 2. '
                             f'Допустимые значения: 1, 2, 5, 10, 20, 50, 100, 200, 500')
        assert value == freq, f'Значение Freq должно быть равно {freq}, а не {value}., ' \
                              f'pin_freq = {pin_freq} current_freq = {current_freq} '


    @pytest.mark.parametrize('link', monitoring_links)
    @pytest.mark.parametrize('freq', [1, 2, 5, 10, 20, 50, 100, 200, 500])
    def test_change_freq_pin3(self, browser, link, freq):
        """
            Проверяем возможность изменить frequency для pin 3 для каждого устройства,
            на страницу мониторинга которого можно зайти с основной страницы.
            В качестве параметров передаём:
            1. список ссылок для каждого устройства
            2. список значений frequency, которые должны быть доступны для выбора в выпадающем списке.
        """

        page = BasePage(browser, link)
        page.open()

        try:
            WebDriverWait(browser, 3).until(lambda wd: wd.find_element_by_xpath(Locators.FREQ_VALUE_PIN_3).text != "Hz")
            current_freq = browser.find_element_by_xpath(Locators.FREQ_VALUE_PIN_3).text
            freq_field = browser.find_element_by_xpath(Locators.FREQ_FIELD_PIN_3)
            freq_field.click()
        except TimeoutException:
            raise TimeoutException(f'Отсутствует текущее значение частоты (freq, Hz).')

        try:
            ActionChains(browser).move_to_element(browser.find_element_by_xpath(f"//div[@label='{freq}']")).perform()
            freq_select = browser.find_element_by_xpath(f"//div[@label='{freq}']")
            freq_select.click()
        except TimeoutException:
            raise TimeoutException(f'Не получилось нажать на значение {freq}')

        button = browser.find_element_by_xpath(Locators.SAVE_BTN_PIN_3)
        button.click()

        if freq != current_freq:
            try:
                WebDriverWait(browser, 3).until(lambda wd: wd.find_element_by_xpath(Locators.FREQ_VALUE_PIN_2).text != current_freq)
            except TimeoutException:
                raise TimeoutException(f'В течение 3 секунд для Pin 2 значение frequency(Hz) не обновилось!')
        else:
            time.sleep(1)    # по-хорошему это другой кейс, и надо это значение перепроверить еще раз, пока так
        pin_freq = browser.find_element_by_xpath(Locators.FREQ_VALUE_PIN_2)
        value = pin_freq.text[:-2]  # отрезаем единицу измерения Hz
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f'{pin_freq.text} - некорректное значение frequency для Pin 2. '
                             f'Допустимые значения: 1, 2, 5, 10, 20, 50, 100, 200, 500')
        assert value == freq, f'Значение Freq должна быть равно {freq}, а не {value}'


