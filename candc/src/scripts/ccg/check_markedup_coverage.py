import sys

def ignore_preface(lines):
    in_preface = True
    for line in lines:
        if in_preface:
            in_preface = line != '\n'
            continue
        yield line


CLASSES = sys.argv[1]
MARKEDUP = sys.argv[2]

classes = {}
for line in ignore_preface(open(CLASSES, "rU")):
    klass, freq = line.split()
    classes[klass] = freq

for line in ignore_preface(open(MARKEDUP, "rU")):
    if line[0] in '#= \n':
        continue
    klass = line.strip()
    if klass not in classes:
        print 'EXTRA:', klass
    else:
        del classes[klass]

for klass in classes:
    print 'MISSING:', klass
