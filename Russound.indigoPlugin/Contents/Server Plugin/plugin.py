#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2011, jottawa. All rights reserved.
# http://sites.google.com/site/russoundpluginforindigo/

import os
import sys
import re
from Russound import Russound

class Plugin(indigo.PluginBase):


	######################################################################################
	# class init & del
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.Russound = Russound(self)	
		self.debug = False
		self.StopThread = False
		
	def __del__(self):
		indigo.PluginBase.__del__(self)


	######################################################################################
	# plugin startup and shutdown
	def startup(self):
		self.debugLog(u"Method: startup")
		try:		
			if valuesDict[u"showDebugInfo"] == True:
				self.debug = True
			else:
				self.debug = False
		except:
			pass
		
	def shutdown(self):
		self.debugLog(u"Method: shutdown")


	######################################################################################
	# ConcurrentThread: Start & Stop
	def runConcurrentThread(self):
		self.debugLog(u"Method: runConcurrentThread")
		self.Russound.runConcurrentThread()

	def stopConcurrentThread(self):
		self.debugLog(u"Method: stopConcurrentThread")
		self.StopThread = True


	######################################################################################
	# Action Menthods
	
	
	def actionAllZonesOn(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "turnAllZonesOn")
		
	def actionAllZonesOff(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "turnAllZonesOff")
		
	def actionTurnZoneOn(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "turnZoneOn")
		
	def actionTurnZoneOff(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "turnZoneOff")
		
	def actionSetZoneSource(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "aetZoneSource")
		
	def actionSetZoneVolume(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "setZoneVolume")
		
	def actionSetZoneBalance(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "setZoneBalance")
		
	def actionTurnBalanceLeft(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "turnBalanceLeft")
		
	def actionTurnBalanceRight(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "turnBalanceRight")
		
	def actionSetZoneBass(self, pluginAction):
		self.Russound.actionGeneric(pluginAction ,"setZoneBass")
		
	def actionTurnBassUp(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "turnBassUp")
		
	def actionTurnBassDown(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "turnBassDown")
		
	def actionSetZoneTreble(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "setZoneTreble")
		
	def actionTurnTrebleUp(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "turnTrebleUp")
		
	def actionTurnTrebleDown(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "turnTrebleDown")
		
	def actionSetZoneLoudnessOn(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "setZoneLoudnessOn")
		
	def actionSetZoneLoudnessOff(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "setZoneLoudnessOff")
		
	def actionSourceControlEvent(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "sourceControl")
		
	def actionKeyPadEvent(self, pluginAction):
		self.Russound.actionGeneric(pluginAction,"keyPad")

	def actionSendMessageToAllZones(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "sendMessageToAllZones")
		
	def actionSendMessageToZone(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "sendMessageToZone")
		
	def actionUpdateDisplayMessageInZone(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "updateDisplayMessageInZone")
		
	def actionSendSourceBroadcast(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "sendSourceBroadcast")
		
	def actionSendMultiFieldBroadcast(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "sendMultiFieldBroadcast")
		
	def actionPollAllZones(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "pollAllZones")
		
	def actionPollZone(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "pollZone")
		
	def actionDirectTuning(self, pluginAction):
		self.Russound.actionGeneric(pluginAction, "directTuning")
		
		
		

	######################################################################################
	# Menu Items
	def menuPollAllZones(self):
		self.Russound.pollAllZones()

	def menuTurnAllZonesOff(self):
		self.Russound.turnAllZonesOff()



	######################################################################################
	# Validations for UI 
	def validatePrefsConfigUi(self, valuesDict):
		return self.Russound.validatePrefsConfigUi(valuesDict)
		
	def validateActionConfigUi(self, valuesDict, typeId, actionId):
		return (True, valuesDict)
		
	def validateEventConfigUi(self, valuesDict, typeId, eventId):
		return (True, valuesDict)

	def validateDeviceConfigUi(self, valuesDict, typeId, eventId):
		return (True, valuesDict)


	######################################################################################
	# Lists for UI 
	
	def getControllerTypeList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getControllerTypeList()

	def getZoneList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getZoneList()

	def getSourceControlEventList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getSourceControlEventList()

	def getKeypadEventList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getKeypadEventList()

	def getControllerList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getControllerList()
	
	def getZoneDeviceList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getZoneDeviceList(filter)

	def getSourceList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getSourceList(filter)

	def getVolumeList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getVolumeList()
		
	def getBassTrebleBalanceList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getBassTrebleBalanceList()
		
	def getFieldIDList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getFieldIDList()
		
	def getFlashTimesList(self, filter="", valuesDict=None, typeId="", targetId=0):
		return self.Russound.getFlashTimesList()
