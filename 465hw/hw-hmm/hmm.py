#! /usr/bin/python

import sys
import math
import re
import collections
from sets import Set


def main():
	trainFile = sys.argv[1]
	testFile = sys.argv[2]
	hmmModel = HmmModel()
	hmmModel.learnModel(trainFile)
	viterbiAlgorithm = ViterbiAlgorithm(hmmModel)
	viterbiAlgorithm.bestPath(testFile)

class HmmModel:

	def __init__(self):
		self.count_ss = collections.defaultdict(int)
		self.count_se = collections.defaultdict(int)
		self.count_s = collections.defaultdict(int)
		self.count_e = collections.defaultdict(int)
		self.count_totalStates = 0
		# will give the possible tag(state) for a given word(emmision)
		self.dict = collections.defaultdict(set)
		# number of tokens of states and emissions should be same.
		self.numOfTokens = 0

		# the set of types of the states
		self.types_s = Set()
		# number of different types of states
		self.numOfType_s = 0

		# the types of the emissions
		self.types_e = Set()
		# number of different types of emissions, including the unseen type OOV
		self.numOfTypes_e = 0
		
		# count the number of singletons of state after state.
		self.singleton_ss = collections.defaultdict(int)
		# count the number of singletons of emission after state.
		self.singleton_se = collections.defaultdict(int)



	def learnModel(self, filename):
		infile = file(filename, "r")
		(oldemission,oldstate) = infile.readline().rstrip().split("/")
		self.dict[oldemission].add(oldstate)
		for line in infile:
			(emission,state) = line.rstrip().split("/")
			# update type set
			self.types_s.add(oldstate)
			self.types_e.add(oldemission)
			# update count of state and emission, will update everything except the last one
			self.count_s[oldstate] += 1
			self.count_e[oldemission] += 1
			# update count_se and singleton_se
			self.count_se[state+' '+emission] += 1
			if self.count_se[state+' '+emission] == 1:
				self.singleton_se[state] += 1
			elif self.count_se[state+' '+emission] == 2:
				self.singleton_se[state] -= 1
			# update count_ss and singleton_ss
			self.count_ss[oldstate+' '+state] += 1
			if self.count_ss[oldstate+' '+state] == 1:
				self.singleton_ss[oldstate] += 1
			elif self.count_ss[oldstate+' '+state] == 2:
				self.singleton_ss[oldstate] -= 1
			self.count_totalStates += 1
			self.numOfTokens += 1
			self.dict[emission].add(state)
			oldstate = state
			oldemission = emission
		# we want to make sure p(###|###) = 1, so the lbd = singletons should be zero
		self.singleton_se["###"] = 0
		print self.types_s
		self.types_s.remove("###")


	def Pss(self, s1, s2):
		# need in future to figure when the count is zero, add more smooth
		# print "Pss key is |%s|" % (s1+' '+s2)
		# print "Pss from %s to %s is %f" %(s1,s2,float(self.count_ss[s1+' '+s2])/self.count_s[s1])
		# print "count ss is %d" % self.count_ss[s1+' '+s2]
		# print "count s is %d" % self.count_s[s1]
		# this is the simplest case where we have no smoothing at all
		# return float(self.count_ss[s1+' '+s2])/self.count_s[s1]
		
		# lambda
		lbd = self.singleton_ss[s1]
		if lbd == 0:
			lbd = 0.5
		if (float(self.count_ss[s1+' '+s2]) + float(lbd*self.count_s[s2])/self.numOfTokens) / (self.count_s[s1] + lbd) == 0:
			print "Pss from %s to %s is %f, lbd is %f" %(s1,s2,(float(self.count_ss[s1+' '+s2]) + lbd*self.count_s[s2]/self.numOfTokens) / (self.count_s[s1] + lbd), lbd)
		# print "Pss from %s to %s is %f" %(s1,s2,(float(self.count_ss[s1+' '+s2]) + lbd*self.count_s[s2]/self.numOfTokens) / (self.count_s[s1] + lbd))
		return (float(self.count_ss[s1+' '+s2]) + float(lbd*self.count_s[s2])/self.numOfTokens) / (self.count_s[s1] + lbd)


	def Pse(self, s, e):
		# print "Pse key is |%s|" % (s+' '+e)
		# print "Pse from %s to %s is %f" %(s,e,float(self.count_se[s+' '+e]/self.count_s[s]))
		lbd = self.singleton_se[s]
		# print lbd
		if lbd == 0:
			lbd = 0.5
		backoff = float(self.count_e[e]+1)/(self.numOfTokens + self.numOfTypes_e)
		# print "Pse from %s to %s is %f" %(s,e,(float(self.count_se[s+' '+e]) + lbd* backoff)/(self.count_s[s]+lbd))
		if (float(self.count_se[s+' '+e]) + float(lbd* backoff))/(self.count_s[s]+lbd) == 0:
			print "Pse from %s to %s is %f" %(s,e,(float(self.count_se[s+' '+e]) + lbd* backoff)/(self.count_s[s]+lbd))
		return (float(self.count_se[s+' '+e]) + float(lbd* backoff))/(self.count_s[s]+lbd)

	def dict_e(self,e):
		# if the word is novel
		if self.count_e[e] == 0:
			return self.types_s
		else:
			return self.dict[e]
		
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
			for state in self.HmmModel.dict_e(self.ob[i]):
				for oldstate in self.HmmModel.dict_e(self.ob[i-1]):
					lp = log(self.HmmModel.Pss(oldstate,state)) + log(self.HmmModel.Pse(state,self.ob[i]))
					# if the Pss or Pse == 0, then we will take the or shall we define our own lod function
					lmu = self.viterbiValue[oldstate+' '+str(i-1)] + lp
					# print "Now at %d th word. Current state is %s, previous state is %s. lp is %f, lmu is %f" % (i, state, oldstate, lp, lmu)
					if lmu > self.viterbiValue[state+' '+str(i)]:
						self.viterbiValue[state+' '+str(i)] = lmu
						# set the back pointer
						self.backpointer[state+' '+str(i)] = oldstate
				if self.viterbiValue[state+' '+str(i)] == float("-inf"):
					# print i
					# print "error here"
					break


		# print self.viterbiValue
		# print self.backpointer
		# print the path
		countNovel = 0
		countNovelCorrect = 0
		countKnown = 0
		countKnownCorrect = 0
		currentTag = '###'
		# add novel and known correct rate
		perplex = 0
		novelRate = 0

		for i in range (len(self.ob)-1, 0 ,-1):
			# print "My tag is %s and the true tag is %s" % (currentTag, self.trueState[i])
			# perplex += log(self.HmmModel.Pse(currentTag, self.ob[i]))
			# print perplex
			if currentTag != "###":
				if self.ob[i] not in self.HmmModel.types_e:
					countNovel += 1
					if currentTag == self.trueState[i]:
						countNovelCorrect += 1
					else:
						print "it is the %d th word. My tag is %s true is %s" %(i,currentTag,self.trueState[i])
				else:
					countKnown += 1
					if currentTag == self.trueState[i]:
						countKnownCorrect += 1
					else:
						print "it is the %d th word. My tag is %s true is %s" %(i,currentTag,self.trueState[i])

			currentTag = self.backpointer[currentTag+' '+str(i)]
		perplex += self.viterbiValue["###"+' '+str(len(self.ob)-1)]
		if countNovel == 0:
			novelRate = 1
		novelRate = float(countNovelCorrect)/countNovel
		print "Tagging accuracy (Viterbi decoding): %f   (Known: %f  Novel: %f )" % (100 * float(countNovelCorrect+countKnownCorrect)/(countKnown+countNovel), float(countKnownCorrect)/countKnown, novelRate)
		print "Perplexity per viertibi-tagged test word: %f" % (2 ** (-1 * perplex / (len(self.ob))))




def log(x):
	if x == 0:
		return float("-inf")
	else:
		return math.log(x)

if __name__ ==  "__main__":
  main()