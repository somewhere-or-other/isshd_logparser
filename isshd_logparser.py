#!/usr/bin/env python


import re
import urllib
import argparse
import gzip, bz2
import os.path
from datetime import datetime

import pprint

#Example input lines:
#"channel_data_server_3 time=1448310282.769933 uristring=NMOD_3.17 uristring=-1463764005%3Am7int02%3A22 count=1639715128 count=0 uristring=%0A%5Blbrown%40m7int02+%7E%5D%24+"
#"channel_data_server_3 time=1448315006.883645 uristring=NMOD_3.17 uristring=-1463764261%3Am7int01%3A22 count=1069172562 count=0 uristring=%1B%5BK.%3A4+++0%2F0%3A11++.%2F.%3A5+++.%2F.%3A6+++.%2F.%3A2+++.%2F.%3A6+++0%2F0%3A12++.%2F.%3A10++0%2F0%3A20++.%2F.%3A10++0%2F0%3A17++0%2F0%3A15++0%2F0%3A16++.%2F.%3A5+++.%2F.%3A10++.%2F.%3A8+++.%2F.%3A"

def openFile(filename=None):
    if filename==None:
        raise ValueError("No filename specified.")
    elif not os.path.exists(filename) or os.path.isdir(filename):
        raise ValueError("Filename specified doesn't exist or is a directory")
    elif filename.endswith(".gz"):
        return gzip.open("filename", 'r')
    #elif filename.endswith(".bz2"):
        ##TODO: handle opening bzip2 file
    else:
        return open(filename, 'r')

def decodeData(data=None):
    if data==None:
        raise ValueError("No data provided.")
    else:
        return urllib.unquote_plus(data).lstrip()

if __name__=="__main__":
    argparser = argparse.ArgumentParser(description="Extract info from isshd logs, making it more intelligible")
    argparser.add_argument('-s', '--sessionid', action='store', metavar="SESSIONID", dest='sessionid', help="REQUIRED OPTION. Session to extract from the log.  Note that this is usually available in the Bro notification email, right before the username.", required=True)
    argparser.add_argument('-l', '--logfile', action='append', metavar='LOGFILEPATH', dest='logfiles', help="Specifies the path or paths to extract data from.  May be specified multiple times, and log files may be compressed with '.gz' extension.", default=[])
    
    
    args = argparser.parse_args()
    
    
    if args.logfiles==[]:
        args.logfiles.append("/usr/local/bro/logs/isshd/isshd.log");
    
    
    
    session_regex_match = r"^(channel_data_server_3|channel_data_client_3)\s+time=([.\d]+)\s+uristring=(\S+)\s+uristring=(\S+)\s+count=%s\s+count=0\s+uristring=(\S+)\s*$" % args.sessionid
    
    #pprint.pprint(session_regex_match)
    
    session_regex_match_re = re.compile(session_regex_match)
    
    sessionevents={}
    
    for filename in args.logfiles:
        print "Parsing parse %s" % filename
        
        fh = openFile(filename)
    
        line = fh.readline()
        while line:
            matchresults = session_regex_match_re.search(line)
            if matchresults != None:
                #print "found matching line: %s" % line
                matchcaptures = matchresults.groups()
                #pprint.pprint(matchcaptures)
                
                sessionevents[datetime.fromtimestamp(float(matchcaptures[1]))]={'type': matchcaptures[0], 'software': matchcaptures[2], 'host': matchcaptures[3], 'data': decodeData(matchcaptures[4])}
            line = fh.readline()
        
        fh.close()
        
        print "Done parsing %s" % filename
        
    #pprint.pprint(sessionevents)
    
    for eventdatetime in sessionevents:
        print "{when} - Type: {type}, Host: {host}, Data: {data}".format(when=eventdatetime, type=sessionevents[eventdatetime]['type'], host=sessionevents[eventdatetime]['host'], data=sessionevents[eventdatetime]['data'])
    