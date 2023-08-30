import re
import Utils

from mininet.node import Host
import matplotlib.pyplot as plt
import statistics
import os


from InfoDataclasses import PingResultInfo


def parse(filename : str) -> PingResultInfo:

    summaryRTTPattern = r"(\d+(?:\.\d+)?)\/(\d+(?:\.\d+)?)\/(\d+(?:\.\d+)?)\/(\d+(?:\.\d+)?)"
    lineRTTPattern = r'time=([\d.]+) ms'

    if not os.path.isfile(filename):
        print(Utils.color.YELLOW + "WARNING: Could not parse ping results: file", filename, "does not exist" + Utils.color.END)
        return None

    pingResultFile = open(filename, "r+")
    pingResults = pingResultFile.read()
    pingResultFile.close()

    # Get all RTT values
    allRTT = []
    for line in pingResults.splitlines():
        if "time=" in line:
            regexMatch = re.search(lineRTTPattern, line)
            if(regexMatch != None):
                rtt = float(regexMatch.group(1))
                allRTT.append(rtt)
            else:
                print(Utils.color.YELLOW + "WARNING: Could not parse ping results" + Utils.color.END)
                return None

    # Get results summary
    summaryRTTLine = pingResults.splitlines()[-1]
    regexMatch = re.search(summaryRTTPattern, summaryRTTLine)
    if(regexMatch != None):
        minRTT = float(regexMatch.group(1))
        avgRTT = float(regexMatch.group(2))
        maxRTT = float(regexMatch.group(3))
        mdevRTT = float(regexMatch.group(4))
        return PingResultInfo(minRTT=minRTT, avgRTT=avgRTT, maxRTT=maxRTT, mdevRTT=mdevRTT, allRTT=allRTT)
    else:
        print(Utils.color.YELLOW + "WARNING: Could not parse ping results" + Utils.color.END)
        return None


def parseAll(hosts : list[Host], resultsDirectory : str, skipFirstPing=False) -> PingResultInfo:
    # Parse all ping results
    allPingRes = []
    for srcHost in hosts:
        for dstHost in hosts:
            if(srcHost == dstHost):
                continue

            resultsFilename = resultsDirectory + "/pingresult_" + srcHost.name + "_" + dstHost.name + ".txt"
            pingResult = parse(resultsFilename)
            if(pingResult == None):
                print(Utils.color.YELLOW + "WARNING: Could not parse all ping results because the result of "
                      + resultsFilename + " could not be parsed" + Utils.color.END)
                return None
            allPingRes.append(pingResult)
    
    # Get average RTT of every ping result's allRTT
    allAvgRTT = []
    pingCount = min([len(pingRes.allRTT) for pingRes in allPingRes])

    for i in range(1 if skipFirstPing else 0, pingCount):
        values = []
        for pingRes in allPingRes:
            values.append(float(pingRes.allRTT[i]))
        avgValue = round(statistics.mean(values), 3)
        allAvgRTT.append(avgValue)


    minRTT = min([pingRes.minRTT for pingRes in allPingRes]) 
    minRTT = round(minRTT, 3)

    maxRTT = max([pingRes.maxRTT for pingRes in allPingRes]) 
    maxRTT = round(maxRTT, 3)

    avgRTT = round(statistics.mean(allAvgRTT), 3)
    stdRTT = round(statistics.stdev(allAvgRTT), 3)

    return PingResultInfo(minRTT=minRTT, maxRTT=maxRTT, avgRTT=avgRTT, mdevRTT=stdRTT, allRTT=allAvgRTT)

def plotResults(pingResultInfo : PingResultInfo, title : str, outDirectory : str, fileName : str):
    plt.figure()
    plt.xlabel("seq")
    plt.ylabel("RTT (ms)")
    plt.title(title)

    plt.plot(pingResultInfo.allRTT, 'b-')
    plt.axhline(y=pingResultInfo.avgRTT, color='k', linestyle='--')

    text = "Minimum: " + str(pingResultInfo.minRTT) + " ms\n"
    text += "Maximum: " + str(pingResultInfo.maxRTT) + " ms\n"
    text += "Average: " + str(pingResultInfo.avgRTT) + " ms\n"
    text += "Standard Deviation: " + str(pingResultInfo.mdevRTT) + " ms\n"
    plt.annotate(text,
            xy = (1, -0.2),
            xycoords='axes fraction',
            ha='center',
            va="center",
            fontsize=10)
    plt.tight_layout()

    if not os.path.exists(outDirectory):
        os.makedirs(outDirectory)
    
    fileName = "/" + fileName
    plt.savefig(outDirectory + fileName + ".png")
    print(Utils.color.GREEN + "Done! Results have been plotted in " + outDirectory + fileName + ".png" + Utils.color.END)

    plt.close()


def compare(pingResultInfo1 : PingResultInfo, pingResultInfo2 : PingResultInfo, title : str, outDirectory : str, fileName : str):
    plt.figure()
    plt.xlabel("seq")
    plt.ylabel("RTT (ms)")
    plt.title(title)

    plt.plot(pingResultInfo1.allRTT, 'b-')
    plt.plot(pingResultInfo2.allRTT, 'g-')
    

    text = "(Results 1)\n"
    text += "Minimum: " + str(pingResultInfo1.minRTT) + " ms\n"
    text += "Maximum: " + str(pingResultInfo1.maxRTT) + " ms\n"
    text += "Average: " + str(pingResultInfo1.avgRTT) + " ms\n"
    text += "Standard Deviation: " + str(pingResultInfo1.mdevRTT) + " ms\n"
    plt.annotate(text,
            # Blue color
            color=(0.0, 0.0, 0.5),
            xy = (0, -0.3),
            xycoords='axes fraction',
            ha='center',
            va="center",
            fontsize=10)

    text = "(Results 2)\n"
    text += "Minimum: " + str(pingResultInfo2.minRTT) + " ms\n"
    text += "Maximum: " + str(pingResultInfo2.maxRTT) + " ms\n"
    text += "Average: " + str(pingResultInfo2.avgRTT) + " ms\n"
    text += "Standard Deviation: " + str(pingResultInfo2.mdevRTT) + " ms\n"
    plt.annotate(text,
            # Green color
            color=(0.0, 0.5, 0.0),
            xy = (1, -0.3),
            xycoords='axes fraction',
            ha='center',
            va="center",
            fontsize=10)

    plt.tight_layout()

    if not os.path.exists(outDirectory):
        os.makedirs(outDirectory)
    
    fileName = "/" + fileName
    plt.savefig(outDirectory + fileName + ".png")
    print(Utils.color.GREEN + "Done! Results have been plotted in " + outDirectory + fileName + ".png" + Utils.color.END)

    plt.close()

