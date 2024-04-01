import pyshark as psh
from config import INTERFACE, SSH_PORT, CONTAINER_IP 

def start_detection(machine_id, timeout):
    # TODO: machine_id based detection
    print("Starting packet capture\n")

    cap = psh.LiveCapture(interface=INTERFACE)
    cap.sniff(timeout=timeout)
    packets = [pkt for pkt in cap._packets]
    cap.close()
    return packets


def ssh_brute_force_detection(packets):
    attempts = {}

    print("Starting SSH brute force detection\n")
    for pkt in packets:
        try:
            if hasattr(pkt, 'ssh'):
                src_ip = pkt.ip.src
                print(f"SSH packet from {src_ip}")
                if src_ip in attempts and src_ip != CONTAINER_IP:
                    attempts[src_ip]['attempts'] += 1
                    # If the number of failed attempts exceeds 10 within a 1-minute window
                    if attempts[src_ip]['attempts'] >= 10 and pkt.sniff_time.timestamp() - attempts[src_ip]['time'] <= 30:
                        print(f"SSH brute force detected from {src_ip}")
                        break
                else:
                    attempts[src_ip] = {'attempts': 1, 'time': pkt.sniff_time.timestamp()}

        except AttributeError:
            pass    # Ignore packets that are not SSH

def port_scaning_detection(packets):
    open_ports = {}

    print("Starting port scanning detection\n")
    for pkt in packets:
        try:
            if hasattr(pkt, 'tcp'):
                src_ip = pkt.ip.src
                dst_port = pkt.tcp.dstport
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

    for src_ip, ports in open_ports.items():
        if len(ports) >= 20:  # Threshold for considering it as port scanning
            print(f"Port scanning detected from {src_ip} to ports {ports}")


# Test the detection functions
packets = start_detection(1, 10)
port_scaning_detection(packets)

