from sklearn.model_selection import KFold
from sklearn.externals import joblib
from sklearn.utils import compute_sample_weight

import random
import csv
import re
import sys
import string
import os
import emoji

import nltk
from xlrd import open_workbook
from statistics import mean
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
from imblearn.over_sampling import SVMSMOTE

import warnings
warnings.filterwarnings('ignore')

CONTRACTION_MAP = {
    "ain't": "is not",
    "aren't": "are not",
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'd've": "he would have",
    "he'll": "he will",
    "he'll've": "he he will have",
    "he's": "he is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how is",
    "I'd": "I would",
    "I'd've": "I would have",
    "I'll": "I will",
    "I'll've": "I will have",
    "I'm": "I am",
    "I've": "I have",
    "i'd": "i would",
    "i'd've": "i would have",
    "i'll": "i will",
    "i'll've": "i will have",
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it'd": "it would",
    "it'd've": "it would have",
    "it'll": "it will",
    "it'll've": "it will have",
    "it's": "it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she would",
    "she'd've": "she would have",
    "she'll": "she will",
    "she'll've": "she will have",
    "she's": "she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so as",
    "that'd": "that would",
    "that'd've": "that would have",
    "that's": "that is",
    "there'd": "there would",
    "there'd've": "there would have",
    "there's": "there is",
    "they'd": "they would",
    "they'd've": "they would have",
    "they'll": "they will",
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what will",
    "what'll've": "what will have",
    "what're": "what are",
    "what's": "what is",
    "what've": "what have",
    "when's": "when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where is",
    "where've": "where have",
    "who'll": "who will",
    "who'll've": "who will have",
    "who's": "who is",
    "who've": "who have",
    "why's": "why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you would",
    "you'd've": "you would have",
    "you'll": "you will",
    "you'll've": "you will have",
    "you're": "you are",
    "you've": "you have"
}


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

# Read in the words with sentiment from the dictionary
with open("EmoticonLookupTable.txt","r") as emotable:
    emoticon_reader=csv.reader(emotable,delimiter='\t')

    #Hash words from dictionary with their values
    emodict={rows[0]:rows[1] for rows in emoticon_reader}
    emotable.close()


grammar = r"""
NegP: {<VERB>?<ADV>+<VERB|ADJ>?<PRT|ADV><VERB>}
{<VERB>?<ADV>+<VERB|ADJ>*<ADP|DET>?<ADJ>?<NOUN>?<ADV>?}
"""
chunk_parser = nltk.RegexpParser(grammar)


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


def remove_url(s):
    url_regex = re.compile(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_regex.sub(" ", s)


negation_words = ['not', 'never', 'none', 'nobody', 'nowhere', 'neither', 'barely', 'hardly',
                  'nothing', 'rarely', 'seldom', 'despite']
emoticon_words = ['PositiveSentiment', 'NegativeSentiment']


def remove_tags(s):
    soup = BeautifulSoup(s, "html.parser")
    for tag in soup.find_all('strong'):
        tag.replaceWith('')
        s = soup.get_text()
    return s


def joint_words(s):
    punc = list(string.punctuation)
    s = re.sub('[\.\-\_\\/&]', ' ', s)
    s = "".join([word.lower() for word in s if word not in punc])
    s = word_tokenize(s)
    s = " ".join([word for word in s if len(word) <= 30])
    s = re.sub('[0-9]+', '', s)
    s = re.sub('lgtm', 'look good', s)
    return s


def negated(input_words):
    # Determine if input contains negation words
    neg_words = []
    neg_words.extend(negation_words)
    for word in neg_words:
        if word in input_words:
            return True
    return False


def prepend_not(word):
    if word in emoticon_words:
        return word
    elif word in negation_words:
        return word
    return "NOT_"+word


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
    # print(text)
    return text


class SentimentData:
    def __init__(self, text, rating):
        self.text = text
        self.rating = rating


class SentiCR:
    def __init__(self, algo="GBT", training_data=None):
        self.algo = algo
        if training_data is None:
            if os.path.exists('{algo}_senti.pkl'.format(algo=self.algo)):
                print('Using existing trained Model')
                self.model = joblib.load(
                    '{algo}_senti.pkl'.format(algo=self.algo))
                self.vectorizer = joblib.load('tfidf_vectorizer.pkl')
            else:
                print('Using default train set')
                self.training_data = self.read_data_from_oracle()
                self.model = self.create_model_from_training_data()

        else:
            self.training_data = training_data
            print('Using custom train set')
            self.model = self.create_model_from_training_data()

    def create_model_from_training_data(self):
        training_comments = []
        training_ratings = []

        print("Training classifier model..")
        for sentidata in self.training_data:
            comments = preprocess_text(sentidata.text)
            training_comments.append(comments)
            training_ratings.append(sentidata.rating)
        print('Preprocessing done')

        # discard stopwords, apply stemming, and discard words present in less than 3 comments
        self.vectorizer = TfidfVectorizer(tokenizer=tokenize_and_stem, sublinear_tf=True, max_df=0.5,
                                          stop_words=mystop_words, min_df=3)
        # Saving vectors as .pkl file
        X_train = self.vectorizer.fit_transform(training_comments).toarray()
        Y_train = np.array(training_ratings)
        joblib.dump(self.vectorizer, 'tfidf_vectorizer.pkl')
        print('Tfidf done')

        # Apply SMOTE to improve ratio of the minority class if needed
        '''smote_model = SVMSMOTE(sampling_strategy={-1:0.3,0:0.4,1:0.3}, random_state=None, k_neighbors=15, m_neighbors=15, out_step=.0001, svm_estimator=None, n_jobs=1)
        X_resampled, Y_resampled=smote_model.fit_sample(X_train, Y_train)'''

        if self.algo == "GBT":
            model = GradientBoostingClassifier()
            model.fit(X_train, Y_train)
        elif self.algo == "XGB":
            sample_weight = compute_sample_weight({-1:0.4,0:0.3,1:0.3}, Y_train)
            model = XGBClassifier()
            model.fit(X_train, Y_train, sample_weight=sample_weight)
       
        print('Training done')

        # Saving model as .pkl file
        joblib_file = "{algo}_senti.pkl".format(algo=self.algo)
        joblib.dump(model, joblib_file)

        return model

    def read_data_from_oracle(self):
        workbook = open_workbook("mod_train.xlsx")
        sheet = workbook.sheet_by_index(0)
        oracle_data = []
        print("Reading data from oracle db..")
        for cell_num in range(0, sheet.nrows):
            comments = SentimentData(sheet.cell(
                cell_num, 0).value, sheet.cell(cell_num, 1).value)
            oracle_data.append(comments)
        return oracle_data

    def get_sentiment_polarity(self, text, labels=False):
        comment = preprocess_text(text)
        feature_vector = self.vectorizer.transform([comment]).toarray()
        sentiment_class = self.model.predict(feature_vector)
        score = np.amax(self.model.predict_proba(feature_vector))
        # print(sentiment_class, sentiment_score)
        if not isinstance(sentiment_class, float):
            sentiment_score = score*sentiment_class[0]
            sentiment_class = sentiment_class[0]
        else:
            sentiment_score = score*sentiment_class
        if labels:
            return (sentiment_class, sentiment_score)
        return sentiment_score