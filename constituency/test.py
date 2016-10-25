from bllipparser import RerankingParser

rrp = RerankingParser.from_unified_model_dir('/home/kashefi/.local/share/bllipparser/WSJ-PTB3')
sentence = "<s> Hell is somewhere where none of us want to end up spending the rest of our lives. </s>"
pcfg = rrp.simple_parse(sentence)
pcfg = pcfg[4:len(pcfg)-1]
print(pcfg)
