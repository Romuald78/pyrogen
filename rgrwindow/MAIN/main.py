
from moderngl_window.timers.clock import Timer

from pyrogen.src.pyrogen.rgrwindow.MAIN.loader      import ResourceLoader
from pyrogen.src.pyrogen.ecs.shaders.simple_shader  import SimpleShader
from pyrogen.src.pyrogen.rgrwindow.MAIN.pyrogen_app import PyrogenApp





# TODO : Add a "type" of Gfx element in the vertex array
# so we can either render a sprite or a basic figure (oval, rectangle, filled or outlined, several colors or gradient, radial or linear gradients ?)

def main():

    # -------------------------------------------------------------------
    # Fill Loader
    # -------------------------------------------------------------------
    loader = ResourceLoader()

    loader.addImage("ball", "images/ball.png")
    mini = 1
    maxi = 22
    for i in range(mini, maxi + 1):
        num = ("00" + str(i))[-3:]
        name = f"image{num}"
        loader.addImage(name, f"images/{name}.png", (1, 5, 32, 32))
    mini = 23
    maxi = 28
    for i in range(mini, maxi + 1):
        num = ("00" + str(i))[-3:]
        name = f"image{num}"
        loader.addImage(name, f"images/{name}.png", (3, 4, 32, 32))

    loader.generateImageAtlas(600, 2)





    # -------------------------------------------------------------------
    # Application configuration
    # -------------------------------------------------------------------

    # Instanciate shader object
    shader = SimpleShader()

    # Instanciate app
    app    = PyrogenApp(loader, (1280,720))
    window = app.window

    # Add program to application
    app.addProgram( "Program #1",
                    vertexStr   = shader.getVertex()  ,
                    geometryStr = shader.getGeometry(),
                    fragmentStr = shader.getFragment()  )




    app.prepareData()

    for field in app.context.info:
        print(f"{field} : {app.context.info[field]}")

    input()

    TIMES = [1/60,]
    timer = Timer()
    timer.start()


    while not app.window.is_closing:
        time, frame_time = timer.next_frame()

        frame_time = max(0,frame_time)
        frame_time = min(1,frame_time)
        TIMES.append(frame_time)

        if len(TIMES)>30:
            average = sum(TIMES) / len(TIMES)
            print(f"FPS={round(1/average,1)}")
            TIMES = [1 / 60, ]

        app.render(time, frame_time)
        window.swap_buffers()

    window.destroy()



if __name__ == '__main__':
    main()

