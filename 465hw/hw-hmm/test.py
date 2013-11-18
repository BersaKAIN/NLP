#! /usr/bin/python

import math
import hmm
from sets import Set
hmmModel = hmm.HmmModel()
hmmModel.learnModel("./data/entrain")
viterbiAlgorithm = hmm.ViterbiAlgorithm(hmmModel)

# print hmmModel.Pse("H","3d")
# print hmmModel.count_s
# print hmmModel.count_ss
# print hmmModel.Pss("###","H")


a = Set()
a.add("b")
a.add(5)
print a 