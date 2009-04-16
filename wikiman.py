#!env python
'''Which wikipedia page do you want?
Fetch Wikipages on Unix commands like man pages like:
% python wikiman.py <COMMAND> | nroff -man | less
'''

class WikiMan:
    '''Get a term, query it from the wikipedia, and nroff it.'''
    def __init__(self, term, raw = False): 
        self.term = term
        self.raw = raw
        query = self.makeQuery(self.term, self.raw)
        import urllib2
        req = urllib2.Request(query)
        try:
            f = urllib2.urlopen(req)
        except Exception, e:
            print e.read()
        import json
        j = json.loads(f.read())
        pages = j['query']['pages']
        k = pages.keys()[0]
        page = pages[k]
        self.title = page['title'].replace(" ", "_")
        self.timestamp = page['revisions'][0]['timestamp']
        body = page['revisions'][0]['*']
        self.content = self.wiki2nroff(body)
        self.wikilink = "http://en.wikipedia.org/wiki/"
        self.wikilink += self.title.replace(" ", "_")

    def makeQuery(self, term, raw):
        query = "http://en.wikipedia.org/w/api.php"
        query += "?action=query&titles="
        query += term
        if (raw is False):
            query += "+(Unix)"
        query += "&redirects&format=json"
        query += "&prop=revisions&rvprop=timestamp|content"
        return query

    def wiki2nroff(self, wikiText):
        # ascii encode - very important
        content = wikiText.encode('ascii', 'ignore')
        # kill the wiki links footer
        content = content.split('== See also ==')[0]
        ## todo: try catch these into a loop so we can handle
        ## errors
        ## todo: add list support
        content = content.replace('[[', '\\fB')
        content = content.replace(']]', '\\fR')
        content = content.replace('<code>', '\\fI')
        content = content.replace('</code>', '\\fR')
        content = content.replace(' : ', '\n')
        content = content.replace('\n; ', '\n.IP ')
        content = content.replace('<tt>', '')
        content = content.replace('</tt>', '')
        content = content.replace('==\n', '\n')
        content = content.replace('\n==', '\n.SH ')
        content = content.replace('==', '\n')
        content = content.replace('\'\'\'', '"')
        content = content.replace('<!--', '')
        content = content.replace('-->', '')
        content = content.replace('&mdash;', '::')
        ## todo: regex {{*}}
        content = content.replace('{{lowercase}}', '')
        ## lazy upcase 
        content = content.replace('.SH Examples', '.SH EXAMPLES')
        content = content.replace('.SH Syntax', '.SH SYNTAX')
        return content

    def getManPage(self):
        ## print it!
        page = ".TH " + self.title + " 0 " + self.timestamp
        page += "\n.SH NAME\n"
        page += self.title
        page += "\n.SH SYNOPSIS\n"
        page += self.content
        page + "\n.SH SEE ALSO\n"
        page += self.wikilink
        return page

def main():
    import getopt
    import sys
    options = getopt.getopt(sys.argv[1:],
                            'h, r',
                            ['help', 'raw'])
    raw = False
    if len(options[-1]) is 0:
        print "Which wikipedia page do you want?"
        sys.exit(0)
    for option, value in options[0]:
        if option in ('-h', '--help'):
            if (len(options[-1]) is 0):
                print "Which wikipedia page do you want?"
            else:
                print __doc__
            sys.exit(0)
        elif option in ('-r', '--raw'):
            raw = True
    term = options[-1][0]
    app = WikiMan(term, raw)
    print app.getManPage()

if __name__ == "__main__":
    main()

