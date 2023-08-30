from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import OVSSwitch

from InfoDataclasses import TopologyInfo
from mininet.net import Mininet
from mininet.node import Host
import Utils
import os

def defineTopology(capacityMatrixFilename : str, configurationFilename : str) -> TopologyInfo:
    net = Mininet (link = TCLink)

    if not os.path.isfile(capacityMatrixFilename):
        print(Utils.color.RED + "ERROR: Could not parse capacity matrix: file", capacityMatrixFilename, "does not exist" + Utils.color.END)
        return None
    
    capacityMatrixFile = open(capacityMatrixFilename, "r")
    capacityMatrix = capacityMatrixFile.read()
    capacityMatrixFile.close()

    if not os.path.isfile(configurationFilename):
        print(Utils.color.RED + "ERROR: Could not parse configuration matrix: file", configurationFilename, "does not exist" + Utils.color.END)
        return None
    
    configurationFile = open(configurationFilename, "r")
    configuration = configurationFile.read()
    configurationFile.close()

    configurationMatrixRows = configuration.splitlines()
    nNodesConfiguration = len(configurationMatrixRows[0].split(','))

    capacityMatrixRows = capacityMatrix.splitlines()
    nNodesCapacity = len(capacityMatrixRows[0].split(','))

    if(nNodesConfiguration != nNodesCapacity):
        print(Utils.color.RED + "ERROR: Number of nodes in capacity and configuration matrices do not match." + Utils.color.END)
        return None
    
    nNodes = nNodesConfiguration

    print(Utils.color.BLUE + "Defining network topology..." + Utils.color.END, end='\r')
    # Add hosts and switches to network
    allHosts = []
    allSwitches = []
    for node in range(nNodes):
        host = net.addHost("h" + str(node))
        switch = net.addSwitch("s" + str(node))
        net.addLink(host, switch)

        # Add to list
        allHosts.append(host)
        allSwitches.append(switch)
    
    links : dict[tuple[Host, Host], float] = {}
    
    # Initialize links matrix
    for srcNodeIndex in range(nNodes):
        srcNodeLinksCapacity = capacityMatrixRows[srcNodeIndex].split(',')
        srcNodeLink = configurationMatrixRows[srcNodeIndex].split(',')
        for dstNodeIndex in range(nNodes):
            enabled = (float(srcNodeLink[dstNodeIndex]) != 0.0)
            linkBandwidth = float(srcNodeLinksCapacity[dstNodeIndex])
            links[srcNodeIndex, dstNodeIndex] = linkBandwidth if enabled else 0.0

    topologyInfo = TopologyInfo(net=net, nNodes=nNodes, hosts=allHosts, switches=allSwitches, links=links)

    # Mininet links will not work if added twice
    for srcNodeIndex in range(nNodes):
        for dstNodeIndex in range(srcNodeIndex, nNodes):
            if(srcNodeIndex == dstNodeIndex):
                continue

            if topologyInfo.linkExists(srcNodeIndex, dstNodeIndex):
                linkBandwidth = topologyInfo.links[srcNodeIndex, dstNodeIndex]
                if(linkBandwidth == 0.0):
                    linkBandwidth = topologyInfo.links[dstNodeIndex, srcNodeIndex]

                linkBandwidth = linkBandwidth/1e7
                net.addLink(allSwitches[srcNodeIndex], allSwitches[dstNodeIndex], bw=linkBandwidth)

    enabledLinks = len(net.links) - len(allSwitches)
    print(Utils.color.GREEN + "Done! Network has", len(allSwitches), "nodes with", enabledLinks, "enabled links" + Utils.color.END)

    return topologyInfo


