
# Web Scraping Homework
# Author: Michael Regpala
# Create Date: 20210327

#Import our Modules
from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pandas as pd
import time 

#Variables
#Site URL Variables
site_base = 'https://astrogeology.usgs.gov'
mars_latest_news_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
mars_gallery_url = 'https://www.jpl.nasa.gov/images?search='
mars_facts_url = 'https://space-facts.com/mars/'
mars_hemisphers_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced'

#Global Variables
paragraph = ""
title = ""

def scrape():
    #Use Beautiful Soup to scrape latest news
    html = requests.get(mars_latest_news_url)
    bs = BeautifulSoup(html.text,'html.parser')
    results = bs.find("div",class_="slide")
    #Following variables contain title and paragraph text from latest news article.
    paragraph = results.a.text.strip()
    title = results.find('div',class_="content_title").text.strip()


    #Setup Chrome session for splinter/selenium scraping
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    #Use Splinter and Beautiful Soup to get image source for current featured Mars image
    browser.visit(mars_gallery_url)
    time.sleep(2)
    #Click on Mars checkbox to get featured Image
    browser.find_by_css("input[id=filter_Mars]").first.click()   
    time.sleep(2)
    bs = BeautifulSoup(browser.html,'html.parser')
    result = bs.find("div", class_='SearchResultCard')
    large_image_html = result.a['href']
    browser.click_link_by_href(large_image_html)
    bs = BeautifulSoup(browser.html,'html.parser')
    results = bs.find("div",class_= "BaseImagePlaceholder")
    featured_image_url = results.img['data-src']

    #Scrape HTML Tables Mars Stats with Pandas

    html = requests.get(mars_facts_url)
    df = pd.read_html(html.text)
    mars_facts_df = df[0]

    cols = ["Stats", "Values"]

    mars_facts_df.set_axis(cols,axis="columns",inplace=True)
    mars_facts_df.set_index(["Stats","Values"],inplace=True)
    mars_facts_html_table = mars_facts_df.to_html(classes=["table","table-striped"])

    mars_facts_html_table = mars_facts_html_table.replace('\n', '')
    browser.visit(mars_hemisphers_url)
    time.sleep(1)
    bs = BeautifulSoup(browser.html,'html.parser')
    results = bs.find_all('div', class_="item")
    hemi_image_url_list = []
    for result in results:
        hemi_dict = {}
        link = result.a['href'].strip()
        title_url = result.h3.text
        browser.visit(site_base + link)
        time.sleep(1)
        bs = BeautifulSoup(browser.html,'html.parser')
        res = bs.find('img',class_='wide-image')
        img_url = site_base + res['src']
        hemi_dict = {"title":title_url, "img_url":img_url}
        hemi_image_url_list.append(hemi_dict)

    final_dict = {
        "LatestNewsTitle": title,
        "LatestNewsParagraph":paragraph,
        "FeatureImageUrl": featured_image_url,
        "MarsFactHtml":mars_facts_html_table,
        "HemispherImageUrlList":hemi_image_url_list
    }
    browser.quit()
    return final_dict

