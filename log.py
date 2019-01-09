#!/usr/bin/python
from __future__ import division
from subprocess import PIPE, Popen
import psutil
from datetime import datetime
import time
import os

def get_gpu_temperature():
	process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
	output, _error = process.communicate()
	#print('GPU temp:: ',output)
	return float(output[output.index('=') + 1:output.rindex("'")])
	
def get_cpu_temperature():
	process = Popen(['cat', '/sys/class/thermal/thermal_zone0/temp'], stdout=PIPE)
	output, _error = process.communicate()
	#print('CPU temp:: ',output)
	return round(float(int(output[0:4]) /int(100)),1)
	
def get_current_cpu_freq():
	process = Popen(['cat', '/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq'], stdout=PIPE)
	output, _error = process.communicate()
	#print('CPU freq:: ', output[0:output.rindex("\n")])	
	return output[0:output.rindex("\n")]
	
def get_throttle_status():
	#1010000000000000101  <- 19 bits  rpi 3b+
	#|||             |||_ under-voltage
	#|||             ||_ currently throttled
	#|||             |_ arm frequency capped
	#|||_ under-voltage has occurred since last reboot
	#||_ throttling has occurred since last reboot
	#|_ arm frequency capped has occurred since last reboot

	process = Popen(['vcgencmd', 'get_throttled'], stdout=PIPE)
	output, _error = process.communicate()
	output_string = (output[output.index('=') + 1:output.rindex("\n")])
	bin(int(output_string,16))[2:]
	#print('Throttled:: ', output_string)
	#print('Throttled:: ', bin(int(output_string,16))[2:])	
	return bin(int(output_string,16))[2:]
	
def get_vcore():	  
	process = Popen(['vcgencmd', 'measure_volts'], stdout=PIPE)
	output, _error = process.communicate()
	#print('Vcore:: ', float(output[output.index('=') + 1:output.rindex("V")]))	
	return float(output[output.index('=') + 1:output.rindex("V")])
	
def get_time_now():	
	return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	
def get_date_now():	
	return datetime.now().strftime('%Y-%m-%d')
	
def get_journal():
	cmd = 'sudo journalctl > ~/Desktop/Logs/Jounal_Log' + '__' + get_date_now() + '.txt'
	os.system(cmd)
	return

def main(logFile):
	time_now = get_time_now()
	gpu_temperature = get_gpu_temperature()
	cpu_temperature = get_cpu_temperature()
	cpu_usage = psutil.cpu_percent()
	cpu_freq = get_current_cpu_freq()
	cpu_vcore = get_vcore()
	throttled = get_throttle_status()
	#print('Time now: ',time_now)
	#print('GPU temp: ',gpu_temperature)
	#print('CPU temp: ',cpu_temperature)
	#print('CPU usuage: ',cpu_usage)
	#print('CPU freq: ',cpu_freq)
	#print('CPU vcore: ',cpu_vcore)
	#print('Throttled: ',throttled)
    
	ram = psutil.virtual_memory()
	#ram_total = ram.total / 2**20       # MiB.
	#ram_used = ram.used / 2**20
	#ram_free = ram.free / 2**20
	ram_percent_used = ram.percent
	#print('RAM %:',ram_percent_used)
    
	#disk = psutil.disk_usage('/')
	#disk_total = disk.total / 2**30     # GiB.
	#disk_used = disk.used / 2**30
	#disk_free = disk.free / 2**30
	#disk_percent_used = disk.percent
	#print('Disk %:',disk_percent_used)
	
	logFile.write(str(time_now) + ',' + str(throttled) + ',' +  
	str(ram_percent_used) + ',' +  str(gpu_temperature) + ',' +  
	str(cpu_temperature) + ',' + str(cpu_usage) + ',' +  
	str(cpu_freq) + ',' +  str(cpu_vcore) + '\n')
	
	print(str(time_now) + ',  ' + str(throttled) + ',  ' +  
	str(ram_percent_used) + '%,  ' +  str(gpu_temperature) + 'C,  ' +  
	str(cpu_temperature) + 'C,  ' + str(cpu_usage) + '%,  ' +  
	str(cpu_freq) + 'Hz,  ' +  str(cpu_vcore) + 'V')
	return


if __name__ == '__main__':
	logName = ".//Logs/" + "Throttle_Log" + "__" + get_date_now();
	
	if (not os.path.isfile(logName + ".txt")):	
		logFile = open(logName + ".txt","a")
		
		logFile.write('Time'  + ',' +  'Throttled Status' + ',' +  
		'RAM Usuage (%)' + ',' +  'GPU Temp (C)' + ',' +  
		'CPU Temp (C)' + ',' + 'CPU Usuage (%)' + ',' +  
		'CPU Freq (Hz)' + ',' +  'CPU Vcore (V)' + '\n')
		logFile.close()
	
	print('Time'  + ',  ' +  'Throttled Status' + ',  ' +  
	'RAM Usuage' + ',  ' +  'GPU Temp' + ',  ' +  
	'CPU Temp' + ',  ' + 'CPU Usuage' + ',  ' +  
	'CPU Freq' + ',  ' +  'CPU Vcore')
	
	i = 0
	
	while(1):
		logFile = open(logName + ".txt","a")
		main(logFile)
		logFile.close()
		
		if (i > 1):
			get_journal()
			i = 0
		else:
			i += 1
		time.sleep(60)
	#print("Here")
	#logFile.close()









