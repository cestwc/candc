import sys

if __name__ == '__main__':
  if len(sys.argv) < 4:
    print "Usage: evalmulti <gold> <model> <test>"
    print """To convert output from bin/super to the test format, this might help:
cat super_out | sed 's/$/\\n/' | tr ' |' '\\n ' | sed 's/^\([^ ]* [^ ]* \)/\\1n-a /' > super_out.multi"""
    sys.exit(1)

GOLD = sys.argv[1]
MODEL = sys.argv[2]
TEST = sys.argv[3]

DICT_CUTOFF = 20

def read_gold():
  line = gold.readline()
  if not line:
    return None
  return map(lambda x: tuple(x.split('|')), line[:-1].split(' '))

def read_test():
  res = []
  line = test.readline()
  while line and len(line) > 1:
    fields = line.split()
    res.append((fields[0], fields[1], fields[3::2]))
    line = test.readline()
  return res

def ignore_preface(lines):
  in_preface = True
  for line in lines:
    if in_preface:
      in_preface = line != '\n'
      continue
    yield line

def load_klasses(model):
  klasses = {}
  for line in ignore_preface(file(model + '/classes')):
    (word, freq) = line.split()
    klasses[word] = int(freq)
  return klasses

def load_lexicon(model):
  lexicon = {}
  for line in ignore_preface(file(model + '/lexicon')):
    (word, freq) = line.split()
    lexicon[word] = int(freq)
  return lexicon

def load_tagdict(model, lexicon, cutoff, ratio):
  tagdict = {}
  fulldict = {}
  for line in ignore_preface(file(model + '/tagdict')):
    (word, tag, freq) = line.split()
    fulldict.setdefault(word, []).append(tag)
    freq = int(freq)
    if freq < cutoff:
      word_freq = lexicon.get(word, 0)
      if freq*ratio < word_freq:
        continue
    tagdict.setdefault(word, []).append(tag)
  return tagdict, fulldict

def load_posdict(model, cutoff):
  posdict = {}
  fulldict = {}
  for line in ignore_preface(file(model + '/posdict')):
    (pos, tag, freq) = line.split()
    fulldict.setdefault(pos, []).append(tag)
    freq = int(freq)
    if freq < cutoff:
      continue
    posdict.setdefault(pos, []).append(tag)
  return posdict, fulldict

klasses = load_klasses(MODEL)
lexicon = load_lexicon(MODEL)
tagdict, fulltagdict = load_tagdict(MODEL, lexicon, 5, 500)
posdict, fullposdict = load_posdict(MODEL, 5)

gold = file(GOLD)
test = file(TEST)

total = 0
total_sent = 0

pos_confusion = {}
pos_error = 0
pos_sent_error = 0

missing_cat_error = 0

ccg_missing = {}
ccg_error = 0
ccg_sent_error = 0

both_error = 0
both_sent_error = 0

rare_error = 0
tagdict_error = 0
full_tagdict_error = 0

posdict_real_error = 0
posdict_gold_error = 0
full_posdict_error = 0

use_tagdict = 0
use_posdict = 0

use_tagdict_error = 0
use_posdict_error = 0

ncats = 0

line = gold.readline()
while line != '\n':
  line = gold.readline()

gsent = read_gold()
while gsent:
  tsent = read_test()
  if len(gsent) != len(tsent):
    print gsent
    print tsent
    raise Exception('sentences not the same length - gold %d, test %d' % (len(gsent), len(tsent)))

  seen_pos_error = False
  seen_ccg_error = False
  for ((gword, gpos, gcat), (tword, tpos, tcats)) in zip(gsent, tsent):
    if gword != tword:
      raise Exception('words do not line up')

    if gpos != tpos:
      error = (gpos, tpos)
      pos_confusion[error] = pos_confusion.get(error, 0) + 1
      pos_error += 1
      seen_pos_error = True

    freq = lexicon.get(gword, 0)
    if freq >= DICT_CUTOFF:
      use_tagdict += 1
    else:
      use_posdict += 1

    if gcat not in tcats:
      ccg_missing[gcat] = ccg_missing.get(gcat, 0) + 1
      ccg_error += 1
      seen_ccg_error = True
      if gpos != tpos:
        both_error += 1

      if gword not in lexicon:
        rare_error += 1

      if gcat not in klasses:
        missing_cat_error += 1

      if freq >= DICT_CUTOFF:
        use_tagdict_error += 1
        if gcat not in tagdict[gword]:
          tagdict_error += 1
          if gcat not in fulltagdict[gword]:
            full_tagdict_error += 1
      else:
        use_posdict_error += 1
        if gcat not in posdict[tpos]:
          posdict_real_error += 1
        if gcat not in posdict[gpos]:
          posdict_gold_error += 1

    ncats += len(tcats)

  if seen_pos_error:
    pos_sent_error += 1
    
  if seen_ccg_error:
    ccg_sent_error += 1
    
  if seen_pos_error and seen_ccg_error:
    both_sent_error += 1

  total += len(gsent)
  total_sent += 1

  gsent = read_gold()

def pct(part, total):
  if total:
    return '%6.2f%%' % (part*100.0/total)
  else:
    return '  ----%'

def report_pct(label, num, total):
  missed = total - num
  print label, '=',
  print '%s (%d/%d) instances' % (pct(num, total), num, total),
  print '%s (%d/%d) missed' % (pct(missed, total), missed, total)
  
def report(label, error, total):
  correct = total - error
  print label, '=',
  print '%s (%d/%d) correct' % (pct(correct, total), correct, total),
  print '%s (%d/%d) error' % (pct(error, total), error, total)

def report2(label, both, error_total, total):
  print label, '=',
  print '%s (%d/%d)' % (pct(both, error_total), both, error_total),
  print '%s (%d/%d) of total accuracy' % (pct(both, total), both, total)

print 'total words =', total
print 'total sentences =', total_sent
print
print 'ncats = %d' % ncats
print 'ncats per word = %.2f' % (float(ncats)/total)
print
report('pos /w', pos_error, total)
report('ccg /w', ccg_error, total)
print
report('pos /s', pos_sent_error, total_sent)
report('ccg /s', ccg_sent_error, total_sent)
print
report_pct('use tagdict /w', use_tagdict, total)
report_pct('use posdict /w', use_posdict, total)
print
report2('missing categories /ccg error', missing_cat_error, ccg_error, total)
print
report2('pos and ccg errors /pos error', both_error, pos_error, total)
report2('pos and ccg errors /ccg error', both_error, ccg_error, total)
report2('pos ok and ccg err /ccg error', ccg_error - both_error, ccg_error, total)
print
report2('rare errors        /ccg error', rare_error, ccg_error, total)
report2('used tagdict error /ccg error', use_tagdict_error, ccg_error, total)
report2('used posdict error /ccg error', use_posdict_error, ccg_error, total)
print
report2('cat not in tagdict      /ccg error', tagdict_error, ccg_error, total)
report2('cat not in fulldict     /ccg error', full_tagdict_error, ccg_error, total)
report2('cat not in real posdict /ccg error', posdict_real_error, ccg_error, total)
report2('cat not in gold posdict /ccg error', posdict_gold_error, ccg_error, total)
