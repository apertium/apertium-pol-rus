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
            print('the wordform doesnt match any expectation: ' + line) # no such lines

    # alternative:
    # os.system("/home/maryszmary/Documents$ cat rus.verbs | grep '<perf>' | grep '<tv>' > verbs.separated/perf_tv")
    # os.system("/home/maryszmary/Documents$ cat rus.verbs | grep '<perf>' | grep '<iv>' > verbs.separated/perf_iv")
    # os.system("/home/maryszmary/Documents$ cat rus.verbs | grep '<impf>' | grep '<tv>' > verbs.separated/impf_tv")
    # os.system("/home/maryszmary/Documents$ cat rus.verbs | grep '<impf>' | grep '<iv>' > verbs.separated/impf_iv")

    return perf_iv, perf_tv, impf_iv, impf_tv


def part_homonyny_test(info):
    """
    Removes stress, replaces ё with е. Leaves unique lines. Makes 2 sets:
    a set of analyses + wordforms and a set of analyses without wordforms.
    If their lengths are not equal, shows analyses which have > 1 wordforms.
    """
    diff_types = {}
    for pair in info:
        lexeme = pair[0]
        forms = [wf.replace(chr(769), '').replace(chr(768), '').replace('ё', 'е') for wf in pair[1]]
        ana_and_wf = set(forms)
        only_ana = set([form.split(':')[0] for form in forms])
        if len(ana_and_wf) != len(only_ana):
            print('\n\n' + lexeme)
            diff_types[lexeme] = []
            # print('ana_and_wf: {0}, only_ana: {1}'.format(len(ana_and_wf), len(only_ana)))

            for ana in only_ana:
                corresponding = []
                for wf in ana_and_wf:
                    if ana + ':' in wf:
                        corresponding.append(wf)
                if len(corresponding) > 1:
                    print(corresponding)
                    diff_types[lexeme].append(corresponding)

    print(len(diff_types))
    with open('part_hom_test.json', 'w') as f:
        json.dump(diff_types, f, ensure_ascii=False, indent=4)
    return diff_types


def main():
    perf_iv, perf_tv, impf_iv, impf_tv = separator(FNAME) # someverbs.txt
    os.system('rm -r {0}'.format(SEP_VERBS))
    os.mkdir(SEP_VERBS)
    perf_iv = forms_collector(perf_iv, 'perf_iv.json')
    perf_iv = forms_collector(perf_tv, 'perf_tv.json')
    perf_iv = forms_collector(impf_iv, 'impf_iv.json')
    perf_iv = forms_collector(impf_tv, 'impf_tv.json')


if __name__ == '__main__':
    main()

# tests:

# 1. check if stress can be replaced safely:
# следующий тест: если внутри одной лексемы есть хотя бы одна форма, которая различается только ударением,
# правда ли то, что все разборы, которые есть у слова с одним вариантом ударения, есть и у слова с другим ударением
# and then decide whether i can kill stress
# ... i decided that i don't care and everythong is ok. it is impossibe to check, because russian accent paradigms are impossible:
# you can never say (automatically) if some stress variant actually lacks some analysis or in this case there's only one stress variant
# besides, it is not really important for the task: it's ok to slightly overgenerate possible forms.

# 2. look for cases like изболеться:
# (done in part_homonyny_test. looked through the verbs found. now should separate them manually)

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


def stress_test(info):
    for pair in info:

        # если внутри одной лексемы есть хотя бы две форма, которые различаются только ударением
        without = set([wf.replace(chr(769), '').replace(chr(768), '') for wf in pair[1]])
        with_st = set(pair[1])
        if len(without) != len(with_st):
            pass

            # правда ли то, что все разборы, которые есть у слова с одним вариантом ударения, есть и у слова с другим ударением
