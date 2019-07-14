import pandas as pd

from fce.pipelines import get_correct_positions
from fce.utils import get_indices


if __name__ == "__main__":
    data_file = "./data/data.csv"        
    data = pd.read_csv(data_file)          
    data.dropna(subset = ["correct_sentence", "incorrect_sentence"], inplace = True)  
    data, word2idx, label2idx = get_indices(data)            
    train = data[data["test"] == 0]
    correct_positions = get_correct_positions(train, word2idx, label2idx)
    test = data[data["test"] == 1]

    