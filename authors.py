#python authors.py -tr EnronDataset/train.txt -te EnronDataset/test.txt

import nltk
import random
import sys
from string import *

smoothing = 'n'

# Constant used for linear interpolation, this is the weight given to bigrams
constant = .8

#Dictionaries of Emails
authors = {}
authorsTest = {}
authorsValidation = {}

#Dicts of Grams
authorUnigrams = {}
authorBigrams = {}
normalizedAuthorUnigrams = {}
normalizedAuthorBigrams = {}

#author -> list
authorProperNouns = {}
stemming_enabled = False


# Porter Stemmer for getting the stems of words
stemmer = nltk.PorterStemmer()

def stem(train_words):
    # Stems the words if stemming is enabled
    if stemming_enabled:
	for words in train_words:
	    for i in range(0,len(words)):
		words[i] = stemmer.stem(words[i])
    return train_words

def readFile(file,emailDictionary):
    file = open(file)
    while 1:
        email = file.readline()
        if not email:
            break
        email = email.split(' ',1)
        author = email[0]
        author = author.strip()
        if author in emailDictionary.keys():
            emailDictionary[author].append(email[1])
        else:
            emailDictionary[author] = []
            emailDictionary[author].append(email[1])
            


# Regex pattern for tokenizing the corpus, accounts for acronyms, etc.
pattern = r'''(?x)  
      \w+        
      | \$?\d+(\.\d+)?
      | ([A-Z]\.)+        
      | [^\w\s]+        
      '''

#Build counts
def buildGrams(email,unigram,bigram,properNouns = None):
    train_words = []
    train_words.append(nltk.tokenize.regexp_tokenize(email, pattern))
    if(stemming_enabled and properNouns is not None):
        train_words = stem(train_words)
    for words in train_words:
            for i in range(0,len(words)-1):
                    w1 = words[i]
                    w2 = words[i+1]
                    if w1.istitle() and words[i-1].isalpha() and len(w1) > 2 and properNouns is not None:
                        w1 = w1.lower()
                        if w1 in properNouns:
                            properNouns[w1.lower()] += 1
                        else:
                            properNouns[w1.lower()] = 0
                    w1 = w1.lower()
                    w2 = w2.lower()
                    if w1 not in unigram:
                            unigram[w1] = 0
                    if w1 not in bigram:
                            bigram[w1] = {}
                    if w2 not in bigram[w1]:
                            bigram[w1][w2] = 0
                  
                    unigram[w1] += 1
                    bigram[w1][w2] += 1
            

    return (unigram,bigram)
            

def main():
    
    # Train each authors unigrams and bigrams using all their emails
    for author in authors.keys():
        authorUnigrams[author] = {}
        authorBigrams[author] = {}
        authorProperNouns[author] = {}
        unigram = authorUnigrams[author]
        bigram = authorBigrams[author]
        properNouns = authorProperNouns[author]
        for email in authors[author]:
            (unigram,bigram) = buildGrams(email,unigram,bigram,properNouns)
            authorUnigrams[author] = unigram
            authorBigrams[author] = bigram
        normalizedAuthorUnigrams[author] = normUnigram(authorUnigrams[author])
        normalizedAuthorBigrams[author] = normBigram(authorUnigrams[author],authorBigrams[author])
        
        
    if len(authorsTest) != 0:
        testResults = []
        bestPredictions = []
        
        (accuracy, predictions) = classifyEmails(authorsTest)
        
        testResults.append(accuracy)
        print accuracy
            
        
            
        
            
    if len(authorsValidation) != 0:
        print classifyEmails(authorsValidation)
    
    

def normUnigram(unigrams):
    normUnigrams = {}
    listSum = sum(unigrams.values())
    for x in unigrams.keys():
        if listSum != 0:
            normUnigrams[x] = float(unigrams[x])/listSum
    return normUnigrams

def normBigram(unigrams, bigrams):
    normBigrams = {}
    for w1 in bigrams.keys():
        
        #conditional probability
        for w2 in bigrams[w1].keys():
            denom = 0;
            num = 0;
            if w2 in unigrams:
                denom = unigrams[w2]
            if w1 in bigrams and w2 in bigrams[w1]:    
                num =  bigrams[w1][w2]
            if w1 not in normBigrams:
                normBigrams[w1] = {}
            if w2 not in normBigrams[w1]:
                normBigrams[w1][w2] = 0
            if denom != 0:
                normBigrams[w1][w2] = float (num) / denom
        #normalization(sum to 1)
        #this is probably retarded as I don't know python datastuctures
        
    
            
        
    return normBigrams

def writeList(L, file = 'results.txt'):
    file = open('results.txt','w')
    for i in predictedAuthors:
        file.write(i + "\n")
    file.close()



def smoothUnigrams(unigrams, normalizedUnigrams, additional):
    if smoothing == 'n':
        return normalizedUnigrams
    smoothUnigrams = {}
    listSum = sum(unigrams.values())
    if smoothing == 'a' or smoothing == 'i':
        for x in unigrams.keys():
            smoothUnigrams[x] = float(1 + unigrams[x]) / (listSum + additional)
            
    return smoothUnigrams
            
def smoothBigrams(bigrams, normalizedBigrams, unigrams, normalizedUnigrams, additional):
    if smoothing == 'n':
        return normalizedBigrams
    smoothBigrams = {}
    listSum = sum(unigrams.values())
    if smoothing == 'a':
        for w1 in bigrams.keys():
            for w2 in bigrams[w1].keys():
                denom = 0;
                num = 0;
                if w2 in unigrams:
                    denom = unigrams[w1]
                if w1 in bigrams and w2 in bigrams[w1]:    
                    num =  bigrams[w1][w2]
                if w1 not in smoothBigrams:
                    smoothBigrams[w1] = {}
                if w2 not in smoothBigrams[w1]:
                    smoothBigrams[w1][w2] = 1
                if denom != 0:
                    smoothBigrams[w1][w2] = float(1 + num) / (denom + additional)
    elif smoothing == 'i':
        for w1 in bigrams.keys():
            for w2 in bigrams[w1].keys():
                if w1 not in smoothBigrams:
                    smoothBigrams[w1] = {}
                if w2 not in smoothBigrams[w1]:
                    smoothBigrams[w1][w2] = 0
                try:
                    smoothBigrams[w1][w2] = constant*normalizedBigrams[w1][w2] + (1-constant)*normalizedUnigrams[w2]
                except KeyError: 
                    smoothBigrams[w1][w2] = normalizedBigrams[w1][w2]
            
    return smoothBigrams


def classifyEmails(emails, weight = None):
    numCorrect = 0
    total = 0

    predictedAuthors = []


    for author in emails.keys():
        for email in emails[author]:
            
            total +=1
            predictedAuthor = predictAuthor(email,True,weight)
            predictedAuthors.append(predictedAuthor)
            if author == predictedAuthor:
                numCorrect +=1
    return (float(numCorrect) / total, predictedAuthors)
        
#weight corresponds to the amount of weight
#to put on the unigrams
def predictAuthor(email, smoothing, weight = None):
    bigramWeight = .5
    unigramWeight = .5
    if weight is not None:
        bigramWeight = 1 - weight
        unigramWeight =  weight
    
    authorsUtility = {}
    emailUnigrams = {}
    emailBigrams = {}
    (emailUnigrams,emailBigrams) = buildGrams(email,emailUnigrams,emailBigrams)
    emailUnigramNorm = normUnigram(emailUnigrams)
    emailBigramNorm = normBigram(emailUnigrams,emailBigrams)
    

    for author in authors.keys():
        authorsUtility[author] = 0;
        bigrams = authorBigrams[author]
        if not smoothing:
            for key in emailBigrams.keys():
               for key2 in emailBigrams[key]:
                    if key in normalizedAuthorBigrams[author] and key2 in normalizedAuthorBigrams[author][key]:
                        properNounBoost = 1
                        if authorProperNouns[author] is not None and key in authorProperNouns[author]:
                            properNounBoost = 3.1
                        
                        authorsUtility[author] += normalizedAuthorBigrams[author][key][key2] * emailBigramNorm[key][key2] * properNounBoost
                        
        additionalUnigrams = 0
        if smoothing:
            for author in authors.keys():
                authorsUtility[author] = 0;
                
                for emailUnigramKey in emailUnigrams.keys():
                    if not (emailUnigramKey in normalizedAuthorUnigrams[author]):
                        authorUnigrams[author][emailUnigramKey] = 0
                        authorBigrams[author][emailUnigramKey] = {}
                        additionalUnigrams += 1
                
                smoothedAuthorUnigrams = smoothUnigrams(authorUnigrams[author], normalizedAuthorUnigrams[author], additionalUnigrams)
                smoothedAuthorBigrams = smoothBigrams(authorBigrams[author], normalizedAuthorBigrams[author], authorUnigrams[author], 
                                                      normalizedAuthorUnigrams[author], additionalUnigrams)
                #smoothedAuthorUnigrams = normalizedAuthorUnigrams[author]
                #smoothedAuthorBigrams = normalizedAuthorBigrams[author]
                
                
                for key in emailBigrams.keys():
                    for key2 in emailBigrams[key]:
                        if key in smoothedAuthorBigrams and key2 in smoothedAuthorBigrams[key]:
                            properNounBoost = 1
                            if authorProperNouns[author] is not None and key in authorProperNouns[author]:
                                properNounBoost = 3.1
                                
                            authorsUtility[author] += smoothedAuthorBigrams[key][key2] * emailBigramNorm[key][key2] * properNounBoost
                       
  
    index = authorsUtility.values().index(max(authorsUtility.values()))
    
    return authorsUtility.keys()[index]

arg = 1
while arg < len(sys.argv):
            
    # -tr <filename> adds <filename> to the train set
    if sys.argv[arg] == '-tr':
        arg += 1
        if arg > len(sys.argv):
            print 'ERROR: -tr <filename> missing parameter <filename>'
            exit(1)
        readFile(sys.argv[arg],authors)
        # -v <filename> adds <filename> to the validation set
    elif sys.argv[arg] == '-v':
        arg += 1
        if arg > len(sys.argv):
            print 'ERROR: -v <filename> missing parameter <filename>'
            exit(1)
        readFile(sys.argv[arg],authorsValidation)
         #-te <filename> adds <filename> to the test set

    elif sys.argv[arg] == '-te':
		arg += 1
		if arg > len(sys.argv):
		    print 'ERROR: - te <filename> missing parameter <filename>'
		    exit(1)
                readFile(sys.argv[arg],authorsTest)
                # -s enables stemming
    elif sys.argv[arg] == '-s':
                stemming_enabled = True

   
    # -s <method> uses <method> for smoothing, <method> in {n (none), a (addone), i (linear interpolation)}
    elif sys.argv[arg] == '-s':

        arg += 1
        if arg > len(sys.argv):
            print 'ERROR: - s <method> missing parameter <method>'
            exit(1)
        smoothing = sys.argv[arg]
        
    arg += 1
        
main()
                
print 'done'            
exit()