# This is the file that when executed, the router virtual machine becomes a router.
# Located at /home/kali/VirusProject

iptables=`which iptables`
LAN='eth1'
WAN='eth0'

# Filter existing rules
$iptables -F
$iptables -t nat -F

# NAT
$iptables -t nat -A POSTROUTING -o $WAN -j MASQUERADE

# Forward packets
$iptables -A FORWARD -i $LAN -o $WAN -j ACCEPT

# Accept incoming packets from WAN
$iptables -A FORWARD -i $WAN -o $LAN -m state --state RELATED,ESTABLISHED -j ACCEPT
