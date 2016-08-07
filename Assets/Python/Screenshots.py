"""

	External requirements: 
		- Set the resolution in Civilization.ini to 1800x1000. Then, the Screenshots overlapps and blending
			allows us to merge them smoothly.
		- TakeScreenshot.exe: Put this into the Civ4:BTS directory. It simulates a 'Print Screen' keystroke.

		- ImageMagick	(optional): Useful tool to merge alle Images into one.
															The helper script MergeScreenshots.py could be used for this task. I.e. if the tiny
															map has 12 Screenshots, three in each row, and the saved Screenshots begin
															with Screenshot0000.JPG, call
															python [path to mapMerge.py] 3 4 0 [filename]

"""
import os
from CvPythonExtensions import *
import CvCameraControls
import CvScreenEnums

gc = CyGlobalContext()
localText = CyTranslator()

class Screenshots:
	def __init__(self, event_manager):
		# Begin operation without keypress
		self.startOnLoad = False
		# Print some debug messages into ingame chat 
		self.verbose = False  
		# made whole map visibile
		self.supermode = True
		# Store zoom value at game loading. (Will not reset at second game loading, etc!)
		self.the_zoom = None
		# Waiting time before first screenshot. Cooldown prevent logging messages on the screen.
		# Possible improvement: Hide the event overlay of the main interface. (where defined?)
		self.waitOnStart = 4*8
		# Saved, but nonrelevant for sattellite view
		self.pitch = CyCamera().GetBasePitch()
		# Rotation. Use 0.0
		self.turn = 0.0

		# List of key wich can be used to start/pause operation
		self.listen_keys = [int(InputTypes.KB_RETURN),
				int(InputTypes.KB_Q), int(InputTypes.KB_END)]

		# Internal 
		self.event_manager = event_manager
		self.bInitScrolling = False 
		self.bProcessScrolling = False
		self.skipSlice = 0 # for waitOnStart.
		self.count_img = 0
		self.cycle_num = 5
		self.cycle_state = 0

		""" State machine 
		cycle_state   | action
								0 | init at first occurence, wait otherwise 
								1 | wait (jumpin after init)
								2 | moveCamera to next point
								3 | wait (note that state will not increase until camera movement ends.)
		cycle_num-1=4 | Take screenshot

		"""

		# Resolution depended values.
		if False:
			""" 1024x768 case. Overlapping values:
					x-Direction: 205
					y-Direction: 39
			"""
			self.dS = {
					"start": [0, 6],
					"diff": [6, 6],
					}
		else:
			""" 1900x1000 case. Overlapping values:
					x-Direction: 177
					y-Direction: 188 (default)
					y-Direction: 483 (pitch = 15.0. Not recommended)

			"""
			self.dS = {
					"start": [0, 4],
					"diff": [14, 7],
					}

		self.update_event_handler()

	def update_event_handler(self):	
		""" Wrap some methodes. """
		self.onKbdEventBase, self.event_manager.EventHandlerMap["kbdEvent"] \
				= self.event_manager.EventHandlerMap["kbdEvent"], self.onKbdEvent
		self.onGameUpdateBase, self.event_manager.EventHandlerMap["gameUpdate"] \
				= self.event_manager.EventHandlerMap["gameUpdate"], self.onGameUpdate
		self.onUnInitBase, self.event_manager.EventHandlerMap["UnInit"] \
				= self.event_manager.EventHandlerMap["UnInit"], self.onUnInit
		self.onLoadGameBase, self.event_manager.EventHandlerMap["OnLoad"] \
				= self.event_manager.EventHandlerMap["OnLoad"], self.onLoadGame


	def onKbdEvent(self, argsList):
		eventType,key,mx,my,px,py = argsList
		if ( eventType == self.event_manager.EventKeyDown ):
			theKey=int(key)
			if (theKey in self.listen_keys):
				self.pauseScreenshotLoop()

		self.onKbdEventBase(argsList)

	def onGameUpdate(self, argsList):
		self.doScreenshotLoopStep()
		self.onGameUpdateBase(argsList)

	def onUnInit(self, argsList):
		#CyCamera().SetZoom(self.the_zoom)
		self.onUnInitBase(argsList)

	def onLoadGame(self, argsList):
		self.onLoadGameBase(argsList)

		if self.startOnLoad:
			self.bInitScrolling = True
			self.bProcessScrolling = False
			# Map specific factor...
			#self.the_zoom = None

	def initScreenshotLoop(self):

		if self.supermode and (gc.getGame().getActivePlayer() != -1):
			self.madeAllVisible(gc.getGame().getActivePlayer())
			self.removeAllSigns()

		self.bInitScrolling = False
		self.skipSlice = self.waitOnStart
		self.cycle_state = 1
		self.count_img = 0
		self.dS["current"] = [self.dS["start"][0]-self.dS["diff"][0], self.dS["start"][1]]

		# Check if top border conditions are bad and try to add an row in this case
		iH = CyMap().getGridHeight()
		s = self.dS["current"][1]
		while s < iH:
			s += self.dS["diff"][1]
		if (s-iH) < int(self.dS["start"][1]/2):
			self.dS["current"][1] -= 1 + int(self.dS["start"][1]/2) - (s-iH)

		self.initCamera()
		CyGame().doControl(ControlTypes.CONTROL_TOP_DOWN_CAMERA) # Toggle Satellte cam
		#CyGame().doControl(ControlTypes.CONTROL_GRID)
		#CyGame().doControl(ControlTypes.CONTROL_BARE_MAP) #no units

		self.bProcessScrolling = True
		self.logScreenshot("Init")

	def initCamera(self):
		# Interface
		CyInterface().setShowInterface(InterfaceVisibility.INTERFACE_HIDE_ALL)

		# Grid lines
		bGrid = CyUserProfile().getGrid()
		if not bGrid and False:
			screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
			screen.setState( "Grid", True )
			#[...] ControlTypes.CONTROL_GRID versenden?!

		# Camera
		#CvCameraControls.g_CameraControls.resetCameraControls()

		#CyCamera().ResetZoom()
		CyCamera().setOrthoCamera(True)
		CyCamera().SetCameraMovementSpeed(CameraMovementSpeeds.CAMERAMOVEMENTSPEED_FAST)

		CyCamera().SetBasePitch(self.pitch)
		CyCamera().SetBaseTurn(self.turn)


		""" Height depends on map size.
		Visible plots in a row with zoom=0.5
		Type	  |	Map size | approx. visible plots	| Default Zoom
		Duell	  |		 40x24 | 11x6							 			| .420840
		Medium  |		 64x40 | 11x6							  		| .423445
		Large	  |		104x64 | 15x8										| .0369631
		Huge	  |		128x80 | 19x10									| .293342
		"""
		iW = CyMap().getGridWidth()
		iH = CyMap().getGridHeight()
		#f = self.the_zoom * (2.0/25) * (16-1) # 11
		#f = self.the_zoom * (2.0/25) * (16-5) # 9
		f = self.the_zoom * (2.0/25) * (16+3) # 15
		
		import math
		self.logScreenshot("Map width: %d, Map height: %d; Startval: %f" % (iW, iH, self.the_zoom))
		CyCamera().SetZoom(f) # distance depends on map size.

	def abortScreenshotLoop(self):
			self.bProcessScrolling = False
			CyInterface().setShowInterface(InterfaceVisibility.INTERFACE_SHOW)

			chatMessage = "Num screenshots: "+str(self.count_img)
			self.logScreenshot(chatMessage, True)

	def pauseScreenshotLoop(self):
			if self.dS.get("current") is None:
				# First start
				self.bInitScrolling = True
				return

			self.bProcessScrolling = not self.bProcessScrolling
			if not self.bProcessScrolling:
				self.logScreenshot("Pause")
				CyInterface().setShowInterface(InterfaceVisibility.INTERFACE_SHOW)
			else:
				self.logScreenshot("Start/Resume")
				self.initCamera()
				self.cycle_state = 3
				coords = self.dS["current"]
				pPlot = CyMap().plot(coords[0],coords[1])
				CyCamera().JustLookAtPlot(pPlot)
				CyCamera().SetBasePitch(self.pitch)


	def doScreenshotLoopStep(self):
		# Turnslice accord 0.25s

		if CyGame().isPitbossHost():
			return

		if self.the_zoom is None:
			self.the_zoom = CyCamera().GetZoom()

		if self.skipSlice > 0:
			self.skipSlice -= 1
			return

		if CyCamera().isMoving():
			return

		frame = self.cycle_state
		self.cycle_state += 1

		if self.bInitScrolling and frame % self.cycle_num == 0:
			self.initScreenshotLoop()

		if self.bProcessScrolling:

			if frame % self.cycle_num == 2:
				self.logScreenshot("Move Camera...")
				iW = CyMap().getGridWidth()
				iH = CyMap().getGridHeight()

				coords = self.dS["current"]
				coords[0] += self.dS["diff"][0]
				if coords[0] >= iW: # - self.dS["diff"][0]/2:
					coords[0] = self.dS["start"][0]
					coords[1] += self.dS["diff"][1]
				if coords[1] >= iH:
					self.abortScreenshotLoop()

				self.dS["current"] = coords
				pPlot = CyMap().plot(coords[0],coords[1])
				CyCamera().JustLookAtPlot(pPlot)
				CyCamera().SetBasePitch(self.pitch)
				CyCamera().SetBaseTurn(self.turn)

				chatMessage = "New position: "+str(coords[0])+", "+str(coords[1])
				self.logScreenshot(chatMessage)

			if frame % self.cycle_num == 4:
				## Should called after a camera reposition.
				self.logScreenshot("Make Shot...")
				os.popen("TakeScreenshot.exe");
				self.count_img += 1

				# Manual abort criteria for debugging
				if self.count_img > 1 and False:
					self.abortScreenshotLoop()
		
	def logScreenshot(self, chatMessage, bForce=False):
		if self.verbose or bForce:
			gc.sendChat(chatMessage, -2)

	# Extras
	def madeAllVisible(self, playerId):
			gcPlayer = gc.getPlayer(playerId)
			gcTeam = gc.getTeam(gcPlayer.getTeam())

			# Kontakt zu allen Spielern
			for i in range(gc.getMAX_TEAMS()):
					if i == gcPlayer.getTeam():
							continue
					gcTeam.meet(i, False)

			# Spionage gegen alle Teams
			for i in range(gc.getMAX_PLAYERS()-1):
					if i == playerId:
							continue
					iP = gc.getPlayer(i)
					if (iP.isEverAlive()):
							gcTeam.setEspionagePointsAgainstTeam(iP.getTeam(), 1000000)

			# Karte aufdecken
			iGridW = CyMap().getGridWidth()
			iGridH = CyMap().getGridHeight()
			for iX in range(iGridW):
					for iY in range(iGridH):
							plot = CyMap().plot(iX, iY)
							plot.setRevealed(gcPlayer.getTeam(), True, False, -1)

			# Karte, Einheiten und unsichtbare Einheiten einsehbar
			for iX in range(iGridW):
					for iY in range(iGridH):
							plot = CyMap().plot(iX, iY)
							plot.changeVisibilityCount(gcPlayer.getTeam(), 1, 1)

	def removeAllSigns(self):
		# For Privacy 
		engine = CyEngine()
		for i in range(engine.getNumSigns()-1, -1, -1):
				pSign = engine.getSignByIndex(i)
				engine.removeSign(
						pSign.getPlot(),
						pSign.getPlayerType())
