#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Copyright/License Notice (Modified BSD License)                       #
#########################################################################
#########################################################################
# Copyright (c) 2008-2010, Daniel Knaggs                                #
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
#   * This Software is not to be used for safety purposes.              #
#                                                                       #
#   * You agree and abide the Disclaimer for your Boltek LD-250.        #
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


###################################################
# StormForce (Danny's Lightning Detection System) #
###################################################
# Version:     v0.6.0                             #
###################################################
mysql_available = False
psyco_available = False

try:
	import MySQLdb
	
	mysql_available = True
	
except ImportError, e:
	mysql_available = False
	
	
try:
	import psyco
	
	psyco.full()
	psyco_available = True
	
except ImportError, e:
	psyco_available = False
	
	


import bz2
from datetime import *
import getopt
from gpsdevice import GPSDevice
from math import *
from netdevice import NetDevice
from os import *
import pygame
from pygame.locals import *
import pylzma
import random
import sha
import signal
import socket
from StringIO import *
import sys
import threading
import time
from xml.dom import minidom
from xmldevice import XMLDevice
import zlib


# Globals
alarm_font = None

background = None
blitzortung_enabled = False
blitzortung_gps_latitude = 0.
blitzortung_gps_longitude = 0.
blitzortung_hostname = "blitzortung.org"
blitzortung_loop = False
blitzortung_password = ""
blitzortung_port = 8309 # This has been reserved by blitzortung.org just for StormForce, thanks Egon!
blitzortung_queue = []
blitzortung_unit = 0
blitzortung_username = ""

captured_file = ""
close_alarm_arguments = ""
cronalive = True
cronblitzortungthread = None
cronthread = None
cronuptimethread = None
cur = None
curl_arguments = ""

database_engine = 0
debug_mode = False
demo_mode = False

efmunit = None
efmunit_port = ""
efmunit_port_compression = ""
efmunit_port_type = ""

fullscreen = False

gpsunit = None
gpsunit_port = ""
gpsunit_port_type = ""
gpsunit_port_compression = ""

ldunit = None
ldunit_close_alarm_last_state = False
ldunit_close_minute = 0
ldunit_close_total = 0
ldunit_noise_minute = 0
ldunit_noise_total = 0
ldunit_port = "/dev/cuad0"
ldunit_port_compression = ""
ldunit_port_type = ""
ldunit_severe_alarm_last_state = False
ldunit_skew_amount = 0.
ldunit_squelch = 0
ldunit_strikes_minute = 0
ldunit_strikes_oor = 0
ldunit_strikes_total = 0
ldunit_uus = False
listener_backlog = 10
listener_multicast_address = ""
listener_multicast_port = 0
listener_multicast_port_compression = ""
listener_multicast_ttl = 0
listener_size = 262144 # 131072 is the lowest we can use, so we'll double it and use that!
listener_tcp = None
listener_tcp_alive = False
listener_tcp_auth = []
listener_tcp_port = 0
listener_tcp_port_compression = ""
listener_tcp_thread = None
listener_udp = None
listener_udp_alive = False
listener_udp_auth = []
listener_udp_port = 0
listener_udp_port_compression = ""
listener_udp_thread = None

mysql_server = "127.0.0.1"
mysql_database = "stormforce"
mysql_username = "stormforce"
mysql_password = ""

number_font = None

reconstruction_file = ""
rotated = False
running = True

screen = None
server_address = ""
server_mode = False
severe_alarm_arguments = ""
show_crosshair = True
show_range_circles = False
show_red_dot = False
small_crosshair = True
small_number_font = None
sound_enabled = True
square_font = None
ssbt_enabled = False
strike_shape = 0
stunit = None
stunit_close_minute = 0
stunit_close_total = 0
stunit_noise_minute = 0
stunit_noise_total = 0
stunit_port = ""
stunit_port_compression = ""
stunit_port_type = ""
stunit_skew_amount = 0.
stunit_squelch = 0
stunit_strikes_minute = 0
stunit_strikes_oor = 0
stunit_strikes_total = 0
stunit_uus = False

time_font = None
trac_active = False
trac_enabled = True
trac_most_active = ""
trac_storms_total = 0

upload_enabled = False
uptime = 0
uptime_font = None

zoom_distance = 300
zoom_multiplier = 1.


# Constants
CENTRE_X = 300
CENTRE_Y = 300
CLOSE_DISTANCE_ALARM = 15
CLOSE_SOUND = path.join("ogg", "kde_digital2.ogg")
CLOSE_TEXT_COLOUR = [255, 0, 0]
COLOUR_ALARM_ACTIVE = [255, 0, 0]
COLOUR_ALARM_INACTIVE = [0, 255, 0]
COLOUR_BLACK = [0, 0, 0]
COLOUR_CROSSHAIR = [245, 245, 90]
COLOUR_NEW_STRIKE = [252, 252, 252]
COLOUR_OLD_STRIKE_1 = [255, 255, 0]
COLOUR_OLD_STRIKE_2 = [210, 180, 0]
COLOUR_OLD_STRIKE_3 = [200, 100, 0]
COLOUR_OLD_STRIKE_4 = [180, 50, 0]
COLOUR_OLD_STRIKE_5 = [150, 25, 0]
COLOUR_RANGE_25 = [146, 146, 146]
COLOUR_RANGE_50 = [146, 146, 146]
COLOUR_RANGE_100 = [146, 146, 146]
COLOUR_RANGE_150 = [146, 146, 146]
COLOUR_RANGE_200 = [146, 146, 146]
COLOUR_RANGE_250 = [146, 146, 146]
COLOUR_RANGE_300 = [146, 146, 146]
COLOUR_SIDELINE = [255, 255, 255]
COLOUR_WHITE = [255, 255, 255]
COLOUR_YELLOW = [255, 255, 0]
CONVERT = "convert"

DB_MYSQL = 1
DB_NONE = 0
DB_VERSION = 1000

EFM100_FIELD = (605, 116)
EFM100_FIELD_VALUE = (682, 116)
EFM100_HEADER = (605, 96)
EFM100_RECEIVER = (605, 108)
EFM100_RECEIVER_VALUE = (682, 108)
EFM_NEGATIVE = "$-"
EFM_POSITIVE = "$+"

GPS_GPRMC = "$GPRMC"

GPS_BEARING = (764, 172)
GPS_BEARING_VALUE = (818, 172)
GPS_DATETIME = (764, 180)
GPS_DATETIME_VALUE = (818, 180)
GPS_HEADER = (605, 144)
GPS_LAT = (764, 156)
GPS_LAT_VALUE = (818, 156)
GPS_LONG = (764, 164)
GPS_LONG_VALUE = (818, 164)
GPS_RECEIVER = (605, 156)
GPS_RECEIVER_VALUE = (682, 156)


#
# LD key:
#
# <bbb.b> = bearing to strike 0-359.9 degrees
# <ccc>   = close strike rate 0-999 strikes/minute
# <ca>    = close alarm status (0 = inactive, 1 = active)
# <cs>    = checksum
# <cr>    = carriage return
# <ddd>   = corrected strike distance (0-300 miles)
# <hhh.h> = current heading from GPS/compass
# <lf>    = line feed
# <sa>    = severe alarm status (0 = inactive, 1 = active)
# <sss>   = total strike rate 0-999 strikes/minute
# <uuu>   = uncorrected strike distance (0-300 miles)
#
LD_NOISE  = "$WIMLN" # $WIMLN*<cs><cr><lf>
LD_STATUS = "$WIMST" # $WIMST,<ccc>,<sss>,<ca>,<sa>,<hhh.h>*<cs><cr><lf>
LD_STRIKE = "$WIMLI" # $WIMLI,<ddd>,<uuu>,<bbb.b>*<cs><cr><lf>

LD250_CLOSE = (764, 20)
LD250_CLOSE_VALUE = (814, 20)
LD250_CLOSE_ALARM = (605, 20)
LD250_CLOSE_ALARM_VALUE = (682, 20)
LD250_HEADER = (605, 0)
LD250_NOISE = (764, 28)
LD250_NOISE_VALUE = (814, 28)
LD250_RECEIVER = (605, 12)
LD250_RECEIVER_VALUE = (682, 12)
LD250_SEVERE_ALARM = (605, 28)
LD250_SEVERE_ALARM_VALUE = (682, 28)
LD250_SQUELCH = (605, 36)
LD250_SQUELCH_VALUE = (682, 36)
LD250_STRIKES = (764, 12)
LD250_STRIKES_VALUE = (814, 12)

INFO_SIZE = None

MANIFESTO_ELECTION = 0
MANIFESTO_PUBLISHED = 1
MANIFESTO_UNPUBLISHED = 2
MAP = path.join("png", "map-300.png")
MAP_MATRIX_CENTRE = (300, 300) # Can be changed if needed
MAP_MATRIX_SIZE = (600, 600) # Ditto
MAP_SIZE = (600, 600) # DO NOT CHANGE!

NOISE_TEXT_COLOUR = [30, 200, 240]

SCREEN_SIZE = (920, 600)
SF_AUTH = "$SFATH"
SF_SQUELCH = "$SFSQU"
SF_ROTATE = "$SFROT"
SHAPE_CIRCLE = 2
SHAPE_SQUARE = 0
SHAPE_TRIANGLE = 1
SMALL_NUM = 0.000001
SSBT_HEADER = (605, 240)
SSBT_MANIFESTO = (605, 260)
SSBT_MANIFESTO_VALUE = (682, 260)
SSBT_STATUS = (605, 252)
SSBT_STATUS_VALUE = (682, 252)
STPCI_CLOSE = (764, 68)
STPCI_CLOSE_VALUE = (814, 68)
STPCI_HEADER = (605, 48)
STPCI_NOISE = (764, 76)
STPCI_NOISE_VALUE = (814, 76)
STPCI_RECEIVER = (605, 60)
STPCI_RECEIVER_VALUE = (682, 60)
STPCI_SQUELCH = (605, 84)
STPCI_SQUELCH_VALUE = (682, 84)
STPCI_STRIKES = (764, 60)
STPCI_STRIKES_VALUE = (814, 60)
STRIKE_SOUND = path.join("ogg", "kde_click3.ogg")
STRIKE_TEXT_COLOUR = [240, 230, 0]
ST_NOISE  = "$WINLN" # $WINLN*<cs><cr><lf>
ST_STATUS = "$WINST" # $WINST,<ccc>,<sss>,<ca>,<sa>,<hhh.h>*<cs><cr><lf>
ST_STRIKE = "$WINLI" # $WINLI,<ddd>,<uuu>,<bbb.b>,<type>,<polarity>*<cs><cr><lf>

TEMP_IMAGE = "lightning.tga"
TIME_SIZE = (220, 20)
TIME_TEXT = [668, 572]
TIME_TEXT_COLOUR = [0, 200, 36]
TRAC_ACTIVE_SOUND = path.join("ogg", "kde_error2.ogg")
TRAC_COLOUR = [0, 255, 255]
TRAC_COUNT = (740, 202)
TRAC_GRADIENT_MIN = [0, 255, 0]
TRAC_GRADIENT_MAX = TRAC_COLOUR
TRAC_HEADER = (605, 192)
TRAC_MOST_ACTIVE = (605, 220)
TRAC_MOST_ACTIVE_VALUE = (682, 220)
TRAC_REPORT = "TRACReport.txt"
TRAC_SENSITIVITY = 10
TRAC_STATUS = (605, 204)
TRAC_STATUS_VALUE = (682, 204)
TRAC_STORM_WIDTH = 30 # miles
TRAC_STORM_WIDTH_TEXT = (605, 228)
TRAC_STORM_WIDTH_VALUE = (682, 228)
TRAC_STORMS = (605, 212)
TRAC_STORMS_VALUE = (682, 212)
TRAC_VERSION = "0.3.0"

UPTIME_SIZE = (140, 18)
UPTIME_TEXT = [698, 532]
UPTIME_TEXT_COLOUR = [255, 0, 0]

UNIT_SECTION_COLOUR = [255, 200, 0]
USER_COPYRIGHT = "Lightning Data (c) " + str(datetime.now().year) + " - Daniel Knaggs"

VERSION = "0.6.0"

XML_EVENT_EFM = 5
XML_EVENT_GPS = 6
XML_EVENT_LD250_NOISE = 2
XML_EVENT_LD250_SQUELCH = 4
XML_EVENT_LD250_STATUS = 3
XML_EVENT_LD250_STRIKE = 1
XML_EVENT_STPCI_NOISE = 7
XML_EVENT_STPCI_SQUELCH = 10
XML_EVENT_STPCI_STATUS = 8
XML_EVENT_STPCI_STRIKE = 9

XML_EVENT_SENDER_EFM = 3
XML_EVENT_SENDER_GPS = 2
XML_EVENT_SENDER_LD250 = 0
XML_EVENT_SENDER_STORMFORCE = 1

XML_SETTINGS_FILE = "stormforce-settings.xml"
XML_TRAC_REPORT = "TRACReport.xml"


# Updated "constants" - DO NOT CHANGE, USERS CHANGE THE "USER_COPYRIGHT" constant instead!
COPYRIGHT_MESSAGE_1 = "StormForce - v" + VERSION
COPYRIGHT_MESSAGE_2 = "(c) 2008-2010 - Daniel Knaggs"

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24


def blitzortungAddToQueue(blitzortung_unit, strike_distance_corrected, strike_distance, strike_angle, strike_type, strike_polarity):
	global blitzortung_queue
	
	blitzortung_queue.add([blitzortung_unit, strike_distance_corrected, strike_distance, strike_angle, strike_type, strike_polarity])
	
def blitzortungThread():
	global blitzortung_loop, blitzortung_queue
	
	connection_established = None
	
	
	while blitzortung_loop:
		current_queue = blitzortung_queue
		blitzortung_queue = []
		
		if connection_established == None:
			# Setup the connection
			pass
			
		else:
			# How old is the connection?  We must kill it if it's been up for over a minute
			pass
			
		
		# Transmit the strikes that are in the queue
		for item in current_queue:
			# TRANS
			#
			if response <> "OK":
				print "Warning: Didn't get a valid response from Blitzortung - %s." % response
			
		current_queue = []
	
def captureScreen(strfilename):
	global screen
	
	
	pygame.image.save(screen, TEMP_IMAGE)
	
	
	try:
		# Since PyGame only supports a few output formats, we'll use ImageMagick's convert tool to make a PNG (or whatever is defined) instead!
		if not strfilename.lower().endswith(".tga"):
			system("convert " + TEMP_IMAGE + " " + strfilename)
		
		if curl_arguments <> "":
			uploadFileViaCurl(strfilename)
		
	except:
		print "WARNING: Failed to convert the screen capture using ImageMagick."
		
		
	try:
		if path.exists(TEMP_IMAGE):
			unlink(TEMP_IMAGE)
		
	except:
		print "WARNING: Failed to remove the old image file."
	
def cBool(value):
	if str(value).lower() == "false" or str(value) == "0":
		return False
		
	elif str(value).lower() == "true" or str(value) == "1":
		return True
		
	else:
		return False
	
def cXMLToSentence(strxml):
	# Make sure we have XML before parsing in detail
	if strxml.startswith("<?xml version=\"1.0\" ?>"):
		# So we don't duplicate the same subroutines, we'll simply convert the XML to it's original sentence and fire the waitForData() sub
		xmlin = StringIO(strxml)
		xmldoc = minidom.parse(xmlin)
		
		myvars = xmldoc.getElementsByTagName("Notification")
		
		
		sentence = ""
		
		for var in myvars:
			sentence = ""
			
			if "EventID" in var.attributes.keys():
				eventid = int(var.attributes["EventID"].value)
				
				if eventid == XML_EVENT_LD250_STRIKE:
					if instr(ldunit_port, ":"):
						corrected_distance, uncorrected_distance, bearing, striketype, strikepolarity, dateandtime = xmlStormForceParseEventStrike(strxml)
						
						sentence = "%s,%d,%d,%f*FF" % (LD_STRIKE, corrected_distance, uncorrected_distance, bearing)
						waitForLD250Data(sentence)
					
				elif eventid == XML_EVENT_LD250_NOISE:
					if instr(ldunit_port, ":"):
						detected, dateandtime = xmlStormForceParseEventNoise(strxml)
						
						sentence = "%s*FF" % LD_NOISE
						waitForLD250Data(sentence) # For now...
					
				elif eventid == XML_EVENT_LD250_STATUS:
					if instr(ldunit_port, ":"):
						close_rate, total_rate, close_alarm, severe_alarm, heading, dateandtime = xmlStormForceParseEventStatus(strxml)
						
						sentence = "%s,%d,%d,%d,%d,%f*FF" % (LD_STATUS, close_rate, total_rate, close_alarm, severe_alarm, heading)
						waitForLD250Data(sentence)
					
				elif eventid == XML_EVENT_LD250_SQUELCH:
					if instr(ldunit_port, ":"):
						level, dateandtime = xmlStormForceParseEventSquelch(strxml)
						
						sentence = "%s,%d*FF" % (SF_SQUELCH, level)
						waitForLD250Data(sentence) # For now...
					
				elif eventid == XML_EVENT_GPS:
					if instr(gpsunit_port, ":"):
						utc_time, satellite_fix_status, latitude_degrees, latitude_hemisphere, longitude_degrees, longitude_hemisphere, speed, bearing, utc_date, magnetic_variation, magnetic_variation_hemisphere, dateandtime = xmlStormForceParseEventGPS(strxml)
						
						sentence = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s*FF" % (GPS_GPRMC, utc_time, satellite_fix_status, latitude_degrees, latitude_hemisphere, longitude_degrees, longitude_hemisphere, speed, bearing, utc_date, magnetic_variation, magnetic_variation_hemisphere)
						waitForGPSData(sentence)
					
				elif eventid == XML_EVENT_EFM:
					if instr(efmunit_port, ":"):
						efs, fault, dateandtime = xmlStormForceParseEventEFM100(strxml)
						
						if efs >= 0.:
							sentence = "%s%s,%d*FF" % (EFM_POSITIVE, efs, fault)
							
						else:
							sentence = "%s%s,%d*FF" % (EFM_NEGATIVE, str(efs).replace("-", ""), fault)
							
						waitForEFM100Data(sentence)
						
				elif eventid == XML_EVENT_STPCI_NOISE:
					if instr(stunit_port, ":"):
						detected, dateandtime = xmlStormForceParseEventNoise(strxml)
						
						sentence = "%s*FF" % ST_NOISE
						waitForSTPCIData(sentence) # For now...
						
				elif eventid == XML_EVENT_STPCI_STATUS:
					if instr(stunit_port, ":"):
						close_rate, total_rate, close_alarm, severe_alarm, heading, dateandtime = xmlStormForceParseEventStatus(strxml)
						
						sentence = "%s*FF" % ST_STATUS
						waitForSTPCIData(sentence)
						
				elif eventid == XML_EVENT_STPCI_STRIKE:
					if instr(stunit_port, ":"):
						corrected_distance, uncorrected_distance, bearing, striketype, strikepolarity, dateandtime = xmlStormForceParseEventStrike(strxml)
						
						sentence = "%s,%d,%d,%f,%s,%s*FF" % (ST_STRIKE, corrected_distance, uncorrected_distance, bearing, striketype, strikepolarity)
						waitForSTPCIData(sentence)
						
				elif eventid == XML_EVENT_STPCI_SQUELCH:
					if instr(stunit_port, ":"):
						level, dateandtime = xmlStormForceParseEventSquelch(strxml)
						
						sentence = "%s,%d*FF" % (SF_SQUELCH, level)
						waitForSTPCIData(sentence) # For now...
					
				else:
					print "Warning: Unknown event ID %d found while converting the XML to a sentence." % eventid
				
	else:
		print "Warning: The data doesn't appear to be XML to transform into a sentence."
		
		if debug_mode:
			print "XML received: '%s'." % strxml
	
def clearEFM100FieldArea():
	global screen
	
	
	rect = pygame.Rect(EFM100_FIELD_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearEFM100ReceiverArea():
	global screen
	
	
	rect = pygame.Rect(EFM100_RECEIVER_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearGPSArea():
	global screen
	
	
	rect = pygame.Rect(GPS_RECEIVER_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearGPSBearingArea():
	global screen
	
	
	rect = pygame.Rect(GPS_BEARING_VALUE, (120, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearGPSDateTimeArea():
	global screen
	
	
	rect = pygame.Rect(GPS_DATETIME_VALUE, (120, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearGPSLatitudeArea():
	global screen
	
	
	rect = pygame.Rect(GPS_LAT_VALUE, (120, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearGPSLongitudeArea():
	global screen
	
	
	rect = pygame.Rect(GPS_LONG_VALUE, (120, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearLD250CloseAlarmArea():
	global screen
	
	
	rect = pygame.Rect(LD250_CLOSE_ALARM_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect

def clearLD250CloseArea():
	global screen
	
	
	rect = pygame.Rect(LD250_CLOSE_VALUE, (120, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearLD250NoiseArea():
	global screen
	
	
	rect = pygame.Rect(LD250_NOISE_VALUE, (120, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearLD250ReceiverArea():
	global screen
	
	
	rect = pygame.Rect(LD250_RECEIVER_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearLD250SevereAlarmArea():
	global screen
	
	
	rect = pygame.Rect(LD250_SEVERE_ALARM_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearLD250SquelchArea():
	global screen
	
	
	rect = pygame.Rect(LD250_SQUELCH_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearLD250StrikeArea():
	global screen
	
	
	rect = pygame.Rect(LD250_STRIKES_VALUE, (120, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearSSBTArea():
	global screen
	
	
	rect = pygame.Rect(SSBT_STATUS_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearSSBTManifestoArea():
	global screen
	
	
	rect = pygame.Rect(SSBT_MANIFESTO_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearSTPCICloseArea():
	global screen
	
	
	rect = pygame.Rect(STPCI_CLOSE_VALUE, (120, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearSTPCINoiseArea():
	global screen
	
	
	rect = pygame.Rect(STPCI_NOISE_VALUE, (120, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearSTPCIReceiverArea():
	global screen
	
	
	rect = pygame.Rect(STPCI_RECEIVER_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearSTPCISquelchArea():
	global screen
	
	
	rect = pygame.Rect(STPCI_SQUELCH_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearSTPCIStrikeArea():
	global screen
	
	
	rect = pygame.Rect(STPCI_STRIKES_VALUE, (120, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearTimeArea():
	global screen
	
	
	rect = pygame.Rect(TIME_TEXT, TIME_SIZE)
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect

def clearTRACArea():
	global screen
	
	
	rect = pygame.Rect(TRAC_STATUS_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearTRACMostActiveArea():
	global screen
	
	
	rect = pygame.Rect(TRAC_MOST_ACTIVE_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearTRACStormsArea():
	global screen
	
	
	rect = pygame.Rect(TRAC_STORMS_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearTRACStormWidthArea():
	global screen
	
	
	rect = pygame.Rect(TRAC_STORM_WIDTH_VALUE, (80, 8))
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def clearUptimeArea():
	global screen
	
	
	rect = pygame.Rect(UPTIME_TEXT, UPTIME_SIZE)
	pygame.draw.rect(screen, COLOUR_BLACK, rect)
	
	return rect
	
def closeEFM():
	global efmunit
	
	
	if efmunit is not None:
		efmunit.stop()
		efmunit.dispose()
		efmunit = None
	
def closeGPS():
	global gpsunit
	
	
	if gpsunit is not None:
		gpsunit.stop()
		gpsunit.dispose()
		gpsunit = None
	
def closeLD250():
	global ldunit
	
	
	if ldunit is not None:
		ldunit.stop()
		ldunit.dispose()
		ldunit = None
	
def closeSTPCI():
	global stunit
	
	
	if stunit is not None:
		stunit.stop()
		stunit.dispose()
		stunit = None
	
def connectToDatabase(conn = []):
	newconn = None
	
	if database_engine == DB_NONE:
		newconn = "/dev/null"
		
	elif database_engine == DB_MYSQL:
		newconn = MySQLdb.connect(host = mysql_server, user = mysql_username, passwd = mysql_password, db = mysql_database)
	
	
	if len(conn) > 0:
		for item in conn:
			item = None
		
		del conn
	
	conn.append(newconn)
	
def createNMEAChecksum(strsentence):
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
	
	return checksum
	
def cronClose():
	global cronalive
	
	
	cronalive = False
	
def cronInit():
	global cronalive, cronblitzortungthread, cronthread, cronuptimethread
	
	
	cronalive = True
	
	
	print "Information: Cron is starting the main thread."
	
	cronthread = threading.Thread(target = cronRun)
	cronthread.setDaemon(1)
	cronthread.start()
	
	
	print "Information: Cron is starting the uptime thread."
	
	cronuptimethread = threading.Thread(target = cronUptime)
	cronuptimethread.setDaemon(1)
	cronuptimethread.start()
	
	
	if blitzortung_enabled:
		print "Information: Cron is starting the Blitzortung thread."
		
		cronblitzortungthread = threading.Thread(target = blitzortungThread)
		cronblitzortungthread.setDaemon(1)
		cronblitzortungthread.start()
	
def cronRun():
	global captured_file, cronalive, ldunit_close_minute, ldunit_close_total, ldunit_noise_minute, ldunit_noise_total, ldunit_strikes_minute, ldunit_strikes_oor, ldunit_strikes_total, stunit_close_minute, stunit_close_total, stunit_noise_minute, stunit_noise_total, stunit_strikes_minute, stunit_strikes_oor, stunit_strikes_total, server_mode
	
	
	while cronalive:
		t = datetime.now()
		
		if t.second == 0:
			if (t.hour == 0 and t.minute == 0):
				# New day, reset grand counters
				ldunit_close_total = 0
				ldunit_noise_total = 0
				ldunit_strikes_oor = 0
				ldunit_strikes_total = 0
				
				stunit_close_total = 0
				stunit_noise_total = 0
				stunit_strikes_oor = 0
				stunit_strikes_total = 0
			
			# Reset the per minute counters
			ldunit_close_minute = 0
			ldunit_noise_minute = 0
			ldunit_strikes_minute = 0
			
			stunit_close_minute = 0
			stunit_noise_minute = 0
			stunit_strikes_minute = 0
			
			
			updateLD250CloseArea()
			updateLD250NoiseArea()
			updateLD250StrikeArea()
			
			updateSTPCICloseArea()
			updateSTPCINoiseArea()
			updateSTPCIStrikeArea()
		
		if (t.minute == 0 and t.second == 0) or (t.minute == 10 and t.second == 0) or (t.minute == 20 and t.second == 0) or (t.minute == 30 and t.second == 0) or (t.minute == 40 and t.second == 0) or (t.minute == 50 and t.second == 0):
			# First, rotate the logs
			rotateLogs()
			
			# Second, see if TRAC finds any thunderstorms
			threading.Thread(target = trac).start()
			
			# Third, transmit squelch for multicast clients
			if listener_multicast_address <> "" and listener_multicast_port > 0 and listener_multicast_ttl >= 0:
				threading.Thread(target = transmitXMLMulticastThread, args = (xmlStormForceCreateEventSquelch(ldunit_squelch, datetime.now()),)).start()
			
		if (t.second == 0) or (t.second == 10) or (t.second == 20) or (t.second == 30) or (t.second == 40) or (t.second == 50):
			if server_mode and not demo_mode and captured_file <> "":
				captureScreen(captured_file)
		
		
		# Wait...
		time.sleep(1)
		
def cronUptime():
	global time_font, uptime, uptime_font
	
	
	while cronalive:
		t = datetime.now()
		
		current_time = str(t.strftime("%d/%m/%Y %H:%M:%S"))
		
		rect = clearTimeArea()
		time_surface = time_font.render(current_time, True, TIME_TEXT_COLOUR)
		screen.blit(time_surface, TIME_TEXT)
		
		pygame.display.update(rect)
		
		
		# Update the uptime the old fashioned way
		uptime += 1
		
		days = int(uptime / DAY)
		hours = int((uptime % DAY) / HOUR)
		minutes = int((uptime % HOUR) / MINUTE)
		seconds = int(uptime % MINUTE)
		
		suptime = "%04d:%02d:%02d:%02d" % (days, hours, minutes, seconds)
		
		rect = clearUptimeArea()
		uptime_surface = uptime_font.render(suptime, True, UPTIME_TEXT_COLOUR)
		screen.blit(uptime_surface, UPTIME_TEXT)
		
		pygame.display.update(rect)
		
		
		# Wait...
		time.sleep(1)
	
def currentTime():
	t = datetime.now()
	
	return str(t.strftime("%d/%m/%Y %H:%M:%S"))
	
def danLookup(strfield, strtable, strwhere, conn = []):
	if len(conn) == 0:
		print "Warning: Database connection hasn't been initialised."
		
	else:
		strsql = ""
		
		if strwhere == "":
			strsql = "SELECT %s FROM %s" % (strfield, strtable)
			
		else:
			strsql = "SELECT %s FROM %s WHERE %s" % (strfield, strtable, strwhere)
		
		
		if database_engine == DB_NONE:
			pass
			
		elif database_engine == DB_MYSQL:
			try:
				conn[0].query(strsql)
				return conn[0].store_result().fetch_row(1)[0][0]
				
			except Exception, e:
				if debug_mode:
					print "MySQL Error: %s" % e
					
				return None
	
def disconnectFromDatabase(conn = []):
	if len(conn) == 1:
		if database_engine == DB_NONE:
			pass
			
		elif database_engine == DB_MYSQL:
			conn[0].close()
		
	else:
		if debug_mode:
			print "WARNING: The connection list doesn't appear to contain one item."
	
def disableInput():
	pygame.event.set_allowed(None)
	
def enableInput():
	pygame.event.set_blocked(None)
	pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN, QUIT, VIDEOEXPOSE])
	
def executeSQLCommand(strsql, conn = []):
	if len(conn) == 0:
		print "Warning: Database connection hasn't been initialised."
		
	else:
		if database_engine == DB_NONE:
			pass
			
		elif database_engine == DB_MYSQL:
			try:
				conn[0].query(strsql)
				return True
				
			except Exception, e:
				if debug_mode:
					print "MySQL Error: %s" % e
					
				return False
	
def executeSQLQuery(strsql, conn = []):
	if len(conn) == 0:
		print "Warning: Database connection hasn't been initialised."
		
	else:
		if database_engine == DB_NONE:
			pass
			
		elif database_engine == DB_MYSQL:
			try:
				conn[0].query(strsql)
				return conn[0].store_result()
			
			except Exception, e:
				if debug_mode:
					print "MySQL Error: %s" % e
					
				return None
		
def exitProgram():
	global listener_tcp, listener_tcp_alive, listener_udp, listener_udp_alive
	
	
	print ""
	print "Information: Closing down..."
	
	cronClose()
	closeEFM()
	closeGPS()
	closeLD250()
	closeSTPCI()
	
	listener_tcp_alive = False
	listener_udp_alive = False
	
	if listener_tcp is not None:
		listener_tcp.close()
		
	if listener_udp is not None:
		listener_udp.close()
		
	sys.exit(0)
	
def ifNoneReturnZero(strinput):
	if strinput is None:
		return 0
	
	else:
		return strinput
	
def iif(testval, trueval, falseval):
	if testval:
		return trueval
	
	else:
		return falseval
	
def initEFM():
	global efmunit
	
	
	output = ""
	
	# Are we using a network link or are we direct?
	device = efmunit_port.split(":")
	
	# The EFM-100 on efm.lightningmaps.com:3000 appears to be giving invalid checksums
	if len(device) == 1:
		# Make sure we've got an actual EFM-100 on the port
		efmunit = GPSDevice(efmunit_port, 9600, 8, "N", 1, 3, waitForEFM100Data, True)
		output = efmunit.readline()
		
		if (output.startswith(EFM_POSITIVE)) or (output.startswith(EFM_NEGATIVE)):
			# Destroy
			try:
				closeEFM()
				
			except:
				efmunit = None
			
			
			# The EFM-100 uses the basically uses the same protocol as a GPS (NMEA 0183) device
			efmunit = GPSDevice(efmunit_port, 9600, 8, "N", 1, None, waitForEFM100Data, True)
			
		else:
			# Destroy
			try:
				closeEFM()
				
			except:
				efmunit = None
				
			print "Warning: Didn't receive any valid sentences from the COM port."
			exitProgram()
			
	else:
		address = ""
		port = 0
		transport = ""
		
		if len(device) == 2:
			# Old style, assume TCP
			transport = "TCP"
			address = str(device[0]).replace("//", "")
			port = int(device[1])
			
		elif len(device) == 3:
			transport = device[0].upper()
			address = str(device[1]).replace("//", "")
			port = int(device[2])
			
		if transport <> "TCP" and transport <> "UDP" and transport <> "MULTICAST":
			print "Unknown transport '%s'." % transport
			
		else:
			# We're using a network, but which type?
			if efmunit_port_type == "TEXT":
				efmunit = NetDevice(address, port, listener_multicast_ttl, listener_size, iif(transport == "TCP", 0, iif(transport == "UDP", 1, 2)), efmunit_port_compression, waitForEFM100Data, True)
				
			elif efmunit_port_type == "XML":
				efmunit = XMLDevice(address, port, listener_multicast_ttl, listener_size, iif(transport == "TCP", 0, iif(transport == "UDP", 1, 2)), efmunit_port_compression, cXMLToSentence, True)
				
				if transport <> "MULTICAST":
					efmunit.writer(xmlStormForceCreateAuthRequest("anonymous", "", ""))
				
			else:
				print "Warning: Unknown port EFM-100 port type '%s'." % efmunit_port_type
				efmunit = None
		
	efmunit.start()
	
def initGPS():
	global gpsunit
	
	
	output = ""
	
	# Are we using a network link or are we direct?
	device = gpsunit_port.split(":")
	
	if len(device) == 1:
		# Make sure we've got an actual GPS on the port
		gpsunit = GPSDevice(efmunit_port, 4800, 8, "N", 1, 3, waitForGPSData, False)
		output = gpsunit.readline()
		
		if output.startswith(GPS_GPRMC):
			# Destroy
			try:
				closeGPS()
				
			except:
				gpsunit = None
			
			
			gpsunit = GPSDevice(efmunit_port, 4800, 8, "N", 1, None, waitForGPSData, False)
			
		else:
			# Destroy
			try:
				closeGPS()
				
			except:
				gpsunit = None
				
			print "Warning: Didn't receive any valid sentences from the COM port."
			exitProgram()
			
	else:
		address = ""
		port = 0
		transport = ""
		
		if len(device) == 2:
			# Old style, assume TCP
			transport = "TCP"
			address = str(device[0]).replace("//", "")
			port = int(device[1])
			
		elif len(device) == 3:
			transport = device[0].upper()
			address = str(device[1]).replace("//", "")
			port = int(device[2])
			
		if transport <> "TCP" and transport <> "UDP" and transport <> "MULTICAST":
			print "Unknown transport '%s'." % transport
			
		else:
			# We're using a network, but which type?
			if gpsunit_port_type == "TEXT":
				gpsunit = NetDevice(address, port, listener_multicast_ttl, listener_size, iif(transport == "TCP", 0, iif(transport == "UDP", 1, 2)), gpsunit_port_compression, waitForGPSData, True)
				
			elif gpsunit_port_type == "XML":
				gpsunit = XMLDevice(address, port, listener_multicast_ttl, listener_size, iif(transport == "TCP", 0, iif(transport == "UDP", 1, 2)), gpsunit_port_compression, cXMLToSentence, True)
				
				if transport <> "MULTICAST":
					gpsunit.writer(xmlStormForceCreateAuthRequest("anonymous", "", ""))
				
			else:
				print "Warning: Unknown port GPS port type '%s'." % gpsunit_port_type
				gpsunit = None
		
	gpsunit.start()
	
def initLD250():
	global ldunit, ldunit_squelch
	
	
	output = ""
	
	ok = False
	
	
	# Are we using a network link or are we direct?
	device = ldunit_port.split(":")
	
	if len(device) == 1:
		# Make sure we've got an actual LD-250 on the port
		ldunit = GPSDevice(ldunit_port, 9600, 8, "N", 1, 3, waitForLD250Data, False)
		output = ldunit.readline()
		
		if (output.startswith(LD_NOISE)) or (output.startswith(LD_STRIKE)) or (output.startswith(LD_STATUS)):
			# Destroy
			try:
				closeLD250()
				
			except:
				ldunit = None
			
			
			# The LD-250 uses the basically uses the same protocol as a GPS (NMEA 0183) device
			ldunit = GPSDevice(ldunit_port, 9600, 8, "N", 1, None, waitForLD250Data, False)
			time.sleep(1) # Wait one second for the serial to catch up
			
			ldunit.writer("SQ" + str(ldunit_squelch) + str(chr(13)))
			
			
			# Ensure the squelch has been set - we should get the result back within a few lines (due to the status being reported every second)
			for i in range(0, 5):
				output = ldunit.readline()
				
				if output.startswith(":SQUELCH " + str(ldunit_squelch) + " (0-15)"):
					ok = True
					break
					
			if not ok:
				# Try again
				print "Warning: Squelch level has not been successfully set to %s, trying again in one second..." % ldunit_squelch
				time.sleep(1)
				
				ldunit.writer("SQ" + str(ldunit_squelch) + str(chr(13)))
				
				for i in range(0, 5):
					output = ldunit.readline()
					
					if output.startswith(":SQUELCH " + str(ldunit_squelch) + " (0-15)"):
						ok = True
						break
						
					
				if not ok:
					print "Warning: Squelch level has not been successfully set to %s." % ldunit_squelch
					
					ldunit_squelch = 0
			
			else:
				print "Information: Squelch level has successfully been set to %s." % ldunit_squelch
				
				
		else:
			# Destroy
			try:
				closeLD250()
				
			except:
				ldunit = None
				
			print "Warning: Didn't receive any valid sentences from the COM port."
			exitProgram()
			
	else:
		address = ""
		port = 0
		transport = ""
		
		if len(device) == 2:
			# Old style, assume TCP
			transport = "TCP"
			address = str(device[0]).replace("//", "")
			port = int(device[1])
			
		elif len(device) == 3:
			transport = device[0].upper()
			address = str(device[1]).replace("//", "")
			port = int(device[2])
			
		if transport <> "TCP" and transport <> "UDP" and transport <> "MULTICAST":
			print "Unknown transport '%s'." % transport
			
		else:
			# We're using a network, but which type?
			if ldunit_port_type == "TEXT":
				ldunit = NetDevice(address, port, listener_multicast_ttl, listener_size, iif(transport == "TCP", 0, iif(transport == "UDP", 1, 2)), ldunit_port_compression, waitForLD250Data, True)
				
			elif ldunit_port_type == "XML":
				ldunit = XMLDevice(address, port, listener_multicast_ttl, listener_size, iif(transport == "TCP", 0, iif(transport == "UDP", 1, 2)), ldunit_port_compression, cXMLToSentence, True)
				
				if transport <> "MULTICAST":
					ldunit.writer(xmlStormForceCreateAuthRequest("anonymous", "", ""))
				
			else:
				print "Warning: Unknown port LD-250 port type '%s'." % ldunit_port_type
				ldunit = None
		
	ldunit.start()
	
def initSTPCI():
	global stunit
	
	
	output = ""
	
	# Are we using a network link or are we direct?
	device = stunit_port.split(":")
	
	if len(device) == 1:
		stunit = None
		print "Warning: Direct connection to the StormTracker is currently not supported, please specify a network address instead e.g. 'localhost:12345'."
		
	else:
		address = ""
		port = 0
		transport = ""
		
		if len(device) == 2:
			# Old style, assume TCP
			transport = "TCP"
			address = str(device[0]).replace("//", "")
			port = int(device[1])
			
		elif len(device) == 3:
			transport = device[0].upper()
			address = str(device[1]).replace("//", "")
			port = int(device[2])
			
		if transport <> "TCP" and transport <> "UDP" and transport <> "MULTICAST":
			print "Unknown transport '%s'." % transport
			
		else:
			# We're using a network, but which type?
			if stunit_port_type == "TEXT":
				stunit = NetDevice(address, port, listener_multicast_ttl, listener_size, iif(transport == "TCP", 0, iif(transport == "UDP", 1, 2)), stunit_port_compression, waitForSTPCIData, True)
				
			elif stunit_port_type == "XML":
				stunit = XMLDevice(address, port, listener_multicast_ttl, listener_size, iif(transport == "TCP", 0, iif(transport == "UDP", 1, 2)), stunit_port_compression, cXMLToSentence, True)
				
				if transport <> "MULTICAST":
					stunit.writer(xmlStormForceCreateAuthRequest("anonymous", "", ""))
				
			else:
				print "Warning: Unknown port StormTracker port type '%s'." % stunit_port_type
				stunit = None
		
	stunit.start()
	
def instr(strtest, strfor):
	return strfor in strtest
	
def lineIntersection2D(x1, y1, x2, y2, _x1, _y1, _x2, _y2):
	#
	# Found this on: http://en.wikibooks.org/wiki/Blender_3D:_Blending_Into_Python/Cookbook#2D_Line_Intersection
	#
	# Exactly what I needed, I just tided it up a bit!
	#
	
	# Bounding box intersection first.
	if min(x1, x2) > max(_x1, _x2) or max(x1, x2) < min(_x1, _x2) or min(y1, y2) > max(_y1, _y2) or max(y1, y2) < min(_y1, _y2):
		return None # Basic Bounds intersection TEST returns false
	
	# Are either of the segments points? Check Seg1
	if abs(x1 - x2) + abs(y1 - y2) <= SMALL_NUM:
		return None
	
	# are either of the segments points? Check Seg2
	if abs(_x1 - _x2) + abs(_y1 - _y2) <= SMALL_NUM:
		return None
	
	# Make sure the HOZ/Vert Line Comes first.
	if abs(_x1 - _x2) < SMALL_NUM or abs(_y1 - _y2) < SMALL_NUM:
		x1, x2, y1, y2, _x1, _x2, _y1, _y2 = _x1, _x2, _y1, _y2, x1, x2, y1, y2
	
	if abs(x2-x1) < SMALL_NUM: # VERTICLE LINE
		if abs(_x2 - _x1) < SMALL_NUM: # VERTICLE LINE SEG2
			return None # 2 verticle lines dont intersect
		
		elif abs(_y2 - _y1) < SMALL_NUM:
			return x1, _y1 # X of vert, Y of hoz. no calculation
			
		yi = ((_y1 / abs(_x1 - _x2)) * abs(_x2 - x1)) + ((_y2 / abs(_x1 - _x2)) * abs(_x1 - x1))
		
		if yi > max(y1, y2): # New point above seg1's vert line
			return None
		
		elif yi < min(y1, y2): # New point below seg1's vert line
			return None
		
		return x1, yi # Intersecting
	
	if abs(y2 - y1) < SMALL_NUM: # HOZ LINE
		if abs(_y2 - _y1) < SMALL_NUM: # HOZ LINE SEG2
			return None # 2 hoz lines dont intersect
		
		# Can skip vert line check for seg 2 since its covered above
		xi = ((_x1 / abs(_y1 - _y2)) * abs(_y2 - y1)) + ((_x2 / abs(_y1 - _y2)) * abs(_y1 - y1))
		
		if xi > max(x1, x2): # New point right of seg1's hoz line
			return None
		
		elif xi < min(x1, x2): # New point left of seg1's hoz line
			return None
		
		return xi, y1 # Intersecting
	
	# Accounted for hoz/vert lines. Go on with both anglular
	b1 = (y2 - y1) / (x2 - x1)
	b2 = (_y2 - _y1) / (_x2 - _x1)
	a1 = y1 - b1 * x1
	a2 = _y1 - b2 * _x1
	
	if b1 - b2 == 0.0:
		return None
	
	xi = -(a1 - a2) / (b1 - b2)
	yi = a1 + b1 * xi
	
	if (x1 - xi) * (xi - x2) >= 0 and (_x1 - xi) * (xi - _x2) >= 0 and (y1 - yi) * (yi - y2) >= 0 and (_y1 - yi) * (yi - _y2) >= 0:
		return xi, yi
	
	else:
		return None
	
def listenerTCPHandler(client, address):
	global listener_tcp_auth
	
	
	while True:
		data = client.recv(listener_size)
		addr = ""
		
		if data:
			# Authenticate clients
			if listener_tcp_port_compression == "bz2":
				data = bz2.decompress(data)
				
			elif listener_tcp_port_compression == "lzma":
				data = pylzma.decompress(data)
			
			
			username, password, key = xmlStormForceParseAuthRequest(data)
			
			# TO DO: Perform authentication against the database
			if username <> "":
				# Make sure we don't add multiple entries
				if not client in listener_tcp_auth:
					print "TCP Listener: Authenticated connection from %s:%d on %s as \"%s\"." % (address[0], address[1], currentTime(), username)
					
					
					# Send the client any settings that are needed
					tosend = []
					
					# Squelch
					tosend.append(xmlStormForceCreateEventSquelch(ldunit_squelch, datetime.now()))
					
					# OK, now send everything
					print "TCP Listener: Sending settings to %s:%d on %s." % (address[0], address[1], currentTime())
					
					for sendnow in tosend:
						if listener_tcp_port_compression == "bz2":
							sendnow = bz2.compress(sendnow)
							
						elif listener_tcp_port_compression == "lzma":
							sendnow = pylzma.compress(sendnow)
							
						client.sendall(sendnow)
						
					
					listener_tcp_auth.append(client)
					
					
					print "TCP Listener: Finished sending settings to %s:%d on %s." % (address[0], address[1], currentTime())
				
			else:
				break
			
		else:
			break
	
	
	# Remove the client from the list
	if client in listener_tcp_auth:
		listener_tcp_auth.remove(client)
	
	
	print "TCP Listener: Closed connection from %s:%d on %s." % (address[0], address[1], currentTime())
	client.close()

def listenerUDPHandler(client, address):
	global listener_udp_auth
	
	
	while True:
		data, addr = client.recvfrom(listener_size)
		address = addr
		
		if data:
			# Authenticate clients
			if listener_udp_port_compression == "bz2":
				data = bz2.decompress(data)
				
			elif listener_udp_port_compression == "lzma":
				data = pylzma.decompress(data)
				
			
			username, password, key = xmlStormForceParseAuthRequest(data)
			
			# TO DO: Perform authentication against the database
			if username <> "":
				# Make sure we don't add multiple entries
				if not client in listener_udp_auth:
					print "UDP Listener: Authenticated connection from %s:%d on %s as \"%s\"." % (address[0], address[1], currentTime(), username)
					
					
					# Send the client any settings that are needed
					tosend = []
					
					# Squelch
					tosend.append(xmlStormForceCreateEventSquelch(ldunit_squelch, datetime.now()))
					
					# OK, now send everything
					print "UDP Listener: Sending settings to %s:%d on %s." % (address[0], address[1], currentTime())
					
					for sendnow in tosend:
						if listener_udp_port_compression == "bz2":
							sendnow = bz2.compress(sendnow)
							
						elif listener_udp_port_compression == "lzma":
							sendnow = pylzma.compress(sendnow)
							
						client.sendall(sendnow)
					
					listener_udp_auth.append((client, address))
					
					
					print "UDP Listener: Finished sending settings to %s:%d on %s." % (address[0], address[1], currentTime())
				
			else:
				break
			
		else:
			break
	
	
	# Remove the client from the list
	if client in listener_udp_auth:
		listener_udp_auth.remove(client)
	
	
	print "UDP Listener: Closed connection from %s:%d on %s." % (address[0], address[1], currentTime())
	client.close()
	
def listenerSig(signal, frame):
	waitpid(-1, WNOHANG)
	
def listenerTCPSub():
	global listener_tcp, listener_tcp_alive
	
	
	while listener_tcp_alive:
		try:
			client, address = listener_tcp.accept()
			
			print "TCP Listener: Accepted connection from %s:%d on %s." % (address[0], address[1], currentTime())
			threading.Thread(target = listenerTCPHandler, args = (client, address,)).start()
			
		except:
			pass
		
	if listener_tcp is not None:
		listener_tcp.close()
	
def listenerUDPSub():
	global listener_udp, listener_udp_alive
	
	
	while listener_udp_alive:
		try:
			# This refuses to fire in a thread, so we can only accept ONE client!!!
			#threading.Thread(target = listenerUDPHandler, args = (listener_udp, None,)).start()
			listenerUDPHandler(listener_udp, None)
			
		except:
			pass
		
	if listener_udp is not None:
		listener_udp.close()
	
def main():
	global alarm_font, background, ldunit_port, listener_tcp, listener_tcp_alive, listener_tcp_thread, listener_udp, listener_udp_alive, listener_udp_thread, number_font, reconstruction_file, running, screen, small_number_font, square_font, ssbt_enabled, time_font, uptime_font
	global MAP, INFO_SIZE, TRAC_SENSITIVITY, TRAC_STORM_WIDTH, USER_COPYRIGHT
	
	csv_file = ""
	
	
	# Show the copyright notice first
	print """
#########################################################################
# Copyright/License Notice (Modified BSD License)                       #
#########################################################################
#########################################################################
# Copyright (c) 2008-2009, Daniel Knaggs                                #
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
#   * This Software is not to be used for safety purposes.              #
#                                                                       #
#   * You agree and abide the Disclaimer for your Boltek LD-250.        #
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

WARNING: If you do not agree to the above copyright/license notice, cease using the software immediately and remove from your system.
"""

	# Welcome message
	print ""
	print ""
	print "Information: Welcome to StormForce v%s." % VERSION
	print "Information: Please report any bugs you find so I can fix them!"
	print ""
	
	# Parse any arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "a:b:c:C:dDe:f:gG:hi:jk:q:Lm:no:p:rRs:S:TuU:w:xy:z:")
		
		if len(opts) > 0:
			print "WARNING: StormForce no longer uses the arguments to define it's settings.  Please restart StormForce with no arguments."
			
			exitProgram()
		
	except getopt.error, msg:
		print msg
		sys.exit(1)
		
		
	if not path.exists(XML_SETTINGS_FILE):
		print "Warning: The XML settings file doesn't exist, create one..."
		
		xmlStormForceSettingsWrite()
		
		
		print "Information: The XML settings file has been created using the default settings.  Please edit it and restart StormForce once you're happy with the settings."
		
		exitProgram()
		
	else:
		print "Information: Reading XML settings..."
		
		xmlStormForceSettingsRead()
		
		# This will ensure it will have any new settings in
		if path.exists(XML_SETTINGS_FILE + ".bak"):
			unlink(XML_SETTINGS_FILE + ".bak")
			
		rename(XML_SETTINGS_FILE, XML_SETTINGS_FILE + ".bak")
		xmlStormForceSettingsWrite()
		
		
	
	print ""
	
	# Are we doing an import?
	if csv_file <> "":
		# Try-except-finally doesn't work correctly in Python v2.4 - has been fixed in v2.5
		try:
			try:
				lines_error = 0
				lines_imported = 0
				lines_skipped = 0
				
				myconn = []
				connectToDatabase(myconn)
				
				print "Information: Updating database structure..."
				updateDatabase(myconn)
				
				
				print "Information: Preparing to import CSV file into database..."
				csv = file(csv_file, "r")
				
				print "Information: Starting import..."
				executeSQLCommand("START TRANSACTION", myconn)
				
				for line in csv.readlines():
					a = line.split(",")
					
					if len(a) == 4:
						if executeSQLCommand("INSERT INTO tblStrikes(DateTimeOfStrike, CorrectedStrikeDistance, UncorrectedStrikeDistance, StrikeAngle, StrikeType, StrikePolarity) VALUES('%s', %f, %f, %s, '%s', '%s')" % (a[0], float(a[1]), float(a[2]), a[3], "CG", ""), myconn):
							lines_imported += 1
							
						else:
							lines_error += 1
					
					else:
						lines_skipped += 1
				
				executeSQLCommand("COMMIT", myconn)
				csv.close()
				
				disconnectFromDatabase(myconn)
				
				print "Information: Import completed! %d errors, %d imported, %d skipped. Exiting..." % (lines_error, lines_imported, lines_skipped)
				
			except Exception, e:
				print "Error: An error has occurred while importing.\n%s" % e
			
		finally:
			exitProgram()
	
	
	# Prepare the game interface
	pygame.init()
	
	# Prepare the game surface
	screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
	pygame.display.set_caption("StormForce v%s" % VERSION)
	
	if sound_enabled:
		pygame.mixer.init(44100, 16, 2, 4096)
	
	alarm_font = pygame.font.Font(path.join("ttf", "aldo.ttf"), 28)
	number_font = pygame.font.Font(path.join("ttf", "lcd2.ttf"), 30)
	square_font = pygame.font.Font(path.join("ttf", "micron55.ttf"), 8)
	small_number_font = pygame.font.Font(path.join("ttf", "7linedigital.ttf"), 8)
	time_font = pygame.font.Font(path.join("ttf", "lcd1.ttf"), 18)
	uptime_font = pygame.font.Font(path.join("ttf", "lcd1.ttf"), 18)
	
	# Set any "constants" up for later use
	INFO_SIZE = (SCREEN_SIZE[0] - MAP_SIZE[0], MAP_SIZE[1])
	
	MAP = path.join("png", "map-%s.png" % zoom_distance)
	
	if not path.exists(MAP):
		print "Warning: " + MAP + " doesn't exist, using blank instead."
		MAP = path.join("png", "blank.png")
		
	if ldunit_skew_amount <> 0.:
		print "Information: Skewing LD-250 strike angle by %s degrees." % ldunit_skew_amount
		
	if stunit_skew_amount <> 0.:
		print "Information: Skewing StormTracker strike angle by %s degrees." % stunit_skew_amount
	
	
	disableInput()
	
	
	print ""
	
	if mysql_available:
		print "Information: MySQL support is available."
		
	else:
		print "Warning: MySQLdb isn't available, please install if you wish to use TRAC, SSBT, or wish to keep any history on strike data."
		
	
	
	if psyco_available:
		print "Information: Psyco support is available."
		
		
	if database_engine == DB_NONE:
		print "Warning: No database engine selected."
		
	if (database_engine == DB_MYSQL and not mysql_available):
		print "Error: Invalid database engine as MySQL is not available."
	
	
	if (database_engine == DB_MYSQL and mysql_available):
		print "Information: Using MySQL as the database backend."
	
	
	
	print "Information: Connecting to database..."
	
	if (debug_mode) and (database_engine == DB_MYSQL):
		print "Information: MySQL Server = \"%s\", Database = \"%s\", Username = \"%s\", Password = \"%s\"" % (mysql_server, mysql_database, mysql_username, mysql_password)
	
	myconn = []
	
	try:
		connectToDatabase(myconn)
		
		print "Information: Updating database structure..."
		updateDatabase(myconn)
		
	except Exception, e:
		print "Error: An error has occurred while connecting to the database.\n%s" % e
		exitProgram()
		
		
	print "Information: Initialising history..."
	
	executeSQLCommand("START TRANSACTION", myconn)
	
	executeSQLCommand("DELETE FROM tblStrikesPersistence0", myconn)
	executeSQLCommand("DELETE FROM tblStrikesPersistence1", myconn)
	executeSQLCommand("DELETE FROM tblStrikesPersistence2", myconn)
	executeSQLCommand("DELETE FROM tblStrikesPersistence3", myconn)
	executeSQLCommand("DELETE FROM tblStrikesPersistence4", myconn)
	executeSQLCommand("DELETE FROM tblStrikesPersistence5", myconn)
	
	executeSQLCommand("DELETE FROM tblSSBTElection", myconn)
	
	executeSQLCommand("COMMIT", myconn)
	
	
	print "Information: Closing database connection..."
	disconnectFromDatabase(myconn)
	
	if not demo_mode:
		if ldunit_port <> "":
			print "Information: Initialising COM port for LD-250 via %s..." % ldunit_port
			initLD250()
			
			print "Information: COM port opened! Waiting for lightning data from LD-250..."
			
		else:
			print "Warning: No COM port set for LD-250."
		
	else:
		ldunit_port = "DEMONSTRATION"
		
		print "Information: Running in demo mode, will be simulating stikes when the certain keys are pressed..."
		
	if stunit_port <> "":
		print "Information: Initialising COM port for StormTracker via %s..." % stunit_port
		initSTPCI()
		
		print "Information: COM port opened! Waiting for StormTracker..."
		
	if efmunit_port <> "":
		print "Information: Initialising COM port for EFM-100 via %s..." % efmunit_port
		initEFM()
		
		print "Information: COM port opened! Waiting for EFM-100..."
		
	if gpsunit_port <> "":
		print "Information: Initialising COM port for GPS via %s..." % gpsunit_port
		initGPS()
		
		print "Information: COM port opened! Waiting for GPS..."
		
		
	# Are we going to use SSBT if we have both the LD-250 and the StormTracker?
	if ldunit_port <> "" and stunit_port <> "":
		ssbt_enabled = False # Disable completely for now
	
	
	if listener_tcp_port > 0:
		print "Information: Attempting to enable the listener on TCP/%d..." % listener_tcp_port
		
		try:
			listener_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			listener_tcp.bind(("", listener_tcp_port))
			listener_tcp.listen(listener_backlog)
			
			signal.signal(signal.SIGCHLD, listenerSig)
			
			
			listener_tcp_alive = True
			
			
			# Start the listener thread
			listener_tcp_thread = threading.Thread(target = listenerTCPSub)
			listener_tcp_thread.setDaemon(1)
			listener_tcp_thread.start()
			
		except socket.error, e:
			if listener_tcp:
				listener_tcp.close()
				
			print "Error: Could not open socket: " + e
				
		except Exception, msg:
			print "Error: An exception has occurred: %s" % msg
			
	if listener_udp_port > 0:
		print "Information: Attempting to enable the listener on UDP/%d..." % listener_udp_port
		
		try:
			listener_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			listener_udp.bind(("", listener_udp_port))
			
			signal.signal(signal.SIGCHLD, listenerSig)
			
			
			listener_udp_alive = True
			
			
			# Start the listener thread
			listener_udp_thread = threading.Thread(target = listenerUDPSub)
			listener_udp_thread.setDaemon(1)
			listener_udp_thread.start()
			
		except socket.error, e:
			if listener_udp:
				listener_udp.close()
				
			print "Error: Could not open socket: " + e
				
		except Exception, msg:
			print "Error: An exception has occurred: %s" % msg
			
	if listener_multicast_address <> "" and listener_multicast_port > 0 and listener_multicast_ttl >= 0:
		# There's no need for a "listener" with multicast since we don't have to deal with authentication
		#
		# The reason for this is that the authentication requests and responses would get captured by all StormForce clients!
		print "Information: Will be attempting to broadcast strike data via MULTICAST/%s/%d." % (listener_multicast_address, listener_multicast_port)
		
	
	
	if (server_mode and curl_arguments <> ""):
		print "Information: Server mode with uploading enabled (Curl arguments = \"%s\")." % curl_arguments
		
	elif (server_mode and curl_arguments == ""):
		print "Information: Server mode without uploading enabled."
		
	
	
	if close_alarm_arguments <> "":
		print "Information: Close alarm script enabled."
		
	if severe_alarm_arguments <> "":
		print "Information: Severe alarm script enabled."
		
	
	# Blitzortung
	if (blitzortung_hostname <> "" and blitzortung_port <> 0 and blitzortung_unit <> 0 and blitzortung_username <> ""):
		blitzortung_enabled = True
		
		print "Information: Blitzortung data upload enabled to '%s:%d'." % (blitzortung_hostname, blitzortung_port)
		
	else:
		blitzortung_enabled = False
		
	
	# We only need to assign the background once
	background = pygame.image.load(MAP).convert()
	
	renderScreen()
	
	# Re-enable input
	enableInput()
	
	# Seed the RNG
	t = datetime.now()
	random.seed(time.mktime(t.timetuple()))
	
	
	# Enable cron
	print "Information: Enabling Cron..."
	cronInit()
	
	# Enter fullscreen mode if we need to
	if fullscreen:
		pygame.display.toggle_fullscreen()
	
	
	print "Information: Entering main loop..."
	print ""
	
	
	pygame.key.set_repeat(1000, 100)
	
	while True:
		event = pygame.event.wait()
		
		if event.type == QUIT:
			exitProgram()
		
		elif event.type == KEYDOWN:
			if event.mod & KMOD_CTRL:
				pass
		
			elif event.mod & KMOD_ALT:
				pass
		
			elif event.mod & KMOD_SHIFT:
				pass
			
			else:
				if event.key == K_ESCAPE:
					exitProgram()
					
				elif event.key == K_INSERT:
					print "Development: To do, zoom in."
					
				elif event.key == K_DELETE:
					print "Development: To do, zoom out."
					
				elif event.key == K_c:
					if demo_mode:
						# This should plot strikes that form a circle
						for x in range(0, 360):
							threading.Thread(target = plotStrike, args = (float(zoom_distance) / 2., float(x), False, 0,)).start()
							
							transmitXML(xmlStormForceCreateEventStrike(int(float(zoom_distance) / 2.), 0, float(x), "CG", "", datetime.now()))
							
				elif event.key == K_f:
					pygame.display.toggle_fullscreen()
					
				elif event.key == K_m:
					if demo_mode:
						# Fire off 50000 strikes to test for data loss
						for x in range(0, 50000):
							distance = random.randint(0, zoom_distance)
							angle = float(random.randint(0, 360))
							
							transmitXML(xmlStormForceCreateEventStrike(distance, 0, angle, "CG", "", datetime.now()))
							plotStrike(distance, angle, False, 0)
					
				elif event.key == K_p:
					if demo_mode:
						t = datetime.now()
						captureScreen(t.strftime("%d%m%Y%H%M%S.png"))
						
						print "Information: Screen captured to file."
						
				elif event.key == K_r:
					if demo_mode:
						rotateLogs()
					
				elif event.key == K_s or event.key == K_d:
					if demo_mode:
						# This will plot strikes in a random position
						distance = random.randint(0, zoom_distance)
						angle = float(random.randint(0, 360))
						
						transmitXML(xmlStormForceCreateEventStrike(distance, 0, angle, "CG", "", datetime.now()))
						
						if event.key == K_s:
							threading.Thread(target = plotStrike, args = (distance, angle, False, 0,)).start()
							
						elif event.key == K_d:
							threading.Thread(target = plotStrike, args = (distance, angle, False, 1,)).start()
						
				elif event.key == K_t:
					if demo_mode:
						trac()
						
				elif event.key == K_q:
					exitProgram()
				
		elif event.type == MOUSEBUTTONDOWN:
			if demo_mode:
				# This will plot a strike where the mouse is
				x, y = event.pos
				
				if (x > 600) or (y > 600):
					pass
					
				else:
					plotStrikeXY(x, y, [255, 0, 140])
					
					myconn = []
					connectToDatabase(myconn)
					
					executeSQLCommand("INSERT INTO tblStrikesPersistence0(X, Y, DateTimeOfStrike) VALUES(%d, %d, '%s')" % (x, y, datetime.now()), myconn)
					disconnectFromDatabase(myconn)
					
					updateLD250StrikeCount(False)
	
def progressBar(position, startcolour, endcolour, value, maxvalue, thickness):
	r_step = 0
	g_step = 0
	b_step = 0
	
	for x in range(0, value):
		if x > maxvalue:
			break
			
		else:
			# Get the next colour
			colour = [min(max(startcolour[0] + r_step, 0), 255), min(max(startcolour[1] + g_step, 0), 255), min(max(startcolour[2] + b_step, 0), 255)]
			
			# Draw the gradient
			rect = pygame.Rect([position[0] + x, position[1]], [1, thickness])
			pygame.draw.rect(screen, colour, rect)
			
			# Increase the colour stepping
			r_step += (endcolour[0] - startcolour[0]) / maxvalue
			g_step += (endcolour[1] - startcolour[1]) / maxvalue
			b_step += (endcolour[2] - startcolour[2]) / maxvalue
			
def progressBarColour(startcolour, endcolour, value, maxvalue):
	r_step = 0
	g_step = 0
	b_step = 0
	colour = TRAC_COLOUR
	
	for x in range(0, value):
		if x > maxvalue:
			break
			
		else:
			# Get the next colour
			colour = [min(max(startcolour[0] + r_step, 0), 255), min(max(startcolour[1] + g_step, 0), 255), min(max(startcolour[2] + b_step, 0), 255)]
			
			# Increase the colour stepping
			r_step += (endcolour[0] - startcolour[0]) / maxvalue
			g_step += (endcolour[1] - startcolour[1]) / maxvalue
			b_step += (endcolour[2] - startcolour[2]) / maxvalue
			
	return colour
	
def playSound(strsound):
	if sound_enabled:
		sound = pygame.mixer.Sound(strsound)
		sound.play()
	
def plotStrike(strikedistance, strikeangle, isold, unit):
	global screen
	
	
	# By using a bit of trignonmetry we can get the missing values
	#
	#       ^
	#      / |
	#  H  /  |
	#    /   | O
	#   /    |
	#  / )X  |
	# /-------
	#     A
	o = 0.
	a = 0.
	
	if unit == 0:
		o = sin(radians(strikeangle + ldunit_skew_amount)) * (float(strikedistance) / zoom_multiplier)
		a = cos(radians(strikeangle + ldunit_skew_amount)) * (float(strikedistance) / zoom_multiplier)
		
	else:
		o = sin(radians(strikeangle + stunit_skew_amount)) * (float(strikedistance) / zoom_multiplier)
		a = cos(radians(strikeangle + stunit_skew_amount)) * (float(strikedistance) / zoom_multiplier)
	
	rect = None
	
	if not isold:
		if strike_shape == SHAPE_SQUARE:
			# We use a 3x3 rectangle to indicate a strike, where (1,1) is the centre (zero-based)
			rect = pygame.Rect([(CENTRE_X + o) - 1, (CENTRE_Y + -a) - 1], [3, 3])
			pygame.draw.rect(screen, COLOUR_NEW_STRIKE, rect)
			
		elif strike_shape == SHAPE_TRIANGLE:
			points = []
			points.append([CENTRE_X + o, CENTRE_Y + -a])
			points.append([(CENTRE_X + o) - 2, (CENTRE_Y + -a) - 2])
			points.append([(CENTRE_X + o) + 2, (CENTRE_Y + -a) - 2])
			
			rect = pygame.draw.polygon(screen, COLOUR_NEW_STRIKE, points)
			
		elif strike_shape == SHAPE_CIRCLE:
			rect = pygame.draw.circle(screen, COLOUR_NEW_STRIKE, [int(CENTRE_X + o), int(CENTRE_Y + -a)], 2, 0)
		
	else:
		# Draw a 1-pixel blue strike instead
		rect = pygame.Rect([(CENTRE_X + o) - 1, (CENTRE_Y + -a) - 1], [1, 1])
		
	
	if show_red_dot:
		# By putting a red-dot in the centre helps me work out the centre easier
		pygame.draw.line(screen, [255, 0, 0], [CENTRE_X + o, CENTRE_Y + -a], [CENTRE_X + o, CENTRE_Y + -a], 1)
		
	pygame.display.update(rect)
	
	if unit == 0:
		updateLD250StrikeCount(False)
		
	else:
		updateSTPCIStrikeCount(False)
	
	
	# Keep a history of the strikes
	myconn = []
	connectToDatabase(myconn)
	
	if not executeSQLCommand("INSERT INTO tblStrikesPersistence0(X, Y, DateTimeOfStrike) VALUES(%d, %d, '%s')" % (int(MAP_MATRIX_CENTRE[0] + o), int(MAP_MATRIX_CENTRE[1] + -a), datetime.now()), myconn):
		print "Warning: Failed to write out the strike to the persistence table."
	
	disconnectFromDatabase(myconn)
	
	if strikedistance < CLOSE_DISTANCE_ALARM:
		if unit == 0:
			updateLD250CloseCount()
			
		else:
			updateSTPCICloseCount()
		
def plotStrikeXY(x, y, colour):
	global screen
	
	
	rect = None
	
	if strike_shape == SHAPE_SQUARE:
		rect = pygame.Rect([x - 1, y - 1], [3, 3])
		pygame.draw.rect(screen, colour, rect)
		
	elif strike_shape == SHAPE_TRIANGLE:
		points = []
		points.append([x, y])
		points.append([x - 2, y - 2])
		points.append([x + 2, y - 2])
			
		rect = pygame.draw.polygon(screen, colour, points)
		
	elif strike_shape == SHAPE_CIRCLE:
		rect = pygame.draw.circle(screen, colour, [int(x), int(y)], 2, 0)
		
	pygame.display.update(rect)
	
def renderScreen():
	global background, screen
	
	
	# Draw the "base" screen
	screen.blit(background, (0, 0))
	
	# Side section
	COUNTER_START = [MAP_SIZE[0] + 5, 4]
	COUNTER_SIZE = [INFO_SIZE[0] - 10, 52]
	
	# Top lines
	pygame.draw.line(screen, COLOUR_SIDELINE, [MAP_SIZE[0] + 2, COUNTER_SIZE[1] - 5], [SCREEN_SIZE[0], COUNTER_SIZE[1] - 5], 1)
	pygame.draw.line(screen, COLOUR_SIDELINE, [MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 42], [SCREEN_SIZE[0], COUNTER_SIZE[1] + 42], 1)
	pygame.draw.line(screen, COLOUR_SIDELINE, [MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 90], [SCREEN_SIZE[0], COUNTER_SIZE[1] + 90], 1)
	pygame.draw.line(screen, COLOUR_SIDELINE, [MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 138], [SCREEN_SIZE[0], COUNTER_SIZE[1] + 138], 1)
	pygame.draw.line(screen, COLOUR_SIDELINE, [MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 186], [SCREEN_SIZE[0], COUNTER_SIZE[1] + 186], 1)
	pygame.draw.line(screen, COLOUR_SIDELINE, [MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 234], [SCREEN_SIZE[0], COUNTER_SIZE[1] + 234], 1)
	
	
	# Starting point
	clearLD250CloseAlarmArea()
	clearLD250ReceiverArea()
	clearLD250SevereAlarmArea()
	clearLD250SquelchArea()
	clearLD250CloseArea()
	clearLD250NoiseArea()
	clearLD250StrikeArea()
	
	clearSTPCIReceiverArea()
	clearSTPCISquelchArea()
	clearSTPCICloseArea()
	clearSTPCINoiseArea()
	clearSTPCIStrikeArea()
	
	clearEFM100FieldArea()
	clearEFM100ReceiverArea()
	
	clearGPSArea()
	clearGPSBearingArea()
	clearGPSDateTimeArea()
	clearGPSLatitudeArea()
	clearGPSLongitudeArea()
	
	clearTRACArea()
	clearTRACMostActiveArea()
	clearTRACStormsArea()
	clearTRACStormWidthArea()
	
	clearSSBTArea()
	clearSSBTManifestoArea()
	
	
	updateLD250CloseArea()
	updateLD250NoiseArea()
	updateLD250StrikeArea()
	
	updateSTPCICloseArea()
	updateSTPCINoiseArea()
	updateSTPCIStrikeArea()
	
	updateTRACMostActiveArea()
	updateTRACStatus(trac_active)
	updateTRACStormsArea()
	updateTRACStormWidthArea()
	
	
	# LD-250
	surface = square_font.render("LD-250 %s" % iif(ldunit_port <> "", "ON %s" % ldunit_port, ""), False, UNIT_SECTION_COLOUR)
	screen.blit(surface, LD250_HEADER)
	
	surface = square_font.render("RECEIVER:", False, COLOUR_WHITE)
	screen.blit(surface, LD250_RECEIVER)
	
	surface = square_font.render("CLOSE ALARM:", False, COLOUR_WHITE)
	screen.blit(surface, LD250_CLOSE_ALARM)
	
	surface = square_font.render("SEVERE ALARM:", False, COLOUR_WHITE)
	screen.blit(surface, LD250_SEVERE_ALARM)
	
	surface = square_font.render("SQUELCH:", False, COLOUR_WHITE)
	screen.blit(surface, LD250_SQUELCH)
	
	surface = square_font.render("STRIKES:", False, COLOUR_WHITE)
	screen.blit(surface, LD250_STRIKES)
	
	surface = square_font.render("CLOSE:", False, COLOUR_WHITE)
	screen.blit(surface, LD250_CLOSE)
	
	surface = square_font.render("NOISE:", False, COLOUR_WHITE)
	screen.blit(surface, LD250_NOISE)
	
	
	# StormTracker
	surface = square_font.render("STORMTRACKER %s" % iif(stunit_port <> "", "ON %s" % stunit_port, ""), False, UNIT_SECTION_COLOUR)
	screen.blit(surface, STPCI_HEADER)
	
	surface = square_font.render("RECEIVER:", False, COLOUR_WHITE)
	screen.blit(surface, STPCI_RECEIVER)
	
	surface = square_font.render("SQUELCH:", False, COLOUR_WHITE)
	screen.blit(surface, STPCI_SQUELCH)
	
	surface = square_font.render("STRIKES:", False, COLOUR_WHITE)
	screen.blit(surface, STPCI_STRIKES)
	
	surface = square_font.render("CLOSE:", False, COLOUR_WHITE)
	screen.blit(surface, STPCI_CLOSE)
	
	surface = square_font.render("NOISE:", False, COLOUR_WHITE)
	screen.blit(surface, STPCI_NOISE)
	
	
	# EFM-100
	surface = square_font.render("EFM-100 %s" % iif(efmunit_port <> "", "ON %s" % efmunit_port, ""), False, UNIT_SECTION_COLOUR)
	screen.blit(surface, EFM100_HEADER)
	
	surface = square_font.render("RECEIVER:", False, COLOUR_WHITE)
	screen.blit(surface, EFM100_RECEIVER)
	
	surface = square_font.render("FIELD LEVEL:", False, COLOUR_WHITE)
	screen.blit(surface, EFM100_FIELD)
	
	
	# GPS
	surface = square_font.render("GPS", False, UNIT_SECTION_COLOUR)
	screen.blit(surface, GPS_HEADER)
	
	surface = square_font.render("RECEIVER:", False, COLOUR_WHITE)
	screen.blit(surface, GPS_RECEIVER)
	
	
	surface = square_font.render("LONG:", False, COLOUR_WHITE)
	screen.blit(surface, GPS_LONG)
	
	surface = square_font.render("LAT:", False, COLOUR_WHITE)
	screen.blit(surface, GPS_LAT)
	
	surface = square_font.render("BEARING:", False, COLOUR_WHITE)
	screen.blit(surface, GPS_BEARING)
	
	surface = square_font.render("DATETIME:", False, COLOUR_WHITE)
	screen.blit(surface, GPS_DATETIME)
	
	
	# We'll set some of values here
	# LD-250
	surface = square_font.render("Inactive", False, COLOUR_ALARM_INACTIVE)
	screen.blit(surface, LD250_CLOSE_ALARM_VALUE)
	
	surface = square_font.render("Inactive", False, COLOUR_ALARM_INACTIVE)
	screen.blit(surface, LD250_SEVERE_ALARM_VALUE)
	
	surface = square_font.render("Inactive", False, COLOUR_ALARM_ACTIVE)
	screen.blit(surface, LD250_RECEIVER_VALUE)
	
	surface = square_font.render("%s" % ldunit_squelch, False, COLOUR_ALARM_INACTIVE)
	screen.blit(surface, LD250_SQUELCH_VALUE)
	
	
	# StormTracker
	surface = square_font.render("Inactive", False, COLOUR_ALARM_ACTIVE)
	screen.blit(surface, STPCI_RECEIVER_VALUE)
	
	surface = square_font.render("%s" % stunit_squelch, False, COLOUR_ALARM_INACTIVE)
	screen.blit(surface, STPCI_SQUELCH_VALUE)
	
	
	# EFM-100
	surface = square_font.render("Inactive", False, COLOUR_ALARM_ACTIVE)
	screen.blit(surface, EFM100_RECEIVER_VALUE)
	
	
	# GPS
	surface = square_font.render("Inactive", False, COLOUR_ALARM_ACTIVE)
	screen.blit(surface, GPS_RECEIVER_VALUE)
	
	
	# TRAC
	surface = square_font.render("TRAC v" + TRAC_VERSION, False, UNIT_SECTION_COLOUR)
	screen.blit(surface, TRAC_HEADER)
	
	surface = square_font.render("STATUS:", False, COLOUR_WHITE)
	screen.blit(surface, TRAC_STATUS)
	
	surface = square_font.render("STORMS:", False, COLOUR_WHITE)
	screen.blit(surface, TRAC_STORMS)
	
	surface = square_font.render("MOST ACTIVE:", False, COLOUR_WHITE)
	screen.blit(surface, TRAC_MOST_ACTIVE)
	
	surface = square_font.render("WIDTH:", False, COLOUR_WHITE)
	screen.blit(surface, TRAC_STORM_WIDTH_TEXT)
	
	
	# SSBT - StormForce Strike Bi/Triangulation
	surface = square_font.render("StormForce Strike Bi/Triangulation (SSBT)", False, UNIT_SECTION_COLOUR)
	screen.blit(surface, SSBT_HEADER)
	
	surface = square_font.render("STATUS:", False, COLOUR_WHITE)
	screen.blit(surface, SSBT_STATUS)
	
	surface = square_font.render("MANIFESTO:", False, COLOUR_WHITE)
	screen.blit(surface, SSBT_MANIFESTO)
	
	if ssbt_enabled:
		surface = square_font.render("Active", False, COLOUR_ALARM_INACTIVE)
		
	else:
		surface = square_font.render("Inactive", False, COLOUR_ALARM_ACTIVE)
		
	screen.blit(surface, SSBT_STATUS_VALUE)
	
	if ssbt_enabled:
		updateSSBTManifesto(MANIFESTO_ELECTION)
	
	
	
	# Side line
	pygame.draw.line(screen, COLOUR_SIDELINE, [MAP_SIZE[0], 0], [MAP_SIZE[0], MAP_SIZE[1] * 2], 1)
	pygame.draw.line(screen, COLOUR_RANGE_300, [MAP_SIZE[0] + 1, 0], [MAP_SIZE[0] + 1, MAP_SIZE[1]], 1)
	
	# Time line
	pygame.draw.line(screen, COLOUR_SIDELINE, [MAP_SIZE[0] + 2, SCREEN_SIZE[1] - 40], [SCREEN_SIZE[0], SCREEN_SIZE[1] - 40], 1)
	pygame.draw.line(screen, COLOUR_SIDELINE, [MAP_SIZE[0] + 2, SCREEN_SIZE[1] - 80], [SCREEN_SIZE[0], SCREEN_SIZE[1] - 80], 1)
	
	surface = square_font.render("DATETIME", False, COLOUR_WHITE)
	screen.blit(surface, [MAP_SIZE[0] + 5, 561])
	
	surface = square_font.render("UPTIME", False, COLOUR_WHITE)
	screen.blit(surface, [MAP_SIZE[0] + 5, 521])
	
	# Range circles
	if show_range_circles:
		pygame.draw.circle(screen, COLOUR_RANGE_25, [CENTRE_X, CENTRE_Y], 25, 1)
		pygame.draw.circle(screen, COLOUR_RANGE_50, [CENTRE_X, CENTRE_Y], 50, 1)
		pygame.draw.circle(screen, COLOUR_RANGE_100, [CENTRE_X, CENTRE_Y], 100, 1)
		pygame.draw.circle(screen, COLOUR_RANGE_150, [CENTRE_X, CENTRE_Y], 150, 1)
		pygame.draw.circle(screen, COLOUR_RANGE_200, [CENTRE_X, CENTRE_Y], 200, 1)
		pygame.draw.circle(screen, COLOUR_RANGE_250, [CENTRE_X, CENTRE_Y], 250, 1)
		pygame.draw.circle(screen, COLOUR_RANGE_300, [CENTRE_X, CENTRE_Y], 300, 1)
	
	if show_crosshair:
		if not small_crosshair:
			# Crosshair V
			pygame.draw.line(screen, COLOUR_CROSSHAIR, [CENTRE_X, 0], [CENTRE_X, CENTRE_Y * 2], 1)
			
			# Crosshair H
			pygame.draw.line(screen, COLOUR_CROSSHAIR, [0, CENTRE_Y], [CENTRE_X * 2, CENTRE_Y], 1)
			
		else:
			# Crosshair V
			pygame.draw.line(screen, COLOUR_CROSSHAIR, [CENTRE_X, CENTRE_Y - 3], [CENTRE_X, CENTRE_Y + 3], 1)
			
			# Crosshair H
			pygame.draw.line(screen, COLOUR_CROSSHAIR, [CENTRE_X - 3, CENTRE_Y], [CENTRE_X + 3, CENTRE_Y], 1)
		
		
	# Copyright text
	uc_split = USER_COPYRIGHT.split("\n")
	
	y_point = 3
	
	for uc_text in uc_split:
		copy_surface = square_font.render(uc_text, True, COLOUR_BLACK)
		screen.blit(copy_surface, [6, y_point])
		
		copy_surface = square_font.render(uc_text, True, COLOUR_WHITE)
		screen.blit(copy_surface, [5, y_point - 1])
		
		y_point += 8
	
	
	surface = square_font.render(COPYRIGHT_MESSAGE_1, True, COLOUR_BLACK)
	screen.blit(surface, [6, 580])
	
	surface = square_font.render(COPYRIGHT_MESSAGE_1, True, COLOUR_WHITE)
	screen.blit(surface, [5, 579])
	
	
	surface = square_font.render(COPYRIGHT_MESSAGE_2, True, COLOUR_BLACK)
	screen.blit(surface, [6, 588])
	
	surface = square_font.render(COPYRIGHT_MESSAGE_2, True, COLOUR_WHITE)
	screen.blit(surface, [5, 587])
	
	
	# Range text
	surface = square_font.render("Range: " + str(zoom_distance) + "miles", True, COLOUR_BLACK)
	screen.blit(surface, [514, 588])
	
	surface = square_font.render("Range: " + str(zoom_distance) + "miles", True, COLOUR_WHITE)
	screen.blit(surface, [513, 587])
	
	
	# Update when done
	pygame.display.update()
	
def rotateLogs():
	myconn = []
	connectToDatabase(myconn)
	
	
	executeSQLCommand("START TRANSACTION", myconn)
	
	for q in range(5, 0, -1):
		executeSQLCommand("DELETE FROM tblStrikesPersistence%d" % q, myconn)
		executeSQLCommand("INSERT INTO tblStrikesPersistence%d(X, Y, DateTimeOfStrike) SELECT X, Y, DateTimeOfStrike FROM tblStrikesPersistence%d" % (q, q - 1), myconn)
	
	executeSQLCommand("DELETE FROM tblStrikesPersistence0", myconn)
	executeSQLCommand("COMMIT", myconn)
	
	
	# Re-draw the base screen and plot "old" strikes
	renderScreen()
	
	# Old strikes
	strike_colour = None
	
	x = 0
	y = 0
	
	for q in range(5, -1, -1):
		results = executeSQLQuery("SELECT DISTINCT X, Y FROM tblStrikesPersistence%d ORDER BY DateTimeOfStrike" % q, myconn)
		
		if not results is None:
			if q == 1:
				strike_colour = COLOUR_OLD_STRIKE_1
				
			elif q == 2:
				strike_colour = COLOUR_OLD_STRIKE_2
				
			elif q == 3:
				strike_colour = COLOUR_OLD_STRIKE_3
				
			elif q == 4:
				strike_colour = COLOUR_OLD_STRIKE_4
				
			elif q == 5:
				strike_colour = COLOUR_OLD_STRIKE_5
				
				
			for row in results.fetch_row(0):
				x = int(row[0])
				y = int(row[1])
				
				plotStrikeXY(x + CENTRE_X - (MAP_SIZE[0] / 2), y + CENTRE_Y - (MAP_SIZE[1] / 2), strike_colour)
				
			
	disconnectFromDatabase(myconn)
	
def ssbtVote(unit, strike):
	myconn = []
	connectToDatabase(myconn)
	
	t = datetime.now()
	
	
	# First, make a vote for the strike
	executeSQLCommand("INSERT INTO tblSSBTElection(UnitID, StrikeDistance, StrikeAngle, DateTimeOfStrike, DateTimeOfVote) VALUES(%d, %s, %s, '%s', '%s')" % (unit, strike[0], strike[1], strike[2], t), myconn)
	
	# Second, see if we can find strike-pairs for "bi-angulation"
	results = executeSQLQuery("SELECT ID, UnitID, StrikeDistance, StrikeAngle FROM tblSSBTElection ORDER BY DateTimeOfStrike, StrikeDistance, StrikeAngle, UnitID", myconn)
	
	if not results is None:
		for row in results.fetch_row(0):
			unit = int(row[0])
			distance = float(row[1])
			angle = float(row[2])
			
		# Third, see if we can publish the manifesto
	
	disconnectFromDatabase(myconn)
	
def trac():
	global screen, trac_active, trac_counter, trac_most_active, trac_storms_total
	
	
	# See if we can find a cluster of strikes within a set mileage
	if trac_enabled and database_engine <> DB_NONE:
		print ""
		print "TRAC: Starting..."
		
		# Inform the user TRAC is busy
		updateTRACStatus(2)
		
		
		myconn = []
		connectToDatabase(myconn)
		
		print "TRAC: Preparing TRAC Report..."
		
		if path.exists(TRAC_REPORT):
			remove(TRAC_REPORT)
			
		if path.exists(XML_TRAC_REPORT):
			remove(XML_TRAC_REPORT)
		
		t = datetime.now()
		
		current_time = str(t.strftime("%d/%m/%Y %H:%M:%S"))
		
		trac_report = file(TRAC_REPORT, "w")
		trac_report.write("*** StormForce TRAC Report generated " + current_time + "\n")
		
		xml_trac_report = minidom.Document()
		sfsettings = xml_trac_report.createElement("StormForce")
		xml_trac_report.appendChild(sfsettings)
		
		var = xml_trac_report.createElement("TRACReport")
		var.setAttribute("ReportGenerated", str(current_time))
		var.setAttribute("StormForceVersion", str(VERSION))
		var.setAttribute("TRACVersion", str(TRAC_VERSION))
		sfsettings.appendChild(var)
		
		
		# TRAC originally only worked on a distance of 300 miles, we should be able to scale it for other distances
		SCALING = 300. / float(zoom_distance)
		
		if debug_mode:
			print "TRAC: Scaling factor is %s." % SCALING
		
		TRAC_FULL = 0
		
		trac_most_active = ""
		trac_storms_total = 0
		
		
		if TRAC_STORM_WIDTH % 2 == 0:
			TRAC_FULL = int(TRAC_STORM_WIDTH * SCALING)
			
		else:
			TRAC_FULL = int((TRAC_STORM_WIDTH - 1) * SCALING)
			
		TRAC_HALF = TRAC_FULL / 2
		TRAC_THIRD = TRAC_FULL / 3
		TRAC_QUARTER = TRAC_HALF / 2
		
		if debug_mode:
			print "TRAC: TRAC_FULL equals %s." % TRAC_FULL
			print "TRAC: TRAC_HALF equals %s." % TRAC_HALF
			print "TRAC: TRAC_THIRD equals %s." % TRAC_THIRD
			print "TRAC: TRAC_QUARTER equals %s." % TRAC_QUARTER
		
		
		print "TRAC: Calculating and plotting..."
		
		trac_active = False
		
		last_rate = 0
		
		# This will count the number of strikes in each grid
		for y in range(0, MAP_MATRIX_SIZE[1], TRAC_FULL):
			for x in range(0, MAP_MATRIX_SIZE[0], TRAC_FULL):
				
				grid_result = danLookup("COUNT(ID)", "vwStrikesPersistence", "(X >= %d AND X < %d) AND (Y >= %d AND Y < %d)" % (x, x + TRAC_FULL, y, y + TRAC_FULL), myconn)
				
				if not grid_result is None:
					count = int(grid_result)
						
						
					# Now start the main bit
					if debug_mode:
						# Draw grid for testing
						pygame.draw.line(screen, COLOUR_SIDELINE, [x, y], [x, y], 1)
					
					
					if count >= TRAC_SENSITIVITY:
						# First, see if the strikes are grouping in an area of the grid so we can offset it
						trac_active = True
						trac_storms_total += 1
						
						
						top_left = int(danLookup("COUNT(ID)", "vwStrikesPersistence", "(X >= %d AND X < %d) AND (Y >= %d AND Y < %d)" % (x, x + TRAC_HALF, y, y + TRAC_HALF), myconn))
						top_right = int(danLookup("COUNT(ID)", "vwStrikesPersistence", "(X >= %d AND X < %d) AND (Y >= %d AND Y < %d)" % (x + TRAC_HALF, x + TRAC_FULL, y, y + TRAC_HALF), myconn))
						bottom_left = int(danLookup("COUNT(ID)", "vwStrikesPersistence", "(X >= %d AND X < %d) AND (Y >= %d AND Y < %d)" % (x, x + TRAC_HALF, y + TRAC_HALF, y + TRAC_FULL), myconn))
						bottom_right = int(danLookup("COUNT(ID)", "vwStrikesPersistence", "(X >= %d AND X < %d) AND (Y >= %d AND Y < %d)" % (x + TRAC_HALF, x + TRAC_FULL, y + TRAC_HALF, y + TRAC_FULL), myconn))
						
						x_offset = 0
						y_offset = 0
						
						total_count = top_left + top_right + bottom_left + bottom_right
						
						if debug_mode:
							print "TRAC: A: %s %s %s %s" % (top_left, top_right, bottom_left, bottom_right)
						
						# Get the percentages
						tl = (float(top_left) / float(total_count)) * TRAC_THIRD
						tr = (float(top_right) / float(total_count)) * TRAC_THIRD
						bl = (float(bottom_left) / float(total_count)) * TRAC_THIRD
						br = (float(bottom_right) / float(total_count)) * TRAC_THIRD
						
						if debug_mode:
							print "TRAC: B: %s %s %s %s" % (tl, tr, bl, br)
						
						# The greater percentage will make the centre offset to the corner
						x_offset = x_offset + -tl
						y_offset = y_offset + -tl
							
						x_offset = x_offset + tr
						y_offset = y_offset + -tr
							
						x_offset = x_offset + -bl
						y_offset = y_offset + bl
							
						x_offset = x_offset + br
						y_offset = y_offset + br
						
						if debug_mode:
							print "TRAC: C: %s %s" % (x_offset, y_offset)
						
						
						# Calculate the degrees and miles from the X and Y points
						new_x = float(x + x_offset)
						new_y = float(y + y_offset)
						
						o = 0.
						a = 0.
						deg_offset = 0
						
						if (new_x >= 0 and new_x < 300) and (new_y >= 0 and new_y < 300):
							# Top left
							o = 300 - new_x
							a = 300 - new_y
							
							deg_offset = 270
							
						elif (new_x >= 300 and new_x < 600) and (new_y >= 0 and new_y < 300):
							# Top right
							o = new_x - 300
							a = 300 - new_y
							
							deg_offset = 0
							
						elif (new_x >= 0 and new_x < 300) and (new_y >= 300 and new_y < 600):
							# Bottom left
							o = 300 - new_x
							a = new_y - 300
							
							deg_offset = 180
							
						else:
							# Bottom right
							o = new_x - 300
							a = new_y - 300
							
							deg_offset = 90
							
						# Numbers will be zero based, so add one
						o += 1
						a += 1
						
						if debug_mode:
							print "TRAC: O = %f, A = %f" % (o, a)
							
						# Time for a bit of trigonometry
						degx = degrees(atan(o / a))
						deg = degx + deg_offset
						distance = sqrt(pow(o, 2) + pow(a, 2))
						
						if debug_mode:
							print "TRAC: Degrees = %f, X = %f, H = %f" % (deg, degx, distance)
							
						# Scale the distance and make adjust it to the centre of the storm
						distance /= SCALING
						distance -= TRAC_HALF
						
						
						first_recorded_activity = danLookup("MIN(DateTimeOfStrike)", "vwStrikesPersistence", "(X >= %d AND X < %d) AND (Y >= %d AND Y < %d)" % (x, x + TRAC_FULL, y, y + TRAC_FULL), myconn)
						last_recorded_activity = danLookup("MAX(DateTimeOfStrike)", "vwStrikesPersistence", "(X >= %d AND X < %d) AND (Y >= %d AND Y < %d)" % (x, x + TRAC_FULL, y, y + TRAC_FULL), myconn)
						
						guid = uuidNotRandom("%d,%d,%d,%d,%s" % (x, x + TRAC_FULL, y, y + TRAC_FULL, first_recorded_activity))
						crc32 = str(hex(zlib.crc32(guid))).replace("0x", "").replace("-", "")
						
						if len(crc32) < 8:
							q = 8 - len(crc32)
							padding = "0" * q
							
							crc32 = padding + crc32
						
						if debug_mode:
							print "TRAC: GUID = %s, CRC32 = %s" % (guid, crc32)
						
						
						current_strike_rate = 0
						peak_strike_rate = 0
						
						if database_engine == DB_MYSQL:
							current_strike_rate = ifNoneReturnZero(danLookup("COUNT(ID)", "vwStrikesPersistence", "DateTimeOfStrike >= DATE_SUB(SYSDATE(), INTERVAL 1 MINUTE) AND (X >= %d AND X < %d) AND (Y >= %d AND Y < %d)" % (x, x + TRAC_FULL, y, y + TRAC_FULL), myconn))
							
						peak_strike_rate = ifNoneReturnZero(danLookup("MAX(StrikeCount)", "vwStrikesPeak", "(MinX >= %d AND MinX < %d) AND (MinY >= %d AND MinY < %d) LIMIT 1" % (x, x + TRAC_FULL, y, y + TRAC_FULL), myconn))
							
							
						if peak_strike_rate == 0:
							peak_strike_rate = current_strike_rate
							
							
						# Since we have the strike rate we can determine the classification of the storm
						intensity_class = "N/A"
						intensity_trend = "N/A"
						intensity_trend_symbol = ""
						
						if current_strike_rate < 10:
							intensity_class = "Very Weak"
							
						elif current_strike_rate < 20:
							intensity_class = "Weak"
							
						elif current_strike_rate < 40:
							intensity_class = "Moderate"
							
						elif current_strike_rate < 50:
							intensity_class = "Strong"
							
						elif current_strike_rate < 60:
							intensity_class = "Very Strong"
							
						else:
							intensity_class = "Severe"
							
							
						# Calculate the trend by counting the rises and the falls based on the average strike rate, not the best way but can be improved later
						rises = 0
						falls = 0
						
						results = executeSQLQuery("SELECT StrikeCount FROM vwStrikesPeak WHERE (MinX >= %d AND MinX < %d) AND (MinY >= %d AND MinY < %d)" % (x, x + TRAC_FULL, y, y + TRAC_FULL), myconn)
						
						average_strike_count = float(ifNoneReturnZero(danLookup("SUM(StrikeCount) / COUNT(*)", "vwStrikesPeak", "(MinX >= %d AND MinX < %d) AND (MinY >= %d AND MinY < %d) LIMIT 1" % (x, x + TRAC_FULL, y, y + TRAC_FULL), myconn)))
						
						if not results is None:
							diff = 0.
							
							if database_engine == DB_MYSQL:
								for row in results.fetch_row(0):
									diff = float(int(row[0]) - average_strike_count)
									
							
							if diff > 0.:
								rises += 1
								
							elif diff < 0.:
								falls += 1
							
						if debug_mode:
							print "TRAC: Rises = %d, falls = %d" % (rises, falls)
						
						if rises > falls:
							intensity_trend = "Intensifying"
							intensity_trend_symbol = "^"
							
						elif falls > rises:
							intensity_trend = "Weakening"
							intensity_trend_symbol = "."
							
						else:
							intensity_trend = "No Change"
							intensity_trend_symbol = "-"
							
						
						# Show where we think the storm is
						amount = 0.
						
						if current_strike_rate > 50:
							amount = 1.
							
						else:
							amount = current_strike_rate / 50.
							
						
						points = []
						
						if strike_shape == SHAPE_SQUARE:
							points.append([x + x_offset + CENTRE_X - (MAP_SIZE[0] / 2), y + y_offset + CENTRE_Y - (MAP_SIZE[1] / 2)])
							points.append([x + TRAC_FULL + x_offset + CENTRE_X - (MAP_SIZE[0] / 2), y + y_offset + CENTRE_Y - (MAP_SIZE[1] / 2)])
							points.append([x + TRAC_FULL + x_offset + CENTRE_X - (MAP_SIZE[0] / 2), y + TRAC_FULL + y_offset + CENTRE_Y - (MAP_SIZE[1] / 2)])
							points.append([x + x_offset + CENTRE_X - (MAP_SIZE[0] / 2), y + TRAC_FULL + y_offset + CENTRE_Y - (MAP_SIZE[1] / 2)])
							
						elif strike_shape == SHAPE_TRIANGLE:
							points.append([x + TRAC_HALF + x_offset + CENTRE_X - (MAP_SIZE[0] / 2), y + y_offset + CENTRE_Y - (MAP_SIZE[1] / 2)])
							points.append([x + TRAC_FULL + x_offset + CENTRE_X - (MAP_SIZE[0] / 2), y + TRAC_HALF + y_offset + CENTRE_Y - (MAP_SIZE[1] / 2)])
							points.append([x + TRAC_HALF + x_offset + CENTRE_X - (MAP_SIZE[0] / 2), y + TRAC_FULL + y_offset + CENTRE_Y - (MAP_SIZE[1] / 2)])
							points.append([x + x_offset + CENTRE_X - (MAP_SIZE[0] / 2), y + TRAC_HALF + y_offset + CENTRE_Y - (MAP_SIZE[1] / 2)])
							
						elif strike_shape == SHAPE_CIRCLE:
							rect = pygame.draw.circle(screen, TRAC_COLOUR, [int(x + TRAC_HALF + x_offset + CENTRE_X - (MAP_SIZE[0] / 2)), int(y + TRAC_HALF + y_offset + CENTRE_Y - (MAP_SIZE[1] / 2))], TRAC_HALF, 1)
						
						
						if (strike_shape == SHAPE_SQUARE or strike_shape == SHAPE_TRIANGLE):
							rect = pygame.draw.polygon(screen, progressBarColour(TRAC_GRADIENT_MIN, TRAC_GRADIENT_MAX, int(TRAC_FULL * amount), TRAC_FULL), points, 1)
							
						pygame.display.update(rect)
						
						
						# Draw the intensity as a "progress bar" with the storm ID as well - the CRC32 length will be 40 pixels
						id_surface = square_font.render(crc32 + intensity_trend_symbol + str(current_strike_rate), True, COLOUR_BLACK)
						screen.blit(id_surface, [(x + x_offset + TRAC_HALF + CENTRE_X - (MAP_SIZE[0] / 2)) - 29, y + y_offset + TRAC_FULL + 3 + CENTRE_Y - (MAP_SIZE[1] / 2)])
						
						id_surface = square_font.render(crc32 + intensity_trend_symbol + str(current_strike_rate), True, COLOUR_WHITE)
						screen.blit(id_surface, [(x + x_offset + TRAC_HALF + CENTRE_X - (MAP_SIZE[0] / 2)) - 30, y + y_offset + TRAC_FULL + 2 + CENTRE_Y - (MAP_SIZE[1] / 2)])
						
						
						# Make log of the storm in the database
						tracid = ifNoneReturnZero(danLookup("ID", "tblTRACHeader", "GID = '%s'" % guid, myconn))
						
						if tracid == 0:
							# Storm not found in database, add new entry
							if not executeSQLCommand("INSERT INTO tblTRACHeader(GID, CRC32, DateTimeOfDiscovery, Bearing, Distance) VALUES('%s', '%s', '%s', %s, %s)" % (guid, crc32, first_recorded_activity, deg, distance), myconn):
								print "TRAC: Failed to write the header for storm ID %s." % crc32
							
							else:
								tracid = ifNoneReturnZero(danLookup("ID", "tblTRACHeader", "GID = '%s'" % guid, myconn))
								
								if tracid == 0:
									# Failed!
									print "TRAC: Failed to locate the newly created record for storm ID %s." % crc32
									
						# Double-check
						if tracid > 0:
							# Write the details
							if not executeSQLCommand("INSERT INTO tblTRACDetails(HeaderID, DateTimeOfReading, DateTimeOfLastStrike, CurrentStrikeRate, TotalStrikes) VALUES(%d, '%s', '%s', %d, %d)" % (tracid, datetime.now(), last_recorded_activity, current_strike_rate, total_count), myconn):
								print "TRAC: Failed to write out the details for storm ID %s." % crc32
								
						if count > last_rate:
							last_rate = count
							trac_most_active = crc32 + intensity_trend_symbol + str(current_strike_rate)
						
						
						# Write the text version of the report
						trac_report.write("\n========================================================\n")
						trac_report.write("Thunderstorm ID %s detected %s\n" % (crc32, first_recorded_activity))
						trac_report.write("\n")
						trac_report.write("Storm location bearing %g degrees distance %g miles\n" % (deg, distance))
						trac_report.write("\n")
						trac_report.write("Last recorded activity: %s\n" % last_recorded_activity)
						trac_report.write("Intensity class:        %s\n" % intensity_class)
						trac_report.write("Intensity trend:        %s\n" % intensity_trend)
						trac_report.write("\n")
						trac_report.write("Current strike rate:    %d/min\n" % current_strike_rate)
						trac_report.write("Peak strike rate:       %d/min\n" % peak_strike_rate)
						trac_report.write("Average strike rate:    %g/min\n" % average_strike_count)
						trac_report.write("\n")
						trac_report.write("Cloud-Ground strikes:   %d\n" % total_count)
						trac_report.write("Total recorded strikes: %d\n" % total_count)
						trac_report.write("========================================================\n")
						
						# Now the XML version of the report
						var = xml_trac_report.createElement("Thunderstorm")
						var.setAttribute("GUID", str(guid))
						var.setAttribute("CRC32", str(crc32))
						var.setAttribute("DetectedOn", str(first_recorded_activity))
						var.setAttribute("Bearing", str(deg))
						var.setAttribute("Distance", str(distance))
						var.setAttribute("LastRecordedActivity", str(last_recorded_activity))
						var.setAttribute("IntensityClass", str(intensity_class))
						var.setAttribute("IntensityTrend", str(intensity_trend))
						var.setAttribute("CurrentStrikeRate", str(current_strike_rate))
						var.setAttribute("PeakStrikeRate", str(peak_strike_rate))
						var.setAttribute("AverageStrikeRate", str(average_strike_count))
						var.setAttribute("CGStrikes", str(total_count))
						var.setAttribute("TotalRecordedStrikes", str(total_count))
						sfsettings.appendChild(var)
		
		if not trac_active:
			trac_report.write("\nNo thunderstorms are being tracked.\n")
			
		else:
			playSound(TRAC_ACTIVE_SOUND)
			
			
		trac_report.write("\n*** TRAC Report end - StormForce v" + VERSION + " (TRAC v" + TRAC_VERSION + ")\n")
		trac_report.close()
		
		xml_trac = file(XML_TRAC_REPORT, "w")
		xml_trac.write(xml_trac_report.toprettyxml())
		xml_trac.close()
		
		if curl_arguments <> "":
			uploadFileViaCurl(TRAC_REPORT)
		
		
		updateTRACMostActiveArea()
		updateTRACStatus(trac_active)
		updateTRACStormsArea()
		
		pygame.display.update()
		
		disconnectFromDatabase(myconn)
		
		
		print "TRAC: Completed."
		
	else:
		if database_engine == DB_NONE:
			print "TRAC: TRAC requires a database to function, please set one using the XML settings file."
	
def transmitXML(xmlin):
	if listener_multicast_address <> "" and listener_multicast_port > 0 and listener_multicast_ttl >= 0:
		threading.Thread(target = transmitXMLMulticastThread, args = (xmlin,)).start()
	
	if listener_tcp_port > 0:
		for cli in listener_tcp_auth:
			threading.Thread(target = transmitXMLTCPThread, args = (cli, xmlin,)).start()
	
	if listener_udp_port > 0:
		for cli in listener_udp_auth:
			threading.Thread(target = transmitXMLUDPThread, args = (cli, xmlin,)).start()
	
def transmitXMLMulticastThread(xmlin):
	# Slightly different when doing multicast...
	try:
		
		mc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		mc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		try:
			mc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			
		except AttributeError:
			pass
		
		mc.bind(("", listener_multicast_port))
		mc.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, listener_multicast_ttl)
		
		
		data = None
		
		if listener_multicast_port_compression == "bz2":
			data = bz2.compress(xmlin)
			
		elif listener_multicast_port_compression == "lzma":
			data = pylzma.compress(xmlin)
			
		else:
			data = xmlin
		
		mc.sendto(data, (listener_multicast_address, listener_multicast_port))
		mc = None
		
	except Exception, e:
		print e
		print "Error: Failed to broadcast XML via multicast."
	
def transmitXMLTCPThread(cli, xmlin):
	if listener_tcp_port_compression == "bz2":
		data = bz2.compress(xmlin)
		
	elif listener_tcp_port_compression == "lzma":
		data = pylzma.compress(xmlin)
		
	else:
		data = xmlin
		
	cli.sendall(data)
		
def transmitXMLUDPThread(cli, xmlin):
	if listener_udp_port_compression == "bz2":
		data = bz2.compress(xmlin)
		
	elif listener_udp_port_compression == "lzma":
		data = pylzma.compress(xmlin)
		
	else:
		data = xmlin
		
	cli[0].sendto(data, cli[1])
	
def updateDatabase(conn = []):
	##########
	# Tables #
	##########
	executeSQLCommand("START TRANSACTION", conn)
	
	
	# tblStrikesPersistence0
	executeSQLCommand("CREATE TABLE tblStrikesPersistence0(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = Memory", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence0 ADD COLUMN X smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence0 ADD COLUMN Y smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence0 ADD COLUMN DateTimeOfStrike datetime NOT NULL", conn)
	
	
	# tblStrikesPersistence1
	executeSQLCommand("CREATE TABLE tblStrikesPersistence1(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = Memory", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence1 ADD COLUMN X smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence1 ADD COLUMN Y smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence1 ADD COLUMN DateTimeOfStrike datetime NOT NULL", conn)
	
	
	# tblStrikesPersistence2
	executeSQLCommand("CREATE TABLE tblStrikesPersistence2(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = Memory", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence2 ADD COLUMN X smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence2 ADD COLUMN Y smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence2 ADD COLUMN DateTimeOfStrike datetime NOT NULL", conn)
	
	
	# tblStrikesPersistence3
	executeSQLCommand("CREATE TABLE tblStrikesPersistence3(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = Memory", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence3 ADD COLUMN X smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence3 ADD COLUMN Y smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence3 ADD COLUMN DateTimeOfStrike datetime NOT NULL", conn)
	
	
	# tblStrikesPersistence4
	executeSQLCommand("CREATE TABLE tblStrikesPersistence4(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = Memory", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence4 ADD COLUMN X smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence4 ADD COLUMN Y smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence4 ADD COLUMN DateTimeOfStrike datetime NOT NULL", conn)
	
	
	# tblStrikesPersistence5
	executeSQLCommand("CREATE TABLE tblStrikesPersistence5(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = Memory", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence5 ADD COLUMN X smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence5 ADD COLUMN Y smallint UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikesPersistence5 ADD COLUMN DateTimeOfStrike datetime NOT NULL", conn)
	
	
	# tblStrikes
	executeSQLCommand("CREATE TABLE tblStrikes(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = MyISAM", conn)
	executeSQLCommand("ALTER TABLE tblStrikes ADD COLUMN DateTimeOfStrike datetime NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikes ADD COLUMN MillisecondsOfStrike int UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikes ADD COLUMN CorrectedStrikeDistance decimal(6,3) UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikes ADD COLUMN UncorrectedStrikeDistance decimal(6,3) UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikes ADD COLUMN StrikeType nvarchar(2) NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikes ADD COLUMN StrikePolarity nvarchar(1) NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblStrikes ADD COLUMN StrikeAngle decimal(4,1) UNSIGNED NOT NULL", conn)
	
	
	# tblSystem
	executeSQLCommand("CREATE TABLE tblSystem(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = MyISAM", conn)
	executeSQLCommand("ALTER TABLE tblSystem ADD COLUMN DatabaseVersion int NOT NULL", conn)
	
	rowcount = int(ifNoneReturnZero(danLookup("COUNT(ID)", "tblSystem", "", conn)))
	
	try:
		if rowcount == 0:
			# First time, create the row
			cur = conn[0].cursor()
			cur.execute("INSERT INTO tblSystem(DatabaseVersion) VALUES(0)")
			
			conn[0].commit()
			
	except:
		pass
	
	
	# tblElectricFieldStrength
	executeSQLCommand("CREATE TABLE tblElectricFieldStrength(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = MyISAM", conn)
	executeSQLCommand("ALTER TABLE tblElectricFieldStrength ADD COLUMN DateTimeOfMeasurement datetime NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblElectricFieldStrength ADD COLUMN kVm decimal(4,2) UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblElectricFieldStrength ADD COLUMN MillisecondsOfMeasurement int UNSIGNED NOT NULL", conn)
	
	
	# tblTRACHeader
	executeSQLCommand("CREATE TABLE tblTRACHeader(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = MyISAM", conn)
	executeSQLCommand("ALTER TABLE tblTRACHeader ADD COLUMN GID nvarchar(40) NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblTRACHeader ADD COLUMN CRC32 nvarchar(8) NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblTRACHeader ADD COLUMN DateTimeOfDiscovery datetime NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblTRACHeader ADD COLUMN Bearing decimal(10,5) UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblTRACHeader ADD COLUMN Distance decimal(10,5) UNSIGNED NOT NULL", conn)
	
	
	# tblTRACDetails
	executeSQLCommand("CREATE TABLE tblTRACDetails(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = MyISAM", conn)
	executeSQLCommand("ALTER TABLE tblTRACDetails ADD COLUMN HeaderID bigint NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblTRACDetails ADD COLUMN DateTimeOfReading datetime NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblTRACDetails ADD COLUMN DateTimeOfLastStrike datetime NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblTRACDetails ADD COLUMN CurrentStrikeRate int NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblTRACDetails ADD COLUMN TotalStrikes int NOT NULL", conn)
	
	
	# tblSSBTElection
	executeSQLCommand("CREATE TABLE tblSSBTElection(ID bigint UNSIGNED NOT NULL auto_increment PRIMARY KEY) ENGINE = Memory", conn)
	executeSQLCommand("ALTER TABLE tblSSBTElection ADD COLUMN StrikeDistance decimal(6,3) UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblSSBTElection ADD COLUMN StrikeAngle decimal(4,1) UNSIGNED NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblSSBTElection ADD COLUMN DateTimeOfStrike datetime NOT NULL", conn)
	executeSQLCommand("ALTER TABLE tblSSBTElection ADD COLUMN DateTimeOfVote datetime NOT NULL", conn)
	
	
	
	#########
	# Views #
	#########
	executeSQLCommand("DROP VIEW vwStrikesPersistence", conn)
	executeSQLCommand("CREATE VIEW vwStrikesPersistence AS SELECT ID, X, Y, DateTimeOfStrike FROM tblStrikesPersistence0 UNION ALL SELECT ID, X, Y, DateTimeOfStrike FROM tblStrikesPersistence1", conn)
	
	executeSQLCommand("DROP VIEW vwStrikesPeak", conn)
	executeSQLCommand("CREATE VIEW vwStrikesPeak AS SELECT COUNT(ID) AS StrikeCount, CAST(DATE_FORMAT(DateTimeOfStrike, '%Y/%m/%d %H:%i:00') AS DATETIME) AS PeakTime, MIN(X) AS MinX, MIN(Y) AS MinY FROM vwStrikesPersistence GROUP BY CAST(DATE_FORMAT(DateTimeOfStrike, '%Y/%m/%d %H:%i:00') AS DATETIME)", conn)
	
	
	
	###########
	# Indices #
	###########
	executeSQLCommand("CREATE INDEX GridRef0 ON tblStrikesPersistence0 (X, Y)", conn)
	executeSQLCommand("CREATE INDEX GridRef1 ON tblStrikesPersistence1 (X, Y)", conn)
	executeSQLCommand("CREATE INDEX GridRef2 ON tblStrikesPersistence2 (X, Y)", conn)
	executeSQLCommand("CREATE INDEX GridRef3 ON tblStrikesPersistence3 (X, Y)", conn)
	executeSQLCommand("CREATE INDEX GridRef4 ON tblStrikesPersistence4 (X, Y)", conn)
	executeSQLCommand("CREATE INDEX GridRef5 ON tblStrikesPersistence5 (X, Y)", conn)
	
	
	
	###########
	# Updates #
	###########
	curr_db_version = int(ifNoneReturnZero(danLookup("DatabaseVersion", "tblSystem", "", conn)))
	
	if curr_db_version < DB_VERSION:
		# Update needed
		
		# Changed to decimal since the StormTracker provides higher precision
		executeSQLCommand("ALTER TABLE tblStrikes MODIFY COLUMN CorrectedStrikeDistance decimal(6,3) UNSIGNED NOT NULL", conn)
		executeSQLCommand("ALTER TABLE tblStrikes MODIFY COLUMN UncorrectedStrikeDistance decimal(6,3) UNSIGNED NOT NULL", conn)
		
		# Finally, update the db version
		executeSQLCommand("UPDATE tblSystem SET DatabaseVersion = %d" % DB_VERSION, conn)
	
	executeSQLCommand("COMMIT", conn)
	
def updateLD250CloseArea():
	rect = clearLD250CloseArea()
	
	close_surface = small_number_font.render("%03d %06d" % (ldunit_close_minute, ldunit_close_total), False, CLOSE_TEXT_COLOUR)
	screen.blit(close_surface, LD250_CLOSE_VALUE)
	
	pygame.display.update(rect)
	
def updateLD250CloseCount():
	global ldunit_close_total, ldunit_close_minute, number_font, screen
	
	
	ldunit_close_total += 1
	ldunit_close_minute += 1
	
	if ldunit_close_total > 999999:
		ldunit_close_total = 1
		
	if ldunit_close_minute > 999:
		ldunit_close_minute = 1
	
	updateLD250CloseArea()
	
	playSound(CLOSE_SOUND)
	
def updateLD250NoiseArea():
	rect = clearLD250NoiseArea()
	
	noise_surface = small_number_font.render("%03d %06d" % (ldunit_noise_minute, ldunit_noise_total), False, NOISE_TEXT_COLOUR)
	screen.blit(noise_surface, LD250_NOISE_VALUE)
	
	pygame.display.update(rect)
	
def updateLD250NoiseCount():
	global ldunit_noise_total, ldunit_noise_minute, number_font, screen
	
	
	ldunit_noise_total += 1
	ldunit_noise_minute += 1
	
	if ldunit_noise_total > 999999:
		ldunit_noise_total = 1
		
	if ldunit_noise_minute > 999:
		ldunit_noise_minute = 1
	
	updateLD250NoiseArea()
	
def updateLD250StrikeArea():
	rect = clearLD250StrikeArea()
	
	strike_surface = small_number_font.render("%03d %06d %03d" % (ldunit_strikes_minute, ldunit_strikes_total, ldunit_strikes_oor), False, STRIKE_TEXT_COLOUR)
	screen.blit(strike_surface, LD250_STRIKES_VALUE)
	
	pygame.display.update(rect)
	
def updateLD250StrikeCount(isoor):
	global number_font, ldunit_strikes_oor, screen, ldunit_strikes_total, ldunit_strikes_minute
	
	
	if not isoor:
		ldunit_strikes_total += 1
		
	else:
		ldunit_strikes_oor += 1
		
	ldunit_strikes_minute += 1
	
	
	if ldunit_strikes_total > 999999:
		ldunit_strikes_total = 1
		
	if ldunit_strikes_minute > 999:
		ldunit_strikes_minute = 1
		
	if ldunit_strikes_oor > 999:
		ldunit_strikes_oor = 1
	
	
	updateLD250StrikeArea()
	
	playSound(STRIKE_SOUND)
	
def updateSSBTManifesto(status):
	rect = clearSSBTManifestoArea()
	
	text = ""
	colour = None
	
	if status == MANIFESTO_ELECTION:
		text = "Election"
		colour = COLOUR_YELLOW
		
	elif status == MANIFESTO_PUBLISHED:
		text = "Published"
		colour = COLOUR_ALARM_INACTIVE
		
	elif status == MANIFESTO_UNPUBLISHED:
		text = "Unpublished"
		colour = COLOUR_ALARM_ACTIVE
	
	ssbt_surface = square_font.render(text, True, colour)
	screen.blit(ssbt_surface, SSBT_MANIFESTO_VALUE)
	
	pygame.display.update(rect)
	
def updateSTPCICloseArea():
	rect = clearSTPCICloseArea()
	
	close_surface = small_number_font.render("%03d %06d" % (stunit_close_minute, stunit_close_total), False, CLOSE_TEXT_COLOUR)
	screen.blit(close_surface, STPCI_CLOSE_VALUE)
	
	pygame.display.update(rect)
	
def updateSTPCICloseCount():
	global stunit_close_total, stunit_close_minute, number_font, screen
	
	
	stunit_close_total += 1
	stunit_close_minute += 1
	
	if stunit_close_total > 999999:
		stunit_close_total = 1
		
	if stunit_close_minute > 999:
		stunit_close_minute = 1
	
	updateSTPCICloseArea()
	
	playSound(CLOSE_SOUND)
	
def updateSTPCINoiseArea():
	rect = clearSTPCINoiseArea()
	
	noise_surface = small_number_font.render("%03d %06d" % (stunit_noise_minute, stunit_noise_total), False, NOISE_TEXT_COLOUR)
	screen.blit(noise_surface, STPCI_NOISE_VALUE)
	
	pygame.display.update(rect)
	
def updateSTPCINoiseCount():
	global stunit_noise_total, stunit_noise_minute, number_font, screen
	
	
	stunit_noise_total += 1
	stunit_noise_minute += 1
	
	if stunit_noise_total > 999999:
		stunit_noise_total = 1
		
	if stunit_noise_minute > 999:
		stunit_noise_minute = 1
	
	updateSTPCINoiseArea()
	
def updateSTPCIStrikeArea():
	rect = clearSTPCIStrikeArea()
	
	strike_surface = small_number_font.render("%03d %06d %03d" % (stunit_strikes_minute, stunit_strikes_total, stunit_strikes_oor), False, STRIKE_TEXT_COLOUR)
	screen.blit(strike_surface, STPCI_STRIKES_VALUE)
	
	pygame.display.update(rect)
	
def updateSTPCIStrikeCount(isoor):
	global number_font, stunit_strikes_oor, screen, stunit_strikes_total, stunit_strikes_minute
	
	
	if not isoor:
		stunit_strikes_total += 1
		
	else:
		stunit_strikes_oor += 1
		
	stunit_strikes_minute += 1
	
	
	if stunit_strikes_total > 999999:
		stunit_strikes_total = 1
		
	if stunit_strikes_minute > 999:
		stunit_strikes_minute = 1
		
	if stunit_strikes_oor > 999:
		stunit_strikes_oor = 1
	
	
	updateSTPCIStrikeArea()
	
	playSound(STRIKE_SOUND)
	
def updateTRACMostActiveArea():
	rect = clearTRACMostActiveArea()
	
	surface = square_font.render("%s" % trac_most_active, False, COLOUR_ALARM_INACTIVE)
	screen.blit(surface, TRAC_MOST_ACTIVE_VALUE)
	
	pygame.display.update(rect)
	
def updateTRACStatus(isactive):
	rect = clearTRACArea()
	
	text = ""
	colour = None
	
	if (isactive == 0) or (not isactive):
		text = "Inactive"
		colour = COLOUR_ALARM_INACTIVE
		
	elif (isactive == 1) or (isactive):
		text = "Active"
		colour = COLOUR_ALARM_ACTIVE
		
	else:
		text = "Busy"
		colour = COLOUR_YELLOW
	
	trac_surface = square_font.render(text, True, colour)
	screen.blit(trac_surface, TRAC_STATUS_VALUE)
	
	pygame.display.update(rect)
	
def updateTRACStormsArea():
	rect = clearTRACStormsArea()
	
	surface = square_font.render("%d" % trac_storms_total, False, COLOUR_ALARM_INACTIVE)
	screen.blit(surface, TRAC_STORMS_VALUE)
	
	pygame.display.update(rect)
	
def updateTRACStormWidthArea():
	rect = clearTRACStormWidthArea()
	
	surface = square_font.render("%d" % TRAC_STORM_WIDTH, False, COLOUR_ALARM_INACTIVE)
	screen.blit(surface, TRAC_STORM_WIDTH_VALUE)
	
	pygame.display.update(rect)
	
def uploadFileViaCurl(strfilename):
	try:
		curl = "curl " + curl_arguments.replace("%%filename%%", strfilename)
		
		system("curl " + curl)
		
	except:
		print "WARNING: Failed to invoke curl."
	
def uuid(*args):
	t = long(time.time() * 1000)
	r = long(random.random() * 100000000000000000L)
	a = None
	
	try:
		a = socket.gethostbyname(socket.gethostname())
	
	except:
		# We can't get a network address, so improvise
		a = random.random() * 100000000000000000L
	
	data = str(t) + " " + str(r) + " " + str(a) + str(args)
	
	return sha.sha(data).hexdigest()
	
def uuidNotRandom(*args):
	data = str(args)
	
	return sha.sha(data).hexdigest()
	
def waitForEFM100Data(sentence):
	star_split = sentence.split("*")
	
	data_split = star_split[0].split(",")
	
	if len(star_split) == 2:
		# Boltek EFM-100
		if sentence.startswith(EFM_POSITIVE) or sentence.startswith(EFM_NEGATIVE):
			if len(data_split) == 2:
				electric_field_level	= data_split[0]
				fault_present		= data_split[1]
				
				
				efl = float(electric_field_level.replace("$", ""))
				
				try:
					myconn = []
					connectToDatabase(myconn)
					
					t = datetime.now()
					
					executeSQLCommand("INSERT INTO tblElectricFieldStrength(DateTimeOfMeasurement, MillisecondsOfMeasurement, kVm) VALUES('%s', %d, %s)" % (t, int(str(t).split(".")[1]), efl), myconn)
					
					disconnectFromDatabase(myconn)
				
				except Exception, msg:
					print "An error has occurred while writing to the database in the Cron thread.\n%s" % msg
					
				
				rect = clearEFM100ReceiverArea()
				efm_surface = None
				
				if int(fault_present) == 0:
					efm_surface = square_font.render("Active", True, COLOUR_ALARM_INACTIVE)
					
				else:
					efm_surface = square_font.render("Fault", True, COLOUR_ALARM_ACTIVE)
				
				screen.blit(efm_surface, EFM100_RECEIVER_VALUE)
				
				pygame.display.update(rect)
				
				
				rect = clearEFM100FieldArea()
				efm_surface = square_font.render("%.2fkV/m" % efl, True, COLOUR_ALARM_INACTIVE)
				screen.blit(efm_surface, EFM100_FIELD_VALUE)
				
				pygame.display.update(rect)
				
				
				# Inform any clients
				try:
					transmitXML(xmlStormForceCreateEventEFM100(efl, fault_present, datetime.now()))
					
				except Exception, msg:
					print "Transmit: %s" % msg
	
def waitForGPSData(sentence):
	star_split = sentence.split("*")
	
	data_split = star_split[0].split(",")
	
	if len(star_split) == 2:
		if sentence.startswith(GPS_GPRMC):
			# Recommended minimum specific GNSS data
			if len(data_split) == 12:
				utc_time			= data_split[1]  # hhmmss.sss
				satellite_fix_status		= data_split[2]  # A = Valid, V = Invalid
				latitude_degrees		= data_split[3]  # ddmm.mmmm
				latitude_hemisphere		= data_split[4]  # N = North, S = South
				longitude_degrees		= data_split[5]  # dddmm.mmmm
				longitude_hemisphere		= data_split[6]  # E = East, W = West
				speed				= data_split[7]  # Knots
				bearing				= data_split[8]  # Degrees
				utc_date			= data_split[9]  # DDMMYY
				magnetic_variation		= data_split[10] # Degrees
				magnetic_variation_hemisphere	= data_split[11] # E = East, W = West
				
				
				colour = None
				rect = None
				text = ""
				
				if satellite_fix_status == "A":
					# Fixed position
					colour = COLOUR_ALARM_INACTIVE
					text = "Fixed"
					
					rect = clearGPSArea()
					gps_surface = square_font.render(text, True, colour)
					screen.blit(gps_surface, GPS_RECEIVER_VALUE)
					
				else:
					# Lost fix
					colour = COLOUR_YELLOW
					text = "No Fix"
					
					rect = clearGPSArea()
					gps_surface = square_font.render(text, True, colour)
					screen.blit(gps_surface, GPS_RECEIVER_VALUE)
					
				pygame.display.update(rect)
				
				
				# Update the location
				rect = clearGPSLatitudeArea()
				gps_surface = square_font.render("%s %s" % (latitude_degrees, latitude_hemisphere), True, colour)
				screen.blit(gps_surface, GPS_LAT_VALUE)
				
				pygame.display.update(rect)
				
				
				rect = clearGPSLongitudeArea()
				gps_surface = square_font.render("%s %s" % (longitude_degrees, longitude_hemisphere), True, colour)
				screen.blit(gps_surface, GPS_LONG_VALUE)
				
				pygame.display.update(rect)
				
				
				rect = clearGPSBearingArea()
				gps_surface = square_font.render("%s" % bearing, True, colour)
				screen.blit(gps_surface, GPS_BEARING_VALUE)
				
				pygame.display.update(rect)
				
				
				rect = clearGPSDateTimeArea()
				gps_surface = square_font.render("%s%s/%s%s/%s%s %s%s:%s%s:%s%s" % (utc_date[0], utc_date[1], utc_date[2], utc_date[3], utc_date[4], utc_date[5], utc_time[0], utc_time[1], utc_time[2], utc_time[3], utc_time[4], utc_time[5]), True, colour)
				screen.blit(gps_surface, GPS_DATETIME_VALUE)
				
				pygame.display.update(rect)
				
				
				
				# Inform any clients
				try:
					transmitXML(xmlStormForceCreateEventGPS(utc_time, satellite_fix_status, latitude_degrees, latitude_hemisphere, longitude_degrees, longitude_hemisphere, speed, bearing, utc_date, magnetic_variation, magnetic_variation_hemisphere, datetime.now()))
					
				except Exception, msg:
					print "Transmit: %s" % msg
	
def waitForLD250Data(sentence):
	global ldunit_close_alarm_last_state, ldunit_severe_alarm_last_state, ldunit_squelch
	
	
	star_split = sentence.split("*")
	
	if sentence.startswith(LD_NOISE):
		# Noise
		updateLD250NoiseCount()
		
		
		# Inform any clients
		try:
			transmitXML(xmlStormForceCreateEventNoise(datetime.now()))
			
		except Exception, msg:
			print "Transmit: %s" % msg
	
	elif sentence.startswith(LD_STATUS):
		# Status update
		if len(star_split) == 2:
			data_split = star_split[0].split(",")
			
			if len(data_split) == 6:
				close_strikes	= int(data_split[1])
				total_strikes	= int(data_split[2])
				close_alarm	= int(data_split[3])
				severe_alarm	= int(data_split[4])
				gps_heading	= float(data_split[5])
				
				
				# Update the alarm status
				colour = None
				rect = None
				text = ""
				
				# Close
				if close_alarm == 0:
					text = "Inactive"
					colour = COLOUR_ALARM_INACTIVE
					
					ldunit_close_alarm_last_state = False
					
				else:
					text = "Active"
					colour = COLOUR_ALARM_ACTIVE
					
					
					if close_alarm_arguments <> "":
						# Try to prevent multiple triggers
						if not ldunit_close_alarm_last_state:
							ldunit_close_alarm_last_state = True
							
							system(close_alarm_arguments)
					
				rect = clearLD250CloseAlarmArea()
				alarm_surface = square_font.render(text, True, colour)
				screen.blit(alarm_surface, LD250_CLOSE_ALARM_VALUE)
				
				pygame.display.update(rect)
				
				
				# Severe
				if severe_alarm == 0:
					text = "Inactive"
					colour = COLOUR_ALARM_INACTIVE
					
					ldunit_severe_alarm_last_state = False
					
				else:
					text = "Active"
					colour = COLOUR_ALARM_ACTIVE
					
					
					if severe_alarm_arguments <> "":
						# Try to prevent multiple triggers
						if not ldunit_severe_alarm_last_state:
							ldunit_severe_alarm_last_state = True
							
							system(severe_alarm_arguments)
					
				rect = clearLD250SevereAlarmArea()
				alarm_surface = square_font.render(text, True, colour)
				screen.blit(alarm_surface, LD250_SEVERE_ALARM_VALUE)
				
				pygame.display.update(rect)
				
				
				# Receiver
				text = "Active"
				colour = COLOUR_ALARM_INACTIVE
				
				rect = clearLD250ReceiverArea()
				alarm_surface = square_font.render(text, True, colour)
				screen.blit(alarm_surface, LD250_RECEIVER_VALUE)
				
				pygame.display.update(rect)
				
				
				# Inform any clients
				try:
					transmitXML(xmlStormForceCreateEventStatus(close_strikes, total_strikes, close_alarm, severe_alarm, gps_heading, datetime.now()))
					
				except Exception, msg:
					print "Transmit: %s" % msg
		
	elif sentence.startswith(LD_STRIKE):
		# Strike
		if len(star_split) == 2:
			data_split = star_split[0].split(",")
			
			if len(data_split) == 4:
				strike_distance_corrected	= int(data_split[1])
				strike_distance			= int(data_split[2])
				strike_angle			= float(data_split[3])
				strike_type			= "CG"
				strike_polarity			= ""
				
				t = datetime.now()
				
				try:
					if database_engine > 0:
						myconn = []
						connectToDatabase(myconn)
						
						executeSQLCommand("INSERT INTO tblStrikes(DateTimeOfStrike, MillisecondsOfStrike, CorrectedStrikeDistance, UncorrectedStrikeDistance, StrikeAngle, StrikeType, StrikePolarity) VALUES('%s', %d, %d, %d, %s, '%s', '%s')" % (t, int(str(t).split(".")[1]), strike_distance_corrected, strike_distance, strike_angle, "CG", ""), myconn)
						
						disconnectFromDatabase(myconn)
				
				except Exception, msg:
					print "An error has occurred while writing to the database in the Cron thread.\n%s" % msg
				
				
				strike_dist = 0
				
				if not ldunit_uus:
					strike_dist = strike_distance_corrected
						
				else:
					strike_dist = strike_distance
				
				
				if ssbt_enabled:
					ssbtVote(0, [strike_dist, strike_angle, t])
					
				else:
					if strike_dist <= zoom_distance:
						plotStrike(strike_dist, strike_angle, False, 0)
						
					else:
						updateLD250StrikeCount(True)
						
				
				# Inform any clients
				try:
					transmitXML(xmlStormForceCreateEventStrike(strike_distance_corrected, strike_distance, strike_angle, "CG", "", datetime.now()))
					
				except Exception, msg:
					print "Transmit: %s" % msg
				
				
				# Send the strike to blitzortung if needed
				if blitzortung_enabled and blitzortung_unit == 1:
					blitzortungAddToQueue(blitzortung_unit, strike_distance_corrected, strike_distance, strike_angle, strike_type, strike_polarity)
					
	elif sentence.startswith(SF_SQUELCH):
		# Squelch level from server
		if len(star_split) == 2:
			data_split = star_split[0].split(",")
			
			if len(data_split) == 2:
				ldunit_squelch = int(data_split[1])
				
				# Need to force an update otherwise it won't appear until next refresh
				if background is not None:
					renderScreen()
				
	elif sentence.startswith(SF_ROTATE):
		# Rotate the logs
		rotateLogs()
	
def waitForSTPCIData(sentence):
	global stunit_squelch
	
	
	star_split = sentence.split("*")
	
	# Boltek StormTracker via my driver program
	if sentence.startswith(ST_STRIKE):
		# Strike
		if len(star_split) == 2:
			data_split = star_split[0].split(",")
			
			if len(data_split) == 6:
				strike_distance_corrected	= float(data_split[1])
				strike_distance			= float(data_split[2])
				strike_angle			= float(data_split[3])
				strike_type			= data_split[4]
				strike_polarity			= data_split[5]
				
				t = datetime.now()
				
				try:
					if database_engine > 0:
						myconn = []
						connectToDatabase(myconn)
						
						executeSQLCommand("INSERT INTO tblStrikes(DateTimeOfStrike, MillisecondsOfStrike, CorrectedStrikeDistance, UncorrectedStrikeDistance, StrikeAngle, StrikeType, StrikePolarity) VALUES('%s', %d, %f, %f, %s, '%s', '%s')" % (t, int(str(t).split(".")[1]), strike_distance_corrected, strike_distance, strike_angle, strike_type, strike_polarity), myconn)
						
						disconnectFromDatabase(myconn)
				
				except Exception, msg:
					print "An error has occurred while writing to the database in the Cron thread.\n%s" % msg
				
				
				strike_dist = 0
				
				if not stunit_uus:
					strike_dist = strike_distance_corrected
						
				else:
					strike_dist = strike_distance
				
				
				if ssbt_enabled:
					# We only want to look at CG strikes for now...
					if strike_type == "CG":
						ssbtVote(1, [strike_dist, strike_angle, t])
					
				else:
					if strike_dist <= zoom_distance:
						plotStrike(strike_dist, strike_angle, False, 1)
						
					else:
						updateSTPCIStrikeCount(True)
						
				
				# Inform any clients
				try:
					transmitXML(xmlStormForceCreateEventStrike(strike_distance_corrected, strike_distance, strike_angle, strike_type, strike_polarity, datetime.now()))
					
				except Exception, msg:
					print "Transmit: %s" % msg
					
				
				# Send the strike to blitzortung if needed
				if blitzortung_enabled and blitzortung_unit == 2:
					blitzortungAddToQueue(blitzortung_unit, strike_distance_corrected, strike_distance, strike_angle, strike_type, strike_polarity)
					
	elif sentence.startswith(ST_NOISE):
		# Noise
		updateSTPCINoiseCount()
		
		
		# Inform any clients
		try:
			transmitXML(xmlStormForceCreateEventNoise(datetime.now()))
			
		except Exception, msg:
			print "Transmit: %s" % msg
			
	elif sentence.startswith(ST_STATUS):
		# Status
		text = "Active"
		colour = COLOUR_ALARM_INACTIVE
		
		rect = clearSTPCIReceiverArea()
		alarm_surface = square_font.render(text, True, colour)
		screen.blit(alarm_surface, STPCI_RECEIVER_VALUE)
		
		pygame.display.update(rect)
		
		
		# Inform any clients
		try:
			transmitXML(xmlStormForceCreateEventNoise(datetime.now()))
			
		except Exception, msg:
			print "Transmit: %s" % msg
			
	elif sentence.startswith(SF_SQUELCH):
		# Squelch level from server
		if len(star_split) == 2:
			data_split = star_split[0].split(",")
			
			if len(data_split) == 2:
				stunit_squelch = int(data_split[1])
				
				# Need to force an update otherwise it won't appear until next refresh
				if background is not None:
					renderScreen()
		
	
def xmlStormForceCreateAuthRequest(strusername, strpassword, strkey):
	xmldoc = minidom.Document()
	
	sfsettings = xmldoc.createElement("StormForce")
	xmldoc.appendChild(sfsettings)
	
	var = xmldoc.createElement("Authentication")
	var.setAttribute("Username", str(strusername))
	var.setAttribute("Password", str(strpassword))
	var.setAttribute("Key", str(strkey))
	sfsettings.appendChild(var)
	
	
	return xmldoc.toprettyxml()
	
def xmlStormForceParseAuthRequest(strxml):
	xmlin = StringIO(strxml)
	xmldoc = minidom.parse(xmlin)
	
	myvars = xmldoc.getElementsByTagName("Authentication")
	
	
	username = ""
	password = ""
	key = ""
	
	for var in myvars:
		for key in var.attributes.keys():
			val = str(var.attributes[key].value)
			
			if key == "Username":
				username = val
				
			elif key == "Password":
				password = val
				
			elif key == "Key":
				key = val
				
			else:
				print "Warning: XML authentication attribute \"%s\" isn't known.  Ignoring..." % key
				
	return username, password, key
	
def xmlStormForceCreateEventEFM100(efs, fault, dateandtime):
	xmldoc = minidom.Document()
	
	sfsettings = xmldoc.createElement("StormForce")
	xmldoc.appendChild(sfsettings)
	
	var = xmldoc.createElement("Notification")
	var.setAttribute("EventID", str(XML_EVENT_EFM))
	var.setAttribute("ElectricFieldStrength", str(efs))
	var.setAttribute("FaultDetected", str(fault))
	var.setAttribute("DateTime", str(dateandtime))
	sfsettings.appendChild(var)
	
	
	return xmldoc.toprettyxml()
	
def xmlStormForceParseEventEFM100(strxml):
	xmlin = StringIO(strxml)
	xmldoc = minidom.parse(xmlin)
	
	myvars = xmldoc.getElementsByTagName("Notification")
	
	
	efs = 0.
	fault = 0
	dateandtime = None
	
	for var in myvars:
		if "EventID" in var.attributes.keys():
			
			if str(var.attributes["EventID"].value) == str(XML_EVENT_EFM):
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					if key == "ElectricFieldStrength":
						efs = float(val)
						
					elif key == "FaultDetected":
						fault = int(val)
						
					elif key == "DateTime":
						dateandtime = val
						
					elif key == "EventID":
						pass
						
					else:
						print "Warning: XML EFM-100 event attribute \"%s\" isn't known.  Ignoring..." % key
						
	return efs, fault, dateandtime
	
def xmlStormForceCreateEventGPS(utc_time, satellite_fix_status, latitude_degrees, latitude_hemisphere, longitude_degrees, longitude_hemisphere, speed, bearing, utc_date, magnetic_variation, magnetic_variation_hemisphere, dateandtime):
	xmldoc = minidom.Document()
	
	sfsettings = xmldoc.createElement("StormForce")
	xmldoc.appendChild(sfsettings)
	
	var = xmldoc.createElement("Notification")
	var.setAttribute("EventID", str(XML_EVENT_GPS))
	var.setAttribute("UTCTime", str(utc_time))
	var.setAttribute("SatelliteFixStatus", str(satellite_fix_status))
	var.setAttribute("LatitudeDegrees", str(latitude_degrees))
	var.setAttribute("LatitudeHemisphere", str(latitude_hemisphere))
	var.setAttribute("LongitudeDegrees", str(longitude_degrees))
	var.setAttribute("LongitudeHemisphere", str(longitude_hemisphere))
	var.setAttribute("Speed", str(speed))
	var.setAttribute("Bearing", str(bearing))
	var.setAttribute("UTCDate", str(utc_date))
	var.setAttribute("MagneticVariation", str(magnetic_variation))
	var.setAttribute("MagneticVariationHemisphere", str(magnetic_variation_hemisphere))
	var.setAttribute("DateTime", str(dateandtime))
	sfsettings.appendChild(var)
	
	
	return xmldoc.toprettyxml()
	
def xmlStormForceParseEventGPS(strxml):
	xmlin = StringIO(strxml)
	xmldoc = minidom.parse(xmlin)
	
	myvars = xmldoc.getElementsByTagName("Notification")
	
	
	utc_time = ""
	satellite_fix_status = ""
	latitude_degrees = ""
	latitude_hemisphere = ""
	longitude_degrees = ""
	longitude_hemisphere = ""
	speed = ""
	bearing = ""
	utc_date = ""
	magnetic_variation = 0.
	magnetic_variation_hemisphere = ""
	dateandtime = None
	
	for var in myvars:
		if "EventID" in var.attributes.keys():
			
			if str(var.attributes["EventID"].value) == str(XML_EVENT_GPS):
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					if key == "UTCTime":
						utc_time = val
						
					elif key == "SatelliteFixStatus":
						satellite_fix_status = val
						
					elif key == "LatitudeDegrees":
						latitude_degrees = val
						
					elif key == "LatitudeHemisphere":
						latitude_hemisphere = val
						
					elif key == "LongitudeDegrees":
						longitude_degrees = val
						
					elif key == "LongitudeHemisphere":
						longitude_hemisphere = val
						
					elif key == "Speed":
						speed = val
						
					elif key == "Bearing":
						bearing = val
						
					elif key == "UTCDate":
						utc_date = val
						
					elif key == "MagneticVariation":
						magnetic_variation = float(val)
						
					elif key == "MagneticVariationHemisphere":
						magnetic_variation_hemisphere = val
						
					elif key == "DateTime":
						dateandtime = val
						
					elif key == "EventID":
						pass
						
					else:
						print "Warning: XML GPS event attribute \"%s\" isn't known.  Ignoring..." % key
						
	return utc_time, satellite_fix_status, latitude_degrees, latitude_hemisphere, longitude_degrees, longitude_hemisphere, speed, bearing, utc_date, magnetic_variation, magnetic_variation_hemisphere, dateandtime
	
def xmlStormForceCreateEventNoise(dateandtime):
	xmldoc = minidom.Document()
	
	sfsettings = xmldoc.createElement("StormForce")
	xmldoc.appendChild(sfsettings)
	
	var = xmldoc.createElement("Notification")
	var.setAttribute("EventID", str(XML_EVENT_LD250_NOISE))
	var.setAttribute("Detected", str("True"))
	var.setAttribute("DateTime", str(dateandtime))
	sfsettings.appendChild(var)
	
	
	return xmldoc.toprettyxml()
	
def xmlStormForceParseEventNoise(strxml):
	xmlin = StringIO(strxml)
	xmldoc = minidom.parse(xmlin)
	
	myvars = xmldoc.getElementsByTagName("Notification")
	
	
	detected = False
	dateandtime = None
	
	for var in myvars:
		if "EventID" in var.attributes.keys():
			
			if str(var.attributes["EventID"].value) == str(XML_EVENT_LD250_NOISE):
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					if key == "Detected":
						detected = cBool(val)
						
					elif key == "DateTime":
						dateandtime = val
						
					elif key == "EventID":
						pass
						
					else:
						print "Warning: XML noise event attribute \"%s\" isn't known.  Ignoring..." % key
						
	return detected, dateandtime
	
def xmlStormForceCreateEventSquelch(level, dateandtime):
	xmldoc = minidom.Document()
	
	sfsettings = xmldoc.createElement("StormForce")
	xmldoc.appendChild(sfsettings)
	
	var = xmldoc.createElement("Notification")
	var.setAttribute("EventID", str(XML_EVENT_LD250_SQUELCH))
	var.setAttribute("SquelchLevel", str(level))
	var.setAttribute("DateTime", str(dateandtime))
	sfsettings.appendChild(var)
	
	
	return xmldoc.toprettyxml()
	
def xmlStormForceParseEventSquelch(strxml):
	xmlin = StringIO(strxml)
	xmldoc = minidom.parse(xmlin)
	
	myvars = xmldoc.getElementsByTagName("Notification")
	
	
	level = 0
	dateandtime = None
	
	for var in myvars:
		if "EventID" in var.attributes.keys():
			
			if str(var.attributes["EventID"].value) == str(XML_EVENT_LD250_SQUELCH):
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					if key == "SquelchLevel":
						level = int(val)
						
					elif key == "DateTime":
						dateandtime = val
						
					elif key == "EventID":
						pass
						
					else:
						print "Warning: XML squelch event attribute \"%s\" isn't known.  Ignoring..." % key
						
	return level, dateandtime
	
def xmlStormForceCreateEventStatus(close_rate, total_rate, close_alarm, severe_alarm, heading, dateandtime):
	xmldoc = minidom.Document()
	
	sfsettings = xmldoc.createElement("StormForce")
	xmldoc.appendChild(sfsettings)
	
	var = xmldoc.createElement("Notification")
	var.setAttribute("EventID", str(XML_EVENT_LD250_STATUS))
	var.setAttribute("CloseStrikeRate", str(close_rate))
	var.setAttribute("TotalStrikeRate", str(total_rate))
	var.setAttribute("CloseAlarmActive", str(close_alarm))
	var.setAttribute("SevereAlarmActive", str(severe_alarm))
	var.setAttribute("Heading", str(heading))
	var.setAttribute("DateTime", str(dateandtime))
	sfsettings.appendChild(var)
	
	
	return xmldoc.toprettyxml()
	
def xmlStormForceParseEventStatus(strxml):
	xmlin = StringIO(strxml)
	xmldoc = minidom.parse(xmlin)
	
	myvars = xmldoc.getElementsByTagName("Notification")
	
	
	close_rate = 0
	total_rate = 0
	close_alarm = 0
	severe_alarm = 0
	heading = 0.
	dateandtime = None
	
	for var in myvars:
		if "EventID" in var.attributes.keys():
			
			if str(var.attributes["EventID"].value) == str(XML_EVENT_LD250_STATUS):
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					if key == "CloseStrikeRate":
						close_rate = int(val)
						
					elif key == "TotalStrikeRate":
						total_rate = int(val)
						
					elif key == "CloseAlarmActive":
						close_alarm = int(val)
						
					elif key == "SevereAlarmActive":
						severe_alarm = int(val)
						
					elif key == "Heading":
						heading = float(val)
						
					elif key == "DateTime":
						dateandtime = val
						
					elif key == "EventID":
						pass
						
					else:
						print "Warning: XML status event attribute \"%s\" isn't known.  Ignoring..." % key
						
	return close_rate, total_rate, close_alarm, severe_alarm, heading, dateandtime
	
def xmlStormForceCreateEventStrike(corrected_distance, uncorrected_distance, bearing, striketype, strikepolarity, dateandtime):
	xmldoc = minidom.Document()
	
	sfsettings = xmldoc.createElement("StormForce")
	xmldoc.appendChild(sfsettings)
	
	var = xmldoc.createElement("Notification")
	var.setAttribute("EventID", str(XML_EVENT_LD250_STRIKE))
	var.setAttribute("CorrectedDistance", str(corrected_distance))
	var.setAttribute("UncorrectedDistance", str(uncorrected_distance))
	var.setAttribute("Bearing", str(bearing))
	var.setAttribute("StrikeType", str(striketype))
	var.setAttribute("StrikePolarity", str(strikepolarity))
	var.setAttribute("DateTime", str(dateandtime))
	sfsettings.appendChild(var)
	
	
	return xmldoc.toprettyxml()
	
def xmlStormForceParseEventStrike(strxml):
	xmlin = StringIO(strxml)
	xmldoc = minidom.parse(xmlin)
	
	myvars = xmldoc.getElementsByTagName("Notification")
	
	
	corrected_distance = 0
	uncorrected_distance = 0
	bearing = 0.
	striketype = ""
	strikepolarity = ""
	dateandtime = None
	
	for var in myvars:
		if "EventID" in var.attributes.keys():
			
			if str(var.attributes["EventID"].value) == str(XML_EVENT_LD250_STRIKE):
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					if key == "CorrectedDistance":
						corrected_distance = int(val)
						
					elif key == "UncorrectedDistance":
						uncorrected_distance = int(val)
						
					elif key == "Bearing":
						bearing = float(val)
						
					elif key == "StrikeType":
						striketype = val
						
					elif key == "StrikePolarity":
						strikepolarity = val
						
					elif key == "DateTime":
						dateandtime = val
						
					elif key == "EventID":
						pass
						
					else:
						print "Warning: XML strike event attribute \"%s\" isn't known.  Ignoring..." % key
						
	return corrected_distance, uncorrected_distance, bearing, striketype, strikepolarity, dateandtime
	
def xmlStormForceSettingsRead():
	global blitzortung_gps_latitude, blitzortung_gps_longitude, blitzortung_hostname, blitzortung_password, blitzortung_port, blitzortung_unit, blitzortung_username, captured_file, close_alarm_arguments, curl_arguments, database_engine, debug_mode, demo_mode, efmunit_port, efmunit_port_compression, efmunit_port_type, fullscreen, gpsunit_port, gpsunit_port_compression, gpsunit_port_type, ldunit_port, ldunit_port_compression, ldunit_port_type, ldunit_skew_amount, ldunit_squelch, ldunit_uus, listener_multicast_address, listener_multicast_port, listener_multicast_port_compression, listener_multicast_ttl, listener_tcp_port, listener_tcp_port_compression, listener_udp_port, listener_udp_port_compression, mysql_server, mysql_database, mysql_username, mysql_password, reconstruction_file, server_mode, severe_alarm_arguments, show_range_circles, show_red_dot, small_crosshair, sound_enabled, strike_shape, stunit_port, stunit_port_compression, stunit_port_type, stunit_skew_amount, stunit_squelch, stunit_uus, trac_enabled, zoom_distance, zoom_multiplier
	global TRAC_SENSITIVITY, TRAC_STORM_WIDTH, USER_COPYRIGHT
	
	
	if path.exists(XML_SETTINGS_FILE):
		xmldoc = minidom.parse(XML_SETTINGS_FILE)
		
		myvars = xmldoc.getElementsByTagName("Setting")
		
		for var in myvars:
			for key in var.attributes.keys():
				val = str(var.attributes[key].value)
				
				# Now put the correct values to correct key
				if key == "DatabaseEngine":
					database_engine = int(val)
					
				elif key == "ConnectionString":
					connstr = val.split("/")
					
					if len(connstr) == 4:
						mysql_server = str(connstr[0])
						mysql_database = str(connstr[1])
						mysql_username = str(connstr[2])
						mysql_password = str(connstr[3])
						
					else:
						print "Error: Connection string doesn't have enough arguments (requires four)."
						exitProgram()
						
				elif key == "Fullscreen":
					fullscreen = cBool(val)
					
				elif key == "LD250Port":
					ldunit_port = val
					
				elif key == "LD250PortCompression":
					ldunit_port_compression = val
					
				elif key == "LD250PortType":
					ldunit_port_type = val
					
					if ldunit_port_type == "":
						ldunit_port_type = "XML"
						
					else:
						if ldunit_port_type <> "TEXT" and ldunit_port_type <> "XML":
							ldunit_port_type = "TEXT"
					
				elif key == "LD250SkewAmount":
					ldunit_skew_amount = float(val)
					
				elif key == "LD250SquelchLevel":
					ldunit_squelch = int(val)
					
				elif key == "LD250UseUncorrectedStrikes":
					ldunit_uus = cBool(val)
					
				elif key == "StormTrackerPort":
					stunit_port = val
					
				elif key == "StormTrackerPortCompression":
					stunit_port_compression = val
					
				elif key == "StormTrackerPortType":
					stunit_port_type = val
					
					if stunit_port_type == "":
						stunit_port_type = "XML"
						
					else:
						if stunit_port_type <> "TEXT" and stunit_port_type <> "XML":
							stunit_port_type = "TEXT"
					
				elif key == "StormTrackerSkewAmount":
					stunit_skew_amount = float(val)
					
				elif key == "StormTrackerSquelchLevel":
					stunit_squelch = int(val)
					
				elif key == "StormTrackerUseUncorrectedStrikes":
					stunit_uus = cBool(val)
					
				elif key == "CloseAlarmArguments":
					close_alarm_arguments = val
					
				elif key == "DemoMode":
					demo_mode = cBool(val)
					
				elif key == "DebugMode":
					debug_mode = cBool(val)
					
				elif key == "EFM100Port":
					efmunit_port = val
					
				elif key == "EFM100PortCompression":
					efmunit_port_compression = val
					
				elif key == "EFM100PortType":
					efmunit_port_type = val
					
					if efmunit_port_type == "":
						efmunit_port_type = "XML"
						
					else:
						if efmunit_port_type <> "TEXT" and efmunit_port_type <> "XML":
							efmunit_port_type = "TEXT"
					
				elif key == "GPSPort":
					gpsunit_port = val
					
				elif key == "GPSPortCompression":
					gpsunit_port_compression = val
					
				elif key == "GPSPortType":
					gpsunit_port_type = val
					
					if gpsunit_port_type == "":
						gpsunit_port_type = "XML"
						
					else:
						if gpsunit_port_type <> "TEXT" and gpsunit_port_type <> "XML":
							gpsunit_port_type = "TEXT"
					
				elif key == "TCPListenerPort":
					listener_tcp_port = int(val)
					
				elif key == "TCPListenerPortCompression":
					listener_tcp_port_compression = val
					
				elif key == "UDPListenerPort":
					listener_udp_port = int(val)
					
				elif key == "UDPListenerPortCompression":
					listener_udp_port_compression = val
					
				elif key == "MulticastListenerAddress":
					listener_multicast_address = val
					
				elif key == "MulticastListenerPort":
					listener_multicast_port = int(val)
					
				elif key == "MulticastListenerPortCompression":
					listener_multicast_port_compression = val
					
				elif key == "MulticastListenerTTL":
					listener_multicast_ttl = int(val)
					
				elif key == "StrikeShape":
					strike_shape = int(val)
					
				elif key == "SmallCrosshair":
					small_crosshair = cBool(val)
					
				elif key == "ShowRedDotOnStrike":
					show_red_dot = cBool(val)
					
				elif key == "ReconstructionFile":
					reconstruction_file = val
					
				elif key == "TRACSensitivity":
					TRAC_SENSITIVITY = int(val)
					
				elif key == "ShowRangeCircles":
					show_range_circles = cBool(val)
					
				elif key == "TRACEnabled":
					trac_enabled = cBool(val)
					
				elif key == "ServerModeImage":
					if val <> "":
						demo_mode = False
						
						server_mode = True
						captured_file = val
					
				elif key == "SevereAlarmArguments":
					severe_alarm_arguments = val
					
				elif key == "SoundEnabled":
					sound_enabled = cBool(val)
					
				elif key == "CurlArguments":
					curl_arguments = val
					
				elif key == "TRACStormWidth":
					TRAC_STORM_WIDTH = int(val)
					
				elif key == "UserCopyright":
					USER_COPYRIGHT = val.replace("\\n", "\n")
					
				elif key == "BlitzortungGPSLatitude":
					blitzortung_gps_latitude = float(val)
					
				elif key == "BlitzortungGPSLongitude":
					blitzortung_gps_longitude = float(val)
					
				elif key == "BlitzortungHostname":
					blitzortung_hostname = val
					
				elif key == "BlitzortungPassword":
					blitzortung_password = val
					
				elif key == "BlitzortungPort":
					blitzortung_port = int(val)
					
				elif key == "BlitzortungUnit":
					blitzortung_unit = int(val)
					
				elif key == "BlitzortungUsername":
					blitzortung_username = val
					
				elif key == "ZoomDistance":
					zoom_distance = int(val)
					
					# Recalculate the zoom multiplier
					zoom_multiplier = float(zoom_distance) / (float(MAP_SIZE[0] / 2.))
					
				else:
					print "Warning: XML setting attribute \"%s\" isn't known.  Ignoring..." % key
					
	else:
		if debug_mode:
			print "WARNING: XML settings file wasn't found."
	
def xmlStormForceSettingsWrite():
	if not path.exists(XML_SETTINGS_FILE):
		xmloutput = file(XML_SETTINGS_FILE, "w")
		
		
		xmldoc = minidom.Document()
		
		# Create header
		sfsettings = xmldoc.createElement("StormForce")
		xmldoc.appendChild(sfsettings)
		
		# Write each of the details one at a time, makes it easier for someone to alter the file using a text editor
		var = xmldoc.createElement("Setting")
		var.setAttribute("DemoMode", str(demo_mode))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("DebugMode", str(debug_mode))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("DatabaseEngine", str(database_engine))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("ConnectionString", "%s/%s/%s/%s" % (mysql_server, mysql_database, mysql_username, mysql_password))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("Fullscreen", "%s" % str(fullscreen))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("LD250Port", str(ldunit_port))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("LD250PortCompression", str(ldunit_port_compression))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("LD250PortType", str(ldunit_port_type))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("LD250SkewAmount", str(ldunit_skew_amount))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("LD250SquelchLevel", str(ldunit_squelch))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("LD250UseUncorrectedStrikes", str(ldunit_uus))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("StormTrackerPort", str(stunit_port))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("StormTrackerPortCompression", str(stunit_port_compression))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("StormTrackerPortType", str(stunit_port_type))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("StormTrackerSkewAmount", str(stunit_skew_amount))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("StormTrackerSquelchLevel", str(stunit_squelch))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("StormTrackerUseUncorrectedStrikes", str(stunit_uus))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("EFM100Port", str(efmunit_port))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("EFM100PortCompression", str(efmunit_port_compression))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("EFM100PortType", str(efmunit_port_type))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("GPSPort", str(gpsunit_port))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("GPSPortCompression", str(gpsunit_port_compression))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("GPSPortType", str(gpsunit_port_type))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("TRACEnabled", str(trac_enabled))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("TRACSensitivity", str(TRAC_SENSITIVITY))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("TRACStormWidth", str(TRAC_STORM_WIDTH))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("CloseAlarmArguments", str(close_alarm_arguments))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("SevereAlarmArguments", str(severe_alarm_arguments))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("TCPListenerPort", str(listener_tcp_port))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("TCPListenerPortCompression", str(listener_tcp_port_compression))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("UDPListenerPort", str(listener_udp_port))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("UDPListenerPortCompression", str(listener_udp_port_compression))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("MulticastListenerAddress", str(listener_multicast_address))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("MulticastListenerPort", str(listener_multicast_port))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("MulticastListenerPortCompression", str(listener_multicast_port_compression))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("MulticastListenerTTL", str(listener_multicast_ttl))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("StrikeShape", str(strike_shape))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("SmallCrosshair", str(small_crosshair))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("ShowRedDotOnStrike", str(show_red_dot))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("ReconstructionFile", str(reconstruction_file))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("ShowRangeCircles", str(show_range_circles))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("ServerModeImage", str(captured_file))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("SoundEnabled", str(sound_enabled))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("CurlArguments", str(curl_arguments))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("BlitzortungGPSLatitude", str(blitzortung_gps_latitude))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("BlitzortungGPSLongitude", str(blitzortung_gps_longitude))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("BlitzortungHostname", str(blitzortung_hostname))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("BlitzortungPassword", str(blitzortung_password))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("BlitzortungPort", str(blitzortung_port))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("BlitzortungUnit", str(blitzortung_unit))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("BlitzortungUsername", str(blitzortung_username))
		sfsettings.appendChild(var)
		
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("UserCopyright", str(USER_COPYRIGHT.replace("\n", "\\n")))
		sfsettings.appendChild(var)
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("ZoomDistance", str(zoom_distance))
		sfsettings.appendChild(var)
		
		
		# Finally, save to the file
		xmloutput.write(xmldoc.toprettyxml())
		xmloutput.close()
		
	else:
		if debug_mode:
			print "WARNING: XML settings already exists, skipping creation..."
	
	
###############################
# Trigger the main subroutine #
###############################
if __name__ == "__main__":
	sys.exit(main())
