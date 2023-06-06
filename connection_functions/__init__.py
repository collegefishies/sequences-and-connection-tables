"""
	Holds the functions for defining the hardware cards
	and channels of the experiment.

	## Implementation

	This folder appears as a module via the use of the 
	`__init__.py` file held inside of it. Through the use of explicit import calls
	, we can import functions held inside each of the subfiles without worrying
	about how they are named. This allows us to spread, what would otherwise be
	very long single file scripts, into many files that are easier to look 
	through.


"""

print("Importing connection functions...", end ='')
from .define_hardware_cards import *
from .define_channels import *
print("Done!")
