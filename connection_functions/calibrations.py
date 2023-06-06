'''
## Technical Details
The technical details of how calibrations are implemented is in Philip Thomas Starkey's Thesis. Section 5.1.9.

## As of Labscript v3.0.0
The calibration classes must all live within the
`labscript_utils.unitconversions` module so that they are importable by the
labscript suite. The calibration class name (and parameters) are stored in the
connection table so that BLACS can instantiate the unit conversion class. This
allows BLACS to provide manual control of each channel in physical units as
well.

As of 3/24/2021, that location is `C:\\Users\\Boris\\Anaconda3\\envs\\ybclock\\Lib\\site-packages\\labscript_utils\\unitconversions`
'''