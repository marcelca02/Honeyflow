FROM ubuntu:22.04

RUN apt update && apt install -y openssh-server sudo

# Script de instalación y configuración de cowrie
COPY cowrie-script.sh /tmp/cowrie-script.sh
RUN chmod +x /tmp/cowrie-script.sh
RUN /tmp/cowrie-script.sh

RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN useradd -m -s /bin/bash user 
RUN echo "user:password-user" | chpasswd && adduser user sudo

EXPOSE 2222

ENTRYPOINT service ssh start && bash

CMD [".", "/home/cowrie/cowrie/cowrie-env/bin/activate"]
