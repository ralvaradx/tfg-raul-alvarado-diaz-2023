from dataclasses import dataclass
from mininet.node import Host
from mininet.node import Switch
from mininet.net import Mininet
@dataclass
class PingResultInfo:
    minRTT : float
    avgRTT : float
    maxRTT : float
    mdevRTT : float
    allRTT : list[float]

@dataclass
class IperfResultInfo:
    minBandwidth : float
    avgBandwidth : float
    maxBandwidth : float
    mdevBandwidth : float
    allBandwidth : list[float]

@dataclass
class TopologyInfo:
    net : Mininet
    nNodes : int
    hosts: list[Host]
    switches: list[Switch]
    links : dict[tuple[int, int], float]
    
    def linkExists(self, srcNodeIndex : int, dstNodeIndex : int) -> bool:
        src2dst = float(self.links[srcNodeIndex, dstNodeIndex]) != 0.0
        dst2src = float(self.links[dstNodeIndex, srcNodeIndex]) != 0.0

        return src2dst or dst2src
    
    def isLinkUnidirectional(self, srcNodeIndex : int, dstNodeIndex : int) -> bool:
        src2dst = float(self.links[srcNodeIndex, dstNodeIndex]) != 0.0
        dst2src = float(self.links[dstNodeIndex, srcNodeIndex]) != 0.0

        return src2dst != dst2src
    
    def isLinkEnabled(self, srcNodeIndex : int, dstNodeIndex : int) -> bool:
        src2dst = float(self.links[srcNodeIndex, dstNodeIndex]) != 0.0

        return src2dst


@dataclass
class RoutingInfo:
    nextHop : dict[tuple[int, int], int]



@dataclass
class TrafficInfo:
    traffic : dict[tuple[Host, Host], float]