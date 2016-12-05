# -*- coding: utf-8 -*-

import sys, os
import re
import json
import spacy
from bllipparser import RerankingParser
from nltk.twitter.common import json2csv


def findLinker(span, doc_id):
    global relations
    linker = []

    for r in relations[doc_id]['relations']:
        for s in r["Arg1"]:
            if span[0] >= s[0] and span[1] <= s[1]:
                linker.append('arg1_' + str(r['ID']))
                break
        for s in r["Arg2"]:
            if span[0] >= s[0] and span[1] <= s[1]:
                linker.append('arg2_' + str(r['ID']))
                break

    return linker

if len(sys.argv) < 2:
    print("Invalid arguments!\nUsaeg: {0} <input>".format(os.path.basename(sys.argv[0])))
    exit()

#to find links
with open('helper.json') as data_file:
    relations = json.load(data_file)

'''
with open('parse.json') as data_file:
    pre = json.load(data_file)
'''

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

        '''
        if doc_id != "muscleman1995 - Sword Writing 1.txt-draft2":
            sentences = pre[doc_id]["sentences"]
            parsejson.update({doc_id: {"sentences": sentences}})
            continue
        '''

        # NLP pipeline parse by spacy
        doc = nlp(unicode(file_text))

        sentences = []
        #dependency parse
        for sent in doc.sents:
            # token index in sentence
            i = 1
            tokend_dic = {}
            words = []
            for token in sent:
                if not token.is_space:
                    first = token.text
                    second = {"CharacterOffsetBegin": token.idx, \
                              "CharacterOffsetEnd": token.idx + len(token), \
                              "Linkers": findLinker([token.idx, token.idx], doc_id),\
                              "PartOfSpeech": token.tag_}

                    words.append([first, second])

                    tokend_dic[token] = i
                    i += 1

            #dependency parse
            dependencies = []
            for token in sent:
                if not token.is_punct and not token.head.is_punct and not token.is_space:
                    first = token.dep_
                    second = "{0}-{1}".format("ROOT" if token.dep_ == "ROOT" else token.head, "0" if token.dep_ == "ROOT" else tokend_dic[token.head])
                    third = "{0}-{1}".format(token, tokend_dic[token])
                    d = [first, second, third]
                    dependencies.append(d)

            #constituency parser
            rsentence = ""

            for t in sent:
                if not token.is_space:
                    rsentence = rsentence + " " + t.text

            rsentence = rsentence.strip().replace('\t', ' ').replace('\n', ' ')

            if re.match("[a-z]+|[A-Z]+", rsentence) == None:
                continue;

            sys.stderr.write(str(filter(None, str(rsentence).split(' ')))+ '\n')
            pcfg = rrp.simple_parse(filter(None, str(rsentence).split(' ')))
            #getting rid of (S1 )
            parsetree = pcfg[4:len(pcfg)-1]

            sentences.append({"dependencies": dependencies, "parsetree": parsetree, "words": words})

        parsejson.update({doc_id: {"sentences": sentences}})

print(json.dumps(parsejson, sort_keys=True))
