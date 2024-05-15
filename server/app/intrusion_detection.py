import pyshark as psh
from datetime import datetime
from flask import json
from collections import defaultdict

ip = ''

def start_detection(interface,ip,timeout,event):
    while (1):
        if event.is_set():
            break

        print("Starting packet capture\n")
        cap = psh.LiveCapture(interface=interface)
        packets = []
        for pkt in cap.sniff_continuously(packet_count=500):
            packets.append(pkt)
            if event.is_set():
                print("Stopping packet capture\n")
                break

        print("Number of packets captured: ", len(packets))
        cap.close()

        ip = ip
        attempts = ssh_brute_force_detection(packets)
        open_ports = port_scaning_detection(packets)
        tcp_sources = dns_tunneling_detection(packets)
        suspicious_smtp = smtp_spam_detection(packets)  
        suspicious_http = http_attack_detection(packets)  

        # Save the results to a JSON file dated 
        file_path = 'results/' + ip + '_' + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + '.json'
        with open(file_path, "w") as file:
            json.dump({
                'SSH Brute Force': {
                    'Attempts': list(attempts.items())
                },
                'Port Scaning': {
                    'Open Ports': list(open_ports.items())
                },
                'Dns Tunneling': {
                    'Tcp Sources': list(tcp_sources.items())
                },
                'Smtp Spam': {
                    'Suspicious IPs': list(suspicious_smtp)
                },
                'Http Attacks': {
                    'Suspicious IPs': suspicious_http["suspicious_ips"],  
                    'Injected Commands': dict(suspicious_http["injected_commands"]),  
                    'Attempted Directories': dict(suspicious_http["attempted_directories"])  
                }
            }, file)

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
                if src_ip != ip:
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
                if src_ip != ip:
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

def smtp_spam_detection(packets):
    print("Starting SMTP attack detection (spam)\n")
    
    spam_threshold=10
    time_window=30

    message_counts = defaultdict(int)  # Contador de mensajes por IP
    first_message_times = {}  # Primer momento en que cada IP envía un mensaje
    
    suspicious_ips = [] 

    for pkt in packets:
        try:
            if hasattr(pkt, 'smtp'):
                src_ip = pkt.ip.src
                if src_ip not in first_message_times:
                    first_message_times[src_ip] = pkt.sniff_time.timestamp()

                message_counts[src_ip] += 1

                # Si el número de mensajes supera el umbral en el periodo de tiempo definido, es un posible spam
                if message_counts[src_ip] > spam_threshold and (pkt.sniff_time.timestamp() - first_message_times[src_ip]) < time_window:
                    suspicious_ips.append(src_ip)

        except AttributeError:
            pass
    
    # Remover duplicados y devolver solo las IPs sospechosas
    return list(set(suspicious_ips))

def http_attack_detection(packets):
    print("Starting HTTP attack detection\n")
    
    # Diccionario para almacenar información sobre IPs sospechosas, comandos y directorios
    suspicious_data = {
        "suspicious_ips": [],
        "injected_commands": defaultdict(list),
        "attempted_directories": defaultdict(list)
    }

    for pkt in packets:
        try:
            if hasattr(pkt, 'http'):
                src_ip = pkt.ip.src

                # Verificar posibles intentos de inyección de comandos
                if 'cmd=' in pkt.http.query or 'exec=' in pkt.http.query or 'bash' in pkt.http.file_name or 'bash' in pkt.http.file_name:
                    suspicious_data["suspicious_ips"].append(src_ip)
                    suspicious_data["injected_commands"][src_ip].append(pkt.http.query)

                # Verificar intentos de descubrimiento de directorios
                if 'dir=' in pkt.http.query or 'folder=' in pkt.http.query or '/' in pkt.http.request_uri:
                    suspicious_data["suspicious_ips"].append(src_ip)
                    suspicious_data["attempted_directories"][src_ip].append(pkt.http.request_uri)

        except AttributeError:
            pass

    # Eliminar duplicados de las IPs sospechosas
    suspicious_data["suspicious_ips"] = list(set(suspicious_data["suspicious_ips"]))

    return suspicious_data

