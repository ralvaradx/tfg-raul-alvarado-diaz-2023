"""
Pruebas con Mininet sobre la topologia Abilene completa.

Demostracion de cómo usar el framework para definir una red en Mininet y ejecutar las pruebas ping e iperf.
"""

from mininet.cli import CLI

import NetworkTopologyDefinition
import NetworkRouting
import EvaluationController
import TrafficMatrixParser

import PingEvaluation
import PingResultParser

import IperfEvaluation
import IperfResultParser

import Utils
import traceback

def abilene12n():
	topologyInfo = NetworkTopologyDefinition.defineTopology(capacityMatrixFilename="tests/abileneCapMatrix.csv", configurationFilename="tests/Configuraciones/configuracion_0.csv")
	routingInfo = NetworkRouting.buildRoutingInfo(topologyInfo)
	trafficInfo = TrafficMatrixParser.parseTrafficInfo(filename="tests/Matrices de tráfico - Test/matriz_0.csv", topologyInfo=topologyInfo)

	try:
		net = topologyInfo.net
		net.start()
		EvaluationController.installFlowTables(topologyInfo=topologyInfo, routingInfo=routingInfo, outDirectory="flows")
		
		hostList = topologyInfo.hosts

		CLI(net)

		PingEvaluation.pingAll(hosts=hostList, pingForSeconds=30, outDirectory="results/pings_async", asynchronousTest=True)
		PingEvaluation.pingAll(hosts=hostList, pingForSeconds=30, outDirectory="results/pings_sync", asynchronousTest=False)

		IperfEvaluation.iperfAll(hosts=hostList, trafficInfo=trafficInfo, outDirectory="results/iperf_async", asynchronousTest=True)
		IperfEvaluation.iperfAll(hosts=hostList, trafficInfo=trafficInfo, outDirectory="results/iperf_sync", asynchronousTest=False)

		##########################################################################
		# Plot ping results
		pingResultsAsync = PingResultParser.parseAll(hosts=hostList, resultsDirectory="results/pings_async", skipFirstPing=True)
		if(pingResultsAsync != None):
			PingResultParser.plotResults(pingResultInfo=pingResultsAsync, title="Ping results for Abilene network (asynchronous tests)", outDirectory="results/plots/", fileName="pingresults_abilene_async")
			
		pingResultsSync = PingResultParser.parseAll(hosts=hostList, resultsDirectory="results/pings_sync", skipFirstPing=True)
		if(pingResultsSync != None):
			PingResultParser.plotResults(pingResultInfo=pingResultsSync, title="Ping results for Abilene network (synchronous tests)",  outDirectory="results/plots/", fileName="pingresults_abilene_sync")
		
		##########################################################################
		# Plot Iperf results
		iperfResultAsync = IperfResultParser.parseAll(hosts=hostList, iperfCount=30, resultsDirectory="results/iperf_async")
		if(iperfResultAsync != None):
			IperfResultParser.plotResults(iperfResultInfo= iperfResultAsync, title="Iperf results for Abilene network (asynchronous tests)", outDirectory="results/plots/", fileName="iperfresults_abilene_async")
		
		iperfResultSync = IperfResultParser.parseAll(hosts=hostList, iperfCount=30, resultsDirectory="results/iperf_sync")
		if(iperfResultSync != None):
			IperfResultParser.plotResults( iperfResultInfo=iperfResultSync, title="Iperf results for Abilene network (synchronous tests)", outDirectory="results/plots/", fileName="iperfresults_abilene_sync")

		##########################################################################
		# Compare ping results
		PingResultParser.compare(pingResultInfo1=pingResultsAsync, pingResultInfo2=pingResultsSync, 
			   title="Ping results for Abilene network", outDirectory="results/plots/", 
			   fileName="pingresults_abilene_comparison")
		
		IperfResultParser.compare(iperfResultInfo1=iperfResultAsync, iperfResultInfo2=iperfResultSync,
			    title="Iperf results for Abilene network", outDirectory="results/plots/", 
			   fileName="iperfresults_abilene_comparison")

		net.stop()
	except:
		print(Utils.color.RED + "An exception has occurred. Stopping the simulation..." + Utils.color.END)
		traceback.print_exc()
		net.stop()

if __name__ == "__main__":
	abilene12n()
