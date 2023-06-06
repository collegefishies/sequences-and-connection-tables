#Write in comments what I want to do...
#It's useful to do this in the docstring (vvvvv).
'''
	green_mot_distance --- Calculates the green mot distance from the mirror.

		# How it works
		* Pulls image from the HDF file.
		* Substract the background image from direct image.
		* Define region for direct image
		* Find the maximum intensity in pixel in x and z directions to normalized intensity.
		* Same two steps above for the reflected image.
		* Optional: Extra processing for cropping out bits of direct image that could pollute the reflected image.
		* Gaussian fit to find the distance between direct and reflected image.
		* The distance from MOT-Mirror equals (Direct Image - Reflected Image)/2.
		* Return and Display important parameters: z, x, y positions; MOT intensity (brightness).
		* These parameters need to be save also in the "log.txt" file.    

'''
from lyse import *
#Add in libraries for working with HDF files
import labscript_utils.h5_lock
import h5py
#analysis libs

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
# from uncertainties import ufloat, unumpy

def cast_image(array):
	return np.array(array, dtype=int)

def main():
	run = Run(path)

	#extract loaded mot and bg image
	green_mot	= cast_image(run.get_image('isometric_cam','green_mot','almost_loaded'))
	green_mot_bg = cast_image(run.get_image('isometric_cam','green_mot','bg'))

	#print(type(green_mot))
	img = Image.fromarray(green_mot)
	plt.imshow(img)


if __name__ == '__main__':
	try:
		main()
	except:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
