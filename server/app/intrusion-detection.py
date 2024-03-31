import pyshark as psh
from config import INTERFACE, SSH_PORT, CONTAINER_IP 


def ssh_brute_force_detection(timeout):
    print("Starting packet capture\n")

    cap = psh.LiveCapture(interface=INTERFACE, bpf_filter=f"port {SSH_PORT}")
    cap.sniff(timeout=timeout)
    packets = [pkt for pkt in cap._packets]
    cap.close()
        
    attempts = {}

    print("Starting packet analysis: \n")
    for pkt in packets:
        try:
            if hasattr(pkt, 'ssh'):
                src_ip = pkt.ip.src
                print(f"SSH packet from {src_ip}")
                if src_ip in attempts and src_ip != CONTAINER_IP:
                    attempts[src_ip]['attempts'] += 1
                    # If the number of failed attempts exceeds 5 within a 1-minute window
                    if attempts[src_ip]['attempts'] >= 5 and pkt.sniff_time.timestamp() - attempts[src_ip]['time'] <= 60:
                        print(f"SSH brute force detected from {src_ip}")
                        break
                else:
                    attempts[src_ip] = {'attempts': 1, 'time': pkt.sniff_time.timestamp()}

        except AttributeError:
            pass    # Ignore packets that are not SSH

ssh_brute_force_detection(20)



