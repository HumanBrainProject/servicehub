
# TODO

## Apache and SSL certificates

The SSL certificates are managed by the mod_md module, but when the certificate change
you need to reload apache configuration

see : https://github.com/icing/mod_md/wiki

One solution can be to add a Crontab entry in the VM, and once per day
send a reload signal to Apache

see : https://stackoverflow.com/questions/34449511/how-to-make-changes-to-httpd-conf-of-apache-running-inside-docker-container-and

docker kill --signal="USR1" <yourcontainer_name>

