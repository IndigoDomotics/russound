#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2011, jottawa. All rights reserved.
# http://sites.google.com/site/russoundpluginforindigo/

import os
import sys
import indigo
import time
import binascii
from binascii import unhexlify, hexlify
import time
from socket import *

SERIAL_PORT = "1"
SOCKET = "2"
SECONDS_BETWEEN_SENDING = 0.25
SOCKET_TIMEOUT = 0.1
NOT_HANDLED_BY_PLUGIN = "\t Message not handled by plugin"
MAX_NUMBER_OF_SOURCES = 12

#Special RNET codes
RNET_BOM = "F0"
RNET_EOM = "F7"
RNET_INVERT_CHAR = "F1"
POWER = "DC"
REMOTE_CONTROL_KEY_RELEASE = "BF"
THE_CONTROLLER_ITSELF = "7F"
ALL_CONTROLLERS = "7E"
ALL_ZONE_KEYPADS = "7D"
ALL_KEYPADS_SELECTED_TO_A_SOURCE = "79"

#Target Zones
PERIPHERAL_DEVICE = "7D"

#RNET Message indexes
TARGET_CONTROLLER_ID = 1
TARGET_ZONE_ID = 2
TARGET_KEYPAD_ID = 3
SOURCE_CONTROLLER_ID = 4
SOURCE_ZONE_ID = 5
SOURCE_KEYPAD_ID = 6
MESSAGE_TYPE = 7
#Event
TARGET_PATH_NUM_LEVELS = 8
#Set Data
PRODUCT_SPECIFIC_OBJECTS = "04"
#Rendered Display
VALUE_LOW_BYTE = 8
VALUE_HIGH_BYTE = 9

#RNET Message Types
MESSAGE_TYPE_SET_DATA = "00"
MESSAGE_TYPE_HANDSHAKE = "02"
MESSAGE_TYPE_EVENT = "05"
MESSAGE_TPYE_RENDERED_DISPLAY = "06"

#Rentering Types
SOURCE_NAME = "05"
VOLUME = "10"
BASS = "11"
TREBLE = "12"
BALANCE = "13"
ON_OFF = "0A"

#RNET polling signatures
POLL_ZONE_STATE_MSG = "F0 cc 00 7F cc zz kk 01 04 02 00 zz 07 00 00"
POLL_ZONE_ON_VOLUME_MSG = "F0 cc 00 7F cc zz kk 01 05 02 00 zz 00 04 00 00"
POLL_ZONE_BG_COLOR_MSG = "F0 cc 00 7F cc zz kk 01 05 02 00 zz 00 05 00 00"



                                  
                                  
CONTROLLER_TYPES = {"CA4":    {"SourceKeyPadID": "71", "ZonesPerController": 4}
                   ,"CAS44":  {"SourceKeyPadID": "70", "ZonesPerController": 6}
                   ,"CAA66":  {"SourceKeyPadID": "70", "ZonesPerController": 6}
                   ,"CAM6.6": {"SourceKeyPadID": "70", "ZonesPerController": 6}
                   ,"CAV6.6": {"SourceKeyPadID": "70", "ZonesPerController": 6}
                   ,"ACA-E5": {"SourceKeyPadID": "71", "ZonesPerController": 8}
                   ,"MCA-C3": {"SourceKeyPadID": "71", "ZonesPerController": 6}
                   ,"MCA-C5": {"SourceKeyPadID": "71", "ZonesPerController": 8}}

ACTION_MESSAGES = {"turnAllZonesOn":           None
                  ,"turnAllZonesOff":         "F0 7E 00 7F 00 00 kk 05 02 02 00 00 F1 22 00 00 00 00 00 01"
                  ,"turnZoneOn":              "F0 cc 00 7F cc zz kk 05 02 02 00 00 F1 23 00 01 00 zz 00 01"
                  ,"turnZoneOff":             "F0 cc 00 7F cc zz kk 05 02 02 00 00 F1 23 00 00 00 zz 00 01"
                  ,"aetZoneSource":           "F0 cc 00 7F cc zz kk 05 02 00 00 00 F1 3E 00 00 00 ## 00 01"
                  ,"setZoneVolume":           "F0 cc 00 7F cc zz kk 05 02 02 00 00 F1 21 00 ## 00 zz 00 01"
                  ,"setZoneBalance":          "F0 cc 00 7F cc zz kk 00 05 02 00 zz 00 03 00 00 00 01 00 01 00 ##"
                  ,"setZoneBass":             "F0 cc 00 7F cc zz kk 00 05 02 00 zz 00 00 00 00 00 01 00 01 00 ##"
                  ,"setZoneTreble":           "F0 cc 00 7F cc zz kk 00 05 02 00 zz 00 01 00 00 00 01 00 01 00 ##"
                  ,"setZoneLoudnessOn":       "F0 cc 00 7F cc zz kk 00 05 02 00 zz 00 02 00 00 00 01 00 01 00 01"
                  ,"setZoneLoudnessOff":      "F0 cc 00 7F cc zz kk 00 05 02 00 zz 00 02 00 00 00 01 00 01 00 00"
                  ,"sourceControl":           "F0 cc 00 7F cc zz kk 05 02 02 00 00 F1 40 00 00 00 ## 00 01"
                  ,"keyPad":                  "F0 cc 00 7F cc zz kk 05 02 02 00 00 ## 00 00 00 00 00 01"
                  #,"keyPad":                  "F0 cc 00 7F cc zz kk 05 03 02 00 01 02 04 03 ## 00 00 00 00 00 01"
                  ,"pollZone":                 None
                  ,"pollAllZones":             None
                  ,"sendMessageToAllZones":   "F0 7F 00 00 00 00 kk 00 02 01 01 00 00 00 01 00 10 00 00 ff 00 00 00 00 00 00 00 00 00 00 00 00 00"
                  ,"sendMessageToZone":       "F0 cc zz 00 00 00 kk 00 02 01 01 00 00 00 01 00 10 00 00 ff 00 00 00 00 00 00 00 00 00 00 00 00 00"
                  ,"updateDisplayMessageInZone": None
                  ,"sendSourceBroadcast":     "F0 7D 00 79 00 7D 00 00 02 01 01 02 01 01 00 00 01 00 28 00 ss ff 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
                  ,"sendMultiFieldBroadcast": "F0 7D 00 79 00 7D 04 00 02 01 01 02 01 01 00 00 01 00 27 00 ss F1 ff 1E 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
                  ,"turnBassUp":              "F0 cc 00 7F cc zz kk 05 05 02 00 zz 00 00 00 69 00 00 00 01 00 01"
                  ,"turnBassDown":            "F0 cc 00 7F cc zz kk 05 05 02 00 zz 00 00 00 6A 00 00 00 01 00 01"
                  ,"turnTrebleUp":            "F0 cc 00 7F cc zz kk 05 05 02 00 zz 00 01 00 69 00 00 00 02 00 01"
                  ,"turnTrebleDown":          "F0 cc 00 7F cc zz kk 05 05 02 00 zz 00 01 00 6A 00 00 00 02 00 01"
                  ,"turnBalanceLeft":         "F0 cc 00 7F cc zz kk 05 05 02 00 zz 00 03 00 6A 00 00 00 04 00 01"
                  ,"turnBalanceRight":        "F0 cc 00 7F cc zz kk 05 05 02 00 zz 00 03 00 69 00 00 00 04 00 01"
		  ,"directTuning":	      None
		  ,"tunerDirectMode":	      "F0 00 7D kk 00 00 70 05 02 01 00 02 01 00 17 00 70 00 kk 00 01"
		  ,"tunerFrequency":	      "F0 00 7D kk 00 00 70 05 02 01 00 02 01 00 ## 00 70 00 kk 00 01" }


MSESSAGE_TYPES = {"00":"Set Data"
                 ,"01":"Request Data"
                 ,"02":"Handshake"
                 ,"05":"Event"
                 ,"06":"Rendered Display"}

KEYPAD_EVENTS = {"64":"Setup Button"
                ,"67":"Previous"
                ,"68":"Next"
                ,"69":"Plus"
                ,"6A":"Minus"
                ,"6B":"Source (source toggle button)"
                ,"6C":"Power"
                ,"6D":"Stop"
                ,"6E":"Pause"
                ,"6F":"Favorite 1"
                ,"70":"Favorite 2"
                ,"71":"Numeric Toggle On"
                ,"72":"Numeric Toggle Off"
                ,"73":"Play"
                ,"7F":"Volume Up"
                ,"80":"Volume Down"
                ,"9D":"Keypad Setup"
                ,"BF":"Remote Control Key Release"}

SOURCE_CONTROL_EVENTS = {"01":"Button 1"
                        ,"02":"Button 2"
                        ,"03":"Button 3"
                        ,"04":"Button 4"
                        ,"05":"Button 5"
                        ,"06":"Button 6"
                        ,"07":"Button 7"
                        ,"08":"Button 8"
                        ,"09":"Button 9"
                        ,"0A":"Button 10"
                        ,"0B":"Volume Up"
                        ,"0C":"Volume Down"
                        ,"0D":"Mute (for zone)"
                        ,"0E":"Channel Up"
                        ,"0F":"Channel Down"
                        ,"10":"Power"
                        ,"11":"Enter"
                        ,"12":"Previous Channel"
                        ,"13":"TV/Video"
                        ,"14":"TV/VCR"
                        ,"15":"A/B"
                        ,"16":"TV/DVD"
                        ,"17":"TV/LD"
                        ,"18":"Input"
                        ,"19":"TV/DSS"
                        ,"1A":"Play"
                        ,"1B":"Stop"
                        ,"1C":"Search Forward"
                        ,"1D":"Search Rewind"
                        ,"1E":"Pause"
                        ,"1F":"Record"
                        ,"20":"Menu"
                        ,"21":"Menu Up"
                        ,"22":"Menu Down"
                        ,"23":"Menu Left"
                        ,"24":"Menu Right"
                        ,"25":"Select"
                        ,"26":"Exit"
                        ,"27":"Display"
                        ,"28":"Guide"
                        ,"29":"Page Up"
                        ,"2A":"Page Down"
                        ,"2B":"Disk"
                        ,"2C":"Plus 10"
                        ,"2D":"Open/Close"
                        ,"2E":"Random"
                        ,"2F":"Track Forward"
                        ,"30":"Track Reverse"
                        ,"31":"Surround On/Off"
                        ,"32":"Surround Mode"
                        ,"33":"Surround Up"
                        ,"34":"Surround Down"
                        ,"35":"PIP"
                        ,"36":"PIP Move"
                        ,"37":"PIP Swap"
                        ,"38":"Program"
                        ,"39":"Sleep"
                        ,"3A":"On"
                        ,"3B":"Off"
                        ,"3C":"11"
                        ,"3D":"12"
                        ,"3E":"13"
                        ,"3F":"14"
                        ,"40":"15"
                        ,"41":"16"
                        ,"42":"Bright"
                        ,"43":"Dim"
                        ,"44":"Close"
                        ,"45":"Open"
                        ,"46":"Stop 2"
                        ,"47":"AM/FM"
                        ,"48":"Cue"
                        ,"49":"Disk Up"
                        ,"4A":"Disk Down"
                        ,"4B":"Info"}
		 
RENDER_TYPES = {"05":"Source Name"
               ,"10":"Volume"
               ,"11":"Bass"
               ,"12":"Treble"
               ,"13":"Balance"
               ,"0A":"Yes/No"}

DISPLAY_ELEMENTS = {"01":"Do Not Disturb Indication"
                   ,"02":"Shared Source Indication"
                   ,"03":"System On Indication"
                   ,"04":"Party Mode Indication"
                   ,"05":"Party Master Indication"}

FIELDID_TYPES = {"01":"Title"
		,"02":"Artist"
		,"03":"Genre"
		,"04":"Album"
		,"06":"Channel Number"
		,"07":"Channel Name"}

FLASH_TIMES = {"00 00":"Constant"
	      ,"7F 00":"1.27 sec"
	      ,"00 01":"2.56 sec"
	      ,"00 02":"5.12 sec"
	      ,"00 03":"7.68 sec"
	      ,"00 04":"10.24 sec"}

SOURCE_STRINGS = [[" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
		 ,[" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
		 ,[" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
		 ,[" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
		 ,[" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
		 ,[" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]]

ANY = "any"
ALL = "all"
CURRENT = "current"

class Russound(object):

	######################################################################################
	# class init & del
	def __init__(self, plugin):
		self.plugin = plugin
		self.needToGetPluginPrefs = True
		self.numberOfControllers = 1
		self.numberOfSources = 1
		self.sourceList = []
		self.connectionType = None
		self.socketIP = None
		self.socketPort = None
		self.serialPort = None
		self.serialPortName = None
		self.sock = None
		self.connected = False
		self.controllerType = None
		self.zonesPerController = None
		self.sourceKeyPadID = None

	def __del__(self):
		pass




	######################################################################################
	# Concurrent Thread Start
	def runConcurrentThread(self):
		self.plugin.debugLog(u"Running Concurrent Thread")

		time_start = time.time()
		mindex = 0

		while self.plugin.StopThread == False:

			if self.needToGetPluginPrefs:
				self.connected = False
				if self.getPluginPrefs():
					self.openConnection()

			if self.connected:
				self.checkForMessages()
			self.plugin.sleep(0.01)

			if (time.time() - time_start) >= 5:
				self.updateDisplayMessage(mindex)
				time_start = time.time()
				if mindex == 0:
					mindex = 1
				elif mindex == 1:
					mindex = 3
				elif mindex == 3:
					mindex = 5
				elif mindex == 5:
					mindex = 6
				elif mindex == 6:
					mindex = 0

		if self.connected:
			self.closeConnection()




	######################################################################################
	# Open and close connections
	def openConnection(self):
		self.plugin.debugLog(u"Opening connection....")
		if self.connectionType == SERIAL_PORT:
			if self.serialPort != None:
				self.serialPort.close()
				self.serialPort = None
			self.serialPort = self.plugin.openSerial(u"Russound Plugin", self.serialPortName, 19200, timeout=1, writeTimeout=1)
			if self.serialPort:
				indigo.server.log(u"Serial Port: %s opened succesfully" % self.serialPortName)
				self.serialPort.flushInput()
			else:
				indigo.server.log(u"Serial Port: %s failed to open. Please check the Russound configuration." % self.serialPortName, isError=True)
				return
		else:
			self.sock = socket(AF_INET, SOCK_STREAM)
			try:
				self.sock.settimeout(SOCKET_TIMEOUT)
				self.sock.connect((self.socketIP, int(self.socketPort)))
				indigo.server.log(u"Socket: %s:%s connected succesfully" % (self.socketIP, self.socketPort))
			except:
				indigo.server.log(u"Socket: %s:%s failed to connect. Please check the Russound configuration." % (self.socketIP, self.socketPort), isError=True)
				return
		self.connected = True
		self.pollAllZones()

	def closeConnection(self):
			if self.connectionType == SERIAL_PORT:
				self.serialPort.close()
				indigo.server.log(u"Serial Port: %s closed succesfully" % self.serialPortName)
			else:
				self.sock.close()
				indigo.server.log(u"Socket: %s:%s closed succesfully" % (self.socketIP, self.socketPort))




	######################################################################################
	# Sending and Receiving
	def sendMessage(self, msg):
		msg = msg.split(" ")
		msg.append(self.getRNETCheckSum(msg)) 
		msg.append(RNET_EOM)
		self.displayRNETMessage(msg, "TX: ")
		if self.connectionType == SERIAL_PORT:
			self.serialPort.write(binascii.unhexlify("".join(msg)))
		else:
	 		self.sock.send(binascii.unhexlify("".join(msg)))
		self.plugin.sleep(SECONDS_BETWEEN_SENDING)

 	def readSerialPort(self):
		stream = self.serialPort.readline(eol=binascii.unhexlify(RNET_EOM))
		if len(stream) != 0:
			return (stream)

	def readSocket(self):
		msg = []
		try:
			while True:
				data = self.sock.recv(1)
				msg.append(data)
				if data == binascii.unhexlify(RNET_EOM):
					break
			return msg
		except:
			pass




	######################################################################################
	# Check for messages
	def checkForMessages(self):
		while True:
			if self.connectionType == SERIAL_PORT:
				msg = self.readSerialPort()
			else:
				msg = self.readSocket()
			if msg == None:
				break
			else:
				msg = self.convertRNETMessageForProcessing(msg)
				if self.RNETMessageIsValid(msg):
					self.processMessage(msg)
				else:
					indigo.server.log(u"Invalid RNET Message: %s" % " ".join(msg), isError=True)




	######################################################################################
	# RNET Message Triage
	def processMessage(self, msg):
		self.displayRNETMessage(msg, "RX: ")
		self.displayRNETMessageHeader(msg)
		if msg[MESSAGE_TYPE] == MESSAGE_TYPE_SET_DATA:
			self.processSetDataMessage(msg)
		elif msg[MESSAGE_TYPE] == MESSAGE_TYPE_EVENT:
			self.processEventMessage(msg)
 		elif msg[MESSAGE_TYPE] == MESSAGE_TPYE_RENDERED_DISPLAY:
			self.processRenderedDisplayMessage(msg)
		else:
			self.plugin.debugLog(NOT_HANDLED_BY_PLUGIN)		




	######################################################################################
	# Set Data Message
	def processSetDataMessage(self, msg):
		#Display Feenback
		if msg[TARGET_KEYPAD_ID] == "79":
			self.processDisplayFeedback(msg)
			return	
		#polling replies
		if msg[TARGET_KEYPAD_ID] == self.sourceKeyPadID and msg[SOURCE_KEYPAD_ID] == THE_CONTROLLER_ITSELF and msg[10] == "02":
			if msg[13] == "07" and msg[16] == "01" and msg[18] == "0C":
				self.updateZoneDeviceStates(msg)
			elif msg[14] == "04" and msg[17] == "01" and msg[19] == "01":
				self.updateZoneTurnOnVolumeState(msg)
			elif msg[9] == "05" and msg[14] == "05" and msg[17] == "01":
				self.updateZoneBGColorState(msg)
		#display element
		if msg[TARGET_KEYPAD_ID] == ALL_ZONE_KEYPADS and msg[SOURCE_KEYPAD_ID] == THE_CONTROLLER_ITSELF: 
			if msg[TARGET_PATH_NUM_LEVELS] == "03" and msg[9] == PRODUCT_SPECIFIC_OBJECTS and msg[10] == "04":
				displayElement = msg[11]
				self.plugin.debugLog(u"\t Display Element:   %s %s" % (displayElement, self.getDisplayElementName(displayElement)))
				self.plugin.debugLog(u"\t Value:             %s" % msg[21])
				dev = self.getDeviceFromControllerIDAndZoneID(msg[TARGET_CONTROLLER_ID], msg[TARGET_ZONE_ID])
				if dev != None:
					if displayElement == "02": #"Shared Source Indication"
						self.updateStateOnServer(dev, "SharedSource", value=self.russoundOnOffState2English(msg[21]))		
		#display messages		
		if msg[TARGET_PATH_NUM_LEVELS] == "02" and msg[9] == "01" and msg[10] == "01" and msg[11] == "02" and msg[12] == "01" and msg[13] == "01":
			displayMessage = ""
			if msg[18] == "00" or msg[23] == "00":
				pass
			else:
				index = 23 + msg.count(RNET_INVERT_CHAR)
				for i in range(index + msg.count(RNET_INVERT_CHAR), len(msg) - 2):
					if msg[i] == "00":
						break
					else:
						displayMessage = displayMessage + chr(self.hex2dec(msg[i]))
			self.plugin.debugLog(u"\t Message:           %s" % displayMessage)
			dev = self.getDeviceFromControllerIDAndZoneID(msg[TARGET_CONTROLLER_ID], msg[TARGET_ZONE_ID])
			if dev != None:
				self.updateStateOnServer(dev, "DisplayMessage", displayMessage)
				if displayMessage == "Hello": # remove the display after the set time as the controller doesn't clear it via a message.
					self.plugin.sleep(self.hex2dec(msg[index - 2]) / 100)
					self.updateStateOnServer(dev, "DisplayMessage", "")
					
					
					
					
	######################################################################################
	# Event Message
	def processDisplayFeedback(self, msg):
		if msg[20].decode("hex") < chr(int('0x20',16)):
			self.plugin.debugLog(u"\t Source Broadcast Display Feedback")
			sourceID = str(int(msg[20], 16) - 16).zfill(2)
			self.plugin.debugLog(u"\t Source ID: %s" % sourceID)
			displayMessage = ""
			index = 23 + msg.count(RNET_INVERT_CHAR)
			for i in range(index + msg.count(RNET_INVERT_CHAR), len(msg) - 2):
				if msg[i] == "00":
					break
				else:
					displayMessage = displayMessage + chr(self.hex2dec(msg[i]))
			self.plugin.debugLog(u"\t Display Message: %s" % displayMessage)
			for dev in indigo.devices.iter("self.russoundZone"):
				if dev.states["SourceID"] == str(sourceID) and dev.states["Power"] == "on":
					self.updateStateOnServer(dev, "DisplayMessage", displayMessage)
		else:
			self.plugin.debugLog(u"\t MultiField Broadcast Display Feedback")
			sourceID = str(int(msg[20], 16) - 32).zfill(2)
			self.plugin.debugLog(u"\t Source ID: %s" % sourceID)
			if msg[21] == RNET_INVERT_CHAR:
				fieldID = str(~int(msg[22],16) & int('0x3f',16)).zfill(2)
			else:
				fieldID = str(int(msg[21],16) & int('0x3f',16)).zfill(2)
			self.plugin.debugLog(u"\t  Field ID: %s" % fieldID)
			displayMessage = ""
			index = 23
			for i in range(index + msg.count(RNET_INVERT_CHAR), len(msg) - 2):
				if msg[i] == "00":
					break
				else:
					displayMessage = displayMessage + chr(self.hex2dec(msg[i]))
			self.plugin.debugLog(u"\t Display Message: %s" % displayMessage)
			SOURCE_STRINGS[int(sourceID)-1][int(fieldID)-1] = displayMessage
			self.plugin.debugLog(u"\t Source Strings: %s" % SOURCE_STRINGS[int(sourceID)-1])
			# to be removed
			if fieldID == "01":
				for dev in indigo.devices.iter("self.russoundZone"):
					if dev.states["SourceID"] == sourceID and dev.states["Power"] == "on":
						self.updateStateOnServer(dev, "DisplayMessage", value=displayMessage)


	

	######################################################################################
	# Event Message
	def processEventMessage(self, msg):
		if msg[TARGET_CONTROLLER_ID] == ALL_CONTROLLERS:
			return #might be useful later
		eventIDLowByte = self.getEventIDLowByte(msg)
		self.plugin.debugLog(u"\t Event ID Low Byte: %s" % eventIDLowByte)
		eventData = ""
		self.plugin.debugLog(u"\t Event Name:        %s" % self.getKeyPadEventName(eventIDLowByte))
		controllerID = msg[SOURCE_CONTROLLER_ID]
		zoneID = msg[SOURCE_ZONE_ID]
		if eventIDLowByte == REMOTE_CONTROL_KEY_RELEASE:
			eventData = msg[20] #Event Data Lo Byte
			self.plugin.debugLog(u"\t Event Data:        %s" % eventData)
			self.plugin.debugLog(u"\t Event Data Name:   %s" % self.getSourceControlEventName(eventData))
		elif msg[TARGET_ZONE_ID] == PERIPHERAL_DEVICE:
			eventID = eventIDLowByte
			#controllerID = msg[15]
			#zoneID = msg[17]
			self.plugin.debugLog(u"\t Event Data:        %s" % eventIDLowByte)
			self.plugin.debugLog(u"\t Event Data Name:   %s" % self.getSourceControlEventName(eventIDLowByte))
		elif eventIDLowByte == POWER:
			self.plugin.debugLog(u"\t Power State:       %s" % msg[17])
			dev = self.getDeviceFromControllerIDAndZoneID(msg[TARGET_CONTROLLER_ID], msg[TARGET_ZONE_ID])
			if dev != None:
				if self.controllerType == "CAV6.6" or self.controllerType == "CAM6.6" or self.controllerType == "CAA66":
					powerByteNumber = 17
				else:
					powerByteNumber = 16
				self.updateStateOnServer(dev, "Power", self.russoundOnOffState2English(msg[powerByteNumber]))
				if msg[powerByteNumber] == "00":
					self.updateStateOnServer(dev, "Volume", dev.states["TurnOnVolume"])		
		self.checkTriggers(controllerID, zoneID, eventIDLowByte, eventData, msg)




	######################################################################################
	# Rendered Display Message
	def processRenderedDisplayMessage(self, msg):
		renderType = msg[12 + msg.count(RNET_INVERT_CHAR)]
		self.plugin.debugLog(u"\t Render Type:       %s %s" % (renderType, self.getRenderTypeName(renderType)))
		self.plugin.debugLog(u"\t Value Low Byte:    %s" % msg[VALUE_LOW_BYTE])
		self.plugin.debugLog(u"\t Value High Byte:   %s" % msg[VALUE_HIGH_BYTE])
		dev = self.getDeviceFromControllerIDAndZoneID(msg[TARGET_CONTROLLER_ID], msg[TARGET_ZONE_ID])
		if dev != None:
			if renderType == SOURCE_NAME:
				self.updateStateOnServer(dev, "Source", self.sourceList[int(msg[VALUE_HIGH_BYTE])][1])
				self.updateStateOnServer(dev, "SourceID", msg[VALUE_HIGH_BYTE])
				self.updateStateOnServer(dev, "DisplayMessage", self.sourceList[int(msg[VALUE_HIGH_BYTE])][1])
			elif renderType == VOLUME:
				self.updateStateOnServer(dev, "Volume", self.hex2dec(msg[VALUE_LOW_BYTE])*2)
			elif renderType == BASS:
				self.updateStateOnServer(dev, "Bass", self.formatBassTreble(msg[VALUE_LOW_BYTE]))
			elif renderType == TREBLE:
				self.updateStateOnServer(dev, "Treble", self.formatBassTreble(msg[VALUE_LOW_BYTE]))
			elif renderType == BALANCE:
				self.updateStateOnServer(dev, "Balance", self.formatBalance(msg[VALUE_LOW_BYTE]))
			elif renderType == ON_OFF:
				if msg[9] == "1F": # Loudness
					self.updateStateOnServer(dev, "Loudness", self.russoundOnOffState2English(msg[VALUE_LOW_BYTE]))




	######################################################################################
	# Polling
	def pollAllZones(self):
		self.plugin.debugLog(u"Polling All Russound Zones")
		for controllerID in range(0, int(self.numberOfControllers)):
			for zoneID in range(0, self.zonesPerController):
				self.pollZone(str(controllerID).zfill(2), str(zoneID).zfill(2))
		self.plugin.debugLog(u"Waiting for a reply from the controller....")

	def pollZone(self, controllerID, zoneID):
		self.plugin.debugLog("Polling Controller: %s Zone: %s" % (controllerID, zoneID))
		self.sendMessage(POLL_ZONE_STATE_MSG.replace("cc", controllerID).replace("zz", zoneID).replace("kk", self.sourceKeyPadID))
		self.sendMessage(POLL_ZONE_ON_VOLUME_MSG.replace("cc", controllerID).replace("zz", zoneID).replace("kk", self.sourceKeyPadID))
		self.sendMessage(POLL_ZONE_BG_COLOR_MSG.replace("cc", controllerID).replace("zz", zoneID).replace("kk", self.sourceKeyPadID))


	def updateZoneTurnOnVolumeState(self, msg):
		dev = self.getDeviceFromControllerIDAndZoneID(msg[4], msg[12])
		if dev != None:
			self.updateStateOnServer(dev, "TurnOnVolume", value=self.hex2dec(msg[21])*2)
		
	def updateZoneBGColorState(self, msg):
		dev = self.getDeviceFromControllerIDAndZoneID(msg[4], msg[12])
		if dev != None:
			self.updateStateOnServer(dev, "BGColor", value=self.formatBGColor(msg[21]))
		
	def updateZoneDeviceStates(self, msg):
		self.plugin.debugLog(u"\t Updating Zone Device States for Controller: %s Zone: %s" % (msg[4], msg[12]))
		dev = self.getDeviceFromControllerIDAndZoneID(msg[4], msg[12])
		if dev != None:
			self.updateStateOnServer(dev, "Power", value=self.russoundOnOffState2English(msg[20]))
			self.updateStateOnServer(dev, "Source", value=self.sourceList[int(msg[21])][1])
			self.updateStateOnServer(dev, "SourceID", value=msg[21])
			self.updateStateOnServer(dev, "Volume", value=self.hex2dec(msg[22])*2)
			self.updateStateOnServer(dev, "Bass", value=self.formatBassTreble(msg[23]))
			self.updateStateOnServer(dev, "Treble", value=self.formatBassTreble(msg[24]))
			self.updateStateOnServer(dev, "Loudness", value=self.russoundOnOffState2English(msg[25]))
			self.updateStateOnServer(dev, "Balance", value=self.formatBalance(msg[26]))
			self.updateStateOnServer(dev, "SystemOnState", value=self.formatSystemOnState(msg[27]))
			self.updateStateOnServer(dev, "SharedSource", value=self.russoundOnOffState2English(msg[28]))
			self.updateStateOnServer(dev, "PartyMode", self.formatPartyMode(msg[29]))
			self.updateStateOnServer(dev, "DoNotDisturb", value=self.russoundOnOffState2English(msg[30]))




	######################################################################################
	# Triggers
	def checkTriggers(self, controllerID, zoneID, eventIDLowByte, eventData, msg):
		self.plugin.debugLog("\t Checking Triggers")
		if eventIDLowByte == REMOTE_CONTROL_KEY_RELEASE:
			eventID = eventData
			triggerType = "sourceControlEvent"
		elif msg[TARGET_ZONE_ID] == PERIPHERAL_DEVICE:
			eventID = eventIDLowByte
			triggerType = "sourceControlEvent"
		else:
			eventID = eventIDLowByte
			triggerType = "keypadEvent"
		for trigger in indigo.triggers.iter("self.%s" % triggerType):
			trgDeviceID = trigger.pluginProps[u'deviceId']
			trgSourceID = trigger.pluginProps[u"sourceID"]
			trgEventID = trigger.pluginProps[u'eventID']
			if trgEventID != eventID:
				continue
			elif trgDeviceID == ANY and trgSourceID == ANY:
				self.plugin.debugLog(u"\t Trigger: DeviceID:%s, SourceID:%s, EventID:%s, ControllerID:%s, ZoneID:%s" % (trgDeviceID, trgSourceID, trgEventID, controllerID, zoneID))
				indigo.trigger.execute(trigger)
			elif trgDeviceID == ANY and trgSourceID != ANY:
				for dev in indigo.devices.iter("self.russoundZone"):
					if trgSourceID == dev.states["SourceID"]:
						self.plugin.debugLog(u"\t Trigger: DeviceID:%s, SourceID:%s, EventID:%s, ControllerID:%s, ZoneID:%s" % (trgDeviceID, trgSourceID, trgEventID, controllerID, zoneID))
						indigo.trigger.execute(trigger)
						break
			elif trgDeviceID == CURRENT:
				for dev in indigo.devices.iter("self.russoundZone"):
					if dev.pluginProps["controllerID"] == controllerID and dev.pluginProps["zoneID"] == zoneID:
						self.plugin.debugLog(u"\t Trigger: DeviceID:%s, SourceID:%s, EventID:%s, ControllerID:%s, ZoneID:%s" % (trgDeviceID, trgSourceID, trgEventID, controllerID, zoneID))
						if trgSourceID == ANY:
							indigo.trigger.execute(trigger)
						elif trgSourceID == dev.states["SourceID"]:
							indigo.trigger.execute(trigger)
			elif trgDeviceID != ANY:
				dev = indigo.devices[int(trgDeviceID)]
				if dev != None:
					if dev.pluginProps["controllerID"] == controllerID and dev.pluginProps["zoneID"] == zoneID: 
						if trgSourceID == ANY:
							self.plugin.debugLog(u"\t Trigger: DeviceID:%s, SourceID:%s, EventID:%s, ControllerID:%s, ZoneID:%s" % (trgDeviceID, trgSourceID, trgEventID, controllerID, zoneID))
							indigo.trigger.execute(trigger)
						elif trgSourceID == dev.states["SourceID"]:
							self.plugin.debugLog(u"\t Trigger: DeviceID:%s, SourceID:%s, EventID:%s, ControllerID:%s, ZoneID:%s" % (trgDeviceID, trgSourceID, trgEventID, controllerID, zoneID))
							indigo.trigger.execute(trigger)




	######################################################################################
	# Actions
	def actionGeneric(self, pluginAction, action):
		dev = None
		if pluginAction.deviceId != 0:
			dev = indigo.devices[pluginAction.deviceId]
			controllerID = dev.pluginProps["controllerID"]
			zoneID = dev.pluginProps["zoneID"]
		msg = ACTION_MESSAGES[action]
		if msg != None:
			msg = msg.replace("kk", self.sourceKeyPadID)
			if dev != None:
				msg = msg.replace("cc", controllerID)
				msg = msg.replace("zz", zoneID)
		if action == "pollAllZones":
			self.pollAllZones()
		elif action == "sendMessageToAllZones" or action == "sendMessageToZone":
			chars = pluginAction.props.get("setting")
			indigo_flash = pluginAction.props.get("setting_flash")
			if chars[0] == '%':
				indigo_var = chars.lstrip('%')
				chars = indigo.variables[indigo_var].value[:12]
			elif chars[0] == "#":
				indigo_var = chars.lstrip('#')
				indigo_varlist = indigo_var.split(',')
				indigo_dev = indigo.devices[indigo_varlist[0]]
				indigo_state = indigo_varlist[1]
				chars = indigo_dev.states[indigo_state][:12]
			else:
				chars = chars[:12]
			msg = msg.replace("ff", indigo_flash)
			msg = msg.split(" ")
			for idx, val in enumerate(chars):
				msg[idx + 21] = self.ascii2hex(val)
			self.plugin.debugLog(u"\t Display Message: %s" % chars)
			self.sendMessage(" ".join(msg))
		elif action == "updateDisplayMessageInZone":
			chars = pluginAction.props.get("setting")
			if chars[0] == '%':
				indigo_var = chars.lstrip('%')
				chars = indigo.variables[indigo_var].value[:40]
			elif chars[0] == "#":
				indigo_var = chars.lstrip('#')
				indigo_varlist = indigo_var.split(',')
				indigo_dev = indigo.devices[indigo_varlist[0]]
				indigo_state = indigo_varlist[1]
				chars = indigo_dev.states[indigo_state][:40]
			else:
				chars = chars[:40]
			self.plugin.debugLog(u"\t Display Message: %s" % chars)
			self.updateStateOnServer(dev, "DisplayMessage", chars)
		elif action == "sendSourceBroadcast":
			indigo_src = pluginAction.props.get("setting_source")
			indigo_flash = pluginAction.props.get("setting_flash")
			chars = pluginAction.props.get("setting")
			if chars[0] == '%':
				indigo_var = chars.lstrip('%')
				chars = indigo.variables[indigo_var].value[:40]
			elif chars[0] == "#":
				indigo_var = chars.lstrip('#')
				indigo_varlist = indigo_var.split(',')
				indigo_dev = indigo.devices[indigo_varlist[0]]
				indigo_state = indigo_varlist[1]
				chars = indigo_dev.states[indigo_state][:40]
			else:
				chars = chars[:37]
			msg = msg.replace("ss", self.dec2hex((int(indigo_src) + 16)))
			msg = msg.replace("ff", indigo_flash)
			msg = msg.split(" ")
			for idx, val in enumerate(chars):
				msg[idx + 23] = self.ascii2hex(val)
			self.plugin.debugLog(u"\t Display Message: %s" % chars)
			self.sendMessage(" ".join(msg))
			for dev in indigo.devices.iter("self.russoundZone"):
				if dev.states["SourceID"] == indigo_src and dev.states["Power"] == "on":
					self.updateStateOnServer(dev, "DisplayMessage", chars)
		elif action == "sendMultiFieldBroadcast":
			indigo_src = pluginAction.props.get("setting_source")
			field_id = pluginAction.props.get("setting_field")
			chars = pluginAction.props.get("setting")
			if chars[0] == '%':
				indigo_var = chars.lstrip('%')
				chars = indigo.variables[indigo_var].value[:40]
			elif chars[0] == "#":
				indigo_var = chars.lstrip('#')
				indigo_varlist = indigo_var.split(',')
				indigo_dev = indigo.devices[indigo_varlist[0]]
				indigo_state = indigo_varlist[1]
				chars = indigo_dev.states[indigo_state][:40]
			else:
				chars = chars[:37]
			if (chars != "" and chars != " " and chars != "------"):
				msg = msg.replace("ss", self.dec2hex((int(indigo_src) + 32)))
				msg = msg.replace("ff", self.dec2hex((127 - int(field_id))))
				msg = msg.split(" ")
				for idx, val in enumerate(chars):
					msg[idx + 24] = self.ascii2hex(val)
				self.plugin.debugLog(u"\t Display Message: %s" % chars)
				self.sendMessage(" ".join(msg))
				SOURCE_STRINGS[int(indigo_src)-1][int(field_id)-1] = chars
				self.plugin.debugLog(u"\t Source Strings: %s" % SOURCE_STRINGS[int(indigo_src)-1])
			else:
				SOURCE_STRINGS[int(indigo_src)-1][int(field_id)-1] = " "
		elif action == "pollZone":
			self.pollZone(controllerID, zoneID)
		elif action == "turnAllZonesOn":
			if self.controllerType == "CAV6.6" or self.controllerType == "CAM6.6" or self.controllerType == "CAA66":
				self.sendMessage("F0 7E 00 7F 00 00 70 05 02 02 00 00 F1 22 00 00 01 00 00 01")
			else:
				self.sendMessage("F0 7E 00 7F 00 00 71 05 02 02 00 00 F1 22 00 01 00 00 00 01")
		elif action == "directTuning":
			indigo_src = pluginAction.props.get("setting_source")
			msg = ACTION_MESSAGES["tunerDirectMode"]
			msg = msg.replace("kk", indigo_src)
			self.sendMessage(msg)
			chars = pluginAction.props.get("setting")
			for i in chars:
				if (i != '.'):
					if int(i) == 0:
						dd = '0A'
					else:
						dd = self.dec2hex(int(i))
					msg = ACTION_MESSAGES["tunerFrequency"]
					msg = msg.replace("kk", indigo_src)
					msg = msg.replace("##", dd)
					self.plugin.sleep(SECONDS_BETWEEN_SENDING)
					self.sendMessage(msg)
		else:
			setting = pluginAction.props.get("setting")
			if setting != None:
				msg = msg.replace("##", setting)
			self.sendMessage(msg)

	def turnAllZonesOff(self):
		self.sendMessage(ACTION_MESSAGES["turnAllZonesOff"].replace("kk", self.sourceKeyPadID))




	######################################################################################
	# Plugin Preferences
	def getPluginPrefs(self):
		try:		
			if self.plugin.pluginPrefs[u'showDebugInLog'] == True:
				self.plugin.debug = True
			else:
				self.plugin.debug = False
			self.plugin.debugLog(u"Getting Plugin Configuration Settings")
			self.connectionType = self.plugin.pluginPrefs["connectionType"]
			self.serialPortName = self.plugin.pluginPrefs["serialPortName"]
			self.socketIP= self.plugin.pluginPrefs["socketIP"]
			self.socketPort = self.plugin.pluginPrefs["socketPort"]
			if self.connectionType == SERIAL_PORT:
				self.plugin.debugLog(u"\t Connection Type:  Serial Port")
				self.plugin.debugLog(u"\t Serial Port Name: %s" % self.serialPortName)
			else:	
				self.plugin.debugLog(u"\t Connection Type: Socket")
				self.plugin.debugLog(u"\t Socket IP:        %s" % self.socketIP)
				self.plugin.debugLog(u"\t Socket Port:      %s" % self.socketPort)
			self.controllerType = self.plugin.pluginPrefs["controllerType"]
			self.plugin.debugLog(u"\t Controller Type:  %s" % self.controllerType)
			self.zonesPerController = CONTROLLER_TYPES[self.controllerType]["ZonesPerController"]
			self.plugin.debugLog(u"\t Controller Zones: %s" % self.zonesPerController)
			self.sourceKeyPadID = CONTROLLER_TYPES[self.controllerType]["SourceKeyPadID"]
			self.numberOfControllers = self.plugin.pluginPrefs["numberOfControllers"]
			self.plugin.debugLog(u"\t Controllers:      %s" % self.numberOfControllers)
			self.numberOfSources = self.plugin.pluginPrefs["numberOfSources"]
			self.plugin.debugLog(u"\t Sources:          %s" % self.numberOfSources)
			self.sourceList = []
			for i in range(1, MAX_NUMBER_OF_SOURCES + 1):
				if self.plugin.pluginPrefs["nameOfSource%s" % i] == "":
					self.plugin.pluginPrefs["nameOfSource%s" % i] = "Source %s" % i
				self.sourceList.append( ( str(i - 1).zfill(2), self.plugin.pluginPrefs["nameOfSource%s" % i] ) )
			for i in range(1, int(self.numberOfSources) + 1):
				self.plugin.debugLog(u"\t Source %s:        %s " % (str(i).zfill(2), self.sourceList[i-1][1]))
			indigo.server.log("Saved Plugin Configuration")
			self.needToGetPluginPrefs = False
			return True
		except:
			self.plugin.debugLog(u"There was an error reading the plugin preferences. Please check your configuration.")
			self.plugin.sleep(3)
			return False			




	######################################################################################
	# UI Validation
	def validatePrefsConfigUi(self, valuesDict):
		self.plugin.debugLog(u"Vaidating Plugin Configuration")
		errorsDict = indigo.Dict()
		if valuesDict[u"connectionType"] == "":
			errorsDict[u"connectionType"] = u"Please select a connection type."
		elif valuesDict[u"connectionType"] == "1":
			if valuesDict[u"serialPortName"] == "":
				errorsDict[u"serialPortName"] = u"Please select a serial port."
		elif valuesDict[u"connectionType"] == "2":
			if valuesDict[u"socketIP"] == "":
				errorsDict[u"socketIP"] = u"Please enter a socket IP."
			if valuesDict[u"socketPort"] == "":
				errorsDict[u"socketPort"] = u"Please enter a socket port."
		if valuesDict[u"controllerType"] == "":
			errorsDict[u"controllerType"] = u"Please select a Russound Controller Type."
		if len(errorsDict) > 0:
			self.plugin.debugLog(u"\t Vaidation Erros")
			return (False, valuesDict, errorsDict)
		else:			
			self.plugin.debugLog(u"\t Vaidation Succesful")
			self.needToGetPluginPrefs = True
			return (True, valuesDict)




	######################################################################################
	# Plug in UI stuff
	def getControllerTypeList(self):
		array = []
		for controllerType in CONTROLLER_TYPES:
			array.append((controllerType, controllerType))
		array.sort()
		return array

	def getControllerList(self):
		array = []
		for i in range(1, int(self.numberOfControllers) + 1):
			array.append((str(i - 1).zfill(2), str(i)))
		return array

	def getZoneList(self):
		array = []
		for i in range(1, self.zonesPerController + 1):
			array.append((str(i - 1).zfill(2), str(i)))
		return array

	def getZoneDeviceList(self, filter=""):
		array = []
		if filter == "withAny":
			array.append((ANY, "Any Zone"))
		elif filter == "withAnyCurrent":
			array.append((ANY, "Any Zone"))
			array.append((CURRENT, "Current Zone"))
		elif filter == "withAll":
			array.append((ALL, "All Zones"))
		for dev in indigo.devices.iter("self.russoundZone"):
			array.append((dev.id, dev.name))
		return array

	def getSourceList(self, filter=""):
		array = []
		if filter == "withAny":
			array.append((ANY, "Any Source"))
		for i in range(1, int(self.numberOfSources) + 1):
			array.append((self.sourceList[i-1][0], self.sourceList[i-1][1]))
		return array
		
	def getSourceControlEventList(self):
		array = SOURCE_CONTROL_EVENTS.items()
		array.sort()
		return array

	def getKeypadEventList(self):
		array = KEYPAD_EVENTS.items()
		array.sort()
		return array

	def getVolumeList(self):
		array = []
		for i in range(0, 51):
			array.append((self.dec2hex(i), i * 2))
			i =+ 1
		return array
			
	def getBassTrebleBalanceList(self):
		array = []
		for i in range(0, 21):
			array.append((self.dec2hex(i), i - 10))
		return array

	def getFieldIDList (self):
		array = FIELDID_TYPES.items()
		array.sort()
		return array

	def getFlashTimesList (self):
		array = FLASH_TIMES.items()
		array.sort()
		return array




	######################################################################################
	# Utiliies`
	def convertRNETMessageForProcessing(self, msg):
		return 	map(self.hexifyAndUpper, msg)

	def hexifyAndUpper(self, i):
		return binascii.hexlify(i).upper()
	
	def ascii2hex(self, s):
		r = ord(s)
		if r >= 20 and r <= 126:
			r = self.dec2hex(r)
		else:
			r = 20
		return str(r)
		  
	def invertRNET(self, numHex):
		return  self.dec2hex(127 - (self.hex2dec(numHex) - 127) + 1)

	def RNETMessageIsValid(self, msg):
		if msg[0] == RNET_BOM and msg[-1] == RNET_EOM:
			if msg[-2].upper() == self.getRNETCheckSum(msg[0:-2]).upper():
				return True

	def displayRNETMessage(self, msg, prefix=""):
		self.plugin.debugLog(u"%s%s" % (prefix, " ".join(msg)))

	def displayRNETMessageHeader(self, msg):
		if self.plugin.debug:
			self.plugin.debugLog(u"\t Target Controller: %s" % msg[TARGET_CONTROLLER_ID])
			self.plugin.debugLog(u"\t Target Zone:       %s" % msg[TARGET_ZONE_ID])
			self.plugin.debugLog(u"\t Target Keypad:     %s" % msg[TARGET_KEYPAD_ID])
			self.plugin.debugLog(u"\t Source Controller: %s" % msg[SOURCE_CONTROLLER_ID])
			self.plugin.debugLog(u"\t Source Zone:       %s" % msg[SOURCE_ZONE_ID])
			self.plugin.debugLog(u"\t Source Keypad:     %s" % msg[SOURCE_KEYPAD_ID])
			self.plugin.debugLog(u"\t Message Type ID:   %s %s" % (msg[MESSAGE_TYPE], MSESSAGE_TYPES[msg[MESSAGE_TYPE]]))
				
	def getRNETCheckSum(self, msg):
		m = map(self.hex2dec, msg)
		return self.dec2hex((sum(m) + len(m)) & 127)

	def hex2dec(self, s):
		return int(s, 16)
		  
	def dec2hex(self, n):
		return ("%X" % n).zfill(2)
		
	def russoundOnOffState2English(self, onOffState):
		if onOffState == "00":
			return "off"
		else:
			return "on"

	def updateStateOnServer(self, dev, state, value):
		self.plugin.debugLog(u"\t Updating Device: %s, State: %s, Value: %s" % (dev.name, state, value))
		dev.updateStateOnServer(state, value=value)		
		
 	def getEventIDLowByte(self, msg):
		eventIDLowByteIndex = 10 + int(msg[TARGET_PATH_NUM_LEVELS]) + int(msg[9 + int(msg[TARGET_PATH_NUM_LEVELS])])
		if msg[eventIDLowByteIndex] == RNET_INVERT_CHAR:
			return self.invertRNET(msg[eventIDLowByteIndex + 1])
		else:
			return msg[eventIDLowByteIndex]
			
	def formatBalance(self, balance):
		bal = self.hex2dec(balance) - 10
		if bal < 0:
			return "L:" + str(abs(bal))
		elif bal > 0:
			return "R:" + str(bal)
		else:
			return "0"

	def formatBassTreble(self, setting):
		s = self.hex2dec(setting) - 10
		if s > 0:
			return "+" + str(s)
		else:
			return s

	def formatPartyMode(self, setting):
		if setting == "00":
			return "off"
		elif setting == "01":
			return "on"
		elif setting == "02":
			return "Master"
		else:		
			return "unknown"

	def formatSystemOnState(self, setting):
		if setting == "00":
			return "All Zones Off"
		else:
			return "Any Zone is On"
				
	def formatBGColor(self, setting):
		if setting == "00":
			return "off"
		elif setting == "01":
			return "Amber"
		elif setting == "02":
			return "Green"
		else:
			return "Unknown"
				
	def getDisplayElementName(self, displayElement):
		if displayElement not in DISPLAY_ELEMENTS or (DISPLAY_ELEMENTS[displayElement] is None):
			return "unknown"
		else:
			return DISPLAY_ELEMENTS[displayElement]

	def getKeyPadEventName(self, eventIDLowByte):
		if eventIDLowByte not in KEYPAD_EVENTS or (KEYPAD_EVENTS[eventIDLowByte] is None): 
			return "unknown"
		else:
			return KEYPAD_EVENTS[eventIDLowByte]

	def getSourceControlEventName(self, eventData):
		if eventData not in SOURCE_CONTROL_EVENTS or (SOURCE_CONTROL_EVENTS[eventData] is None):
			return "unknown"
		else:
			return SOURCE_CONTROL_EVENTS[eventData]

	def getRenderTypeName(self, renderType):
		if renderType not in RENDER_TYPES or (RENDER_TYPES[renderType] is None): 
			return "unknown"
		else:
			return RENDER_TYPES[renderType]

	def getDeviceFromControllerIDAndZoneID(self, controllerID, zoneID):
		for dev in indigo.devices.iter("self.russoundZone"):
			if dev.pluginProps["zoneID"] == zoneID and dev.pluginProps["controllerID"] == controllerID:
				return dev
		self.plugin.debugLog(u"\t The plugin can't find a device for Controller: %s Zone: %s. Please create a device for this zone in order to control it and get status updates." % (controllerID, zoneID))

	def updateDisplayMessage(self, mindex):
		for dev in indigo.devices.iter("self.russoundZone"):
			if dev.states["Power"] == "on":
				sourceID = int(dev.states["SourceID"]) - 1
				if SOURCE_STRINGS[sourceID][5] == "PAUSED":
					self.updateStateOnServer(dev, "DisplayMessage", SOURCE_STRINGS[sourceID][5])
				elif SOURCE_STRINGS[sourceID][mindex] != "" and SOURCE_STRINGS[sourceID][mindex] != ' ' and SOURCE_STRINGS[sourceID][mindex] != "------":
					self.updateStateOnServer(dev, "DisplayMessage", SOURCE_STRINGS[sourceID][mindex])
