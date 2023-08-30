import os
import Utils
import time
from mininet.node import Host

def pingAll(hosts : list[Host], pingForSeconds : int, outDirectory : str, asynchronousTest : bool):
    nNodes = len(hosts)
    testCount = (nNodes * nNodes - nNodes)
    estimatedTimeInSeconds = testCount*pingForSeconds if not asynchronousTest else pingForSeconds

    print(Utils.color.BLUE + "Pinging all hosts for", pingForSeconds, "seconds", "(asynchronously)" if asynchronousTest else "(synchronously)", 
          "Estimated time: ", estimatedTimeInSeconds, "s" + Utils.color.END)

    if(not os.path.exists(outDirectory)):
        os.makedirs(outDirectory)

    pingResultProgress = 0
    for hostSrc in hosts:
        for hostDst in hosts:
            if(hostSrc == hostDst):
                continue 

            outputFileName = outDirectory + "/pingresult_" + hostSrc.name + "_" + hostDst.name + ".txt"
            pingCommand = "ping" + " -w " + str(pingForSeconds) + " " + str(hostDst.IP()) + " > " + outputFileName

            if(asynchronousTest):
                hostSrc.cmd(pingCommand + " &")
            else:
                Utils.progressBar(pingResultProgress, testCount)
                hostSrc.cmd(pingCommand)
                
            pingResultProgress += 1
    if not asynchronousTest:
        Utils.finishProgressBar() 

    if(asynchronousTest):              
        print(Utils.color.BLUE + "Waiting for tests to finish...", end='\r')
        time.sleep(estimatedTimeInSeconds 
                   + estimatedTimeInSeconds/2)
    
    print(Utils.color.GREEN + "Done! Output files have been written in " + outDirectory + "/")