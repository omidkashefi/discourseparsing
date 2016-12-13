# -*- coding: utf-8 -*-

import sys, os
import codecs
import json
import spacy
from nltk.twitter.common import json2csv
from conn_head_mapper import ConnHeadMapper

def readGS(filename):
    global gs_relations
    global gs_rel_count
    global gs_rel_type_count
    global gs_rel_sense_count

    gs_file = codecs.open(filename, encoding='utf8')
    for x in gs_file:
        gs_rel_count += 1

        j = json.loads(x)
        doc_id = j['DocID']

        rel_id = j['ID']

        arg1 = []
        for a1 in j['Arg1']['TokenList']:
            arg1.append(a1[2])

        arg2 = []
        for a2 in j['Arg2']['TokenList']:
            arg2.append(a2[2])

        con_tlist = []
        for c in j['Connective']['TokenList']:
            con_tlist.append(c[2])
        rel_conn = {'RawText': j['Connective']['RawText'], 'TokenList': con_tlist}

        rel_sense = j['Sense'][0] if len(j['Sense']) > 0 else ''
        gs_rel_sense_count[rel_sense] += 1 if len(j['Sense']) > 0 else 0

        rel_type =  j['Type']
        gs_rel_type_count[rel_type] += 1

        if doc_id not in gs_relations:
            gs_relations.update({doc_id: [{'Arg1': arg1, 'Arg2': arg2, 'Connective': rel_conn, 'Sense': rel_sense, 'Type': rel_type, 'ID': rel_id}]})
        else:
            gs_relations[doc_id].append({'Arg1': arg1, 'Arg2': arg2, 'Connective': rel_conn, 'Sense': rel_sense, 'Type': rel_type, 'ID': rel_id})

    #print(json.dumps(gs_relations, sort_keys = True))
    #gs_relations = json.loads(json.dumps(gs_relations, sort_keys = True))

def evalSO(filename):
    global so_rel_count
    global so_rel_type_count
    global so_rel_sense_count

    global so_matching_type_count
    global so_matching_sense_count_ex
    global so_matching_sense_count_nex
    global so_matching_args_count_ex
    global so_matching_args_count_nex
    global so_matching_connective_count_ex
    global so_matched_e2e_count
    global so_relations

    global gs_relations

    processed_id = []

    chm = ConnHeadMapper()
    os_file = codecs.open(filename, encoding='utf8')
    for x in os_file:
        so_rel_count += 1

        j = json.loads(x)
        doc_id = j['DocID']

        arg1 = []
        for a1 in j['Arg1']['TokenList']:
            arg1.append(a1)

        arg2 = []
        for a2 in j['Arg2']['TokenList']:
            arg2.append(a2)

        con_tlist = []

        for c in j['Connective']['TokenList']:
            con_tlist.append(c)
        if j['Type'] == 'Explicit':
            rel_conn = {'RawText': j['conn_name'], 'TokenList': con_tlist}
        else:
            rel_conn = {'RawText': "", 'TokenList': con_tlist}

        rel_sense = j['Sense'][0].split('.')[0] if len(j['Sense']) > 0 else ''
        so_rel_sense_count[rel_sense] += 1 if len(j['Sense']) > 0 else 0

        rel_type =  j['Type']
        so_rel_type_count[rel_type] += 1


        #print(gs_relations)
        #print(gs_relations[doc_id])
        #evaluation process
        for r in gs_relations[doc_id]:
            #if r["ID"] in processed_id:
            #    continue
            find_arg1 = False
            find_arg2 = False
            find_connective = False
            find_sense = False

            #Arg 1
            #print(r)
            #print(r['Arg1'])
            #print(arg1)
            if abs(sorted(r['Arg1'])[0] - sorted(arg1)[0]) <= 5 and abs(sorted(r['Arg1'])[-1] - sorted(arg1)[-1]) <= 5:
                #processed_id.append(r["ID"])
                find_arg1 = True
                if rel_type == "Explicit":
                    so_matching_args_count_ex["Arg1"] += 1
                else:
                    so_matching_args_count_nex["Arg1"] += 1

            #Arg2
            if abs(sorted(r['Arg2'])[0] - sorted(arg2)[0]) <= 5 and abs(sorted(r['Arg2'])[-1] - sorted(arg2)[-1]) <= 5:
                #processed_id.append(r["ID"])
                find_arg2 = True
                if rel_type == "Explicit":
                    so_matching_args_count_ex["Arg2"] += 1
                else:
                    so_matching_args_count_nex["Arg2"] += 1

            #Arg1/2
            if find_arg1 and find_arg2:
                #processed_id.append(r["ID"])
                if rel_type == "Explicit":
                    so_matching_args_count_ex["Arg12"] += 1
                else:
                    so_matching_args_count_nex["Arg12"] += 1

            #Connective
            if rel_type == "Explicit":
                head_connective_gs, i = chm.map_raw_connective(r['Connective']['RawText'])
                head_connective_so, i = chm.map_raw_connective(rel_conn['RawText'])

                if ((abs(sorted(r['Connective']['TokenList'])[0] - sorted(rel_conn['TokenList'])[0]) <= 2 and \
                    abs(sorted(r['Connective']['TokenList'])[-1] - sorted(rel_conn['TokenList'])[-1]) <= 2)) or \
                    (head_connective_so.find(head_connective_gs) != -1 and (find_arg1 or find_arg2)):
                    #processed_id.append(r["ID"])
                    find_connective = True
                    so_matching_connective_count_ex += 1

            #Sense
            '''
            if rel_sense == r['Sense']:
                find_sense = True
                if rel_type == "Explicit":
                    so_matching_sense_count_ex[rel_sense] += 1
                else:
                    so_matching_sense_count_nex[rel_sense] += 1

            #Type
            so_rel_type_count[rel_sense] += 1
            if rel_type == r['Type']:
                so_matching_type_count[rel_type] += 1
            '''

            #PARSE
            if find_arg1 and find_arg2 and (find_connective or rel_type != "Explicit"):
                so_matched_e2e_count += 1
                break

            if find_connective:
                break


if len(sys.argv) < 3:
    print("Invalid arguments!\nUsaeg: {0} <gold_standard> <system_output>".format(os.path.basename(sys.argv[0])))
    exit()

#read gold-standard
gs_rel_count = 0.0
gs_rel_type_count = {"Explicit": 0.0, "EntRel": 0.0, "Implicit": 0.0, "AltLex": 0.0}
gs_rel_sense_count = {"Comparison": 0.0, "Expansion": 0.0, "Temporal": 0.0, "Contingency": 0.0, "EntRel": 0.0, "": 0.0}
gs_relations = {}

readGS(sys.argv[1])

#read system output
so_rel_count = 0.0
so_rel_type_count = {"Explicit": 0.0, "EntRel": 0.0, "Implicit": 0.0, "AltLex": 0.0}
so_rel_sense_count = {"Comparison": 0.0, "Expansion": 0.0, "Temporal": 0.0, "Contingency": 0.0, "EntRel": 0.0, "": 0.0}

so_matched_e2e_count = 0.0
so_matching_type_count = {"Explicit": 0.0, "EntRel": 0.0, "Implicit": 0.0, "AltLex": 0.0}
so_matching_sense_count_ex = {"Comparison": 0.0, "EntRel": 0.0, "Expansion": 0.0, "Temporal": 0.0, "Contingency": 0.0, "EntRel": 0.0, "": 0.0}
so_matching_sense_count_nex = {"Comparison": 0.0, "EntRel": 0.0, "Expansion": 0.0, "Temporal": 0.0, "Contingency": 0.0, "EntRel": 0.0, "": 0.0}
so_matching_args_count_ex = {"Arg1": 0.0, "Arg2": 0.0, "Arg12": 0.0}
so_matching_args_count_nex = {"Arg1": 0.0, "Arg2": 0.0, "Arg12": 0.0}
so_matching_connective_count_ex = 0.0

evalSO(sys.argv[2])


print("Gold Standard\n----------------------------\n\n")
print("Relation #:\t", gs_rel_count)
print("Type Count:\t", gs_rel_type_count)
print("Sense Count:\t", gs_rel_sense_count)

print("\n\nSystem Output\n----------------------------\n")
print("Relation #:\t", so_rel_count)
print("Type Count:\t", so_rel_type_count)
print("Sense Count:\t", so_rel_sense_count)

print("Matching Type Count:\t", so_matching_type_count)
print("Matching Explicit Sense Count:\t", so_matching_sense_count_ex)
print("Matching Non-Explicit Sense Count:\t", so_matching_sense_count_nex)
print("Matching Explicit Args Count:\t", so_matching_args_count_ex)
print("Matching Non-Explicit Args Count:\t", so_matching_args_count_nex)
print("Matching Connective Count:\t", so_matching_connective_count_ex)
print("Matching End-To-End Count:\t", so_matched_e2e_count)

print("---------------------------------------------\n")
print("Arg1 N-Ex")
p = so_matching_args_count_nex['Arg1']/(so_rel_count - so_rel_type_count['Explicit'])
r = so_matching_args_count_nex['Arg1']/(gs_rel_count - gs_rel_type_count['Explicit'])
f = (2*p*r)/(p+r)
print("P: {0}\tR: {1}, F: {2}\n".format(p, r, f))

print("Arg2 N-Ex")
p = so_matching_args_count_nex['Arg2']/(so_rel_count - so_rel_type_count['Explicit'])
r = so_matching_args_count_nex['Arg2']/(gs_rel_count - gs_rel_type_count['Explicit'])
f = (2*p*r)/(p+r)
print("P: {0}\tR: {1}, F: {2}\n".format(p, r, f))

print("Arg1/2 N-Ex")
p = so_matching_args_count_nex['Arg12']/(so_rel_count - so_rel_type_count['Explicit'])
r = so_matching_args_count_nex['Arg12']/(gs_rel_count - gs_rel_type_count['Explicit'])
f = (2*p*r)/(p+r)
print("P: {0}\tR: {1}, F: {2}\n".format(p, r, f))

print("Arg1 Ex")
p = so_matching_args_count_ex['Arg1']/so_rel_type_count['Explicit']
r = so_matching_args_count_ex['Arg1']/gs_rel_type_count['Explicit']
f = (2*p*r)/(p+r)
print("P: {0}\tR: {1}, F: {2}\n".format(p, r, f))

print("Arg2 Ex")
p = so_matching_args_count_ex['Arg2']/so_rel_type_count['Explicit']
r = so_matching_args_count_ex['Arg2']/gs_rel_type_count['Explicit']
f = (2*p*r)/(p+r)
print("P: {0}\tR: {1}, F: {2}\n".format(p, r, f))

print("Arg1/2 Ex")
p = so_matching_args_count_ex['Arg12']/so_rel_type_count['Explicit']
r = so_matching_args_count_ex['Arg12']/gs_rel_type_count['Explicit']
f = (2*p*r)/(p+r)
print("P: {0}\tR: {1}, F: {2}\n".format(p, r, f))

print("Connective")
p = so_matching_connective_count_ex/so_rel_type_count['Explicit']
r = so_matching_connective_count_ex/gs_rel_type_count['Explicit']
f = (2*p*r)/(p+r)
print("P: {0}\tR: {1}, F: {2}\n".format(p, r, f))

print("Arg")
p = (so_matching_args_count_ex['Arg12'] + so_matching_args_count_nex['Arg12'])/so_rel_count
r = (so_matching_args_count_ex['Arg12'] + so_matching_args_count_nex['Arg12'])/gs_rel_count
f = (2*p*r)/(p+r)
print("P: {0}\tR: {1}, F: {2}\n".format(p, r, f))

print("End to End")
p = so_matched_e2e_count/so_rel_count
r = so_matched_e2e_count/gs_rel_count
f = (2*p*r)/(p+r)
print("P: {0}\tR: {1}, F: {2}\n".format(p, r, f))
