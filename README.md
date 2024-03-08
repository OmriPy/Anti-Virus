# Anti-Virus
*Explanation of the project*

## Prerequisites
*Prerequisites*

## LAN Configuration
Our goal here is to connect all of the Virtual Machines to a new LAN that will be private to them. Which means that the VMs' network won't even be accessible to the main Operating System of the Laptop, just like your home's Wi-Fi isn't accessible to the White House (theoretically).

### Creating the Private Network for each PC
For every VM that is Not the Router, we change the Network Adapter settings to Private to my Mac.

Right click the VM -> `Settings` -> `Network Adapter` -> select `Private to my Mac`

![image](https://github.com/OmriPy/Virus/assets/110406612/00e376b7-ab58-4499-affb-288932443d4f)

![image](https://github.com/OmriPy/Virus/assets/110406612/371e05e8-9a19-4796-a80c-7afd3e511fc1)

![image](https://github.com/OmriPy/Virus/assets/110406612/ee397530-80e6-4330-ac79-9c576922a0ad)

### Creating the Private Network for the Router
In order for the Router VM to actually route packets, it needs to be connected to two networks. One is our LAN for the VMs, and the second is the one that the main OS is connected to, which is your home's physical router in most cases.

This is exactly what we will do, we will add a new Network Adapter to our Router VM.

Right click the Router VM -> `Settings` -> `Add Device...` (top right corner) -> `Network Adapter` -> `Add...` -> select `Private to my Mac`

![image](https://github.com/OmriPy/Virus/assets/110406612/f9c4afdb-03d4-4310-b924-9450ee07c659)

![image](https://github.com/OmriPy/Virus/assets/110406612/88baca52-cc1f-4d7d-8812-69165f075585)

![image](https://github.com/OmriPy/Virus/assets/110406612/f21afec4-84d5-453e-ba98-26add5430597)

![image](https://github.com/OmriPy/Virus/assets/110406612/ce024544-f1d4-4b83-a34b-e4381c314fda)


Now, start the Router VM, open the `Terminal` and type:
```
ip a
```
or
```
ifconfig
```
If you see two interfaces, `eth0` and `eth1` (see below), it means that we successfully connected the Router to two networks.

![image](https://github.com/OmriPy/Virus/assets/110406612/e3b5b9ca-fbba-4c2e-934b-c41a3bffa64b)

### Routing
In order to enable IP forwarding, type the following commands on the Router machine:
```
sudo su
echo 1 > /proc/sys/net/ipv4/ip_forward
```
To make these changes persistent even after rebooting the system, run:
```
echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
sysctl -p
```
