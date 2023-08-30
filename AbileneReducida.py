"""
Pruebas con Mininet sobre la topologia Abilene reducida.

Demostracion de cómo debe definirse una topologia en Mininet, definir e instalar las reglas para el encaminamiento
manualmente, y usar los modulos PingEvaluation + PingResultParser, IperfEvaluation + IperfResultParser del framework
para evaluar y representar las pruebas de ping e iperf, respectivamente.
"""

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSSwitch
from mininet.link import TCLink

import PingEvaluation
import PingResultParser
import IperfEvaluation
import IperfResultParser

import Utils
import traceback

def networkDefinition ():
	net = Mininet (topo = None, build = False, switch = OVSSwitch, link = TCLink)
	# net.addController("c0")

	# Add hosts and switches
	DNVRng = net.addSwitch("s0")
	hostDNVRng = net.addHost("h0")
	SNVAng = net.addSwitch("s1")
	hostSNVAng = net.addHost("h1")
	STTLng = net.addSwitch("s2")
	hostSTTLng = net.addHost("h2")

	# Add links
	net.addLink( hostDNVRng, DNVRng)
	net.addLink( hostSNVAng, SNVAng)
	net.addLink( hostSTTLng, STTLng)
	net.addLink( STTLng, DNVRng, bw=152 )
	net.addLink( STTLng, SNVAng, bw=152 )

	print("Starting sim")
	net.start()

	try:

		flujoDNVRng = open("./DNVRng.txt","w+")
		flujoSNVAng = open("./SNVAng.txt","w+")
		flujoSTTLng = open("./STTLng.txt","w+")


		##########################################################################
		# DNVR flows
		flowDNVR = "dl_type=0x0800,nw_dst=" + hostDNVRng.IP() + ",actions=output:1\n"
		arpFlowDNVR = "dl_type=0x806,nw_dst=" + hostDNVRng.IP() + ",actions=output:1\n"
		
		flowDNVR_STTL = "dl_type=0x0800,nw_dst=" + hostSTTLng.IP() + ",actions=output:2" + "\n"
		arpFlowDNVR_STTL = "dl_type=0x806,nw_dst=" + hostSTTLng.IP() + ",actions=output:2\n"

		flowDNVR_SNVA = "dl_type=0x0800,nw_dst=" + hostSNVAng.IP() + ",actions=output:2" + "\n"
		arpFlowDNVR_SNVA = "dl_type=0x806,nw_dst=" + hostSNVAng.IP() + ",actions=output:2\n"

		##########################################################################
		# SNVA flows
		flowSNVA = "dl_type=0x0800,nw_dst=" + hostSNVAng.IP() + ",actions=output:1\n"
		arpFlowSNVA = "dl_type=0x806,nw_dst=" + hostSNVAng.IP() + ",actions=output:1\n"

		flowSNVA_DNVRng = "dl_type=0x0800,nw_dst=" + hostDNVRng.IP() + ",actions=output:2\n"
		arpFlowSNVA_DNVRng = "dl_type=0x806,nw_dst=" + hostDNVRng.IP() + ",actions=output:2\n"

		flowSNVAg_STTL = "dl_type=0x0800,nw_dst=" + hostSTTLng.IP() + ",actions=output:2\n"
		arpFlowSNVAng_STTL = "dl_type=0x806,nw_dst=" + hostSTTLng.IP() + ",actions=output:2\n"

		##########################################################################
		# STTL flows
		flowSTTL = "dl_type=0x0800,nw_dst=" + hostSTTLng.IP() + ",actions=output:1\n"
		arpFlowSTTL = "dl_type=0x806,nw_dst=" + hostSTTLng.IP() + ",actions=output:1\n"	

		flowSTTL_DNVR = "dl_type=0x0800,nw_dst=" + hostDNVRng.IP() + ",actions=output:2\n"
		arpFlowSTTL_DNVR = "dl_type=0x806,nw_dst=" + hostDNVRng.IP() + ",actions=output:2\n"

		flowSTTL_SNVA = "dl_type=0x0800,nw_dst=" + hostSNVAng.IP() + ",actions=output:3\n"
		arpFlowSTTL_SNVA = "dl_type=0x806,nw_dst=" + hostSNVAng.IP() + ",actions=output:3\n"

		flujoDNVRng.write(flowDNVR)
		flujoDNVRng.write(arpFlowDNVR)
		flujoDNVRng.write(flowDNVR_STTL)
		flujoDNVRng.write(arpFlowDNVR_STTL)
		flujoDNVRng.write(flowDNVR_SNVA)
		flujoDNVRng.write(arpFlowDNVR_SNVA)

		flujoSNVAng.write(flowSNVA)
		flujoSNVAng.write(arpFlowSNVA)
		flujoSNVAng.write(flowSNVA_DNVRng)
		flujoSNVAng.write(arpFlowSNVA_DNVRng)
		flujoSNVAng.write(flowSNVAg_STTL)
		flujoSNVAng.write(arpFlowSNVAng_STTL)

		flujoSTTLng.write(flowSTTL_DNVR)
		flujoSTTLng.write(arpFlowSTTL_DNVR)
		flujoSTTLng.write(flowSTTL_SNVA)
		flujoSTTLng.write(arpFlowSTTL_SNVA)
		flujoSTTLng.write(flowSTTL)
		flujoSTTLng.write(arpFlowSTTL)


		flujoDNVRng.close()
		flujoSNVAng.close()
		flujoSTTLng.close()

		# Install manually-defined flows
		DNVRng.cmd("ovs-ofctl add-flows s0 ./DNVRng.txt")
		SNVAng.cmd("ovs-ofctl add-flows s1 ./SNVAng.txt")
		STTLng.cmd("ovs-ofctl add-flows s2 ./STTLng.txt")

		CLI(net)

		hostList = [hostDNVRng, hostSNVAng, hostSTTLng]

		PingEvaluation.pingAll(hosts=hostList, pingForSeconds=30, outDirectory="results/pings_async", asynchronousTest=True)
		PingEvaluation.pingAll(hosts=hostList, pingForSeconds=30, outDirectory="results/pings_sync", asynchronousTest=False)

		#IperfEvaluation.iperfAll(hosts=hostList, iperfForSeconds=30, outDirectory="results/iperf_async", asynchronousTest=True)
		#IperfEvaluation.iperfAll(hosts=hostList, iperfForSeconds=30, outDirectory="results/iperf_sync", asynchronousTest=False)

		##########################################################################
		# Plot ping results
		pingResultsAsync = PingResultParser.parseAll(hosts=hostList, resultsDirectory="results/pings_async", skipFirstPing=True)
		if(pingResultsAsync != None):
			PingResultParser.plotResults(pingResultInfo=pingResultsAsync, title="Ping results for reduced Abilene network", outDirectory="results/plots/", fileName="pingresults_abilene_reduced_async")
			
		pingResultsSync = PingResultParser.parseAll(hosts=hostList, resultsDirectory="results/pings_sync", skipFirstPing=True)
		if(pingResultsSync != None):
			PingResultParser.plotResults(pingResultInfo=pingResultsSync, title="Ping results for reduced Abilene network",  outDirectory="results/plots/", fileName="pingresults_abilene_reduced_sync")
		
		##########################################################################
		# Plot Iperf results
		iperfResultAsync = IperfResultParser.parseAll(hosts=hostList, iperfCount=30, resultsDirectory="results/iperf_async")
		if(iperfResultAsync != None):
			IperfResultParser.plotResults(iperfResultInfo= iperfResultAsync, title="Iperf results for reduced Abilene network", outDirectory="results/plots/", fileName="iperfresults_abilene_reduced_async")
		
		iperfResultSync = IperfResultParser.parseAll(hosts=hostList, iperfCount=30, resultsDirectory="results/iperf_sync")
		if(iperfResultSync != None):
			IperfResultParser.plotResults( iperfResultInfo=iperfResultSync, title="Iperf results for reduced Abilene network", outDirectory="results/plots/", fileName="iperfresults_abilene_reduced_sync")


		net.stop()
	except:
		print(Utils.color.RED + "An exception has occurred. Stopping the simulation..." + Utils.color.END)
		traceback.print_exc()
		net.stop()

if __name__ == "__main__":
	networkDefinition()
