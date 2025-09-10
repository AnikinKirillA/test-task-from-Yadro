FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       apache2 openssh-server curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ARG APACHE_INDEX_CONTENT="Hello from Apache!"
RUN mkdir -p /var/www/html
RUN echo "${APACHE_INDEX_CONTENT}" > /var/www/html/index.html

ARG ROOT_PASSWORD=toor
RUN echo "root:${ROOT_PASSWORD}" | chpasswd
RUN mkdir /var/run/sshd
RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config || true
RUN sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config || true

EXPOSE 22 80

CMD ["/bin/sh", "-c", "/usr/sbin/sshd && /usr/sbin/apache2ctl -D FOREGROUND"]
