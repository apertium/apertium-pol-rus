'''
cleaning the bidix from the messy translations from glosbe
dictionaries: bab.ls, pons, classes
'''

# subtasks:
# write finctions for parsing the output of resourses (firstly, pons)
# change the func from_babla
# write a func for dealing with glosbe output (either choose first two or choose those which confporm to some criteria)
# implement the algorithm for cleaning


import os
from urllib import request
from urllib import parse
from lxml import etree

DICNAME = '../apertium-pol-rus.pol-rus.dix'

def get_all_pairs(tag):
    with open(DICNAME, 'r') as f:
        t = f.readlines()
    translations = [line for line in t if '<e><p><l>' in line
                    and '<s n="' + tag in line]
    return translations


def lines_parsed(translations):
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


def homo_dealer(d):
    for key in d:
        if len(d[key]) > 2:
            new_translations = get_better(key, d[key])


def get_better(sword, translations):
    pass


def from_pons(word):
    prefix = 'http://en.pons.com/translate?'



def from_babla(word, tags, dictionary):
    link_noun = parse.quote(noun)
    noun_page = request.urlopen('http://pl.bab.la/slownik/polski-rosyjski/' + link_noun).read().decode('utf-8')
    translations = lxml.html.fromstring(noun_page).xpath('.//a[@class="result-link"]')
    for tr in translations:
        print(tr.text)
        if verifier(tr.text) is not None:
            dictionary.write('<e><p><l>' + noun + tags + '</l><r>' 
                + tr.text.replace(' ', '<b/>') + verifier(tr.text) + '</r></p></e>\n')
        else:
            dictionary.write('<e><p><l>' + noun + tags + '</l><r>' 
                        + tr.text.replace(' ', '<b/>') + '<s n="n"/></r></p></e>\n')


def from_classes():
    prefix = 'http://www.classes.ru/all-polish/dictionary-polish-russian-term-2.htm' # всё сложно
    pass


def main():
    translations = get_all_pairs('n')
    d = lines_parsed(translations)
    # print(sum([len(d[key]) for key in d]))
    homo_dealer(d)

main()

# def det_pairs():
#     os.system('cat apertium-pol-rus.pol-rus.dix | grep -P \'<e><p><l>[^<]+<s n="\' > \tmp\pairs')
