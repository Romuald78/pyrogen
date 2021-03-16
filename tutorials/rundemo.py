from .scenes.simple_gfx import SimpleGfx
from ..launcher import Launcher


def runDemo(title):

    print(f"Running '{title}'")

    scenes = {"SimpleGfx":{"width"     :960,
                           "height"    :540,
                           "fullScreen":False,
                           "sceneClass":SimpleGfx,
                           },
              }

    if title in scenes:
        # Create application instance
        game = Launcher( scenes[title]["width" ],
                         scenes[title]["height"],
                         title,
                         scenes[title]["fullScreen"],
                         )
        # Add scene to application
        game.addScene( scenes[title]["sceneClass"], title)
        # Run application
        game.start()
    else:
        msg  = f"\nThe demo name '{title}' does not exist.\n"
        msg += "To select and run a demo, please choose from following values : \n"
        for k in scenes.keys():
            msg += f"- '{k}'\n"
        raise RuntimeError(msg)
