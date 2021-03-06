#!/usr/bin/env python2

import subprocess as sp
import os
import sys
import datetime
from optparse import OptionParser

##########################################
#
# INTERFACE

def commandline_interface():
    parser = OptionParser()

    # parameters for our scripts
    parser.add_option("-g",              dest="graph_file")
    parser.add_option("-c",              dest="communities_file")
    parser.add_option("-s",              dest="seed_file")
    parser.add_option("-o",              dest="output_file",   help="write the nmi value to this file")
    parser.add_option("-i",              dest="iterations",    type="int", help="the number of iterations for the iterative method")

    options, args = parser.parse_args()

    valid = True
    if not (options.output_file and
            options.communities_file and
            options.seed_file and
            options.output_file and
            options.iterations):
        parser.print_help()
        valid = False

    return options, valid


##########################################
# 
# SETTINGS

method="fraction"
factor=1.1


##########################################
# 
# EXECUATBLES

ROOT = os.path.dirname(os.path.realpath(__file__)) + "/.."
LFR = ROOT + "/external/binary_networks/benchmark"
communityDetectionIterative = ROOT + "/scripts/communityDetectionIterative.py"
communityClassifier = ROOT + "/scripts/communityClassifier.py"
graphParser = ROOT + "/scripts/graphParser.py"
NMI = ROOT + "/external/NMI/mutual"


##########################################
# 
# TEMPORARY FILES

affinities = "tmp_affinies"
# the output from the community classifier
detectedCommunities = "tmp_detectedCommunities"


######################################
#
# MAIN

options, valid = commandline_interface()

if valid:

    try:

        print "=> perform community detection"
        sp.check_call([communityDetectionIterative,
            "-g", options.graph_file,
            "-s", options.seed_file,
            "-A", affinities,
            "-i", str(options.iterations),
            "-m", method,
            "-f", str(factor)])


        print "=> classify communities and calculate NMI"

        nmis = []
        for i in range(options.iterations):

            affinities_i = affinities + "_" + str(i)
            detectedCommunities_i = detectedCommunities + "_" + str(i)

            sp.check_call([communityClassifier,
                "-a", affinities_i,
                "-c", options.communities_file,
                "-C", detectedCommunities_i])

            nmis.append(sp.check_output([NMI, options.communities_file, detectedCommunities_i]).split()[1])

        with open (options.output_file, "w") as f:
            f.writelines("\n".join(nmis))

        for i in range(options.iterations):
            os.remove(options.seed_file + "_" + str(i))
            os.remove(affinities + "_" + str(i))
            os.remove(detectedCommunities + "_" + str(i))
        os.remove(options.seed_file + "_" + str(options.iterations))


        print ""
        print "======================="
        print ""
        print ""
        print "NMI:" 
        print "----"
        with open (options.output_file, "r") as f:
            print f.read()



    except sp.CalledProcessError:
        print ""
        print "======================="
        print ""
        sys.stderr.write(str(datetime.datetime.now()) + " - ERROR in subprocess.\n")
        sys.exit(1)
