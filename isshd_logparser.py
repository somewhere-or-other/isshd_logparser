#!/usr/bin/env python


import re
import urllib
import argparse
import gzip
import os.path
from datetime import datetime
import string
import unicodedata
import curses

import pprint



def cursesMain(stdscr, sessionevents):
    
    columnstrings = {
        'date': {'strings':[], 'maxlen':0},
        'client': {'strings':[], 'maxlen':0},
        'server': {'strings':[], 'maxlen':0}
    }
    
    
    #preprocess sessionevents
    for eventdatetime in sorted(sessionevents):
        datestr = '%s' % eventdatetime
        columnstrings['date']['strings'].append(datestr)
        if len(datestr) > columnstrings['date']['maxlen']:
            columnstrings['date']['maxlen']=len(datestr)
            
        if sessionevents[eventdatetime]['type'] == "channel_data_client_3":
            columnstrings['client']['strings'].append(sessionevents[eventdatetime]['data'])
            columnstrings['server']['strings'].append('')
            if len(sessionevents[eventdatetime]['data']) > columnstrings['client']['maxlen']:
                columnstrings['client']['maxlen'] = len(sessionevents[eventdatetime]['data'])
        elif sessionevents[eventdatetime]['type'] == 'channel_data_server_3':
            columnstrings['server']['strings'].append(sessionevents[eventdatetime]['data'])
            columnstrings['client']['strings'].append('')
            if len(sessionevents[eventdatetime]['data']) > columnstrings['server']['maxlen']:
                columnstrings['server']['maxlen'] = len(sessionevents[eventdatetime]['data'])
                
                
                
    #for eventdatetime in sorted(sessionevents):
    #print "{when} - Type: {type}, Host: {host}, Data: {data}".format(when=eventdatetime, type=sessionevents[eventdatetime]['type'], host=sessionevents[eventdatetime]['host'], data=sessionevents[eventdatetime]['data'])  
    
    stdscr.clear()
    stdscr.refresh()
    
    height, width = stdscr.getmaxyx()
    
    width_3 = width/3
    lines = len(sessionevents)
    
    
    pads = {    
                'date': {'pad':None, 'params':{'pminrow':0, 'pmincol':0, 'sminrow':0, 'smincol':0, 'smaxrow':height, 'smaxcol':75, 'padlines':lines+2, 'padcols':columnstrings['date']['maxlen']+2}},
                'client': {'pad':None, 'params':{'pminrow':0, 'pmincol':0, 'sminrow':0, 'smincol':0, 'smaxrow':height, 'smaxcol':75, 'padlines':lines, 'padcols':columnstrings['client']['maxlen']}},
                'server': {'pad':None, 'params':{'pminrow':0, 'pmincol':0, 'sminrow':0, 'smincol':0, 'smaxrow':height, 'smaxcol':75, 'padlines':lines, 'padcols':columnstrings['server']['maxlen']}}
            }
    
    
    #pad = cursesGeneratePad(stdscr, padparams)
    pads['date']['pad'] = cursesGeneratePad(stdscr, pads['date']['params'], text="\n".join(columnstrings['date']['strings']))
    #pads['client']['pad'] = cursesGeneratePad(stdscr, pads['client']['params'], text="\n".join(columnstrings['client']['strings']))
    #pads['server']['pad'] = cursesGeneratePad(stdscr, pads['server']['params'], text="\n".join(columnstrings['server']['strings']))
    
    #cursesRefreshPad(pad, padparams)
    
    #cursesRefreshPad(pads['date']['pad'], pads['date']['params'])
    #cursesRefreshPad(pads['client']['pad'], pads['client']['params'])
    #cursesRefreshPad(pads['server']['pad'], pads['server']['params'])
    
    while 1:
        c = stdscr.getch()
        if c == ord('q'):
            stdscr.clear()
            stdscr.refresh()
            break
        elif c == ord('h'):
            helpMessage = 'Press "q" to quit.'
            cursesCenterStringInWindow(stdscr, helpMessage)
            stdscr.refresh()
        elif c == curses.KEY_UP:
            if (padparams['pminrow'] > 0):
                padparams['pminrow'] -= 1
            #cursesRefreshPad(pad, padparams)
        elif c == curses.KEY_DOWN:
            if (padparams['pminrow'] < (padparams['padlines']-padparams['smaxrow']+padparams['sminrow']-1)):
                padparams['pminrow'] += 1
            #cursesRefreshPad(pad, padparams)
        elif c == curses.KEY_LEFT:
            if (padparams['pmincol'] > 0):
                padparams['pmincol'] -= 1
            #cursesRefreshPad(pad, padparams)
        elif c == curses.KEY_RIGHT:
            if (padparams['pmincol'] < (padparams['padcols']-padparams['smaxcol']+padparams['smincol']-1)):
                padparams['pmincol'] += 1
            #cursesRefreshPad(pad, padparams)
        elif c == curses.KEY_HOME:
            padparams['pminrow'] = 0
            padparams['pmincol'] = 0
            #cursesRefreshPad(pad, padparams)
        #TODO: handle PgUp and PgDown by the screenfull
        
        stdscr.refresh()


def cursesRefreshPad(pad, padparams):
    pad.refresh(padparams['pminrow'], padparams['pmincol'], padparams['sminrow'], padparams['smincol'], padparams['smaxrow'], padparams['smaxcol'])


def cursesCenterStringInWindow(window, string):
    height, width = window.getmaxyx()
    yorigin = (height / 2) - 1
    xorigin = (width / 2) - (len(string) / 2)
    window.addstr(yorigin, xorigin, string)
    return


def cursesGeneratePad(stdscr, padparams, text=None):
    pad = curses.newpad(padparams['padlines'],padparams['padcols'])
    
    if text==None:
        for y in range(0,padparams['padlines']):
            for x in range(0,padparams['padcols']):
                try:
                    pad.addch(y,x,ord('a') + (x*x+y*y) % 26)
                except curses.error:
                    pass
    else:
        #pprint.pprint(text)
        pad.addstr(text)
        
    #pad.box()
    pad.border()
    
    
    return pad
    

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

if __name__=="__main__":
    argparser = argparse.ArgumentParser(description="Extract info from isshd logs, making it more intelligible")
    argparser.add_argument('-s', '--sessionid', action='store', metavar="SESSIONID", dest='sessionid', help="REQUIRED OPTION. Session to extract from the log.  Note that this is usually available in the Bro notification email, right before the username.", required=True)
    argparser.add_argument('-l', '--logfile', action='append', metavar='LOGFILEPATH', dest='logfiles', help="Specifies the path or paths to extract data from.  May be specified multiple times, and log files may be compressed with '.gz' extension.", default=[])
    argparser.add_argument('-c', '--curses', action="store_true", dest="curses", help="use curses-based output (h for help, q to exit)")

    args = argparser.parse_args()
    
    
    if args.logfiles==[]:
        args.logfiles.append("/usr/local/bro/logs/isshd/isshd.log");
    
    
    

    session_regex_match = r"^(channel_data_server_3|channel_data_client_3)\s+time=([.\d]+)\s+uristring=(\S+)\s+uristring=-?\d+%%3A(\S+)\s+count=%s\s+count=0\s+uristring=(\S+)\s*$" % args.sessionid
    
    session_regex_match_re = re.compile(session_regex_match)
    
    sessionevents={}
    
    for filename in args.logfiles:
        print "Parsing parse %s" % filename
        
        fh = openFile(filename)
    
        line = fh.readline()
        while line:
            matchresults = session_regex_match_re.search(line)
            if matchresults != None:
                matchcaptures = matchresults.groups()
                
                sessionevents[datetime.fromtimestamp(float(matchcaptures[1]))]={'type': matchcaptures[0], 'software': matchcaptures[2], 'host': decodeData(matchcaptures[3]), 'data': decodeData(matchcaptures[4])}
            line = fh.readline()
        
        fh.close()
        
        print "Done parsing %s" % filename
        
    if args.curses:
        curses.wrapper(cursesMain, sessionevents)
    else:
        for eventdatetime in sorted(sessionevents):
            print "{when} - Type: {type}, Host: {host}, Data: {data}".format(when=eventdatetime, type=sessionevents[eventdatetime]['type'], host=sessionevents[eventdatetime]['host'], data=sessionevents[eventdatetime]['data'])
    