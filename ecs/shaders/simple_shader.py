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
            uniform sampler2D   fsGpuID;
                
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
            uniform sampler2D   atlasTextureID;
            uniform sampler2D   fsGpuID;
            uniform usampler2D  atlasInfoID;

            // Since geometry shader can take multiple values from a vertex
            // shader we need to define the inputs from it as arrays.
            // In our instance we just take single values (points)
            in ivec2 fsCoords[];

            out vec2 uv;

            void main() {

                // Get coord in the FS texture                
                ivec2 fsTexelCoords = fsCoords[0];
                
                // Get filtering color
                vec4 colorFS = texelFetch( fsGpuID, fsTexelCoords, 0 );
                fsTexelCoords.x  += 1;

                // Get position and size
                vec2 posFS  = texelFetch( fsGpuID, fsTexelCoords, 0 ).xy;
                vec2 sizeFS = texelFetch( fsGpuID, fsTexelCoords, 0 ).zw;
                fsTexelCoords.x += 1;
                
                // Get angle and texture ID
                float angleFS  = texelFetch( fsGpuID, fsTexelCoords, 0 ).x;
                float textIdFS = texelFetch( fsGpuID, fsTexelCoords, 0 ).y;

                // Set center and halfsize of sprite
                vec2 center = posFS;
                vec2 hsize  = sizeFS / 2.0;

                // Get whole Atlas dimensions
                vec2  texDim  = textureSize(atlasTextureID,0);
                // Get position and size of texture from the atlas
                uvec4 texBox2 = texelFetch(atlasInfoID, ivec2(int(textIdFS),0), 0 );
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
                float angle = radians(angleFS);
                // Create a 2d rotation matrix
                mat2 rot = mat2(
                    cos(angle), sin(angle),
                    -sin(angle), cos(angle)
                );

                // Get center position and check if it is outside viewport
                vec4 glCenter = projection * vec4(center, 0.0, 1.0);
                if (abs(glCenter.x) > 1.05 || abs(glCenter.y) > 1.05){
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
            uniform sampler2D  atlasTextureID;

            in vec2 uv;
            out vec4 fragColor;

            void main() {

                vec4 color = texture(atlasTextureID, uv);
                fragColor = color; 

            }
            """

