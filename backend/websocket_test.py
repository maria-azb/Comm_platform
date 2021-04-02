import requests
import asyncio
import websockets

url = "http://0.0.0.0:5585"
all_devices = ['Engine', 'Power', 'Transmission', 'Brake', 'Control']


def get_devices_addresses():
    """
        По GET запросу получает адреса доступных устройств.
        Возвращает в виде списка.
    """
    response = requests.get(url + '/devices').json()
    addresses = []
    for r in response:
        addresses.append(r['address'])
    return addresses


device_addresses = get_devices_addresses()


async def get_pwm_params():
    for address in device_addresses:

        url = f"ws://0.0.0.0:5585/start_monitoring/{address}"

        async with websockets.connect(url) as ws:

            if ws.open is True:
                try:
                    data = await ws.recv()
                    print(f"Информация от сервера об устройстве {address}: {data}")
                except Exception as ex:
                    print(f"При получени информации об устройстве {address} произошла ошибка: {ex.args}")
            else:
                print(f"Соединение не установлено. url: {url}")

asyncio.get_event_loop().run_until_complete(get_pwm_params())
#   При чтении данных об устройствах, адрес которых содержит только цифры, мы получаем ответ "Not found"
#   Если адрес устройства содержит буквы, то происходит неизвестная ошибка.
#   Вероятно, здесь где-то здесь закрался баг:)
