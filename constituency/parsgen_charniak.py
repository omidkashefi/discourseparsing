# -*- coding: utf-8 -*-

import sys, os
import re
import json
import spacy
from bllipparser import RerankingParser
from nltk.twitter.common import json2csv


if len(sys.argv) < 2:
    print("Invalid arguments!\nUsaeg: {0} <input>".format(os.path.basename(sys.argv[0])))
    exit()

parsejson = {}

nlp = spacy.load('en')

#PCFG parser
rrp = RerankingParser.from_unified_model_dir('/home/kashefi/.local/share/bllipparser/WSJ-PTB3')

f = ["draft1/", "draft2/"]
for fname in f:
    (_, _, filenames) = os.walk(os.path.join(sys.argv[1],fname)).next()

    for input_file in filenames:

        sys.stderr.write("Proccesing " + fname + input_file + "\n")

        file_text = open(os.path.join(os.path.join(sys.argv[1], fname), input_file)).read()

        # output param: DocID
        doc_id = os.path.basename(input_file) + "-" + fname.rstrip("/")

        # NLP pipeline parse by spacy
        doc = nlp(unicode(file_text))

        sentences = []
        #dependency parse
        for sent in doc.sents:
            # token index in sentence
            i = 1
            #constituency parser
            rsentence = ""

            for t in sent:
                if not t.is_space:
                    rsentence = rsentence + " " + t.text

            rsentence = rsentence.strip().replace('\t', ' ').replace('\n', ' ')

            if re.match("[a-z]+|[A-Z]+", rsentence) == None:
                continue;

            #sys.stderr.write(str(filter(None, str(rsentence).split(' ')))+ '\n')
            pcfg = rrp.simple_parse(filter(None, str(rsentence).split(' ')))
            #getting rid of (S1 )
            parsetree = pcfg[4:len(pcfg)-1]

            print parsetree
