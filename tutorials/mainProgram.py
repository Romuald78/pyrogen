
# Import pyrogen (either from the dev branch or the standard package build)
try:
    import pyrogen.src.pyrogen as pyrogen
except ImportError:
    import pyrogen



def mainProgram(title, sceneClass):
    # Create application instance
    game = pyrogen.Launcher(960, 540, f"Pyrogen Demo : [{title}]", False)
    # Add scene to application
    game.addScene(sceneClass, title)
    # Run application
    game.start()
