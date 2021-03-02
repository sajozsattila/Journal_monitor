#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib
import pandas as pd
import re
import datetime
import numpy as np
import pickle
import requests
from time import sleep
import pandas as pd
import random
import os
import random


# In[2]:


version = "1.0.0"
datadir = "data/"
archivedir = "data/Archive"


# In[3]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from selenium.webdriver.support.ui import WebDriverWait, Select

from selenium.webdriver.firefox.options import Options
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)


# In[4]:


journals = pd.read_csv("doaj_journals.csv", sep="|")
journals = journals[journals['publisher'] == "Optical Society of America (OSA)"]
journals = journals.to_dict('records')
random.shuffle(journals)
print(journals)


# In[5]:


def gedjournalarticles(journal, filename, driver):
    # open old file
    olddf = pd.DataFrame({'url': [] })
    try:
        olddf = pd.read_pickle(os.path.join(archivedir, filename))
        print(olddf.tail())
    except:
        pass
    
    driver.get(journal['address'])
    print(driver.current_url)
    sleep(5)
    
    # itterate over the journal searching to get the Article list
    articles = []
    def pagefind():
        # get all of the Article on this page
        content = driver.page_source
        # load the page content in BeautifulSoup
        soup = BeautifulSoup(content, features="lxml")
        # found the Article
        for h5 in soup.find_all("h3"):
            # get link 
            for a in h5.find_all("a"):        
                articles.append("https://www.osapublishing.org"+a['href'])
    
        # find next page
        for ulp in driver.find_elements_by_class_name('pagination'):
            try:
                for lis in ulp.find_elements_by_css_selector('li.active + li a'):
                    print(lis.text)
                    lis.click()
                    sleep(random.uniform(15, 45))                        
                    return True
            except exception as e:
                print(e)
                return False
        return False

    nextpage = True
    while  nextpage:
        nextpage = pagefind()                
        print(driver.current_url, end='\r')
        
    # filer out old articles
    oldarticles = olddf['url']
    articles = list( set(articles).difference(set(oldarticles) ))
    print(len(articles), "new article found!")
    
    # make df
    df = pd.DataFrame({'url': list(set(articles)), 
                       'journal_title': journal['title'], 
                       'journal_eissn': journal['eissn'],
                       'journal_pissn': journal['pissn'],
                       'category': journal['categories']
                      })
    # chek there was a not Arhived but previously loaded file
    adf = None
    try:
        adf = pd.read_pickle(os.path.join(datadir, filename))
    except:
        pass
    if adf is not None:
        df = pd.concat([df, adf])
        df.drop_duplicates(inplace=True)
    
    return df, olddf


# In[6]:


def getarticledetails(df, olddf, filename):
    
    articles = df['url'].values

    titles = [ None for _ in range(len(df))]
    abstracts = [ None for _ in range(len(df))]
    writers = [ None for _ in range(len(df))]
    dates = [ None for _ in range(len(df))]
    dois = [  None for _ in range(len(df)) ]
    keywords = [  None for _ in range(len(df)) ]

    for idx in range(len(articles)):
        # print percentiage of the process
        print( str(np.round(100*idx/len(df),2))+"%" , end='\r')
        
        url = df.iloc[idx]['url']
        request = urllib.request.Request(url)
        request.add_header('Accept-Encoding', 'utf-8')
        try:
            response = urlopen(request)    
            page_content = response.read().decode('utf-8')
        except:
            continue
    
        page_soup = BeautifulSoup(page_content, features="lxml")
        
        # abstract
        abstract = ""
        abst = page_soup.find("h2", {'id':['Abstract']})
        count = 0
        while True:
            abst = abst.findNext('p')
            if abst.get_text() is not None and len(abst.get_text()) > 10:
                abstract = abst.get_text()
                break
            
            if count == 3:
                break
            count = count+1
        if len(abstract) > 0:
            abstracts[idx] = abstract
        else:
            # if no abstract we ignore the page
            print('No abstract:', url)
            continue

        # title
        titles[idx] = page_soup.find('title').get_text().split("|")[1] 
        # if all title is capital we change it just the first letter
        fullcapital = True
        titletext = re.sub(r'[^a-zA-Z]', '', titles[idx], flags=re.UNICODE)
        for l in titletext :
            if l.isupper() is False:
                fullcapital = False
                break
        if fullcapital:
            titles[idx] = titles[idx].lower().title()
            
        # writer and publish date
        writter = []
        key = []
        for m in page_soup.find_all("meta"):
            if m.has_attr("name"):
                if m['name'] == "citation_author":
                    writter.append( m['content'].title() )
                # add the author institute to the author
                elif m['name'] == "citation_author_institution":
                    writter[-1] = writter[-1] + "--" + m['content']
                # add writer orcid 
                elif m['name'] == "citation_author_orcid":
                    writter[-1] = writter[-1] + "---" + m['content']
                elif m['name'] == "dc.date":
                    # change to ISO dateformat
                    dates[idx] = datetime.datetime.strptime(m['content'], "%Y-%m-%d").strftime('%Y-%m-%d')
                elif m['name'] == "citation_doi":
                    dois[idx] = m['content']
                elif m['name'] == "dc.subject":
                    key.append( m['content'] )
        # writers            
        if len(writter) > 0:
            writers[idx] =  "#".join(writter)        
        # keywords
        if len(key) > 0:
            keywords[idx] =  "#".join(key)
        
        sleep(random.uniform(15, 45))
    
    # extend the df
    df['title'] = titles
    df['doi'] = dois
    df['abstract'] = abstracts
    df['writer'] = writers
    df['publishdate'] = dates
    df['keyword'] = keywords
    
    # merge owith old df
    df = pd.concat([df, olddf])
    print(df.head())
    
    # save data
    df.to_pickle(os.path.join(datadir, filename))
    
    # test
    test = pd.read_pickle(os.path.join(datadir, filename))
    print(test.tail())


# In[7]:


journalsenrichment = [   
    {'eissn': '2334-2536', 'address': 'https://www.osapublishing.org/search.cfm?q=&j=optica&v=&i=&p=&cj=1&cc=0&cr=0'},
    {'eissn': '2159-3930', 'address': 'https://www.osapublishing.org/search.cfm?q=&j=ome&v=&i=&p=&cj=1&cc=0&cr=0'},
    {'eissn': '1094-4087', 'address': 'https://www.osapublishing.org/search.cfm?q=&j=oe&v=&i=&p=&cj=1&cc=0&cr=0'},
    {'eissn': '2578-7519', 'address': 'https://www.osapublishing.org/search.cfm?q=&j=osac&v=&i=&p=&cj=1&cc=0&cr=0'},
]


# In[8]:


for jidx in journals:
    for eidx in journalsenrichment:
        if jidx['eissn'] == eidx['eissn']:
            jidx['address'] = eidx['address']            
print(journals)


# In[9]:


random.shuffle(journals)
for jidx in range(len(journals)):
    filename = 'journal_'+ journals[jidx]['title'].replace(" ", "_").replace(":", "") +'_'+version+'.pandas'
    
    # search for articles
    df, olddf = gedjournalarticles(journals[jidx], filename, driver )
    
    # get the articles details
    getarticledetails(df, olddf, filename)


# In[ ]:


driver.close()


# In[ ]:


print(df.iloc[16]['url'])


# In[ ]:


print(df.tail())

