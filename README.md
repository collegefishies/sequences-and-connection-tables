Welcome to Ybclock Labscript Edition!

See the Feature List for what we've built and what you can do. Make sure you
understand how to edit & build the documentation if you're going to
contribute. This experiment should be able to be ran even if helpful grad
students aren't around.

If you find an interesting bug, that keeps you occupied for a couple of days,
stick it in `Bugs.md`.

# How to Edit & Build the Documentation

Documentation shall be performed using 'pdoc', as it is simple. Perfect for grad
students. Built Documentation is stored in '/html'. (This is is the README.md)

**pdoc** let's the user documentation stored in python `'''docstrings.'''` You
might have trouble compiling the documentation if you forget to wrap your
scripts, in `if __name__ == '__main__':` blocks. This prevents your code from trying to execute when pdoc imports it in the build process, and thus from hanging on errors, or unsatisfied requirements/inputs inside your code.

Whenever possible, divide code into functions, modules, etc. and document those
functions via  'docstrings'. These keeps the documentation close to the source
and allows pdoc to find it. The docstrings use markdown, as well as reST?, and latex**!**.

To use inline equations, type `\\(...\\)`. For a block, use `$$...$$` or `\\[...\\]`.

If you wish to add images, use a `.. image:: .imgs/imagefile.png` type
command. Note, currently, as far as I know, you have to manually move over the
images to the appropiate location in the `/html` build location. With the
batch file provided, pdoc won't move them.

See [the pdocs documentation](https://pdoc3.github.io/pdoc/doc/pdoc/#gsc.tab=0) 
for more.

Run `compile_documentation.bat` to compile the docs. It will work if the labscript
is on an anaconda install.

If you wish to build documentation see `labscriptlib.html` for more.

# Opening Labscript

For labscript to function properly it must be opened in order. 

1. `runmanager`
2. `BLACS`
3. `Lyse`

# Recommended Programming Environment (Sublime Text)

Use Sublime Text, and Sublime Merge for a fantastic text editor and repository
manager respectively.  Use the elasticTabstops package in Sublime Text! Very
useful for maintaining readable code.

## Renaming a Variable

Occasionally, you need to rename a channel, either to improve clarity or to
reflect an update. A multi-file search and replace is ideal for this, and
luckily, sublime text does this easily. 

While there is risk of unforseen replacements, an advantage of using long
variable names like we do, is there is reduced chance of errors when
performing a global search and replace. Although it is true, that the search
and replace might be so easy that you forget to update the documentation. 

To prevent this, document first, then perform a global search and replace.

To do this in sublime text, `Find > Find in Files (Ctrl+Shift+F)`, then select
your folder as `labscriptlib/ybclock/` and attempt to find the variable name
in question. Check to see that find is accurate, then write down the variable
name replacement. Double check the replacement spelling. Commit after the
change. This way it's easy to revert any unforseen incidents.

# Feature List

This implementation of labview was developed by the most fundamental feature
to the most obscure. It's thus how this list is ordered, which will help users
acclimate to the system.

This section is intended to enumerate the features, whose implementation will
occasionally be scattered across many file, so that future users can easily
find simple explanations of their intended use as well as the functions,
classes, or libraries that implemented them where one can find in depth
documentation.




## Virtual Environments

I am not familiar with the use of virtual environments. I know only that they 
are used to maintain independent versions of different programs. 

Code writing unfortunately involves a lot of debugging and determining the 
idiosyncracies of every function defined in the libraries you're using for 
development. These are at the whims of the developer and may change at any time.
No library is perfect in what ever respect you define at the outset, and so the 
developer might decide to change the syntax needed to do something. Rather than
have to rewrite *perfectly working* code, one can use a virtual environment to 
keep the libraries young for eternity. And if one needs to move or try updates,
transfer to a new virtual environment without breaking existing code.

That's all I know. If you want to learn more about how to actually implement 
these ideas in practice. Use google.

I'm using conda to manage virtual environments I believe. They are used via 
`conda activate ybclock` commands in the Anaconda Powershell. Use that as a starting point for understanding
how this virtual environment management is implemented. See [the labscript docs](https://docs.labscriptsuite.org/en/stable/installation/regular-anaconda/) for
more. Hopefully, that link won't break in the future.

## Working with HDF files

HDF files are nice, they're sort of like zip files, in that they are one file
that can hold "groups" which are just like Windows Folders, and "datasets"
which are like files, but restricted to multidimensional arrays consisting of
integers or floats. (This means if one wants to save something one needs to
encode it in such a format. Of course, this is less restrictive than a binary
format.)

However, unfortunately, **they are easy to corrupt**. If you access the HDF
file from two programs at once, it will corrupt. So if you leave it open in
python for instance and open it up with an HDF viewer, it will corrupt. So one
needs to take care not to open it from two places at once. This obviously
becomes less risky when working with old datasets (HDFs) as that means
labscript isn't opening the data. The biggest danger I've found is to work on
it with python and then open it up with an external HDF Viewer GUI. So if one
doesn't use the HDF Viewer, as well as only access HDF files via a `with
h5py.File(hdf5_filename, 'r') as hdf5_file:` syntax calls, which always close
the files when you leave their scope, you'll be fine. 

Labscript I believe also takes effort to prevent corruption, but I'm not so
well versed with it's protection techniques. So I'm not sure how much harder
it makes it to mess things up.

It definitely does not protect against 3rd Party Programs from reading an HDF
file simultaneously and causing corruption.

## Organized Sequence Structure
### Using Sequences

Open up `runmanager (ybclock)` and select the sequence you want. (De)select
run/view shots as you please. 

For testing compilation, turn off run/view shot then engage.

### Sequence File Structure

Sequence files can be stored anywhere. The way they import modules makes them
free to be wherever. So you can use whatever folder structure you desire to
organize the large number of sequences that will arise in the future.

I have them in `ybclock.sequences`

### Subsequence File Structure

The sequence must be defined in compartmentalized sections. That means a file
for a the Loading Sequence, maybe a file for the green mot, maybe for the blue.
A file for pumping sequence, and so on. A top-down partition is a MUST for
posterity, readability, and debugging. How 'down' you go is up to you. Too many
files for especially simple sequences is counter productive. As with everything
in life, this is an art.

See 'loading_sequence.py' for a good example. It has a function in there you can
 call to include it in the main sequence, or if you just want to run it in
constant mode to optimize the mot by hand you can, as there is a second block
for allowing compilation by run manager.

## Adding Devices

If you add a new device, it can be defined in either the virtual environment
directory of `labscript_devices` or the local directory
`labscript-suite/userlib/user_devices`. See `AnalogIMAQdxCamera` for a simple
example of the file structure needed. You also might need to look up Phil
Starkey's Thesis. `P7888` is the device I built from the ground up. So that's
a good example for the least that's needed, although it's file structure isn't
clear.

Every change you make beyond might need to be accompanied by a reset of the
appropriate portion labscript program.  You can get away sometimes with
smaller resets in each of the programs. Try it, but if it fails you know why.

If you edit `labscript_devices`, you definitely need to reset the whole program.

## Using Metadata (Essential)

Labscript was designed for BEC/Fermi gas type experiments that involve
manipulation of quantum gases. Such experiments are typically probed via
absorption imaging. A process which is destructive to the atoms, so one can
only measure once at the end of the experiment.

Our experiment isn't at all destructive, while it perturbs the spin state, for
the most part, the atoms are left intact. While the measurement can cause
unwanted heating and spin mixing, the atoms aren't guaranteed to be lost.

This allows us to measure repeatedly. And furthermore we can measure to
extract different aspects of the atomic spin state. Unfortunately, each
measurement can be quite similar in execution. This is essentially scanning
light across the cavity. 

However, *context* on the desired experiment can change analysis. So it's
useful to save **metadata** to be able to simplify analysis. This metadata
lets us easily save parameters that are available when writing the experiment,
that is much harder to infer from the instructions sent to the NI cards (which
is typically the only thing guaranteed to be saved either in your average AMO
lab or in Labscript).

While Labscript does not have wrapper functions for simplifying this process,
thanks to the help of the labscript writers, there exists a method for saving
metadata. The earliest implementation occured in the ExperimentalCavity class,
currently (April 9, 2021) saved in subsequences. (It's location may change in
the future.) See [this google group chat](groups.google.com/g/labscriptsuite/c/5ZzEHWkWft0) 
for more contextual information as well as technical detail. Look for my
questions (Enrique Mendez) to understand the intention. It took a number of
emails to straighten out a mutual understanding. Phil's answers I believe have
the most useful answers as well as technical information for how to store
metadata.

Currently, one must save the metadata in the HDF group 'shot_properties'. It
is necessary to store the files here so that BLACS keeps a copy of the
metadata when repeating the experimental shot. This can be done with
`compiler.shot_properties` which is a dictionary. One can import `compiler`
from `labscript`, i.e., `from labscript import compiler`. This works only when
executing a sequence script in runmanager.

To save complicated formats of data like dictionaries (which are quite nice as
they serve the ability to be self documenting since they can be indexed by
strings), one can use the `pickle` library which serializes (turns into a
binary stream), something that doesn't have a predefined algorithm for
serializing. In other words, it allows you to store `dict`s in a file or
array.

Data can be saved by opening up the HDF file directly or using labscripts
techniques for saving data: for example, in lyse, one can use
`run.save_result()`, or in the sequence generation side
`compiler.shot_properties`. 

## Simple Calibrations

Labscript implements a way for using calibrations. Our first attempt at this
was with a VCO. Simone wanted to implement the calibrations in globals. In
retrospect this was not ideal. Globals should be thought of as daily/weekly
tunable parameters. Calibrations are tuned much rarer than that. So it is
good practice to store the calibration data in the script where the
calibration is defined. See
`labscriptlib.ybclock.connection_functions.calibrations` for details.

### How do we define Calibrations
### Where are they stored
   
   For labscript 3.0.0, they have sto be stored with all the other base code
   of the virtual environment... unfortunately.


### Where can they be stored

   For labscript 3.1, I believe they improved the freedom in importing different calibrations.

   Ah yes `Save full import path of unit conversion classes
   (PR#84, chrisjbillington). This allows for custom unit conversion classes
   to be located outside the labscript_utils module (ie in the user’s
   labscriptlib)`. See [this mailing list email]
   (https://groups.google.com/g/labscriptsuite/c/w4v_PtgMAn0).

### How do we use them in Labscript?

## Class-Based Cavity Scan/Photon Counter/Data Management

Using Classes, we can make an object `ExperimentalCavity()` that: keeps track
of *start* pulses sent to the Photon Counting Card -- this lets us keep track
of how data is spaced in the binary file the P7888 DLL creates; contains a
dictionary for recording all the types of scans performed -- each seperated by
their method of analysis; as well as lists of dictionaries that contain the
parameters for each particular scan; and functions for saving these and
extracting these parameters from the HDF file for easy usage; the most
important is the development of the `scan(t,label)` function call which let's
us record the analysis label, as well as in the future, keep track of any
extra parameters that will be useful.

This class takes advantage of the ability to use metadata researched above.

For an example of the wonderful simplicity this gives the analysis, see
`ybclock.analysis.scripts.cavity_scan_analysis`.

## Analysis/Run Creation On A Different Computer

To take a load off of the current aging computer, we're going to take
advantage of labscripts ability to run across multiple computers. 

This isn't as simple as just installing labscript. As to compile shots, one
needs to also have access to the NI Card .py scripts. So I made a git repo in
the `labscript-devices` folder stored in the `ybclock` virtual environment. I
pulled it on the analysis comp to ensure that we can have the same labscript
files for when we inevitably need to add the NI Analog Input cards (April
2021).

One also need to keep a record of the Calibration Scripts. This is stored in
`labscript_utils` in the virtual enviroment as well.


To ensure a connection, one needs to change the `.ini` files stored in the
`%USERPROFILE%\labscript-suite\labconfig\` to ensure they both look for the
same secret key and the correct IP addresses for the `[servers]`.

## Simple Feedback Loops

One feature we need is to perform feedback on measured atom data and adjust
future experiments accordingly. 

The simplest example we have of this, is measuring the empty experimental
cavity frequency and adjusting the bridging frequency for the 759nm laser.
This allows us to position the experimental cavity to be on resonance with the
atoms.

## MLOOP

MLOOP is a Machine Learning Based optimization suite for optimizing
experiments.

### How it Works (Top Level)

MLOOP is an external program to Labscript. Ultimately, it is a program that
plays the role of the graduate student. So think of it in that way, we first
tell the grad student which parameters we want to scan: this is specified in
MLOOPs config file.

 * Need to Specify the Config File (Parameters to Scan & How to Learn) 
 * Running MLOOP
    * Sets the parameters, runs labscript, analyzes the results and repeats. 

### How to Use It (Mid Level)

Our scripts for making config files are stored in `scripts\mloop\`. Building
them will generate a local MLOOP config file, i.e., in the same directory.
The MLOOP program expects the config file to be in it's installed directory
of config files.

Use `mloop_multishot.py` in the multishot section of lyse. It's stored in `analysis\analysislib-mloop`.
You also need the `generate_cost.py` script in the single shot routine. This is the thing it optimizes.

Make sure the config file is also stored in `analysislib-mloop`. The easiest
way to do this is to hardlink the file created in `scripts` into this new
location. To do this on windows, use `mklink /h "final location" "source"` on Command Prompt in Admin Mode.

Once that's done, you can just execute the `mloop_config_XXX.py` scripts in
situ. Running the loop will then engage in MLOOP. 

If you need to stop MLOOP halfway, but still want to find out the best
parameters out of the batch, I wrote a script that pulls the experiment with
the best parameters `analysis/scripts/meta/find_best_mloop_sequences.py`.

### Simple Use Case Tutorial

In `scripts/mloop`, run `python mloop_config_....py`. Close and reopen
`optimizations.h5` globals in runmanager, `mloop_config...py` edits them. Activate all the subgroups.
Restart the subprocess for the `mloop_multishot.py`, Kill
`feedback_cavity.py` analysis, it's handled in `mloop_multishot.py`. Turn off
repeat in BLACS. Hit `Run multishot analysis`. Hooray~ You got MLOOP
working!


## Hardware Versioning

The idea for the version number is to separate mutually exclusive hardware
wirings. For example when we use something that was driving the mot now drives
an AOM, we should change version number so as not to run (old AOM) code that
could break our MOT by over-driving it.

Documentation as to what changed shall go into HW_VERSIONING.md

If however we are installing new channels without disconnecting old channels
, then the hardware version shall remain the same, and the git shall account
for improvements and new connections.

#Future Features


### Update MLOOP Configuration Method

To facilitate testing and future usage, we need to improve the horrible
configuration method currently in use by analysislib-mloop. It uses the .ini
file instead of the Python API given by MLOOP.

## MLOOP + Feedback Compatibility

Both MLOOP and Simple Feedback loops rely on using the labscript `remote`
module. Something is going on that prevents the `remote` module being
accessed from multiple scripts. The error manifests as the globals file
getting corrupted(?) and causing runmanager to hang.

## Rabi Pulse Tracker

To help catch unforseen errors, I am going to develop a class that keeps track
of the location of the two-level atoms, to see if there is spurious
rotations, uncalibrated magnetic fields, or stray light beams messing with
our atoms.

## Unit Under Tests Modules

Unit Under Tests are a concept from software development to help catch bugs,
they also help in development by clarifying what it is that you're trying to
build. 

They are error tests that work by specifying what the program is supposed to
do, and what it's output is supposed to be, and checking that the output is
correct.

It can gather statistics to quantify the failure rate.

### What do I do when I do a major change?

Change the git branch number. Change it from `master` to `v2.x`, and `v2.x`
to `v3.x`. This way there's a clear cut divide between massive hardware versions.

Since Lab Changes are almost always minor by design, and in an effort to
maintain backward compatibility, I doubt anyone will ever actually need to
increment the number.





.. include:: ./BUGS.md