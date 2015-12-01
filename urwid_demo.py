#!/usr/bin/env python

import urwid

if __name__=='__main__':

    def show_or_exit(key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        txt.set_text(repr(key))

    datetext=[]
    clienttext=[]
    servertext=[]

    for i in range(0,100):
        datetext.append(urwid.Text("date column - line %u" % i))
        clienttext.append(urwid.Text("client column - line %u" % i))
        servertext.append(urwid.Text("server column - line %u" % i))

    txt = urwid.Text(u"Hello World")
    columns = urwid.Columns([
        urwid.LineBox(urwid.ListBox(datetext)),
        urwid.LineBox(urwid.ListBox(clienttext)),
        urwid.LineBox(urwid.ListBox(servertext))
    ])
    #fill = urwid.Filler(columns, 'top')
    #loop = urwid.MainLoop(fill, unhandled_input=show_or_exit)
    header = urwid.AttrWrap(urwid.Text("headertext"), 'header')
    frame = urwid.Frame( columns, header=header)
    loop = urwid.MainLoop(frame, unhandled_input=show_or_exit)
    loop.run()
