#########################################################################
# Copyright/License Notice (Modified BSD License)                       #
#########################################################################
#########################################################################
# Copyright (c) 2008, Daniel Knaggs                                     #
# All rights reserved.                                                  #
#                                                                       #
# Redistribution and use in source and binary forms, with or without    #
# modification, are permitted provided that the following conditions    #
# are met: -                                                            #
#                                                                       #
#   * Redistributions of source code must retain the above copyright    #
#     notice, this list of conditions and the following disclaimer.     #
#                                                                       #
#   * Redistributions in binary form must reproduce the above copyright #
#     notice, this list of conditions and the following disclaimer in   #
#     the documentation and/or other materials provided with the        #
#     distribution.                                                     #
#                                                                       #
#   * Neither the name of the author nor the names of its contributors  #
#     may be used to endorse or promote products derived from this      #
#     software without specific prior written permission.               #
#                                                                       #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS   #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT     #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT  #
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT      #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT   #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  #
#########################################################################


import serial
import threading

class GPSDevice(object):
	def __init__(self, port, speed, bits, parity, stop, timeout, sentencesub, ignorechecksum):
		self.fire = sentencesub
		self.ignorechecksum = ignorechecksum
		
		
		self.ser = serial.Serial()
		self.ser.baudrate = speed
		self.ser.bytesize = bits
		self.ser.parity = parity
		self.ser.port = port
		self.ser.stopbits = stop
		self.ser.timeout = timeout
		
		self.ser.open()
		
	def dispose(self):
		self.ser.close()
		self.ser = None
		
	def reader(self):
		line = ""
		
		
		while self.alive:
			try:
				line = self.readline().replace("\r", "").replace("\n", "")
				
				# Validate checksum
				valid = False
				
				if self.ignorechecksum == False:
					valid = validatesentencechecksum(line)
					
				else:
					valid = True
				
				
				if valid == True:
					threading.Thread(target = self.fire, args = (line,)).start()
					
					line = ""
			except:
				pass
				
	def readline(self):
		return self.ser.readline().replace("\r", "").replace("\n", "")
	
	def whoami(self):
		return "GPS"
		
	def writer(self, text):
		self.ser.write(text)
		
	def start(self):
		self.alive = True
		
		self.monitoring_thread = threading.Thread(target = self.reader)
		self.monitoring_thread.setDaemon(1)
		self.monitoring_thread.start()
	
	def stop(self):
		self.alive = False
		
def validatesentencechecksum(strsentence):
	s = 0
	
	for i in range(len(strsentence)):
		if strsentence[i] == "$":
			pass
		
		elif strsentence[i] == "*":
			break
			
		else:
			s = s ^ ord(strsentence[i])
		
	checksum = ""
	
	s = "%02X" % s
	checksum += s
	
	# Split the checksum from the sentence and compare
	split_sen = strsentence.split("*")
	
	if len(split_sen) == 2:
		if checksum == split_sen[1]:
			return True
		
		else:
			return False
		
	else:
		return False
	