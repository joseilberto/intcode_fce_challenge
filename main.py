import os
import pandas as pd
import tensorflow as tf

from models import LSTM_Keras
from utils import get_indices, max_in_seqs

os.environ['CUDA_VISIBLE_DEVICES'] = ''

def train_model(model_type, train, test, max_len_seq, max_len_pos, word2idx, label2idx, V, D):    
    Xtrain = [train["incorrect_indexed"], train["incorrect_text_pos"], 
                   train["correct_indexed"], train["correct_text_pos"]]
    Ytrain = [train["incorrect_positions"], train["correct_positions"]]
    labels_train = train["labels_types"]
    model = model_type(V, D, max_len_seq, max_len_pos)
    model.fit(Xtrain, Ytrain)


if __name__ == "__main__":
    data_file = "./data/data.csv"        
    data = pd.read_csv(data_file)          
    data.dropna(subset = ["correct_sentence", "incorrect_sentence"], inplace = True)  
    data, word2idx, label2idx = get_indices(data)
    V, D = len(word2idx), 100
    max_len_seq = max_in_seqs(data, ["correct_indexed", "incorrect_indexed"])    
    max_len_pos = max_in_seqs(data, 
                ["correct_positions", "incorrect_positions"], param = "maximum")  
    train = data[data["test"] == 0]
    test = data[data["test"] == 1]
    train_model(LSTM_Keras, train, test, max_len_seq, max_len_pos, word2idx, 
                label2idx, V, D)
    