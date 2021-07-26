import pathlib

try:
    from pyrogen.ecs3.main.pyrogen_app import Pyrogen
    from pyrogen.tutorials.dev_test.scenes.dev_test_scene import FpsTest
except:
    from pyrogen.src.pyrogen.ecs3.main.pyrogen_app import Pyrogen
    from pyrogen.src.pyrogen.tutorials.dev_test.scenes.dev_test_scene import FpsTest


def main():

    # Set tutorial folder
    rootDir = pathlib.Path(__file__).parent.resolve()

    # -----------------------------------------------------------
    # INSTANCIATE APPLICATION
    # -----------------------------------------------------------
    app    = Pyrogen(width=1920,
                     height=1080,
                     vsync=False,
                     atlasDir=f"{rootDir}/resources/atlas",
                     fsGpuMemSize=1*1024*1024*4)

    # -----------------------------------------------------------
    # ADD IMAGE RESOURCES
    # -----------------------------------------------------------
    # Add football image
    app.addImage("ball", f"{rootDir}/resources/images/ball.png")
    # Add misc. sprites
    mini = 1
    maxi = 22
    for i in range(mini, maxi + 1):
        num = ("00" + str(i))[-3:]
        name = f"image{num}"
        app.addImage(name, f"{rootDir}/resources/images/{name}.png", (1, 5, 32, 32))
    # Add misc. sprites
    mini = 23
    maxi = 28
    for i in range(mini, maxi + 1):
        num = ("00" + str(i))[-3:]
        name = f"image{num}"
        app.addImage(name, f"{rootDir}/resources/images/{name}.png", (3, 4, 32, 32), )
    # Characters
    app.addImage("characters", f"{rootDir}/resources/images/characters001.png", (12, 8, 32, 48))

    # -----------------------------------------------------------
    # ADD FONT RESOURCES
    # -----------------------------------------------------------
    app.addFont("mandala", f"{rootDir}/resources/fonts/Mandala.ttf", 64)
    app.addFont("subway" , f"{rootDir}/resources/fonts/Subway.ttf" , 64)

    # -----------------------------------------------------------
    # FINALIZE RESOURCES
    # -----------------------------------------------------------
    app.finalizeResources()

    # -----------------------------------------------------------
    # ADD SCENES
    # -----------------------------------------------------------
    app.addScene( "MAIN", FpsTest() )

    # -----------------------------------------------------------
    # RUN APPLICATION
    # -----------------------------------------------------------
    app.run()









if __name__ == '__main__':
    main()

