# -*- coding: utf-8 -*-

import codecs
import re
import json
import copy


FNAME = '/home/maryszmary/Documents/rus.verbs'


def forms_collector_new(fname):
    '''opens a file with verbs from Zaliznyak, reads it and makes a dictionary where 
    keys are lexemes and values are dictionaries with wordforms and morph tags'''
    with open(fname, 'r') as f:
        verbs = f.read().split('\n')
    verbs.pop(-1) 
    classes = []
    for line in verbs:
         lemma, gram_info = tuple(line.split('<', 1))
         gram_info = '<' + gram_info
         if classes and lemma == classes[-1][0]:
                classes[-1][1].append(gram_info)
         else:
                classes.append([lemma, [gram_info]])
    return list(reversed(classes))


def lexeme_spliter(info):
    tochange = {}
    for lexeme in info:
        infinitives = []
        for wordform in info[lexeme]:
            if 'inf' in wordform[1] and 'pass' not in wordform[1]:  # куча глаголов с пассивами ВАЩЕТ!
                infinitives.append(wordform)
        if len(infinitives) > 1:
            lexemes = split_correctly_mod(info[lexeme])
            tochange[lexeme] = lexemes
    for lemma in tochange:
        info.pop(lemma)
        for i in range(len(tochange[lemma])):
            info[lemma + str(i + 1)] = tochange[lemma][i]
            # print(lemma + str(i + 1) + ' : ' +  str(tochange[lemma][i]))
    return info


def split_correctly_mod(lexeme):  # отдебажить
    perf_iv, perf_tv, impf_iv, impf_tv = [], [], [], []
    for wordform in lexeme:
        if 'impf iv' in wordform[1]:
            impf_iv.append(wordform)
        elif 'perf iv' in wordform[1]:
            perf_iv.append(wordform)
        elif 'impf tv' in wordform[1]:
            impf_tv.append(wordform)
        elif 'perf tv' in wordform[1]:
            perf_tv.append(wordform)
        else:
            print(wordform)
    lexemes = [perf_iv, perf_tv, impf_iv, impf_tv]
    lexemes = [arr for arr in lexemes if arr != []]
    # if len(lexemes) != 2:
    #     print(lexemes)
    #     quit()
    return lexemes


def main():
	info = forms_collector_new(FNAME) # someverbs.txt
	with open('verbs_z.json', 'w') as f:
	    json.dump(info, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
	main()


# -------------------
# -*- old version -*-	
# def forms_collector(fname):
#     '''opens a file with verbs from Zaliznyak, reads it and makes a dictionary where 
#     keys are lexemes and values are dictionaries with wordforms and morph tags'''
#     with codecs.open(fname, 'r', 'utf-8') as f:
#         forms = [line.replace(chr(769),'').replace(chr(768),'') for line in f]
#     print(len(forms))
#     # forms = kill_duplicates(forms)
#     print(len(forms))
#     forms = [form.split('+', 1) for form in forms]

#     gram_d = {}
#     for line in forms:
#         pair = line[0].split(':')
#         lexeme = pair[1]
#         wordform = pair[0]
#         if lexeme not in gram_d:
#             gram_d[lexeme] = [(wordform,  line[1][:-1].replace('+', ' '))]
#         else:
#             gram_d[lexeme].append((wordform, line[1][:-1].replace('+', ' ')))
#     return gram_d


# def kill_duplicates(forms):
#     '''deletes repeting lines and lines that are the repetiotions of lines without jo'''
#     table = {}
#     for line in forms:
#         if line not in table:
#             table[line.replace('ё', 'е')] = line
#     forms = [table[key] for key in table]
#     print(len(forms))
#     forms = list(forms)
#     return forms
