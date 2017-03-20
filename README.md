# Firmware chooser

## Prerequisites:

- *python 3*
- *pip*

## Installation:
- clone repo
- change owner of the folder to *httpd* user
- change to the *firmwarechooser* directory
- cp *settings.py.example* to *settings.py*
- if data dir is external change *datapath* in settings.py to the location
- if data dir is internal create *data* dir
- install globally via pip: *uwsgi*
- cp *fwchooser.ini.example* to *fwchooser.ini*
- change *chdir* in *fwchooser.ini* to the correct path
- copy *fwchooser.service* to */etc/systemd/system*
