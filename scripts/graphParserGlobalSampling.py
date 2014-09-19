#!/usr/bin/env python2

import sys
import datetime
from optparse import OptionParser
from collections import defaultdict
from collections import deque
from random import sample
from math import ceil
import re

# interface
def commandline_interface():
    usage = "usage: %prog"
    parser = OptionParser()
   
    parser.add_option("-g", dest="graph_file_input", type="string",
            help="Input: LFR benchmark graph file")
    parser.add_option("-c", dest="community_file_input", type="string",
            help="Input: LFR benchmark community network")

    parser.add_option("-G", dest="graph_file_output", type="string",
            help="Output: custom graph file")
    parser.add_option("-C", dest="community_file_output", type="string",
            help="Output: custom community file")

    parser.add_option("-s", dest="seed_nodes", type="string",
            help="Output: custom seed-node file")
    parser.add_option("-n", dest="seed_perc", type="int",
            help="percentage of seed nodes (in range 0 to 100)")
   
    global options, args
    (options, args) = parser.parse_args()

    if not options.graph_file_input:
        parser.error("input graph file not given")
        parser.print_help()
        return False

    elif not options.community_file_input:
        parser.error("input community file not given")
        parser.print_help()
        return False

    elif not options.graph_file_output:
        parser.error("output graph file not given")
        parser.print_help()
        return False

    elif not options.community_file_output:
        parser.error("output community file not given")
        parser.print_help()
        return False

    elif not options.seed_nodes:
        parser.error("output seed-node file not given")
        parser.print_help()
        return False

    elif not options.seed_perc:
        parser.error("seed-node percentage not given")
        parser.print_help()
        return False

    return True

# read LFR network file
# returns (graph, max_vertex, max_edge)
def read_graph(file):
    with open (file, "r") as f:
        graph = defaultdict(list)
        max_vertex = 0
        # store edges
        for i, line in enumerate(f):
            splitLine = line.split()
            if len(splitLine) != 2:
                raise Exception("line should have exactly two entries")
            vertex = int(splitLine[0]) - 1
            neighbour = int(splitLine[1]) - 1
            # update number of vertices
            m = max(vertex, neighbour)
            if m > max_vertex:
                max_vertex = m
            # update adjaceny list
            graph[vertex].append(neighbour)
    return graph, max_vertex, i

# read LFR community file
def read_community(file):
    with open (file, "r") as f:
        vertex_communities = defaultdict(list)
        max_community = 0
        #genrate community adjacency list
        for line in f:
            splitLine = line.split()
            if len(splitLine) != 2:
                raise Exception("line should have exactly two entries")

            vertex = int(splitLine[0]) - 1
            community = int(splitLine[1]) - 1
            vertex_communities[vertex].append(community)

            if community > max_community:
                max_community = community

            #match = number.findall(line.strip())
            #for m in match[1:]:
                #vertex_communities[int(match[0]) - 1].append(int(m) - 1)
                ## update number of communities (needed later on)
                #if int(m) - 1 > max_community:
                    #max_community = int(m) - 1

    return vertex_communities, max_community

# check connectivity
def dfs(graph, start, max_vertex):
    visited = set() 
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        if vertex not in visited:
            visited.add(vertex)
            for neighbour in graph[vertex]:
                if neighbour not in visited:
                    queue.append(neighbour)
    # get length of connected component
    return len(visited) - max_vertex == 1

# remap value list as keys, keys as values
def reverse_dictionary(key_valuelist):
    reversed_dict = defaultdict(list)
    for k in key_valuelist:
        for v in key_valuelist[k]:
            reversed_dict[v].append(k)
    return reversed_dict

# generate seed nodes
# returns a dictionary which maps seed nodes to their communities
def generate_seeds(vertex_communities, max_vertex, seed_perc):
    seed_communities = defaultdict(list)
    total_seeds = int(ceil((seed_perc * (max_vertex + 1)) / 100))
    seed_communities = dict(sample(vertex_communities.items(), total_seeds))
    return seed_communities


#write output graph
def write_graph(file, graph, max_vertex, max_edge):
    with open (file, "w") as file:
        # number of vertices, numberOfEdges
        file.write("{0} {1}".format(max_vertex + 1, max_edge + 1))
        for v, neighbours in graph.iteritems():
            for n in neighbours:
                file.write("\n{0} {1}".format(v, n))


#write output community file
def write_communites(file, community_vertices):
    with open (file, "w") as file:
        for c, vertices in community_vertices.iteritems():
            file.write("{0}".format(vertices[0]))
            for v in vertices[1:]:
                file.write(" {0}".format(v))
            file.write("\n")

#write output seed_nodes
def write_seed_nodes(file, seed_communities, max_community):
    with open (file, "w") as file:
        # number of seed nodes, number of communities
        file.write("{0} {1}".format(len(seed_communities), max_community + 1))

        for s, communities in seed_communities.iteritems():
            file.write("\n{0}".format(s))
            i = 0
            for c in sorted(communities):
                while (i < c):
                    file.write(" 0")
                    i += 1
                file.write(" 1")
                j = c
                while (j < max_community):
                    file.write(" 0")
                    j += 1

# main program
options, args = 0, 0
if commandline_interface():
    # read graph
    number = re.compile(r'[0-9]+')
    graph, max_vertex, max_edge = read_graph(options.graph_file_input)

    if dfs(graph, 0, max_vertex):
        # proceed if the graph is connected
        write_graph(options.graph_file_output, graph, max_vertex, max_edge)
        # read, process, and write community file
        vertex_communities, max_community = read_community(options.community_file_input)
        community_vertices = reverse_dictionary(vertex_communities)
        write_communites(options.community_file_output, community_vertices)
        # calculate and write seed file
        seed_communities = generate_seeds(vertex_communities, max_vertex, options.seed_perc)
        write_seed_nodes(options.seed_nodes, seed_communities, max_community)

    else:
        #fail if graph is not connected
        sys.stderr.write(str(datetime.datetime.now()) + " - Error: Graph file is not one connected component!\n")
        sys.exit(1)