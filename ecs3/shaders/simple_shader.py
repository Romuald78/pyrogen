from .default_shader import Shader

class SimpleShader(Shader):

    def __init__(self, name="Shader v1"):
        super().__init__(name)

    def _getHeader(self):
        return """
            #version 330
            
            # ------------ FILE SYSTEM ----------------
            #define PAGE_SIZE_BITS (16)
            #define PAGE_NUM_BITS  (16)            
            #define OFFSET_MASK    ((1<<PAGE_SIZE_BITS)-1)
            #define PAGE_MASK      ( ((1<<PAGE_NUM_BITS )-1) << PAGE_SIZE_BITS )
            #define OVERHEAD       (1)

            # ------------ GFX TYPES ----------------
            #define TYPE_SPRITE    (1)
            #define TYPE_TEXT      (2)
            #define TYPE_RECTANGLE (3)
            #define TYPE_OVAL      (4)
            #define TYPE_FONT      (5)
            

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
            out vec4 inColor;
            out vec4 filterColor;
            out float gfxType;

            void processSprite(){
            
            }
            
            void processBox(){
            
            }

            void main() {

                // Get coord in the FS texture                
                ivec2 fsTexelCoords = fsCoords[0];
                
                //-------------------------------------------------------------------
                // Get GFX Header data
                //-------------------------------------------------------------------

                // Get filtering color
                filterColor = texelFetch( fsGpuChan, fsTexelCoords, 0 )/255.0;
                // Init IN and OUT colors with the same values
                inColor  = filterColor;
                fsTexelCoords.x  += 1;

                // Get position and size
                vec2 posFS  = texelFetch( fsGpuChan, fsTexelCoords, 0 ).xy;
                vec2 sizeFS = texelFetch( fsGpuChan, fsTexelCoords, 0 ).zw;
                fsTexelCoords.x += 1;
                
                // Get Scale / angle / visibility values
                float scaleFS    = texelFetch( fsGpuChan, fsTexelCoords, 0 ).x;
                float angleFS    = texelFetch( fsGpuChan, fsTexelCoords, 0 ).y;
                float fsVisOn    = texelFetch( fsGpuChan, fsTexelCoords, 0 ).z;
                float fsVisTotal = texelFetch( fsGpuChan, fsTexelCoords, 0 ).w;
                fsTexelCoords.x += 1;

                // Get Auto-Rotate / gfx type / Anchor X-Y
                float fsAutoRot  = texelFetch( fsGpuChan, fsTexelCoords, 0 ).x;
                float fsType     = texelFetch( fsGpuChan, fsTexelCoords, 0 ).y;
                vec2  fsAnchor   = texelFetch( fsGpuChan, fsTexelCoords, 0 ).zw;
                fsTexelCoords.x += 1;

                // Get Z-Index
                float fsZIndex = texelFetch( fsGpuChan, fsTexelCoords, 0 ).x;
                // Get FLIPX and FLIPY
                vec2 fsFlip = texelFetch( fsGpuChan, fsTexelCoords, 0 ).yz;
                // TODO : 1 remaining data for future use
                fsTexelCoords.x += 1;


                //-------------------------------------------------------------------
                // CHECK if this Gfx is visible or not
                //-------------------------------------------------------------------

                // Hide element if needed                
                if (fract(systemTime/fsVisTotal) > (fsVisOn/fsVisTotal)){
                    return;
                }
                
                // Set center and halfsize of sprite
                vec2 center = posFS;
                vec2 hsize  = scaleFS * sizeFS / 2.0;

                // Prepare data for geometry process
                vec2 pos0 = vec2(0.0);
                vec2 pos1 = vec2(0.0);
                


                //==========================================================
                // SPRITE
                //==========================================================
                if (fsType == TYPE_SPRITE){
                    // Get texture ID (for SPRITE)
                    float textIdFS = texelFetch( fsGpuChan, fsTexelCoords, 0 ).x;
                    fsTexelCoords.x += 1;
                    
                    // Get whole Atlas dimensions
                    vec2  texDim  = textureSize(atlasTextureChan,0);
                    // Get position and size of texture from the atlas
                    uvec4 texBox2 = texelFetch(atlasInfoChan, ivec2(int(textIdFS),0), 0 );
                    // Set values from unsigned to signed
                    vec4  texBox  = vec4(texBox2);
                    // Half pixel
                    vec2 halfPixel = vec2(0.0)/texDim;   // set 0.5 for half pixel feature
    
                    // Get texture coords
                    pos0   = (texBox.xy/texDim.xy);
                    pos1   = pos0 + (texBox.zw/texDim.xy);
                    pos0   = pos0 + halfPixel;
                    pos1   = pos1 - halfPixel;
                    pos0.y = 1.0-pos0.y;
                    pos1.y = 1.0-pos1.y;
                    // Flip texture if needed
                    float tmp;
                    if (fsFlip.x != 0.0){
                        tmp    = pos0.x;
                        pos0.x = pos1.x;
                        pos1.x = tmp;
                    }
                    if (fsFlip.y != 0.0){
                        tmp    = pos0.y;
                        pos0.y = pos1.y;
                        pos1.y = tmp;
                    }
                }
                
                //==========================================================
                // BASIC BOX SHAPE
                //==========================================================
                if (fsType == TYPE_RECTANGLE){
                    // get inside color
                    vec4 fsInClr = texelFetch( fsGpuChan, fsTexelCoords, 0 )/255.0;
                    fsTexelCoords.x += 1;    
                    inColor  = fsInClr;
                }


                //-------------------------------------------------------------------
                // CONVERT size and position according to current viewport
                //-------------------------------------------------------------------

                // Get center position and check if it is outside viewport
                vec4 glMin = projection * vec4(center-hsize, 0.0, 1.0);
                vec4 glMax = projection * vec4(center+hsize, 0.0, 1.0);
                if ( (abs(glMin.x) > 1.0 && abs(glMax.x) > 1.0)
                     || 
                     (abs(glMin.y) > 1.0 && abs(glMax.y) > 1.0)
                    ){
                    return;
                }

                // Convert the rotation to radians
                float angle = angleFS + (systemTime * fsAutoRot);
                angle = radians(angle);
                // Create a 2d rotation matrix
                mat2 rot = mat2(
                     cos(angle), sin(angle),
                    -sin(angle), cos(angle)
                );

                //-------------------------------------------------------------------
                // EMIT 4 vertices in order to display the Gfx element
                //-------------------------------------------------------------------

                // Type of GFX
                gfxType = fsType;
        
                // Emit a triangle strip creating a quad (4 vertices).
                // Here we need to make sure the rotation is applied before we position the sprite.
                // We just use hardcoded texture coordinates here. If an atlas is used we
                // can pass an additional vec4 for specific texture coordinates.
                // Each EmitVertex() emits values down the shader pipeline just like a single
                // run of a vertex shader, but in geomtry shaders we can do it multiple times!
                vec2 corner = vec2(0.0);
                // Anchor position is also affected by the scale value
                fsAnchor *= scaleFS;

                // Upper left
                corner = vec2(-hsize.x, -hsize.y) - fsAnchor;
                corner = rot * corner;
                corner = corner + center;
                gl_Position = projection * vec4(corner, 0.0, 1.0);
                uv = vec2(pos0.x, pos0.y);
                EmitVertex();

                // lower left
                corner = vec2(-hsize.x, hsize.y) - fsAnchor;
                corner = rot * corner;
                corner = corner + center;
                gl_Position = projection * vec4(corner, 0.0, 1.0);
                uv = vec2(pos0.x, pos1.y);
                EmitVertex();

                // upper right
                corner = vec2(hsize.x, -hsize.y) - fsAnchor;
                corner = rot * corner;
                corner = corner + center;
                gl_Position = projection * vec4(corner, 0.0, 1.0);
                uv = vec2(pos1.x, pos0.y);
                EmitVertex();

                // lower right
                corner = vec2(hsize.x, hsize.y) - fsAnchor;
                corner = rot * corner;
                corner = corner + center;
                gl_Position = projection * vec4(corner, 0.0, 1.0);
                uv = vec2(pos1.x, pos1.y);
                EmitVertex();

                // We are done with this triangle strip now
                EndPrimitive();
            }
        """

    def getFragment(self):
        return self._getHeader() + """
            uniform sampler2D  atlasTextureChan;

            in  vec2  uv;
            in  vec4  inColor;
            in  vec4  filterColor;
            in  float gfxType;
            out vec4  fragColor;

            vec3 RGB2YUV( vec3 rgb ){
                mat3 matrix = mat3(  0.299, -0.14713,  0.615  ,
                                     0.587, -0.28886, -0.51498,
                                     0.114,  0.436  , -0.10001 );
                return matrix * rgb;             
            }

            vec3 YUV2RGB( vec3 yuv ){
                mat3 matrix = mat3(  1.0   ,  1.0   , 1.0  ,
                                     0.0   , -0.3455, 1.779,
                                     1.4075, -0.7169, 0.0    );
                return matrix * yuv;             
            }

            void main() {

                // Get pixel color from the texture (only needed for Sprites
                vec4 color = texture(atlasTextureChan, uv);
                
                // Update color if basic shape
                if (gfxType == TYPE_RECTANGLE){
                    color = inColor;
                }
                
                // Modify color according to filter                
                vec3 pixel  = RGB2YUV(color.xyz);                
                vec3 filter = RGB2YUV(filterColor.xyz);

                // Lightness
                pixel.x = (pixel.x * filter.x);                
                // Color
                pixel.yz = (pixel.yz + filter.yz) * 0.5;

                // Transform to RGB back
                pixel = YUV2RGB(pixel);
                
                color.xyz = pixel;
                
                // Handle Transparency
                color.a  *= filterColor.a;

                // Set pixel color
                fragColor = color; 
            }
            """

