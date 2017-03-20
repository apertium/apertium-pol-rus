'''
cleaning the bidix from the messy translations from glosbe
dictionaries: bab.ls, pons, wiki, <s>classes</s>, glosbe (safe)
'''

# subtasks:
# write a func for changing the bidix (replacing old entries with new ones)

# TODO: е/ё: leave ё
# think about words which translate as expressions


from lxml import etree
from lxml import html
from urllib import error
from urllib import parse
from urllib import request
import json
import os
import socket
import string
import subprocess


POS = 'adv'
BIDIX = '../apertium-pol-rus.pol-rus.dix'
RUSDIX = '../../apertium-rus/apertium-rus.rus.dix'
BABLA = 'http://pl.bab.la/slownik/polski-rosyjski/'
GLOSBE = 'https://glosbe.com/pl/ru/'
PONS = 'http://en.pons.com/translate?q={0}&l=plru&in=&lf=pl'
WIKI = 'https://pl.wiktionary.org/wiki/{0}'
TAGS_BOUNDARY = {'n' : 3, 'adj' : 2, 'adv' : 1}
TAGS_LEMMAS = {'n' : '<n>.*<sg><nom>', 'adj' : '<adj>.*<sg><nom>',
               'vblex' : '<vblex>.*<inf>', 'adv' : '<adv>'}


def get_all_pairs():
    '''takes POS tag needed, returns all lines with pairs of this POS'''
    with open(BIDIX, 'r') as f:
        t = f.readlines()[1:]
    translations = [line for line in t if '<e><p><l>' in line
                    and '<s n="' + POS in line]
    return translations


def lines_parsed(translations):
    '''takes lines with translations, returns dict '''
    d_of_tr = {}
    for line in translations:
        sinfo = get_line_info(line, 0)
        tword = get_line_info(line, 1)[0]
        if sinfo not in d_of_tr:
            d_of_tr[sinfo] = [tword]
        else:
            d_of_tr[sinfo] += [tword]
    return d_of_tr


def get_line_info(line, n):
    try:
        tree = etree.fromstring(line)
        word = tree[0][n].text
        if tree[0][n][0].tail:
            word += ' ' + tree[0][n][0].tail
        prefix = line[:line.index('<r>') + 3]
        suffix = line[line.index('</r>'):]
        return word, prefix, suffix
    except etree.XMLSyntaxError:
        print(line) 



def check_homonimy(d):
    with open('already_there') as f:
        already_there = f.read().split('\n')
    need_change = []
    for key in d:
        if len(d[key]) > 2 and key[0]:
            if key[0] not in already_there:
                need_change.append(key)
            else:
                print('already_there: ' + key[0])
        elif key[0] is None:
            print('key is None')
            print(str(key))
    with open('need_change.json', 'w') as f:
        json.dump(need_change, f, ensure_ascii=False, indent=4)
    print('need_change created')


def get_new_translations(old_words):
    new_translations = []
    for word in old_words:
        try:
            new_cur = correct(word)
        except error.URLError:
            input('Is connection stable? ')
            new_cur = correct(word)
        new_translations += new_cur
        for tr in new_cur:
            os.system('echo \'{0}\' >> new.tr'.format(tr.strip()))
    return new_translations


def correct(sword):
    '''returns a list of lines with pairs'''
    lexeme = sword[0]
    print('\n---{0}---\n'.format(lexeme))
    first_part = '<e><p><l>' + lexeme + '<s n="' + '/><s n="'.join(sword[0])
    pons_tr = from_pons(parse.quote(lexeme.encode()))
    try:
        babla_tr = from_babla(parse.quote(lexeme.encode()))
    except ConnectionResetError:
        babla_tr = []
    wiki_tr = from_wiki(parse.quote(lexeme.encode()))
    if pons_tr + babla_tr + wiki_tr:
        return [sword[1] + tr + sword[2] for tr in set(pons_tr + babla_tr + wiki_tr)]
    else:
        print('\nNOT FOUNND IN OTHER DICTS. LOOKING IN GLOSBE: ' + lexeme + '\n')
        glsb_tr = safe_glosbe_parser(parse.quote(lexeme.encode()))
        glsb_tr = [sword[1] + tr + sword[2] for tr in set(glsb_tr)]
        return [tr.strip() + '  <!-- from glosbe -->\n' for tr in glsb_tr]


def safe_glosbe_parser(word):
    page = request.urlopen(GLOSBE + word).read().decode('utf-8')
    translations = html.fromstring(page).xpath('.//strong[@class=" phr"]')
    translations = [tr.text.replace(chr(769), '') for tr in translations
                    if all_cyrillic(tr.text) and ' ' not in tr.text][:3]
    print(translations)
    return translations_tagged(translations)


def from_babla(word):
    page = request.urlopen(BABLA + word).read().decode('utf-8')
    translations = html.fromstring(page).xpath('.//ul[@class="sense-group-results"]')[0]
    translations = [ch[0] for ch in translations.getchildren() if ch[0].tag == 'a']
    translations = [tr.text for tr in translations if all_cyrillic(tr.text)]
    print('BABLA: ' + str(translations))
    return translations_tagged(translations)


def from_pons(word):
    page = request.urlopen(PONS.format(word)).read().decode('utf-8')
    if correct_page(page, word):
        translations = html.fromstring(page).xpath('.//div[@class="target"]')
        translations = [' '.join([a.text for a in t if a.tag == 'a']).replace(chr(769), '')
                        for t in translations]
        print('PONS: ' + str(translations))
        translations = [tr for tr in translations if all_cyrillic(tr)]
        return translations_tagged(translations)
    return []


def correct_page(page, word):
    entries = html.fromstring(page).xpath('.//dt[@class="_entry_title"]')
    word = parse.unquote(word)
    if entries and entries[0][0].text != word:
        print('PONS: no such word: ' + word)
        return False
    return True


def from_wiki(word):
    try:
        page = request.urlopen(WIKI.format(word)).read().decode('utf-8')
        for li in html.fromstring(page).xpath('.//li'):
            if li.text and li.text.startswith('rosyjski:'):
                translations = [tr.text.replace(chr(769), '')  for tr in li 
                                if tr.text is not None and all_cyrillic(tr.text)]
                print('WIKI: ' + str(translations))
                return translations_tagged(translations)
        else:
            print('WIKI: no russian translation')
    except error.HTTPError:
        print('WIKI: no such word: ' + parse.unquote(word))
    return []


def all_cyrillic(s): return not set(string.ascii_letters).intersection(set(s))


def translations_tagged(translations):
    '''takes a list of russian words, returnes a list of them with grammar tags
    if there are such in the dictionary'''
    result = []
    for tr in translations:
        line = tags_getter(tr)
        if line:
            result.append(line)
            print('appended: ' + line)
        else:
            print('NOT FOUND ' + tr)
    return result


def tags_getter(rword):
    ana = subprocess.getoutput('echo {0} | lt-proc -a '
        '../../apertium-rus/rus.automorf.bin | tr "/" "\n" '
        '| grep "{1}"'.format(rword, TAGS_LEMMAS[POS]))
    if not ana:
        os.system('echo {0} >> not_in_rus.dix'.format(rword))
        ana = get_tags_from_z(rword)
        print(ana)
    ana = ana.split('<')[:TAGS_BOUNDARY[POS] + 1]

    # TODO: debug
    if ana[0] != rword and ana[0]:
        print('not equal: ' + ana[0] + ', ' + rword)
        os.system('echo {0} >> not_equal'.format(rword))
        if ana[0] == rword.replace('ё', 'е'):
            ana[0] = rword # AAAAA. IN THIS LINE YOU ARE DOING SOMETHING WRONG. ПОДУМОЙ.
        elif ana[0] == rword + '²' or ana[0] == rword + '¹':
            print(rword + ' : uppercase digit')
        else:
            print('SOMETHING GOES WRONG WITH: ' + rword + ' and ' + ana[0])

    return '<s n="'.join(ana).replace('>', '"/>')


def get_tags_from_z(rword):
    ana = subprocess.getoutput('cat ../../rus.nouns '
        '| grep "^{0}" | grep "{1}"'.format(rword, TAGS_LEMMAS[POS]))
    return ana


def change_dict(new_tr):
    with open(BIDIX, 'r') as f: #  + '-new'
        t = f.readlines()[1:]
    try:
        whole_dict = etree.fromstring(''.join(t))
    except etree.XMLSyntaxError:
        print(t[1])
    section = whole_dict.xpath('section')[0]
    new_tr = etree.fromstring('<new>' + '\n'.join(new_tr) + '</new>')
    new_section = delete_prev(section, new_tr)
    new_section = append_new(new_section, new_tr)
    whole_dict.replace(section, new_section)
    with open(BIDIX + '-new', 'w') as f:
        f.write(etree.tostring(whole_dict, encoding='utf-8', xml_declaration=True).decode())


def delete_prev(section, new_tr):
    for entry in section.xpath('e/p'):
        for new_ent in new_tr:
            if new_ent.text != ' from glosbe '\
                and entry[0].text == new_ent[0][0].text \
                and attributes_equal(entry[0], new_ent[0][0]):
                    section.remove(entry.getparent())
                    break
    return section


def append_new(section, new_tr):
    # section.append(etree.Comment(text=' new nouns. 10.02.2017 '))
    for entry in new_tr:
        section.append(entry)
    return section


def attributes_equal(old, new):
    '''checks if all grammar attributes in two nodes are equal'''
    for i in range(min(len(old), len(new))):
        if old[i].get('n') != new[i].get('n'):
            return False
    return True


def rewrite_need_change(last_writen):
    with open('need_change.json', 'r') as f:
        data = json.load(f)
    only_words = [line[0] for line in data]
    data = data[only_words.index(last_writen) + 1:]
    with open('need_change.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    # d = lines_parsed(get_all_pairs())
    # check_homonimy(d)

    # with open('need_change.json') as f:
    #     old_words = json.load(f)
    # get_new_translations(old_words)

    # rewrite_need_change('definitywnie')

    with open('new.tr') as f:
        new_translations = f.read().split('\n')
    change_dict(new_translations)



main()
# print(from_wiki(parse.quote('papier'.encode())))


# --- for future --- 

def from_classes():
    prefix = 'http://www.classes.ru/all-polish/dictionary-polish-russian-term-2.htm' # всё сложно
