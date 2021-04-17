
"""
Custom usage: window creation and mapping callbacks functions at module level
"""
import random

from moderngl_window.timers.clock import Timer

from pyrogen.src.pyrogen.ecs.shaders.simple_shader import SimpleShader
from pyrogen.src.pyrogen.rgrwindow.MAIN.pyrogen_app import PyrogenApp




def main():

    # instanciate shader object
    shader = SimpleShader("Basic Shader")

    # instanciate app
    app    = PyrogenApp()
    window = app.window

    app.addProgram( "Basic Program",
                    vertexStr   = shader.getVertex()  ,
                    geometryStr = shader.getGeometry(),
                    fragmentStr = shader.getFragment()  )

    app.prepareData()

    for field in app.context.info:
        print(f"{field} : {app.context.info[field]}")

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
            print(f"frameTime={round(1/average,1)}")
            TIMES = [1 / 60, ]  # TIMES[1:]

        app.render(time, frame_time)
        window.swap_buffers()

    window.destroy()






if __name__ == '__main__':
    main()
