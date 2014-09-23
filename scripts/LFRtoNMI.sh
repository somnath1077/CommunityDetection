#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT=$DIR/..

LFR=$ROOT/external/binary_networks/benchmark
#communityDetection=$ROOT/algorithm/build/community_detection
communityDetection=$ROOT/algorithm/script/community_detection_nonoverlapping_iterative.py
communityClassifier=$ROOT/scripts/communityClassifier.py
graphParser=$ROOT/scripts/graphParser.py
NMI=$ROOT/external/NMI/mutual

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
# write the nmi value to this file
nmiValue="tmp_nmivalue"

# the number of iterations for the iterative method
iterations=20
# the multiplication factor for the iterative method
factor=1.1

# fail fast
set -e

echo "=> run LFR"
$LFR "${@:2}"

echo "=> convert the LFR files to our file format and get the seed nodes"
$graphParser -g $graphLFR -G $graph -c $communitiesLFR -C $communities -s $seedNodes -n $percentage

echo "=> perform community detection"
$communityDetection -g $graph -s $seedNodes -a $affinities -i $iterations -f $factor

rm -f $nmiValue
echo "=> classify communities and calculate NMI"
for i in $(seq 0 $(($iterations-1))); do 
    #echo "($(($i+1))/$iterations)"
    $communityClassifier -a ${affinities}_$i -o 0 -c ${detectedCommunities}_$i
    $NMI $communities ${detectedCommunities}_$i | awk '{print $2 }' >> $nmiValue
done

echo "=> delete files except for $nmiValue"
rm $graphLFR
rm $communitiesLFR
rm $graph
rm $communities
rm $seedNodes
rm ${seedNodes}_$iterations
for i in $(seq 0 $(($iterations-1))); do 
    rm ${seedNodes}_$i
    rm ${affinities}_$i
    rm ${detectedCommunities}_$i
done

echo ""
echo "======================="
echo ""
echo ""
echo "NMI:" 
echo "----"
cat $nmiValue

