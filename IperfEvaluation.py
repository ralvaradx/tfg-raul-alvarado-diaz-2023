import os
import Utils
import time
from mininet.node import Host
from InfoDataclasses import TrafficInfo

import re
from signal import SIGINT

def iperfAll(hosts : list[Host], trafficInfo : TrafficInfo, outDirectory : str, asynchronousTest : bool):
	nNodes = len(hosts)
	testCount = (nNodes * nNodes - nNodes)

	print(Utils.color.BLUE + "Iperfing all hosts", "(asynchronously)" if asynchronousTest else "(synchronously)", Utils.color.END)

	if(not os.path.exists(outDirectory)):
		os.makedirs(outDirectory)

	# Open pipes of the iperf servers, to be shut down once all tests have finished.
	popens = {}
	for srcHostIndex in range(nNodes):
		for dstHostIndex in range(nNodes):
			if(srcHostIndex == dstHostIndex):
				continue
						
			port = findPort(srcHostIndex, dstHostIndex)
			srcHost = hosts[srcHostIndex]
			dstHost = hosts[dstHostIndex]

			outputFilename = outDirectory + "/iperfresult_" + srcHost.name + "_" + dstHost.name + ".txt"
			iperfServerCommand = "iperf -s " + " -i 1 " + " -p " + str(port) + " -f M " + " -o " + outputFilename+ " &"

			popens[srcHostIndex, dstHostIndex] = srcHost.popen(iperfServerCommand)
	print(Utils.color.GREEN + "All IPERF servers started!" + Utils.color.END)

	iperfResultProgress = 0
	for srcHostIndex in range(nNodes):
		for dstHostIndex in range(nNodes):
			if(srcHostIndex == dstHostIndex):
				continue

			srcHost = hosts[srcHostIndex]
			dstHost = hosts[dstHostIndex]
			port = findPort(dstHostIndex, srcHostIndex)
			trafficVolume = int(trafficInfo.traffic[srcHost, dstHost])
			if(trafficVolume == 0):
				trafficVolume = 1000
			iperfClientCommand = "iperf -c " + dstHost.IP() + " -p " + str(port) + " -n " + str(trafficVolume) + "B "
			if(asynchronousTest):
				srcHost.cmd(iperfClientCommand + " &")
			else:
				Utils.progressBar(iperfResultProgress, testCount)
				srcHost.cmd(iperfClientCommand)

			iperfResultProgress += 1

	if not asynchronousTest:
		Utils.finishProgressBar() 

	if(asynchronousTest): 
		finishedTests = 0
		print(Utils.color.BLUE + "Waiting for tests to finish..." + Utils.color.END)
		while(finishedTests < testCount):
			Utils.progressBar(finishedTests, testCount)
			time.sleep(5)
			finishedTests = getFinishedTests(hosts=hosts, outDirectory=outDirectory)
		Utils.finishProgressBar()

	print(Utils.color.BLUE + "Shutting down iperf servers..." + Utils.color.END)
	for pipe in popens.values():
		pipe.send_signal(SIGINT)
	time.sleep(10)

	print(Utils.color.GREEN + "Done! Output files have been written in " + outDirectory + "/")
			

def findPort(srcHostIndex : int, dstHostIndex : int) -> str:
	srcHostIndex = str(srcHostIndex)
	dstHostIndex = str(dstHostIndex)

	if(len(srcHostIndex) == 2 and len(dstHostIndex) == 2):
		# Both have 2 digits
		return "2" + srcHostIndex + dstHostIndex
	if(len(srcHostIndex) + len(dstHostIndex) == 3):
		# One has 2 digits; the other, only 1
		return "19" + srcHostIndex + dstHostIndex
	if(len(srcHostIndex) + len(dstHostIndex) == 2):
		# Both have 1 digit
		return "99" + srcHostIndex + dstHostIndex


def getFinishedTests(hosts : list[Host], outDirectory : str) -> int:
	finishedTests = 0
	for hostSrc in hosts:
		for hostDst in hosts:
			finished = True
			if(hostSrc == hostDst):
				continue 

			outputFileName = outDirectory + "/iperfresult_" + hostSrc.name + "_" + hostDst.name + ".txt"
			file = open(outputFileName, "r+")
			fileContent = file.read()
			file.close()

			lineRegex = r"\[  1\] 0\.0000-(\d+\.\d+)"
			lastLine = fileContent.splitlines()[-1]
			regexMatch = re.search(lineRegex, lastLine)
			if(regexMatch != None):
				finishedTests += 1
	
	return finishedTests