#! /usr/bin/python

import nltk

from nltk import load_parser
cp = load_parser('grammar.fcfg')
query = 'amigo move to the object'
trees = list(cp.parse(query.split()))

print trees

answer = trees[0].label()['SEM']

print answer

answer = [s for s in answer if s]
q = ' '.join(answer)
print(q)