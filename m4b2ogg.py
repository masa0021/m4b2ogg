#!/usr/bin/env python

#***************************************************************************
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#***************************************************************************
#    Written by Robert Penz <robert@penz.name>
#	Extended by Marco Salm <m.salm@lusi.uni-sb.de>



# Changelog:
# * Code written by Robert Penz <robert@penz.name>
# * Option for ogg quality and number of threads by M. Salm
# * Job-Queue and threading by M. Salm
# * Optparse by M. Salm


import sys
import os
import getopt
import subprocess
import threading
import Queue
import optparse

global JobPool
global Version
JobPool  = Queue.Queue() 
Version  = "0.1.0"

#### PARAMETER CLASS ####
class parameters:
	def __init__(self,workingDir, overwriteOggs, removeM4b, oggQuality, numthreads):
		self.workingDir = workingDir
		self.overwriteOggs = overwriteOggs 
		self.removeM4b = removeM4b
		self.oggQuality = oggQuality
		self.numthreads = numthreads
#### END OF PARAMETER CLASS ####



#### CREATE JOB QUEUE ####
def createQueue(par):
	global JobPool
	for root, dirs, files in os.walk(par.workingDir):
		for name in files:
			if os.path.splitext(name)[1].lower() == ".m4b":
				JobPool.put(['execute',root,name, par])
#### END OF CREATE JOB QUEUE ####




#### WORKQUEUE ####
def workQueue(par):
	for x in range(par.numthreads):
		jobThread().start()
#### END OF WORKQUEUE ####





#### JOBTHREAD ####
# Job Threading class
class jobThread ( threading.Thread ):
	def run ( self ):
		global JobPool
		while JobPool.qsize():
			status,root,name,par = JobPool.get()
			pathM4b = os.path.join(root, name)
			if status != "stop":
				pathOgg = os.path.splitext(pathM4b)[0] + ".ogg"
				if not par.overwriteOggs and os.path.exists(pathOgg):
					print "Info: %s already exists" % pathOgg[len(par.workingDir):]
					return

				print "converting: ",pathM4b[len(par.workingDir):]
   	
				p1 = subprocess.Popen(["faad", "-q", "-o", "-", pathM4b], stdout=subprocess.PIPE)
				p2 = subprocess.Popen(["oggenc", "-Q", "-q",par.oggQuality, "-", "-o", pathOgg], stdin=p1.stdout, stdout=subprocess.PIPE)

				output = p2.communicate()

				if output[0] or output[1]:
					print "error converting %s" % pathM4b[len(par.workingDir):]
					print output[0]
					print output[1]
					return
				else:
					if par.removeM4b:
						os.unlink(pathM4b)
				print pathM4b,status
#### END OF JOBTHREAD ####




#### MAIN ####
# Main program: parse command line and start processing
def main():
	par = parameters("", "false", "false", "6", 1)
	workingDir = os.getcwd()
	
	parser = optparse.OptionParser()

	parser.add_option('-d','--directory', dest="workingDir", default=workingDir, metavar="workingDir",
			help="Working directory [./]")
	parser.add_option('-q','--quality', dest="oggQuality", default="6", metavar="oggQuality",
			help="Ogg quality [6]")
	parser.add_option('-n','--threads', dest="numthreads", default=1, metavar="numthreads",
			type="int", help="Number of threads [1]")
	parser.add_option('-o', action="store_true", dest="overwriteOggs", default=False,
			help="Shall existing oggs be overwrite?")
	parser.add_option('-r', action="store_true", dest="removeM4b", default=False,
			help="Shall the M4bs be deleting?")
	parser.add_option('-v','--version', action="store_true", dest="version", default=False,
			help="Show the version")


	(options,args)    = parser.parse_args()
	par.workingDir    = options.workingDir
	par.oggQuality    = options.oggQuality
	par.numthreads    = options.numthreads
	par.overwriteOggs = options.overwriteOggs
	par.removeM4b     = options.removeM4b

	if options.version:
		print "m4b2ogg.py: Version ",Version

	if par.workingDir[-1] != "/":
		par.workingDir += "/"
	
	if not par.workingDir:
		par.workingDir = ""	

	createQueue(par)
	workQueue(par)
#### END OF MAIN ####


if __name__ == '__main__':
	main()
