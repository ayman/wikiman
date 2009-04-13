#!env python
import getopt
import sys

options = getopt.getopt(sys.argv[1:],
                        'hu:iI',
                        ['help', 'head', 'user='])
include_header = 0
header_only = 0
username, password = None, ''
for option, value in options[0]:
    if option in ('-h', '--help'):
        print __doc__
        sys.exit(0)
    elif option == '-i':
        include_header = 1
    elif option in ('-I', '--head'):
        header_only = 1
    elif option in ('-u', '--user'):
        username, password = value.split(':', 2)

import urllib2 as u
terms = options[-1]
for term in terms:
    query = "http://en.wikipedia.org/w/api.php?action=query&titles="+ term + "+(Unix)&redirects&format=json&prop=revisions&rvprop=timestamp|content"
    req = u.Request(query)
    # print query
    try:
        f = u.urlopen(req)
#        if include_header or header_only: print f.headers
#        if not header_only: print f.read()
        import json
        j = json.loads(f.read())
        pages = j['query']['pages']
        k = pages.keys()[0]
        page = pages[k]
        title = page['title']
        timestamp = page['revisions'][0]['timestamp']
        content = page['revisions'][0]['*']
        content = content.encode('ascii', 'ignore')
        ## todo try catch these into a loop so we can handle errors
        content = content.split('== See also ==')[0]
        # content = content.replace('[[', '\n.B "')
        # content = content.replace(']]', '"')
        # content = content.replace('<code>', '\n.I "')
        # content = content.replace('</code>', '"\n')
        content = content.replace('[[', '')
        content = content.replace(']]', '')
        content = content.replace('<code>', '')
        content = content.replace('</code>', '')
        content = content.replace('<tt>', '')
        content = content.replace('</tt>', '')
        content = content.replace('==\n', '\n')
        content = content.replace('\n==', '\n.SH ')
        content = content.replace('==', '\n')
        content = content.replace('\'\'\'', '"')
        content = content.replace('<!--', '')
        content = content.replace('-->', '')
        content = content.replace('&mdash;', '::')
        content = content.replace('{{lowercase}}', '')
        content = content.replace('.SH Examples', '.SH EXAMPLES')
        content = content.replace('.SH Syntax', '.SH SYNTAX')
        # content = content.encode('\n', '.p')
        wikititle = "http://en.wikipedia.org/wiki/"
        wikititle += title.replace(" ", "_")
        print ".TH " + title + " 0 " + timestamp
        print ".SH NAME"
        print title
        print ".SH SYNOPSIS"
        print content
        print ".SH SEE ALSO"
        print wikititle
    except Exception, e:
        print e.read()
