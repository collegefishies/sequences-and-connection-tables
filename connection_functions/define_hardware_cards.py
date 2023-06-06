from labscript_devices.NI_DAQmx.labscript_devices import NI_PCI_6723, NI_PCI_6713, NI_PCI_6284
from labscript_devices.PineBlaster import PineBlaster
from labscript_devices.PrawnBlaster.labscript_devices import PrawnBlaster
from user_devices.P7888.labscript_devices import P7888
from user_devices.AnalogIMAQdxCamera.labscript_devices import AnalogIMAQdxCamera
from user_devices.HP8648.labscript_devices import HP8648
from user_devices.AnalogInputReader.labscript_devices import AnalogInputReader
from labscriptlib.ybclock.connection_functions  import camera_settings
from user_devices.FPGA_DDS.labscript_devices import FPGA_DDS
'''
Here we define the hardware cards and cameras.
'''
kHz = 1e3
GEN = 'PrawnBlaster'
def define_hardware_cards():
	'''
		We define cards in order of connection.
		The PseudoClock drives the digital card which in turn triggers the
		secondary pseudoclock 'analog_clock', which in turn drives the analog
		or secondary NI cards.
		
	'''
	print("\tDefining Pseudoclocks, NI Cards, P7888...",end='')
	### Pseudo Clock
	if GEN == 'PineBlaster':
		PineBlaster(
			name              	= 'digital_clock',
			trigger_device    	= None,
			trigger_connection	= None,
			usbport           	= 'COM9'
		)
	elif GEN == 'PrawnBlaster':
		PrawnBlaster(
			name = 'digital_clock',
			com_port = 'COM8',
			num_pseudoclocks = 1,
			trigger_device = None,
			trigger_connection = None,
			out_pins = [9,11,13],
			in_pins = [1, 2, 4]
		)
		digital_clock.clockline = digital_clock._clocklines[0]

	### Acquisition
	P7888( #photon counting card
		name	= 'photon_counter'
	)

	
	
	### NI Cards
	NI_PCI_6284( #digital card
		#serial number 018E2C2F
		name            	= 'ni_pci_6284_dev2',
		parent_device   	= digital_clock.clockline,
		clock_terminal  	= 'PFI1',
		MAX_name        	= 'Dev2',
		acquisition_rate	= 1e3,
		# max_AO_sample_rate  = 100*kHz,
		# max_DO_sample_rate	= 100*kHz,
	)
	
	### Secondary Pseudoclock
	if GEN == 'PineBlaster':
		PineBlaster(
			name              	= 'analog_clock',
			trigger_device    	= ni_pci_6284_dev2,
			trigger_connection	= 'port0/line0',
			usbport           	= 'COM10'
		)
	elif GEN == 'PrawnBlaster':
		PineBlaster(
			name              	= 'analog_clock',
			trigger_device    	= ni_pci_6284_dev2,
			trigger_connection	= 'port0/line0',
			usbport           	= 'COM10'
		)

	FPGA_DDS(
		name         		= 'FPGA_DDS9',
		parent_device		= ni_pci_6284_dev2,
		connection   		= 'port0/line3',
		usbport      		= 'COM12'
	)

	### Secondary NI Cards
	NI_PCI_6713( #analog out
		#serial number 0163784A
		name          	= 'ni_pci_6713_dev4',
		parent_device 	= analog_clock.clockline,
		clock_terminal	= 'PFI2',
		MAX_name      	='Dev4',
		# max_AO_sample_rate  = 100*kHz,
		# max_DO_sample_rate	= 100*kHz,
	)

	NI_PCI_6723( #analog out
		#serial number 0165ED7E
		name          	= 'ni_pci_6723_dev3',
		parent_device 	= analog_clock.clockline,
		clock_terminal	= 'PFI2',
		MAX_name      	='Dev3',
		max_AO_sample_rate  = 300*kHz,
		max_DO_sample_rate	= 300*kHz,

	)

	NI_PCI_6713( #analog out
		#serial number: 0166BD67
		name          	= 'ni_pci_6713_dev1',
		parent_device 	= analog_clock.clockline,
		clock_terminal	= 'PFI2',
		MAX_name      	='Dev1',
		# max_AO_sample_rate  = 100*kHz,
		# max_DO_sample_rate	= 100*kHz,

	)

	print('Done!')

	### Cameras
	print("\tDefining Cameras...",end='')
	AnalogIMAQdxCamera(
		name                         	= 'wide_angle_cam',
		parent_device                	= ni_pci_6713_dev4,
		connection                   	= 'ao3',
		serial_number                	= '6BE00895F',
		voltage                      	= 8,
		trigger_edge_type            	= 'falling',
		camera_attributes            	= camera_settings.seq_camera_attributes,
		manual_mode_camera_attributes	= camera_settings.manual_camera_attributes
	)

	AnalogIMAQdxCamera(
		name                         	= 'isometric_cam',	#See `isometric video game graphics`
		parent_device                	= ni_pci_6713_dev4,
		connection                   	= 'ao2',
		serial_number                	= '6BE008960',
		voltage                      	= 8,
		trigger_edge_type            	= 'falling',
		camera_attributes            	= camera_settings.seq_camera_attributes,
		manual_mode_camera_attributes	= camera_settings.manual_camera_attributes
	)
	print("Done!")

	# ### Synthesizers

	print("\tDefining HP Synthesizers...",end="")
	HP8648(
		name        	= 'HP8648Cfor759',
		gpib_address	= 'GPIB0::18::INSTR'
	)

	HP8648(
		name        	= 'HP8648B',
		gpib_address	= 'GPIB0::7::INSTR'
	)

	## Analog Input Reader
	print("\tAdding AnalogInputReader...",end='')
	# AnalogInputReader(
	#   	name    	= 'Light_Monitor', 
	#   	channels	= {
	#   	        	'Green Probe Monitor'      		: 'Dev2/ai5',
	#   	        	'556_nm_ultrastable_cavity'		: 'Dev2/ai0',
	#   	        	'759nm_reference_cavity'   		: 'Dev2/ai2',
	#   	        	'759nm_exp_cavity'         		: 'Dev2/ai3',
	#   	        	'759nm_Lattice_Input'      		: 'Dev2/ai4',
	#   	        	'Cooling Pi Power Monitor' 		: 'Dev2/ai6',
	#  #	        	'1157nm_ultrastable_cavity'		: 'Dev2/ai7'
	#   	}
	# )
	print("Done!")
