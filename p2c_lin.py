import sys, os, re
import json
import spacy


tokenDic = {}

def init(doc):
    global tokenDic
    tokenDic = {}

    sentIndex = 0
    for sent in doc.sents:

        #if re.match("[a-z]+|[A-Z]+", sent.text) == None:
        #    continue;

        tokenInSentIndex = 0
        for token in sent:
            tokenDic[token] = [0, tokenInSentIndex, sentIndex]
            tokenInSentIndex += 1
        sentIndex += 1

    tokenInDocIndex = 0
    for token in doc:
        if token not in tokenDic:
            continue

        tokenDic[token] = [tokenInDocIndex, tokenDic[token][1], tokenDic[token][2]]
        tokenInDocIndex += 1

    #print tokenDic

def extractSpan(doc, span):
    global tokenDic

    charSpan = []
    tokenList = []
    rawText = ""
    for start, end in span:
        charSpan.append([start, end])
        rawText = rawText + str(doc.text[start:end]) + ";"
        for token in tokenDic:
            if start <= token.idx and token.idx <= end:
                #tokenList.insert(0, [token.idx, token.idx + len(token) if end != 0 else 0, tokenDic[token][0], tokenDic[token][2], tokenDic[token][1]])
                tokenList.insert(0, tokenDic[token][0])

    if len(tokenList) == 0:
        tokenList.insert(0, -1)

    return {"CharacterSpanList": charSpan, "RawText": rawText.rstrip(';'), "TokenList": sorted(tokenList)}

def extractSpanFromText(doc, txt):
    global tokenDic

    charSpan = []
    tokenList = []
    rawText = ""

    for t in txt:
        start = doc.text.find(t)
        if start == -1:
            start = doc.text.find(t[0:min(len(txt), 10)])
        end = start + len(t)
        rawText = rawText + t + ";"

        if start != -1:
            charSpan.append([start, end])
            for token in tokenDic:
                if start <= token.idx and token.idx <= end:
                    #tokenList.insert(0, [token.idx, token.idx + len(token) if end != 0 else 0, tokenDic[token][0], tokenDic[token][2], tokenDic[token][1]])
                    tokenList.insert(0, tokenDic[token][0])

    if len(tokenList) == 0:
        tokenList.insert(0, -1)

    return {"CharacterSpanList": charSpan, "RawText": rawText.rstrip(';'), "TokenList": sorted(tokenList)}

def main(argv):

    f = ["draft1/", "draft2/"]
    nlp = spacy.load('en')
    id = 9999
    output = {}
    for fname in f:
        (_, _, filenames) = os.walk(os.path.join(argv[1],fname)).next()

        for input_file in filenames:
            sys.stderr.write("Proccesing " + fname + input_file + "\n")

            parsejson = []
            # output param: DocID
            doc_id = os.path.basename(input_file.rstrip(".pipe")) + "-" + fname.rstrip("/")

            annotated_file = os.path.join(os.path.join(sys.argv[1], fname), input_file)
            if not os.path.isfile(annotated_file):
                continue

            raw_file = os.path.join(sys.argv[1]+"../raw/"+fname, input_file.rstrip(".pipe"))
            if not os.path.isfile(raw_file):
                continue

            raw_file_text = open(raw_file).read()

            # NLP pipeline parse by spacy
            doc = nlp(unicode(raw_file_text))
            init(doc)

            file_text = open(annotated_file)
            for line in file_text:
                id += 1

                if line.startswith("EntRel"):
                    parts = line.split('|')

                    rtype = parts[0]

                    txt = parts[24].split(';')
                    arg1 = extractSpanFromText(doc, txt)
                    #if len(arg1["CharacterSpanList"]) == 0:
                    #    continue

                    txt2 = parts[34].split(';')
                    arg2 = extractSpanFromText(doc, txt2)
                    #if len(arg2["CharacterSpanList"]) == 0:
                    #    continue

                    #no connective fot EntRel
                    span = [[0, 0]]
                    connective = extractSpan(doc, span)

                    #ne sense for EntRel
                    sense = []

                    j = {"Arg1": arg1, "Arg2": arg2, "Connective": connective, "DocID": doc_id, "ID": id, "Sense": sense, "Type": rtype}
                    print(json.dumps(j, sort_keys=True))

                    #parsejson.append({"ID": id, "Arg1": arg1['CharacterSpanList'], "Arg2": arg2['CharacterSpanList']})

                if line.startswith("AltLex"):
                    parts = line.split('|')

                    rtype = parts[0]

                    span = []
                    spanStr = parts[14].split(';')
                    for s in spanStr:
                        start = int(s.split('..')[0])
                        end = int(s.split('..')[1])
                        span.append([start, end])

                    arg1 = extractSpan(doc, span)

                    span = []
                    spanStr = parts[20].split(';')
                    for s in spanStr:
                        start = int(s.split('..')[0])
                        end = int(s.split('..')[1])
                        span.append([start, end])

                    arg2 = extractSpan(doc, span)

                    span = []
                    spanStr = parts[1].split(';')
                    for s in spanStr:
                        start = int(s.split('..')[0])
                        end = int(s.split('..')[1])
                        span.append([start, end])

                    connective = extractSpan(doc, span)

                    sense = [parts[8]]

                    j = {"Arg1": arg1, "Arg2": arg2, "Connective": connective, "DocID": doc_id, "ID": id, "Sense": sense, "Type": rtype}
                    print(json.dumps(j, sort_keys=True))

                    #parsejson.append({"ID": id, "Arg1": arg1['CharacterSpanList'], "Arg2": arg2['CharacterSpanList']})

                if line.startswith("Implicit"):
                    parts = line.split('|')

                    rtype = parts[0]

                    txt = parts[24].split(';')
                    arg1 = extractSpanFromText(doc, txt)
                    #if len(arg1["CharacterSpanList"]) == 0:
                    #    continue

                    txt2 = parts[34].split(';')
                    arg2 = extractSpanFromText(doc, txt2)
                    #if len(arg2["CharacterSpanList"]) == 0:
                    #    continue

                    #no connective
                    span = [[0, 0]]
                    connective = extractSpan(doc, span)
                    #connective["RawText"] = parts[7]

                    sense = [parts[11]]

                    j = {"Arg1": arg1, "Arg2": arg2, "Connective": connective, "DocID": doc_id, "ID": id, "Sense": sense, "Type": rtype}
                    print(json.dumps(j, sort_keys=True))

                    #parsejson.append({"ID": id, "Arg1": arg1['CharacterSpanList'], "Arg2": arg2['CharacterSpanList']})

                if line.startswith("Explicit"):
                    parts = line.split('|')

                    rtype = parts[0]

                    span = []
                    spanStr = parts[22].split(';')
                    for s in spanStr:
                        if s == '':
                            span = [[0, 0]]
                        else:
                            start = int(s.split('..')[0])
                            end = int(s.split('..')[1])
                            span.append([start, end])

                    arg1 = extractSpan(doc, span)

                    span = []
                    spanStr = parts[32].split(';')
                    for s in spanStr:
                        if s == '':
                            span = [[0, 0]]
                        else:
                            start = int(s.split('..')[0])
                            end = int(s.split('..')[1])
                            span.append([start, end])

                    arg2 = extractSpan(doc, span)

                    span = []
                    spanStr = parts[3].split(';')
                    for s in spanStr:
                        start = int(s.split('..')[0])
                        end = int(s.split('..')[1])
                        span.append([start, end])

                    connective = extractSpan(doc, span)

                    '''
                    print(doc_id + "\texp:\t" + connective["RawText"])
                    print(doc_id + "\targ:\t" + arg1["RawText"])
                    print(doc_id + "\targ:\t" + arg2["RawText"])
                    '''

                    sense = [parts[11]]

                    j = {"Arg1": arg1, "Arg2": arg2, "Connective": connective, "DocID": doc_id, "ID": id, "Sense": sense, "Type": rtype}
                    print(json.dumps(j, sort_keys=True))

                    #parsejson.append({"ID": id, "Arg1": arg1['CharacterSpanList'], "Arg2": arg2['CharacterSpanList']})

            output.update({doc_id: {"relations": parsejson}})


    #print(json.dumps(output, sort_keys=True))



if len(sys.argv) < 2:
    print("Invalid arguments!\nUsaeg: {0} <input>".format(os.path.basename(sys.argv[0])))
    exit()

main(sys.argv)
