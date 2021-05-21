import math
import moderngl
import moderngl_window
import pyglet
from moderngl_window import settings
from moderngl_window.timers.clock import Timer

gamepad = pyglet.input.get_joysticks()[0]
gamepad.open()

class PyrogenApp():

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

    def on_joybutton_press(self, joystick, button=0):
        print(f"\ngamepad={joystick} button={button}\n")

    def __init__(self, size=(1280,720), fullScreen=False):
        settings.WINDOW['class'] = 'moderngl_window.context.pyglet.Window'
        settings.WINDOW['vsync'] = True
        settings.WINDOW['size' ] = size
        self._window             = moderngl_window.create_window_from_settings()
        self._window.fullscreen  = fullScreen

        self._program            = None
        self._programs           = {}

        self._window.key_event_func            = self.keyboardEvent
        self._window.mouse_press_event_func    = self.mouseButtonPressed
        self._window.mouse_release_event_func  = self.mouseButtonReleased
        self._window.mouse_position_event_func = self.mouseMoveEvent
        self._window.mouse_drag_event_func     = self.mouseDragEvent
        self._window.mouse_scroll_event_func   = self.mouseScrollEvent

    @property
    def window(self):
        return self._window
    @property
    def context(self):
        return self._window.ctx

    def render(self, time, frame_time):
        print(gamepad.buttons, gamepad.hat_x, gamepad.hat_y)
        self._window.ctx.clear(
            (math.sin(time + 0) + 1.0) / 2,
            (math.sin(time + 2) + 1.0) / 2,
            (math.sin(time + 3) + 1.0) / 2,
        )
        self._window.ctx.enable(moderngl.BLEND)


def main():
    app    = PyrogenApp()
    window = app.window

    timer = Timer()
    timer.start()

    while not app.window.is_closing:
        time, frame_time = timer.next_frame()
        print("tick")
        pyglet.clock.tick()
        print("step")
        pyglet.app.platform_event_loop.step(0.001)
        print("render")
        app.render(time, frame_time)
        print("swap")
        window.swap_buffers()

    window.destroy()


if __name__ == '__main__':
    main()
