"""
Introduccion a la API de Mininet

Script sencillo que define la topologia minima de Mininet y ejecuta una prueba de ping e iperf.
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI

net = Mininet(waitConnected=True)

# Topology definition
h1 = net.addHost("h1")
h2 = net.addHost("h2")

net.addSwitch("s1")

net.addLink(h1, "s1")
net.addLink(h2, "s1")

net.addController("c0")

net.start()
CLI(net)

# Ping
h1.cmd("ping -c 4 " + h1.IP() + " > pingResult.txt")

# Iperf
h2.cmd("iperf -s &")

print(h1.cmd("iperf -c " + h2.IP()))
h1.cmd("iperf -c " + h2.IP() + " > iperfResult.txt")

net.stop()
