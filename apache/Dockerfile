FROM ubuntu:xenial

#
# we need to build a special image to include mod_md
#   see : https://github.com/icing/mod_md
#
RUN apt-get update && apt-get -y install software-properties-common
RUN LC_ALL=C.UTF-8 add-apt-repository ppa:ondrej/apache2 
RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-auth-openidc \
    apache2-dev build-essential autoconf make libtool libssl-dev libjansson-dev libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY mod_md-1.1.7.tar.gz /tmp/
RUN tar xvzf /tmp/mod_md-1.1.7.tar.gz 
RUN cd mod_md-1.1.7 && ./configure --with-apxs=/usr/bin/apxs
RUN cd mod_md-1.1.7 && make 
RUN cd mod_md-1.1.7 && make install 
    
COPY md.load /etc/apache2/mods-available/
COPY md.conf /etc/apache2/mods-available/
RUN a2enmod rewrite && a2enmod auth_openidc && a2enmod proxy && a2enmod proxy_http && a2enmod md

#
# for production it should be replaced by the https version
#
# COPY servicehub_https.conf /etc/apache2/sites-available/servicehub.conf
COPY servicehub_http.conf /etc/apache2/sites-available/servicehub.conf


RUN a2ensite servicehub && a2dissite 000-default


EXPOSE 80
RUN mkdir /var/lock/apache2 /var/run/apache2
CMD . /etc/apache2/envvars && apache2 -DFOREGROUND
