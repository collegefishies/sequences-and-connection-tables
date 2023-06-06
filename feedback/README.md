#Feedback

This folder stores our scripts for running runmanager and editing globals.

## Simple Feedback

It turns out to do simple feedback, which is the heart of more complex
feedback routines, one needs to use a small program
[runmanager.remote](https://github.com/labscript-suite/runmanager/blob/master/runmanager/remote.py).
"For example `runmanager.remote.get_globals()` will return a dictionary of
global names and their values. It will connect to the instance of runmanager
at the IP address specified in your labconfig under `[servers]` / runmanager by
default." - Zak

"Note that a default instance of the client class defined in that module is
created
[here](https://github.com/labscript-suite/runmanager/blob/2181d1048eff81f3e2b2a3de00993c5332b0ccf6/runmanager/remote.py#L117),
then [all the methods of the
module](https://github.com/labscript-suite/runmanager/blob/2181d1048eff81f3e2b2a3de00993c5332b0ccf6/runmanager/remote.py#L119-L140)
just call the corresponding methods of that default client instance. If you
need to talk to a different instance of runmanager than the one specified in
your labconfig, you can create your own instance of `runmanager.remote.Client`
for your desired IP/port." - Zak

Calls to `runmanager.remote` can be made to execute as part of the labscript
loop by calling them from lyse as a single-shot analysis routine. This
guarantees that feedback is done after every sequence.