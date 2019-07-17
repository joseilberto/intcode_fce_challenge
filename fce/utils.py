from math import isnan

from .constants import filters, spliters, sep_exclusions, word_exceptions


def initial_instance(filters, spliters):
    word2idx = {
    "": 1, 
    " ": 2,                          
    }
    current_idx = max(word2idx.values()) + 1
    word2idx.update({fil: idx for idx, fil in enumerate(list(filters), 
                        start = current_idx)})                        
    current_idx = max(word2idx.values()) + 1
    word2idx.update({spliter: idx for idx, spliter in enumerate(list(spliters), 
                        start = current_idx)})
    current_idx = max(word2idx.values()) + 1
    return word2idx, current_idx


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
    word2idx, current_idx = initial_instance(filters, spliters)
    original_idx = current_idx
    correct_sentences, correct_text_pos, word2idx, current_idx = (
            get_indexed_sentences(corrects, word2idx, current_idx, filters, spliters))
    incorrect_sentences, incorrect_text_pos, word2idx, current_idx = (
            get_indexed_sentences(incorrects, word2idx, current_idx, filters, spliters))
    incorrect_positions, correct_positions, labels_types, label2idx = (
                                                get_labels(data["labels"]))
    correct_sentences = reindex_sentences(correct_sentences, word2idx, original_idx)
    incorrect_sentences = reindex_sentences(incorrect_sentences, word2idx, original_idx)
    check_position_matches(incorrect_text_pos, correct_text_pos,
                                        incorrect_positions, correct_positions)
    data["correct_indexed"] = correct_sentences
    data["incorrect_indexed"] = incorrect_sentences
    data["correct_text_pos"] = correct_text_pos
    data["incorrect_text_pos"] = incorrect_text_pos
    data["incorrect_positions"] = incorrect_positions
    data["correct_positions"] = correct_positions
    data["labels_types"] = labels_types
    return data, word2idx, label2idx


def reindex_sentences(sentences, word2idx, original_cur_idx):
    unchanged = {key: value for key, value in word2idx.items() if value < original_cur_idx}
    reduced = {key: value for key, value in word2idx.items() if value >= original_cur_idx}
    ordered = sorted(reduced.keys())    
    ordered_word2idx = {key: reduced[key] for key in ordered}
    ordered_word2idx.update(unchanged)
    convert_dict = {word2idx[key]: value for key, value in ordered_word2idx.items()}
    for idx in range(len(sentences)):
        for idx2 in range(len(sentences[idx])):
            sentences[idx][idx2] = convert_dict[sentences[idx][idx2]]            
    return sentences


def check_position_matches(incorrect_text_pos, correct_text_pos,
                                        incorrect_positions, correct_positions):
    for idx, inc_text_pos in enumerate(incorrect_text_pos):
        cor_text_pos = correct_text_pos[idx]
        incor_pos = incorrect_positions[idx]
        cor_pos = correct_positions[idx]
        assert(set(incor_pos).issubset(inc_text_pos))
        assert(set(cor_pos).issubset(cor_text_pos))


def get_indexed_sentences(actual_sentences, word2idx, current_idx, filters, spliters):
    sentences = []
    cum_sizes = []
    for actual_sentence in actual_sentences:        
        sentence = []
        cum_size = [0]
        cumulative = 0        
        sep2 = None
        split_sentence = actual_sentence.split(" ")                        
        updater = [sentence, cumulative, cum_size, word2idx, current_idx]
        for idx, word in enumerate(split_sentence):            
            updater = update_for_word(word, updater, filters, spliters)
            if idx < len(split_sentence) - 1:
                updater = update_data(" ", *updater)
        sentences.append(updater[0])
        cum_sizes.append(updater[2])
        word2idx, current_idx = updater[-2:]
    return sentences, cum_sizes, word2idx, current_idx


def apply_filters(word, filters, recursion = True):    
    for char in filters:
        if word.startswith(char):
            return apply_filters(word[len(char):], filters)
    for char in filters:
        if word.endswith(char):              
            return apply_filters(word[:-len(char)], filters)    
    return word    


def parse_exceptions(word, updater):
    if word == "16.12.2000y":
        updater = update_data("16.12.2000", *updater)
        return update_data("y", *updater)
    typos = large_typo(word, updater[3])
    for typo in typos:
        updater = update_data(typo, *updater)
    return updater


def split_word(word, splited, updater, filters):
    for spliter in splited:
        if spliter in word:
            splits = word.split(spliter)
            if splits[-1] in sep_exclusions:
                compose_word = "-".join(splits[:-1])
                updater = update_data(compose_word, *updater)                
                splits = [splits[-1]]
                updater = update_data(spliter, *updater)
            for idx, sep_word in enumerate(splits):
                updater = split_word(sep_word, splited, updater, filters)
                isolated = apply_filters(sep_word, filters)                                
                updater = update_from_isolated(sep_word, isolated, updater, [], filters)
                if idx < len(splits) - 1:
                    updater = update_data(spliter, *updater)
    return updater


def update_for_word(word, updater, filters, spliters):  
    isolated_word = apply_filters(word, filters)
    splited = [char for char in spliters if char in isolated_word]                   
    updater = update_from_isolated(word, isolated_word, updater, splited, filters)            
    return updater


def update_from_isolated(word, isolated_word, updater, splited, filters):    
    idx_min = word.find(isolated_word)
    idx_max = idx_min + len(isolated_word)
    condition = (idx_max - idx_min == len(word) 
                and not splited 
                and isolated_word not in word_exceptions)
    if condition:                        
        return update_data(word, *updater)
    if idx_min > 0:
        for idx in range(idx_min):
            char = word[idx]
            updater = update_data(char, *updater)
    if not splited:        
        if isolated_word in word_exceptions:
            updater = parse_exceptions(isolated_word, updater)
        else:
            updater = update_data(isolated_word, *updater)
    else:
        updater = split_word(isolated_word, splited, updater, filters)        
    if idx_min + len(isolated_word) < len(word):            
        for idx in range(idx_max, len(word)):
            char = word[idx]
            updater = update_data(char, *updater)
    return updater


def update_data(word, sentence, cumulative, cum_size, word2idx, current_idx):
    if word not in word2idx:
        word2idx[word] = current_idx
        current_idx += 1
    sentence.append(word2idx[word])
    cumulative += len(word)
    cum_size.append(cumulative)
    return sentence, cumulative, cum_size, word2idx, current_idx


def large_typo(isolated_word, word2idx):    
    largest = ""        
    for idx in range(1, len(isolated_word)):
        word = isolated_word[:idx]
        if word in word2idx or word.lower() in word2idx:
            largest = word if len(word) > len(largest) else largest
    
    remainder = isolated_word.replace(largest, "")    
    if remainder in word2idx or remainder.lower() in word2idx:
        idx_largest = isolated_word.find(largest)
        if idx_largest == 0:
            return [largest, remainder]
        else:
            return [remainder, largest]
    elif remainder == ".lf":
        return [largest, ".", "lf"]

        
