

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import uuid
import json
from tqdm import tqdm
import os


'''
This is a BBC recipe site scraper module for the unittest module.
Some methods have been ammended to be standalone from other methods 
for testing purposes.
'''


class BBCRecipeScraper:
    
    def __init__(self, chrome_options, url: str = 'https://www.bbc.co.uk/food/recipes/a-z/a/1#featured-content'):
        '''
        Initialises desired URL
        
        This identifies the URL as the BBC recipe site and uses Chrome webdriver 
        to open it.
        '''
        #scraper init
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(url)
        self.WebDriverWait = WebDriverWait
        self.EC = EC
        time.sleep(3)
        
        print('Opening www.bbc.co.uk/food/recipes in background.')
        
        
    def accept_cookies(self):
        '''
        Accepts Cookies
        
        This clicks 'accept' on cookies pop-up if it appears, if it does not appear then
        nothing happens.
        '''
        try:
            self.driver.find_element(
                By.XPATH, '//*[@id="bbccookies-continue-button"]').click()
        except:
            pass
        
        print('Cookies acccepted.')
        
        
    def get_categories(self):
        '''
        Obtains links for each alphabet recipe category via the recipe sites main page
        
        Parameters
        ----------
        driver: webdriver.Chrome
            The driver that contains information about the current page
        
        Returns
        -------
        category_links: list
            A list with all the links for category
        '''
        #find len of web element containing category links
        rows = len(self.driver.find_elements(By.XPATH, '//*[@class="az-keyboard__list"]/li'))
        beforeXPath = '//*[@class="az-keyboard gel-wrap"]/div/ul/li['
        afterXPath = ']/a'
        self.category_links = []
        
        for t_rows in range(1, (rows + 1)):
            finalXPath = beforeXPath + str(t_rows) + afterXPath
            # the letter x category link does not exist
            try:
                letter_list = self.driver.find_element(By.XPATH, finalXPath)
                link = letter_list.get_attribute('href')
                self.category_links.append(link)
            except:
                pass
            
        print(f'{len(self.category_links)} recipe category links obtained.')
        
        return self.category_links
    
    
    def get_links(self):
        '''
        Obtains all the links on the current page and concatinates into list
        
        Returns
        -------
        recipe_links: list
            A list with all the links in the page
        '''
        recipe_container = self.driver.find_element(
            By.XPATH, '//*[@class="gel-wrap promo-collection__container az-page"]/div')
        recipe_list = recipe_container.find_elements(By.XPATH, './div')
        self.recipe_links = []
        
        for recipe in recipe_list:
            a_tag = recipe.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            self.recipe_links.append(link)
        
        return self.recipe_links
    
    
    def next_page(self):
        '''
        Obtains all links from all categories until 1000 URLs collected.        
        
        This method obtains the total page number per recipe category and clicks next 
        page for self.get_links method and appends all URLs to total_recipe_list. When 
        over 1000 URLs have been collected inside total_recipe_list the loop breaks.
        
        Returns
        -------
        total_links_list: list
            An extended recipe_links list with all links from all pages
        '''
        
        try:
            number_of_pages = int(self.driver.find_element(
                    By.XPATH, "//span[@aria-label='Next']/preceding::a[1]").text)
        except:
            pass
        
        if number_of_pages > 0:
            
            for page in range(number_of_pages - 1):
                
                next_button = self.driver.find_element(By.XPATH, "//span[@aria-label='Next']")
                self.driver.execute_script("arguments[0].click();", next_button)
                #wait for page to load
                time.sleep(3)
    
    
    
    def get_ingredients(self):
        '''
        Obtains ingredient list for each recipe, which is then appended to the 
        dict_recipe in get_details method
        
        Returns
        -------
        ingredient_list: list
            A list containing the ingredients from each link in total_links_list
        '''       
        ingredient_list = []
        container = self.driver.find_element(
            By.XPATH, '//div[@class="recipe-ingredients-wrapper"]')
        container_list = container.find_elements(By.XPATH, './ul')
        
        for element in container_list:
            
            rows = len(element.find_elements(By.XPATH, './li'))
            beforeXPath =  './li['
            afterXPath = ']/a'
            
            for t_rows in range(1, (rows + 1)):
                finalXPath = beforeXPath + str(t_rows) + afterXPath
                try:
                    ingredient = element.find_element(By.XPATH, finalXPath).text.upper()
                    ingredient_list.append(ingredient)
                except:
                    pass
                
        #remove duplicates
        ingredient_list = list(dict.fromkeys(ingredient_list))
        return ingredient_list
    
    
    def get_details(self):
        '''        
        Extracts data points from a URL, adds an UUID(v4) and stores inside dictionary.
        
        From the recipe webpage, the method extracts the name, decription, ingredients,
        cook time and image_url. A SKU is generated from the name, to be used as a unique
        user friendly identifier.
        
        Returns
        -------
        dict_recipe: dictionary
            An dictionary containing all the recipe details from each link in total_links_list
        '''
        self.dict_recipe = {
            'uuid': [],
            'sku': [],
            'name': [],
            'description': [],
            'ingredients': [],
            'time': [], 
            'image_url': [], 
            'image_s3': [],
            'recipe_url': []
        }
        #recipe URL
        #self.dict_recipe['recipe_url'] = self.link
        #recipe name
        try:
            self.name = self.driver.find_element(
                By.XPATH, '//h1[@class="gel-trafalgar content-title__text"]').text
            self.dict_recipe['name'] = self.name.replace("'", "")
            #recipe SKU 
            self.SKU = self.name.upper().replace(" ", "-").replace("'", "")
            self.dict_recipe['sku'] = self.SKU
        except:
            pass
        #description
        try:
            description = self.driver.find_element(
                By.XPATH, '//p[@class="recipe-description__text"]').text
            self.dict_recipe['description'] = description.replace("'", "")
        except:
            #webpages do not always have descriptions
            pass
        #recipe total cooking time
        try:
            time_container = self.driver.find_element(
                By.XPATH, '//div[@class="gel-layout__item gel-1/4 recipe-leading-info__side-bar"]/div')
            cook_time = time_container.find_element(By.XPATH, './div[2]/p[2]').text
            self.dict_recipe['time'] = cook_time
        except: 
            pass
        #recipe image url
        try:
            image_tag = self.driver.find_element(
                By.XPATH, '//div[@class="recipe-media__image responsive-image-container__16/9"]/img')
            self.dict_recipe['image_url'] = image_tag.get_attribute('src')
        except:
            #webpages do not always have images
            pass
            
        #recipe ingredients
        try:
            self.dict_recipe['ingredients'] = self.get_ingredients()    
        except:
            pass
        #UUID v4
        self.dict_recipe['uuid'] = str(uuid.uuid4())
        
        
        return self.dict_recipe

