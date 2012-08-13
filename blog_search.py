# coding: UTF-8
from sphinxapi import *
import sys, time
import MySQLdb as mdb

mode = SPH_MATCH_ALL
host = 'localhost'
port = 9312
index = '*'
filtercol = 'group_id'
filtervals = []
sortby = ''
groupby = ''
groupsort = '@group desc'
limit = 0

def main():
    q = ''
    i = 1
    while (i<len(sys.argv)):
        arg = sys.argv[i]
        q = '%s%s ' % ( q, arg )
        i += 1
    q = q.decode('UTF-8')
    #print '%s\n' % q

    # do query
    cl = SphinxClient()
    cl.SetServer ( host, port )
    cl.SetWeights ( [100, 1] )
    cl.SetMatchMode ( mode )
    if filtervals:
        cl.SetFilter ( filtercol, filtervals )
    if groupby:
        cl.SetGroupBy ( groupby, SPH_GROUPBY_ATTR, groupsort )
    if sortby:
        cl.SetSortMode ( SPH_SORT_EXTENDED, sortby )
    if limit:
        cl.SetLimits ( 0, limit, max(limit,1000) )
    res = cl.Query ( q, index )

    if not res:
        print 'query failed: %s' % cl.GetLastError()
        sys.exit(1)

    if cl.GetLastWarning():
        print 'WARNING: %s\n' % cl.GetLastWarning()

    print 'Query \'%s\' retrieved %d of %d matches in %s sec' % (q, res['total'], res['total_found'], res['time'])
    print 'Query stats:'

    if res.has_key('words'):
        for info in res['words']:
            print '\t\'%s\' found %d times in %d documents' % (info['word'], info['hits'], info['docs'])

    if res.has_key('matches'):
        con = mdb.connect('localhost', 'ganyue', 'miaomiaomiao', 'blogdb')
        cur = con.cursor()
        print '\n'
        n = 1
        print '\nMatches:'
        for match in res['matches']:
            attrsdump = ''
            for attr in res['attrs']:
                attrname = attr[0]
                attrtype = attr[1]
                value = match['attrs'][attrname]
                if attrtype==SPH_ATTR_TIMESTAMP:
                    value = time.strftime ( '%Y-%m-%d %H:%M:%S', time.localtime(value) )
                attrsdump = '%s, %s=%s' % ( attrsdump, attrname, value )

            with con:
                cur.execute('SELECT * FROM archive where Id = %d' % match['id'])
                row = cur.fetchone()
            print '%d. weight=%d, Id=%d, Title=%s, Author=%s, Content=%s, Date=%s%s' % (n, match['weight'], match['id'], row[1], row[2], row[3], row[4], attrsdump)
            print '\n'
            n += 1

if __name__ == '__main__':
    if not sys.argv[1:]:
        print "Usage: python blog_search.py query words\n"
        sys.exit(0)
    main();
