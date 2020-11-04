from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from DMarket import DMarketApi


class Targeter:

    def __init__(self):
        self.driver = webdriver.Chrome('D:\chromedriver/chromedriver.exe')
        self.wait = WebDriverWait(self.driver, 5)
        self.driver.get('https://dmarket.com/')
        self.api = DMarketApi()
        self.api.get_cookies()

    def login(self, login, password):
        WebDriverWait(self.driver, 10).until(lambda driver: self.driver.find_element_by_id('onesignal-popover-cancel-button')).click()
        self.driver.find_element_by_class_name('c-dialogHeader__close').click()
        self.driver.find_element_by_xpath('//mat-icon[text()="close"]').click()
        self.driver.find_element_by_xpath("//button[@class='c-cookieBanner__btn']").click()

        self.driver.find_elements_by_xpath("//button[text()='Log in']")[2].click()

        self.driver.find_element_by_xpath("//button[@class='c-authFooter__button o-dmButton o-dmButton--round o-dmButton--blue mat-ripple']").click()

        WebDriverWait(self.driver, 5).until(lambda driver: self.driver.find_element_by_id("mat-input-3")).send_keys(login)
        self.driver.find_element_by_id("mat-input-4").send_keys(password)
        self.driver.find_element_by_xpath("//div[@class='mat-checkbox-inner-container']").click()
        self.driver.find_element_by_xpath(
            "//button[@class='c-authFooter__button c-authFooter__button--fluid o-dmButton o-dmButton--blue mat-ripple']").click()

        sleep(4)
        try:
            self.driver.find_elements_by_xpath("//mat-icon[text()='close']")[1].click()
        except:
            pass

    def create_offer(self, line, buy_price):
        """
        :param line: линия из списка поиска по названию из начального окна создания таргетов
        :param buy_price: цена, по которой готовы купить
        :return:
        """
        line.click()
        # ожидаем загрузки окна
        # ставим 'any' trade_lock
        # self.wait.until(EC.presence_of_element_located((By.XPATH, "//mat-radio-button//div[@class='mat-radio-label-content'][text()='Any']"))).click()
        #вводим цену
        cents = str(buy_price % 100)
        if len(cents) == 1:
            cents = '0' + cents

        buy_price = str(buy_price//100) + '.' + cents
        print(f"Price in 'create_offer': {buy_price}")

        # sleep(0.5)
        enter_price = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='c-dialogPrice__item']//input")))
        # enter_price = self.driver.find_element_by_xpath("//div[@class='c-dialogPrice__item']//input")
        while enter_price.get_attribute("value") != buy_price:
            enter_price.clear()
            for c in buy_price:
                enter_price.send_keys(c)
                sleep(0.1)
            sleep(0.5)

        print("price was entered")
        #активируем target
        sleep(1)
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()=' Save and activate ']"))).click()

        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//p[@class="c-dialogStatus__text"]/span[text()=" Target was activated successfully. "]')))
        except:
            print("Target wasn't created due to some mistake")
            raise Exception

        #закрываем окно
        self.driver.find_element_by_xpath("//button[@class='c-dialogHeader__close ng-star-inserted']").click()

        #закрываем окно с подпиской, если оно появилось
        try:
            WebDriverWait(self.driver, 2).until(lambda driver: self.driver.find_element_by_xpath("//button[@class='c-dialogHeader__close c-dialogSubscription__close']")).click()
        except:
            pass


    def create_class_offers(self, item_class="AK-47", pos=0):
        """
        :param item_class: название класса скинов (например, "АК-47", "AWP")
        :return: создаёт таргеты на все скины из данного класса
        """
        # открытие меню создания таргетов
        self.driver.find_element_by_xpath('//dm-button[@data-analytics-id="targetsCreate_startButton"]').click()
        # ввод названия в строку поиска
        self.driver.find_element_by_xpath('//div[@class="c-targetsSearch"]//input').send_keys(item_class)

        active_offers = set()

        # pos = 127
        while(1):
            pos += 1

            #ждём загрузки списка названий
            names = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="c-targetsSearch"]//div[@class="c-targetsSearch__list ng-star-inserted"]//div[@class="c-targetsSearch__item ng-star-inserted"]/img')))

            # выход из цикла, если прошли по всем скинам из данного класса
            if len(names) <= pos:
                break

            # получаем название
            title = names[pos].get_attribute('alt')

            # если уже создавали такой оффер
            if(title in active_offers):
                continue

            #проверка на то, что скин из CS:GO
            if names[pos].get_attribute('src') != 'https://s3.amazonaws.com/dmarket-images-stage/a161879c-e633-4fdd-815d-e4347d528320.png':
                continue

            # на случай cooldown'а на запросы к api от сайта
            while(True):
                try:
                    opt_price = self.api.get_optimal_price(title=title)
                except:
                    sleep(1)
                else:
                    break

            print(f"Title: {title},\t is_popular: {opt_price['is_popular']},\t optimal_buy_price: {opt_price['price_to_buy']},\t pos: {pos}")

            # на случай cooldown'а на запросы к api от сайта
            while (True):
                try:
                    balance = self.api.get_balance()
                except:
                    sleep(1)
                else:
                    break

            # если не популярна или оптимальная стоимость больше суммы на балансе, пропускаем
            if not opt_price['is_popular'] or opt_price['price_to_buy'] > balance or opt_price['price_to_buy'] < 2:
                continue

            print(f"Trying to create an offer:\nTitle: {title}\nPotential selling price:c {opt_price['potential_sell_price']}\nGood price to buy: {opt_price['price_to_buy']}")
            try:
                self.create_offer(line=names[pos], buy_price=opt_price['price_to_buy'])
            except:
                print("Some error occured in 'create_offer' function")
            else:
                active_offers.add(title)
                with open("CreatedOffers.txt", "a") as file:
                    file.write(f"{title}, Buy_price = {opt_price['price_to_buy']}, Sell_price = {opt_price['potential_sell_price']}\n")

            # открытие меню создания таргетов
            self.driver.find_element_by_xpath('//dm-button[@data-analytics-id="targetsCreate_startButton"]').click()
            # ввод названия в строку поиска
            self.driver.find_element_by_xpath('//div[@class="c-targetsSearch"]//input').send_keys(item_class)
            pos -= 5

    def create_all_lists(self):
        names = ['AWP', 'M4A1-S', 'USP-S']
        for name in names:
            self.create_class_offers(item_class=name)
