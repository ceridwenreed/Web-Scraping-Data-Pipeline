
FROM python:3.8-slim-buster

    #install required modules
RUN apt-get -y update && \
    apt-get -yqq install wget gnupg curl unzip libpq-dev gcc && \
    pip install psycopg2 && \
    # install google chrome
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get -y update && \
    apt-get install -y google-chrome-stable && \
    #get chrome version
    CHROMEVER=$(google-chrome --product-version | grep -o "[^\.]*\.[^\.]*\.[^\.]*") && \
    DRIVERVER=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROMEVER") && \
    # install chromedriver
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$DRIVERVER/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

COPY . .

#install requirements
RUN pip install -r requirements.txt

#run scraper
CMD ["python3", "scraper/recipe_scraper.py"]
