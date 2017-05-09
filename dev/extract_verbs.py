 # -*- coding: utf-8 -*-

import re
import json
import copy
import os

INDIR = 'verbs.separated'
OUTDIR = 'verbs.extracted'
# OUTFILE = 'russian_verbs.dix.xml'
MODAL = ['иметь', 'быть', 'мочь', 'хотеть']

def paradigm_collector(gram_d, secondary=True):
    """
    Takes a dictionary, where keys are lemmas and values are lists of analyses.
    Returns a dictionary, where keys are lemmas and values are tuples of
    a stem, a lemma flection and a list of strings with grammar tags
    and flections of each form. E.g.: '<tag><tag><tag>:flection'.
    """
    if secondary:
        gram_d = remove_fin_tags(gram_d)

    # morph_d is a dictionary, where keys are lemmas
    # and values are lists of wordforms (without analyses)
    morph_d = {lexeme : [el.split(':')[-1] for el in gram_d[lexeme]]
               for lexeme in gram_d}

    paradigms = {}
    for lemma in morph_d:
        if secondary:
            new_lemma = choose_lemma(gram_d[lemma])
        else:
            new_lemma = lemma
        stem_len = stem_finder(morph_d[lemma], new_lemma)
        stem, lem_flection = new_lemma[:stem_len], new_lemma[stem_len:]
        ana_and_flec = get_flec_and_ana(gram_d[lemma], stem_len)
        paradigms[lemma] = (stem, lem_flection, ana_and_flec)
    return paradigms


def get_flec_and_ana(wordforms, stem_len):
    """
    Takes a list of wordforms with analyses and an integer with stem length.
    Returns a sorted list with analyses (grammar tags) and flections.
    """
    ana_and_flec = []
    for line in wordforms:
        ana, wf = tuple(line.split(':'))
        flec = wf[stem_len:]
        ana_and_flec.append(':'.join([ana, flec]))
    return sorted(ana_and_flec)


def remove_fin_tags(gram_d):
    """
    Takes gram_d and boolean, removes redundant tags from secondary paradigms.
    Returns changed gram_d.
    """
    to_remove = ['<vblex>', '<impf>', '<perf>', '<tv>', '<iv>', '<pp>',
                 '<pprs>', '<actv>', '<pasv>']
    for lexeme in gram_d:
        for i in range(len(gram_d[lexeme])):
            for tag in to_remove:
                gram_d[lexeme][i] = gram_d[lexeme][i].replace(tag, '')
    return gram_d


def choose_lemma(lexeme):
    """
    Takes a list of strings (wordforms amd grammar tags), returns a lemma.
    """
    for wf in lexeme:
        if '<m><an><sg><nom>' in wf and '<pass>' not in wf:
            return wf.split(':')[-1]
    print('The verb probably has this participle only in pass. Checking...')
    for wf in lexeme:
        if '<m><an><sg><nom>' in wf:
            print('Yes!')
            return wf.split(':')[-1]
    print('No! No lemma: ' + lexeme[0])


def stem_finder(forms, lemma):
    '''finds length of the stem, returns an integer. called in paradigm_collector'''
    min_len = len(min(forms, key=len))
    stems_len = min_len
    for form in forms:
        for i in range(min_len):
            if lemma[i:i+1] != form[i:i+1]:
                # print(form[i:], end = ', ')
                if i < stems_len:
                    stems_len = i
                    break
    return stems_len


def find_infl_types(paradigms):
    """
    Takes a dictionary where keys are lemmas and values are tuples of a stem,
    a lemma flection and a list of strings with analyses. Returns a dictionary
    where keys are frozensets with analyses and values are lists of lemmas
    of verbs belonging to the inflectional with these sets of analyses.
    """
    infl_types = {}
    for lemma in paradigms:
        anas = frozenset(paradigms[lemma][2])
        # anas = '\n'.join(paradigms[lemma][2])
        if anas not in infl_types:
            infl_types[anas] = [lemma]
        else:
            infl_types[anas].append(lemma)
    print('number of paradigms: ' + str(len(infl_types)))
    return infl_types


def par_splitter(info):
    """
    Takes a list of pairs (lexeme and wordforms) and separates participles
    from each other and from finite forms. Returns dictionaries where keys
    are lemmas and values are lists with analyses.
    """
    pstact = {pair[0]:[] for pair in info}
    pstpss, prsact, prspss, finite = copy.deepcopy(pstact), copy.deepcopy(pstact), copy.deepcopy(pstact), copy.deepcopy(pstact)
    for pair in info:
        lexeme = pair[0]
        for wordform in pair[1]:
            if '<pp><pasv>' in wordform and '<short>' not in wordform:
                pstpss[lexeme].append(wordform)
            elif '<pp><actv>' in wordform and '<adv>' not in wordform:
                pstact[lexeme].append(wordform)
            elif '<pprs><actv>' in wordform and '<adv>' not in wordform:
                prsact[lexeme].append(wordform)
            elif '<pprs><pasv>' in wordform:
                prspss[lexeme].append(wordform)
            else:
                finite[lexeme].append(wordform)
    for d in pstpss, pstact, prsact, prspss, finite:
        for pair in info:
            if d[pair[0]] == []:
                d.pop(pair[0])
    return pstpss, pstact, prsact, prspss, finite


def tags_writer(text, infl_type):
    """
    Takes a frozenset with analyses (tags and endings) and transforms them
    into a paradigm. Returns a string with the paradigm.
    """
    for ana in infl_type:
        ana = ana.split(':')
        text += '        <e><p><l>' + ana[1] + '</l><r>{1}'
        ana[0] = ana[0].replace('@0@', '<use_obs>').replace('use_obs', 'obs') # for the easier parsing
        tags = ana[0].strip('<>').split('><')
        for tag in tags:
            if tag in ['leng', 'obs', 'prb']:
                text = text.rsplit('\n', 1)[0] + '\n'\
                       + text.rsplit('\n', 1)[1].replace('<e>', '<e r="LR">')
                continue
            text += '<s n="' + tag + '"/>'
        text += '</r></p></e>\n'
    return text


def par_maker(infl_types, pos, paradigms):
    """
    Takes a dictionary of inflection types, a string (pos: participle type)
    and a dictionary of lexemes and their paradigms. Returns a string with
    paradigms and a dictionary where keys are strings (paradigm labels) and
    values are tuples with lemmas which belong to the corresponding paradigms.
    """
    infl_classes = {}
    text = '\n\n'
    for infl_type in infl_types:
        label = infl_types[infl_type][0]
        base, ending = tuple(paradigms[label][:2])
        infl_classes[label] = ((base, ending), infl_types[infl_type]) # DIFF
        # print('par_maker: ' + str((base, ending)))
        text += '    <pardef n="{0}' + base + '/' + ending + '__' + pos + '">\n'
        text = tags_writer(text, infl_type)
        if pos == 'vblex':
            text = participle_pars(text, label, base, ending)
            text = text.format('', ending)
        else:
            text = text.format('BASE__', '')
        text += '    </pardef>\n\n'
    return text, infl_classes


def participle_pars(text, label, base_fin, ending):
    """
    Makes placeholders for references to secondary paradigms.
    """
    replacer = {'pstpss' : '<s n="pp"/><s n="pasv"/>',
                'pstact' : '<s n="pp"/><s n="actv"/>',
                'prspss' : '<s n="pprs"/><s n="pasv"/>',
                'prsact' : '<s n="pprs"/><s n="actv"/>'}
    for el in ['pstpss', 'pstact', 'prsact', 'prspss']:
        tags = replacer[el]
        text += '        <e><p><l>#' + base_fin + '#</l><r>' + ending\
                + '<s n="vblex"/>' + tags + '</r></p><par n="%BASE REQUIRED%'\
                + el  + '%' + label + '%"/></e>\n'
    return text


def find_paradigm(word, inventories, similar):

    for inventory in inventories:
        if word in inventory:
            wordclass = inventory

    for key in similar:
        if similar[key] == wordclass:
            print(key)


def fun_debugging_time(similar):
    inventories = similar.values()
    greatest = sorted(inventories, key=len)[-1]
    print('length of the greatest class: ' + str(len(greatest)))
    print('three words from the greatest wordclass: ' + greatest[0] + ', ' + greatest[1] + ', ' + greatest[2])
    find_paradigm(greatest[0], inventories, similar)
    print('----------------')
    second = sorted(inventories, key=len)[-2]
    print('length of the second greatest class: ' + str(len(second)))
    print('three words from the second greatest wordclass: ' + second[0] + ', ' + second[1] + ', ' + second[2])
    find_paradigm(second[0], inventories, similar)
    print('----------------')
    third = sorted(inventories, key=len)[-3]
    print('length of the third greatest class: ' + str(len(third)))
    print('three words from the second greatest wordclass: ' + third[0] + ', ' + third[1] + ', ' + third[2])
    find_paradigm(third[0], inventories, similar)
    print('----------------')
    fourth = sorted(inventories, key=len)[-4]
    print('length of the fourth greatest class: ' + str(len(fourth)))
    print('three words from the second greatest wordclass: ' + fourth[0] + ', ' + third[1] + ', ' + third[2])
    find_paradigm(fourth[0], inventories, similar)


def jsonify(data, fname):
    with open(fname, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def entries_maker(infl_classes): # WORKING ON THIS ONE
    """
    Takes a dictionary where keys are paradigm labels and values are tuples,
    where first element is base and stem and second element is a list
    of lemmas belonging to the corresponding paradigms.
    Returns a string with verb entries.
    """
    print('building entries ...')
    text = '\n'*4
    for label in infl_classes:
        st_and_fl, verb_list = infl_classes[label]
        base, ending = tuple(st_and_fl)
        clean_ending = re.sub('[¹²³]', '', ending)
        for verb in verb_list:
            clean_verb = re.sub('[¹²³]', '', verb)
            text += '    <e lm="' + verb + '"><i>'\
                    + clean_verb.split(clean_ending)[0] + '</i><par n="'\
                    + base + '/' + ending + '__vblex"/></e>\n'
    return text


def prtcp_affixes(line, wordforms, ending):
    """
    Takes a string with a pardef reference placeholder, a list of ptcpl anas
    and a string with the participle lemma's ending. Returns a string with
    the participle affix placeholder replaced with the real affix.
    """
    ptcpl_lemma = choose_lemma(wordforms)
    prtcp_base = ptcpl_lemma.split(ending)[0]
    base = line.split('#')[1]
    if base:
        if len(prtcp_base.split(base)) > 1:
            prtcp_base = prtcp_base.split(base)[1]
            # print('SUCCESSFULLY: ' + affix + ', base: ' + base)
        else:
            print('Something strange: '+ line + '\nbase: '\
                  + base + ', ptcpl_base: ' + prtcp_base)
    else:
        print('zero ptcpl ending: ' + line)
    line = line.split('#')[0] + prtcp_base + line.split('#')[2]
    return line


def secondary_par_matcher(text, ptcpl_labels, ptcpls):
    """
    Takes a string with all pardefs, a dictionary with participle labels and
    a dictionary with participles and analyses. Finds places in vblex pardefs
    where wich require references to participle pardefs and makes them, if
    there is such a pardef. Returns a string with pardefs.
    """
    lines = []
    for line in text.split('\n'):
        if 'BASE REQUIRED' in line:
            ptcpl, lexeme = tuple(line.split('%')[2:4])

            if ptcpl in ptcpl_labels: # check if the verbs have this kind of participles at all
                labels = ptcpl_labels[ptcpl]
                anas = ptcpls[ptcpl]
                for label in labels:
                    base, ending = tuple(labels[label][0])
                    if lexeme in labels[label][1]:
                        line = line.split('%')[0] + 'BASE__' + base + '/'\
                               + ending + '__' + ptcpl + line.split('%')[4]
                        # print('secondary_par_matcher: ' + str((base, ending)))
                        line = prtcp_affixes(line, anas[lexeme], ending)
                        lines.append(line)
                        break
        else:
            lines.append(line)
    return '\n'.join(lines)


def secondary_par_writer(ptcpls):
    """
    Takes a dictionary where keys are participle labels and values are
    dictionaries with participle analyses. Returns string with participle
    paradigms and a dictionary where keys are ptcple kinds and values
    are dictionaries from par_maker.
    """
    text = ''
    ptcpl_labels = {}
    for ptcple in ptcpls:
        print(ptcple, end=': ')
        if ptcpls[ptcple]:
            paradigms = paradigm_collector(ptcpls[ptcple])
            infl_types = find_infl_types(paradigms)
            new_text, infl_classes = par_maker(infl_types, ptcple, paradigms)
            text += new_text
            ptcpl_labels[ptcple] = infl_classes
        else:
            print('empty')
    return text, ptcpl_labels


def final_writer(info):
    '''returns a string with all paradigms'''
    pstpss, pstact, prsact, prspss, finite = par_splitter(info)
    ptcpls = {'pstpss' : pstpss, 'pstact' : pstact, 'prsact' : prsact, 'prspss' : prspss}
    text, ptcpl_labels = secondary_par_writer(ptcpls)
    paradigms = paradigm_collector(finite, secondary=False)
    infl_types_finite = find_infl_types(paradigms)
    vblex_pardefs, labels_vblex = par_maker(infl_types_finite, 'vblex', paradigms)
    text += vblex_pardefs
    text = secondary_par_matcher(text, ptcpl_labels, ptcpls)
    text += '</pardefs>\n\n  <section id="main" type="standard">\n\n'
    text += entries_maker(labels_vblex)
    text += ' </section>\n\n</dictionary>\n'
    # fun_debugging_time(infl_types_finite)

    with open('all_verbs', 'w') as f:
        f.write(text)
    quit()

    return text


def remove_stress(info):
    """
    Takes a list with lexemes and all their wordforms, removes stress,
    kills repeting entries. Returns the changed list.
    """
    for i in range(len(info)):
        wordforms = info[i][1]
        wordforms = list(set([w.replace(chr(769), '').replace(chr(768), '')
                              for w in wordforms]))
        info[i][1] = wordforms
    return info


def remove_modal(info):
    """
    Takes a list with lexemes and all their wordforms, removes modal verbs.
    """
    i = 0
    while i < len(info):
        if info[i][0] in MODAL:
            info.pop(i)
            continue
        i += 1
    return info


# def add_beginning(text):
#     beginning = codecs.open('rus_dix_beginning', 'r').read()
#     return beginning + text


def main():
    for fname in os.listdir(INDIR):

        # processing each file in verbs.separated
        print('procesing {0}...'.format(fname))
        verb_type = fname.replace('.json', '')
        with open(os.path.join(INDIR, fname)) as f:
            info = json.load(f)
        info = remove_stress(info)
        info = remove_modal(info)
        text = final_writer(info)
        # with open(os.path.join(OUTDIR, verb_type + '.xml'), 'w') as f:
        #     f.write(text)

    # text = add_beginning(text)


if __name__ == '__main__':
    main()
