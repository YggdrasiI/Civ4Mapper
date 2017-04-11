
This Mod extend Civ4 by a mechanism to take several screenshots
at predefined locations. The images could be combined into one big
by external tools.

An example toolchain is included: MergeScreenshots.py uses
ImageMagick to merge screenshot into one big file and/or into
a collection of tiles.

Usage:
  1. Enter a singleplayer or multiplayer game. (The
     save should be password-free! Otherwise, the game
     crashes if you add Screenshot.py to the mod/game files.)

  2. Press Q to start the looping process. The game should
     center on several plots and take a screenshot.
     At the end, copy them from
     [My Documents]\My Games\Beyond the Sword\Screenshots into
     a separate folder.


Installation:
  1. Copy TakeScreenshot.exe into your BTS folder. It simulates keypress events
     and should toggle the ingame mechanism for screenshots.
  2a) Copy this folder into the Mods-folder of Civ4:BTS.
      This is useful to render a good image for a scenario map.
      If your scenario/world builder file is loadable without mods (i.e. all
      non-DLL modifications), you could it also load with this mod.

  2b) Move Assets/Python/Screenshots.py into your Mod and add the following
      lines at the end of the __init__method in CvEventManager.py.
      (This is useful for post documentation of Pitboss/PBEM games.)

		# ScreenshotMap Mod - Begin
    import Screenshots
		self.screenshots = Screenshots.Screenshots(self)
		# ScreenshotMap Mod - End


  3)  Edit CivilizationIV.ini to start Civ4 in windowed mode with 1800x1000 resolution.
      (Read comment in Screenshot.py if you really need an other resolution. Geometry
      constants for 1024x768 are included, too.)

  4) (Optional) Use python script MergeScreenshots.py to combine images.
     This requires Imagemagick + Python.
     Copy script into your screenshot folder and run 'python MergeScreenshots.py -h' to show
     the arguments for the script.
     Default output filename: out.png

     (I've also added a faster, but really memory consuming
     variant of the script.)

  5) The tilled images of step 4 could be used in a
     simple HTML page with Leaflet.js, see Tools/mapviewer.

     Copy the mapviewer-folder on your http server or test
     it with 'python3 -m http.server'.

     Open http://localhost:8000/index.html to load the map.  As default, the included images
     from 'Tools/mapviewer/dummy_map' will be shown.

Requirements:
  Python + Imagemagick to merge the screenshots.


