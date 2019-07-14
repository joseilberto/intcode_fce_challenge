import numpy as np

def get_correct_positions(data, word2idx, label2idx):
    idx2word = {value: key for key, value in word2idx.items()}
    incorrect_sentences = data["incorrect_sentence"].tolist()
    correct_sentences = data["correct_sentence"].tolist()

    incorrect_idxs = data["incorrect_indexed"].tolist()
    correct_idxs = data["correct_indexed"].tolist()

    incorrect_text_pos = data["incorrect_text_pos"].tolist()
    correct_text_pos = data["correct_text_pos"].tolist()

    incorrect_positions = data["incorrect_positions"].tolist() #delete when done
    correct_positions = data["correct_positions"].tolist() #delete when done
           
    for idx, inc_text_pos in enumerate(incorrect_text_pos):
        cor_text_pos = correct_text_pos[idx]
        incor_pos = incorrect_positions[idx]
        cor_pos = correct_positions[idx]
        assert(set(incor_pos).issubset(inc_text_pos))
        assert(set(cor_pos).issubset(cor_text_pos))            

    incor_positions = []
    cor_positions = []
    found_corrects = []
    for idx, sentence in enumerate(incorrect_idxs):
        correct = correct_idxs[idx]        
        found_correct_sentence = []
        for idx2, word in enumerate(sentence):
            correct_word = correct[idx2]
            if word == correct_word:
                found_correct_sentence.append(idx2word[correct_word]) 
                continue
            else:
                max_idx = max(idx2 + 10, len(correct))
                context = [correct[i] for i in range(idx2, max_idx)]
                for idx_context, context_word in enumerate(context):
                    continue

