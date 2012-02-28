#python authors.py -tr EnronDataset/train.txt -te EnronDataset/test.txt

import nltk
import random
import sys

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
def buildGrams(email,unigram,bigram):
    train_words = []
    train_words.append(nltk.tokenize.regexp_tokenize(email, pattern))
    for words in train_words:
            for i in range(0,len(words)-1):
                w1 = words[i].lower()
                w2 = words[i+1].lower()
                if w1 not in unigram:
                        unigram[w1] = 0
                if w1 not in bigram:
                        bigram[w1] = {}
                if w2 not in bigram[w1]:
                        bigram[w1][w2] = 0
                if not (w1 in authors.keys()):
                    unigram[w1] += 1
                if not (w2 in authors.keys()):
                    bigram[w1][w2] += 1
    return (unigram,bigram)
            

def main():
    
    # Train each authors unigrams and bigrams using all their emails
    for author in authors.keys():
        authorUnigrams[author] = {}
        authorBigrams[author] = {}
        unigram = authorUnigrams[author]
        bigram = authorBigrams[author]
        for email in authors[author]:
            (unigram,bigram) = buildGrams(email,unigram,bigram)
            authorUnigrams[author] = unigram
            authorBigrams[author] = bigram
        normalizedAuthorUnigrams[author] = normUnigram(authorUnigrams[author])
        normalizedAuthorBigrams[author] = normBigram(authorUnigrams[author],authorBigrams[author])
        
        
    if len(authorsValidation) != 0:
        print classifyEmails(authorsValidation)
            
    if len(authorsTest) != 0:
        print classifyEmails(authorsTest)
    
    

def normUnigram(unigrams):
    normUnigrams = {}
    listSum = sum(unigrams.values())
    for x in unigrams.keys():
        normUnigrams[x] = float(unigrams[x])/listSum
    return normUnigrams

def normBigram(unigrams, bigrams):
    normBigrams = {}
    for w1 in bigrams.keys():
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
                
    return normBigrams

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

def classifyEmails(emails):
    numCorrect = 0
    total = 0
    
    for author in emails.keys():
        for email in emails[author]:
            print total
            total +=1
            if author == predictAuthor(email):
                numCorrect +=1
    return float(numCorrect) / total
        
        
def predictAuthor(email):
    authorsUtility = {}
    emailUnigrams = {}
    emailBigrams = {}
    (emailUnigrams,emailBigrams) = buildGrams(email,emailUnigrams,emailBigrams)
    emailUnigramNorm = normUnigram(emailUnigrams)
    emailBigramNorm = normBigram(emailUnigrams,emailBigrams)
    
    additionalUnigrams = 0
    
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
        
        for emailUnigramKey in emailUnigrams.keys():
            if emailUnigramKey in smoothedAuthorUnigrams:
                authorsUtility[author] += smoothedAuthorUnigrams[emailUnigramKey] * emailUnigramNorm[emailUnigramKey]
        
        for key in emailBigrams.keys():
            for key2 in emailBigrams[key]:
                if key in smoothedAuthorBigrams and key2 in smoothedAuthorBigrams[key]:
                    authorsUtility[author] += smoothedAuthorBigrams[key][key2] * emailBigramNorm[key][key2]
                   
    
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