from sys import stderr, argv, exit
from string import join

if len(argv) != 2:
  print >> stderr, "usage: %s <model>" % argv[0]
  exit(1)

model = argv[1]
if model[-1] == '/':
  model = model[:-1]

def load(filename, lookup):
  for line in open(filename):
    line = line[:-1]
    fields = line.split()
    lookup.append(join(fields[:-1]))

klasses = []
load(model + "/classes", klasses)

attributes = []
load(model + "/attributes", attributes)

for line in open(model + "/contexts"):
  line = line[:-1]
  fields = line.split()
  fields[1] = klasses[int(fields[1])]
  for i in range(3, len(fields)):
    fields[i] = attributes[int(fields[i])]
  print join(fields)
