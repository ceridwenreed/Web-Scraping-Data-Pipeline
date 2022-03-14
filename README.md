# BBC-Recipe-Web-Scraper

## Contents of this file
### Introduction
### Milestones 1-7
### Conclusion


## Introduction

This is a web scraper designed to retrieve information from BBC recipe site and store it locally in a JSON file, as well as in an externally hosted S3 bucket.


## Milestone 1: Navigating webpages with Selenium

First the website is retrieved using python library requests, where requests.get() returns a response from the API.  

Links to recipe webpages are obtained using Selenium to read the HTML code and find web elements by XPATH and the attribute 'href' which contains the link. Selenium with python provides a simple API to create step-by-step interactions with a webpage and assess the response of a browser to various changes using Selenium WebDriver. 

The website is navigated using web element XPATHs in order to scrape a large amount of URLs. This is achieved, for example, by automating finding the number of pages that contains recipe links and clicking onto the next page.

Try/except statements are implemented to bypass any URLs which cause finding of web elements to fail.


## Milestone 2: Data point extraction

Data points are extracted from each recipe URL via web element relative XPATHs and appended to a dictionary. Universally unique IDs (UUID) are generated using using *str(uuid.uuid4())* and the user friendly Stock Keeping Unit (SKU) is created from the name acquired from the recipe.  

The dictionary created for each recipe is converted to a JSON file and save locally, where the folder is associated with the unique SKU. Images are downloaded from the image URL inside the dictionary and saved to the same folder as the JSON file. 


## Milestone 3: Unit testing

Unit testing is achieve through unittest module, a built-in Python testing framework. The unittest module provides *assert* methods that allows the user to check for and report failures in their code.  

*assertGreater(first, second)* function is used to compare two objects, where the first is greater than the second. For example, to demonstrate the scraper module has obtained and concatinated list of URLs, we state that the *len(list)* of the list is greater than 1: *assertGreater(len(list), 1)*

*assertEqual(first, second)* function is used to compare two objects and states that they must be equal to pass the unittest. For exmaple, to demonstrate the scraper module is navigating the webpage correctly, we assert what the URL should be after calling a method. 

Each test must be carried out independently to other test cases within the test class, hence the methods.py file in th test folder is adjusted so each method is standalone and does not require another method to function correctly.  

*setUp()* is called before each test method and is used to assert chrome_options arguments such as *headless* mode for each instance of the webpage. 


## Milestone 4: Cloud services and storage

Data points extracted from the recipe webpages are stored locally and in the cloud. This is achieved through Amazon Web Services (AWS). The JSON files and saved images (obtained in Milestone 2) are uploaded to an Amazon Simple Storage Service (S3) bucket, which is a filesystem or data lake where you can store your files in the cloud. In order to access the S3 bucket on AWS from the webscraper module, an Identity and Access Management (IAM) user must be created to provide the necessary credentials. The scraper module is connected to the S3 bucket using the IAM credentials through *boto3* module. 

A temporary directory is created to download the images before they are uploaded, using *tempfile.TemporaryDirectory(suffix=None, prefix=None, dir=None, ignore_cleanup_errors=False)*. *urllib.request.urlretrieve(url, filename=None, reporthook=None, data=None)* is used to copy the URL from the dictionary to a temporary directory. Which is then uploaded to the S3 bucket. Each JSON file and image is uploaded to the bucket with a unique SKU, so the image is associated with the correct recipe and to prevent re-uploading of the same data.  

An PostgreSQL database is created to store the data and display it in tabular form, through AWS Regional Database Service (RDS). The scraper module is connected to RDS using *slqalchemy* module. *sqlalchemy* can be used to send queries to the postgreSQL database to determine if a specific URL has been scraped already.


## Milestone 5: Docker

Docker is tool that containerises an application so it can run in any environment. Containerising is the process using containers to hold an application and all the dependecies within a single environment. Docker containers virtualise the operating system (OS), and provides the necessary tools to make a specific OS run without needing to install it. Docker images are the templates to run containers, and indicates the steps needed to run the container.  

Docker images are built using Dockerfiles, which contains commands to build the layers of a docker image. *FROM python:3.8-slim-buster* specifies the base image, which in this instance is a version of python. *RUN* command tells Docker which additional commands to execute. To run the webscraper in a docker container, it is necessary to install Google Chrome and Chrome driver (the same version). *RUN* command is also used to install the requirements such as modules needed to run the webscraper, where a requirements.txt is generated from *pipreqs* inside the webscraper directory. *COPY* command is used to copy files from context location to current working directory inside the container. If the Dockerfile is in the same directory as the file you want to build a container for, use *COPY . .* command. Finally, *CMD* command tells Docker to execute the command when the image loads, and is used to launch the webscraper.


## Milestone 6: Monitoring and Prometheus

Docker containers can be run inside an EC2 instance (SSH). AWS Elastic Compute Cloud (EC2) service allows you to run virtual machines on Amazon's infrastructure. Crontab can be used inside SSH to schedule tasks, such as running the webscraper, at a specific time. 

Docker containers run inside SSH can be monitored using Prometheus. Prometheus is an open source monitoring and alerting toolkit for gathering and processing data locally. Inside SSH, create a docker container running prometheus (pulled from DockerHub) and configure a prometheus.yml config file. This is so Prometheus can access your EC2 instance through the public IPv4 address. Hence, EC2 security groups will need to be edited so there is an inbound rule for Prometheus port *9090*. 

Grafana is used with Prometheus to create monitoring dashboards. Prometheus must be added as a data source in Grafana to start tracking the metrics of the webscraper container. Prometheus panels can then be built inside Grafana to customise the visualisation of the monitoring process. 


## Milestone 7: CI/CD Pipeline

Create an access token on DockerHub and add this to Secrets on Github. On Github Actions, configure Docker image so that everytime a new commit is made to the main branch, this initiates a docker build and pushes the docker image to DockerHub.


## Conclusion

### Improvements:

    - The BBC recipe site has over 10,000 recipes that can be scraped (the limiting factor of 1000 URLs can be removed, however the scraping process will take a long time, this could be achieved using cronjobs).
    
    - Ingredients from each recipe can be obtained in a list, which can be uploaded to RDS as separate data points. Relational model for database management can be applied in PostgreSQL to create (many-to-many relational) tables that allow a user to essentially 'filter' recipe retrieval and return recipes containing only a specific set of ingredients. A meal planner, tada!

    - This can be paired with a supermarket site scraper, where by scraping the latest 'ingredient' offers, you can plan what ingredients to buy based on both the cheaper prices and a specific recipe to use the ingredients for.  