import os
import heapq  
import nltk
import re
import imp
import sys
from glob import glob
import imp

def get_summary(dir_path):
    parts = dir_path.split("/")
    id = parts[-2]
    my_files = glob(dir_path+'*.txt')
    for file in my_files:
        f = open(file, 'r')                   #以读方式打开文件
        #result = list()
        article_text = ""
        for line in f.readlines():                      
            line = line.strip()                             #delete spaces
            if not len(line) or line.startswith('#'):       #delete empty lines or # one
                continue                                       
            article_text += "\n"+str(line)
            # Removing Square Brackets and Extra Spaces, store in clean_text
            clean_text = re.sub(r'\[[0-9]*\]', ' ', article_text)  
            clean_text = re.sub(r'\s+', ' ', article_text)  

            # Removing special characters and digits
            #formatted_clean_text used to calculate weighted frequency
            formatted_clean_text = re.sub('[^a-zA-Z]', ' ', clean_text )  
            formatted_clean_text = re.sub(r'\s+', ' ', formatted_clean_text)  

            #tokenizing the text into sentences
            sentence_list = nltk.sent_tokenize(clean_text)  
            #get stop words from nltk
            stopwords = nltk.corpus.stopwords.words('english')
            #get the frequency of each word
            word_freq = {}  
            for word in nltk.word_tokenize(formatted_clean_text):  
                if word not in stopwords:
                    if word not in word_freq.keys():
                        word_freq[word] = 1
                    else:
                        word_freq[word] += 1
            #calculate the precentage
            max_freq = max(word_freq.values())
            for word in word_freq.keys():  
                word_freq[word] = (word_freq[word]/max_freq)

            sentence_order = {}
            first = 1
            for sentence in sentence_list:
                sentence_order[sentence] =first
                first += 1

            #calculate sentence scores
            #keys of "sentence_scores" = themselves 
            #values of it = the corresponding scores of the sentences. 
            sentence_scores = {}  
            for sent in sentence_list:  
                for word in nltk.word_tokenize(sent.lower()):
                    if word in word_freq.keys():
                    	#do not want long sentences, so keep it < 20
                        if len(sent.split(' ')) < 50:
                            if sent not in sentence_scores.keys():
                                sentence_scores[sent] = word_freq[word]
                            else:
                                sentence_scores[sent] += word_freq[word]

        my_files = glob(dir_path + '*.txt')
        my_files = ',\n\t'.join(map(lambda x: x.split('/')[-1], my_files))
        print("Input files:\n\t",my_files)
        #I should have a method to clean up the similar sentences before summarizing
        summary_sentences = heapq.nlargest(5, sentence_scores, key=sentence_scores.get)

        # summary = ' '.join(summary_sentences)  
        # print('id is: '+id,end = ','+'\n')
        # print('adress of the file'+file,end=','+'\n')
        # print('The summary is: '+summary) 

        ordered_helper = {}
        for sentence in summary_sentences:
            ordered_helper[sentence] = sentence_order[sentence]
        ordered_summary = heapq.nsmallest(5,sentence_order,ordered_helper,key = ordered_helper.get)
"""
for sent in sentence_list:
    sentence_scores[sent] /= len(sent.split(' '))
"""

def main():
    articles_path = sys.argv[1]
    out_path = sys.argv[2]
    out_path = os.path.join(out_path, 'output.txt')
    sys.stdout = open(out_path,'w')

    dirs = glob(articles_path+'/*/')

    for dir in dirs:
        print(dir)
        get_summary(dir)

if __name__ == '__main__':
    main()
