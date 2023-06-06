'''
	Plots Images of the MOT for debugging.
'''
from lyse import *
#Add in libraries for working with HDF files
import labscript_utils.h5_lock
import h5py
#analysis libs
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from uncertainties import ufloat, unumpy


def cast_image(array):
	return np.array(array, dtype=int)

def box(left,right,top,bottom):
	return (left,top,right,bottom)
def crop_array(array,box):
	return array[box[1]:box[3],box[0]:box[2]]


#x offset to the crop region
xo = 40
#right side reduction
rr = -30
if __name__ == '__main__':

	#get data
	run = Run(path)
	#extract blue mot images
	try:
		#extract loaded mot and bg image
		green_mot	= cast_image(run.get_image('isometric_cam','green_mot','almost_loaded'))
		green_mot_bg = cast_image(run.get_image('isometric_cam','green_mot','bg'))

		#crop the image
		print("Cropping Image")
		crop_area = box(left=280+xo,right=345+xo+rr,top=190,bottom=230)
		cropped_green_mot   	= crop_array(green_mot,crop_area)
		cropped_green_mot_bg	= crop_array(green_mot_bg, crop_area)
		cropped_green_mot_signal = np.absolute(cropped_green_mot-0*cropped_green_mot_bg)
		var_atoms_noise = cropped_green_mot.sum()
		var_bg_noise = cropped_green_mot_bg.sum()
		var_signal_noise = var_bg_noise

		print("Shot Noise (Std of Pixel Strength):")
		print(f"\tBG	= {var_bg_noise}")

		#integrate the cropped image and rescale to get the mot fluorescence
		integrated_green_mot = (cropped_green_mot_signal.sum())
		integrated_green_mot_bg = (cropped_green_mot_bg.sum())

		plt.imshow(cropped_green_mot_signal)
		plt.title(f'green_mot\nsum={ufloat(integrated_green_mot,var_signal_noise):.2eP} Pixels')
		run.save_result(name="green_mot_light",value=integrated_green_mot)
		run.save_result(name="green_mot_light_err",value=var_signal_noise)
		run.save_result(name="green_mot_SNR", value=integrated_green_mot/var_signal_noise)
	except Exception as e:
		print(e)
