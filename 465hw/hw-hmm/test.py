#! /usr/bin/python

import math
import hmm
import hmm_fb
import hmm_em
from sets import Set
from copy import deepcopy
hmmModel = hmm_em.HmmModel()
hmmModel.learnModel("./data/ictrain","./data/icraw")
# viterbiAlgorithm = hmm.ViterbiAlgorithm(hmmModel)
# forwardBackward = hmm_fb.ForwardBackward(hmmModel)

# print hmmModel.Pse("H","3d")
# print hmmModel.count_s
# print hmmModel.count_ss
# print hmmModel.Pss("###","H")
hmmModel_new = deepcopy(hmmModel)

hmmModel_new.count_ss = {}

print hmmModel.count_ss
print hmmModel_new.count_ss




# print forwardBackward.alpha["fdfsd"]