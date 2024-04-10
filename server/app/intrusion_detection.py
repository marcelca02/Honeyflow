import pyshark as psh
from app.config import INTERFACE, CONTAINER_IP 
from flask import json


def start_detection(machine_id, timeout):
    # TODO: machine_id based detection
    print("Starting packet capture\n")

    cap = psh.LiveCapture(interface=INTERFACE)
    cap.sniff(timeout=timeout)
    packets = [pkt for pkt in cap._packets]
    cap.close()

    attempts = ssh_brute_force_detection(packets)
    open_ports = port_scaning_detection(packets)
    tcp_sources = dns_tunneling_detection(packets)
    # TODO: Add more detection methods

    return json.dumps({
        'ssh_brute_force': {
            'attempts': list(attempts.items())
        },
        'port_scaning': {
            'open_ports': list(open_ports.items())
        },
        'dns_tunneling': {
            'tcp_sources': list(tcp_sources.items())
        }
    })

def ssh_brute_force_detection(packets):
    attempts = {}
    time = {}
    attempts_suspicious_ips = {}

    print("Starting SSH brute force detection\n")
    for pkt in packets:
        try:
            if hasattr(pkt, 'ssh'):
                src_ip = pkt.ip.src
                print(f"SSH packet from {src_ip}")
                if src_ip != CONTAINER_IP:
                    if src_ip in attempts:
                        attempts[src_ip] += 1
                    else:
                        attempts[src_ip] = 1
                        time[src_ip] = pkt.sniff_time.timestamp()

                    if attempts[src_ip] > 10 and pkt.sniff_time.timestamp() - time[src_ip] < 30:
                        attempts_suspicious_ips[src_ip] = attempts[src_ip]


        except AttributeError:
            pass    # Ignore packets that are not SSH


    return attempts_suspicious_ips

    

def port_scaning_detection(packets):

    open_ports = {}


    print("Starting port scanning detection\n")

    for pkt in packets:

        try:

            if hasattr(pkt, 'tcp'):

                src_ip = pkt.ip.src

                dst_port = pkt.tcp.dstport

                if src_ip != CONTAINER_IP:

                    print(f"TCP packet from {src_ip} to port {dst_port}")

                    if pkt.tcp.flags_syn == '1' and pkt.tcp.flags_ack == '0':

                        # SYN packet (potential start of TCP handshake)

                        if src_ip in open_ports:

                            open_ports[src_ip].add(dst_port)

                        else:

                            open_ports[src_ip] = {dst_port}


                    elif pkt.tcp.flags_rst == '1':

                        # RST packet (indicating closed port)

                        if src_ip in open_ports and dst_port in open_ports[src_ip]:

                            open_ports[src_ip].remove(dst_port)


        except AttributeError:

            pass


    # Create a copy of the open_ports dictionary to avoid modifying it during iteration

    open_ports_copy = dict(open_ports)

    for src_ip, ports in open_ports_copy.items():

        if len(ports) < 20:  # Threshold for considering it as port scanning

            print(f"Port scanning detected from {src_ip} to ports {ports}")

            open_ports.pop(src_ip)

        open_ports[src_ip] = list(ports)


    return open_ports

def dns_tunneling_detection(packets):
    print("Starting DNS tunnel detection\n")

    suspicious_ips = {}
    suspicious_traffic_sources = {}
    print("Starting DNS tunnel analysis")
    for pkt in packets:
        try:
            if hasattr(pkt, 'dns'):
                dns_pkt = pkt.dns
                src_ip = pkt.ip.src

                # Anomaly Detection
                if dns_pkt.flags & dns_pkt.flags.QR == 0 and dns_pkt.qdcount == 1:
                    query_name = dns_pkt.qd.qname

                    # Payload Analysis
                    if dns_pkt.edns:
                        payload_size = dns_pkt.edns.udp_payload_size
                        if payload_size > 512:  # Suspiciously large payload
                            suspicious_traffic_sources[src_ip] += 1
                    
                    # Query Name Analysis
                    elif len(query_name) > 50:  # Unusually large query name
                        suspicious_traffic_sources[src_ip] += 1

                    if suspicious_traffic_sources[src_ip] > 50:  # Excessive number of queries
                        print(f"Suspicious traffic detected from {src_ip}")
                        suspicious_ips[src_ip] = suspicious_traffic_sources[src_ip]

        except AttributeError:
            pass

    return suspicious_ips 

def tcp_session_hijaking_detection(packets):
    print("Starting TCP session hijacking detection\n")

    suspicious_ips = []

    for pkt in packets:
        try:
            if hasattr(pkt, 'tcp'):
                src_ip = pkt.ip.src
                pkt_tcp = pkt.tcp
                
                # TODO: Improve the detection logic with more TCP flags and sequence number analysis
                if pkt_tcp.flags.fin == '1' and pkt_tcp.flags.ack == '1' and int(pkt_tcp.seq) > 0 and int(pkt_tcp.ack) > 0:
                    suspicious_ips.append(src_ip)
                
        except AttributeError:
            pass
    return suspicious_ips
