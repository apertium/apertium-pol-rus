from lxml import etree
import os

INDIR = 'verbs.extracted'
OUTFILE = 'russian_verbs.dix.xml'


def beginning():
    """
    Gets alphabet and tag definitions, returns an etree object.
    """
    with open('dix.beginning.xml') as f:
        beginning = f.read()
    return etree.fromstring(beginning)


def write_dix(basepars, vbpars, entries):
    """
    Takes BASE pardefs, finite verb pardefs and lexical entries, creates
    a dictionary sceleton, appends the elements to the dictionary and
    writes the dictionary.
    """
    di = etree.fromstring('<dictionary>\n</dictionary>')
    di.extend(beginning()[:2])
    pardefs = etree.fromstring('<pardefs>\n</pardefs>')
    pardefs.extend(basepars)
    pardefs.extend(vbpars)
    di.append(pardefs)
    lex = etree.fromstring('<section id="main" type="standard"></section>')
    lex.extend(entries)
    di.append(lex)
    text = etree.tostring(di, encoding='utf-8', xml_declaration=True).decode()
    with open(OUTFILE, 'w') as f:
        f.write(text)


def merge():
    """
    Reads each file in INDIR, gets all elements, separeates them,
    calls the function for writing the new dix.
    """
    basepars, vbpars, entries = [], [], []
    for fname in os.listdir(INDIR):
        print('processing {0}...'.format(fname))
        with open(os.path.join(INDIR, fname)) as f:
            text = f.read()
        di = etree.fromstring(text)
        pardefs = di.xpath('pardefs')[0]
        entries += di.xpath('section')[0].getchildren()
        basepars += [pd for pd in pardefs if 'BASE' in pd.get('n')]
        vbpars += [pd for pd in pardefs if 'vblex' in pd.get('n')]
    write_dix(basepars, vbpars, entries)


merge()
