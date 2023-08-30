from dataclasses import dataclass

import sys
import os
import Utils

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


trafficMatricesDirectory = "tests/Matrices de tráfico - Test/"
configurationsDirectory = "tests/Configuraciones/"
routingDirectory = "tests/Encaminamiento/"
logisticRegressionMappingFile = "tests/RegresionLogistica_Test_200.csv"
Directory200 = "tests/200/"
capacityMatrixFile = "tests/abileneCapMatrix.csv"

resultsSubdirectory = "pruebas_"

@dataclass
class ParametrosPruebaDefinitiva:
    selectedTrafficMatrix : str
    selectedConfigurationMatrix : str
    selectedRoutingMatrix : str
    selectedConfiguration200Matrix : str
    selectedRouting200Matrix : str

def checkFileExists(fichero):
    if(not os.path.isfile(fichero)):
        print(Utils.color.RED + "No se ha encontrado", fichero, Utils.color.END)
        exit(-1)

def defineParameters(t : int) -> ParametrosPruebaDefinitiva:
    selectedTrafficMatrix = trafficMatricesDirectory + "matriz_" + str(t) + ".csv"
    checkFileExists(selectedTrafficMatrix)

    trafficMatrix = open(selectedTrafficMatrix, "r+")
    n = int(float(trafficMatrix.read().splitlines()[-1].split(',')[0]))
    trafficMatrix.close() 
    print(Utils.color.BLUE + "La matriz de trafico requiere la configuracion y encaminamiento", n, Utils.color.END)

    selectedConfigurationMatrix = configurationsDirectory + "configuracion_" + str(n) + ".csv"
    matrizEncaminamientoSeleccionado = routingDirectory + "encaminamiento_" + str(n) + ".csv"

    checkFileExists(selectedConfigurationMatrix)
    checkFileExists(matrizEncaminamientoSeleccionado)

    print(Utils.color.BLUE + "Se han encontrado los ficheros de configuracion y encaminamiento", n, Utils.color.END)

    regresionLogistica_Test_200 = open(logisticRegressionMappingFile, "r+")
    i = int(float(regresionLogistica_Test_200.read().splitlines()[t]))
    regresionLogistica_Test_200.close()

    print(Utils.color.BLUE + "La configuración y encaminamiento del algoritmo ML con la que compararla es", i, Utils.color.END)

    selectedConfiguration200Matrix = Directory200 + "configuracion_" + str(i) + ".csv"
    matrizEncaminamiento200Seleccionado = Directory200 + "encaminamiento_" + str(i) + ".csv"

    checkFileExists(selectedConfiguration200Matrix)
    checkFileExists(matrizEncaminamiento200Seleccionado)

    print(Utils.color.BLUE + "Se han encontrado los ficheros de configuracion y encaminamiento del algoritmo ML", i, Utils.color.END)
    checkFileExists(selectedTrafficMatrix)

    return ParametrosPruebaDefinitiva(selectedTrafficMatrix=selectedTrafficMatrix, 
                                      selectedConfigurationMatrix=selectedConfigurationMatrix,
                                      selectedRoutingMatrix=matrizEncaminamientoSeleccionado,
                                      selectedConfiguration200Matrix=selectedConfiguration200Matrix,
                                      selectedRouting200Matrix=matrizEncaminamiento200Seleccionado)

def executeTests(params : ParametrosPruebaDefinitiva, t : int):
    topologyInfo = NetworkTopologyDefinition.defineTopology(capacityMatrixFilename=capacityMatrixFile, configurationFilename=params.selectedConfigurationMatrix)
    routingInfo = NetworkRouting.parseRoutingInfo(topologyInfo=topologyInfo, routingMatrixFilename=params.selectedRoutingMatrix)
    trafficInfo = TrafficMatrixParser.parseTrafficInfo(filename=params.selectedTrafficMatrix, topologyInfo=topologyInfo)

    pìngResults = None
    iperfResults = None

    try:
        topologyInfo.net.start()
        EvaluationController.installFlowTables(topologyInfo=topologyInfo, routingInfo=routingInfo, outDirectory="pruebas/flows")
        topologyInfo.net.pingAll() # Rellena las tablas ARP para los tests.
        PingEvaluation.pingAll(hosts=topologyInfo.hosts, pingForSeconds=30, outDirectory=resultsSubdirectory+"/resultados/pings", asynchronousTest=True)
        IperfEvaluation.iperfAll(hosts=topologyInfo.hosts, trafficInfo=trafficInfo, outDirectory=resultsSubdirectory+"/resultados/iperfs", asynchronousTest=True)

        pìngResults = PingResultParser.parseAll(hosts=topologyInfo.hosts, resultsDirectory=resultsSubdirectory+"/resultados/pings", skipFirstPing=False)
        iperfResults = IperfResultParser.parseAll(hosts=topologyInfo.hosts, resultsDirectory=resultsSubdirectory+"/resultados/iperfs")

        if(pìngResults == None or iperfResults == None):
            raise Exception("No se han podido parsear los resultados")
        
        configName = params.selectedConfigurationMatrix
        configName = configName.split("_")[1]
        configName = configName.split(".")[0]

        iperfName = params.selectedTrafficMatrix
        iperfName = iperfName.split("_")[1]
        iperfName = iperfName.split(".")[0]

        PingResultParser.plotResults(pingResultInfo=pìngResults, title="Pings sobre Abilene con configuración=" + configName, outDirectory=resultsSubdirectory+"/resultados/graficas/", fileName="ping_no_ml")
        IperfResultParser.plotResults(iperfResultInfo=iperfResults, title="Iperf sobre Abilene con configuración=" + iperfName, outDirectory=resultsSubdirectory+"/resultados/graficas/", fileName="iperf_no_ml")
        topologyInfo.net.stop()

        print(Utils.color.GREEN + "Pruebas iniciales finalizadas, comenzando las siguientes pruebas..." + Utils.color.END)

        topologyInfo = NetworkTopologyDefinition.defineTopology(capacityMatrixFilename=capacityMatrixFile, configurationFilename=params.selectedConfiguration200Matrix)
        routingInfo = NetworkRouting.parseRoutingInfo(topologyInfo=topologyInfo, routingMatrixFilename=params.selectedRouting200Matrix)
        trafficInfo = TrafficMatrixParser.parseTrafficInfo(filename=params.selectedTrafficMatrix, topologyInfo=topologyInfo)

        topologyInfo.net.start()
        EvaluationController.installFlowTables(topologyInfo=topologyInfo, routingInfo=routingInfo, outDirectory="pruebas/flows200")
        topologyInfo.net.pingAll() # Rellena las tablas ARP para los tests.
        PingEvaluation.pingAll(hosts=topologyInfo.hosts, pingForSeconds=30, outDirectory=resultsSubdirectory+"/resultados200/pings", asynchronousTest=True)
        IperfEvaluation.iperfAll(hosts=topologyInfo.hosts, trafficInfo=trafficInfo, outDirectory=resultsSubdirectory+"/resultados200/iperfs", asynchronousTest=True)

        resultadosPing200 = PingResultParser.parseAll(hosts=topologyInfo.hosts, resultsDirectory=resultsSubdirectory+"/resultados200/pings", skipFirstPing=False)
        resultadosIperf200 = IperfResultParser.parseAll(hosts=topologyInfo.hosts, resultsDirectory=resultsSubdirectory+"/resultados200/iperfs")

        if(pìngResults == None or iperfResults == None):
            raise Exception("No se han podido parsear los resultados")
        
        configName = params.selectedConfigurationMatrix
        configName = configName.split("_")[1]
        configName = configName.split(".")[0]

        iperfName = params.selectedTrafficMatrix
        iperfName = iperfName.split("_")[1]
        iperfName = iperfName.split(".")[0]
        PingResultParser.plotResults(pingResultInfo=pìngResults, title="Pings sobre Abilene con configuración=" + configName, outDirectory=resultsSubdirectory+"/resultados200/graficas/", fileName="ping_ml")
        IperfResultParser.plotResults(iperfResultInfo=iperfResults, title="Iperf sobre Abilene con configuración=" + iperfName, outDirectory=resultsSubdirectory+"/resultados200/graficas/", fileName="iperf_ml")
        
        
        print(Utils.color.GREEN + "Todas las pruebas finalizadas. Generando gráficas de comparación..." + Utils.color.END)
        PingResultParser.compare(pingResultInfo1=pìngResults, pingResultInfo2=resultadosPing200, title="Ping durante 30 sobre Abilene (12 nodos)", outDirectory=resultsSubdirectory, fileName="ping")
        IperfResultParser.compare(iperfResultInfo1=iperfResults, iperfResultInfo2=resultadosIperf200, title="Iperf sobre Abilene (12 nodos) usando la matriz de tráfico " + str(t), outDirectory=resultsSubdirectory, fileName="iperf")
        
        topologyInfo.net.stop()
    except:
        print(Utils.color.RED + "Ha ocurrido una excepcion. Deteniendo la simulacion..." + Utils.color.END)
        topologyInfo.net.stop()

    

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        print(Utils.color.RED + "Especifica el número de la matriz de tráfico" + Utils.color.END)
        exit(-1)

    t = sys.argv[1]
    resultsSubdirectory += (t + "/")
    params = defineParameters(int(t))
    executeTests(params, t)

   





