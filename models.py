from keras.models import Model, Sequential
from keras.layers import Bidirectional, concatenate, Dense, Dropout, Input, LSTM, TimeDistributed
from keras.optimizers import Adam
from keras.utils import plot_model
from keras.layers.embeddings import Embedding
from keras.preprocessing.sequence import pad_sequences
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split


import numpy as np
import tensorflow as tf
import os

import matplotlib.pyplot as plt


class LSTM_Keras:
    def __init__(self, V, D, seq_len, labels_len, n_hidden_rnn = 64, 
                n_hidden_dense = 100, lr = 1e-3,
                optimizer = Adam,
                loss_fun = "categorical_crossentropy"):
        self.V = V
        self.D = D
        self.seq_len = seq_len
        self.labels_len = labels_len + 1
        self.n_hidden_rnn = n_hidden_rnn    
        self.n_hidden_dense = n_hidden_dense    
        self.lr = lr
        self.optimizer = optimizer
        self.loss_fun = loss_fun        
        self._build()


    def _build(self):        
        input_correct_seq = Input(shape = (self.seq_len,))
        input_incorrect_seq = Input(shape = (self.seq_len,))
        input_correct_pos = Input(shape = (self.seq_len, 1))
        input_incorrect_pos = Input(shape = (self.seq_len, 1))
        input_list = [input_correct_seq, input_incorrect_seq, 
                                        input_correct_pos, input_incorrect_pos]
        
        embedding1 = Embedding(self.V, self.D, input_length = self.seq_len)(input_correct_seq)
        lstm1 = Bidirectional(LSTM(self.n_hidden_rnn))(embedding1)
        dense1 = Dense(self.n_hidden_dense, activation = "sigmoid")(lstm1)        
        model1 = Model(inputs = input_correct_seq, outputs = dense1)

        lstm4 = LSTM(self.n_hidden_rnn)(input_incorrect_pos)
        dense4 = Dense(self.n_hidden_dense, activation = "sigmoid")(lstm4)
        model4 = Model(inputs = input_incorrect_pos, outputs = dense4)    

        embedding3 = Embedding(self.V, self.D, input_length = self.seq_len)(input_incorrect_seq)
        lstm3 = Bidirectional(LSTM(self.n_hidden_rnn))(embedding3)
        dense3 = Dense(self.n_hidden_dense, activation = "sigmoid")(lstm3)
        model3 = Model(inputs = input_incorrect_seq, outputs = dense3) 

        lstm2 = LSTM(self.n_hidden_rnn)(input_correct_pos)
        dense2 = Dense(self.n_hidden_dense, activation = "sigmoid")(lstm2)
        model2 = Model(inputs = input_correct_pos, outputs = dense2)    

        combined = concatenate([model1.output, model2.output, model3.output, 
                                model4.output])

        final_dense = Dense(self.n_hidden_dense, activation = "sigmoid")(combined)
        
        preds_incorrect = Dense(self.labels_len, activation = "sigmoid")(final_dense)
        preds_correct = Dense(self.labels_len, activation = "sigmoid")(final_dense)

        output_list = [preds_incorrect, preds_correct]
        model = Model(inputs = input_list, outputs = output_list)
        optimizer = Adam(lr = self.lr)
        model.compile(optimizer = optimizer, loss = self.loss_fun, metrics=['accuracy'])
        self.model = model

    
    def fit(self, X, Y, epochs = 1, batch_sz = 32, validation_split = 0.2, shuffle = True):
        inputs, outputs = self._pad_and_split(X, Y) 
        plot_model(self.model, show_shapes = True, to_file = "model1.png")
        progress = self.model.fit(inputs, outputs, epochs = epochs, batch_size = batch_sz,
                        validation_split = validation_split, shuffle = shuffle)
        self.model.evaluate(inputs, outputs)
        import ipdb; ipdb.set_trace()

    
    def _pad_and_split(self, X, Y):
        X_inc_seq = pad_sequences(X[0], maxlen = self.seq_len, padding = "post",
                        truncating = "post", value = 0)
        # X_inc_seq = X_inc_seq.reshape((*X_inc_seq.shape, 1))
        X_cor_seq = pad_sequences(X[2], maxlen = self.seq_len, padding = "post",
                                truncating = "post", value = 0)
        # X_cor_seq = X_cor_seq.reshape((*X_cor_seq.shape, 1))
        X_inc_text_pos = pad_sequences(X[1], maxlen = self.seq_len, 
                            padding = "post", truncating = "post", value = 0)
        X_inc_text_pos = X_inc_text_pos.reshape((*X_inc_text_pos.shape, 1))
        X_cor_text_pos = pad_sequences(X[3], maxlen = self.seq_len, 
                            padding = "post", truncating = "post", value = 0)
        X_cor_text_pos = X_cor_text_pos.reshape((*X_cor_text_pos.shape, 1))
        inputs = [X_cor_seq, X_inc_seq, X_cor_text_pos, X_inc_text_pos]

        Y_inc_pos = pad_sequences(Y[0], maxlen = self.labels_len, 
                            padding = "post", truncating = "post", value = self.labels_len)
        # Y_inc_pos = Y_inc_pos.reshape((*Y_inc_pos.shape, 1))                  
        Y_cor_pos = pad_sequences(Y[1], maxlen = self.labels_len, 
                            padding = "post", truncating = "post", value = self.labels_len)
        # Y_cor_pos = Y_cor_pos.reshape((*Y_cor_pos.shape, 1))        
        outputs = [Y_inc_pos, Y_cor_pos]       
        return inputs, outputs
