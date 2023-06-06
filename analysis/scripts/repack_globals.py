'''
	Repacks globals to prevent MLOOP bloat.
'''
def repack_globals(list_of_globals_filenames):
	import os
	print("Repacking globals...")
	for filename in list_of_globals_filenames:
		try:
			#variables for repacking the globals file
			userProfile      	= "C:\\Users\\YbClockReloaded"
			globals_file     	= os.path.join(userProfile,f"labscript-suite\\userlib\\labscriptlib\\ybclock\\{filename}.h5")
			hdf5repack_file  	= os.path.join(userProfile,r"labscript-suite\userlib\labscriptlib\ybclock\feedback\h5repack.exe")
			temp_globals_file	= os.path.join(userProfile,r"labscript-suite\userlib\labscriptlib\ybclock\temp_globals.h5")

			if os.path.exists(temp_globals_file):
				os.remove(temp_globals_file)
				
			#repack the globals
			print(f"Repacking Globals... {filename}....",end="")
			os.rename(globals_file, temp_globals_file)
			os.system(f'{hdf5repack_file} {temp_globals_file} {globals_file}')
			os.remove(temp_globals_file)
			print("Done!")
		except:
			import traceback
			import sys
			traceback.print_exception(*sys.exc_info())

def main():
	repack_globals(
		[
			"globals",
			"cavity_globals",
			"optimization",
			"working_globals"
		]
	)
if __name__ == '__main__':
	main()