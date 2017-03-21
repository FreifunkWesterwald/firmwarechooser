#!/usr/bin/env python3

import os
import os.path
import datetime
import mimetypes
import settings

mimetypes.init()

hf = open('templates/html.template', 'r')
html = hf.read()
hf.close()

nf = open('templates/notfound.template', 'r')
notfound = nf.read()
nf.close()

def human_readable(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    if isinstance(size, int):
        ret = "%d %s"%(size,suffixes[suffixIndex])
    else:
        ret = "%.*f %s"%(precision,size,suffixes[suffixIndex])
    return ret

def ls(rootdir):
    # First entry (Back entry)
    index = '<tr><td class="n"><a href="..">..</a>/</td><td class="s">-</td><td class="d">'
    dt = datetime.datetime.fromtimestamp(os.path.getmtime(rootdir))
    index += dt.strftime("%a %b %d %H:%M:%S") + "</td></tr>"
    # Iterate over directory
    with os.scandir(rootdir) as it:
        for entry in it:
            # If filename starts with '.', e.g. .gitignore, ignore entry
            if entry.is_file and entry.name.startswith('.'):
                continue
            # Gather name, size and modify date
            name = entry.name
            if entry.is_file():
                sz = human_readable(os.path.getsize(entry.path))
            else:
                sz = "-"
            dt = datetime.datetime.fromtimestamp(os.path.getmtime(entry.path))
            date = dt.strftime("%a %b %d %H:%M:%S")
            # Concat entry
            line = '\n<tr><td class="n"><a href="' + name + '">' + name + '</a>'
            if entry.is_dir():
                line += '/'
            line += '</td><td class="s">' + sz + '</td><td class="d">' + date + '</td></tr>'
            index += line
        it.close()
    return index

def filecontent(path):
    f = open(path, 'rb')
    content = f.read()
    f.close()
    return content

def resolve_mimetype(path):
    extension = os.path.splitext(path)[1]
    if extension in mimetypes.types_map:
        mime_type = mimetypes.types_map[extension]
    elif extension in settings.mimetypes:
        mime_type = settings.mimetypes[extension]
    else:
        mime_type = 'application/octet-stream'
    return mime_type

# function called from uwsgi
def application(environ, start_response):

    # Get REQUEST_URI from environment
    req_uri = environ['REQUEST_URI']
    path = settings.datapath + req_uri
    print(req_uri)

    # Set status content_type to default values
    status = '200 OK'
    content_type = 'text/html'
    additional_header = []

    if os.path.isdir(path):
        # Send 301 to url ending with '/', because relative links
        if not req_uri.endswith('/'):
            status = '301 Moved Permanently'
            additional_header.append(('Location', req_uri + '/'))
            response_body = b""
        else:
            listening = ls(path)
            response_body = (html % {
                'path': req_uri or '/',
                'table': listening
            }).encode('utf-8')
    elif os.path.isfile(path):
        content_type = resolve_mimetype(path)
        response_body = filecontent(path)
    else:
        status = '404 Not Found'
        response_body = (notfound % {
            'path': req_uri
        }).encode('utf-8')

    # Set header
    response_header = [
        ('Content-Type', content_type),
        ('Content-Length', str(len(response_body)))
    ]
    for header in additional_header:
        response_header.append(header)

    start_response(status, response_header)
    return [response_body]
