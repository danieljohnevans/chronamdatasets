#!/usr/bin/env python
# coding: utf-8

# This Jupyter notebook provides some basic building blocks for analyzing Chronicling America Title Essay datasets. Please reach out with any comments, edits, suggestions, or questions.

# --------

# First we will import the necessary packages. To ease our analysis we rely heavily on two popular Python natural language processing frameworks: `nltk` and `spacy`. As part of this import step, we need to download the necessary tokenization and language models packages.

# In[1]:


from bs4 import BeautifulSoup
import csv
import logging
import pandas as pd
import requests
import time
import nltk
import spacy
import numpy as np
from nltk.text import Text

# display max column width for descriptions
pd.set_option('display.max_colwidth', None)


# In[2]:


nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# get_ipython().system('python3 -m spacy download en_core_web_sm')

# load small language model
nlp = spacy.load("en_core_web_sm")


# Next we'll read in the raw data. To make sure everything is working correctly, we'll print out the first few lines

# In[3]:


df = pd.read_csv("raw.csv")
df.head()


# We next create a small Python function that removes the html tags from the `essay` column:

# In[4]:


def stripped_strings(text):
    try:
        return (' '.join(BeautifulSoup(text).stripped_strings))
    except TypeError as e:
        print(e)


df['essay'] = [stripped_strings(text) for text in df['essay'] ]
    


# In[5]:


df.head()


# -------

# Now that the data has been cleaned, we can begin pre-processing it. Let's [tokenize](https://www.nltk.org/_modules/nltk/tokenize/punkt.html) the essays into their individual components. First, we convert the `essay` column into a string. We'll next break the essays down into individual unigrams and then break those down into tokenized words. Read more about `unigrams` and `word tokenization` here: *GET LINK*

# In[6]:


df["essay"] = df["essay"].astype(str)


# In[7]:


start = time.time()
df["unigrams"] = df["essay"].apply(nltk.word_tokenize)
print(time.time() - start)


# Let's print out our unigrams to get a sense of what our code did.

# In[8]:


text = df['unigrams'].apply(Text)
text.head()


# Next we'll tokenize the sentences and apply part of speech tagging.

# In[27]:


token_sent = df.essay.apply(nltk.word_tokenize)  
tagged_sent= token_sent.apply(nltk.pos_tag)
tagged_sent.head()


# Now that we have pre-processed our `essays`, we can do basic things like get the count of words. e.g. 'century'

# In[10]:


t = token_sent.apply(lambda x: nltk.Text(x).count('century'))
t


# More interesting, perhaps, is the fact that we can create a concordance of words and perform a search. In this example, we concordance search, grab 35 characters before / after word a particular word. Rows with `no matches` denote that the essay does not contain the text in question.

# In[26]:


t = token_sent.apply(lambda x: nltk.Text(x).concordance("printer"))
t.head()


# -------

# Another aspect that thinks more deeply about extracting information from title essay content utilizes `spacy's` language models to isolate named identities such as people, organization, and locations within the unstructured content of the essays.
# 
# The code below extracts people and organizations from the title essays. The commented text also includes starter code to extract noun phrases or locations.
# 
# NOTE: This code takes a few minutes to run.

# In[12]:


df['essay']= df['essay'].astype(str)
ppl_df = pd.DataFrame()


for row in range(len(df)):
    people = {}
    lccn = df.loc[row, "raw_lccn"]
    doc = nlp(df.loc[row, "essay"])
#     for np in doc.noun_chunks:
#         print(np.text)
    person = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
    orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    lccn = str(lccn).strip()
    people[lccn] = [person, orgs]
    t = pd.DataFrame.from_dict(people, orient='index', columns=["people","organization"])
    ppl_df = pd.concat([ppl_df, t], ignore_index = True)

#     test['person'] = docs.ents.apply(ent.text if ent.label == 'PERSON')
#     orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
#     LOC = [ent.text for ent in doc.ents if ent.label_ == 'LOC']
#     person = pd.DataFrame(person)
#     print(person)
#     test['person'] = person.loc[row, "essay"]


# In[25]:


ppl_df.tail()


# In[14]:


df_cd = pd.concat([df, ppl_df], axis=1)


# In[24]:


df_cd.head()


# In[17]:


final = pd.concat([df, ppl_df], axis=1, sort=False)


# In[23]:


final.head()


# Finally, we'll save this data as a csv for external analysis:

# In[21]:


final.to_csv('final.csv', index=False)

