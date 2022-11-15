from curses.ascii import isalpha, isdigit
from plistlib import InvalidFileException
import sys
import os
import numpy as np
from sklearn.naive_bayes import MultinomialNB

from Bill import Bill, CongressPerson

def make_bills(folder:str):
    bill_locations = os.listdir(folder)
    bill_locations = list(map(lambda loc:folder + '/' + loc, bill_locations))
    bills = []
    for bill_file in bill_locations:
        if bill_file[-3:] == 'txt':
            try:
                bills.append(Bill(bill_file))
            except InvalidFileException as e:
                continue
    return bills

def to_word_vector(translator:dict, bill:Bill):
    """ Turns bill to a vector of word counts using the indicies from translator """
    vector = np.array([0] * len(translator), dtype = 'uint8')
    for word in get_words(bill):
        index = translator[word]
        vector[index] += 1
    return vector

def make_translator(bills:list):
    """ makes a dictionary with word as input, index in word count vector as output """
    words = set()
    for bill in bills:
        for word in get_words(bill):
            if word not in words:
                words.add(word)
    counter = 0
    translator = dict()
    for word in words:
        translator[word] = counter
        counter += 1

    return translator

def get_words(bill:Bill):
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


if __name__ == "__main__":
    folder = sys.argv[1]
    bills = make_bills(folder)

    #pi = fraction of the total bills that are labeled with a given party
    pi = {}
    for bill in bills:
        if not(bill.party in pi.keys()):
            pi[bill.party] = 0
        pi[bill.party] += 1

    for key in pi:
        pi[key] /= len(bills)

    print("Probability of each class:")
    print("\n".join("{}: {}".format(k, v) for k, v in pi.items()))

    translator = make_translator(bills)
    inv_translator = {v: k for k, v in translator.items()}

    print("making bill vectors!")
    bill_vectors = []
    bill_labels = []
    for bill in bills:
        bill_vectors.append(to_word_vector(translator, bill))
        bill_labels.append(bill.party)

    bill_vectors = np.array(bill_vectors)
    bill_labels = np.array(bill_labels)

    print("making model!")
    clf = MultinomialNB()
    clf.fit(bill_vectors, bill_labels)

    accuracy = 0
    outputs = clf.predict(bill_vectors)
    for i in range(len(bill_labels)):
        if str(outputs[i]) == str(bill_labels[i]):
            accuracy += 1
    print(accuracy / len(outputs))



    