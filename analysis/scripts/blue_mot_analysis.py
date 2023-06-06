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

if __name__ == '__main__':

	#get data
	run = Run(path)
	#extract blue mot images
	try:
		#extract loaded mot and bg image
		blue_mot	= cast_image(run.get_image('wide_angle_cam','blue_mot','atoms'))
		blue_mot_bg = cast_image(run.get_image('wide_angle_cam','blue_mot','bg'))

		#crop the image
		print("Cropping Image")
		crop_area = box(left=50,right=250,top=25,bottom=200)
		cropped_blue_mot   	= crop_array(blue_mot,crop_area)
		cropped_blue_mot_bg	= 0*crop_array(blue_mot_bg, crop_area)
		cropped_blue_mot_signal = np.absolute(cropped_blue_mot)
		var_atoms_noise = cropped_blue_mot.sum()
		var_bg_noise = 0
		var_signal_noise = 0

		print("Shot Noise (Std of Pixel Strength):")
		print(f"\tBG	= {var_bg_noise}")

		#integrate the cropped image and rescale to get the mot fluorescence
		integrated_blue_mot = (cropped_blue_mot_signal.sum())
		integrated_blue_mot_bg = (cropped_blue_mot_bg.sum())

		plt.imshow(cropped_blue_mot_signal)
		plt.title(f'blue_mot\nsum={ufloat(integrated_blue_mot,var_signal_noise):.2eP} Pixels')
		run.save_result(name="blue_mot_light",value=integrated_blue_mot)
		run.save_result(name="blue_mot_light_err",value=var_signal_noise)
		run.save_result(name="blue_mot_SNR", value=integrated_blue_mot)
	except Exception as e:
		print(e)
