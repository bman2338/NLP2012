import nltk

from nltk.corpus import brown

mappings = {} # maps from word to info about the word
stemmer = nltk.PorterStemmer() 
stopwords = nltk.corpus.stopwords.words('english')

a = 0
for line in open("Data/train.data"):
    a += 1
    print a
    words = line.split()
    currentmap = mappings.setdefault(words[0], {})
    x = 1
    senses = []
    while words[x] != '@':
        if words[x] == '1':
            senses.append(x-1)
        x += 1
    x += 1
    
    while x < len(words):
        word = words[x].lower()
        x += 1
        if word in stopwords or len(word) == 1: # ignore stopwords and punctuation
            continue
        if (word[0] != '@'): # not the word we're analyzing
            word = stemmer.stem(word)
            for sense in senses:
                sensemap = currentmap.setdefault(sense, {'form' : {}, 'words' : {}, 'nearby': {}})
                count = sensemap['words'].setdefault(word, 0)
                sensemap['words'][word] = count + 1
        else:
            for sense in senses:
                sensemap = currentmap.setdefault(sense, {'form' : {}, 'words' : {}, 'nearby': {}})
                count = sensemap['form'].setdefault(word.strip('@'), 0)
                sensemap['form'][word.strip('@')] = count + 1
				
                # include all words within two words of the target
                for index in range(max(0, x-2), min(len(words), x+3)): 
                    if index == x-1: # don't include target word
                        continue
                    nearword = stemmer.stem(words[index].lower())
                    count = sensemap['nearby'].setdefault(nearword, 0)
                    sensemap['nearby'][nearword] = count + 1
					

out = open('mostcommon.txt', 'w')
for word in mappings:
    out.write(word + ":\n")
    for sense in sorted(mappings[word].keys(), key = lambda x : int(x)):
        out.write('\t' + str(sense) + ":\n")
        out.write("\t\tForms:\n")
        for form in sorted(mappings[word][sense]['form'].items(), key = lambda x : -x[1]):
            out.write("\t\t\t" + str(form[1]) + " " + form[0] + "\n")
        out.write("\t\tRelated stems:\n")
        for words in sorted(mappings[word][sense]['words'].items(), key = lambda x : -x[1])[:5]:
            out.write("\t\t\t" + str(words[1]) + " " + words[0] + "\n")
        out.write("\t\tNearby stems:\n")
        for words in sorted(mappings[word][sense]['nearby'].items(), key = lambda x : -x[1])[:5]:
            out.write("\t\t\t" + str(words[1]) + " " + words[0] + "\n")
out.close()
        
    