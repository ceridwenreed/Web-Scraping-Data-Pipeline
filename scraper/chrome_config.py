'''
This file is to configure chrome options when calling google chrome
in the web scraper.  

'''

from selenium.webdriver.chrome.options import Options

chrome_options = Options()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
chrome_options.add_argument("window-size=1920,1080")
chrome_options.add_argument("--headless")
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-running-insecure-content')
chrome_options.add_argument("--allow-insecure-localhost")
chrome_options.add_experimental_option('detach', True)