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


import bz2
import socket
from StringIO import *
import threading

class DataIn(object):
	def Handler(self, data, fire):
		# It appears that we can get several XML "files" in the data (maybe due to the threading), so we need to handle that
		line_buffer = ""
		
		datain = StringIO(str(data))
		
		for line in datain.readlines():
			line = line.replace("\r", "").replace("\n", "")
			
			if line <> "":
				if line_buffer == "":
					line_buffer = line
					
				else:
					line_buffer = "%s\n%s" % (line_buffer, line)
				
			if line.startswith("</StormForce>") == True:
				if line_buffer.endswith("\n") == False:
					line_buffer = line_buffer + "\n"
					
				threading.Thread(target = fire, args = (line_buffer,)).start()
				
				line_buffer = ""
	
class XMLDevice(object):
	def __init__(self, hostname, port, ttl, buffer_size, conn_type, compression, sentencesub, ignorechecksum):
		self.fire = sentencesub
		self.ignorechecksum = ignorechecksum
		self.buffer_size = buffer_size
		self.hostname = hostname
		self.port = port
		self.ttl = ttl
		self.conn_type = conn_type
		self.compression = compression
		
		
		if self.conn_type == 0:
			# TCP
			self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.skt.connect((hostname, port))
			
		elif self.conn_type == 1:
			# UDP
			self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			
		elif self.conn_type == 2:
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
		self.skt.close()
		self.skt = None
		
	def reader(self):
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
						
					
					threading.Thread(target = datain.Handler, args = (data, self.fire,)).start()
					
				else:
					break
				
			except socket.error, e:
				pass
		
	def readline(self):
		pass
		
	def whoami(self):
		return "XML"
		
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
		
	