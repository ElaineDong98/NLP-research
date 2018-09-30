# -*- coding: utf-8 -*-
# This script is written in python 3
# written by Jonathan Gomez Martinez (December 2017)
# modief by Gabriel Wang (February 2018) 

# command line usage: 
#          python StanfordCoreNLP.py 
#                 [path-of-stanford-corenlp-package] 
#                 [path-of-input-files-dir]  
#                 [path-of-input-file]
#                 [path-of-output]
# TODO:  More comment on what are the rest of the arguments doing.

#cd "C:\Program files (x86)\PC-ACE\NLP\CoreNLP" & 
#	Python StanfordCoreNLP.py "C:\Program files (x86)\PC-ACE\NLP\stanford-corenlp-full-2018-02-27" 
#	"C:\Users\rfranzo\Documents\ACCESS Databases\PC-ACE\NEW\DATA\CORPUS DATA\Sample txt"    
#   "C:\Users\rfranzo\Desktop\NLP_output" 4 1 1 _ 1 3
from pycorenlp import StanfordCoreNLP
import os
import glob
import time
import datetime
import pandas as pd
import subprocess
import sys
import numpy as np
import io
import re
from collections import OrderedDict
from unidecode import unidecode
import socket
from contextlib import closing

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            print ("Port is open")
        else:
            print ("Port is not open")

def get_open_port():
    # function to find a open port on local host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port

class RunCoreNLP():
    #check_socket('localhost',9000)
    port = get_open_port() #find a open port for corenlp
    '''
    This procedure takes *.txt files and runs StanfordCoreNLP to produce ConLL files for each individual file.
    It then creates a merged ConLL file including all of the ConLL tables in a single ConLL file

    arguments:
        Path: The first argument should be the path to the *.txt files.
        OutputPath: The second argument should be the folder where the user would like his/her ConLL files saved
        Memory: The third argument should be an integer value specifying how much memory (RAM) a user is willing to give to CoreNLP
            More memory can lead to quicker runtime on large *.txt files
        mergeFiles: A boolean specifying whether or not to run the merge algorithm with 1 meaning yes and 0 meaning no
        getDate: A boolean specifying whether or not to run the date grabbing algorithm with 1 meaning yes and 0 meaning no
                ~Required parameter if running merge files algorithm
        Separator: A specified separator for dates, must still specify something even if not running date
                ~Required parameter if running date grabbing algorithm
        Loc: The date start location
                ~Required parameter if running date grabbing algorithm
        NumFields: The number of date fields provided
                ~Required parameter if running date grabbing algorithm
    '''
    #print(sys.argv,len(sys.argv))
    
    #TODO: Modify the all-files-in-dir mode & one-file mode, the current version is really bad practice
    # Useful debug tip: well, you may be in trouble if you are trying to debug the arguments
    # But just start with enumerating the sys.argv
    for i, arg in enumerate(sys.argv):
        print(i,arg)
    CoreNLPPath = sys.argv[1]
    Path = sys.argv[2] + '\\'
    # if the third argument is a path, then it is output path
    # else it is the specific input file
    is_path = os.path.isdir(sys.argv[3])
    print(is_path)
    if is_path:
	    outputPath = sys.argv[3] + '\\'
	    mem = sys.argv[4]
	    mergeFiles = sys.argv[5]
	    mergeFiles = int(mergeFiles)
	    if mergeFiles == 1:
	        getDate = sys.argv[6]
	        getDate = int(getDate)
	        if getDate == 1:
	            separator = sys.argv[7]
	            loc = sys.argv[8]
	            loc = int(loc)
	            numFields = sys.argv[9]
	            numFields = int(numFields)
    else:
        filename = sys.argv[3]
        outputPath = sys.argv[4] + '\\'
        mem = sys.argv[5]
        mergeFiles = sys.argv[6]
        mergeFiles = int(mergeFiles)
        if mergeFiles == 1:
        	getDate = sys.argv[7]
        	getDate = int(getDate)
        	if getDate == 1:
        	    separator = sys.argv[8]
        	    loc = sys.argv[9]
        	    loc = int(loc)
        	    numFields = sys.argv[10]
        	    numFields = int(numFields)
    CoreNLPPath = CoreNLPPath + '\\'
    command = 'java -mx' + str(
        mem) + 'g -cp "' + CoreNLPPath + '*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port '+ str(port)  # Command to launch CoreNLP Server with user specified memory options

    server = subprocess.Popen(command)  #Launch CoreNLP server, allowing us to run *.txt files without re-initializing CoreNLP
    nlp = StanfordCoreNLP('http://localhost:'+str(port))  #Attach the server to a variable for cleaner code

    if(is_path): #This is the all-files-in-dir mode
    	Docs=[]
    	for f in os.listdir(Path):
	    	if not f[:2] == '~$': # ignore the temporary files
	    		if f[-4::]=='.txt':# check if it is a .txt file
	    			Docs.append(Path+f)
    else: # one-file mode
    	Docs = [Path+filename]
    #Docs = []
    #print(Docs)
    startTime = time.localtime()
    print("Started running at " + str(startTime[3]) + ':' + str(startTime[4])) #Prints start time for future reference
    #print(Docs)
    #The loop below opens each *.txt file in the input directory and passes the text to our local CoreNLP server.
    #   The server then returns our ConLL table in a tab separated format which is then saved as a *.ConLL file
    #   Opened files are closed as soon as they are no longer necessary to free-up resources
    i = 0.0
    fileNames = []
    for file in Docs:
        server.poll()
        F = io.open(file, 'r', encoding='utf-8',errors='ignore')
        text = F.read()
        text = text.encode('utf-8')
        F.close()
        x = file[len(Path)::] # Only keep the file name with .txt
        fileNames.append(x)
        print("Parsing: " + x)
        #print(x.find('_'))
        try:
            udata = text.decode("utf-8")
            text = udata.encode("ascii", "ignore")
            output = nlp.annotate(text.decode('utf-8'), properties={        #Passes text and preferences (properties) to CoreNLP
                'annotators': 'tokenize,ssplit,pos,lemma, ner,parse',
                'outputFormat': 'conll',
                'timeout': '999999',
                'outputDirectory': outputPath,
                'replaceExtension': True
            })
            # Replace normalized paranthese back
            output = str(output).replace("-LRB-","(").replace("-lrb-","(") .replace("-RRB-",")") .replace("-rrb-",")") .replace("-LCB-","{") .replace("-lcb-","{") .replace("-RCB-","}") .replace("-rcb-","}") .replace("-LSB-","[") .replace("-lsb-","[") .replace("-RSB-","]") .replace("-rsb-","]") 
            print("Writing: " + x)
            text_file = io.open(outputPath + x + ".conll", "w", encoding='utf-8')
            text_file.write(output)             #Output *.ConLL file
            text_file.close()
            print(str(100 * round(float(i) / len(Docs), 2)) + "% Complete") #Rough progress bar for reference mid-run
            i += 1
        except Exception as e:
        	print("Could not create CoNLL for " + x+' because of '+str(e)) 
        	server.poll()
    endTime = time.localtime()

    server.kill() #Server is killed before entire procedure is completed since we no longer need it
    print("Finished running at " + str(endTime[3]) + ':' + str(endTime[4]))    #Time when ConLL tables finished computing, for future reference

    #Here we merge all of the previously computed ConLL tables into a single merged ConLL table
    ConLL = glob.glob(outputPath + "*.conll")   #Produce a list of ConLL tables in the output directory

    #The loop below opens each *.ConLL file in the ouput directory and pulls the contents into memory,
    #    creating a running table of concatenated tables. Opened files are closed after being pulled into memory to preserve resources

    if mergeFiles == 1:
        startTime = time.localtime()
        print("Started merging at " + str(startTime[3]) + ':' + str(startTime[4]))  #Time when merge started, for future reference
        merge = None    #Initialize an empty variable to assure the  new merged table is in fact new
        docNum = 1
        for table in ConLL:
            lineNum = 1
            x = table[len(outputPath):-6]
            if x in fileNames:
                print(x)    #Prints the name of the table being worked on
                if getDate == 1:
                    startSearch = 0
                    iteration = 0
                    while iteration < loc:
                        startSearch = x.find(separator, startSearch)
                        iteration += 1
                    end = x.find(separator, startSearch + 1)
                    iteration = 0
                    raw_date = x[startSearch+1:end]
                    # new find_date method to tolerate differnet seperator
                    """
                    while iteration <= numFields:
                        end = x.find(separator, end) + 1
                        if end == -1:
                            iteration = 5
                        iteration += 1
                    if end >= 0:
                        date = x[x.find(separator, startSearch) + 1:end - 1]
                    else:
                        date = x[x.find(separator, startSearch) + 1:]
                    if date[-1:] == separator:
                        date = date[:-1]
                    """
                    try:
                        date = datetime.datetime.strptime(raw_date, '%m-%d-%Y')
                        print('Date is',date.strftime("%Y-%m-%d"))
                    except ValueError:
                        try:
                            print('Format is off, best guess of the date')
                            date_data = re.split('[^a-zA-Z0-9]', raw_date)
                            date = data_data[0]+'-'+date_data[1]+'-'+date_data[2]
                            print(date)
                        except IndexError:
                            print('Make sure the date field is in mm-dd--yyyy format')
                            date = 'NaN-NaN-NaN'
                            print('Date is set to '+date)
                    if x == 'mergedConllTables': #Assures that the merged ConLL table is not merged into our new merged ConLL table (in the case of re-running script)
                        continue
                    if merge is None:
                        hold = pd.DataFrame.from_csv(io.open(table, 'rb'), sep='\t', header=None, index_col=False)
                        holdDocNum = pd.DataFrame(OrderedDict( (('DocNum', np.ones(hold.shape[0]) * docNum) , ('name', x), ('date', date))) )
                        hold = hold.merge(holdDocNum, left_index=True, right_index=True, how='inner')
                        merge = hold
                    else:
                        hold = pd.DataFrame.from_csv(io.open(table, 'rb'), sep='\t', header=None, index_col=False)
                        holdDocNum = pd.DataFrame(OrderedDict( (('DocNum', np.ones(hold.shape[0]) * docNum) , ('name', x), ('date', date))) )
                        hold = hold.merge(holdDocNum, left_index=True, right_index=True, how='inner')
                        merge = pd.concat([merge, hold], axis=0, ignore_index=True)
                    docNum += 1
                if getDate == 0:
                    if x == 'mergedConllTables': #Assures that the merged ConLL table is not merged into our new merged ConLL table (in the case of re-running script)
                        continue
                    if merge is None:
                        hold = pd.DataFrame.from_csv(io.open(table, 'rb'), sep='\t', header=None, index_col=False)
                        holdDocNum = pd.DataFrame(OrderedDict((('DocNum', np.ones(hold.shape[0]) * docNum), ('name', x))))
                        hold = hold.merge(holdDocNum, left_index=True, right_index=True, how='inner')
                        merge = hold
                    else:
                        hold = pd.DataFrame.from_csv(io.open(table, 'rb'), sep='\t', header=None, index_col=False)
                        holdDocNum = pd.DataFrame(
                            OrderedDict((('DocNum', np.ones(hold.shape[0]) * docNum), ('name', x))))
                        hold = hold.merge(holdDocNum, left_index=True, right_index=True, how='inner')
                        merge = pd.concat([merge, hold], axis=0, ignore_index=True)
                    docNum += 1
        counter = np.arange(1,merge.shape[0]+1)
        #print(merge)
        merge.insert(7, 'RecordNum', counter)
        sentenceID = 0
        docID = 1
        sentIDs = []
        for i in range(merge.shape[0]):
            if int(merge.iloc[i][8]) > docID:
               docID = docID + 1
               sentenceID = 0
            if(str(merge.iloc[i][0]) == '1'):
                sentenceID += 1
            sentIDs.append(sentenceID)
        merge.insert(9, 'SentenceID', sentIDs)
        merge.to_csv(outputPath + "mergedConllTables.conll", sep='\t', index=False, header=False)    #Outputs merged ConLL table as a *.ConLL file into our output directory
        endTime = time.localtime()
        print("Finished merging at " + str(endTime[3]) + ':' + str(endTime[4]))     #Time when merge finished, for future reference







