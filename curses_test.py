#!/usr/bin/env python


import curses
import time

import pprint

def centerStringInWindow(window, string):
    height, width = window.getmaxyx()
    yorigin = (height / 2) - 1
    xorigin = (width / 2) - (len(string) / 2)
    window.addstr(yorigin, xorigin, string)
    return


def generatePad(stdscr, padlines=100, padcols=100):
    height, width = stdscr.getmaxyx()
    
     
    
    pad = curses.newpad(padlines,padcols)
    for y in range(0,padlines):
        for x in range(0,padcols):
            try:
                pad.addch(y,x,ord('a') + (x*x+y*y) % 26)
            except curses.error:
                pass
    
    pad.box()
    
    
    return pad

def debugScroll(padparams, window):
    centerStringInWindow(window, pprint.pformat(padparams))

def refreshPad(pad, padparams):
    pad.refresh(padparams['pminrow'], padparams['pmincol'], padparams['sminrow'], padparams['smincol'], padparams['smaxrow'], padparams['smaxcol'])

def main(stdscr):
    stdscr.clear()
    hello = 'Hello, world!'
    bye = 'Goodbye.'
    stdscr.addstr(hello)
    stdscr.refresh()
    
    padparams = {
        'pminrow':0,
        'pmincol':0,
        'sminrow':0,
        'smincol':10,
        'smaxrow':20,
        'smaxcol':75,
        'padlines':100,
        'padcols':100
    }
    
    pad = generatePad(stdscr, padparams['padlines'], padparams['padcols'])
    
    refreshPad(pad, padparams)
    
    while 1:
        c = stdscr.getch()
        if c == ord('q'):
            stdscr.clear()
            centerStringInWindow(stdscr, bye)
            stdscr.refresh()
            #time.sleep(2)
            break
        elif c == ord('h'):
            helpMessage = 'Press "q" to quit.'
            centerStringInWindow(stdscr, helpMessage)
            stdscr.refresh()
        elif c == curses.KEY_UP:
            if (padparams['pminrow'] > 0):
                padparams['pminrow']-=1
            debugScroll(padparams, stdscr)
            refreshPad(pad, padparams)
        elif c == curses.KEY_DOWN:
            if (padparams['pminrow'] < (padparams['padlines']-padparams['smaxrow']+padparams['sminrow']-1)):
                padparams['pminrow']+=1
            debugScroll(padparams, stdscr)
            refreshPad(pad, padparams)
        elif c == curses.KEY_LEFT:
            if (padparams['pmincol'] > 0):
                padparams['pmincol']-=1
            debugScroll(padparams, stdscr)
            refreshPad(pad, padparams)
        elif c == curses.KEY_RIGHT:
            if (padparams['pmincol'] < (padparams['padcols']-padparams['smaxcol']+padparams['smincol']-1)):
                padparams['pmincol']+=1
            debugScroll(padparams, stdscr)
            refreshPad(pad, padparams)
        elif c == curses.KEY_HOME:
            padparams['pminrow']=0
            padparams['pmincol']=0
            debugScroll(padparams, stdscr)
            refreshPad(pad, padparams)
        elif c == curses.KEY_BACKSPACE:
            centerStringInWindow(stdscr, "pressed KEY_BACKSPACE")
        elif c == curses.KEY_END:
            centerStringInWindow(stdscr, "pressed KEY_END")

            

if __name__ == '__main__':
    # curses.wrapper takes care of terminal initialization and cleanup for us:
    curses.wrapper(main)