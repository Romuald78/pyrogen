from .default_shader import Shader

class SimpleShader(Shader):

    def __init__(self, name="Shader v1"):
        super().__init__(name)

    def _getHeader(self):
        return """
            #version 330
            
            # ------------ FILE SYSTEM ----------------
            #define PAGE_SIZE_BITS (18)
            #define PAGE_NUM_BITS  (14)            
            #define OFFSET_MASK    ((1<<PAGE_SIZE_BITS)-1)
            #define PAGE_MASK      ( ((1<<PAGE_NUM_BITS )-1) << PAGE_SIZE_BITS )
            #define OVERHEAD       (1)

        """

    def getVertex(self):
        return self._getHeader() + """
            // The per sprite input data
            in int blockID;
            
            // Uniforms
            uniform sampler2D   fsGpuChan;
                
            // Output                
            out ivec2 fsCoords;

            void main() {
            
                // Extract X,Y texture position from offset
                int fsOffset = (blockID & OFFSET_MASK) >> 2;
                int fsPage   = (blockID & PAGE_MASK  ) >> PAGE_SIZE_BITS;
                fsOffset    += OVERHEAD;
                fsCoords     = ivec2(fsOffset,fsPage);
                
            }
        """

    def getGeometry(self):
        return self._getHeader() + """
            // We are taking single points form the vertex shader
            // and emitting 4 new vertices creating a quad/sprites
            layout (points) in;
            layout (triangle_strip, max_vertices = 4) out;

            uniform mat4        projection;
            uniform sampler2D   atlasTextureChan;
            uniform sampler2D   fsGpuChan;
            uniform usampler2D  atlasInfoChan;
            uniform float       systemTime;

            // Since geometry shader can take multiple values from a vertex
            // shader we need to define the inputs from it as arrays.
            // In our instance we just take single values (points)
            in ivec2 fsCoords[];

            out vec2 uv;

            void main() {

                // Get coord in the FS texture                
                ivec2 fsTexelCoords = fsCoords[0];
                
                // Get filtering color
                vec4 colorFS = texelFetch( fsGpuChan, fsTexelCoords, 0 );
                fsTexelCoords.x  += 1;

                // Get position and size
                vec2 posFS  = texelFetch( fsGpuChan, fsTexelCoords, 0 ).xy;
                vec2 sizeFS = texelFetch( fsGpuChan, fsTexelCoords, 0 ).zw;
                fsTexelCoords.x += 1;
                
                
                // TODO handle scale (here .x value)
                // Get angle and visibility values
                float angleFS    = texelFetch( fsGpuChan, fsTexelCoords, 0 ).y;
                float fsVisOn    = texelFetch( fsGpuChan, fsTexelCoords, 0 ).z;
                float fsVisTotal = texelFetch( fsGpuChan, fsTexelCoords, 0 ).w;
                fsTexelCoords.x += 1;

                // Hide element if needed                
                if (fract(systemTime/fsVisTotal) > (fsVisOn/fsVisTotal)){
                    return;
                }
                
                // Get autorotate
                float fsAutoRot = texelFetch( fsGpuChan, fsTexelCoords, 0 ).x;
                fsTexelCoords.x += 1;

                // TODO : retireve the Gfx element type in order to know what to do with data

                // Get texture ID (for SPRITE)
                float textIdFS = texelFetch( fsGpuChan, fsTexelCoords, 0 ).x;
                fsTexelCoords.x += 1;

                // Set center and halfsize of sprite
                vec2 center = posFS;
                vec2 hsize  = sizeFS / 2.0;

                // Get whole Atlas dimensions
                vec2  texDim  = textureSize(atlasTextureChan,0);
                // Get position and size of texture from the atlas
                uvec4 texBox2 = texelFetch(atlasInfoChan, ivec2(int(textIdFS),0), 0 );
                // Set values from unsigned to signed
                vec4  texBox  = vec4(texBox2);

                // Half pixel
                vec2 halfPixel = vec2(0.0)/texDim;   // set 0.5 for half pixel feature

                // Get texture coords
                vec2 pos0 = (texBox.xy/texDim.xy);
                vec2 pos1 = pos0 + (texBox.zw/texDim.xy);
                pos0      = pos0 + halfPixel;
                pos1      = pos1 - halfPixel;
                pos0.y    = 1.0-pos0.y;
                pos1.y    = 1.0-pos1.y;

                // Convert the rotation to radians
                float angle = angleFS + (systemTime * fsAutoRot);
                angle = radians(angle);
                // Create a 2d rotation matrix
                mat2 rot = mat2(
                     cos(angle), sin(angle),
                    -sin(angle), cos(angle)
                );

                // Get center position and check if it is outside viewport
                vec4 glMin = projection * vec4(center-hsize, 0.0, 1.0);
                vec4 glMax = projection * vec4(center+hsize, 0.0, 1.0);
                if ( (abs(glMin.x) > 1.0 && abs(glMax.x) > 1.0)
                     || 
                     (abs(glMin.y) > 1.0 && abs(glMax.y) > 1.0)
                    ){
                    return;
                }

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

    def getFragment(self):
        return self._getHeader() + """
            uniform sampler2D  atlasTextureChan;

            in vec2 uv;
            out vec4 fragColor;

            void main() {

                vec4 color = texture(atlasTextureChan, uv);
                fragColor = color; 

            }
            """

