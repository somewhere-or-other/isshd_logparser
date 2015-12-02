#!/usr/bin/env python

import urwid

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


if __name__=='__main__':

    #updatecount=0
    
    palette = [
        ('date','dark blue', '', 'standout'),
        ('focus','dark red', '', 'standout'),
        ('client', 'dark green', '', 'standout'),
        ('server', 'brown', '', 'standout'),
        ('head','light red', 'black'),
        ]

    
    def show_or_exit(key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()



    rows = []

    for i in range(0,100):
        
        item = ItemWidget(i, "date column - line %u" % i, "message column - line %u" % i, 'client' if (i%2==0) else 'server')
        rows.append(item)
            
    rowwalker = urwid.SimpleListWalker(rows)
    rowlistbox = urwid.ListBox(rowwalker)

    header = urwid.Columns([urwid.AttrWrap(urwid.Text("headertext", align='center'), 'header'), urwid.AttrWrap(urwid.Text("Client Says", align='center'), 'client'), urwid.AttrWrap(urwid.Text("Server Says", align='center'), 'server')])
    frame = urwid.Frame( rowlistbox, header=header)
    loop = urwid.MainLoop(frame, palette, unhandled_input=show_or_exit)
    
    
    loop.run()



