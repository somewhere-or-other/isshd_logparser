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
            urwid.Text((msgtype, '%s' % message))
        ]
        w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

#class OverlayBgFocus (urwid.Overlay):
    #def selectable(self):
        #"""Return selectable from bottom_w."""
        #return self.bottom_w.selectable()

    #def keypress(self, size, key):
        #"""Pass keypress to bottom_w."""
        #return self.bottom_w.keypress(size, key)

    #def _get_focus(self):
        #"""
        #Currently self.bottom_w is always the focus of an Overlay
        #"""
        #return self.bottom_w
 
    #def _get_focus_position(self):
        #"""
        #Return the bottom widget position (currently always 0).
        #"""
        #return 0
    #def _set_focus_position(self, position):
        #"""
        #Set the widget in focus.  Currently only position 0 is accepted.

        #position -- index of child widget to be made focus
        #"""
        #if position != 0:
            #raise IndexError, ("OverlaBgFocus widget focus_position currently "
                #"must always be set to 0, not %s" % (position,))
    
    #def mouse_event(self, size, event, button, col, row, focus):
        #"""Pass event to bottom_w, ignore if outside of bottom_w."""
        #if not hasattr(self.bottom_w, 'mouse_event'):
            #return False

        #left, right, top, bottom = self.calculate_padding_filler(size,
            #focus)
        #maxcol, maxrow = size
        #if ( col<left or col>=maxcol-right or
            #row<top or row>=maxrow-bottom ):
            #return False

        #return self.bottom_w.mouse_event(
            #self.bottom_w_size(size, left, right, top, bottom),
            #event, button, col-left, row-top, focus )

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


    #legend = urwid.LineBox( urwid.ListBox([ urwid.AttrWrap(urwid.Text(client_key_string, align='center'), 'client'), 
        #urwid.AttrWrap(urwid.Text(server_key_string, align='center'), 'server')]), title='Key')

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
    

    
    #frame = urwid.Frame( urwid.ListBox(eventslist), header=mainheader)
    frame = urwid.Frame( urwid.ListBox(eventslist), header=headercolumns)
    
    #overlay = OverlayBgFocus(legend, frame ,valign='top', align='right', width=max(len(client_key_string),len(server_key_string))+2, height=4)
    #overlay = urwid.Overlay(legend, frame ,valign='top', align='right', width=max(len(client_key_string),len(server_key_string))+2, height=4)
    
    
    def unhandled(key):
        if key in ('q','Q'):
            raise urwid.ExitMainLoop()

    #loop = urwid.MainLoop(overlay, palette, unhandled_input=unhandled)
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
