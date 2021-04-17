
"""
Custom usage: window creation and mapping callbacks functions at module level
"""
import random

from moderngl_window.timers.clock import Timer
from pyrogen.src.pyrogen.rgrwindow.MAIN.pyrogen_app import PyrogenApp

def getShaderHeader():
    return """
        #version 330

        #define ID_TEXT_DIFFUSE   0
        #define ID_TEXT_NORMAL    1
        #define ID_TEXT_SPECULAR  2
        
    """


def getVertexShader():
    return """
        // The per sprite input data
        in vec2 in_position;
        in vec2 in_size;
        in float in_rotation;
        in float in_tex_id;

        out vec2 size;
        out float rotation;
        out float tex_id;

        void main() {
            // We just pass the values unmodified to the geometry shader
            gl_Position = vec4(in_position, 0, 1);
            size = in_size;
            rotation = in_rotation;
            tex_id = in_tex_id;
        }
    """

def getGeometryShader():
    return """
        // We are taking single points form the vertex shader
        // and emitting 4 new vertices creating a quad/sprites
        layout (points) in;
        layout (triangle_strip, max_vertices = 4) out;

        uniform mat4       projection;
        uniform sampler2D  atlasDataID[3];
        uniform usampler2D atlasInfoID;

        // Since geometry shader can take multiple values from a vertex
        // shader we need to define the inputs from it as arrays.
        // In our instance we just take single values (points)
        in vec2  size[];
        in float rotation[];
        in float tex_id[];

        out vec2 uv;

        void main() {
            // Get texture dimensions
            vec2  texDim  = textureSize(atlasDataID[ID_TEXT_DIFFUSE],0);
            uvec4 texBox2 = texelFetch( atlasInfoID, ivec2(int(tex_id[0]),0), 0 );
            vec4  texBox  = vec4(texBox2);
    
            // Half pixel
            vec2 halfPixel = vec2(0.0)/texDim;
            
            // Get texture coords
            vec2 pos0 = (texBox.xy/texDim.xy);
            vec2 pos1 = pos0 + (texBox.zw/texDim.xy);
            pos0   = pos0 + halfPixel;
            pos1   = pos1 - halfPixel;
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
        uniform sampler2D  atlasDataID[3];
        uniform usampler2D atlasInfoID;

        in vec2 uv;
        out vec4 fragColor;

        void main() {

            vec4 color = texture(atlasDataID[ID_TEXT_DIFFUSE], uv);
            fragColor = color; 
        
        }
        """





def main():


    # instanciate app
    app    = PyrogenApp()
    window = app.window
    app.addProgram( "basicSprite",
                    vertexStr   = getShaderHeader()+getVertexShader(),
                    geometryStr = getShaderHeader()+getGeometryShader(),
                    fragmentStr = getShaderHeader()+getFragmentShader() )

    app.prepareData()

    for field in app.context.info:
        print(f"{field} : {app.context.info[field]}")

    PREVTIME = 0
    timer = Timer()
    timer.start()

    while not app.window.is_closing:
        time, frame_time = timer.next_frame()

        #print(f"frameTime={round(1000*(time-PREVTIME),1)}")
        PREVTIME = time

        app.render(time, frame_time)
        window.swap_buffers()

    window.destroy()






if __name__ == '__main__':
    main()
