from pyrogen.src.pyrogen.rgrwindow.MAIN.gamepadTest3Pyglet import PyrogenApp3




# TODO : Add a "type" of Gfx element in the vertex array
# so we can either render a sprite or a basic figure (oval, rectangle, filled or outlined, several colors or gradient, radial or linear gradients ?)
# No ! we will use the GPU file system instead


def main():


    # Instanciate app
    app    = PyrogenApp3(width=1280, height=720)

    # Add all images needed for this app
    app.addImage("ball", "images/ball.png")
    mini = 1
    maxi = 22
    for i in range(mini, maxi + 1):
        num = ("00" + str(i))[-3:]
        name = f"image{num}"
        app.addImage(name, f"images/{name}.png", (1, 5, 32, 32))
    mini = 23
    maxi = 28
    for i in range(mini, maxi + 1):
        num = ("00" + str(i))[-3:]
        name = f"image{num}"
        app.addImage(name, f"images/{name}.png", (3, 4, 32, 32), )

    # prepare sprite data etc....
    #app.prepareData()

    # run app
    app.run()



if __name__ == '__main__':
    main()

