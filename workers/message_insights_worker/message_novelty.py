import logging
import multiprocessing
import os
from datetime import date

import numpy as np
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from keras.layers import Dense, Input
from keras.models import Model, load_model
from scipy.spatial.distance import cosine
from skimage.filters import threshold_otsu
from sklearn import utils as skl_utils

from augur import ROOT_AUGUR_DIRECTORY
from workers.message_insights_worker.preprocess_text import \
    normalize_corpus as normalize_corpus

train_path = os.path.join(ROOT_AUGUR_DIRECTORY, "workers", "message_insights_worker", "train_data")

''' Doc2Vec model training

def build_model(max_epochs, vec_size, alpha, tag_data):    
    model = Doc2Vec(vector_size=vec_size, alpha=alpha,min_alpha=0.00025, min_count=2, dm=1)
    model.build_vocab(tag_data)

    for epoch in range(max_epochs):
        model.train(skl_utils.shuffle(tag_data),
                   total_examples=model.corpus_count,
                   epochs=model.epochs)

        model.alpha -= 0.0002
        model.min_alpha = model.alpha

    model.save("doc2vec.model")
    print("Model Saved")
    return model
'''

def autoencoder(vec_input, train):
    input_dim = Input(shape = (vec_input, ))
    encoded1 = Dense(vec_input//2, activation='sigmoid')(input_dim)
    encoded2 = Dense(1, activation='sigmoid')(encoded1)

    # Decoder Layers
    decoded1 = Dense(vec_input//2, activation='tanh')(encoded2)
    decoded2 = Dense(vec_input, activation='tanh')(decoded1)

    # Combine Encoder and Deocder layers
    model = Model(inputs = input_dim, outputs = decoded2)

    # Compile the Model
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mean_squared_error'])
    model.fit(train, train, epochs = 20)
    return model

def reconstruction(pred, val):
    rec_error = []
    for i in range(len(pred)):
        rec_error.append(np.linalg.norm(pred[i] - val[i]))
    rec_error = np.array(rec_error)
    return rec_error

def get_normal_data(rec_error, val):
    # otsu thresholding corresponding to the maximum value of between two class variances
    threshold = threshold_otsu(rec_error)
    normals = []
    for i in range(len(rec_error)):
        if rec_error[i] < threshold:
            normals.append(val[i])
    normals = np.array(normals)
    return threshold, normals

''' Cosine similarity based novel detection

def key_cosine_similarity(tupple):
    return tupple[1]

def get_computed_similarities(df_present, vectors, predicted_vectors, reverse=False):
    data_size = len(df_present)
    cosine_similarities = []
    cosine_sim_values = []
    for i in range(data_size):
        cosine_sim_val = (1 - cosine(vectors[i], predicted_vectors[i]))
        cosine_similarities.append((df_present['msg_id'].iloc[i], cosine_sim_val))
        cosine_sim_values.append(cosine_sim_val)

    df_present['uniqueness_score'] = cosine_sim_values
    return df_present, sorted(cosine_similarities, key=key_cosine_similarity, reverse=reverse)

def display_unique(sorted_cosine_similarities):
    i=0
    unique_message_list=[]
    cos_val = []
    index, cosine_sim_val = sorted_cosine_similarities[0]
    while cosine_sim_val<=-0.1:
        if cosine_sim_val not in cos_val:
            unique_message_list.append(index)
            cos_val.append(cosine_sim_val)
            print('Message id: ', index)  
            print('Cosine Sim Val :', cosine_sim_val)
        i+=1    
        index, cosine_sim_val = sorted_cosine_similarities[i]
        
    return unique_message_list
'''

def novelty_analysis(df_message, r_id, models_dir, full_train, logger=logging):
    # Normlize text corpus
    df_message['cleaned_msg_text'] = df_message['msg_text'].map(lambda x: normalize_corpus(x))
    logger.info('Normalized text corpus')

    # Load pretrained Doc2Vec model
    d2v_model = Doc2Vec.load(os.path.join(train_path,"doc2vec.model"))
    doc2vec_vectors = np.array([d2v_model.infer_vector(str(row['cleaned_msg_text']).split())for index, row in df_message.iterrows()])
    logger.info('Doc2Vec vectorization done')

    # Trains the AE model when worker runs first time
    if full_train:
    
        # First autoencoder to identify normal data records
        ae1 = autoencoder(250, doc2vec_vectors)
        logger.info('AE 1 training done')
        pred_train = ae1.predict(doc2vec_vectors)
        _rec_error1 = reconstruction(pred_train, doc2vec_vectors)
        _, normal_data = get_normal_data(_rec_error1, doc2vec_vectors)

        # Second autoencoder to decide threshold using otsu
        ae = autoencoder(250, normal_data)
        logger.info('AE 2 training done')
        predicted_vectors = ae.predict(doc2vec_vectors)
        rec_error = reconstruction(predicted_vectors, doc2vec_vectors)
        threshold, _ = get_normal_data(rec_error, doc2vec_vectors)

        # Save final model for future
        ae.save(f'{models_dir}/{r_id}_uniq.h5')

    # Pretrained AE model already exists, directly predict
    else:
        threshold = 0
        ae = load_model(f'{models_dir}/{r_id}_uniq.h5')
        logger.info('Loaded pretrained AE model for repo')

        # Fitting on present data
        predicted_vectors_test = ae.predict(doc2vec_vectors)
        rec_error = reconstruction(predicted_vectors_test, doc2vec_vectors)

    return (threshold, np.array(rec_error))
