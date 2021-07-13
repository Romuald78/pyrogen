from pyrogen.src.pyrogen.ecs3.main.pyrogen_app import PyrogenApp



def main():

    # -----------------------------------------------------------
    # INSTANCIATE APPLICATION
    # -----------------------------------------------------------
    app    = PyrogenApp(width=1920, height=1080, vsync=False)

    # -----------------------------------------------------------
    # ADD IMAGE RESOURCES
    # -----------------------------------------------------------
    # Add football image
    app.addImage("ball", "resources/images/fps_test/ball.png")
    # Add misc. sprites
    mini = 1
    maxi = 22
    for i in range(mini, maxi + 1):
        num = ("00" + str(i))[-3:]
        name = f"image{num}"
        app.addImage(name, f"resources/images/fps_test/{name}.png", (1, 5, 32, 32))
    # Add misc. sprites
    mini = 23
    maxi = 28
    for i in range(mini, maxi + 1):
        num = ("00" + str(i))[-3:]
        name = f"image{num}"
        app.addImage(name, f"resources/images/fps_test/{name}.png", (3, 4, 32, 32), )
    # Characters
    app.addImage("characters", f"resources/images/fps_test/characters001.png", (12, 8, 32, 48))

    # -----------------------------------------------------------
    # ADD FONT RESOURCES
    # -----------------------------------------------------------
    app.addFont("mandala", "resources/fonts/Mandala.ttf", 64)
    app.addFont("subway" , "resources/fonts/Subway.ttf" , 64)

    # -----------------------------------------------------------
    # RUN APPLICATION
    # -----------------------------------------------------------
    app.run()




if __name__ == '__main__':
    main()

