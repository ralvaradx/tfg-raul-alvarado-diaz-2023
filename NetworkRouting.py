from InfoDataclasses import TopologyInfo
from InfoDataclasses import RoutingInfo
from mininet.node import Host
import Utils
import os
import re

def buildRoutingInfo(topologyInfo : TopologyInfo) -> RoutingInfo:
    cost : dict[tuple[int, int], int] = {}
    prevNode : dict[tuple[int, int], int] = {}

    for srcNodeIndex in range(topologyInfo.nNodes):
        # Step 1: Init cost and previous nodes lists
        for dstNodeIndex in range(topologyInfo.nNodes):
            prevNode[srcNodeIndex, dstNodeIndex] = srcNodeIndex
        
            if (dstNodeIndex == srcNodeIndex):
                initialCost = 0
            else:
                if(topologyInfo.isLinkEnabled(srcNodeIndex, dstNodeIndex)):
                    initialCost = 1
                else:
                    initialCost = float('inf')
            cost[srcNodeIndex, dstNodeIndex] = initialCost

        # Step 2: define visited nodes list
        visitedNodes = []
        visitedNodes.append(srcNodeIndex)

        while(len(visitedNodes) != topologyInfo.nNodes):
            # Step 3: Select the minimum cost unvisited node
            minCostSoFar = float('inf')
            visitedNode = srcNodeIndex
            for nodeIndex in range(topologyInfo.nNodes):
                if(nodeIndex in visitedNodes):
                    continue

                if(cost[srcNodeIndex, nodeIndex] < minCostSoFar):
                    visitedNode = nodeIndex
                    minCostSoFar = cost[srcNodeIndex, nodeIndex]
            
            visitedNodes.append(visitedNode)

            # Step 4: Find adjacent nodes
            adjacentNodes = []
            for nodeIndex in range(topologyInfo.nNodes):
                if(nodeIndex == visitedNode):
                    continue

                if(topologyInfo.isLinkEnabled(visitedNode, nodeIndex)):
                    adjacentNodes.append(nodeIndex)
            # Step 5: For every adjacent node, compare its previous cost against the new
            for adjacentNode in adjacentNodes:
                currentDistance = cost[srcNodeIndex, adjacentNode]
                baseDistance = cost[srcNodeIndex, visitedNode]
                addUpDistance = 1

                newDistance = baseDistance + addUpDistance

                if(newDistance < currentDistance):
                    cost[srcNodeIndex, adjacentNode] = newDistance
                    prevNode[srcNodeIndex, adjacentNode] = visitedNode

    # Build next hop dictionary using previous hop
    nextHop : dict[tuple[int, int], int]= {}
    for srcNodeIndex in range(topologyInfo.nNodes):
        for dstNodeIndex in range(topologyInfo.nNodes):
            _nextHop = dstNodeIndex
            while(prevNode[srcNodeIndex, _nextHop] != srcNodeIndex):
                _nextHop = prevNode[srcNodeIndex, _nextHop]

            nextHop[srcNodeIndex, dstNodeIndex] = _nextHop

    return RoutingInfo(nextHop=nextHop)


def parseRoutingInfo(topologyInfo : TopologyInfo, routingMatrixFilename : str) -> RoutingInfo:
    if not os.path.isfile(routingMatrixFilename):
        print(Utils.color.RED + "ERROR: Could not parse routing matrix: file", routingMatrixFilename, "does not exist" + Utils.color.END)
        return None
    routingMatrixFile = open(routingMatrixFilename, "r")
    lines = routingMatrixFile.read().splitlines()
    routingMatrixFile.close()

    nextHop : dict[tuple[int, int], int]= {}
    nNodes = topologyInfo.nNodes

    for srcNode in range(nNodes):
        pattern = "0|\[.*?\]" 
        matches = re.findall(pattern, lines[srcNode]) 

        for dstNode in range(len(matches)):
            nodesPath = matches[dstNode]

            # Cleanup useless characters
            nodesPath = nodesPath.replace('[', '')
            nodesPath = nodesPath.replace(']', '')
            nodesPath = nodesPath.replace(' ', '')

            # Get a list of nodes
            nodesPath = nodesPath.split(',')

            if(len(nodesPath) > 1):
                nextHop[srcNode, dstNode] = int(nodesPath[1])
            else:
                nextHop[srcNode, dstNode] = srcNode

    res = RoutingInfo(nextHop=nextHop)
    return res