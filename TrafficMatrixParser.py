from InfoDataclasses import TrafficInfo
from InfoDataclasses import TopologyInfo
from mininet.node import Host
import Utils
import os
def parseTrafficInfo(filename : str, topologyInfo : TopologyInfo) -> TrafficInfo:
    if not os.path.isfile(filename):
        print(Utils.color.YELLOW + "WARNING: Could not parse traffic matrix: file", filename, "does not exist" + Utils.color.END)
        return None
    
    trafficMatrixFile = open(filename, "r")
    trafficMatrix = trafficMatrixFile.read()
    trafficMatrixFile.close()

    allNodeTraffic = []
    allLines = trafficMatrix.splitlines()
    for n in range(topologyInfo.nNodes):
        allNodeTraffic.append(allLines[n])

    traffic : dict[tuple[Host, Host], int]= {}

    for srcNodeIndex in range(topologyInfo.nNodes):
        nodeTraffic = allNodeTraffic[srcNodeIndex].split(',')
        for dstNodeIndex in range(topologyInfo.nNodes):
            srcHost = topologyInfo.hosts[srcNodeIndex]
            dstHost = topologyInfo.hosts[dstNodeIndex]

            traffic[srcHost, dstHost] = float(nodeTraffic[dstNodeIndex])

    return TrafficInfo(traffic=traffic)

