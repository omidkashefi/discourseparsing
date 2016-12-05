from nltk.parse.stanford import StanfordParser
import re, nltk

parser = StanfordParser()
sentence = "In the 3rd level I would place my little brother in. because my little brother is a very greedy little bot he always wants something."
#print nltk.pos_tag(sentence.split(' '))
#pcfg = parser.raw_parse(sentence)
pcfg = parser.tagged_parse(nltk.pos_tag(sentence.split(' ')))
#getting rid of (S1 )
parsetree = re.sub("\s+", " ", str(list(pcfg)[0][0]).replace("\n", "").replace("ROOT", "")) + "\n"

print parsetree
