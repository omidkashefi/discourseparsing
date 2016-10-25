from bllipparser import RerankingParser

rrp = RerankingParser.from_unified_model_dir('/home/kashefi/.local/share/bllipparser/WSJ-PTB3')
print(rrp.simple_parse("It's that easy."))
