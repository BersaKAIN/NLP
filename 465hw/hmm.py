#! /usr/bin/python

import sys
import math
import re
import collections


def main():
	hmmModel = HmmModel()
	hmmModel.learnModel("./data/ictrain")
	viterbiAlgorithm = ViterbiAlgorithm(hmmModel)
	viterbiAlgorithm.bestPath("./data/ictest")

class HmmModel:

	def __init__(self):
		self.pss = {}
		self.pst = {}
		self.count_ss = collections.defaultdict(int)
		self.count_se = collections.defaultdict(int)
		self.count_s = collections.defaultdict(int)
		self.count_e = collections.defaultdict(int)
		self.count_totalStates = 0
		self.dict = collections.defaultdict(set)



	def learnModel(self, filename):
		infile = file(filename, "r")
		(oldemission,oldstate) = infile.readline().rstrip().split("/")
		# self.count_s[oldstate] += 1
		# self.count_e[oldemission] += 1
		# self.count_totalStates += 1
		self.dict[oldemission].add(oldstate)
		for line in infile:
			(emission,state) = line.rstrip().split("/")
			self.count_s[oldstate] += 1
			self.count_e[oldemission] += 1
			self.count_se[state+' '+emission] += 1
			self.count_ss[oldstate+' '+state] += 1
			self.count_totalStates += 1
			self.dict[emission].add(state)
			oldstate = state
			oldemission = emission


	def Pss(self, s1, s2):
		# need in future to figure when the count is zero, add more smooth
		# print "Pss key is |%s|" % (s1+' '+s2)
		# print "Pss from %s to %s is %f" %(s1,s2,float(self.count_ss[s1+' '+s2])/self.count_s[s1])
		# print "count ss is %d" % self.count_ss[s1+' '+s2]
		# print "count s is %d" % self.count_s[s1]
		return float(self.count_ss[s1+' '+s2])/self.count_s[s1]

	def Pse(self, s, e):
		# print "Pse key is |%s|" % (s+' '+e)
		# print "Pse from %s to %s is %f" %(s,e,float(self.count_se[s+' '+e]/self.count_s[s]))
		return float(self.count_se[s+' '+e])/self.count_s[s]
		
class ViterbiAlgorithm:
	def __init__(self, HmmModel):
		self.HmmModel = HmmModel
		self.ob = []
		self.trueState = []
		self.viterbiValue = collections.defaultdict(lambda:float("-inf"))
		self.backpointer = {}

	def bestPath(self, filename):
		# load the test data
		infile = file(filename, "r")
		for line in infile:
			(emission, state) = line.rstrip().split("/")
			self.ob.append(emission)
			self.trueState.append(state)

		# viterbi algorithm
		# define the starting point
		self.viterbiValue["### 0"] = 0
		for i in range(1,len(self.ob)):
			# print self.ob[i]
			for state in self.HmmModel.dict[self.ob[i]]:
				for oldstate in self.HmmModel.dict[self.ob[i-1]]:
					lp = log(self.HmmModel.Pss(oldstate,state)) + log(self.HmmModel.Pse(state,self.ob[i]))
					# if the Pss or Pse == 0, then we will take the or shall we define our own lod function
					lmu = self.viterbiValue[oldstate+' '+str(i-1)] + lp
					if lmu > self.viterbiValue[state+' '+str(i)]:
						self.viterbiValue[state+' '+str(i)] = lmu
						# set the back pointer
						self.backpointer[state+' '+str(i)] = oldstate
		print self.viterbiValue

		# print the path
		count = 0
		countAll = 0
		currentTag = '###'
		# add novel and known correct rate
		perplex = 0
		for i in range (len(self.ob)-1, 0 ,-1):
			# print "My tag is %s and the true tag is %s" % (currentTag, self.trueState[i])
			# perplex += log(self.HmmModel.Pse(currentTag, self.ob[i]))
			# print perplex
			if currentTag != "###":
				countAll += 1
				if currentTag == self.trueState[i]:
					count += 1
			currentTag = self.backpointer[currentTag+' '+str(i)]
		perplex += self.viterbiValue["###"+' '+str(len(self.ob)-1)]
		print perplex/34
		print "Tagging accuracy (Viterbi decoding): %f   (Known: %f  Novel: %f )" % (100 * float(count)/countAll, 1, 1)
		print "Perplexity per viertibi-tagged test word: %f" % (2 ** (-1 * perplex / (len(self.ob) - 2)))





		













def log(x):
	if x == 0:
		return float("-inf")
	else:
		return math.log(x)

if __name__ ==  "__main__":
  main()