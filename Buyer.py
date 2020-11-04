from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import browser_cookie3
import requests
import json
from pprint import pprint

class Buyer:

    def __init__(self):
        self.driver = webdriver.Chrome('D:\chromedriver/chromedriver.exe')
        self.driver.get('https://dmarket.com/')

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

    def refresh(self):
        """
        обновляет страницу маркета
        """
        self.driver.find_element_by_xpath("//filters[@class='c-exchange__filters']//button[@class='o-filter o-filter--refresh mat-ripple']").click()
        self.wait_for_refresh()

    def get_items(self, limit):
        """
        возвращает список офферов с текущей страницы в формате Webelements
        """
        return self.driver.find_elements_by_xpath("//market-inventory//asset-card[@data-analytics-id='list_marketInventory']")[:limit]

    def close_windows(self):
        """
        закрывает все появляющиеся окна
        """
        try:
            self.driver.find_element_by_xpath(
                "//button[@data-analytics-id='buy_closeByCross'][@type='button']").click()
        except:
            pass
        """
        while True:
            sleep(1)
            cl = self.driver.find_element_by_xpath("//button[@aria-label='Close']")
            if cl is None:
                break
            cl.click()
        """

    def buy_item(self, item):
        """
        :param item: webelement оффера
        :return: покупает его
        """
        try:
            item.find_element_by_xpath(".//button[@class='c-asset__action c-asset__action--info']").click()
            WebDriverWait(self.driver, 2).until(lambda driver: self.driver.find_element_by_xpath(
                '//dm-button[@data-analytics-id="buy_startButton_clickInfo"]')).click()
            WebDriverWait(self.driver, 2).until(lambda driver: self.driver.find_element_by_xpath(
                '//button[@data-analytics-id="buy_buyButton"]')).click()
            WebDriverWait(self.driver, 2).until(lambda driver: self.driver.find_element_by_xpath(
                "//button[@class='c-dialog__button o-dmButton o-dmButton--green mat-ripple ng-star-inserted']")).click()
        except:
            print("Looks like offer is already in deal")

        try:
            WebDriverWait(self.driver, 2).until(lambda driver: self.driver.find_element_by_xpath(
            "//button[@data-analytics-id='buy_closeByCross'][@type='button']")).click()
            WebDriverWait(self.driver, 2).until(lambda driver: self.driver.find_element_by_xpath(
            "//button[@class='c-dialogHeader__close c-dialogSubscription__close']")).click()
        except:
            pass

        self.close_windows()

    def wait_for_refresh(self):
        while self.is_refreshing():
            pass
        sleep(0.5)

    def set(self, apply_filter=False, price_from=None, price_to=None):
        """
        устанавливает стартовые настройки
        """
        if apply_filter:
            # фильтр на новые офферы:
            self.driver.find_element_by_xpath("//div[@class='o-select__sortTexts']").click()
            self.driver.find_element_by_xpath("//strong[contains(text(),'Date: Newest First')]").click()

        if price_from is not None:
            f = self.driver.find_element_by_xpath("//input[@formcontrolname='priceFrom']")
            f.clear()
            f.send_keys(f"{price_from//100}.{price_from%100}")

        if price_to is not None:
            f = self.driver.find_element_by_xpath("//input[@formcontrolname='priceTo']")
            f.clear()
            f.send_keys(f"{price_to//100}.{price_to%100}")

        self.wait_for_refresh()

    def is_refreshing(self):
        """
        :return: True, если список офферов ещё обновляется
        """
        return (self.driver.find_element_by_xpath("//market-inventory//assets-card-scroll").get_attribute('class') != "c-assetList")

    def reserve_item(self, item):
        """
        :return: возвращает True, если удалось зарезервировать item
        """
        try:
            item.find_element_by_xpath(".//button[@class='c-asset__action c-asset__action--info']").click()
            WebDriverWait(self.driver, 2).until(lambda driver: self.driver.find_element_by_xpath(
                '//dm-button[@data-analytics-id="buy_startButton_clickInfo"]')).click()
        except:
            print("Looks like order is already in deal")
            return False
        else:
            return True

    def clear_basket(self):
        while True:
            try:
                self.driver.find_element_by_xpath("//div[@class='c-asset__inner c-asset__inner--sm']//img[@class='c-asset__img']").click()
                sleep(0.3)
            except:
                break

    def dereserve_item(self):
        try:
            self.close_windows()
            #self.driver.find_element_by_xpath(
            #    "//button[@class='c-dialogHeader__close ng-star-inserted']//mat-icon[@class='mat-icon notranslate material-icons mat-icon-no-color'][contains(text(),'close')]").click()
            self.clear_basket()
            #item.click()
        except:
            print("Error occured when tried to dereserve the item")
        #self.driver.find_element_by_xpath("//div[@class='c-exchangeSum ng-star-inserted c-exchangeSum--market']//button[@class='mat-fab mat-accent']").click()
        #self.driver.find_element_by_xpath("//div[@class='c-asset__inner c-asset__inner--sm']//img[@class='c-asset__img']").click()

    def buy_reserved_item(self):
        try:
            WebDriverWait(self.driver, 2).until(lambda driver: self.driver.find_element_by_xpath(
                '//button[@data-analytics-id="buy_buyButton"]')).click()
            WebDriverWait(self.driver, 2).until(lambda driver: self.driver.find_element_by_xpath(
                "//button[@class='c-dialog__button o-dmButton o-dmButton--green mat-ripple ng-star-inserted']")).click()
        except:
            print("Couldn't buy the reserved item")
