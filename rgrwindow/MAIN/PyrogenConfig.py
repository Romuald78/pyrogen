"""
Quick and dirty example showing how sprites can be rendered using a geometry shader.
We also show simple scrolling with projection matrix.

The goal is to redice the sprite data on the client as much as possible.
We can define a sprite by its postion, size and rotation. This can be
expressed in 5 32 bit floats. This also opens up for individually rotating
each sprite in the shader itself. This technique can be extended with more
sprite parameters.

Other optimizations that can be done:
* Cull sprites outside the viewport in geo shader
"""
import math
import moderngl_window
import moderngl

from pathlib import Path

from pyrr import Matrix44
from array import array


# EVENT management
# TODO
# https://github.com/moderngl/moderngl-window/blob/master/examples/custom_config_functions.py
# https://github.com/moderngl/moderngl-window/blob/master/examples/window_events.py
# TODO


class PyrogenApp(moderngl_window.WindowConfig):

    # FEATURE : self.wnd.keys    for all the keyboard definitions




    resource_dir = Path(__file__).parent.resolve()


    def keyPressed(self, symbol, modifiers):
        print(symbol, modifiers)


    def setupCallbacks(self):
        self.wnd.on_key_press = self.keyPressed


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        print(kwargs)

        # PYGLET Window instance ?
        self.wnd.use()
        self.wnd.clear()

        self.wnd._window.on_key_press = self.keyPressed


        # TODO
        # CULLING (removingvertex emit if not useful to be displayed)
        # TODO

        self.ball_texture = self.load_texture_2d("ball.png")

        # Sprite shader using geometry shader
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            // The per sprite input data
            in vec2 in_position;
            in vec2 in_size;
            in float in_rotation;

            out vec2 size;
            out float rotation;

            void main() {
                // We just pass the values unmodified to the geometry shader
                gl_Position = vec4(in_position, 0, 1);
                size = in_size;
                rotation = in_rotation;
            }
            """,
            geometry_shader="""
            #version 330

            // We are taking single points form the vertex shader
            // and emitting 4 new vertices creating a quad/sprites
            layout (points) in;
            layout (triangle_strip, max_vertices = 4) out;

            uniform mat4 projection;

            // Since geometry shader can take multiple values from a vertex
            // shader we need to define the inputs from it as arrays.
            // In our instance we just take single values (points)
            in vec2 size[];
            in float rotation[];
            out vec2 uv;

            void main() {
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
                uv = vec2(0, 1);
                EmitVertex();

                // lower left
                gl_Position = projection * vec4(rot * vec2(-hsize.x, -hsize.y) + center, 0.0, 1.0);
                uv = vec2(0, 0);
                EmitVertex();

                // upper right
                gl_Position = projection * vec4(rot * vec2(hsize.x, hsize.y) + center, 0.0, 1.0);
                uv = vec2(1, 1);
                EmitVertex();

                // lower right
                gl_Position = projection * vec4(rot * vec2(hsize.x, -hsize.y) + center, 0.0, 1.0);
                uv = vec2(1, 0);
                EmitVertex();

                // We are done with this triangle strip now
                EndPrimitive();
            }

            """,
            fragment_shader="""
            #version 330

            uniform sampler2D sprite_texture;

            in vec2 uv;
            out vec4 fragColor;

            void main() {
                fragColor = texture(sprite_texture, uv);
                // texelFetch( ivec2(0,0), 0 );
            }
            """,
        )

        self.sprite_data_size = 5 * 4  # 5 32 bit floats
        self.sprite_data = self.ctx.buffer(reserve=1000 * self.sprite_data_size)  # Capacity for 1000 sprites
        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (self.sprite_data, "2f 2f 1f", "in_position", "in_size", "in_rotation"),
            ]
        )

        w, h = self.ctx.screen.size
        self.projection = Matrix44.orthogonal_projection(0, w, h, 0, 1, 0, dtype="f4")

    #    def resize(self, w, h):
    #        self.ctx.screen.viewport = (0, 0, w // 2, h // 2)



    def render(self, time, frame_time):

        self.ctx.clear()

        self.ctx.enable(moderngl.BLEND)
        #        self.ctx.blend_equation  = moderngl.FUNC_SUBTRACT
        #        self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)

        num_sprites = 16
        # We'll just generate some sprite data on the fly here.
        # This should only be necessary every time the sprite data changes (in a prefect wold)

        # Grab the size of the screen or current render target
        width, height = self.ctx.fbo.size

        # We just create a generator function instead of
        def gen_sprites(time):
            rot_step = math.pi * 2 / num_sprites
            for i in range(num_sprites):
                # Position
                yield width / 2 + math.sin(time + rot_step * i) * 150
                yield height / 2 + math.cos(time + rot_step * i) * 150
                # size
                yield 100
                yield 100
                # rotation
                yield math.sin(time + i) * 200

        # struct/array python
        # numpy ?
        # " cpu to GPU"
        self.sprite_data.write(array("f", gen_sprites(time)))

        # calculate some offset. We truncate to intergers here.
        # This depends what "look" you want for your game.
        scroll_x, scroll_y = int(math.sin(time) * 100), int(math.cos(time) * 100)

        # Let's also modify the viewport to scroll the entire screen.
        self.projection = Matrix44.orthogonal_projection(
            scroll_x,  # left
            width + scroll_x,  # right
            height + scroll_y,  # top
            scroll_y,  # bottom
            1,  # near
            -1,  # far
            dtype="f4",  # ensure we create 32 bit value (64 bit is default)
        )

        # CPU to GPU (uniform data)
        self.program["projection"].write(self.projection)
        self.program["sprite_texture"] = 0

        # uniform buffer objects (for lights ?)
        # lights could be in a texture buffer and we could update this texture buffer ?

        # texture channels (up to 16 ?)
        # texture atlas (
        # texture arrays (several layers , same coords)
        # texture that stores information on atlas positions
        # warning take care of borders in case of 2d atlas !! :
        # Use atlas from pyglet (algo to make fits the better)

        self.ball_texture.use(0)
        # self.atlas.use(0) instead
        # max dim 16k*16k
        # see ctx.info for info

        # Since we have overallocated the buffer (room for 1000 sprites) we
        # need to specify how many we actually want to render passing number of vertices.
        # Also the mode needs to be the same as the geometry shader input type (points!)
        self.vao.render(mode=moderngl.POINTS, vertices=num_sprites)

        if self.ctx.error != "GL_NO_ERROR":
            print(self.ctx.error)





# Perfs :
# time.perf_counter()
#
# distinct PROGRAM with "Transform" shader to update buffers (particle info , size, pos, etc...)
# can't read and write from/to same buffer
# geometry will handle the reap state of each particle
# example available in moderngl


# give aSCII message to opengl + texture coords (text rendering)




if __name__ == "__main__":
    PyrogenApp.run()
