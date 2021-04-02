from selenium.webdriver.common.by import By


class Locators:

    DEVICE_TABLE = (By.CSS_SELECTOR, ".ant-table")
    AT_LEAST_ONE_DEVICE_IN_TABLE = (By.CSS_SELECTOR, ".ant-table-row")
    TABLE_ROWS="//tr[contains(@class, 'ant-table-row')]"
    DEVICE_NAME="//tr/td[contains(@class, 'ant-table-cell')][1]"
    DEVICE_TYPE="//tr/td[contains(@class, 'ant-table-cell')][2]"
    DEVICE_ADDRESS="//tr/td/article[contains(@class, 'ant-typography')]"
    BUTTONS_MONITORING = "//button/span[contains(text(), 'Monitoring')]"
    BUTTONS_DIAGNOSTIC = "//button/span[contains(text(), 'Diagnostics')]"
    HEADER_MONITORING = (By.XPATH, "//h2[contains(text(), 'Monitoring')]")
    HEADER_DIAGNOCTIC = (By.XPATH, "//h2[contains(text(), 'Diagnostics')]")

    SAVE_BTN_PIN_2 = "//div[@class='ant-row']/div[2]/div[@class='ant-card']//button"
    SAVE_BTN_PIN_3 = "//div[@class='ant-row']/div[3]/div[@class='ant-card']//button"
    DUTY_FIELD_PIN_2 = "//div[@class='ant-row']/div[2]/div[@class='ant-card']//input[@type='text']"
    DUTY_FIELD_PIN_3 = "//div[@class='ant-row']/div[3]/div[@class='ant-card']//input[@type='text']"
    DUTY_VALUE_PIN_2 = "//div[2]//div[contains(@class, 'ant-card-body')]//div[1]/article"
    DUTY_VALUE_PIN_3 = "//div[3]//div[contains(@class, 'ant-card-body')]//div[1]/article"
    FREQ_FIELD_PIN_2 = "//div[@class='ant-row']/div[2]//div[@class='ant-select-selector']"
    FREQ_FIELD_PIN_3 = "//div[@class='ant-row']/div[3]//div[@class='ant-select-selector']"
    FREQ_VALUE_PIN_2 = "//div[@class='ant-row']/div[2]//div[@class='ant-row']/div[3]/article"
    FREQ_VALUE_PIN_3 = "//div[@class='ant-row']/div[2]//div[@class='ant-row']/div[3]/article"

    SELECT_REPORT_FIELD = "//input"
    LOAD_REPORT_BUTTON = "//button"
    REPORT = "//div[@class='ant-typography']/pre"
