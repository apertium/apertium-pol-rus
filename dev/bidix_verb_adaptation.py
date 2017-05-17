import re
import subprocess
from lxml import etree


BIDIX = '../apertium-pol-rus.pol-rus.dix'
RUSDIX = '../../apertium-rus/apertium-rus.rus.dix'
POS = 'vblex'


def get_data(dixname, ent_sec):
    """
    Takes 2 strings: path to the dix and name of the section.
    Returns a tuple of par etree, entries etree and whole dictionary etree. 
    """
    with open(dixname) as rus_dix:
        dix = rus_dix.read()
    dix = etree.fromstring(dix.replace('<?xml version=\'1.0\' encoding=\'utf-8\'?>', ''))
    entries = dix.xpath(ent_sec)[0]
    return entries, dix


def verb_ents_bidix(pairs):
    """
    Takes a tree with word entries, returns a tuple with verb entries,
    verb entries translated as expressions ans a tree of entries cleaned
    from any verb entries.
    """
    print('len of entries: ' + str(len(pairs)))
    expressions, verbents = [], []
    for pair in pairs:
        if pair.xpath('./p/r/s[@n="vblex"]'):
            if pair[0][-1][0].tag == 'b':
                expressions.append(pair)
            else:
                verbents.append(pair)
            pairs.remove(pair)
    print('verbents: ' + str(len(verbents)))
    print('len of cleaned entries: ' + str(len(pairs)))
    return expressions, verbents, pairs


def change_verbents(verbents): # WORKING ON THIS ONE
    """
    Takes a list of subtrees with verbal entries, ...
    Returns valid verbal etries.
    """
    rus_verbs = dix_of_rus_verbs(verbents)
    n = 0
    for rverb in rus_verbs:
        new_rverbs = analyze_by_ltproc(rverb)
        n += 1
        if n % 100 == 0:
            print(str(n) + ': ' + rverb)
    return verbents


def analyze_by_ltproc(rword):
    """
    Takes a string with russian word, looks for analyses in rus.dix,
    returns a ...
    """
    anas = subprocess.getoutput('echo {0} | lt-proc -a '
        '../../apertium-rus/rus.automorf.bin'.format(rword))
    anas = anas.strip('$') # i've checked that there are no analyses with letters after $
    anas = [ana for ana in anas.split('/') if '<vblex>' in ana]
    if not anas:
        print('no verb analyses: ' + rword)

    # return ana_handling(ana, rword)


def ana_handling(analyses, rword):
    '''takes 2 strindgs, returns a list'''
    anas = []
    for ana in analyses.split('\n'):
        if not ana:
            os.system('echo {0} >> not_in_rus.dix'.format(rword))
            ana = get_tags_from_z(rword)
        if not ana:
            continue

        ana = ana.split('<')[:TAGS_BOUNDARY[POS]]

        if ana[0] != rword and ana[0]:
            print('not equal: ' + ana[0] + ', ' + rword)

            # taking care of е/ё distinctions
            if ana[0] == rword.replace('ё', 'е'):
                ana[0] = rword

            # taking care of digits marking different inflection paradigms
            elif re.match(rword + '[¹²]?[1-4]?', ana[0]):
                print(rword + ' : different paradigms')

            # taking care about the stuff with reflexive analyses 
            elif re.match(rword + 'ся[¹²]?[1-4]?', ana[0]) \
                 or (rword[-2:] == 'ся' and re.match(rword[:-2] + '[¹²]?[1-4]?', ana[0])):
                continue

            # if some unpredictable stuff happens
            else:
                print('SOMETHING GOES WRONG WITH: ' + rword + ' and ' + ana[0])
                os.system('echo "{0} : {1}" >> not_equal'.format(rword, ana[0]))

        anas.append('<s n="'.join(ana).replace('>', '"/>'))
    return anas


def dix_of_rus_verbs(verbents):
    """
    Takes a list of subtrees with verbal entries, returns a dictionary,
    where keys are clean russian verbs and values are entry subtrees
    with these verbs.
    """
    rus_verbs = {}
    for pair in verbents:
        rusverb = pair[0][-1].text
        rusverb = re.sub('[1234¹²³]', '', rusverb)
        if rusverb not in rus_verbs:
            rus_verbs[rusverb] = [pair]
        else:
            rus_verbs[rusverb].append(pair)
    return rus_verbs
    


def write_new_bidix(bidix, cleaned_pairs, verbents, expressions):
    """
    Takes a bidix tree, a subtree with entries, a list with verb entries
    and a list with expressions. Extends the dictionary with the two lists
    and writes it to file. 
    """
    cleaned_pairs.extend(verbents),
    cleaned_pairs.extend(expressions)
    text = etree.tostring(bidix, encoding='utf-8').decode()
    with open(BIDIX + '-new', 'w') as f:
        f.write(text)


def main():
    # monoverbs, monodix = get_data(RUSDIX, 'section[@id="gci"]')
    pairs, bidix = get_data(BIDIX, 'section[@id="main"]')
    expressions, verbents, cleaned_pairs = verb_ents_bidix(pairs)
    verbents = change_verbents(verbents)
    bidix = write_new_bidix(bidix, cleaned_pairs, verbents, expressions)


if __name__ == '__main__':
    main()
