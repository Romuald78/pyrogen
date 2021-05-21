import math
import moderngl
import moderngl_window
import pyglet
from moderngl_window import settings
from moderngl_window.timers.clock import Timer


class PyrogenApp():

    #========================================================================
    # EVENT CALLBACKS
    #========================================================================
    def keyboardEvent(self, symbol, action, modifiers):
        isPressed = True if action==self._window.keys.ACTION_PRESS else False
        print(f"key:{symbol} pressed:{isPressed} modifiers:{modifiers}")

    def mouseButtonPressed(self, x, y, button):
        print(f"Button {button} is pressed @{x}/{y}")

    def mouseButtonReleased(self, x, y, button):
        print(f"Button {button} is released @{x}/{y}")

    def mouseMoveEvent(self, x, y, dx, dy):
        print(f"Moving mouse @{x}/{y} with speed:{dx}/{dy}")

    def mouseDragEvent(self, x, y, dx, dy):
        print(f"Dragging mouse @{x}/{y} with speed:{dx}/{dy}")

    def mouseScrollEvent(self, dx, dy):
        print(f"Scrolling mouse with speed:{dx}/{dy}")

    # TODO ==========================================
    # TODO =====            GAMEPADS            =====
    # TODO ==========================================
    def on_joybutton_press(self, joystick, button):
        print(f"\ngamepad={joystick} button={button}\n")
    # TODO ==========================================

    #========================================================================
    # CONSTRUCTOR
    #========================================================================
    def __init__(self, size=(1280,720), fullScreen=False):
        # Create a Pyglet window
        settings.WINDOW['class'] = 'moderngl_window.context.pyglet.Window'
        settings.WINDOW['vsync'] = True
        settings.WINDOW['size' ] = size
        self._window             = moderngl_window.create_window_from_settings()
        self._window.fullscreen  = fullScreen

        # Store a list of different programs
        # Only one can be selected at a time
        #the selected program will be used in the prepareData method
        self._program            = None
        self._programs           = {}

        # Map callback functions
        self._window.key_event_func            = self.keyboardEvent
        self._window.mouse_press_event_func    = self.mouseButtonPressed
        self._window.mouse_release_event_func  = self.mouseButtonReleased
        self._window.mouse_position_event_func = self.mouseMoveEvent
        self._window.mouse_drag_event_func     = self.mouseDragEvent
        self._window.mouse_scroll_event_func   = self.mouseScrollEvent

        # TODO ==========================================
        # TODO =====            GAMEPADS            =====
        # TODO ==========================================
        # Store gamepad list
        self.gamepads = pyglet.input.get_joysticks()
        # Check every connected gamepad
        if self.gamepads:
            for g in self.gamepads:
                print(g)
                # Link all gamepad callbacks to the current class methods
                g.open()
                #g.on_joybutton_press = self.on_joybutton_press
                #self._window._window.event(self.on_joybutton_press)
                #g.on_joybutton_release = self.__onButtonReleased
                #g.on_joyhat_motion     = self.__onCrossMove
                #g.on_joyaxis_motion    = self.__onAxisMove
        else:
            print("No gamepad connected !")
        # TODO ==========================================

    # ========================================================================
    # GETTERS
    # ========================================================================
    @property
    def window(self):
        return self._window
    @property
    def context(self):
        return self._window.ctx

    def render(self, time, frame_time):

        # Clear buffer with background color
        self._window.ctx.clear(
            (math.sin(time + 0) + 1.0) / 2,
            (math.sin(time + 2) + 1.0) / 2,
            (math.sin(time + 3) + 1.0) / 2,
        )

        self._window.ctx.enable(moderngl.BLEND)










def main():

    # Instanciate app
    app    = PyrogenApp()
    window = app.window

    for field in app.context.info:
        print(f"{field} : {app.context.info[field]}")

    timer = Timer()
    timer.start()

    while not app.window.is_closing:
        time, frame_time = timer.next_frame()

        pyglet.clock.tick()
        pyglet.app.platform_event_loop.step(0.01)

        app.render(time, frame_time)
        window.swap_buffers()

    window.destroy()



if __name__ == '__main__':
    main()

