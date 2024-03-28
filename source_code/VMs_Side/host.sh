#!/bin/bash
tcpserver=`which tcpserver`
dest_ip=0.0.0.0
port=51768
file=./vulnerable.py

printf 'Listening on %s:%s\nRunning %s\n\n' $dest_ip $port $file

$tcpserver -v $dest_ip $port $file
