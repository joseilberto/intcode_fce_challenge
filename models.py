from sklearn.utils import shuffle
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

import numpy as np
import tensorflow as tf
import os

import matplotlib.pyplot as plt


class LSTM_Autoencoder:
    def __init__(self, V, D, seq_len, n_hidden = 64, lr = 1e-4,
                optimizer = tf.train.AdamOptimizer,
                loss_fun = tf.nn.sampled_softmax_loss):
        self.V = V
        self.D = D
        self.seq_len = seq_len
        self.n_hidden = n_hidden        
        self.lr = lr
        self.optimizer = optimizer
        self.loss_fun = loss_fun        
        self._build()

    
    def _build(self):
        V = self.V
        M1 = self.D
        M2 = self.n_hidden
        activation = tf.nn.tanh
                
        self.W0 = tf.Variable(tf.random.normal((M2, V)) / np.sqrt(M2 + V))
        self.h0 = tf.Variable(tf.zeros(V))

        self.weights_embedding = tf.Variable(tf.random.normal((V, M1)) 
                                                / np.sqrt(V + M1))
        self.tfX = tf.placeholder(tf.int32, shape = (None, self.seq_len), name = "X")
        self.tfY = tf.placeholder(tf.int32, shape = (None, self.seq_len), name = "Y")
        self.learning_rate = tf.placeholder(tf.float32, shape = [], name = "LR")

        embedded = tf.nn.embedding_lookup(self.weights_embedding, self.tfX)
        rnn_unit1 = tf.nn.rnn_cell.LSTMCell(num_units = M2, activation = activation)                 
        outputs, states = tf.nn.dynamic_rnn(rnn_unit1, embedded, dtype = tf.float32)           
        multi = tf.reshape(tf.matmul(tf.reshape(outputs, [-1, M2]), self.W0), 
                            [-1, self.seq_len, self.V])     
        self.logits = multi + self.h0        
        self.outputs = tf.nn.softmax(self.logits)
        self.predict_op = tf.argmax(self.logits, 1)
        nce_weights = tf.transpose(self.W0)
        nce_biases = self.h0
        inputs = tf.reshape(outputs, (-1, M2))
        labels = tf.reshape(self.tfY, (-1, 1))
        self.cost = tf.reduce_mean(self.loss_fun(
                weights = nce_weights,
                biases = nce_biases,
                labels = labels,
                inputs = inputs,
                num_sampled = 100,
                num_classes = V
            ))
        self.train_op = self.optimizer(self.lr).minimize(self.cost)
    

    def fit(self, X, Y, epochs = 200, batch_size = 32, validation_split = 0.2, 
            show_fig = True):
        X = pad_sequences(X, maxlen = self.seq_len, padding = "post", 
                            truncating = "post")
        Y = pad_sequences(Y, maxlen = self.seq_len, padding = "post", 
                            truncating = "post")
        init = tf.global_variables_initializer()
        self.saver = tf.train.Saver()
        self.session.run(init)        
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, 
                                test_size = validation_split)
        n_batches = X_train.shape[0] // batch_size
        costs = []
        for epoch in range(epochs):
            X_train, Y_train = shuffle(X_train, Y_train)            
            n_correct = 0
            cost = 0
            for i in range(n_batches):
                x_batch = X_train[i*batch_size:(i+1)*batch_size]
                y_batch = Y_train[i*batch_size:(i+1)*batch_size]                
                c, _ = self.session.run((self.cost, self.train_op),
                    feed_dict = {
                        self.tfX: x_batch,
                        self.tfY: y_batch,
                        self.learning_rate: self.lr,
                    })
                cost += c
                if i % 50 == 0:
                    print("Epoch: {}/{}\t Batch: {}/{}\t Current cost per batch: {}".format(epoch + 1, epochs, i, n_batches, c))
                costs.append(cost)
        cur_score = self.score(X_train, Y_train)
        val_score = self.score(X_test, Y_test)
        print("Epoch: {}/{}\t Train/validation scores: {:.2f}/{:.2f}".format(
                                            epoch, epochs, cur_score, val_score))
        if show_fig:
            plt.plot(costs)
            plt.show()

    
    def score(self, X, Y, chunk_size = 128):
        accuracy = 0
        calculated = 0
        n_chunks = X.shape[0] // chunk_size
        for i in range(n_chunks):
            x_chunk = X[i*chunk_size:(i+1)*chunk_size]
            y_chunk = Y[i*chunk_size:(i+1)*chunk_size]
            if not np.any(x_chunk):
                continue
            preds = np.argmax(self.session.run(self.outputs, 
                        feed_dict = {self.tfX: x_chunk}), axis = 2)
            accuracy += np.mean(preds == y_chunk)
            calculated += 1
        return accuracy / calculated

    def set_session(self, session, *args, **kwargs):
        self.session = session


    def save_model(self, savefile, *args, **kwargs):
        self.saver.save(self.session, savefile)


    def load_model(self, savefile, *args, **kwargs):
        self._build()
        self.saver = tf.train.Saver()
        self.saver.restore(self.session, savefile)
        
        