FROM ubuntu:xenial

RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-auth-openidc \
 && rm -rf /var/lib/apt/lists/*

# enable needed modules
RUN a2enmod auth_openidc && a2enmod ssl && a2enmod rewrite && a2enmod proxy && a2enmod proxy_http && a2enmod proxy_wstunnel
# disable default virtual host
RUN a2dissite 000-default

# trick to send logs to stderr and stdout
# see : https://serverfault.com/questions/711168/writing-apache2-logs-to-stdout-stderr
#
RUN ln -sf /proc/self/fd/1 /var/log/apache2/other_vhosts_access.log && \
    ln -sf /proc/self/fd/2 /var/log/apache2/error.log

# for development you may change this to unprivileged port (for example 8080 and 8443)
EXPOSE 80
EXPOSE 443
RUN mkdir /var/lock/apache2 /var/run/apache2
CMD . /etc/apache2/envvars && apache2 -DFOREGROUND
