#!/usr/bin/env python2

import datetime
import sys
import os
import numpy as np
import subprocess as sp
import json
from optparse import OptionParser
from collections import defaultdict

from pprint import pprint


#path to the repositories root
ROOT = os.path.dirname(os.path.realpath(__file__)) + "/.."

#for logging purposes
LOGERROR = open("LOGERROR", 'w')
DEVNULL = open(os.devnull, 'w')

OUTPUTFOLDER = "./nmi_values_" + str(datetime.datetime.now()).replace(" ", "_") + "/"

################################

class Benchmark:
    def __init__( self
                , numberOfNodes
                , communitySize
                , _seedFraction
                , _samplesPerDatapoint
                , _mixingParam
                , _overlapRange
                , _overlapAmount
                , _iterations
                , _classification_strategy):


        # LFR parameters
        self.k = 20
        self.maxk = 50
        self.t1 = 2
        self.t2 = 1
        self.N = numberOfNodes
        self.om = _overlapAmount


        if communitySize == "small":
            self.minc = 10
            self.maxc = 50
            
            
        elif communitySize == "big":
            self.minc = 20 
            self.maxc = 100 
            
            
        else:
            raise Exception("wrong parameter for communitySize. it must either be small or big")

        #how many graphs with the same parameters
        self.samplesPerDatapoint = _samplesPerDatapoint

        #the values for the amount of overlap
        self.overlapRange = _overlapRange

        #the values for the mixing parameter
        self.mu= _mixingParam

        #the fraction of seed nodes
        self.seedFraction = _seedFraction

        #the number of iterations for the iterative method
        self.iterations = _iterations

        #a list of nmi-values for each overlap parameter and round for the iterative method
        #self.nmiValues[on][round][i] will give the nmi for mixingParam mu after the "round"th iterative round and the ith iteration
        self.nmiValues = []

        #the mean nmi-value for each overlap parameter
        #self.nmiValues[on][round] will give the mean-nmi for mixingParam mu after the "round"th iterative round
        self.nmiValuesMean = []

        self.classification_strategy = _classification_strategy

        #the filename under which this object gets stored
        self.filename = ( str(self.N) + "N"
                      + "_" + communitySize + "Communities"
                      + "_" + str(self.mu) + "mu"
                      + "_" + str(self.om) + "om"
                      + "_" + str(self.seedFraction) + "seed"
                      + ".json" 
                      )


    # fill in all data by running LFRtoNMI.sh a couple times
    def run(self):
        print ""
        print "====================================="
        print ""
        print "parameters for next benchmark:"
        print "seedFraction =",           self.seedFraction 
        print "N =",                      self.N
        print "minc =",                   self.minc
        print "maxc =",                   self.maxc
        print "k =",                      self.k
        print "maxk =",                   self.maxk
        print "t1 =",                     self.t1
        print "t2 =",                     self.t2
        print "mu =",                     self.mu
        print "om =",                     self.om
        print "iterations =",             self.iterations
        print "samplesPerDatapoint =",    self.samplesPerDatapoint
        print "_overlapRange =",            self.overlapRange
        print "classificationStrategy =", self.classification_strategy

         
        for on in self.overlapRange:
            on_p = on                   #the percentage of the overlapping nodes
            on = on * self.N            #the actual value of overlapping nodes
            print ""
            print "on = " + str(on_p)+"% (" + str(on) + " vertices)"
            print "---------"

            successful = 0
            successiveErrors = 0

            
            #nmis[round][i] contains the nmi for a fixed mixingParam on after the "round"th iterative round and the ith iteration
            nmiValuesFixedOn = [ [] for x in range(self.iterations) ]

            while successful < self.samplesPerDatapoint:
                #call graph generator and calculate nmi

                # this scripts generates a graph, runs the algorithm and calculates the nmi
                scriptName = ROOT + "/scripts/LFRtoNMI.py"
                # the file the script stores the nmi values in
                nmiFileName = "tmp_nmivalues"

                if not os.path.isfile(scriptName):
                        raise Exception("path to LFRtoNMI.py is wrong")
                call = [ scriptName
                       , "--k", str(self.k)
                       , "--maxk" ,str(self.maxk)
                       , "--t1", str(self.t1)
                       , "--t2", str(self.t2)
                       , "--minc",str(self.minc)
                       , "--maxc", str(self.maxc)
                       , "--mu", str(self.mu)
                       , "--N", str(self.N)
                       , "--on", str(on)
                       , "--om", str(self.om)
                       , "-o", nmiFileName
                       , "-s", str(self.seedFraction)
                       , "-i", str(self.iterations)
                       , "--seed_strategy", "degree"
                       , "--classification_strategy", self.classification_strategy
                       ]

                returnValue = sp.call(call, stdin=None , stderr=LOGERROR, stdout=DEVNULL, shell=False)

                if returnValue == 0:
                    #script was successful
                    successful = successful + 1
                    successiveErrors = 0

                    nmisOfIteration = []
                    with open (nmiFileName, "r") as f:
                        for line in f:
                            nmisOfIteration.append(float(line))

                    if len(nmisOfIteration) != self.iterations:
                        raise Exception("wrong number of lines in nmi-file")

                    for r in range(self.iterations):
                        nmiValuesFixedOn[r].append(nmisOfIteration[r])

                    print "(" + str(successful) + "/" + str(self.samplesPerDatapoint) + "): " + str(nmisOfIteration)
                else:
                    successiveErrors = successiveErrors + 1
                    if successiveErrors > 100:
                        raise Exception("LFRtoNMI crashes a lot for these parameters")

            tmp = defaultdict()
            tmp["on"] = on_p
            tmp["value"] = nmiValuesFixedOn
            self.nmiValues.append(tmp)

            tmpMean = defaultdict()
            tmpMean["on"] = on_p
            tmpMean["value"] = [[] for x in range(self.iterations) ]
            for r in range(self.iterations):
                tmpMean["value"][r] = np.mean(nmiValuesFixedOn[r])
            self.nmiValuesMean.append(tmpMean)




    # dump the object as json file
    def dump(self):
        obj = defaultdict()
        obj["_k"]                       = self.k
        obj["_maxk"]                    = self.maxk
        obj["_t1"]                      = self.t1
        obj["_t2"]                      = self.t2
        obj["_N"]                       = self.N
        obj["_mu"]                      = self.mu
        obj["_om"]                      = self.om
        obj["_minc"]                    = self.minc
        obj["_maxc"]                    = self.maxc
        obj["_iterations"]              = self.iterations
        obj["_samplesPerDatapoint"]     = self.samplesPerDatapoint
        obj["_seedFraction"]            = self.seedFraction
        obj["_classification_strategy"] = self.classification_strategy
        obj["nmiValues"]                = self.nmiValues
        obj["nmiValuesMean"]            = self.nmiValuesMean

        #print (options.outputfolder + "/" + self.filename, 'w')
        with open(options.outputfolder + "/" + self.filename, 'w') as outfile:
            json.dump(obj, outfile, sort_keys=True, indent=4, separators=(',', ': '))

################################



# interface
def commandline_interface():
    usage = "usage: %prog"
    parser = OptionParser()
    
    # command line options
    parser.add_option("-n", dest="numberOfNodes", type="string",
        help="whitespace separated list of graph sizes")

    parser.add_option("-c", dest="communitySizes", type="string",
        help="whitespace separated list of community sizes")

    parser.add_option("-s", dest="seedFractions", type="string",
        help="whitespace separated list of seed percentages")

    parser.add_option("-o", dest="outputfolder", type="str",
        help="the folder the json files will be written to")

    parser.add_option("-m", dest="mixingParam", type="float",
        help="mxing parameter")

    parser.add_option("-O", dest="overlapRange", type="str",
        help="start stop step, separated by whitespaces")

    parser.add_option("-i", dest="iterations", type="int",
        help="number of iterations for the iterative method")

    parser.add_option("--samples_per_datapoint", dest="samplesPerDatapoint", type="int",
        help="samplse per data point")

    parser.add_option("--classification_strategy", dest="classification_strategy",
        help="")

    parser.add_option("--om",dest="overlap_amount",type="int",help="the amount of communities an overlapping vertex is in")

    parser.add_option("--overwrite_file", dest="overwrite_file", type="int", default=1,
        help="if nonzero exit if output file already exists")

    
    global options, args
    (options, args) = parser.parse_args()

    if not (options.numberOfNodes and 
            options.communitySizes and
            options.seedFractions and
            options.outputfolder and
            options.samplesPerDatapoint and
            options.mixingParam and
            options.iterations and
            options.classification_strategy): 
        parser.print_help()
        return False
    return True


options, args = 0, 0
if commandline_interface():

    numberOfNodes       = [int(N) for N in options.numberOfNodes.split()]
    communitySizes      = options.communitySizes.split()
    seedFractions       = [float(s) for s in options.seedFractions.split()]
    samplesPerDatapoint = options.samplesPerDatapoint


    mixingParam          = options.mixingParam
    overlap_amount      = options.overlap_amount
    tmp                 = [float(x) for x in options.overlapRange.split()]
    overlapRange         = [x for x in np.arange(tmp[0], tmp[1], tmp[2])]

   


    print "outputfolder:", options.outputfolder
    if not os.path.exists(options.outputfolder):
        os.makedirs(options.outputfolder)

    print "will run the following benchmarks:"
    benchmarks = []
    for N in numberOfNodes:
        for size in communitySizes:
            for seed in seedFractions:
                print "> create Benchmark(", N, size, seed, samplesPerDatapoint, mixingParam, options.iterations, options.classification_strategy, ")"
                benchmarks.append(Benchmark(N, size, seed, samplesPerDatapoint, mixingParam,overlapRange,overlap_amount, options.iterations, options.classification_strategy))

    print "start benchmarks"
    for benchmark in benchmarks:
        if os.path.isfile(options.outputfolder + "/" + benchmark.filename) and not options.overwrite_file:
            print "file already exists, abort"
        else:
            benchmark.run()
            benchmark.dump()
