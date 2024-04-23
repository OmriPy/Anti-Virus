# Anti-Virus
*Explanation of the project*

## Prerequisites
*Prerequisites*

## LAN Configuration
Our goal here is to connect all of the Virtual Machines to a new LAN that will be private to them. Which means that the VMs' network won't even be accessible to the main Operating System of the Laptop, just like your home's Wi-Fi isn't accessible to the White House (theoretically).

### Creating the Private Network for each Client
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


### Making a Kali Linux Virtual Machine become a router
#### Routing settings
In order to enable IP forwarding, type the following commands on the Router machine:
```
sudo su
echo 1 > /proc/sys/net/ipv4/ip_forward
```
To make these changes consistent after rebooting, run:
```
echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
sysctl -p
```
#### NAT and routing configuration
In order for this VM to actually route packets to the WAN (Wide Area Network), recieve packets from it, and enable the NAT process, we need to use `ip-tables`.

Make sure you're at the root directory of this project, create `route.sh` and write this in the file:
```
# This is the file that when executed, the router virtual machine becomes a router.

iptables=`which iptables`
LAN='eth1'
WAN='eth0'

# Filter existing rules
$iptables -F
$iptables -t nat -F

# NAT
$iptables -t nat -A POSTROUTING -o $WAN -j MASQUERADE

# Forward packets from LAN to WAN
$iptables -A FORWARD -i $LAN -o $WAN -j ACCEPT

# Accept incoming packets from WAN to LAN
$iptables -A FORWARD -i $WAN -o $LAN -m state --state RELATED,ESTABLISHED -j ACCEPT
```

Now, we need to make sure this file gets executed whenever the machine is booted.
In order to do that, we need to use a Service. The path for services in linux distributions is `/etc/systemd/system` or `/lib/systemd/system` (depends on the distro). `cd` to that directory, create `route.service` and write the following:
```
[Unit]
Description=Making this Linux VM a router

[Service]
ExecStart=/bin/bash <the project's root directory>/route.sh

[Install]
WantedBy=multi-user.target
```
Make sure you wrote the root directory where needed.

The file we created is the service which is going to run the script `route.sh` every time the system boots. Now we need to make it actually run the script whenever the system boots:
```
sudo su
systemctl enable route
```
Everything is theoretically done, now we need to make sure the service is working. We can do that by manually executing the service (still inside `root`):
```
systemctl start route
systemctl status route
```
If you see `status=0/SUCCESS` it means that the service worked:

![image](https://github.com/OmriPy/Anti-Virus/assets/110406612/5009b4cd-60ab-45f2-ab2a-243b6b589597)

Congrats! You made this Virtual Machine a router.

### Connecting a Kali Linux Virtual Machine to a router
Default Gateway - IP address of a computer's router

Now our router is working, but no other machine can use it as a real router, yet.
In order to set the machine's default gateway to our router's IP, we can use Services again.

`cd` to this project's root directory, create `set_default_gateway.sh` and write:
```
sudo ip route add default via <Router's IP> dev <the LAN's interface, usually eth0>
```
When this script runs, the default gateway is manually changed to our router. Now, just as before with our router, we need to make this script run automatically
whenever the system is starting.

`cd` to your distro's default path of services (as mentioned before: `/etc/systemd/system` / `/lib/systemd/system`), create `automatic_set_defualt_gateway.service` and write:
```
[Unit]
Description=Setting default gatway to router

[Service]
ExecStart=/bin/bash <the project's root directory>/set_default_gateway.sh

[Install]
WantedBy=multi-user.target
```

run the following to automatically execute the service:
```
sudo su
systemctl enable automatic_set_defualt_gateway
```

and manually check if the service is working:
```
systemctl start automatic_set_defualt_gateway
systemctl status automatic_set_defualt_gateway
```

if you see `status=0/SUCCESS` it means the service is working properly.

Now repeat this process for every VM you would like to connect to the router VM.

### DNS Server
I created a DNS server in my router this way:

1. Installed dnsmasq:
```
sudo apt update
sudo apt install dnsmasq
```

2. Added this to the `/etc/dnsmasq.conf` file:

```
# Specify DNS forwarders
server=172.20.10.1

# Specify DNS domain
domain=antiVirusProject.local

# Set DNS resolution for local domain
address=/antiVirusProject.local/172.16.175.131
```

3. Restarted dnsmasq service:

```
sudo systemctl restart dnsmasq
```

4. In each client VM I edited the /etc/resolv.conf file:

```
nameserver 172.16.175.131
```

### New Default Gateway way
In the client kali machines, you set the default gateway by adding:

```
# Define eth0 interface
auto eth0
iface eth0 inet static
    address 172.16.175.130
    netmask 255.255.255.0
    gateway 172.16.175.131
```

to the `/etc/network/interfaces` file
