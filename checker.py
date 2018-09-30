articles_path = 'data/articles'

import os
from glob import glob
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import sys

lemmatizer = WordNetLemmatizer()

def load_soc_actors(path='socact.csv'):
    my_soc_actors = set()
    with open(path) as fin:
        for line in fin:
            # prin  t(line.strip().split(','))
            if line.strip().split(',')[-1] in ['x','X']:
                # print(line)
                my_soc_actors.add(line.split(',')[0])

    return my_soc_actors

def get_article_soc_actors(dir_path, soc_acts):
    my_files = glob(dir_path+'*.txt')
    #print(my_files)

    actors = set()
    for file in my_files:
        with open(file) as fin:
            fcontent = fin.read() # encoding / decoding issue to be fixed later!!!

        tokens = nltk.word_tokenize(fcontent)
        for i in range(len(tokens)):
            tokens[i] = lemmatizer.lemmatize(tokens[i].lower())
        # print(tokens)
        for token in tokens:
            if token in soc_acts:
                actors.add((token, file.split('/')[-1]))

    return actors

def get_comp_soc_actors(id, soc_acts, c_path='data/out/'):
    my_path = 'data/out/' + id + '.txt'

    try:
        with open(my_path) as fin:
            fcontent = fin.read()
    except:
        return set()

    tokens = nltk.word_tokenize(fcontent)
    actors = set()
    for i in range(len(tokens)):
        tokens[i] = lemmatizer.lemmatize(tokens[i].lower())

    for token in tokens:
        if token in soc_acts:
            actors.add(token)

    return actors

def check(dir_path, soc_acts, compilation_path):
    parts = dir_path.split("/")
    id = parts[-2]
    #print("parts are: {0}".format(parts))
    #print("dir_path: {}".format(soc_acts))
    article_actors = get_article_soc_actors(dir_path, soc_acts)
    #print(article_actors)
    comp_actors = get_comp_soc_actors(id, soc_acts, c_path=compilation_path)
    missings = set()
    for act_tup in article_actors:
        article_act, article = act_tup
        if article_act not in comp_actors:
            missings.add(act_tup)
    my_files = glob(dir_path + '*.txt')
    my_files = ',\n\t\t\t\t\t\t\t'.join(map(lambda x: x.split('/')[-1], my_files))
    print("Input files:\n\t\t\t\t\t\t",my_files)
    # print("Missing:\n\t", end='')
    print("Event ID,Missing words,Input file name,Summary file name")
    for missing in missings:
        print(id, end=',')
        print(missing[0], end=',')
        print('"'+ missing[1] + '"', end=',')
        print(id+'.txt')
        # print('\t', missing)
    # print()
   


def main():
    articles_path = sys.argv[1]
    compilations_path = sys.argv[2]
    out_path = sys.argv[3]

    #redirect output
    # if out_path[-1] != '/':
        # out_path = out_path[:-1]
    # if out_path[-1] != '':
    # articles_path = articles_path[:-1]
    # compilations_path = compilations_path[:-1]
    # out_path = out_path[:-1] 
    # print(articles_path)
    # print(compilations_path)
    # print(out_path)
    # sys.exit(1)
    out_path = os.path.join(out_path, 'validity.csv')
    sys.stdout = open(out_path, 'w')
    #print("Event ID,word,Input file name,Summary file name")

    actors = load_soc_actors()
    # print("My actors", actors)
    dirs = glob(articles_path+'/*/')
    
    # print("hello")
    
    for dir in dirs:
        check(dir, actors, compilation_path=compilations_path)

if __name__ == '__main__':
    main()

#readable output