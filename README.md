# isshd_logparser
A quick-and-dirty tool to extract client/server interaction information from an [Instrumented SSH](https://github.com/set-element/InstrumentedSSHD) instance.

The purpose here is to take a session ID number from an ISSHd/Bro email, and be able to extract the details of the session, to try to figure out context, and what triggered the alert.

This requires the [URWID](http://urwid.org/) toolkit to render the textual environment.

For syntax help, run the following:
> isshd_logparser.py -h
