# -*- coding: utf-8 -*-

import codecs
import re
import json
import copy
import os


FNAME = '/home/maryszmary/Documents/rus.verbs'
SEP_VERBS = 'verbs.separated'


def forms_collector(verbs, fname):
    '''opens a file with verbs from Zaliznyak, reads it and makes a dictionary where 
    keys are lexemes and values are dictionaries with wordforms and morph tags'''
    classes = []
    for line in verbs:
         lemma, gram_info = tuple(line.split('<', 1))
         gram_info = '<' + gram_info
         if classes and lemma == classes[-1][0]:
                classes[-1][1].append(gram_info)
         else:
                classes.append([lemma, [gram_info]])
    with open(SEP_VERBS + '/'  + fname, 'w') as f:
        json.dump(classes, f, ensure_ascii=False, indent=4)
    return classes


def separator(fname):
    with open(fname, 'r') as f:
        verbs = f.read().split('\n')
    verbs.pop(-1) 
    perf_iv, perf_tv, impf_iv, impf_tv = [], [], [], []
    for line in verbs:
        if '<impf>' in line and '<iv>' in line:
            impf_iv.append(line)
        elif '<perf>' in line and '<iv>' in line:
            perf_iv.append(line)
        elif '<impf>' in line and '<tv>' in line:
            impf_tv.append(line)
        elif '<perf>' in line and '<tv>' in line:
            perf_tv.append(line)
        else:
            print('the wordform doesnt match any expectation: ' + wordform)


    # alternative:
    # maryszmary@maryszmary-UX303UB:~/Documents$ cat rus.verbs | grep '<perf>' | grep '<tv>' > verbs.separated/perf_tv
    # maryszmary@maryszmary-UX303UB:~/Documents$ cat rus.verbs | grep '<perf>' | grep '<iv>' > verbs.separated/perf_iv
    # maryszmary@maryszmary-UX303UB:~/Documents$ cat rus.verbs | grep '<impf>' | grep '<tv>' > verbs.separated/impf_tv
    # maryszmary@maryszmary-UX303UB:~/Documents$ cat rus.verbs | grep '<impf>' | grep '<iv>' > verbs.separated/impf_iv

    return perf_iv, perf_tv, impf_iv, impf_tv


# предыдущий способ сплиттинга не работает, потому что теперь, с учётом порядка лексем, 
# в одной лексеме не бывает больше одного инфинитива при том, что это не пассив 
# так ли это?..
def lexeme_spliter(info):
    print('hi there')
    tochange = {}
    for pair in info:
        lexeme = pair[0]
        infinitives = []
        for wordform in pair[1]:
            if ('<inf>' in wordform) and ('<pass>' not in wordform):  # куча глаголов с пассивами ВАЩЕТ!
                infinitives.append(wordform)
        if len(infinitives) > 1:
            if len(infinitives) not in [2, 4]:
                print(str(len(infinitives)) + ' : ' + lexeme)
            # lexemes = split_correctly(pair[1])
            tochange[lexeme] = pair[1]
    # for lemma in tochange:
    #     info.pop(lemma)
    #     for i in range(len(tochange[lemma])):
    #         info[lemma + str(i + 1)] = tochange[lemma][i]
            # print(lemma + str(i + 1) + ' : ' +  str(tochange[lemma][i]))
    print(len(tochange))
    return info


def split_correctly(lexeme):
    perf_iv, perf_tv, impf_iv, impf_tv = [], [], [], []
    for wordform in lexeme:
        if '<impf>' in wordform[1] and '<iv>' in wordform[1]:
            impf_iv.append(wordform)
        elif '<perf>' in wordform[1] and '<iv>' in wordform[1]:
            perf_iv.append(wordform)
        elif '<impf>' in wordform[1] and '<tv>' in wordform[1]:
            impf_tv.append(wordform)
        elif '<perf>' in wordform[1] and '<tv>' in wordform[1]:
            perf_tv.append(wordform)
        else:
            print('the wordform doesnt match any expectation: ' + wordform)
    lexemes = [perf_iv, perf_tv, impf_iv, impf_tv]
    lexemes = [arr for arr in lexemes if arr != []]
    # if len(lexemes) != 2:
    #     print(lexemes)
    #     quit()
    return lexemes




def main():
    # perf_iv, perf_tv, impf_iv, impf_tv = separator(FNAME) # someverbs.txt
    # os.system('rm -r {0}'.format(SEP_VERBS))
    # os.mkdir(SEP_VERBS)
    # perf_iv = forms_collector(perf_iv, 'perf_iv.json')
    # perf_iv = forms_collector(perf_tv, 'perf_tv.json')
    # perf_iv = forms_collector(impf_iv, 'impf_iv.json')
    # perf_iv = forms_collector(impf_tv, 'impf_tv.json')


    with open('verbs_z.json') as f:
        info = json.load(f)
    # i should do 2 tests:
    # 1. check if stress can be replaced safely:
    # i think i should separate stress variants from each other, check for differences and then decide whether i can kill stress.
    # 2. look for cases like изболеться:
    # actually, looking for such cases by infinitives makes no sense. i should use some other forms instead. like 3sg.fut, like in this case.
    
    lexeme_spliter(info)
    # with open('verbs_z.json', 'w') as f:
    #     json.dump(info, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()


# ------------------------
# -*- not used anymore -*-

def ununique_lexemes_test(info):
    # so, i learned, that:
    # 1. there _are_ ununique lexemes
    # 2. there _are_ exact intersections in their analyses (in a small number of cases)
    # 3. but it is supposedly due to the cases like возблистаю/возблещу,
    # where some wordforms are similar, like in this case "<vblex><perf><inf>:возблиста́ть"
    # supposedly, they are treated as different lexemes in the generator's source *reverse ingeneering :D * 

    # UPD: solved the problem

    lemmas = [pair[0] for pair in info]
    ununique = {}
    for i in range(len(lemmas)):
        if lemmas.count(lemmas[i]) > 1:
            if lemmas[i] not in ununique:
                ununique[lemmas[i]] = [i]
            else:
                ununique[lemmas[i]].append(i)
    print('ununique lemmas: ' + str(len(ununique)))
    # with open('ununique.json') as f:
    #     ununique = json.load(f)
    # for lemma in ununique:
    #     if len(ununique[lemma]) > 2:
    #         pass
    #     else:
    #         i, j = tuple(ununique[lemma])
    #         intersection = set(info[i][1]).intersection(set(info[j][1]))
    #         if intersection:
    #             print(lemma)
    return ununique


def need_splitting_test(info):
    need_splitting = []
    for pair in info:
        asp = 'perf' if '<perf>' in pair[1] else 'impf'
        trn = 'tv' if '<tv>' in pair[1] else 'iv'
        for wf in pair[1]:
            if (asp == 'perf' and '<impf>' in wf)\
               or (asp == 'impf' and '<perf>' in wf):
               need_splitting.append(pair)
               break
        for wf in pair[1]:
            if (trn == 'tv' and '<iv>' in wf)\
               or (trn == 'iv' and '<tv>' in wf):
               if pair not in need_splitting:
                   need_splitting.append(pair)
               break
    print('found {0} lexemes needing splitting the'
          ' paradigm'.format(len(need_splitting)))
    # print('different aspects: ' + str(len(different_aspects))) # 1039 
    # print('different transitivity: ' + str(len(different_transitivity))) # 17942
    return need_splitting


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
