'''
cleaning the bidix from the messy translations from glosbe
dictionaries: bab.ls, pons, classes
'''

# subtasks:
# write finctions for parsing the output of resourses (firstly, pons)
# change the func from_babla
# write a func for dealing with glosbe output (either choose first two or choose those which confporm to some criteria)
# implement the algorithm for cleaning


from lxml import etree
from lxml import html
from urllib import parse
from urllib import request
import os
import string
import subprocess


POS = 'n'
BIDIX = '../apertium-pol-rus.pol-rus.dix'
RUSDIX = '../../apertium-rus/apertium-rus.rus.dix'
BABLA = 'http://pl.bab.la/slownik/polski-rosyjski/'
TAGS_BOUNDARY = {'n' : 3, 'adj' : 2}
TAGS_LEMMAS = {'n' : '<n>.*<sg><nom>', 'adj' : '<adj>.*<sg><nom>',
               'vblex' : '<vblex>.*<inf>'}


def get_all_pairs():
    '''takes POS tag needed, returns all lines with pairs of this POS'''
    with open(BIDIX, 'r') as f:
        t = f.readlines()
    translations = [line for line in t if '<e><p><l>' in line
                    and '<s n="' + POS in line]
    return translations


def lines_parsed(translations):
    '''takes lines with translations, returns dict '''
    d_of_tr = {}
    for line in translations:
        tree = etree.fromstring(line)
        spair = get_line_info(tree, 0)
        tpair = get_line_info(tree, 1)
        if spair not in d_of_tr:
            d_of_tr[spair] = [tpair]
        else:
            d_of_tr[spair] += [tpair]
    return d_of_tr


def get_line_info(tree, n):
    word = tree[0][n].text
    if tree[0][n][0].tail:
        word += ' ' + tree[0][n][0].tail
    tags = ' '.join([tag.get('n') for tag in tree[0][n].getchildren()
                     if tag.get('n') is not None])
    return word, tags


def check_homonimy(d):
    for key in d:
        if len(d[key]) > 2:
            new_translations = correct(key, d[key])


def correct(sword, translations):
    '''returns a list of lines with pairs'''
    lexeme = sword[0]
    # pons_tr = from_pons(parse.quote(lexeme))
    babla_tr = from_babla(parse.quote(lexeme.encode()))
    if babla_tr:
        return [lexeme + sword[1] + tr for tr in babla_tr]


def from_pons(word):
    prefix, postfix = 'http://en.pons.com/translate?q=', '&l=plru&in=&lf=pl'


def from_babla(word):
    result = []
    page = request.urlopen(BABLA + word).read().decode('utf-8')
    translations = html.fromstring(page).xpath('.//ul[@class="sense-group-results"]')[0]
    translations = [ch[0] for ch in translations.getchildren() if ch[0].tag == 'a']
    translations = [tr.text for tr in translations if all_cyrillic(tr.text)]
    print(word)
    for tr in translations:
        print(tr)
        line = tags_getter(tr)
        if line:
            result.append(line)
        else:
            print('didnt find ' + tr)
    return result


def all_cyrillic(s): return not set(string.ascii_letters).intersection(set(s))


def from_classes():
    prefix = 'http://www.classes.ru/all-polish/dictionary-polish-russian-term-2.htm' # всё сложно


def tags_getter(rword):
    ana = subprocess.getoutput('echo {0} | lt-proc -a '
        '../../apertium-rus/rus.automorf.bin | tr "/" "\n" '
        '| grep "{1}"'.format(rword, TAGS_LEMMAS[POS]))
    ana = ana.split('<')[:TAGS_BOUNDARY[POS] + 1]
    return '<s n="'.join(ana).replace('>', '">')


def main():
    translations = get_all_pairs()
    d = lines_parsed(translations)
    # print(sum([len(d[key]) for key in d]))
    check_homonimy(d)

# main()
print(from_babla('naprawa'))
