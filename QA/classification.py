import re
import nltk

from collections import defaultdict
from nltk.corpus import wordnet
from nltk.tokenize import PunktSentenceTokenizer
from operator import itemgetter
from sets import Set
from subprocess import call

types=defaultdict(str)
stopwords = nltk.corpus.stopwords.words('english')
tokenizer = PunktSentenceTokenizer()

def getSentences(number):
    sentences = [] 
    inText = False 
    text = ""
    for line in file("./train/docs/top_docs." + number):
        if line[:6] == "<TEXT>":
            inText = True
            text += line[6:].strip()
            continue
        
        if not inText:
            continue
        
        if line[-8:-1] == "</TEXT>":
            inText = False
            text += " " + line[:-8].strip()
            sentences.extend(tokenizer.tokenize(text))
            text = ""
            continue
        
        text += " " + line.strip()
        
    return sentences
            

def classify(type, question, number):
    questionTerms = Set()
    questionSynonyms = Set()
    for word in question.split():
        word = word.strip("?")
        
        if word in ["what", "name", "who", "when", "how", "where", "why"] or word.lower() in stopwords:
            continue
        
        if not word.islower():
            questionTerms.add(word.lower())
            continue        
        
        questionTerms.add(word)
        syns = wordnet.synsets(word)
        for lemmaname in [lemma.name for syn in syns for lemma in syn.lemmas]:
            if "_" not in lemmaname:
                questionSynonyms.add(lemmaname.lower())
        questionSynonyms.discard(word)

    print question, questionTerms, questionSynonyms
        
    if type == "what":
        pass
    
    elif type == "name":
        pass
    
    elif type == "whodid":
        pass
    
    elif type == "whois":
        pass
    
    elif type == "whoisverb":
        pass
    
    elif type == "when":
        pass
    
    elif type == "how":
        pass
    
    elif type == "where":
        pass
     
    elif type == "why":
        pass

qlist=['what','name','who','when','how','where','why']
questionfilename='./train/questions.txt'
questionfile=open(questionfilename,'r')
seq=''
questions=[]
for line in questionfile:
    line=line.strip()
    if line=='<top>':
        s=seq.split('Description:')
        if len(s)>1:
            questions.append(s[1])
            numb=s[0].split('Number: ')
            numb=re.findall('[0-9]+',numb[1])
            numb=numb[0]
            typeofq=s[1].split(' ')
            cq=s[1].split('</top>')
            curq=[]
            curq.append(cq[0])
            curq.append(numb)
            curqlist=cq[0].split(' ')
            typeofq=typeofq[0].split('\'')
            start=typeofq[0]
            start=start.lower()
            if start in qlist:
                if start in types:
                    templist = types[start]
                    templist.append(curq)
                    types[start]=templist
                else:
                    types[start]=[curq]

            else:
                for word in curqlist:
                    word=word.lower()
                    word=re.findall('[A-Za-z]+',word)
                    word=word[0]
                    if word in qlist:
                        if word in types:
                            templist = types[word]
                            templist.append(curq)
                            types[word]=templist
                        else:
                            types[start]=[curq]
                    else:
                        continue
        seq=''
        seq+=line
    else:
        seq+=line


wholist=types['who']
types['whois']=[]
types['whodid']=[]
types['whoisverb']=[]
for q in wholist:
    q1=q[0]
    text = nltk.word_tokenize(q1)
    tag=nltk.pos_tag(text)
    listoftags=[]
    if (tag[1][0]=='is' or tag[1][0]=='was'):
        f=0
        for i in range(2,len(tag)):
            if (tag[i][1]=='VB' or tag[i][1]=='VBD' or tag[i][1]=='VBN' or tag[i][1]=='VBZ') :
                if ('NNP' in listoftags) or ('NN' in listoftags):
                    f=1
                    break
            else:
                listoftags.append(tag[i][1])
        if f==1:
            types['whoisverb'].append(q)
        else:
            types['whois'].append(q)
    else:
        types['whodid'].append(q)
   

for type, list in types.iteritems():
    if type=='who':
        continue
    for item in list:
        question = item[0]
        number = item[1]
        classify(type, question, number)

    
#sum1=0  
#for k,v in types.iteritems():
#    if k=='who':
#        continue
#    else:
#        sum1+=len(v)
#        filetowrite=open('questionclass_'+str(k)+'.txt','w')
#        for l in v:
#            qnum=l[1]
#            qtext=l[0]
#            filetowrite.write(str(qnum)+':'+str(qtext)+'\n')
#            
#        filetowrite.close()
#print sum1
