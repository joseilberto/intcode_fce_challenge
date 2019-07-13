import pandas as pd

from pipelines import get_correct_positions
from utils import get_indices, max_in_seqs


if __name__ == "__main__":
    data_file = "./data/data.csv"        
    data = pd.read_csv(data_file)          
    data.dropna(subset = ["correct_sentence", "incorrect_sentence"], inplace = True)  
    data, word2idx, label2idx = get_indices(data)
    max_len_seq = max_in_seqs(data, ["correct_indexed", "incorrect_indexed"])        
    train = data[data["test"] == 0]
    correct_positions = get_correct_positions(train, word2idx, label2idx)
    test = data[data["test"] == 1]

    