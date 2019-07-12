from keras.models import Sequential, Model
from keras.layers import Dense, Embedding, Input, LSTM, RepeatVector, TimeDistributed, Reshape
from keras.optimizers import Adam, SGD, RMSprop
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.utils import plot_model

import matplotlib.pyplot as plt



class LSTM_Autoencoder:
    def __init__(self, V, D, seq_len,
                n_hidden = 128, 
                activation = "sigmoid", 
                lr = 1e-3,
                optimizer = SGD,
                loss_fun = "categorical_crossentropy"):
        self.V = V
        self.D = D
        self.seq_len = seq_len
        self.n_hidden = n_hidden
        self.activation = activation
        self.lr = lr
        self.optimizer = optimizer
        self.loss_fun = loss_fun
        self._build()

    
    def _build(self):
        model = Sequential()
        model.add(Embedding(self.V, self.D, input_length = self.seq_len))
        model.add(LSTM(self.n_hidden, activation = self.activation, 
              input_shape = (self.seq_len, self.D)))        
        model.add(RepeatVector(self.seq_len))                                     
        model.add(LSTM(self.n_hidden, activation = self.activation, 
                                        return_sequences = True))
        model.add(TimeDistributed(Dense(self.V, activation = "softmax")))
        optimizer = self.optimizer(lr = self.lr, clipnorm = 0.2)
        model.compile(optimizer = optimizer, loss = self.loss_fun, 
                                    metrics=['accuracy'])
        self.model = model
    

    def fit(self, X, Y, epochs = 1, batch_size = 16, validation_split = 0.2, shuffle = True):
        X = pad_sequences(X, maxlen = self.seq_len, padding = "post", 
                            truncating = "post")
        Y = pad_sequences(Y, maxlen = self.seq_len, padding = "post", 
                            truncating = "post")                     
        plot_model(self.model, show_shapes = True, to_file = "LSTM_shape2.png")   
        progress = self.model.fit(X_in, Y_in, epochs = epochs, batch_size = batch_size, 
                    validation_split = validation_split, shuffle = shuffle)
        plt.plot(progress.history['acc'], label='acc')
        plt.plot(progress.history['val_acc'], label='val_acc')
        plt.show()
        