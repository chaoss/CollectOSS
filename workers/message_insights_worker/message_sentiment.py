import csv
import logging
import os
import random
import re
import string
import sys
import warnings
from statistics import mean

import emoji
import joblib
import nltk
import numpy as np
from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils import compute_sample_weight
from xgboost import XGBClassifier
from xlrd import open_workbook

from augur import ROOT_AUGUR_DIRECTORY
from workers.message_insights_worker.preprocess_text import \
    CONTRACTION_MAP as contraction_map
# End of initial imports


# Forcing errors to be ignored, since the worker is highly experimental 
warnings.filterwarnings('ignore')

# Initial setup of machine learning functionality
CONTRACTION_MAP = contraction_map

train_path = os.path.join(ROOT_AUGUR_DIRECTORY, "workers", "message_insights_worker", "train_data")

def replace_all(text, dic):
    if(sys.version_info[0] < 3):
        for i, j in dic.iteritems():
            text = text.replace(i, j)
    else:
        for i, j in dic.items():
            text = text.replace(i, j)
    return text

stemmer = SnowballStemmer("english")

def stem_tokens(tokens):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize_and_stem(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens)
    return stems
# End of initial machine learning setup

# List of “stop words”, words that do not generally convey positive or negative emotion, usually join multiple parts of a sentence together
# They are added by the developer from other sources that are additive to the default stopwords in NLTK (Natural Language Toolkit)
mystop_words = [
    'i', 'me', 'my', 'myself', 'we', 'our',  'ourselves', 'you', 'your',
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her',
    'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'themselves',
    'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
    'and',  'if', 'or', 'as', 'until',  'of', 'at', 'by',  'between', 'into',
    'through', 'during', 'to', 'from', 'in', 'out', 'on', 'off', 'then', 'once', 'here',
    'there',  'all', 'any', 'both', 'each', 'few', 'more',
    'other', 'some', 'such',  'than', 'too', 'very', 's', 't', 'can', 'will',  'don', 'should', 'now'
    # keywords
    'while', 'case', 'switch', 'def', 'abstract', 'byte', 'continue', 'native', 'private', 'synchronized',
    'if', 'do', 'include', 'each', 'than', 'finally', 'class', 'double', 'float', 'int', 'else', 'instanceof',
    'long', 'super', 'import', 'short', 'default', 'catch', 'try', 'new', 'final', 'extends', 'implements',
    'public', 'protected', 'static', 'this', 'return', 'char', 'const', 'break', 'boolean', 'bool', 'package',
    'byte', 'assert', 'raise', 'global', 'with', 'or', 'yield', 'in', 'out', 'except', 'and', 'enum', 'signed',
    'void', 'virtual', 'union', 'goto', 'var', 'function', 'require', 'print', 'echo', 'foreach', 'elseif', 'namespace',
    'delegate', 'event', 'override', 'struct', 'readonly', 'explicit', 'interface', 'get', 'set', 'elif', 'for',
    'throw', 'throws', 'lambda', 'endfor', 'endforeach', 'endif', 'endwhile', 'clone'
]

emodict = []

# Pull in words from the library with their associated emotion values
with open(os.path.join(train_path,"EmoticonLookupTable.txt"),"r") as emotable:
    emoticon_reader=csv.reader(emotable,delimiter='\t')

    #Hash words from dictionary with their values
    emodict={rows[0]:rows[1] for rows in emoticon_reader}
    emotable.close()

# Helping the program take in account sentence structure when analyzing the text
grammar = r"""
NegP: {<VERB>?<ADV>+<VERB|ADJ>?<PRT|ADV><VERB>}
{<VERB>?<ADV>+<VERB|ADJ>*<ADP|DET>?<ADJ>?<NOUN>?<ADV>?}
"""
chunk_parser = nltk.RegexpParser(grammar)

# Takes into account verbal contractions (shorthand, like anything with “ ‘nt “)
def expand_contractions(text, contraction_mapping=CONTRACTION_MAP):
    contractions_pattern = re.compile('({})'.format('|'.join(contraction_mapping.keys())),
                                      flags=re.IGNORECASE | re.DOTALL)

    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        expanded_contraction = contraction_mapping.get(match) if contraction_mapping.get(
            match) else contraction_mapping.get(match.lower())
        expanded_contraction = first_char+expanded_contraction[1:]
        return expanded_contraction

    expanded_text = contractions_pattern.sub(expand_match, text)
    expanded_text = re.sub("'", "", expanded_text)
    return expanded_text

# Function to remove URLs, as it would be silly to dissect the emotion in a URL
def remove_url(s):
    url_regex = re.compile(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_regex.sub(" ", s)

# List of negation words that cause the following word to reverse its meaning
negation_words = ['not', 'never', 'none', 'nobody', 'nowhere', 'neither', 'barely', 'hardly',
                  'nothing', 'rarely', 'seldom', 'despite']
emoticon_words = ['PositiveSentiment', 'NegativeSentiment']

# Function to remove html tags from the text being analyzed 
def remove_tags(s):
    soup = BeautifulSoup(s, "html.parser")
    for tag in soup.find_all('strong'):
        tag.replaceWith('')
        s = soup.get_text()
    return s

# Function to handle words separated by punctuation but not white space
def joint_words(s):
    punc = list(string.punctuation)
    s = re.sub('[\.\-\_\\/&]', ' ', s)
    s = "".join([word.lower() for word in s if word not in punc])
    s = word_tokenize(s)
    s = " ".join([word for word in s if len(word) <= 30])
    s = re.sub('[0-9]+', '', s)
    s = re.sub('lgtm', 'look good', s)
    return s

# Function to determine if a word is negated in the input by seeing if there is a negation word followed by a normal word
def negated(input_words):
    # Determine if input contains negation words
    neg_words = []
    neg_words.extend(negation_words)
    for word in neg_words:
        if word in input_words:
            return True
    return False

# Function to add “NOT_” to the beginning of the given word
def prepend_not(word):
    if word in emoticon_words:
        return word
    elif word in negation_words:
        return word
    return "NOT_"+word

# Loop through every word in a list of comments, find the words that are negated, and call the previous function to prepend “NOT_”, if the word is an adverb, adjective, or verb
def handle_negation(comments):
    sentences = nltk.sent_tokenize(comments)
    modified_st = []
    for st in sentences:
        allwords = nltk.word_tokenize(st)
        modified_words = []
        if negated(allwords):
            part_of_speech = nltk.tag.pos_tag(allwords, tagset='universal')
            chunked = chunk_parser.parse(part_of_speech)
            for n in chunked:
                if isinstance(n, nltk.tree.Tree):
                    words = [pair[0] for pair in n.leaves()]
                    if n.label() == 'NegP' and negated(words):
                        for i, (word, pos) in enumerate(n.leaves()):
                            if (pos == "ADV" or pos == "ADJ" or pos == "VERB") and (word != "not"):
                                modified_words.append(prepend_not(word))
                            else:
                                modified_words.append(word)
                    else:
                        modified_words.extend(words)
                else:
                    modified_words.append(n[0])
            newst = ' '.join(modified_words)
            modified_st.append(newst)
        else:
            modified_st.append(st)
    return ". ".join(modified_st)

# Function that calls every prior function to clean up the text and make it easier to analyze
def preprocess_text(s):
    text = expand_contractions(s)
    text = remove_tags(text)
    text = emoji.demojize(text)
    text = text.encode('ascii', 'ignore').decode('utf-8', 'ignore')
    text = re.sub('\n', ' ', text)
    text = re.sub('\r', ' ', text)
    text = replace_all(text, emodict)
    text = re.sub('[()){}]', ' ', text)
    text = re.sub('\<[^<>]*\>', '', text)
    text = re.sub('\`[^``]*\`', '', text)
    s = re.sub(r'\w*@\w*', ' ', text)
    text = remove_url(text)
    text = joint_words(text)
    text = handle_negation(text)
    return text


# Constructor for SentimentData
class SentimentData:
    def __init__(self, text, rating):
        self.text = text
        self.rating = rating


class SentiCR:
    # Constructor for SentiCR, trains a new machine learning model or pulls an existing one.
    def __init__(self, training_data=None, models_dir=os.path,logger=logging):
        self.algo = 'XGB'
        self.models_dir = models_dir
        self.logger = logger
        if training_data is None:
            # Check if pretrained model exists, else perform training
            if os.path.exists(f'{self.models_dir}/{self.algo}_senti.pkl'):
                self.logger.info('Using existing Trained Model')
                self.model = joblib.load(f'{self.models_dir}/{self.algo}_senti.pkl')
                self.vectorizer = joblib.load(f'{self.models_dir}/tfidf_vectorizer.pkl')
                self.logger.info('Loaded Trained Models')
            else:
                self.logger.info('Using default train set')
                self.training_data = self.read_data_from_oracle()
                self.model = self.create_model_from_training_data()

        else:
            self.training_data = training_data
            self.logger.info('Using custom train set')
            self.model = self.create_model_from_training_data()

    # Method that is called in the SentiCR constructor, uses training data to create a model 
    def create_model_from_training_data(self):
        training_comments = []
        training_ratings = []

        self.logger.info("Training sentiment classifier model..")
        for sentidata in self.training_data:
            comments = preprocess_text(sentidata.text)
            training_comments.append(comments)
            training_ratings.append(sentidata.rating)
        self.logger.info('Text Preprocessing done')

        # Discard stopwords, apply stemming, and discard words present in less than 3 comments
        self.vectorizer = TfidfVectorizer(tokenizer=tokenize_and_stem, sublinear_tf=True, max_df=0.5,
                                          stop_words=mystop_words, min_df=3)
        # Saving TFIDF vectors as .pkl file for future use
        X_train = self.vectorizer.fit_transform(training_comments).toarray()
        Y_train = np.array(training_ratings)
        joblib.dump(self.vectorizer, f'{self.models_dir}/tfidf_vectorizer.pkl')
        self.logger.info('TF-IDF vectorization done')

        sample_weights = compute_sample_weight({-1:0.4,0:0.3,1:0.3}, Y_train)
        model = XGBClassifier()
        model.fit(X_train, Y_train, sample_weight=sample_weights)      
            
        self.logger.info('Model Training done\n')

        # Saving XGB model as .pkl file for future use
        joblib_file = f'{self.models_dir}/{self.algo}_senti.pkl'
        joblib.dump(model, joblib_file)

        return model

    # Method to pull data to use for training, used by the SentiCR constructor
    def read_data_from_oracle(self):
        workbook = open_workbook(os.path.join(train_path,"custom_dataset.xls"))
        sheet = workbook.sheet_by_index(0)
        oracle_data = []
        self.logger.info(f"Reading training data from 'train_data/custom_dataset.xls'...")
        for cell_num in range(0, sheet.nrows):
            comments = SentimentData(sheet.cell(
                cell_num, 0).value, sheet.cell(cell_num, 1).value)
            oracle_data.append(comments)
        return oracle_data

    # Method to scrub the data by calling the preprocessing function on line 179, then push the messaging data into the trained model to extract a sentiment score
    def get_sentiment_polarity(self, text, label=False):
        comment = preprocess_text(text)
        feature_vector = self.vectorizer.transform([comment]).toarray()
        sentiment_class = self.model.predict(feature_vector)
        score = np.amax(self.model.predict_proba(feature_vector))
        # self.logger.info(score)
        if not isinstance(sentiment_class, float):
            sentiment_score = score*sentiment_class[0]
            sentiment_class = sentiment_class[0]
        else:
            sentiment_score = score*sentiment_class
        if label:
            return (sentiment_class, sentiment_score)
        return sentiment_score
    
# Function to get sentiment score
# Starting point of the worker, ties the whole file’s code together, outputs the final score.
def get_senti_score(df, col, models_dir, label=False, logger=logging):
    sentiment_analyzer = SentiCR(logger=logger, models_dir=models_dir)
    i = 0
    labels = []
    scores = []
    logger.info('Calculating sentiment scores...')
    while (i < df.shape[0]):
        if label:
            x, y = sentiment_analyzer.get_sentiment_polarity(df.iloc[i][col], label)
            labels.append(x)
            scores.append(y)
        else:
            score = sentiment_analyzer.get_sentiment_polarity(df.iloc[i][col], label)
            scores.append(score)
        i+=1
    scores = np.array(scores)
    labels = np.array(labels)
    if label:
        return (labels,scores)
    return scores
