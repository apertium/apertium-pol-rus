from lxml import etree


OLDDIX = '../../apertium-rus/apertium-rus.rus.dix'
VERBDIX = 'russian_verbs.dix.xml'
NEWDIX = 'apertium-rus.rus.dix.new'


def get_data(dixname, ent_sec):
    """
    Takes 2 strings: path to the dix and name of the section with verb pars.
    Returns a tuple of par etree, entries etree and whole dictionary etree. 
    """
    with open(dixname) as rus_dix:
        dix = rus_dix.read()
    dix = etree.fromstring(dix.replace('<?xml version=\'1.0\' encoding=\'utf-8\'?>', ''))
    paradigms = dix.xpath('pardefs')[0]
    verb_entries = dix.xpath(ent_sec)[0]
    return paradigms, verb_entries, dix


def del_vblex_pars(paradigms):
    """
    Takes pardefs etree, finds and deletes all vblex paradigms and participle
    bases from it, returnes pardefs without verbsal pardefs.
    """
    print('length of pars before ' + str(len(paradigms)))
    basenames = []
    for child in paradigms:
        if len(child.xpath('./e/p/r/s[@n="vblex"]')):
            # print(child.get('n'))
            refs = child.xpath('./e/par')
            basenames += [ref.get('n') for ref in refs]
            paradigms.remove(child)
    basenames = set(basenames)
    print('basenames num: ' + str(len(basenames)))
    paradigms = del_ptcpl_bases(paradigms, basenames)
    print('length of pars after ' + str(len(paradigms)))
    return paradigms


def del_ptcpl_bases(paradigms, basenames):
    """
    Takes pardefs etree, finds and deletes all participle bases from it,
    returnes pardefs without participle pardefs.
    """
    print('length of pars before deleting bases ' + str(len(paradigms)))
    for child in paradigms:
        if child.get('n') in basenames:
            print(child.get('n') + ' found!')
            paradigms.remove(child)
    return paradigms


def del_vblex_ents(entries):
    """
    Takes subtree with all entries, removes vblex entries, returns the
    cleaned subtree.
    """
    print('entr bfr: ' + str(len(entries)))
    for child in entries:
        if child.tag == 'e' and '__vblex' in child.xpath('par')[0].get('n'):
            entries.remove(child)
    print('entr aftr: ' + str(len(entries)))
    return entries


def write_new_dix(dictionary):
    """
    Takes a tree with new dictionary, writes it to file.
    """
    text = etree.tostring(dictionary, encoding='utf-8').decode()
    text = text.replace('>\n      <pardef', '>\n\n\n      <pardef')
    with open(NEWDIX + '-1', 'w') as f:
        f.write(text)


def main():
    oldpar, old_gci_ent, rusdix = get_data(OLDDIX, 'section[@id="gci"]')
    newpar, newent, verbdix = get_data(VERBDIX, 'section[@id="main"]')
    print('entries before: ' + str(len(old_gci_ent)))
    print('len of new verb entries: ' + str(len(verbdix)))
    cleaned_pars = del_vblex_pars(oldpar)
    cleaned_gci_ents = del_vblex_ents(old_gci_ent)
    cleaned_pars.extend(newpar)
    cleaned_gci_ents.extend(newent)
    cl_ent = rusdix.xpath('section[@id="gci"]')[0]
    print('entries after: ' + str(len(cl_ent)))
    write_new_dix(rusdix)


if __name__ == '__main__':
    main()
