from bllipparser import RerankingParser

rrp = RerankingParser.from_unified_model_dir('/home/kashefi/.local/share/bllipparser/WSJ-PTB3')
sentence = "In the 3rd level I would place my little brother in. because my little brother is a very greedy little bot he always wants something."

pcfg = rrp.simple_parse(sentence.split(' '))
pcfg = pcfg[4:len(pcfg)-1]
print pcfg
'''
pcfg = rrp.simple_parse(sentence)
pcfg = pcfg[4:len(pcfg)-1]
print(pcfg)
'''
