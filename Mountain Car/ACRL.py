import mountaincar
from Tilecoder import numTilings, tilecode, numTiles
from Tilecoder import numTiles as n
from pylab import *
import numpy as np
import random
import math

class ACRL():
    def __init__(self,gamma = 1, alphaR = 0/numTilings, alphaV = 0/numTilings, alphaU = 0.05/numTilings, lmbda = 0.75):
	self.gamma = gamma
	self.alphaR = alphaR
	self.alphaV = alphaV
	self.alphaU = alphaU
	self.lmbda = lmbda
	
	self.avgR = 0
	self.ev = np.zeros(n)
	self.e_mu = np.zeros(n)
	self.e_sigma = np.zeros(n)
	
	self.w = np.zeros(n)             
	self.u_mu = np.zeros(n)
	self.u_sigma = np.zeros(n)
	
	self.delta = 0.0
	self.R = 0.0
	self.value = 0.0
	self.nextValue = 0.0
	
	self.compatibleFeatures_mu = np.zeros(n)
	self.compatibleFeatures_sigma = np.zeros(n)
	
	self.mean = 0.0
	self.sigma = 1.0
    
    def Value(self,features):
	Val = 0.0
	for index in features:
	    Val += self.w[index]
	self.value = Val
	
    def Next_Value(self,features):
	Val = 0.0
	for index in features:
	    Val += self.w[index]
	self.nextValue = Val
	
    def Delta(self):
	self.delta = self.R - self.avgR - self.value
    
    def Delta_Update(self):
	self.delta += self.gamma*self.nextValue
    
    def Trace_Update_Critic(self,features):
	self.ev = self.gamma*self.lmbda*self.ev
	for index in features:
	    self.ev[index] += 1
    
    def Trace_Update_Actor(self):
	self.e_mu = self.gamma * self.lmbda * self.e_mu + self.compatibleFeatures_mu
	self.e_sigma = self.gamma * self.lmbda * self.e_sigma + self.compatibleFeatures_sigma
	    
    def Weights_Update_Critic(self):
	self.w += self.alphaV * self.delta * self.ev
	
    def Weights_Update_Actor(self):
	self.u_mu += self.alphaU * self.delta * self.e_mu
	self.u_sigma += self.alphaU * self.delta * self.e_sigma 
	
    def Compatible_Features(self,action,features):

	self.compatibleFeatures_mu = np.zeros(n)
	self.compatibleFeatures_sigma = np.zeros(n)
	
	mcf = ((action - self.mean)/(pow(self.sigma,2))) 
	scf = (pow((action - self.mean),2)/pow(self.sigma,2)) - 1 
	for index in features:
	    self.compatibleFeatures_mu[index] = mcf
	    self.compatibleFeatures_sigma[index] = scf
	    
    def Average_Reward_Update(self):
	self.avgR += self.alphaR * self.delta
    
    def getAction(self,features):
	self.mean = 0.0
	self.sigma = 0.0
	for index in features:
	    self.mean += self.u_mu[index]
	    self.sigma += self.u_sigma[index]
	
	#print self.sigma
	self.sigma = exp(self.sigma)   
	if self.sigma == 0:
	    self.sigma = 1  
	    a = self.mean
	    self.Erase_Traces()	    
	else:
	    a = np.random.normal(self.mean,self.sigma)
	if a > 1:
	    a = 0.99
	if a < -1:
	    a = -0.99
	#print a
	return a
	
    def Erase_Traces(self):
	self.e_mu = np.zeros(n)
	self.ev = np.zeros(n)
	self.e_sigma = np.zeros(n)

def get_features(S):
    F = np.zeros(numTilings)
    tilecode(S[0],S[1],F)
    return F

if __name__ == '__main__':
    numEpisodes = 200
    numRuns = 50    
    runSum = 0.0
    runs = np.zeros(numRuns)

    timeSteps = np.zeros((numRuns,numEpisodes))
    returns = np.zeros((numRuns,numEpisodes))
    for run in range(numRuns):
	mc = ACRL()
	returnSum = 0.0
	for episodeNum in range(numEpisodes):
	       S = mountaincar.init()
	       G = 0
	       steps = 0
	       mc.Erase_Traces()
	       while(1):
		   prev_features = get_features(S)	       
		   A = mc.getAction(prev_features)
		   R,Snext = mountaincar.sample(S,A)
		   mc.R = R
		   if steps >= 5000 or Snext == None: # or isnan(Snext[0]) or isnan(Snext[1]):
		       break
		   mc.Value(prev_features)
		   mc.Delta()
		   next_features = get_features(Snext)
		   mc.Next_Value(next_features)
		   mc.Delta_Update()
		   mc.Average_Reward_Update()
		   mc.Trace_Update_Critic(prev_features)
		   mc.Weights_Update_Critic()
		   mc.Compatible_Features(A,prev_features)
		   mc.Trace_Update_Actor()
		   mc.Weights_Update_Actor()
		   S = Snext
		   G += R
		   steps += 1	       
	       print "Run = ", run, "Episode = ", episodeNum, "Return = ", G
	       returns[run][episodeNum] = G
               timeSteps[run][episodeNum] = steps
               returnSum = returnSum + G
	print "Average return:", returnSum/numEpisodes
        runs[run] = returnSum
        runSum += returnSum
    print "Overall average return:", runSum/numRuns/numEpisodes

    print np.mean(runs)          # Mean of performance numbers
    print np.std(runs)           # Standard deviation of the performance numbers 
    print (np.std(runs)/sqrt(numRuns))      # Standard Error of the performance numbers 
    np.savetxt('returns', returns)
    np.savetxt('timeSteps', timeSteps)	    
    
