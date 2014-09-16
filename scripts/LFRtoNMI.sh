#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

ROOT=$DIR/..

LFR=$ROOT/external/binary_networks/benchmark
communityDetection=$ROOT/algorithm/build/community_detection
communityClassifier=$ROOT/scripts/communityClassifier.py
graphParser=$ROOT/scripts/graphParser.py
NMI=$ROOT/code/coverComparision/mutual

# the percentage of seed nodes
percentage=$1

# the graph output of the lfr
graphLFR="network.dat"
# the community output of the lfr
communitiesLFR="community.dat"
# the graph generated by the graph parser
graph="tmp_graph"
# the community file generated by the graph parser
communities="tmp_communities"
# the seed-node file generated by the graph parser
seedNodes="tmp_seedNodes"
# the affinity output from the c++ algorithm
affinities="tmp_affinies"
# the output from the community classifier
detectedCommunities="tmp_detectedCommunities"

# fail fast
set -e

echo "=> delete old files"
rm -f $graphLFR
rm -f $communitiesLFR
rm -f $graph
rm -f $communities
rm -f $seedNodes
rm -f $affinities
rm -f $detectedCommunities

echo "=> run LFR"
$LFR "${@:2}"

echo "=> convert the LFR files to our file format and get the seed nodes"
$graphParser -g $graphLFR -G $graph -c $communitiesLFR -C $communities -s $seedNodes -n $percentage

echo "=> perform community detection"
$communityDetection $graph $seedNodes $affinities

echo "=> classify communities"
$communityClassifier -a $affinities -o 0 -c $detectedCommunities

echo "=> calculate NMI"
$NMI $communities $detectedCommunities
