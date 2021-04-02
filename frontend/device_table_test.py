import pytest
import requests
from selenium import webdriver
from base_page import BasePage
from locators import Locators

link = "http://0.0.0.0:5585"


@pytest.fixture(scope="class")
def browser():
    browser = webdriver.Chrome()
    yield browser
    browser.quit()


@pytest.fixture(scope="class")
def available_devices():
    return requests.get(link + '/devices').json()


class TestDeviceTable:

    def test_devices_list_exists(self, browser):
        """
            Проверяем, что таблица существует, и в ней есть хоть одна строка.

            Дополнение: В реальности я бы создала условия, при которых я точно знаю,
            сколько устройств должно быть доступно, и сравнила бы с этим количеством.
        """
        page = BasePage(browser, link)
        page.open()
        assert page.is_element_present(*Locators.DEVICE_TABLE)
        assert page.is_element_present(*Locators.AT_LEAST_ONE_DEVICE_IN_TABLE)

    def test_device_is_displayed(self, browser, available_devices):
        """
            По GET запросу получаем имена доступных устройств.
            Сравниваем список устройств из таблицы с полученным по API.

            Дополнение: В данном тесте полученный по API список считаем верным.
            В реальности это должен быть список заведомо подключенных устройств.
        """

        page = BasePage(browser, link)
        page.open()
        assert page.is_element_present(*Locators.DEVICE_TABLE)
        devices = browser.find_elements_by_xpath(Locators.DEVICE_NAME)
        devices_names = []
        missing_names = []
        for device in devices:
            devices_names.append(device.text)
        for ad in available_devices:
            if ad['name'] not in devices_names:
                missing_names.append(ad['name'])
        assert len(missing_names) == 0, f'В таблице не отображены доступные устройства {missing_names}'

        if len(devices_names) > len(available_devices):
            unique_devices = set()
            for device in devices_names:
                unique_devices.add(device)
            if len(devices) > len(unique_devices):
                raise AssertionError('В таблице есть повторяющиеся имена устройств')

    def test_device_has_right_name(self, browser, available_devices):
        """
            Проверяем, что во всех строках в поле Name - имя из списка доступных устройств.
            Если хотя бы в одной строке неизвестное имя, либо имя отсутствует,
            выбрасываем ошибку с указанием таких строк.

            Дополнение: В реальности можно было бы сравнивать значения с заранее известным списком устройств.
        """

        page = BasePage(browser, link)
        page.open()
        assert page.is_element_present(*Locators.DEVICE_TABLE)
        devices_names = browser.find_elements_by_xpath(Locators.DEVICE_NAME)

        right_list = []
        for r in available_devices:
            right_list.append(r['name'])

        wrong_list = []
        i = 1
        for dname in devices_names:
            name = dname.text
            if name not in right_list:
                wrong_list.append(i)
            i += 1

        if len(wrong_list) > 0:
            raise AssertionError(f"Неизвестное имя (либо имя отсутствует) в строках: {wrong_list}")

    def test_device_has_right_type(self, browser, available_devices):
        """
            Проверяем, что во всех строках имени устройства соответствует правильный тип,
            основываясь на данных, полученных по API.
            Если хотя бы в одной строке тип неверный, выбрасываем ошибку с указанием всех устройств с неправильным типом

            Дополнение: В реальности можно было бы сравнивать значения с заранее известным списком типов
            и соответствие типа имени устройства.
        """

        page = BasePage(browser, link)
        page.open()
        assert page.is_element_present(*Locators.DEVICE_TABLE)
        devices_types = browser.find_elements_by_xpath(Locators.DEVICE_TYPE)
        devices_names = browser.find_elements_by_xpath(Locators.DEVICE_NAME)

        right_list = {}
        for r in available_devices:
            right_list[r['name']] = r['type']

        wrong_list = []
        i = 0
        for dname in devices_names:
            name = dname.text
            if right_list[name] != devices_types[i].text:
                wrong_list.append(name)
            i += 1

        if len(wrong_list) > 0:
            raise AssertionError(f"Неверно указан тип для устройств: {wrong_list}")

    def test_device_has_right_address(self, browser, available_devices):
        """
            Проверяем, что во всех строках имени устройства соответствует правильный адрес,
            основываясь на данных, полученных по API.
            Если хотя бы в одной строке адрес неверный (сравниваем в 10-м представлении),
            то выбрасываем ошибку с указанием всех устройств с неправильным адресом.

            Дополнение: В реальности можно было бы сравнивать значения с заранее известным списком устройств
            и соответствие адреса имени устройства.
        """

        def convert_16_to_10(num: str) -> int:
            """
                Принимает на вход 16-ое число,
                Возвращает 10-й эквивалент
            """
            return int(num, 16)

        page = BasePage(browser, link)
        page.open()
        assert page.is_element_present(*Locators.DEVICE_TABLE)
        devices_addresses = browser.find_elements_by_xpath(Locators.DEVICE_ADDRESS)
        devices_names = browser.find_elements_by_xpath(Locators.DEVICE_NAME)

        right_list = {}
        for r in available_devices:
            addr_10 = convert_16_to_10(r['address'])    # перевести в 10ную систему
            right_list[r['name']] = addr_10

        wrong_list = []
        i = 0
        for dname in devices_names:
            name = dname.text
            if int(right_list[name]) != int(devices_addresses[i].text):
                wrong_list.append(f"Устройство {name}: указан неверный адрес {devices_addresses[i].text}, "
                                  f"верный - {right_list[name]}.")
            i += 1

        if len(wrong_list) > 0:
            raise AssertionError(f"{wrong_list}")

    def test_monitoring_button_leads_to_Monitoring_Engine(self, browser):
        """
            Проверяем наличие кнопки "Monitoring" для каждого устройства и, что
            при нажатии на кнопку мы переходим на страицу Мониторинга.
            Проверяем сразу ВСЕ кнопки, если хоть одна не переводит на страницу Мониторинга,
            выводим ошибку с номерами строк с неработающими кнопками
        """
        page = BasePage(browser, link)
        page.open()

        devices = browser.find_elements_by_xpath(Locators.TABLE_ROWS)
        buttons = browser.find_elements_by_xpath(Locators.BUTTONS_MONITORING)
        assert len(devices) == len(buttons), "Кнопка 'Monitoring' отображается не для всех устройств"

        disabled_buttons = []

        for i in range(len(buttons)):
            page.open()
            browser.find_element_by_xpath(f"//tr[{i+1}]/td/button/span[contains(text(), 'Monitoring')]").click()
            if not page.is_element_present(*Locators.HEADER_MONITORING):
                disabled_buttons.append(i+1)
        if len(disabled_buttons) > 0:
            raise AssertionError(f"Кнопки 'Monitoring' в строках: {disabled_buttons} НЕ ведут на страницу Мониторинга")

    def test_monitoring_button_leads_to_Diagnostics_Engine(self, browser):
        """
            Проверяем, что при нажатии на кнопку "Diagnostics" мы переходим на страницу с отчетами.
            Проверяем сразу ВСЕ кнопки, если хоть одна не переводит на страницу с отчетами,
            выводим ошибку с номерами строк с неработающими кнопками
        """
        page = BasePage(browser, link)
        page.open()

        devices = browser.find_elements_by_xpath(Locators.TABLE_ROWS)
        buttons = browser.find_elements_by_xpath(Locators.BUTTONS_DIAGNOSTIC)
        assert len(devices) == len(buttons), "Кнопка 'Diagnostics' отображается не для всех устройств"

        disabled_buttons = []

        for i in range(len(buttons)):
            page.open()
            browser.find_element_by_xpath(f"//tr[{i+1}]/td/button/span[contains(text(), 'Diagnostics')]").click()
            if not page.is_element_present(*Locators.HEADER_DIAGNOCTIC):
                disabled_buttons.append(i+1)
        if len(disabled_buttons) > 0:
            raise AssertionError(f"Кнопки 'Diagnostics' в строках: {disabled_buttons} НЕ ведут на страницу с отчетами")
