from difflib import SequenceMatcher

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

    incor_pos_found = []
    cor_pos_found = []
    found_corrects = []
    for idx in range(len(incorrect_idxs)):
        incorrect_sentence = incorrect_idxs[idx]
        correct_sentence = correct_idxs[idx]
        incor_text_pos = incorrect_text_pos[idx]
        cor_text_pos = correct_text_pos[idx]
        found_data = get_correct_sentence(correct_sentence, incorrect_sentence,
                                            cor_text_pos, incor_text_pos)
        incor_pos_found.append(found_data[0])
        cor_pos_found.append(found_data[1])
    
    incor_acc = 0
    cor_acc = 0
    for idx, correct_pos in enumerate(correct_positions):
        incorrect_pos = incorrect_positions[idx]
        cors_found = cor_pos_found[idx]
        incors_found = incor_pos_found[idx]    
        incor_intersection = [idx for idx in incorrect_pos if idx in incors_found]
        cor_intersection = [idx for idx in correct_pos if idx in cors_found]
        incor_acc += len(incor_intersection) / len(incorrect_pos)
        cor_acc += len(cor_intersection) / len(correct_pos)
    print("Incorrect accuracy: ", incor_acc / len(correct_positions))
    print("Correct accuracy: ", cor_acc / len(correct_positions))


def get_correct_sentence(cor, incor, cor_text_pos, incor_text_pos):
    incor_position = []
    cor_position = []
    found_correct = []
    if incor[0] != cor[0]:
        incor_position.append(0)
        cor_position.append(0)
        incor = incor[1:]
        cor = cor[1:]
    matches = SequenceMatcher(None, incor, cor, autojunk = False).get_matching_blocks()
    for match in matches[:-1]:
        idx_incor, idx_cor, size = match.a, match.b, match.size                  
        incor_position.append(incor_text_pos[idx_incor + size])
        cor_position.append(cor_text_pos[idx_cor + size])
    incor_position = (incor_position[:-1] if len(incor_position) > 1 
                        else incor_position)
    cor_position = (cor_position[:-1] if len(cor_position) > 1
                        else cor_position) 
    return incor_position, cor_position
