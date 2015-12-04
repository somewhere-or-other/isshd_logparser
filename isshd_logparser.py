#!/usr/bin/env python


import re
import urllib
import argparse
import gzip
import os.path
from datetime import datetime
import string
import unicodedata

#import pprint

interactivedefault=True #change to false if you want non-interactive to be default

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




if __name__=="__main__":
    argparser = argparse.ArgumentParser(description="Extract info from isshd logs, making it more intelligible")
    argparser.add_argument('-s', '--sessionid', action='store', metavar="SESSIONID", dest='sessionid', help="REQUIRED OPTION. Session to extract from the log.  Note that this is usually available in the Bro notification email, right before the username.", required=True)
    argparser.add_argument('-l', '--logfile', action='append', metavar='LOGFILEPATH', dest='logfiles', help="Specifies the path or paths to extract data from.  May be specified multiple times, and log files may be compressed with '.gz' extension.", default=[])
    argparser.add_argument('-i', '--interactive', action="store_true", dest="interactive", help="use colorized, interactive output (q to exit)", default=interactivedefault)
    argparser.add_argument('-n', '--noninteractive', action="store_false", dest="interactive", help="plain, non-interactive output")
    
    args = argparser.parse_args()
    
    interactive_output = args.interactive
    
    try:
        import urwid
        
        #we succeeded in importing.  Just use whatever the user already specified, which we've already put into "interactive_output"
        #and define a bunch of stuff here, so if we don't have it, these won't throw errors about unknown names
        
        class ItemWidget (urwid.WidgetWrap):

            def __init__ (self, id, date, message, msgtype):
                self.id = id
                self.item = [
                    ('fixed', 28, urwid.Padding(urwid.AttrWrap(urwid.Text('%s' % date), 'date', 'focus'))),
                    urwid.Text((msgtype, '%s' % message))
                ]
                w = urwid.Columns(self.item)
                self.__super.__init__(w)

            def selectable (self):
                return True

            def keypress(self, size, key):
                return key

        def urwidMain(eventslist, sessionid):
        
            #main color pallette:
            #Syntax:
            # ( NAME , ForegroundColor, BackgroundColor, I'm Not Sure )
            palette = [
                ('date','light gray', '', 'standout'),
                ('focus','dark red', '', 'standout'),
                ('client', 'dark green', '', 'standout'),
                ('clientbg', '', 'dark green', 'standout'),
                ('server', 'brown', '', 'standout'),
                ('serverbg', '', 'brown', 'standout'),
                ('header','light red', 'black'),
                ]  
        
            headerstring = "isshd_logparser for session %s" % sessionid
            client_key_string='Client Input'
            server_key_string='Server Output'
            key_key_string='Key:'
            
            mainheader = urwid.AttrWrap(urwid.Text(headerstring), 'header')


        
            legend = urwid.Columns([
                urwid.Padding(urwid.Text(key_key_string), left=5),
                (2, urwid.AttrWrap(urwid.Text('', align='right'), 'clientbg')),
                urwid.AttrWrap(urwid.Text(client_key_string, align='left'), 'client'),
                (2, urwid.AttrWrap(urwid.Text('', align='right'), 'serverbg')),
                urwid.AttrWrap(urwid.Text(server_key_string, align='left'), 'server')
                ])
            
            headercolumns = urwid.Columns([
                mainheader,
                (len(key_key_string)+len(client_key_string)+len(server_key_string)+15, legend)
                ])
            

            
            frame = urwid.Frame( urwid.ListBox(eventslist), header=headercolumns)
            
            def unhandled(key):
                if key in ('q','Q'):
                    raise urwid.ExitMainLoop()

            loop = urwid.MainLoop(frame, palette, unhandled_input=unhandled)
            loop.run()
            
        
        
        
        
        
    except ImportError:
        if (args.interactive):
            print "Error: interactive output requires the URWID library (urwid.org), but I can't seem to find it.  Reverting to non-interactive output"
        interactive_output=False
    
    
    if args.logfiles==[]:
        args.logfiles.append("/usr/local/bro/logs/isshd/isshd.log");
    

    session_regex_match = r"^(channel_data_server_3|channel_data_client_3)\s+time=([.\d]+)\s+uristring=(\S+)\s+uristring=-?\d+%%3A(\S+)\s+count=%s\s+count=0\s+uristring=(\S+)\s*$" % args.sessionid
    
    session_regex_match_re = re.compile(session_regex_match)

    displaylines = [] #for interactive
    sessionevents = {} #for plain output
    idcount=0
    
    for filename in args.logfiles:
        print "Parsing file %s" % filename
        
        fh = openFile(filename)
    
        line = fh.readline()
        
        if (interactive_output):
            #TODO: handle sorting events by date/time, when sessions are split across multiple files
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
                
        else: #non-interactive output
            
            while line:
                matchresults = session_regex_match_re.search(line)
                if matchresults != None:
                    matchcaptures = matchresults.groups()
                    
                    eventtype="Unknown"
                    
                    if matchcaptures[0] == "channel_data_client_3":
                        eventtype="Client"
                    elif matchcaptures[0] == "channel_data_server_3":
                        eventtype="Server"
                    
                    
                    sessionevents[datetime.fromtimestamp(float(matchcaptures[1]))]={'type': eventtype, 'data': decodeData(matchcaptures[4])}

                line = fh.readline()
            
        fh.close()
        
        print "Done parsing %s" % filename
        
    
    
    if (interactive_output):
        urwidMain(displaylines, args.sessionid)
    else:
        for eventdatetime in sorted(sessionevents):
            print "{when} {type}: {data}".format(when=eventdatetime, type=sessionevents[eventdatetime]['type']
, data=sessionevents[eventdatetime]['data'])

