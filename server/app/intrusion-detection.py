import pyshark as psh

SSH_PORT = 22

def ssh_brute_force_detection(pcap_file):
    cap = psh.FileCapture(pcap_file, display_filter='tcp.port == 22')

    failed_attempts = {}

    for pkt in cap:
        try:
            if pkt.ssh:
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

    cap.close()

ssh_brute_force_detection('../data/demo.pcap')


