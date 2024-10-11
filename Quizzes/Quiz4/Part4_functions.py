import requests
import re
import string

# Refactored these functions slightly so they could be tested - required that valence() has form valence(text)

def remove_stopwords(stopwords, words):
    list_ = re.sub(r"[^a-zA-Z0-9]", " ", words.lower()).split()
    return [itm for itm in list_ if itm not in stopwords]

def clean_text(stopwords, text):
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)
    text = re.sub('[\d\n]', ' ', text)
    return ' '.join(remove_stopwords(stopwords,  text))

def calc_word_valence(word, afinn_dict):
    if word in afinn_dict:
        return int(afinn_dict[word])
    else:
        return None

def calc_valence(text, afinn_dict):
    '''
    Gets the valence of a line of cleaned text, returned as a list of valences at each word
    '''
    # At this point they will have been cleaned, so we assume a space seperator
    word_valences = list(map(lambda word: calc_word_valence(word, afinn_dict), text.split(' ')))
    return list(filter(lambda valence: valence is not None, word_valences))

def valence(text):
    '''
    Gets the valence of a line of raw text
    '''
    # Using afinn_dict and stopwords as inputs so I don't have to load them anew for every line - just once at beginning of mapper
    stopwords_list = requests.get("https://gist.githubusercontent.com/rg089/35e00abf8941d72d419224cfd5b5925d/raw/12d899b70156fd0041fa9778d657330b024b959c/stopwords.txt").content
    stopwords = list(set(stopwords_list.decode().splitlines()))

    afinn = requests.get('https://raw.githubusercontent.com/fnielsen/afinn/master/afinn/data/AFINN-en-165.txt').content.decode().splitlines()
    afinn_dict = dict(map(lambda x: (x.split('\t')), afinn))
    
    if type(text) != str:
        text = text.decode()
    return calc_valence(clean_text(stopwords, text), afinn_dict)