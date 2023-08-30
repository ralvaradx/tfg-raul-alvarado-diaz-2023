from mininet.net import Mininet
from mininet.node import Host
import Utils
from InfoDataclasses import RoutingInfo
from InfoDataclasses import TopologyInfo
import os

def installFlowTables(topologyInfo : TopologyInfo, routingInfo : RoutingInfo, outDirectory : str):
    print(Utils.color.BLUE + "Installing flow tables..." + Utils.color.END)

    if(not os.path.exists(outDirectory)):
        os.makedirs(outDirectory)

    for srcNodeIndex in range(topologyInfo.nNodes):
        switch = topologyInfo.switches[srcNodeIndex]

        nodeFlowTable_filename = outDirectory + "/flows_" + switch.name + ".txt"
        nodeFlowTable = open(nodeFlowTable_filename, "w+")

        for dstNodeIndex in range(topologyInfo.nNodes):
            nextHopNode = routingInfo.nextHop[srcNodeIndex, dstNodeIndex] if(srcNodeIndex != dstNodeIndex) else srcNodeIndex

            srcHost = topologyInfo.hosts[srcNodeIndex]
            dstHost = topologyInfo.hosts[dstNodeIndex]

            ip_dst = dstHost.IP()

            outputInterface = findOutput(srcNodeIndex=srcNodeIndex, dstNodeIndex=nextHopNode, configurationInfo=topologyInfo)

            flow = "priority=1,dl_type=0x0800,nw_dst=" + ip_dst + ",actions=output:" + str(outputInterface) + "\n"
            arpFlow = "priority=1,dl_type=0x806,nw_dst=" + ip_dst + ",actions=output:" + str(outputInterface) + "\n"

            
            if(srcNodeIndex != dstNodeIndex
                and topologyInfo.isLinkUnidirectional(srcNodeIndex, dstNodeIndex)
                and not topologyInfo.isLinkEnabled(dstNodeIndex, srcNodeIndex)):
                
                blockedIngressPort = findOutput(srcNodeIndex=srcNodeIndex, dstNodeIndex=dstNodeIndex, configurationInfo=topologyInfo)
                firewallFlow = "priority=2,in_port=" + str(blockedIngressPort) + ",actions=drop" + '\n'
                nodeFlowTable.write(firewallFlow)

            nodeFlowTable.write(flow)
            nodeFlowTable.write(arpFlow)
    
        nodeFlowTable.close()
        switch.cmd("ovs-ofctl add-flows " + switch.name + " " + nodeFlowTable_filename)
    print(Utils.color.GREEN + "Done! Flow tables successfully installed on switches" + Utils.color.END)


# Esto deberia hacerse ya en el ConfigurationMatrixParser
def findOutput(srcNodeIndex : int, dstNodeIndex : int, configurationInfo : TopologyInfo) -> int:
    try:
        if(srcNodeIndex == dstNodeIndex):
            return 1
        else:
            srcNodeInterfacesDictionary : dict[int, int] = {}
            interfaceIndex : int = 2
            for n in range(configurationInfo.nNodes):
                if(configurationInfo.linkExists(srcNodeIndex, n)):
                    srcNodeInterfacesDictionary[n] = interfaceIndex
                    interfaceIndex += 1
            
            return srcNodeInterfacesDictionary[dstNodeIndex]
    except KeyError as e:
        print(Utils.color.YELLOW + "WARNING: Could not find output interface from node", srcNodeIndex, "to", dstNodeIndex, " - Mismatched configuration and routing?\nKeyError:", str(e) + Utils.color.END)
        return 1