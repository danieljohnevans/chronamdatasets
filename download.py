#!/usr/bin/env python
# coding: utf-8

# This Jupyter Notebook produces a dataset from the Chronicling America Title Essays. It introduces readers to the concept of the [Library of Congress API](https://www.loc.gov/apis/), the various facets that it queries, and the titles essays themselves. It is meant to act as a stand-in workshop that introduces a few programming elements while producing the neccessay code to bulk download and package the Chronicling America title essays. If you would like to jump ahead and see the packaged title essays themselves, they are included in this repository as a comma-separated values (CSV) file titled lc_output.csv. That file is updated periodically and was last created on October 13, 2022. 
# 
# To best understand this Jupyter Notebook, read it in conjunction with the following Jupyter [notebook](https://github.com/LibraryOfCongress/data-exploration/blob/master/loc.gov%20JSON%20API/Accessing%20images%20for%20analysis.ipynb). While this notebook provides the reader with the ability to produce datasets, the following notebook hopes to contextualize these data by providing code-snippets for possible project starting points. 
# 
# As a whole, this notebook should be read as a hands-on tutorial for downloading data, selecting metadata fields, and writing that data to CSVs. 
# 
# Please note that not all newspapers have title essays and that title essays are added on a rolling basis. This data is up to date as of October 13, 2022. 
# 
# ---------
# 
# Although they produce different datasets, other notebooks within this [repository](https://github.com/LibraryOfCongress/data-exploration/blob/master/loc.gov%20JSON%20API/Accessing%20images%20for%20analysis.ipynb) function in a similar way to this one. Please use them for reference and as a further guide.
# 

# ----

# ## Title Essays
# 
# In addition to standardized description based on existing cataloging records, newspapers that have been selected for digitization by the [National Digital Newspaper Program](https://www.loc.gov/ndnp/) (NDNP) state partners are accompanied by supplementary description (also known as “title essays”). These essays contain basic information about the paper, including:
# 
# - place of publication (if not already evident);
# - dates and schedule of publication (e.g., weekly, daily, morning, or evening);
# - geographic area covered and circulation statistics;
# - political, religious, or other affiliation and reason for publication;
# - specialized audiences;
# - physical attributes;
# - changes in name, format, and ownership.
# 
# 
# In addition, title essays usually discuss:
# 
# - editors, publishers, or reporters of note;
# - significant events covered by the paper in the relevant time period (a short quote from the paper itself can help provide a sense of the paper's voice);
# - special features such as poetry or fiction, women’s section, sports, society, etc.;
# - relationships with other area newspapers;
# - innovations or advances in newspaper production and technology.
# 
# These brief essays appear as part of the descriptive title information, NDNP state partners research and write these essays specifically for Chronicling America. [The Division of Preservation and Access](https://www.neh.gov/divisions/preservation) of the [National Endowment of the Humanities](https://www.neh.gov) review the essays as part of the NDNP partnership. The essays are intended as starting points for additional research and understanding of the historical role of each newspaper.
# 
# Newspapers that have title essays are identified in the [All Digitized Newspapers list](https://chroniclingamerica.loc.gov/newspapers/) where the “More Info” value is “Yes.” The content of the essays can be searched through the U.S. Newspaper Directory search form, using the “keyword” search. Results will link to records that include those keywords.
# 
# Historical newspapers reflect the language and attitudes of their time, and may contain biased, offensive, and outdated words and images that may be hurtful to particular groups or people. In the title essays, writers strive to avoid this language in supplemental text and only include these terms where it is deemed necessary to understanding the context in which the newspaper was produced. Title essay authors only use such language in the title of the newspaper, the name of an affiliated organization, part of the self-identification of a person or group, or if we are directly quoting from the newspaper. Even then, the title essays only include these terms if the author deems it necessary to understanding the context in which the newspaper was produced.
# 

# ----------------------------

# This code produces a static dataset from Chronicling America's Title Essays. It also includes elements of those title's MARC records. See below for specific details of the metadata captured when the code is run.
# 
# Finally, because this code is written for pedagogic purposes, it is highly commented. Feel free to fork this code, or take elements for your project.

# ------

# ## Part 1

# -------

# The code elements within this notebook can be run by clicking the Run button above. 
# 
# ![Screen%20Shot%202022-10-20%20at%2012.32.35%20PM.png](attachment:Screen%20Shot%202022-10-20%20at%2012.32.35%20PM.png)
# 
# Feel free to edit the code within these boxes, save a copy, and reuse it for your purposes. 

# First, as with most Python notebooks, we will import the necessary Python libraries. 
# 
# Included below is a list of the libraries we are importing along with a link to further documentation.
# 
# - [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
# - [csv](https://docs.python.org/3/library/csv.html)
# - [numpy](https://numpy.org/doc/stable/)
# - [pandas](https://pandas.pydata.org/docs/)
# - [random](https://docs.python.org/3/library/random.html)
# - [requests](https://requests.readthedocs.io/en/latest/)
# - [time](https://docs.python.org/3/library/time.html)
# 
# 

# In[1]:


# import necessary libraries.

from bs4 import BeautifulSoup
import csv
import numpy as np
import pandas as pd
import random
import requests
import time


# Let's first get an idea of the newspapers available in Chronicling America. 
# 
# In order to do this, we'll go to the Library of Congress's website for the [Directory of US Newspapers and filter by Chroncling America](https://www.loc.gov/collections/directory-of-us-newspapers-in-american-libraries/?all=true&c=50&fa=partof_collection:chronicling+america&sp=1). As of October 13, 2022, this search returns 3,683 full text newspaper titles.
# 
# We'll use these URLs and the LCCNs from these URLS to construct our dataset.
# 
# However, first we need to "crawl" this website to save these urls. Web crawling is a form of data mining that anticipates programatically going through web pages and vacuuming up the data on them. Others have written more comprehensive guides and tools do [exist](https://programminghistorian.org/en/lessons/fetch-and-parse-data-with-openrefine). 
# 
# The following two blocks of code generate a list of urls. Like most Jupyter notebooks, this code is broken down into manageable sections that can be run independently of each other. 
# 1. The first block of code creates a list of pages from the Directory of US Newspapers that contain Chronicling America urls.
# 2. The second block, iterates through those pages with Chronicling America urls and saves those urls to a new list. Our code pauses for two seconds, or "sleeps," in between each page so as not to overload the Library of Congress's servers. The end result is a list of 3683 urls. 

# In[2]:


total_url = 'https://www.loc.gov/collections/directory-of-us-newspapers-in-american-libraries/?all=true&c=1000&fa=partof_collection:chronicling+america&sp={}'

pages = list(map(lambda x: total_url.format(x), 
                 range(1, 5)))


# Use beautiful soup to grab urls for lccns:

# In[3]:


links = []
for page in pages:
    response = requests.get(page)
    time.sleep(2)
    soup = BeautifulSoup(response.text, "html.parser")
    for title in soup.find_all("span", "item-description-title"):
        link = title.find("a")["href"]
        links.append(link)


# Let's list the first 10 links to make sure everything worked correctly:

# In[4]:


links[:10]


# And that those link out to a single column csv for analysis and storage.

# In[5]:


header = ["lccn"]
with open("lc_output.csv", "w") as f:
    write = csv.writer(f) 
    write.writerow(header) 
    for link in links:
        write.writerow([link])


# ------------

# ## Part 2

# ---------

# Next, we will take that list of URLs and create a small script to pull down data from the Library API. I originally wrote it as a parallelized script that downloaded the code in about 45 minutes. Unfortunately, it kept overloading the Library of Congress API. I re-wrote it so that it instead uses a handful of 'user-agents' to download the data. This "slow" method takes about three hours. 

# In[6]:


df = pd.read_csv("lc_output.csv")  
    
df.head(10) 


# In[7]:


lccns = df.lccn
lccns.head()


# In[8]:


urls = []

for lccn in lccns:
    urls.append(f"{lccn}?fo=json")


# In[9]:


len(urls)


# In[1]:


# N.B. As of October 13, 2022, ther are only about ~2000 unique essays. The rest are variations and duplicates. 


# In[11]:


with open('user_agents.txt', 'r') as f:
    user_agents_list = [x.strip() for x in f.readlines()]

user_agents_list[:2]


# In[12]:


val = random.randint(0, len(user_agents_list)-1)
# headers = {'User-agent' : user_agents_list[val]}
val


# In[13]:


# generates random headers to avoid timeouts
def rando_headers():
    val = random.randint(0, len(user_agents_list)-1)
    headers = {'User-agent' : user_agents_list[val]}
#     print(headers)


# First, we'll get one record to determine both the structure of the json and figure out which aspects of the record we want to download. We do so below.
# 
# 
# This JSON data is an adaption of the bibliographic metadata created for the Library of Congress's [CONSER Program](https://www.loc.gov/aba/pcc/conser/index.html). The CONSER metadata is standard for all Chronicling America and Library of Congress serials. The [CONSER Documentation and Updates](https://www.loc.gov/aba/pcc/conser/more-documentation.html) page, specifically the section on newspapers, contains more information about the application of CONSER to serials.
# 
# Additionally, the following page contains information for mapping [CONSER Standard Record (CSR) to Metadata Application Profiles (MAPs)](https://www.loc.gov/aba/pcc/conser/issues/CSR.html). This includes information about mapping CONSER to MARC21.
# 
# Finally, please find more information about the metadata contained in the CONSER Standard Record [here](https://www.loc.gov/aba/pcc/conser/documents/CONSER-RDA-CSR.pdf). 

# In[14]:


# get one record to see fields.
# compare extract_timestamp 
r = requests.get("https://www.loc.gov/item/sn85059812/?fo=json")
r.json()


# Once we determine which fields we want to use, we next create a function that downloads selected MARC fields along with the title essays and save them to a Python dictionary. 
# 
# This section needs to be fleshed out a bit more with examples for how to append more / less information from MARC records. It would also be useful to limit by particular subject tags i.e. `African American`

# The following code function downloads all data. We filter based on marc record fields i.e. `created_published` or `date.` These can be further limited based on criteria (see the commented out code below for examples). Feel free to experiment or reach out if you need assistance delimiting data.

# In[15]:


def parse_json(url):
    datum = {}
    response = requests.get(url, headers=rando_headers(), timeout=15)
    
    json_data = response.json() if response and response.status_code == 200 else None
    
    if json_data and 'item' in json_data:
        
        datum['created_published'] = json_data.get('item').get('created_published', 'none')
        # datum['date'] = json_data.get('item').get('date', '1861')
        datum['date'] = json_data.get('item').get('date', 'none')
        datum['dates_of_publication'] = json_data.get('item').get('dates_of_publication', 'none')
        datum['description'] = json_data.get('item').get('description', 'none')
        datum['essay'] = json_data.get('item').get('essay', 'none')
        datum['essay_contributor'] = json_data.get('item').get('essay_contributor', 'none')
        datum['language'] = json_data.get('item').get('language', 'none')
        datum['latlong'] = json_data.get('item').get('latlong', 'none')
        datum['location'] = json_data.get('item').get('location', 'none')
        datum['raw_lccn'] = json_data.get('item').get('raw_lccn', 'none')
        datum['subjects'] = json_data.get('item').get('item').get('subjects', 'none')
        # datum['subjects'] = json_data.get('item').get('subjects', 'African Americans')
        datum['title'] = json_data.get('item').get('item').get('title', 'none')
        datum['url'] = json_data.get('item').get('url', 'none')
        
    time.sleep(0.8)
    
    return datum


# ### Main Loop

# Now that our function is defined and our fields are selected, we can run our code below. We append our data into a large list so that we can save it to a csv later.
# 
# We give our script a timeout of 15 seconds and write the links that don't download to a file called `errors.txt`.
# 
# Note that the code below takes about 3 hours to run. 

# In[16]:


get_ipython().run_cell_magic('time', '', "\ndatas = []\n\nfor url in urls:\n    try:\n        datas.append(parse_json(url))\n    except Exception as e:\n        print(e)\n        \n        with open('errors.txt', 'a') as f:\n            f.write(f'\\n{url}')\n        continue\n    time.sleep(0.7)")


# Finally we write out the data to a csv. If you decide to download different records, you'll need to change the `field_names`

# In[17]:


with open("raw.csv", "w") as f:
        field_names = ['created_published', 'date', 'dates_of_publication', 'description', 'essay', 'essay_contributor',
                          'language', 'latlong', 'location', 'raw_lccn', 'subjects', 'title', 'url']
        writer = csv.DictWriter(f, field_names)
        writer.writerow({x: x for x in field_names})
        for row in datas:
            writer.writerow(row)


# In[18]:


raw = pd.read_csv("raw.csv")  
    
raw


# In[ ]:




