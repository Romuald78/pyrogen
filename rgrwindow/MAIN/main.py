
"""
Custom usage: window creation and mapping callbacks functions at module level
"""
import random

from moderngl_window.timers.clock import Timer
from pyrogen.src.pyrogen.rgrwindow.MAIN.pyrogen_app import PyrogenApp


def getVertexShader():
    return """
        #version 330

        // The per sprite input data
        in vec2 in_position;
        in vec2 in_size;
        in float in_rotation;
        in vec4 in_atlas_pos;

        out vec2 size;
        out float rotation;
        out vec4 atlas_pos;

        void main() {
            // We just pass the values unmodified to the geometry shader
            gl_Position = vec4(in_position, 0, 1);
            size = in_size;
            rotation = in_rotation;
            atlas_pos = in_atlas_pos;
        }
    """

def getGeometryShader():
    return """
        #version 330

        // We are taking single points form the vertex shader
        // and emitting 4 new vertices creating a quad/sprites
        layout (points) in;
        layout (triangle_strip, max_vertices = 4) out;

        uniform mat4      projection;
        uniform sampler2D sprite_texture;

        // Since geometry shader can take multiple values from a vertex
        // shader we need to define the inputs from it as arrays.
        // In our instance we just take single values (points)
        in vec2 size[];
        in float rotation[];
        in vec4 atlas_pos[];
        out vec2 uv;

        void main() {
            // Get texture dimensions
            vec2 texDim = textureSize(sprite_texture,0);
            
            // Get texture coords
            float x0 = atlas_pos[0].x/texDim.x;
            float y0 = atlas_pos[0].y/texDim.y;
            float x1 = x0 + (atlas_pos[0].z/texDim.x);
            float y1 = y0 + (atlas_pos[0].w/texDim.y);

            // We grab the position value from the vertex shader
            vec2 center = gl_in[0].gl_Position.xy;
            // Calculate the half size of the sprites for easier calculations
            vec2 hsize = size[0] / 2.0;
            // Convert the rotation to radians
            float angle = radians(rotation[0]);
            // Create a 2d rotation matrix
            mat2 rot = mat2(
                cos(angle), sin(angle),
                -sin(angle), cos(angle)
            );

            // Emit a triangle strip creating a quad (4 vertices).
            // Here we need to make sure the rotation is applied before we position the sprite.
            // We just use hardcoded texture coordinates here. If an atlas is used we
            // can pass an additional vec4 for specific texture coordinates.
            // Each EmitVertex() emits values down the shader pipeline just like a single
            // run of a vertex shader, but in geomtry shaders we can do it multiple times!

            // Upper left
            gl_Position = projection * vec4(rot * vec2(-hsize.x, hsize.y) + center, 0.0, 1.0);
            uv = vec2(x0, y1);
            EmitVertex();

            // lower left
            gl_Position = projection * vec4(rot * vec2(-hsize.x, -hsize.y) + center, 0.0, 1.0);
            uv = vec2(x0, y0);
            EmitVertex();

            // upper right
            gl_Position = projection * vec4(rot * vec2(hsize.x, hsize.y) + center, 0.0, 1.0);
            uv = vec2(x1, y1);
            EmitVertex();

            // lower right
            gl_Position = projection * vec4(rot * vec2(hsize.x, -hsize.y) + center, 0.0, 1.0);
            uv = vec2(x1, y0);
            EmitVertex();

            // We are done with this triangle strip now
            EndPrimitive();
        }
    """

def getFragmentShader():
    return """
        #version 330

        uniform sampler2D sprite_texture;

        in vec2 uv;
        out vec4 fragColor;

        void main() {
            fragColor = texture(sprite_texture, uv);
            // texelFetch( ivec2(0,0), 0 );
        }
        """





def main():


    # instanciate app
    app    = PyrogenApp()
    window = app.window
    app.addProgram( "basicSprite",
                    vertexStr   = getVertexShader(),
                    geometryStr = getGeometryShader(),
                    fragmentStr = getFragmentShader() )

    app.prepareData()


    PREVTIME = 0
    timer = Timer()
    timer.start()

    while not app.window.is_closing:
        time, frame_time = timer.next_frame()

        print(round(1000*(time-PREVTIME),1))
        PREVTIME = time

        app.render(time, frame_time)
        window.swap_buffers()

    window.destroy()











def render(time: float, frametime: float):
    # We can also check if a key is in press state here
    if window.is_key_pressed(window.keys.SPACE):
        print("User is holding SPACE button")

def resize(width: int, height: int):
    print("Window was resized. buffer size is {} x {}".format(width, height))

def iconify(iconify: bool):
    """Window hide/minimize and restore"""
    print("Window was iconified:", iconify)

def key_event(key, action, modifiers):
    keys = window.keys

    # Key presses
    if action == keys.ACTION_PRESS:
        if key == keys.SPACE:
            print("SPACE key was pressed")

        # Using modifiers (shift and ctrl)

        if key == keys.Z and modifiers.shift:
            print("Shift + Z was pressed")

        if key == keys.Z and modifiers.ctrl:
            print("ctrl + Z was pressed")

    # Key releases
    elif action == keys.ACTION_RELEASE:
        if key == keys.SPACE:
            print("SPACE key was released")

    # Move the window around with AWSD
    if action == keys.ACTION_PRESS:
        if key == keys.A:
            window.position = window.position[0] - 10, window.position[1]
        if key == keys.D:
            window.position = window.position[0] + 10, window.position[1]
        if key == keys.W:
            window.position = window.position[0], window.position[1] - 10
        if key == keys.S:
            window.position = window.position[0], window.position[1] + 10

        # toggle cursor
        if key == keys.C:
            window.cursor = not window.cursor

        # Shuffle window tittle
        if key == keys.T:
            title = list(window.title)
            random.shuffle(title)
            window.title = ''.join(title)

        # Toggle mouse exclusivity
        if key == keys.M:
            window.mouse_exclusivity = not window.mouse_exclusivity

def mouse_position_event(x, y, dx, dy):
    print("Mouse position pos={} {} delta={} {}".format(x, y, dx, dy))

def mouse_drag_event(x, y, dx, dy):
    print("Mouse drag pos={} {} delta={} {}".format(x, y, dx, dy))

def mouse_scroll_event(x_offset, y_offset):
    print("mouse_scroll_event", x_offset, y_offset)

def mouse_press_event(x, y, button):
    print("Mouse button {} pressed at {}, {}".format(button, x, y))
    print("Mouse states:", window.mouse_states)

def mouse_release_event(x: int, y: int, button: int):
    print("Mouse button {} released at {}, {}".format(button, x, y))
    print("Mouse states:", window.mouse_states)

def unicode_char_entered(char):
    print("unicode_char_entered:", char)



if __name__ == '__main__':
    main()
