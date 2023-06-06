#Bugs.md

Here we place the list of known bugs in our labscript control system. For
reproducibility, we specify at least one commit that has the bug. Each commit
is specified by a number called a *hash*. Since these numbers are very unique,
you do not need to specify all the digits, only the first few are needed. For
example for commit `943ba098ecf980737e23cd4bf9122c39dc1fd89a`, you could just
write `943ba098` - the first few digits of the hash.

##photon_counter bug (Resolved)

Author: Enrique Mendez (2021/02/08)

Bug Type: Non-deterministic.

How to Reproduce: run `test_blue_mot.py` on repeat.

In labscriptlib commit hash `943ba098`, **AND** user_devices hash `a3daf9bd`
(this is definitely where the error is). The `blacs_worker.py` for the P7888
counter does not wait enough time for the photon counting card to dump it's data.
So occasionally it will complain that the file is in use by the time you
request the next run. We need to update the logic in this class to prevent
unnecessary breaks in sequence runs. 

The **resolution** was adding several checks for file usage before attempting a
write, or delete. Despite telling the file to delete at earlier points in the
script, the DLL or OS would not faithfully act out commands. This required
these redunant checks. Wait conditions were also added to not send too many
commands. This was mostly so debug print commands wouldn't overload the
Ybclock Operator. This can possibly slow down multiple shot speed. 



##Analog Camera Triggers are inverted. (Resolved)

Author: Enrique Mendez (2021/02/08)

Bug Type: Deterministic.

How to Reproduce: Take a picture with only one camera instead of two.

The channels in the analog camera triggers were switched before commit
`8a6c2b22`. This actually might have been a bug in labview code that persisted
because pictures were always taken simultaneously or, a bug that occured from
how I copied the labview definitions.
