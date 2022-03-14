#%%

from methods import BBCRecipeScraper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import time
import unittest


class RecipeTestScraper(unittest.TestCase):
    
    def setUp(self):
        '''
        Setting up an instance of the webdriver class for testing
        '''
        print('setUp')
        self.WebDriverWait = WebDriverWait
        self.EC = EC
        chrome_options = Options()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f'user-agent={user_agent}')
        self.instance = BBCRecipeScraper(chrome_options)
        
        
    def test_get_categories(self):
        
        category_links = self.instance.get_categories()
        self.assertGreater(len(category_links), 1)
        
    def test_get_links(self):
        
        recipe_links = self.instance.get_links()
        self.assertGreater(len(recipe_links), 1)
        
    def test_current_url(self): 
        self.instance.next_page()     
        try:
            self.WebDriverWait(self.instance.driver, 20).until(self.EC.url_to_be('https://www.bbc.co.uk/food/recipes/a-z/a/10#featured-content'))
        except TimeoutException:
            print(False)
        
        current_page = self.instance.driver.current_url
        exp_page = 'https://www.bbc.co.uk/food/recipes/a-z/a/10#featured-content'
        self.assertEqual(exp_page, current_page) 
        
    def test_ingredients(self):
        self.instance.driver.get('https://www.bbc.co.uk/food/recipes/aclassicspongecakewi_9406')
        get_ingredients = self.instance.get_ingredients()
        self.assertGreater(len(get_ingredients), 1)
        
    def test_get_details(self):
        self.instance.driver.get('https://www.bbc.co.uk/food/recipes/aclassicspongecakewi_9406')
        get_details = self.instance.get_details()
        self.assertGreater(len(get_details), 1)
        
    def tearDown(self):
        print('tearDown/n')
        self.instance.driver.quit()



if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=3, exit=False)


# %%
