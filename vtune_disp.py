# import sys
# program_name = sys.argv[0]

class color_font:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

import sys
import os.path
from os import path
import subprocess

program_name = sys.argv[0]
arguments_cmd = sys.argv[1]

arguments = arguments_cmd.rstrip(".pwr")

path = "runs/vtune_socwatch_demo/"+arguments

arg_1 = "runs/pwr/"+arguments+".pwr"
arg_2 = path+"/"+arguments+".amplxe"


#Debug statements; uncomment this if you want to debug the script
# print "program_name = %s" %program_name
# print "arguments_cmd = %s" %arguments_cmd
# print "arguments = %s" %arguments
# print "path = %s" %path
# print "arg_1 = %s" %arg_1
# print "arg_2 = %s" %arg_2
# print(os.path.exists(arg_1))
# print(os.path.exists(path))



if (not(os.path.isfile(arg_1))):
	print (color_font.RED+color_font.BOLD+arguments_cmd+" file doesn't exist; please generate the .PWR file first before importing it in VTune GUI"+color_font.END)

else:

	if (os.path.exists(path)):
		print ("Opening existing VTune report for "+ color_font.BOLD + arguments_cmd + color_font.END + " file")	
		print ("Ignore the below DispatchAsyncMessage errors")
		subprocess.call("amplxe-gui "+arg_2)
		

	else:
		print (color_font.GREEN+color_font.BOLD+"Created a new report in the "+path+" directory"+color_font.END)
		print (color_font.GREEN+color_font.BOLD+"Ignore the below DispatchAsyncMessage errors"+color_font.END)
		subprocess.call("amplxe-cl -import "+arg_1+" -result-dir "+path)
		subprocess.call("amplxe-gui "+arg_2)