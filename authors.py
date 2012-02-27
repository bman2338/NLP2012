#python authors.py -tr EnronDataset/train.txt -te EnronDataset/test.txt

import nltk
import random
import sys

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
                    if w1.isalpha():
                        unigram[w1] += 1
                    if w2.isalpha():
                        bigram[w1][w2] += 1
                    if words[i].lower().isalpha():
                        unigram[words[i].lower()] += 1
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
    

def classifyEmails(emails):
    numCorrect = 0
    total = 0
    for author in emails.keys():
        for email in emails[author]:
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
    for author in authors.keys():
        authorsUtility[author] = 0;
        
        for emailUnigramKey in emailUnigrams.keys():
            if emailUnigramKey in normalizedAuthorUnigrams[author]:
                authorsUtility[author] += normalizedAuthorUnigrams[author][emailUnigramKey] * emailUnigramNorm[emailUnigramKey]
        
        for key in emailBigrams.keys():
            for key2 in emailBigrams[key]:
                if key in normalizedAuthorBigrams[author] and key2 in normalizedAuthorBigrams[author][key]:
                    authorsUtility[author] += normalizedAuthorBigrams[author][key][key2] * emailBigramNorm[key][key2]
                   
    
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
        arg += 1
main()
                
print 'done'            
exit()