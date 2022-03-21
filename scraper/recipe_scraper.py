
import time
import requests
import uuid
import json
import os
#import boto3
import pandas as pd
import urllib
import tempfile
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from sqlalchemy import create_engine
from storage_credentials import(s3_client, engine)


'''
This is a BBC recipe site scraper module.
A scraper designed to automatically open a URL, navigate the web page,
extract multiple data types from different variables and store data in
an external storage service. 
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
        
        return
        
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
        before_xpath = '//*[@class="az-keyboard gel-wrap"]/div/ul/li['
        after_xpath = ']/a'
        self.category_links = []
        
        for t_rows in range(1, (rows + 1)):
            final_xpath = before_xpath + str(t_rows) + after_xpath
            # the letter x category link does not exist
            try:
                letter_list = self.driver.find_element(By.XPATH, final_xpath)
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
        self.total_links_list = []
        
        for links in self.category_links:
            
            self.driver.get(links)
            time.sleep(3)
            #obtain links for first page, otherwise cannot obtain in loop below
            self.total_links_list.extend(self.get_links())
            #find number of pages per category
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
                    self.total_links_list.extend(self.get_links())
                    
            #obtain 1000 recipe links
            if len(self.total_links_list) > 1000:
                break
            
        print(f'{len(self.total_links_list)} recipe urls obtained.')
        
        return self.total_links_list
    
    
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
            before_xpath =  './li['
            after_xpath = ']/a'
            
            for t_rows in range(1, (rows + 1)):
                final_xpath = before_xpath + str(t_rows) + after_xpath
                try:
                    ingredient = element.find_element(By.XPATH, final_xpath).text.upper()
                    ingredient_list.append(ingredient)
                except:
                    pass
                
        #remove duplicates
        ingredient_list = list(dict.fromkeys(ingredient_list))
        return ingredient_list
    
    
    def _get_details(self):
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
        self.dict_recipe['recipe_url'] = self.link
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
    
    
    def _download_image(self):
        '''
        Downloads the images locally 
        
        This method downloads images as a jpg and the image filename is appended to the 
        dict_recipe, so each image is associated with the correct recipe in dict_recipe
        '''
        # #user friendly ID for each recipe
        self.filepath = f'raw_recipe_data/{self.SKU}'
        #check filepath exists
        if os.path.isdir(self.filepath):
            pass
        else:
            os.makedirs(self.filepath)
        #download image to filepath
        src = self.dict_recipe['image_url']
        try:
            img_data = requests.get(src).content
            with open(f'{self.filepath}/images.jpg', 'wb') as handler:
                handler.write(img_data)
            self.dict_recipe['image_s3'] = f'{self.SKU}.jpg'
        except:
            pass
        
        return
    
    
    def _upload_image(self):
        '''
        Uploads images and stores them externally to an s3 bucket hosted by AWS 
        (Amazon Web Services).
        
        A temporary directory is created to download the images before they are uploaded. 
        The image's object url is appended to the dict_recipe dictionary to ensure each
        image is correctly associated with it's item and obtains a unique identifier.
        '''
        # create temp directory to store images
        with tempfile.TemporaryDirectory() as temp_dir:
            
            src = self.dict_recipe['image_url']
            try:
                urllib.request.urlretrieve(src, f'{temp_dir}/{self.SKU}_image.jpg')
                #upload images to s3 bucket
                s3_client.upload_file(
                    f'{temp_dir}/{self.SKU}_image.jpg', 'demo-aicore-bucket', f'{self.SKU}_image.jpg')
                time.sleep(1)
                #append new image link to dict_recipe dictionary
                self.dict_recipe["image_s3"] = (
                    'https://demo-aicore-bucket.s3.eu-west-2.amazonaws.com/' + f'{self.SKU}_image.jpg')
                
            except:
                pass
        
        return
    
    
    def _download_info(self):
        '''
        Converts the dictionary into a json file and stores locally.
        '''
        #create filepath
        self.filepath = f'raw_recipe_data/{self.SKU}'
        #check filepath exists
        if os.path.isdir(self.filepath):
            pass
        else:
            os.makedirs(self.filepath)
        #save data in json file to same filepath as image
        with open(f'{self.filepath}/data.json', 'w') as json_file:
            json.dump(self.dict_recipe, json_file)
        
        return
    
    
    def _upload_to_cloud(self):
        '''
        Uploads the json file to s3 bucket hosted by AWS as storage for the tabular data.
        '''
        #upload file to s3 bucket
        s3_client.upload_file(
            f'{self.filepath}/data.json', 'demo-aicore-bucket', f'{self.SKU}_data.json')
        
        return
    
    
    def _upload_to_RDS(self):
        '''
        Connects to an RDS instance and SQL database to present the data in table form.
        
        Using sqlalchemy this method creates a query to determine if recipe_data table 
        exists and creates one if it does not. Then it creates a query to find if the
        recipe_url exists in the recipe_data table and appends to it if it does not. 
        '''
        #to pandas
        self.recipe_df = pd.DataFrame.from_dict(self.dict_recipe, orient='index')
        self.recipe_df = self.recipe_df.transpose()
        
        #if SQL table does not exist, create it
        if not engine.execute(  """
                                SELECT EXISTS 
                                (
                                SELECT FROM information_schema.tables 
                                WHERE  table_schema = 'public'
                                AND    table_name   = 'recipe_data'
                                );
                                """
                                ).first()[0]:
            self.recipe_df.to_sql("recipe_data", engine, index=False)
            
            
        #if URL does not exist in recipe_data table, append df
        if not engine.execute(  f"""
                                SELECT EXISTS
                                (
                                SELECT * FROM recipe_data
                                WHERE recipe_url = '{self.link}'
                                );
                                """        
                                ).first()[0]:
            self.recipe_df.to_sql("recipe_data", engine, index=False, if_exists='append')
            
        return
    
    
    def scraper_scrape(self):
        '''
        Scrape data for each link in total_links_list through get_details method
        
        Store and upload the data by calling upload_image, download_info, 
        upload_to_cloud and upload_to_RDS methods
        '''
        for self.link in tqdm(self.total_links_list):
            
            self.driver.get(self.link)
            time.sleep(3)
            self._get_details()
            time.sleep(5)
            # self._download_image()
            self._upload_image()
            self._download_info()
            self._upload_to_cloud()
            self._upload_to_RDS()
            
        print(f'{len(os.listdir("raw_recipe_data"))} urls have been scraped')
