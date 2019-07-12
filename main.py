from keras.preprocessing.text import one_hot

import pandas as pd

from models import LSTM_Autoencoder
from utils import get_indices


def train_model(model_type, train, test, max_len_seq, word2idx, V, D):    
    incorrect_train = train["incorrect_indexed"]
    correct_train = train["correct_indexed"]
    labels_train = train["labels"]

    incorrect_test = test["incorrect_indexed"]
    correct_test = test["correct_indexed"]
    labels_test = test["labels"]

    model = model_type(V, D, max_len_seq)    
    model.fit(incorrect_train, correct_train)


if __name__ == "__main__":
    data_file = "./data/data.csv"    
    data = pd.read_csv(data_file)      
    left_out = data[(data["correct_sentence"].isna()) | 
                    (data["incorrect_sentence"].isna())] # Work if time allows     
    data = data.dropna(subset = ["correct_sentence", "incorrect_sentence"])  
    data, word2idx = get_indices(data)
    V, D = len(word2idx), 100
    max_len_correct = max([len(sentence) 
                            for sentence in data["correct_indexed"].tolist()])
    max_len_incorrect = max([len(sentence) 
                            for sentence in data["incorrect_indexed"].tolist()])
    max_len_seq = max(int(max_len_correct*1.1), int(max_len_incorrect*1.1))
    train = data[data["test"] == 0]
    test = data[data["test"] == 1]
    train_model(LSTM_Autoencoder, train, test, max_len_seq, word2idx, V, D)
    