
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
            
            // Half pixel
            vec2 halfPixel = vec2(0.0)/texDim;
            
            // Get texture coords
            vec2 pos0 = (atlas_pos[0].xy/texDim.xy);
            vec2 pos1 = pos0 + (atlas_pos[0].zw/texDim.xy);
            pos0 = pos0 + halfPixel;
            pos1 = pos1 - halfPixel;
            pos0.y = 1.0-pos0.y;
            pos1.y = 1.0-pos1.y;

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
            uv = vec2(pos0.x, pos1.y);
            EmitVertex();

            // lower left
            gl_Position = projection * vec4(rot * vec2(-hsize.x, -hsize.y) + center, 0.0, 1.0);
            uv = vec2(pos0.x, pos0.y);
            EmitVertex();

            // upper right
            gl_Position = projection * vec4(rot * vec2(hsize.x, hsize.y) + center, 0.0, 1.0);
            uv = vec2(pos1.x, pos1.y);
            EmitVertex();

            // lower right
            gl_Position = projection * vec4(rot * vec2(hsize.x, -hsize.y) + center, 0.0, 1.0);
            uv = vec2(pos1.x, pos0.y);
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

    for field in app.context.info:
        print(f"{field} : {app.context.info[field]}")

    PREVTIME = 0
    timer = Timer()
    timer.start()

    while not app.window.is_closing:
        time, frame_time = timer.next_frame()

        print(f"frameTime={round(1000*(time-PREVTIME),1)}")
        PREVTIME = time

        app.render(time, frame_time)
        window.swap_buffers()

    window.destroy()






if __name__ == '__main__':
    main()
