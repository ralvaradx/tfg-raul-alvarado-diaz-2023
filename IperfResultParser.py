import re
import statistics
from mininet.node import Host

import matplotlib.pyplot as plt
import os
import Utils

from InfoDataclasses import IperfResultInfo

def parse(filename : str) -> IperfResultInfo:
    bandwidthPattern = r"(\d+(?:\.\d+)?\s+)MBytes/sec"

    if not os.path.isfile(filename):
        print(Utils.color.YELLOW + "WARNING: Could not parse ping results: file", filename, "does not exist" + Utils.color.END)
        return None

    iperfResultFile = open(filename, "r+")
    iperfResult = iperfResultFile.read()
    iperfResultFile.close()

    allLines = iperfResult.splitlines()
    nLines = len(allLines)

    allBandwidthValues = []
    for lineIndex in range(nLines):
        line = allLines[lineIndex]
        if "MBytes/sec" in line:
            regexMatch = re.search(bandwidthPattern, line)
            if(regexMatch != None):
                bw = float(regexMatch.group(1))
                allBandwidthValues.append(bw)
            else:
                print(Utils.color.YELLOW + "WARNING: Could not parse iperf results" + Utils.color.END)
                return None

    if(len(allBandwidthValues) > 1):
        # Remove last value as it is a summary of the transmitted volume
        allBandwidthValues = allBandwidthValues[:-1]

    if(len(allBandwidthValues) >= 2):
        minBandwidth = min(allBandwidthValues)
        maxBandwidth = max(allBandwidthValues)
        avgBandwidth = statistics.mean(allBandwidthValues)
        mdevBandwidth = statistics.stdev(allBandwidthValues)
        return IperfResultInfo(minBandwidth=minBandwidth, maxBandwidth=maxBandwidth, avgBandwidth=avgBandwidth, mdevBandwidth=mdevBandwidth, allBandwidth=allBandwidthValues)
    else:
        return IperfResultInfo(minBandwidth=allBandwidthValues[0], maxBandwidth=allBandwidthValues[0], avgBandwidth=allBandwidthValues[0], mdevBandwidth=0, allBandwidth=allBandwidthValues)

def parseAll(hosts : list[Host], resultsDirectory : str) -> IperfResultInfo:
    # Parse all iperf results
    allIperfRes = []
    for srcHost in hosts:
        for dstHost in hosts:
            if(srcHost == dstHost):
                continue

            resultsFilename = resultsDirectory + "/iperfresult_" + srcHost.name + "_" + dstHost.name + ".txt"
            iperfResult = parse(resultsFilename)
            if(iperfResult == None):
                print(Utils.color.YELLOW + "WARNING: Could not parse all iperf results because the result of "
                      + resultsFilename + " could not be parsed" + Utils.color.END)
                return None
            allIperfRes.append(iperfResult)
    
    # Get average bandwidth of every interval
    allAvgBandwidth = []

    # IperfCount is the maximum length of all the vectors
    iperfCount = max([len(iperfResult.allBandwidth) for iperfResult in allIperfRes])
    for i in range(iperfCount):
        values = []
        for iperfResult in allIperfRes:
            vectorLength = len(iperfResult.allBandwidth)
            if(not i < vectorLength):
                continue
            value = float(iperfResult.allBandwidth[i])
            values.append(value)
        avgValue = round(statistics.mean(values), 3)
        allAvgBandwidth.append(avgValue)


    minBandwidth = min([iperfResult.minBandwidth for iperfResult in allIperfRes]) 
    minBandwidth = round(minBandwidth, 3)

    maxBandwidth = max([iperfResult.maxBandwidth for iperfResult in allIperfRes]) 
    maxBandwidth = round(maxBandwidth, 3)

    avgBandwidth = round(statistics.mean(allAvgBandwidth), 3)
    mdevBandwidth = round(statistics.stdev(allAvgBandwidth), 3)

    return IperfResultInfo(minBandwidth=minBandwidth, maxBandwidth=maxBandwidth, avgBandwidth=avgBandwidth, mdevBandwidth=mdevBandwidth, allBandwidth=allAvgBandwidth)

def plotResults(iperfResultInfo : IperfResultInfo, title : str, outDirectory : str, fileName : str):
    plt.figure()
    plt.xlabel("Time (s)")
    plt.ylabel("Bandwidth (MB/s)")
    plt.title(title)

    plt.plot(iperfResultInfo.allBandwidth, 'r-')

    plt.axhline(y=iperfResultInfo.avgBandwidth, color='k', linestyle='--')

    text = "Minimum: " + str(iperfResultInfo.minBandwidth) + " MB/s\n"
    text += "Maximum: " + str(iperfResultInfo.maxBandwidth) + " MB/s\n"
    text += "Average: " + str(iperfResultInfo.avgBandwidth) + " MB/s\n"
    text += "Standard Deviation: " + str(iperfResultInfo.mdevBandwidth) + " MB/s\n"
    text += "Time taken: " + str(len(iperfResultInfo.allBandwidth)) + " s"
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

def compare(iperfResultInfo1 : IperfResultInfo, iperfResultInfo2 : IperfResultInfo, title : str, outDirectory : str, fileName : str):
    plt.figure()
    plt.xlabel("Time (s)")
    plt.ylabel("Bandwidth (MB/s)")
    plt.title(title)

    plt.plot(iperfResultInfo1.allBandwidth, 'r-')
    plt.axvline(x=len(iperfResultInfo1.allBandwidth), color='r', linestyle='--')

    plt.plot(iperfResultInfo2.allBandwidth, 'm-')
    plt.axvline(x=len(iperfResultInfo2.allBandwidth), color='m', linestyle='--')

    text = "(Results 1)\n"
    text += "Minimum: " + str(iperfResultInfo1.minBandwidth) + " MB/s\n"
    text += "Maximum: " + str(iperfResultInfo1.maxBandwidth) + " MB/s\n"
    text += "Average: " + str(iperfResultInfo1.avgBandwidth) + " MB/s\n"
    text += "Standard Deviation: " + str(iperfResultInfo1.mdevBandwidth) + " MB/s\n"
    text += "Time taken: " + str(len(iperfResultInfo1.allBandwidth)) + " s"
    plt.annotate(text,
            color=(0.5, 0, 0),
            xy = (0, -0.3),
            xycoords='axes fraction',
            ha='center',
            va="center",
            fontsize=10)
    
    text = "(Results 2)\n"
    text += "Minimum: " + str(iperfResultInfo2.minBandwidth) + " MB/s\n"
    text += "Maximum: " + str(iperfResultInfo2.maxBandwidth) + " MB/s\n"
    text += "Average: " + str(iperfResultInfo2.avgBandwidth) + " MB/s\n"
    text += "Standard Deviation: " + str(iperfResultInfo2.mdevBandwidth) + " MB/s\n"
    text += "Time taken: " + str(len(iperfResultInfo2.allBandwidth)) + " s"
    plt.annotate(text,
            color=(0.5, 0, 0.5),
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