#! /usr/bin/python

import math
import hmm

hmmModel = hmm.HmmModel()
hmmModel.learnModel("./data/ictrain")
viterbiAlgorithm = hmm.ViterbiAlgorithm(hmmModel)

print hmmModel.count_s
print hmmModel.count_ss
print hmmModel.Pss("###","H")