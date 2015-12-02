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
#import urwid.raw_display


class ItemWidget (urwid.WidgetWrap):

    def __init__ (self, id, date, message, msgtype):
        self.id = id
        self.item = [
            ('fixed', 28, urwid.Padding(urwid.AttrWrap(urwid.Text('%s' % date), 'date', 'focus'))),
            urwid.Text((msgtype, '%s' % message), wrap='clip')
        ]
        w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key


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
        #return urllib.unquote_plus(data).lstrip()

def urwidMain(eventslist, sessionid):
    mainheader = urwid.Pile([ urwid.AttrWrap(urwid.Text("isshd_logparser for session %s" % sessionid), 'header'), urwid.AttrWrap(urwid.Text('Client Input'), 'client'), urwid.AttrWrap(urwid.Text('Server Output'), 'server') ])
    
    palette = [
        ('date','light gray', '', 'standout'),
        ('focus','dark red', '', 'standout'),
        ('client', 'dark green', '', 'standout'),
        ('server', 'brown', '', 'standout'),
        ('head','light red', 'black'),
        ]
    
    frame = urwid.Frame( urwid.ListBox(eventslist), header=mainheader)
    
    def unhandled(key):
        if key in ('q','Q'):
            raise urwid.ExitMainLoop()

    loop = urwid.MainLoop(frame, palette, unhandled_input=unhandled)
    loop.run()

if __name__=="__main__":
    argparser = argparse.ArgumentParser(description="Extract info from isshd logs, making it more intelligible")
    argparser.add_argument('-s', '--sessionid', action='store', metavar="SESSIONID", dest='sessionid', help="REQUIRED OPTION. Session to extract from the log.  Note that this is usually available in the Bro notification email, right before the username.", required=True)
    argparser.add_argument('-l', '--logfile', action='append', metavar='LOGFILEPATH', dest='logfiles', help="Specifies the path or paths to extract data from.  May be specified multiple times, and log files may be compressed with '.gz' extension.", default=[])
    
    
    args = argparser.parse_args()
    
    
    if args.logfiles==[]:
        args.logfiles.append("/usr/local/bro/logs/isshd/isshd.log");
    
    
    

    session_regex_match = r"^(channel_data_server_3|channel_data_client_3)\s+time=([.\d]+)\s+uristring=(\S+)\s+uristring=-?\d+%%3A(\S+)\s+count=%s\s+count=0\s+uristring=(\S+)\s*$" % args.sessionid
    
    session_regex_match_re = re.compile(session_regex_match)

    displaylines = []
    idcount=0
    
    for filename in args.logfiles:
        print "Parsing file %s" % filename
        
        fh = openFile(filename)
    
        line = fh.readline()
        while line:
            matchresults = session_regex_match_re.search(line)
            if matchresults != None:
                matchcaptures = matchresults.groups()
                
                
                if matchcaptures[0]=="channel_data_server_3":
                    displaylines.append(ItemWidget(idcount, datetime.fromtimestamp(float(matchcaptures[1])), decodeData(matchcaptures[4]), 'server'))
                    idcount += 1
                elif matchcaptures[0]=="channel_data_client_3":
                    displaylines.append(ItemWidget(idcount, datetime.fromtimestamp(float(matchcaptures[1])), decodeData(matchcaptures[4]), 'client'))
                    idcount += 1
            line = fh.readline()
        
        fh.close()
        
        print "Done parsing %s" % filename
        
    
    urwidMain(displaylines, args.sessionid)
