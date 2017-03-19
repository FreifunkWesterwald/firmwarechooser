import os
import os.path
import datetime
import mimetypes

basepath = os.path.dirname(os.path.abspath(__file__)) + "/data"
mimetypes.init()

html_before = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Index of %(path)s</title>
    <link rel="author" href="https://twitter.com/thepaffy" title="thepaffy on Twitter" />
    <link rel="canonical" href="http://images.freifunk-westerwald.de/" />
</head>
<body>
<h1>Index of %(path)s</h1>
<hr>
<table>
<tr><th class="n">File Name</th><th class="s">File Size</th><th class="d">Date</th></tr>
"""

html_after = """
</table>
</body>
</html>
"""

notfound = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Not found</title>
    <link rel="author" href="https://twitter.com/thepaffy" title="thepaffy on Twitter" />
    <link rel="canonical" href="http://images.freifunk-westerwald.de/" />
</head>
<body>
<h1>Sorry, but the content you are looking for is not aviable!</h1>
<p>File or directory %(path)s not found.</p>
</body>
</html>
"""

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
                size = str(os.path.getsize(entry.path))
            else:
                size = "-"
            dt = datetime.datetime.fromtimestamp(os.path.getmtime(entry.path))
            date = dt.strftime("%a %b %d %H:%M:%S")
            # Concat entry
            line = '\n<tr><td class="n"><a href="' + name + '">' + name + '</a>'
            if entry.is_dir():
                line += '/'
            line += '</td><td class="s">' + size + '</td><td class="d">' + date + '</td></tr>'
            index += line
    return index

def filecontent(path):
    f = open(path, 'rb')
    content = f.read()
    f.close()
    return content

def resolve_mimetype(path):
    extension = os.path.splitext(path)[1]
    return mimetypes.types_map[extension]

def application(environ, start_response):

    # Get REQUEST_URI from environment
    req_uri = environ['REQUEST_URI']
    path = basepath + req_uri

    # Set status content_type to default values
    status = '200 OK'
    content_type = 'text/html'

    if os.path.isdir(path):
        response_body = (html_before % {
            'path': req_uri or '/'
        }).encode('utf-8')
        response_body += ls(path).encode('utf-8')
        response_body += html_after.encode('utf-8')
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

    start_response(status, response_header)
    return [response_body]
