def get_indices(data, filters = (",", ".", "!", "?", ";", ":")):       
    corrects = data["correct_sentence"].tolist()
    incorrects = data["incorrect_sentence"].tolist()
    word2idx = {" ": 0, "-": 1}
    word2idx.update({fil: idx for idx, fil in enumerate(list(filters), start = 2)})
    current_idx = max(word2idx.values()) + 1
    correct_sentences, word2idx, current_idx = get_indexed_sentences(corrects, 
                                            word2idx, current_idx, filters)
    incorrect_sentences, word2idx, current_idx = get_indexed_sentences(incorrects, 
                                            word2idx, current_idx, filters)
    data["correct_indexed"] = correct_sentences
    data["incorrect_indexed"] = incorrect_sentences
    return data, word2idx


def get_indexed_sentences(actual_sentences, word2idx, current_idx, filters):
    sentences = []
    for actual_sentence in actual_sentences:        
        sentence = []        
        split_sentence = actual_sentence.split()        
        for word in split_sentence:
            word, sep = filtered_word(word, filters)
            if word not in word2idx:
                word2idx[word] = current_idx
                current_idx += 1
            sentence.append(current_idx - 1)
            if sep:
                sentence.append(word2idx[sep])
            sentence.append(0)
        sentences.append(sentence)
    return sentences, word2idx, current_idx


def filtered_word(word, filters):
    sep = None            
    for fil in filters:
        if word.endswith(fil):
            word = word.replace(fil, "")
            sep = fil
            break
    return word, sep