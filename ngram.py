import math
import nltk
import random
import sys

from nltk.corpus import brown
from nltk.tokenize import sent_tokenize

stemming_enabled = False
perplexity = None
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
	# -pp <filename> calculates the perplexity of the model given <filename> as test data
	elif sys.argv[arg] == '-pp':
		arg += 1
		if arg > len(sys.argv):
			print 'ERROR: -f <filename> missing parameter <filename>'
			exit(1)
		perplexity = open(sys.argv[arg], 'r')
	# -w <word> sets <word> as the first word in the sentence generator, otherwise chosen randomly
	elif sys.argv[arg] == '-w':
		arg += 1
		if arg > len(sys.argv):
			print 'ERROR: -w <word> missing parameter <word>'
			exit(1)
		seed_word = sys.argv[arg].lower() 
	# -l <length> sets the minimum sentence length to the number <length>
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
		seed_word = random_word()

# If seed_word is invalid, randomize seed_word
if seed_word not in bigram:
	seed_word = random_word()
	
		
# Count entries in models, for perplexity
total_uni=0
total_big=0
for words in unigram:
	total_uni+=unigram[words]
	
for key, dicts in bigram.items():
	for key,value in dicts.items():
		total_big+=value
	
			
#calculates perplexity, pass text passage & model='u' or 'b'
def perp(passage,model):
	p=0
	#parses test file into sentences
	for sent in sent_tokenize(passage):
		p=sentence_prob(sent,model,p)
	return math.pow(math.e, -1/len(unigram) *p)

#calculates log prob of a generated sentence wrt to model.
def sentence_prob(sent, model,p):
	n=0
	#retokenize
	sent2 = nltk.tokenize.regexp_tokenize(sent, pattern)
	n += len(sent2)
	#pr (A)*pr(b)*pr(C)...
	if model=='u':
		for words in sent2:
			if words.lower() in unigram:
				p+=math.log(unigram[words.lower()]/float(total_uni))
	#pr(A)*(B|A)...
	if model=='b': 
		if sent2[0].lower() in unigram:
			p+=math.log(unigram[sent2[0].lower()]/float(total_uni))
		for i in range(0,n-2):
			if sent2[i].lower() in bigram:
				if sent2[i+1].lower() in bigram[sent2[i].lower()]:
					p+=math.log(bigram[sent2[i].lower()][sent2[i+1].lower()]/float(total_big))
	return p

# Generate a random passage of pass_len sentences each of sent_len words 
curr_word = seed_word
prev_word = ''
for k in range(0, pass_len):
	i = 0
	sent = curr_word.capitalize()
	early_term = False
	while True:
		# Set of possible next words with relative frequency matching that of the corpus
		possible_words = []
		for w in bigram[curr_word]:
			# Don't allow punctuation if below min sentence length, don't allow sentence to end with punctuation
			if not ((w == '.' or w == '!' or w == '?') and i < sent_len -2):
				for j in range(0, bigram[curr_word][w]):
					possible_words.append(w)
		if len(possible_words) <= 0:
			# No possible word (must be punctuation) - need to end sentence.
			for w in bigram[curr_word]:
				sent += w
				break
			print sent + '\n'	
			curr_word = random_word()
			prev_word = ''
			break

		curr_word = possible_words[random.randint(0,len(possible_words)-1)]		
			
		if curr_word == '.' or curr_word == '!' or curr_word == '?':
			sent += curr_word 
			print sent + '\n'	
			curr_word = random_word()
			prev_word = ''
			break
		# Add space before current word, unless previous was an apostrophe or paranthesis
		elif (curr_word.isalpha() or curr_word == '(' or curr_word == '[') and not (prev_word == "'" 
																or prev_word == '(' or prev_word == '['):
			sent += ' '
		sent += curr_word
		prev_word = curr_word
		i += 1

if perplexity != None:
	print "Perplexity: ", perp(perplexity.read(), 'u')

