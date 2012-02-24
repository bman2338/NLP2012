import nltk
import random
import sys

from nltk.corpus import brown

stemming_enabled = False
train = []
seed_word = ''
sent_len = 20
pass_len = 100
unigram = {}
bigram = {}

def random_word():
	possible_words = []
	for w in bigram:
		if w.isalpha():
			possible_words.append(w)
	return possible_words[random.randint(0,len(possible_words)-1)]

# Command line arguments
arg = 1
while arg < len(sys.argv):
	# -s enables stemming
	if sys.argv[arg] == '-s':
		stemming_enabled = True
	# -f <filename> adds <filename> to the train set
	elif sys.argv[arg] == '-f':
		arg += 1
		if arg > len(sys.argv):
			print 'ERROR: -f <filename> missing parameter <filename>'
			exit(1)
		train.append(open(sys.argv[arg], 'r'))
	# -w <word> sets <word> as the first word in the sentence generator, otherwise chosen randomly
	elif sys.argv[arg] == '-w':
		arg += 1
		if arg > len(sys.argv):
			print 'ERROR: -w <word> missing parameter <word>'
			exit(1)
		seed_word = sys.argv[arg].lower() 
	# -l <length> sets the sentence length to the number <length>
	elif sys.argv[arg] == '-l':
		arg += 1
		if arg > len(sys.argv):
			print 'ERROR: -l <length> missing parameter <length>'
			exit(1)
		sent_len = int(sys.argv[arg])
	# -p <length> sets the passage length to the number <length>
	elif sys.argv[arg] == '-p':
		arg += 1
		if arg > len(sys.argv):
			print 'ERROR: -p <length> missing parameter <length>'
			exit(1)
		pass_len = int(sys.argv[arg])
	arg += 1


# Porter Stemmer for getting the stems of words
stemmer = nltk.PorterStemmer()

# Regex pattern for tokenizing the corpus, accounts for acronyms, etc.
pattern = r'''(?x)  
	  \w+		
	  | \$?\d+(\.\d+)?
	  | ([A-Z]\.)+		
	  | [^\w\s]+		
	  '''

# Tokenizes the words in the training file
train_words = []
for book in train:
	train_words.append(nltk.tokenize.regexp_tokenize(book.read(), pattern))

# Stems the words if stemming is enabled
if stemming_enabled:
	for words in train_words:
		for i in range(0,len(words)):
			words[i] = stemmer.stem(words[i])

# Counts up unigram and bigram counts
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
		unigram[w1] += 1
		bigram[w1][w2] += 1
	unigram[words[i].lower()] += 1
	# Set the starting word for the sentence generator
	if seed_word == '':
		seed_word = words[i].lower()

# If seed_word is invalid, randomize seed_word
if seed_word not in bigram:
	seed_word = random_word()

# Generate a random passage of pass_len sentences each of sent_len words 
curr_word = seed_word
for k in range(0, pass_len):
	sent = curr_word.capitalize()
	early_term = False
	for i in range(0, sent_len-1):
		# Set of possible next words with relative frequency matching that of the corpus
		possible_words = []
		for w in bigram[curr_word]:
			if w.isalpha():
				for j in range(0, bigram[curr_word][w]):
					possible_words.append(w)
		if len(possible_words) <= 0:
			early_term = True
			break
		curr_word = possible_words[random.randint(0,len(possible_words)-1)]
		sent += ' '
		sent += curr_word
	sent += '.'
	print sent + '\n'	
	if early_term:
		curr_word = random_word()

