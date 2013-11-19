#! /usr/bin/python

import math
import hmm
import hmm_fb
from sets import Set
hmmModel = hmm.HmmModel()
hmmModel.learnModel("./data/entrain")
viterbiAlgorithm = hmm.ViterbiAlgorithm(hmmModel)
forwardBackward = hmm_fb.ForwardBackward(hmmModel)

# print hmmModel.Pse("H","3d")
# print hmmModel.count_s
# print hmmModel.count_ss
# print hmmModel.Pss("###","H")


print forwardBackward.alpha["fdfsd"]