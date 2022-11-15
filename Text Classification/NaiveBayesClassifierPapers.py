from curses.ascii import isalpha, isdigit
from plistlib import InvalidFileException
import sys
import os
import numpy as np
from sklearn.naive_bayes import MultinomialNB

def make_papers(folder:str):
    paper_locations = os.listdir(folder) # returns all the names of all the files in the folder
    paper_locations = list(map(lambda loc:folder + '/' + loc, paper_locations)) #returns a list of all the location
    papers = []
    for paper_file in paper_locations:
        if paper_file[-3:] == 'txt': # if it's a text file
            try:
                papers += [open(paper_file).read()] # turn the file into a paper
            except InvalidFileException as e: # if the file was invalid, ignore
                continue
    return papers

def to_word_vector(translator:dict, paper:str):
    """ Turns paper to a vector of word counts using the indicies from translator """
    vector = np.array([0] * len(translator), dtype = 'uint8')
    for word in get_words(paper):
        if word in translator:
            index = translator[word]
            vector[index] += 1
    new_vector = []
    for cell in vector:
        new_vector += [100000 * (cell / len(paper))]
    return np.array(new_vector, dtype = 'uint8') 

def make_translator(papers:list):
    """ makes a dictionary with word as input, index in word count vector as output """
    words = set()
    for paper in papers:
        for word in get_words(paper):
            if word not in words:
                words.add(word)
    counter = 0
    translator = dict()
    for word in words:
        translator[word] = counter
        counter += 1

    return translator

def make_translator_of_valid_words(valid_words:list):
    """ makes a dictionary with word as input, index in word count vector as output """
    counter = 0
    translator = dict()
    for word in valid_words:
        translator[word] = counter
        counter += 1

    return translator
def get_words(paper:str):
    words = []
    current_word = ''
    for character in preprocess(paper):
        if isdigit(character) or isalpha(character):
            current_word += character
        else:
            if len(current_word) > 0 :
                words.append(current_word)
                current_word = ''

    return words

def preprocess(paper:str):
    paperCopy = paper.lower();
    paperCopy.replace("hamilton","")
    paperCopy.replace("madison","")
    paperCopy.replace("jay","")
    return paperCopy

def valid_words(paperVectors:np.array, translator:dict):
    valid_words = set()
    for word in translator:
        papers_word_used_in = 0
        for vec in paperVectors:
            if vec[translator[word]] > 0:
                papers_word_used_in += 1
        if papers_word_used_in > ((1 * len(paperVectors)) / 7): 
            print(word)       
            valid_words.add(word)   
    return valid_words



if __name__ == "__main__":
    folder = sys.argv[1]
    hamilton_papers = make_papers(folder+"/hamilton/")
    madison_papers = make_papers(folder+"/madison/")
    disputed_papers = make_papers(folder+"/disputed/")

    #pi = fraction of the total papers that are labeled with a given party
    pi = {
        'hamilton' : len(hamilton_papers[:len(madison_papers)]) / (len(madison_papers) + len(hamilton_papers)),
        'madison' : len(madison_papers) / (len(madison_papers) + len(hamilton_papers)),
    }

    print("Probability of each class:")
    print("\n".join("{}: {}".format(k, v) for k, v in pi.items()))

    translator = make_translator(hamilton_papers + madison_papers + disputed_papers)
    inv_translator = {v: k for k, v in translator.items()}

    print("making paper vectors!")
    paper_vectors = []
    paper_labels = []
    for paper in hamilton_papers:
        paper_vectors.append(to_word_vector(translator, paper))
        paper_labels.append('hamilton')

    for paper in madison_papers:
        paper_vectors.append(to_word_vector(translator, paper))
        paper_labels.append('madison')

    paper_vectors = np.array(paper_vectors)
    paper_labels = np.array(paper_labels)

    valid_words = valid_words(paper_vectors,translator)
    valid_words.add('whilst')
    valid_words.add('while')

    translator = make_translator_of_valid_words(valid_words)

    print("making paper vectors! (again)")
    paper_vectors = []
    paper_labels = []
    for paper in hamilton_papers[:len(madison_papers)]:
        paper_vectors.append(to_word_vector(translator, paper))
        paper_labels.append('hamilton')

    for paper in madison_papers:
        paper_vectors.append(to_word_vector(translator, paper))
        paper_labels.append('madison')

    for word in translator:
        print(word + ": " + str(paper_vectors[0][translator[word]]))

    paper_vectors = np.array(paper_vectors)
    paper_labels = np.array(paper_labels)

    print("making model!")
    clf = MultinomialNB()
    clf.fit(paper_vectors, paper_labels)

    accuracy = 0
    outputs = clf.predict(paper_vectors)
    for i in range(len(paper_labels)):
        if str(outputs[i]) == str(paper_labels[i]):
            accuracy += 1
        print(str(outputs[i]) + " " + str(paper_labels[i]))
    print(accuracy / len(outputs))

    disputed_vectors = []
    for paper in disputed_papers:
        disputed_vectors.append(to_word_vector(translator, paper))

    outputs = clf.predict(disputed_vectors)
    for i in range(len(disputed_vectors)):
        print(disputed_papers[i].split('\n')[0] + ": " + outputs[i])



    