#!/usr/bin/env python


import re
import urllib
import argparse
import gzip, bz2
import os.path


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


if __name__=="__main__":
    argparser = argparse.ArgumentParser(description="Extract info from isshd logs, making it more intelligible")
    argparser.add_argument('-s', '--sessionid', action='store', metavar="SESSIONID", dest='sessionid', help="REQUIRED OPTION. Session to extract from the log.  Note that this is usually available in the Bro notification email, right before the username.", required=True)
    argparser.add_argument('-l', '--logfile', action='append', metavar='LOGFILEPATH', dest='logfiles', help="Specifies the path or paths to extract data from.  May be specified multiple times, and log files may be compressed with '.gz' extension.", default=[])
    
    
    args = argparser.parse_args()
    
    
    if args.logfiles==[]:
        args.logfiles.append("/usr/local/bro/logs/isshd/isshd.log");
    
    for filename in args.logfiles:
        print "Opening to parse %s" % filename
        
        