#!/usr/bin/env python


import re
import urllib
import argparse
import gzip
import os.path
from datetime import datetime
import string
import unicodedata

import pprint

import urwid
import urwid.raw_display


def openFile(filename=None):
    if filename==None:
        raise ValueError("No filename specified.")
    elif not os.path.exists(filename) or os.path.isdir(filename):
        raise ValueError("Filename specified doesn't exist or is a directory")
    elif filename.endswith(".gz"):
        return gzip.open(filename, 'r')
    else:
        return open(filename, 'r')
    
def escape_control_characters(s):
    return "".join(ch.encode('unicode_escape') if unicodedata.category(unicode(ch))[0]=="C" else ch for ch in s)

def decodeData(data=None):
    if data==None:
        raise ValueError("No data provided.")
    else:
        return escape_control_characters(urllib.unquote_plus(data).lstrip())

def urwidMain(eventslist, sessionid):
    mainheader = urwid.AttrWrap(urwid.Text("isshd_logparser for session %s" % sessionid), 'header')
    
    
    columns = urwid.Columns([
        (28, urwid.Frame(urwid.LineBox(urwid.ListBox(eventslist['date']), title="Date/Time"))),
        urwid.Frame(urwid.LineBox(urwid.ListBox(eventslist['client']), title="Client Typed")),
        urwid.Frame(urwid.LineBox(urwid.ListBox(eventslist['server']), title="Server Said"))
    ])
        
    
    frame = urwid.Frame( columns, header=mainheader)

    
    def unhandled(key):
        if key in ('q','Q'):
            raise urwid.ExitMainLoop()

    print "Debugging: right before MainLoop"

    loop = urwid.MainLoop(frame, unhandled_input=unhandled)
    loop.run()
    
    print "Debugging: right after MainLoop"

if __name__=="__main__":
    argparser = argparse.ArgumentParser(description="Extract info from isshd logs, making it more intelligible")
    argparser.add_argument('-s', '--sessionid', action='store', metavar="SESSIONID", dest='sessionid', help="REQUIRED OPTION. Session to extract from the log.  Note that this is usually available in the Bro notification email, right before the username.", required=True)
    argparser.add_argument('-l', '--logfile', action='append', metavar='LOGFILEPATH', dest='logfiles', help="Specifies the path or paths to extract data from.  May be specified multiple times, and log files may be compressed with '.gz' extension.", default=[])
    
    
    args = argparser.parse_args()
    
    
    if args.logfiles==[]:
        args.logfiles.append("/usr/local/bro/logs/isshd/isshd.log");
    
    
    

    session_regex_match = r"^(channel_data_server_3|channel_data_client_3)\s+time=([.\d]+)\s+uristring=(\S+)\s+uristring=-?\d+%%3A(\S+)\s+count=%s\s+count=0\s+uristring=(\S+)\s*$" % args.sessionid
    
    session_regex_match_re = re.compile(session_regex_match)
    
    columnobjs={ 'date':[], 'client': [], 'server': [] }
    sessionevents = {}
    
    for filename in args.logfiles:
        print "Parsing file %s" % filename
        
        fh = openFile(filename)
    
        line = fh.readline()
        while line:
            matchresults = session_regex_match_re.search(line)
            if matchresults != None:
                matchcaptures = matchresults.groups()
                
                sessionevents[datetime.fromtimestamp(float(matchcaptures[1]))]={'type': matchcaptures[0], 'software': matchcaptures[2], 'host': decodeData(matchcaptures[3]), 'data': decodeData(matchcaptures[4])}
                
                if matchcaptures[0]=="channel_data_server_3":
                    columnobjs['server'].append(urwid.Text(decodeData(matchcaptures[4]), wrap="clip"))
                    columnobjs['client'].append(urwid.Text(""))
                    columnobjs['date'].append(urwid.Text("%s"%datetime.fromtimestamp(float(matchcaptures[1]))))
                elif matchcaptures[0]=="channel_data_client_3":
                    columnobjs['client'].append(urwid.Text(decodeData(matchcaptures[4]), wrap="clip"))
                    columnobjs['server'].append(urwid.Text(""))
                    columnobjs['date'].append(urwid.Text("%s"%datetime.fromtimestamp(float(matchcaptures[1]))))                    
            line = fh.readline()
        
        fh.close()
        
        print "Done parsing %s" % filename
        
    
    #for eventdatetime in sorted(sessionevents):
        #print "{when} - Type: {type}, Host: {host}, Data: {data}".format(when=eventdatetime, type=sessionevents[eventdatetime]['type'], host=sessionevents[eventdatetime]['host'], data=sessionevents[eventdatetime]['data'])
    
    #pprint.pprint(columnobjs)
    #pprint.pprint(sessionevents)
    urwidMain(columnobjs, args.sessionid)
    
    