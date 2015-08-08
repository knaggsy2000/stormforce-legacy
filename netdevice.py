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


import socket
from StringIO import *
import threading

class DataIn(object):
	def Handler(self, data, ignorechecksum, fire):
		datain = StringIO(str(data))
		
		for line in datain.readlines():
			line = line.replace("\r", "").replace("\n", "")
			
			
			# Validate checksum
			valid = False
			
			if ignorechecksum == False:
				valid = validatesentencechecksum(line)
				
			else:
				valid = True
			
			
			if valid == True:
				threading.Thread(target = fire, args = (line,)).start()
	
class NetDevice(object):
	def __init__(self, hostname, port, ttl, buffer_size, conn_type, compression, sentencesub, ignorechecksum):
		self.fire = sentencesub
		self.ignorechecksum = ignorechecksum
		self.buffer_size = buffer_size
		self.hostname = hostname
		self.port = port
		self.conn_type = conn_type
		self.compression = compression
		self.ttl = ttl
		
		
		if conn_type == 0:
			# TCP
			self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.skt.connect((hostname, port))
			
		elif conn_type == 1:
			# UDP
			self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.skt.connect((hostname, port))
			
		elif conn_type == 2:
			# Multicast
			self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			
			try:
				self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
				
			except AttributeError:
				# Some systems don't support SO_REUSEPORT, not sure which...
				pass
			
			self.skt.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, ttl)
			self.skt.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
			
			self.skt.bind(("", port))
			
			self.skt.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(hostname) + socket.inet_aton("0.0.0.0"))
			self.skt.setblocking(0)
		
	def dispose(self):
		if self.conn_type == 2:
			self.skt.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(hostname) + socket.inet_aton("0.0.0.0"))
			
		self.skt.close()
		self.skt = None
		
	def reader(self):
		line = ""
		line_completed = False
		line_buffer = ""
		
		
		while self.alive:
			try:
				data = ""
				address = ""
				
				
				if self.conn_type == 0:
					data = self.skt.recv(self.buffer_size)
					
				else:
					data, address = self.skt.recvfrom(self.buffer_size)

				if data:
					datain = DataIn()
					
					if self.compression == "bz2":
						data = bz2.decompress(data)
						
					
					threading.Thread(target = datain.Handler, args = (data, self.ignorechecksum, self.fire,)).start()
					
				else:
					break
				
			except socket.error, e:
				pass
		
	def readline(self):
		pass
		
	def whoami(self):
		return "NET"
		
	def writer(self, text):
		if self.compression == "bz2":
			text = bz2.compress(text)
			
		
		if self.conn_type == 0:
			self.skt.sendall(text)
			
		else:
			self.skt.sendto(text, (self.hostname, self.port))
		
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
	