from pyrogen.src.pyrogen import Launcher
from pyrogen.src.pyrogen.tutorials.scenes.simple_gfx import SimpleGfx

width      = 960
height     = 540
title      = "Simple_Gfx"
fullScreen = False
game = Launcher(width, height, title, fullScreen)
game.addScene( SimpleGfx, "scene01" )
game.start()
