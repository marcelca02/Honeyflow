import pyshark as psh

SSH_PORT = 22
INTERFACE = 'wlp2s0'

def ssh_brute_force_detection(timeout):
    print("Starting packet capture\n")

    cap = psh.LiveCapture(interface=INTERFACE, bpf_filter=f"port {SSH_PORT}")
    cap.sniff(timeout=timeout)
    packets = [pkt for pkt in cap._packets]
    cap.close()
        
    failed_attempts = {}

    print("Starting packet analysis: \n")
    for pkt in packets:
        try:
            if hasattr(pkt, 'ssh'):
                print("SSH packet detected")
                src_ip = pkt.ip.src
                if pkt.ssh.response_code == 'Failure':
                    if src_ip in failed_attempts:
                        failed_attempts[src_ip] += 1
                    else:
                        failed_attempts[src_ip] = 1
                        failed_attempts[src_ip]['time'] = pkt.sniff_time.timestamp()

                        # If the number of failed attempts exceeds 5 within a 1-minute window
                        if failed_attempts[src_ip] >= 5 and pkt.sniff_time.timestamp() - failed_attempts[src_ip]['time'] <= 60:
                            print(f"SSH brute force detected from {src_ip}")

        except AttributeError:
            pass    # Ignore packets that are not SSH

ssh_brute_force_detection(10)


