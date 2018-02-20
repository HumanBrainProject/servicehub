FROM ubuntu:xenial

RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-auth-openidc \
 && rm -rf /var/lib/apt/lists/*

COPY servicehub.conf /etc/apache2/sites-available/servicehub.conf
RUN a2enmod auth_openidc && a2enmod proxy && a2enmod proxy_http
RUN a2ensite servicehub && a2dissite 000-default

EXPOSE 80
RUN mkdir /var/lock/apache2 /var/run/apache2
CMD . /etc/apache2/envvars && apache2 -DFOREGROUND