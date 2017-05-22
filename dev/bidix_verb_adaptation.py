import re
import subprocess
from lxml import etree


BIDIX = '../apertium-pol-rus.pol-rus.dix'


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


def change_verbents(verbents):
    """
    Takes a list of subtrees with verbal entries, reanalyzes all the russian
    verbs and checks them for adecvacy. Returns valid verbal etries.
    """
    rus_verbs = dix_of_rus_verbs(verbents)
    new_verbents = []
    n = 0
    for rverb in rus_verbs:
        new_rus_anas = analyze_by_ltproc(rverb)
        for pol_part in rus_verbs[rverb]:
            new_portion = make_new_ents(pol_part, new_rus_anas)
            if not new_portion:
                new_portion = comment_this_hell_out(pol_part, new_rus_anas)
            new_verbents += new_portion

        n += 1
        if n % 200 == 0:
            print(str(n) + ': ' + rverb + ', ' + str(new_rus_anas))
            print(str(rus_verbs[rverb]))

    # workaround for the fact that tostring writes everything as a single line
    new_verbents = '<new>' + '\n'.join(new_verbents) + '</new>'
    new_verbents = etree.fromstring(new_verbents)
    new_verbents = new_verbents.getchildren()
    print(len(new_verbents))
    return new_verbents


def comment_this_hell_out(pol_part, new_rus_anas):
    # because i'm sick of fixing the issues with aspect
    print('\nProblems with aspect: ' + pol_part)
    print('New rus anas: ' + str(new_rus_anas))
    print('Commenting it out!\n')
    new_verbents = []
    for ana in new_rus_anas:
        entry = pol_part.format('<r>' + ana + '</r>')
        entry = '<!-- <e>' + entry + '</e> fix the aspect! -->'
        new_verbents.append(entry)
    return new_verbents


def make_new_ents(pol_part, new_rus_anas):
    """
    Takes a string with the rest of the entry and a list with analyses
    of corresponding russian verbs. Returns a list of strings with new entries.
    """
    new_verbents = []
    # i've checked that every pol_part has either 'perf' or 'impf'
    perfectiveness = 'perf' if '"perf"' in pol_part else 'impf'
    for ana in new_rus_anas:
        if perfectiveness in ana:
            entry = pol_part.format('<r>' + ana + '</r>')
            entry = '<e>' + entry + '</e>'
            new_verbents.append(entry)
    return new_verbents


def analyze_by_ltproc(rword):
    """
    Takes a string with russian word, looks for analyses in rus.dix,
    returns a list with analyses.
    """
    anas = subprocess.getoutput('echo {0} | lt-proc -a '
        '../../apertium-rus/rus.automorf.bin'.format(rword))
    # i've checked that there are no analyses with letters after $
    anas = anas.strip('$')
    # i've checked that there are no analyses without verbs anymore
    anas = [an for an in anas.split('/') if '<vblex>' in an and '<inf>' in an]
    anas = anas_handling(anas, rword)
    return anas


def anas_handling(analyses, rword):
    """
    Takes a list with analyses and a string with russian verb.
    Checks if the lemma in analysis is equal to the input lemma.
    Returns a list of strings with correct analyses.
    """
    anas = []
    for ana in analyses:
        ana = ana.split('<')[:4]
        if re.sub('[¹²³]', '', ana[0]) != rword and ana[0]\
           and re.sub('[¹²³]', '', ana[0]).replace('ё', 'е') != rword:
            # taking care about the stuff with reflexives
            if not (re.sub('[¹²³]', '', ana[0]) == rword + 'ся'
                    or re.sub('[¹²³]', '', ana[0]) + 'ся' == rword):
            # if some unpredictable stuff happens
                print('SOMETHING GOES WRONG WITH: ' + ana[0] + ', ' + rword)
        else:
            anas.append('<s n="'.join(ana).replace('>', '"/>'))
    return anas


def dix_of_rus_verbs(verbents):
    """
    Takes a list of subtrees with verbal entries. Returns a dictionary,
    where keys are clean russian verbs and values are strings with the rest
    of the entries with these verbs (with {0} instead of the russian verbs).
    """
    rus_verbs = {}
    for pair in verbents:
        rusverb = pair[0][-1].text
        rusverb = re.sub('[1234¹²³]', '', rusverb)
        pol_part = etree.tostring(pair[0][0], encoding='utf-8').decode()
        agr_par = etree.tostring(pair[1], encoding='utf-8').decode()
        rest = '<p>' + pol_part + '{0}</p>' + agr_par
        if rusverb not in rus_verbs:
            rus_verbs[rusverb] = [rest]
        elif rest not in rus_verbs[rusverb]:
            rus_verbs[rusverb].append(rest)
    return rus_verbs


def postprocessing(text):
    """
    Takes a string with the bidix and returns the beautified one.
    Removes orphaned comments about glosbe and makes indentation.  
    """
    text = text.replace('\n<!-- from glosbe -->', '')
    text = text.replace('\n<e>', '\n    <e>')
    return text


def write_new_bidix(bidix, cleaned_pairs, new_verbents, expressions):
    """
    Takes a bidix tree, a subtree with entries, a list with verb entries
    and a list with expressions. Extends the dictionary with the two lists
    and writes it to file. 
    """
    cleaned_pairs.extend(new_verbents)
    cleaned_pairs.extend(expressions)
    text = etree.tostring(bidix, encoding='utf-8').decode()
    text = postprocessing(text)
    with open(BIDIX + '-new', 'w') as f:
        f.write(text)


def main():
    pairs, bidix = get_data(BIDIX, 'section[@id="main"]')
    expressions, verbents, cleaned_pairs = verb_ents_bidix(pairs)
    new_verbents = change_verbents(verbents)
    bidix = write_new_bidix(bidix, cleaned_pairs, new_verbents, expressions)


if __name__ == '__main__':
    main()
