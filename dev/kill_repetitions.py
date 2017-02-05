
BIDIX = '../apertium-pol-rus.pol-rus.dix'

def find_repeting_translations():
    with open(BIDIX, 'r') as f:
        t = f.readlines()
    entries = [line for line in t if '<e><p><l>' in line 
               and 'n="sg"' not in line and 'n="pl"' not in line]
    new, repeating = [], []
    for line in t: 
        if line in new and line in entries:
            repeating.append(line)
#            print(line.strip()) 
        else:
            new.append(line)
    return new, repeating


def rewrite_bidix(new_lines):
    with open('/tmp/new', 'w') as f:
        f.write(''.join(new_lines))
   


new, repeating = find_repeting_translations()
rewrite_bidix(new)
with open('/tmp/re', 'w') as f:
    f.write(''.join(repeating))

