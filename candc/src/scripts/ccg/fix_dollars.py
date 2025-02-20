# C&C NLP tools
# Copyright (c) Universities of Edinburgh, Oxford and Sydney
# Copyright (c) James R. Curran
#
# This software is covered by a non-commercial use licence.
# See LICENCE.txt for the full text of the licence.
#
# If LICENCE.txt is not included in this distribution
# please email candc@it.usyd.edu.au to obtain a copy.

import sys
import re

#SMALL = re.compile(r"[^ ]*[$#]\|[$#] [^|]*\|CD")
#LARGE = re.compile(r"[^ ]*[C$#]\|[$#] [^|]*\|CD [^0-9.|]*\|CD")

SMALL = re.compile(r"[^ ]*[#$]\|[#$] [^|]*\|CD")
LARGE = re.compile(r"[^ ]*[#$]\|[#$] [^|]*\|CD [^0-9.|]*\|CD")

# DOLLARS = re.compile(r"[^ ]*[$#]\|[$#]")
TAGS = re.compile(r"\|[^ ]*")
QUOTES = re.compile(r"""''?\|''|``?\|``""")

PTB = {}

def load_ptb(filename, ptb):
  for line in file(filename):
    ptbank = line[:-1]
    ccgbank = ptbank
    ccgbank = LARGE.sub("DOLLARS|NNS", ccgbank)
    ccgbank = SMALL.sub("DOLLARS|NNS", ccgbank)
#    ccgbank = DOLLARS.sub("DOLLARS|NNS", ccgbank)
    ccgbank = QUOTES.sub('', ccgbank)
    ccgbank = TAGS.sub('', ccgbank)
    ccgbank = ccgbank.replace('\\*', '')
    ccgbank = ' '.join(ccgbank.split())
    ccgbank = ccgbank.replace('(', '-LRB-').replace(')', '-RRB-')
    ccgbank = ccgbank.replace('[', '-LSB-').replace(']', '-RSB-')
    ccgbank = ccgbank.replace('{', '-LCB-').replace('}', '-RCB-')
    ptb[ccgbank] = ptbank
    print >> sys.stderr, 'CCG', ccgbank
    print >> sys.stderr, 'PTB', ptbank

for filename in sys.argv[1:]:
  load_ptb(filename, PTB)

class Node:
  def __init__(self, orig):
    self.orig = orig
  def __str__(self):
    return self.orig

class TNode(Node):
  def __init__(self, orig):
    Node.__init__(self, orig)
    fields = orig[4:-1].split(' ')
    (self.head, self.cat, self.pos, self.tmp, self.nchildren) = fields
    self.tmp = int(self.tmp)
    self.nchildren = int(self.nchildren)
    self.left = None
    self.right = None
  def sentence(self):
    if self.right:
      return self.left.sentence() + self.right.sentence()
    else:
      return self.left.sentence()

class LNode(Node):
  def __init__(self, orig):
    Node.__init__(self, orig)
    fields = orig[4:-1].split(' ')
    (self.head, self.cat, self.pos, self.word) = fields
  def sentence(self):
    return [ self.word ]

class Tree:
  def __init__(self, lines):
    lines.reverse()
    self.root = self.parse(lines)

  def parse(self, lines):
    if lines[-1].startswith('(<T'):
      node = TNode(lines.pop())
      node.left = self.parse(lines)
      if node.nchildren == 2:
        node.right = self.parse(lines)      
    elif lines[-1].startswith('(<L'):
      node = LNode(lines.pop())
    else:
      raise 'unexpected line "%s"' % lines[-1]

    if lines[-1] != ')':
      raise 'expected closing parenthesis'
    lines.pop()

    return node

  def sentence(self):
    return self.root.sentence()

MISSED = re.compile('DOLLARS [0-9.]+ (?:millions?|billions?)')

lines = []
for line in sys.stdin:
  if len(line) == 1:
    tree = Tree(lines)
    lines = []
    ccgbank = ' '.join(tree.sentence())
    if ccgbank not in PTB:
      missing = MISSED.sub('DOLLARS', ccgbank)
      if missing not in PTB:
        print ccgbank
    continue

  line = line[:-1]
  if line == '###':
    continue

  lines.append(line)
