from curses.ascii import isalpha, isdigit
from plistlib import InvalidFileException
import sys
import os
import numpy as np
from tensorflow import keras
import pandas as pd
import matplotlib.pyplot as plt

from Bill import Bill

def make_model(size):
    """
    Uses Keras to create a neural network classifier of words
    """
    model = keras.models.Sequential()
    model.add(keras.Input(shape=(size,)))
    model.add(keras.layers.Dense(128,activation="relu"))
    model.add(keras.layers.Dropout(0.3))
    model.add(keras.layers.Dense(64,activation="relu"))
    model.add(keras.layers.Dropout(0.3))
    model.add(keras.layers.Dense(16,activation="tanh"))
    model.add(keras.layers.Dense(3,activation="softmax"))

    model.build()

    model.summary()

    model.compile(loss = "binary_crossentropy",optimizer="adam",metrics=["accuracy"])

    return model

from Bill import Bill, CongressPerson

def make_bills(folder:str):
    bill_locations = os.listdir(folder)
    bill_locations = list(map(lambda loc:folder + '/' + loc, bill_locations))
    bills = []
    for bill_file in bill_locations:
        if bill_file[-3:] == 'txt':
            try:
                current_bill = Bill(bill_file)
                if current_bill.party != 'N/A':
                    bills.append(current_bill)
            except InvalidFileException as e:
                continue
    return bills, bill_locations

def to_word_vector(translator:dict, bill:Bill):
    """ Turns paper to a vector of word counts using the indicies from translator """
    vector = np.array([0] * len(translator), dtype = 'uint8')
    words = ""
    if type(bill) == str:
        words = get_words(bill)
    else:
        words = get_words_bill(bill)
    for word in words:
        if word in translator:
            index = translator[word]
            vector[index] += 1
    new_vector = []
    for cell in vector:
        if type(bill) == str:
            new_vector += [100000 * (cell / len(bill))]
        else:
            new_vector += [100000 * (cell / len(bill.text))]
    return np.array(new_vector, dtype = 'uint8') 

def make_translator(bills:list):
    """ makes a dictionary with word as input, index in word count vector as output """
    words = set()
    for bill in bills:
        for word in get_words_bill(bill):
            if word not in words:
                words.add(word)
    counter = 0
    translator = dict()
    for word in words:
        translator[word] = counter
        counter += 1

    return translator

def get_words_bill(bill:Bill):
    words = []
    current_word = ''
    for character in bill.text.lower():
        if isdigit(character) or isalpha(character):
            current_word += character
        else:
            if len(current_word) > 0:
                words.append(current_word)
                current_word = ''

    return words

def get_words(bill:str):
    words = []
    current_word = ''
    for character in bill.lower():
        if isdigit(character) or isalpha(character):
            current_word += character
        else:
            if len(current_word) > 0:
                words.append(current_word)
                current_word = ''

    return words


def make_labels(bills):
    parties = set()
    for bill in bills:
        if bill.party not in parties:
            parties.add(bill.party)
    party_list = list(parties)
    labels = []
    for bill in bills:
        label = [0] * len(party_list)
        label[party_list.index(bill.party)] = 1
        label = np.array(label, dtype = 'uint8')
        labels.append(label)
    return labels,party_list

def max_index(list_of_stuff:list) -> int:
    max_num = -1
    max_index = 0
    for i in range(len(list_of_stuff)):
        if list_of_stuff[i] > max_num:
            max_index = i
            max_num = list_of_stuff[i]
    return max_index

    


if __name__ == "__main__":
    folder = sys.argv[1]
    bills, bill_locations = make_bills(folder)

    translator = make_translator(bills)
    inv_translator = {v: k for k, v in translator.items()}

    print("making bill vectors!")
    bill_vectors = []
    counter=0
    for bill in bills:
        bill_vectors.append(to_word_vector(translator, bill))
        print(counter/len(bills))
        counter +=1

    bill_labels,index_translator = make_labels(bills)
    print("index_translator= " + str(type(index_translator)))
    for i in index_translator:
        print(i)
    

    print("making model!")
    model = make_model(len(bill_vectors[0]))

    bill_vectors = np.array(bill_vectors, dtype = 'uint8')
    bill_labels = np.array(bill_labels, dtype = 'uint8')
    
    print("bill vectors: " + str(len(bill_vectors)))
    print("bill labels: " + str(len(bill_labels)))

    print(bill_vectors[0])
    print(bill_labels[0])


    history = model.fit(bill_vectors, bill_labels, epochs=30, validation_split = 0.05)

    accuracy = 0
    outputs = model.predict(bill_vectors)
    for i in range(len(bill_labels)):
        if str(max_index(outputs[i])) == str(max_index(bill_labels[i])):
            accuracy += 1
        else:
            print(bills[i].file_location + ": " + str(index_translator[max_index(outputs[i])]) + " " + str(index_translator[max_index(bill_labels[i])]) + " " + str(bills[i].percent_left()) + " " + str(bills[i].percent_right()))
    print(accuracy / len(outputs))
    

    pd.DataFrame(history.history).plot(figsize=(8,5))
    plt.grid(True)
    plt.gca().set_ylim(0,1)
    plt.show()

    while True:
        input_text = file(input("input file: ")).read()
        bill_vectors = []
        bill_vectors.append(to_word_vector(translator, input_text))
        bill_vectors = np.array(bill_vectors)
        outputs = model.predict(bill_vectors)
        for i in range(len(outputs[0])):
            print(index_translator[i] + ": " + str(outputs[0][i]))