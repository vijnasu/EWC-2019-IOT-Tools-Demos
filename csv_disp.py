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

import csv
import sys
import os.path
from os import path

arguments_cmd = sys.argv[1]

arguments = "runs/pwr/"+arguments_cmd

if (not(os.path.isfile(arguments))):
	print (color_font.RED+color_font.BOLD+arguments_cmd+" file doesn't exist; please generate the .CSV file first before importing it"+color_font.END)

else:
	with open(arguments, 'r') as csvfile:
		reader = csv.reader(csvfile)
	 
		for row in reader:
			print(row)
