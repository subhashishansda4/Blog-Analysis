import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
# https://pypi.org/project/syllables/
import syllables

import re
import spacy
nlp = spacy.load("en_core_web_sm")

import nltk
from nltk.corpus import stopwords
#nltk.download('stopwords')
stops = set(stopwords.words('english'))


# -----------------------------------------------------------------------------

# RAW DATA
raw_data = pd.read_excel('data/Input.xlsx')
raw_data = pd.DataFrame(raw_data, columns=['URL_ID', 'URL'])

# generating txt files for each link
dic = dict(zip(raw_data[raw_data.columns[0]], raw_data[raw_data.columns[1]]))
path = 'A:/O/projects/DATA SCIENCE/Black-Coffer/texts/'
raw_text = []
for link in raw_data[raw_data.columns[1]]:
    name = [k for k,v in dic.items() if v == link]
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        ps = soup.find('div', {'class': 'td-post-content'}).find_all('p')
                
    except Exception as e:
        with open('logs.txt', 'w', encoding='utf-8') as f:
            f.write(f"{name[0]}: {e}" + '\n')
    
    texts = [p.text for p in ps]
    
    # making folder to save all the txt files
    os.mkdir(path) if os.path.exists(path) is False else None
    # URL_ID as filename
    with open(f"texts/{name[0]}.txt", 'w', encoding='utf-8') as f:
        for text in texts:
            f.write(text + '\n')
            
    texts = ' '.join(texts)
    raw_text.append(texts)

raw_data['RAW_TEXT'] = raw_text
raw_data.to_csv('output/raw_data.csv')

# -----------------------------------------------------------------------------

# STOP WORDS
stop_type = ['Auditor', 'Currencies', 'DatesandNumbers', 'Generic', 'GenericLong', 'Geographic', 'Names']
stop_words_list = []
stop_file = 'data/StopWords/'
for file in tqdm(os.listdir(stop_file)):
    path = os.path.join(stop_file, file)
    
    if path == os.path.join(stop_file, 'StopWords_GenericLong.txt'):
        with open(path, 'r') as f:
            stop_words_list.append(f.read().split())
    else:
        with open(path, 'r') as f:
            words = f.read().split()
            upper_words = [word for word in words if word.isupper()]
            upper_words = [words.lower() for words in upper_words]
            stop_words_list.append(upper_words)

for i in range(len(stop_type)):
    stop_words_list[i] = ' '.join(stop_words_list[i])
stop_words_list = ' '.join(stop_words_list)
stop_words_list = stop_words_list.split()


# POSITIVE AND NEGATIVE
negative_words = []
positive_words = []
value_file = 'data/MasterDictionary/'
for file in tqdm(os.listdir(value_file)):
    path = os.path.join(value_file, file)
    if file == 'negative-words.txt':
        with open(path, 'r') as f:
            negative_words.append(f.read())       
    else:
        with open(path, 'r') as f:
            positive_words.append(f.read())

negative_words = ' '.join(negative_words)
negative_words = negative_words.split()
negative_words = [words.lower() for words in negative_words]

positive_words = ' '.join(positive_words)
positive_words = positive_words.split()
positive_words = [words.lower() for words in positive_words]

# -----------------------------------------------------------------------------

# REMOVING STOP WORDS
def stop_words(s):
    words = nltk.word_tokenize(s)
    clean = [word for word in words if word not in (stop_words_list or stops)]
    
    s = ' '.join(clean)
    return s

def number_to_words(num):
    to_19 = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
    tens = 'twenty thirty forty fifty sixty seventy eighty ninety'.split()

    def words(n):
        if n < 20:
            return to_19[n-1:n]
        if n < 100:
            return [tens[n//10-2]] + words(n%10)
        if n < 1000:
            return [to_19[n//100-1]] + ['hundred'] + words(n%100)
        for p, w in enumerate(('thousand', 'million', 'billion'), 1):
            if n < 1000**(p+1):
                return words(n//1000**p) + [w] + words(n%1000**p)

    return ' '.join(words(num))

def replace_numbers_with_words(text):
    for word in re.findall(r'\b\d+\b', text):
        num = int(word)
        new_word = number_to_words(num)
        text = text.replace(word, new_word)
    return text


# PREPROCESS
def preprocess(s):
    s = s.lower()
    
    # replace certain special characters with their string esuivalents
    s = s.replace('%', ' percent ')
    s = s.replace('$', ' dollar ')
    s = s.replace('₹', ' rupee ')
    s = s.replace('€', ' euro ')
    s = s.replace('@', ' at ')
    
    # replacing numbers with string esuivalents
    s = replace_numbers_with_words(s)
    
    # replacing connected words with full words
    s = s.replace("'ve", " have")
    s = s.replace("n't", " not")
    s = s.replace("'re", " are")
    s = s.replace("'ll", " will")
        
    # remove punctuations
    pattern = re.compile('[^\w\s.]')
    s = re.sub(pattern, ' ', s).strip()
    
    s = ' '.join(s.split())
    return s

def clean(s):
    s = s.lower()
    
    s = stop_words(s)
    # remove punctuations
    punctuations = re.compile('[^\w\s]')
    s = re.sub(punctuations, '', s).strip()
    
    s = ' '.join(s.split())
    return s
    
data = pd.DataFrame(raw_data['URL_ID'])
data['PRE_PROCESS'] = raw_data['RAW_TEXT'].apply(preprocess)
data['CLEAN'] = data['PRE_PROCESS'].apply(clean)
data.to_csv('output/data.csv')

# -----------------------------------------------------------------------------

# FEATURE ENGINEERING
def positive_negative(words, negative_score, positive_score):
    for word in words:
        if word in positive_words:
            positive_score += 1
        elif word in negative_words:
            negative_score += 1
    return [negative_score, positive_score]

def polarity(words, polarity_score, negative_score, positive_score):    
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    polarity_score = max(-1, min(polarity_score, 1))
    return round(polarity_score, 2)

def subjectivity(words, subjectivity_score, negative_score, positive_score):
    subjectivity_score = (positive_score + negative_score) / (len(words) + 0.000001)
    subjectivity_score = max(0, min(subjectivity_score, 1))
    return round(subjectivity_score, 2)

def average_word_length(characters_count, words_count, word_len):
    word_len = characters_count / words_count
    return round(word_len, 2)

def personal_pronouns(text, pronouns, pronoun_len):
    pronoun = pronouns.findall(text)
    pronoun_len = len(pronoun)
    return pronoun_len

def syllable_count(words, sentences_count, words_count, syllable_len):
    for word in words:
        syllable_len += syllables.estimate(word)
        
    syllable_len -= sentences_count
    syllable_len = syllable_len/words_count
    return round(syllable_len, 2)

def complex_word_count(words, complex_word_len):
    for word in words:
        if syllables.estimate(word) > 2:
            complex_word_len += 1
    return complex_word_len

def average_word_per_sentence(words_count, sentences_count, word_per_sentence_len):
    word_per_sentence_len = words_count / sentences_count
    return round(word_per_sentence_len, 2)

def percent_complex_count(words, words_count, percent_complex_len):
    percent_complex_len = complex_word_count(words, 0) / words_count
    return round(percent_complex_len, 2)

def fog_index(words, words_count, sentences_count, fog):
    fog = 0.4 * (average_word_per_sentence(words_count, sentences_count, 0) + percent_complex_count(words, words_count, 0))
    return round(fog, 2)
    

p_scores = []
n_scores = []
pol_scores = []
sub_scores = []
word_scores = []

syllable_scores = []
word_len_scores = []
complex_word_scores = []
word_per_sen_scores = []
percent_complex_scores = []
fog_scores = []

pnoun_scores = []


texts = data['CLEAN']
for text in texts:
    words = nltk.word_tokenize(text)
    
    word_count = len(words)
    
    n_scores.append(positive_negative(words, 0, 0)[0])
    p_scores.append(positive_negative(words, 0, 0)[1])
    word_scores.append(word_count)
    
for i in range(0, 114):
    pol_scores.append(polarity(words, 0, n_scores[i], p_scores[i]))
    sub_scores.append(subjectivity(words, 0, n_scores[i], p_scores[i]))
    
    
texts_ = data['PRE_PROCESS']
for text in texts_:
    sentences = nltk.sent_tokenize(text)
    words = nltk.word_tokenize(text)
    
    characters_count = len(text) - len(sentences)
    sentences_count = len(sentences)
    words_count = len(words) - len(sentences)
    
    word_len_scores.append(average_word_length(characters_count, words_count, 0))
    syllable_scores.append(syllable_count(words, sentences_count, words_count, 0))
    complex_word_scores.append(complex_word_count(words, 0))
    word_per_sen_scores.append(average_word_per_sentence(words_count, sentences_count, 0))
    percent_complex_scores.append(percent_complex_count(words, words_count, 0))
    fog_scores.append(fog_index(words, words_count, sentences_count, 0))
    

pronouns = re.compile(r'\b(I|we|my|ours|(?-i:us))\b',re.I)
texts__ = raw_data['RAW_TEXT']
for text in texts__:
    pnoun_scores.append(personal_pronouns(text, pronouns, 0))



feat = pd.DataFrame()
feat['POSITIVE SCORE'] = p_scores
feat['NEGATIVE SCORE'] = n_scores
feat['POLARITY SCORE'] = pol_scores
feat['SUBJECTIVITY SCORE'] = sub_scores
feat['AVG SENTENCE LENGTH'] = word_per_sen_scores
feat['PERCENTAGE OF COMPLEX WORDS'] = percent_complex_scores
feat['FOG INDEX'] = fog_scores
feat['AVG NUMBER OF WORDS PER SENTENCE'] = word_per_sen_scores
feat['COMPLEX WORD COUNT'] = complex_word_scores
feat['WORD COUNT'] = word_scores
feat['SYLLABLE PER WORD'] = syllable_scores
feat['PERSONAL PRONOUNS'] = pnoun_scores
feat['AVG WORD LENGTH'] = word_len_scores

output = pd.DataFrame({'URL_ID': raw_data['URL_ID'], 'URL': raw_data['URL']})
output = pd.concat([output, feat], axis=1)

feat.to_csv('output/features.csv')
output.to_excel('output/Output.xlsx')



