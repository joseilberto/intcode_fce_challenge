from math import isnan

from constants import filters, spliters


def get_labels(labels_dict):
    incorrect_positions = []
    correct_positions = []
    labels_types = []
    label2idx = {}
    current_idx = 0
    for label_dict in labels_dict:
        if isinstance(label_dict, float):
            incorrect_positions.append([])
            correct_positions.append([])
            labels_types.append([])
            continue
        incorrect = []
        correct = []
        types = []
        for mistake in eval(label_dict):            
            incorrect.append(mistake["incorrect_position"])            
            correct.append(mistake["correct_position"])
            mistake_type = mistake["type"]
            if mistake_type not in label2idx:
                label2idx[mistake_type] = current_idx
                current_idx += 1
            types.append(label2idx[mistake_type])
        incorrect_positions.append(incorrect)
        correct_positions.append(correct)
        labels_types.append(types)
    return incorrect_positions, correct_positions, labels_types, label2idx        


def get_indices(data, filters = filters, spliters = spliters):       
    corrects = data["correct_sentence"].tolist()
    incorrects = data["incorrect_sentence"].tolist()
    word2idx = {
        "": 0, 
        " ": 1, 
        "-": 2,                       
        }
    current_idx = max(word2idx.values()) + 1
    word2idx.update({fil: idx for idx, fil in enumerate(list(filters), 
                        start = current_idx)})
    current_idx = max(word2idx.values()) + 1
    correct_sentences, correct_text_pos, word2idx, current_idx = (
            get_indexed_sentences(corrects, word2idx, current_idx, filters, spliters))
    incorrect_sentences, incorrect_text_pos, word2idx, current_idx = (
            get_indexed_sentences(incorrects, word2idx, current_idx, filters, spliters))
    incorrect_positions, correct_positions, labels_types, label2idx = (
                                                get_labels(data["labels"]))
    data["correct_indexed"] = correct_sentences
    data["incorrect_indexed"] = incorrect_sentences
    data["correct_text_pos"] = correct_text_pos
    data["incorrect_text_pos"] = incorrect_text_pos
    data["incorrect_positions"] = incorrect_positions
    data["correct_positions"] = correct_positions
    data["labels_types"] = labels_types
    return data, word2idx, label2idx


def get_indexed_sentences(actual_sentences, word2idx, current_idx, filters, spliters):
    sentences = []
    cum_sizes = []
    for actual_sentence in actual_sentences:        
        sentence = []
        cum_size = [0]
        cumulative = 0        
        sep2 = None
        split_sentence = actual_sentence.split(" ")                        
        updater = [sentence, cumulative, cum_size]
        for idx, word in enumerate(split_sentence):
            if word == "":
                updater = update_data(word2idx[" "], *updater)
            updater, word2idx, current_idx = update_for_word(word, word2idx, 
                                        current_idx, updater, filters, spliters)
        sentences.append(updater[0])
        cum_sizes.append(updater[-1])
    return sentences, cum_sizes, word2idx, current_idx


def apply_filters(word, filters, recursion = True):    
    for char in filters:
        if word.startswith(char):
            return apply_filter(word[1:], filters)
    for char in filters:
        if word.endswith(char):
            return apply_filter(word[:-1], filters)
    return word    


    # for char in filters:
    #     if word == "p.m" or word == "a.m":
    #         break
    #     word = word.replace(char, "")        
    # return word


def check_split(word, spliters):
    for char in spliters:
        if char in word:
            return sep    


def update_for_word(word, word2idx, current_idx, updater, filters, spliters):            
    actual_word = apply_filters(word, filters)
    spliter = check_split(actual_word, spliters)
    if not spliter:
        idx_min = word.find(actual_word)
        idx_max = idx_min + len(actual_word)
        
    

def update_data(idx, sentence, cumulative, cum_size, length = 1):
    sentence.append(idx)
    cumulative += length
    cum_size.append(cumulative)
    return sentence, cumulative, cum_size

# def get_indexed_sentences(actual_sentences, word2idx, current_idx, filters):
#     sentences = []
#     cum_sizes = []
#     for actual_sentence in actual_sentences:        
#         sentence = []
#         cum_size = [0]
#         cumulative = 0        
#         sep2 = None
#         split_sentence = actual_sentence.split(" ")                        
#         for idx, word in enumerate(split_sentence):
#             if word == "":
#                 sentence.append(word2idx[" "])
#                 cumulative += 1
#                 cum_size.append(cumulative)
#                 continue
#             word, sep = filtered_word(word, filters)
#             if word.startswith('"') or word.startswith("'") or word.startswith("("):                    
#                 sentence.append(word2idx[word[0]])
#                 word = word[1:]
#                 cumulative += 1
#                 cum_size.append(cumulative)
#             if word.startswith(";"):
#                 sentence.append(word2idx[word[0]])
#                 word = word[1:]
#                 cumulative += 1
#                 cum_size.append(cumulative)
#             original_word = word
#             if word.endswith('"') or word.endswith("'") or word.endswith(")"):                
#                 word = word[:-1]
#                 word, sep2 = filtered_word(word, filters)
#             if "/" in word:
#                 splits = word.split("/")
#                 for idx, wrd in enumerate(splits):
#                     if wrd not in word2idx:
#                         word2idx[wrd] = current_idx
#                         current_idx += 1
#                     sentence.append(word2idx[wrd])
#                     cumulative += len(wrd)
#                     cum_size.append(cumulative)
#                     if idx < len(splits) - 1:
#                         sentence.append(word2idx["/"])
#                         cumulative += 1
#                         cum_size.append(cumulative)
#             elif word == "p.m." or word == "a.m.":
#                 if word[:-1] not in word2idx:
#                     word2idx[word[:-1]] = current_idx
#                     current_idx += 1
#                 sentence.append(word2idx[word[:-1]])
#                 cumulative += len(word[:-1])
#                 cum_size.append(cumulative)
#                 sentence.append(word2idx["."])
#                 cumulative += 1            
#                 cum_size.append(cumulative)          
#             else:
#                 if word not in word2idx:                
#                     word2idx[word] = current_idx
#                     current_idx += 1
#                 sentence.append(word2idx[word])
#                 cumulative += len(word)
#                 cum_size.append(cumulative)
#             if original_word.endswith('"') or original_word.endswith("'") or original_word.endswith(")"):
#                 if sep2:
#                     sentence.append(word2idx[sep2])
#                     cumulative += 1
#                     cum_size.append(cumulative)
#                 sentence.append(word2idx[original_word[-1]])
#                 cumulative += 1
#                 cum_size.append(cumulative)    
#             if sep:
#                 sentence.append(word2idx[sep])
#                 cumulative += 1
#                 cum_size.append(cumulative)
#             if idx < len(split_sentence) - 1:
#                 sentence.append(word2idx[" "])
#                 cumulative += 1            
#                 cum_size.append(cumulative)
#             elif idx == (len(split_sentence) - 1) and not sep:
#                 sentence.append(word2idx[""])
#                 cumulative += 1
#                 cum_size.append(cumulative)
#         sentences.append(sentence)
#         cum_sizes.append(cum_size[:-1])
#     return sentences, cum_sizes, word2idx, current_idx


def max_in_seqs(data, columns, param = "length"):
    if "length" in param:
        fun = len
    elif "maximum" in param:
        fun = max
    max_len1 = max([fun(cur_data) if cur_data else 0 for cur_data in data[columns[0]].tolist()])
    max_len2 = max([fun(cur_data) if cur_data else 0 for cur_data in data[columns[1]].tolist()])    
    return max(max_len1, max_len2)



