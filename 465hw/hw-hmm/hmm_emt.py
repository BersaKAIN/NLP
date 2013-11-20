#! /usr/bin/python

import sys
import math
import re
import collections
from sets import Set
from copy import deepcopy



def main():
	trainFile = sys.argv[1]
	testFile = sys.argv[2]
	rawFile = sys.argv[3]
	numOfIteration = 3
	# the origin hmm model (origin counts)
	hmmModel_ori = HmmModel()
	hmmModel_ori.learnModel(trainFile,rawFile)
	hmmModel_cur = hmmModel_ori
	for i in range(numOfIteration):
		hmmModel_cur = EMIteration(hmmModel_ori,hmmModel_cur,testFile,rawFile)


def EMIteration(HmmModel_ori, HmmModel_cur, testFile, rawFile):
	'''The EM algorithm will take two hmm models and return a new one which is the estimation of the model
	'''
	# use viterbi to estimate the best path
	viterbiAlgorithm = ViterbiAlgorithm(HmmModel_cur)
	viterbiAlgorithm.bestPath(testFile)

	# use forward-backward to reestimate the counts and return it to a new HmmModel
	forwardBackward = ForwardBackward(HmmModel_cur)
	newHmmModel = forwardBackward.totalPath(rawFile, HmmModel_ori)
	return newHmmModel




class HmmModel:

	def __init__(self):
		self.count_ss = collections.defaultdict(float)
		self.count_se = collections.defaultdict(float)
		self.count_s = collections.defaultdict(float)
		self.count_e = collections.defaultdict(float)
		# will give the possible tag(state) for a given word(emmision)
		self.dict = collections.defaultdict(set)
		# number of tokens of states and emissions should be same.
		self.numOfTokens = 0
		self.numOfTokens_s = 0

		# the set of types of the states
		self.types_s = Set()
		# number of different types of states
		self.numOfType_s = 0


		# the types of the emissions
		self.types_e = Set()
		self.typesR_e = Set()
		self.seen = Set()
		# number of different types of emissions, including the unseen type OOV
		self.numOfTypes_e = 0
		self.numOfTypesR_e = 0
		
		# count the number of singletons of state after state.
		self.singleton_ss = collections.defaultdict(int)
		# count the number of singletons of emission after state.
		self.singleton_se = collections.defaultdict(int)



	def learnModel(self, filename, filenameRaw):
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
			self.numOfTokens += 1
			self.numOfTokens_s += 1
			self.dict[emission].add(state)
			oldstate = state
			oldemission = emission
		# we want to make sure p(###|###) = 1, so the lbd = singletons should be zero
		self.dict["###"].add("###")
		self.singleton_se["###"] = 0
		self.types_s.remove("###")

		# now we accuulate the number of types of words in raw file.
		infile = file(filenameRaw, "r")
		for line in infile:
			# print line.rstrip()
			e = line.rstrip()
			self.typesR_e.add(e)
			self.count_e[e] += 1
			self.numOfTokens += 1

		self.numOfTypes_e = len(self.types_e)
		self.seen = self.typesR_e - self.types_e




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
			lbd = 10 ** (-100)
		if (float(self.count_ss[s1+' '+s2]) + float(lbd*self.count_s[s2])/self.numOfTokens_s) / (self.count_s[s1] + lbd) == 0:
			print "Pss from %s to %s is %f, lbd is %f" %(s1,s2,(float(self.count_ss[s1+' '+s2]) + lbd*self.count_s[s2]/self.numOfTokens_s) / (self.count_s[s1] + lbd), lbd)
		# print "Pss from %s to %s is %f" %(s1,s2,(float(self.count_ss[s1+' '+s2]) + lbd*self.count_s[s2]/self.numOfTokens) / (self.count_s[s1] + lbd))
		return (float(self.count_ss[s1+' '+s2]) + float(lbd*self.count_s[s2])/self.numOfTokens_s) / (self.count_s[s1] + lbd)


	def Pse(self, s, e):
		# print "Pse key is |%s|" % (s+' '+e)
		# print "Pse from %s to %s is %f" %(s,e,float(self.count_se[s+' '+e]/self.count_s[s]))
		lbd = self.singleton_se[s]
		# print lbd
		if lbd == 0:
			lbd = 10 ** (-100)
		backoff = float(self.count_e[e]+1)/(self.numOfTokens + self.numOfTypes_e)
		# print "Pse from %s to %s is %f" %(s,e,(float(self.count_se[s+' '+e]) + lbd* backoff)/(self.count_s[s]+lbd))
		if (float(self.count_se[s+' '+e]) + float(lbd* backoff))/(self.count_s[s]+lbd) == 0:
			print "Pse from %s to %s is %f" %(s,e,(float(self.count_se[s+' '+e]) + lbd* backoff)/(self.count_s[s]+lbd))
		return (float(self.count_se[s+' '+e]) + float(lbd* backoff))/(self.count_s[s]+lbd)

	def dict_e(self,e):
		# if the word is novel
		if e not in self.dict.keys():
			# print "the bad e is %s" % e
			return self.types_s
		else:
			# print self.dict[e]
			return self.dict[e]

	def clearCount(self):
		self.count_ss = collections.defaultdict(float)
		self.count_se = collections.defaultdict(float)
		self.count_s = collections.defaultdict(float)
		self.numOfTokens_s = 0

		
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
					# print "Now at %d th word: %s. Current state is %s, previous state is %s. lp is %f, lmu is %f" % (i, self.ob[i],state, oldstate, lp, lmu)
					if lmu > self.viterbiValue[state+' '+str(i)]:
						self.viterbiValue[state+' '+str(i)] = lmu
						# set the back pointer
						self.backpointer[state+' '+str(i)] = oldstate



		# print self.viterbiValue
		# print self.backpointer
		# print the path
		countNovel = 0
		countNovelCorrect = 0
		countKnown = 0
		countKnownCorrect = 0
		countSeen = 0
		countSeenCorrect = 0
		currentTag = '###'
		# add novel and known correct rate
		perplex = 0
		novelRate = 0
		seenRate = 0
		# print self.backpointer

		for i in range (len(self.ob)-1, 0 ,-1):
			# print "My tag is %s and the true tag is %s" % (currentTag, self.trueState[i])
			# perplex += log(self.HmmModel.Pse(currentTag, self.ob[i]))
			# print perplex
			if currentTag != "###":
				if (self.ob[i] not in self.HmmModel.types_e) and (self.ob[i] not in self.HmmModel.typesR_e):
					countNovel += 1
					if currentTag == self.trueState[i]:
						countNovelCorrect += 1
					# else:
					# 	print "it is the %d th word. My tag is %s true is %s" %(i,currentTag,self.trueState[i])
				elif self.ob[i] in self.HmmModel.seen:
					countSeen += 1
					if currentTag == self.trueState[i]:
						countSeenCorrect += 1
				else:
					countKnown += 1
					if currentTag == self.trueState[i]:
						countKnownCorrect += 1
					# else:
					# 	print "it is the %d th word. My tag is %s true is %s" %(i,currentTag,self.trueState[i])

			currentTag = self.backpointer[currentTag+' '+str(i)]
		perplex += self.viterbiValue["###"+' '+str(len(self.ob)-1)]
		# print perplex
		if countNovel == 0:
			novelRate = 1
		else:
			novelRate = float(countNovelCorrect)/countNovel

		if countSeen == 0:
			seenRate = 1
		else:
			seenRate = float(countSeenCorrect)/countSeen
		print "Tagging accuracy (Viterbi decoding): %f   (Known: %f  Novel: %f Seen: %f)" % (100 * float(countNovelCorrect+countKnownCorrect)/(countKnown+countNovel), float(countKnownCorrect)/countKnown, novelRate, seenRate)
		print "Perplexity per viertibi-tagged test word: %f" % (math.e ** (-1 * perplex / len(self.ob)))

class ForwardBackward:
	def __init__(self, HmmModel):
		self.HmmModel = HmmModel
		self.newHmmModel = deepcopy(HmmModel)
		self.newHmmModel.clearCount()
		self.ob = []
		self.alpha = collections.defaultdict(lambda:float("-inf"))
		self.beta = collections.defaultdict(lambda:float("-inf"))

	def totalPath(self, filename, HmmModel_ori):
		# load the raw data
		infile = file(filename, "r")
		for line in infile:
			(emission) = line.rstrip()
			self.ob.append(emission)

		# compute the alpha values
		self.alpha["### 0"] = 0
		for i in range(1,len(self.ob)):
			for state in self.HmmModel.dict_e(self.ob[i]):
				for oldstate in self.HmmModel.dict_e(self.ob[i-1]):
					lp = log(self.HmmModel.Pss(oldstate,state)) + log(self.HmmModel.Pse(state,self.ob[i]))
					# actually alpha += p, but since alpha stores the log probability, we should have log(alpha) = log(alpha+p) = log(expalpha + explp) = logadd(lalpha+lp)
					lmu = self.alpha[oldstate+' '+str(i-1)] + lp
					# print "its in the %d th word of alpha lmu is %f and the value of alpha before update is %f " %(i,lmu, self.alpha[state+' '+str(i)])
					self.alpha[state+' '+str(i)] = logadd(self.alpha[state+' '+str(i)], lmu)
					# print "its in the %d th word of alpha lmu is %f and the value of alpha after update is %f " %(i,lmu, self.alpha[state+' '+str(i)])

		POb = self.alpha["### "+str(len(self.ob)-1)]
		# print "the probability of the whole ob is %f" %POb
		# then we compute the beta values
		self.beta["###"+' '+str(len(self.ob)-1)] = 0
		for i in range(len(self.ob)-1, 0, -1):
			for state in self.HmmModel.dict_e(self.ob[i]):
				# add the count to new count_s
				# print "we are at day %d adding new count_s to state %s: %f" %(i,state,math.exp(self.alpha[state+' '+str(i)] + self.beta[state+' '+str(i)] - POb))
				# print "The alpha: %f beta: %f sum: %f" %(self.alpha[state+' '+str(i)], math.exp(self.beta[state+' '+str(i)]), POb)
				self.newHmmModel.count_s[state] += math.exp(self.alpha[state+' '+str(i)] + self.beta[state+' '+str(i)] - POb)
				self.newHmmModel.numOfTokens_s += math.exp(self.alpha[state+' '+str(i)] + self.beta[state+' '+str(i)] - POb)
				# add the count to new count_se
				# print "adding new count_se: %f" %math.exp(self.alpha[state+' '+str(i)] + self.beta[state+' '+str(i)] - POb)
				self.newHmmModel.count_se[state+' '+self.ob[i]] += math.exp(self.alpha[state+' '+str(i)] + self.beta[state+' '+str(i)] - POb)
				for oldstate in self.HmmModel.dict_e(self.ob[i-1]):
					lp = log(self.HmmModel.Pss(oldstate,state)) + log(self.HmmModel.Pse(state,self.ob[i]))
					lmu = self.beta[state+' '+str(i)] + lp
					# implement the logadd method
					self.beta[oldstate+' '+str(i-1)] = logadd(self.beta[oldstate+' '+str(i-1)], lmu)
					# add the count to new count_ss
					# print "adding new count_ss: %f" %math.exp(self.alpha[oldstate+' '+str(i-1)] + lp + self.beta[state+' '+str(i)] - POb)
					self.newHmmModel.count_ss[oldstate+' '+state] += math.exp(self.alpha[oldstate+' '+str(i-1)] + lp + self.beta[state+' '+str(i)] - POb)


		# print "printing the alpha table"
		# print self.alpha

		# print "printing the beta table"
		# print self.beta

		# print "printing the count_ss"
		# print self.HmmModel.count_ss
		# print "printing the count_se"
		# print self.HmmModel.count_se
		# print "printing the count_s"
		# print self.HmmModel.count_s


		# add count_ss count_se and count_s from ori to the new model
		for (key,value) in HmmModel_ori.count_ss.iteritems():
			self.newHmmModel.count_ss[key] += value
		for (key,value) in HmmModel_ori.count_se.iteritems():
			self.newHmmModel.count_se[key] += value
		for (key,value) in HmmModel_ori.count_s.iteritems():
			self.newHmmModel.count_s[key] += value
		self.newHmmModel.numOfTokens_s += HmmModel_ori.numOfTokens_s



		# print "new model updated"
		# print self.newHmmModel.count_ss
		# print self.newHmmModel.count_se
		# print self.newHmmModel.count_s
		# 
		print "Iteration %d:  Perplexity per untagged raw word:   %f" % (1,math.exp(-1 * POb / len(self.ob)))

		return self.newHmmModel		

		# print self.alpha
		# print self.beta
		


		# # find out the best tag
		# countNovel = 0
		# countNovelCorrect = 0
		# countKnown = 0
		# countKnownCorrect = 0
		# for i in range(1, len(self.ob)):
		# 	# skip all ### tag/word
		# 	if self.trueState[i] == "###":
		# 		continue
		# 	currentTag = ""
		# 	bestTagValue = float("-inf")
		# 	for possibleTag in self.HmmModel.dict_e(self.ob[i]):
		# 		if self.alpha[possibleTag+' '+str(i)]+self.beta[possibleTag+' '+str(i)] > bestTagValue:
		# 			bestTagValue = self.alpha[possibleTag+' '+str(i)]+self.beta[possibleTag+' '+str(i)]
		# 			currentTag = possibleTag
		# 	# update counts
		# 	# print "My guess is %s and the true tag is %s" %(currentTag, self.trueState[i])
		# 	if self.ob[i] in self.HmmModel.types_e:
		# 		countKnown += 1
		# 		if currentTag == self.trueState[i]:
		# 			countKnownCorrect += 1
		# 	else:
		# 		countNovel += 1
		# 		if currentTag == self.trueState[i]:
		# 			countNovelCorrect += 1
		# if countNovel == 0:
		# 	novelRate = 1
		# else:
		# 	novelRate = float(countNovelCorrect)/countNovel
		# print "Tagging accuracy (Posterior decoding): %f   (Known: %f  Novel: %f )" % (100 * float(countNovelCorrect+countKnownCorrect)/(countKnown+countNovel), float(countKnownCorrect)/countKnown, novelRate)







def logadd(x,y):
	if x < y:
		return y + math.log1p(math.exp(x-y))
	else:
		return x + math.log1p(math.exp(y-x))



def log(x):
	if x == 0:
		return float("-inf")
	else:
		return math.log(x)

if __name__ ==  "__main__":
  main()