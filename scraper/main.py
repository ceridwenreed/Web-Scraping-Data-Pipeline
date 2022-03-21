#%%

import time
from chrome_config import *
from recipe_scraper import *


def main():
    '''
    Function that controls recipe_scraper script
    '''
    
    scraper = BBCRecipeScraper(chrome_options)
    time.sleep(3)
    scraper.accept_cookies()
    scraper.get_categories()
    scraper.next_page()
    scraper.scraper_scrape()


if __name__ == '__main__':
    
    main()

#%%