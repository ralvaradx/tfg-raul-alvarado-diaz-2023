# tfg-raul-alvarado-diaz-2023
Framework para la evaluación de algoritmos de Machine Learning para la mejora de la eficiencia en redes softwarizadas


El código de este TFG contiene los siguientes ficheros, divididos en:

## 1. Código del framework
### 1.1: EvaluationController.py
Módulo encargado de instalar las reglas de flujo en los switches de Mininet según la información de topología y enrutamiento pasada como entrada.

### 1.2: InfoDataclasses.py
Módulo que recoge todas las dataclasses utilizadas por el framework.

### 1.3: IperfEvaluation.py
Módulo encargado de ejecutar las pruebas iperf (síncronas o asíncronas) a partir de una matriz de tráfico pasada como entrada.

### 1.4: IperfResultParser.py
Módulo encargado de recuperar los resultados de las pruebas iperf y hacer una representación gráfica de éstos, así como comparar dos resultados iperf.

### 1.5: NetworkRouting.py
Módulo encargado de ejecutar el algoritmo de Dijkstra o leer una matriz de enrutamiento para construir la información sobre el enrutamiento que se utilizará en el framework.

### 1.6: NetworkTopologyDefinition.py
Módulo encargado de leer una matriz de capacidad y configuración para crear la red en Mininet donde se ejecutarán las pruebas.

### 1.7: PingEvaluation.py
Módulo encargado de ejecutar las pruebas ping (síncronas o asíncronas) durante un tiempo pasado como entrada.

### 1.8: PingResultParser.py
Módulo encargado de recuperar los resultados de las pruebas ping y hacer una representación gráfica de éstos, así como comparar dos resultados ping. 

### 1.9: TrafficMatrixParser.py
Módulo encargado de leer una matriz de tráfico y construir la información sobre el tráfico que se utilizará en el framework.

### 1.10: Utils.py
Módulo con funciones auxiliares (colorear salida del texto y mostrar una barra de progreso animada)

## 2. Código usuario del framework:
### 2.1: AbileneCompleta.py
Ejemplo que muestra cómo utilizar el framework para realizar pruebas ping e iperf.

### 2.2: AbilenePruebasDefinitivas.py 
Ejemplo más específico que muestra como utilizar el framework para, dada una matriz de tráfico, ejecutar dos pares de pruebas ping e iperf (asíncronas) y comparar ambos en una gráfica, además de crear las gráficas individuales.

### 2.3: AbileneReducida.py
Ejemeplo que define manualmente una topología de 3 nodos y su enrutamiento, ejecutando pruebas ping sobre éste. Las llamadas para ejecutar las pruebas iperf están comentadas porque la función a la que se invoca no se corresponde con la de la versión final. La sección 5.2 de la memoria justifica esto.

### 2.4: Introduccion_API_Mininet
Ejemplo sencillo que muestra cómo definir la topología minimalista de Mininet usando su API de Python.
