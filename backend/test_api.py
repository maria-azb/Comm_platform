import requests
import pytest

api_url = "http://0.0.0.0:5585"
all_devices = ['Engine', 'Power', 'Transmission', 'Brake', 'Control']
valid_freqs = [1, 2, 5, 10, 20, 50, 100, 200, 500]


def get_devices_names():
    """
        По GET запросу получает имена доступных устройств.
        Возвращает в виде списка.
    """
    response = requests.get(api_url + '/devices').json()
    devices = []
    for device in response:
        devices.append(device['name'])
    return devices

def get_devices_addresses():
    """
        По GET запросу получает имена и адреса доступных устройств.
        Возвращает в виде словаря.
    """
    response = requests.get(api_url + '/devices').json()
    addresses = {}
    for device in response:
        addresses[device['name']] = device['address']
    return addresses


def test_devices_names():
    """
        По GET запросу получаем имена доступных устройств.
        Сравниваем список с ожидаемым.

        Дополнение: В данном тесте в качестве ожидаемого списка использую полученный по API.
        В реальности это должен быть список заведомо подключенных устройств.
    """

    response = requests.get(api_url + '/devices')
    assert response.status_code == 200, "Ресурс '/devices' недоступен"

    devices = get_devices_names()

    missing_devices = []
    for device in all_devices:
        if device not in devices:
            missing_devices.append(device)
    assert len(missing_devices) == 0, f'Нет данных об устройствах: {missing_devices}'

    if len(devices) > len(all_devices):
        unique_devices = set()
        for device in devices:
            unique_devices.add(device)
        if len(devices) > len(unique_devices):
            raise AssertionError('В списке устройств, полученных по API, есть повторяющиеся имена устройств')
        else:
            extra = []
            for device in devices:
                if device not in all_devices:
                    extra.append(device)
            raise AssertionError(f'В списке устройств, полученных по API, есть лишние устройства: {extra}')


@pytest.mark.parametrize('device', all_devices)
@pytest.mark.parametrize(['duty', 'positive'], [[100, True], [50, True], [0, True], [-1, False],
                                                [101, False], [2.5, False], ['aa', False], ['-', False]])
def test_changing_duty_pin_2(device, duty, positive):
    """
        Проверяем возможность изменить duty для pin 2 каждого устройства.

        В качестве параметров передаём:
        1. список имен устройств
        2. список пар: значение duty + булевый параметр 'positive' (является ли это значение допустимым)

        Параметр duty должен измениться в случае, если значение является целым числом в диапазоне (0; 100).
        Значение freq сохраняется предыдущее.
    """
    response = requests.get(api_url + '/devices').json()
    for row in response:
        if row['name'] == device:
            previous_duty = row['pin_1_pwm_d']
            previous_freq = row['pin_1_pwm_f']
    device_addresses = get_devices_addresses()

    patch = requests.patch(api_url + f"/devices?address={device_addresses[device]}&duty1={duty}&freq1={previous_freq})")
    assert patch.status_code == 200
    response = requests.get(api_url + '/devices').json()
    for row in response:
        if row['name'] == device:
            if positive:
                assert row['pin_1_pwm_d'] == duty, f"Предыдущее значение: {previous_duty}, " \
                                                   f"внесённое: {duty} (ПРАВИЛЬНОЕ), текущее : {row['pin_1_pwm_d']}"
            else:
                assert row['pin_1_pwm_d'] == previous_duty, f"Предыдущее значение: {previous_duty} (ПРАВИЛЬНОЕ), " \
                                                            f"внесённое: {duty}, текущее : {row['pin_1_pwm_d']}"


@pytest.mark.parametrize('device', all_devices)
@pytest.mark.parametrize(['duty', 'positive'], [[100, True], [50, True], [0, True], [-1, False],
                                               [101, False], [2.5, False], ['aa', False], ['-', False]])
def test_changing_duty_pin_3(device, duty, positive):
    """
        Проверяем возможность изменить duty для pin 3 каждого устройства.

        В качестве параметров передаём:
        1. список имен устройств
        2. список пар: значение duty + булевый параметр 'positive' (является ли это значение допустимым)

        Параметр duty должен измениться в случае, если значение является целым числом в диапазоне (0; 100).
        Значение freq сохраняется предыдущее.
    """
    response = requests.get(api_url + '/devices').json()
    for row in response:
        if row['name'] == device:
            previous_duty = row['pin_2_pwm_d']
            previous_freq = row['pin_2_pwm_f']
    device_addresses = get_devices_addresses()

    patch = requests.patch(api_url + f"/devices?address={device_addresses[device]}&duty2={duty}&freq2={previous_freq})")
    assert patch.status_code == 200
    response = requests.get(api_url + '/devices').json()
    for row in response:
        if row['name'] == device:
            if positive:
                assert row['pin_2_pwm_d'] == duty, f"Предыдущее значение: {previous_duty}, " \
                                                   f"внесённое: {duty} (ПРАВИЛЬНОЕ), текущее : {row['pin_2_pwm_d']}"
            else:
                assert row['pin_2_pwm_d'] == previous_duty, f"Предыдущее значение: {previous_duty} (ПРАВИЛЬНОЕ), " \
                                                            f"внесённое: {duty}, текущее : {row['pin_2_pwm_d']}"


@pytest.mark.parametrize('device', all_devices)
@pytest.mark.parametrize('freq', [1, 2, 5, 10, 20, 50, 100, 200, 500, 0, 'a', '-1', '2.5', '-'])
def test_changing_freq_pin_2(device, freq):
    """
        Проверяем возможность изменить freq для pin 2 каждого устройства.

        В качестве параметров передаём:
        1. список имен устройств
        2. список значений freq

        Параметр freq должен измениться в случае, если значение входит в список разрешенных значений
        valid_freqs = [1, 2, 5, 10, 20, 50, 100, 200, 500]
        Значение duty сохраняется предыдущее.
    """

    response = requests.get(api_url + '/devices').json()
    for row in response:
        if row['name'] == device:
            previous_freq = row['pin_1_pwm_f']
            previous_duty = row['pin_1_pwm_d']

    device_addresses = get_devices_addresses()

    patch = requests.patch(api_url + f"/devices?address={device_addresses[device]}&duty1={previous_duty}&freq1={freq}")
    assert patch.status_code == 200
    response1 = requests.get(api_url + '/devices').json()
    for row in response1:
        if row['name'] == device:
            if freq in valid_freqs:
                assert row['pin_1_pwm_f'] == freq, f"Предыдущее значение: {previous_freq}, " \
                                                   f"внесённое: {freq} (ПРАВИЛЬНОЕ), текущее : {row['pin_1_pwm_f']}"
            else:
                assert row['pin_1_pwm_f'] == previous_freq, f"Предыдущее значение: {previous_freq} (ПРАВИЛЬНОЕ), " \
                                                            f"внесённое: {freq}, текущее : {row['pin_1_pwm_f']}"


@pytest.mark.parametrize('device', all_devices)
@pytest.mark.parametrize('freq', [1, 2, 5, 10, 20, 50, 100, 200, 500, 0, 3, 300, 5000, 'a', '-1', '2.5', '-'])
def test_changing_freq_pin_3(device, freq):
    """
        Проверяем возможность изменить freq для pin 3 каждого устройства.

        В качестве параметров передаём:
        1. список имен устройств
        2. список значений freq

        Параметр freq должен измениться в случае, если значение входит в список разрешенных значений
        valid_freqs = [1, 2, 5, 10, 20, 50, 100, 200, 500]
        Значение duty сохраняется предыдущее.
    """
    response = requests.get(api_url + '/devices').json()
    for row in response:
        if row['name'] == device:
            previous_freq = row['pin_2_pwm_f']
            previous_duty = row['pin_2_pwm_d']
    device_addresses = get_devices_addresses()

    patch = requests.patch(api_url + f"/devices?address={device_addresses[device]}&duty2={previous_duty}&freq2={freq}")
    assert patch.status_code == 200
    response1 = requests.get(api_url + '/devices').json()
    for row in response1:
        if row['name'] == device:
            if freq in valid_freqs:
                assert row['pin_2_pwm_f'] == freq, f"Предыдущее значение: {previous_freq}, " \
                                                   f"внесённое: {freq} (ПРАВИЛЬНОЕ), текущее : {row['pin_2_pwm_f']}"
            else:
                assert row['pin_2_pwm_f'] == previous_freq, f"Предыдущее значение: {previous_freq} (ПРАВИЛЬНОЕ), " \
                                                            f"внесённое: {freq}, текущее : {row['pin_2_pwm_f']}"


@pytest.mark.parametrize('device', all_devices)
@pytest.mark.parametrize(['report', 'code'], [[100, 200], [200, 200], [300, 200], [400, 200],
                                              [500, 404], [600, 404], [0, 404], [1, 404]])
def test_reports(device, report, code):
    """
        Проверяем доступность отчетов (100, 200, 300, 400) - код ответа 200
        Для недоступных отчетов ожидаемый код ответа - 404
        Повторяем для всех устройств.
    """
    device_addresses = get_devices_addresses()
    response = requests.get(api_url + f'/report?address={device_addresses[device]}&repId={report}')
    assert response.status_code == code, f'Отчет {report}, ожидаемый код ответа {code}, ' \
                                         f'фактический {response.status_code}'


@pytest.mark.parametrize('device', all_devices)
@pytest.mark.parametrize('report', ['-100', '-200', 'abc', '1.5'])
def test_reports_invalid_id(device, report):
    """
        Проверяем ответ сервера при запроса отчета с невалидным Id.
        Повторяем для всех устройств.
    """
    device_addresses = get_devices_addresses()
    response = requests.get(api_url + f'/report?address={device_addresses[device]}&repId={report}')
    assert response.text == "Invalid type of 'repId' value"


