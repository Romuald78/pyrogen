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
            out vec4 filterColor;

            void main() {

                // Get coord in the FS texture                
                ivec2 fsTexelCoords = fsCoords[0];
                
                // Get filtering color
                filterColor = texelFetch( fsGpuChan, fsTexelCoords, 0 )/255.0;
                fsTexelCoords.x  += 1;

                // Get position and size
                vec2 posFS  = texelFetch( fsGpuChan, fsTexelCoords, 0 ).xy;
                vec2 sizeFS = texelFetch( fsGpuChan, fsTexelCoords, 0 ).zw;
                fsTexelCoords.x += 1;
                
                
                // Get scale (here .x value)
                float scaleFS = texelFetch( fsGpuChan, fsTexelCoords, 0 ).x;
                
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

                // TODO : retrieve the Gfx element type in order to know what to do with data

                // Get texture ID (for SPRITE)
                float textIdFS = texelFetch( fsGpuChan, fsTexelCoords, 0 ).x;
                fsTexelCoords.x += 1;

                // Set center and halfsize of sprite
                vec2 center = posFS;
                vec2 hsize  = scaleFS * sizeFS / 2.0;

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

            in  vec2 uv;
            in  vec4 filterColor;
            out vec4 fragColor;

            float max3(vec3 v){
                return max(max(v.x, v.y), v.z);
            }
            float min3(vec3 v){
                return min(min(v.x, v.y), v.z);
            }

            vec3 RGB2HSL(vec3 rgb){
                float maxi  = max3(rgb);
                float mini  = min3(rgb);
                float delta = maxi - mini;            
                
                float L = (maxi + mini) * 0.5;
                float S = 0.0;
                float H = 0.0;
                if (delta != 0.0){
                    S = delta/(1-abs(2*L-1));
                    if (maxi == rgb.r){
                        float tmp = (rgb.g-rgb.b) / delta;
                        tmp = fract(tmp/6.0) * 6.0;
                        H = 60 * tmp;
                    }
                    else if(maxi == rgb.g){
                        float tmp = (rgb.b-rgb.r) / delta;
                        tmp = tmp + 2.0;
                        H = 60 * tmp;
                    }
                    else if(maxi == rgb.b){
                        float tmp = (rgb.r-rgb.g) / delta;
                        tmp = tmp + 4.0;
                        H = 60 * tmp;
                    }
                }
                                
                return vec3(H,S,L);
            }
            
            vec3 HSL2RGB(vec3 hsl){
                float H = hsl.x;
                float S = hsl.y;
                float L = hsl.z;
                float C = (1-abs(2*L-1))*S;
                float tmp = H/60;
                tmp = fract(tmp/2.0) * 2.0;
                float X = (1-abs(tmp-1))*C;
                float m = L-(C/2.0);
                vec3 rgb = vec3(0.0);
                if(H>=0.0 && H<60.0){
                    rgb.r = C;
                    rgb.g = X;
                }
                else if (H<120.0){
                    rgb.r = X;
                    rgb.g = X;                
                }
                else if (H<180.0){
                    rgb.g = C;
                    rgb.b = X;
                }
                else if (H<240.0){
                    rgb.g = X;
                    rgb.b = C;
                }
                else if (H<300.0){
                    rgb.r = X;
                    rgb.b = C;
                }
                else if (H<360.0){
                    rgb.r = C;
                    rgb.b = X;                
                }
                rgb += m;
                return rgb;
            }

            vec3 RGB2YUV(vec3 rgb){
                mat3 matrix = mat3( 0.299,  0.587,  0.114,
                                   -0.14714, -0.28886,  0.436,
                                    0.615, -0.51499, -0.10001);
                vec3 yuv = matrix * rgb;
                return yuv;
            }

            vec3 YUV2RGB(vec3 yuv){
                mat3 matrix = mat3( 1.0,  0.0  ,  1.13983,
                                    1.0, -0.39465, -0.58060,
                                    1.0,  2.03211,  0.0   );
                vec3 rgb = matrix * yuv;
                return rgb;
            }


            void main() {

                // Get pixel color from the texture
                vec4 color = texture(atlasTextureChan, uv);

                // Modify color according to filter                
                vec3 pixel  = RGB2HSL(color.xyz);                
                vec3 filter = RGB2HSL(filterColor.xyz);
                // Lightness
                pixel.z = (pixel.z * filter.z);                
                // Hue
                pixel.x = filter.x;
                // Saturation
                pixel.y = max(pixel.y, filter.y);
                // Transform to RGB back
                pixel = HSL2RGB(pixel);
                
                color.xyz = pixel;
                
                // Handle Transparency
                color.a  *= filterColor.a;
                 
                // Set pixel color
                fragColor = color; 
            }
            """

