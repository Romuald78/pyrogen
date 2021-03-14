# TODO : move all these functions into the correct file
# e.g. ECS Gfx component  

import arcade
from random import *


def createSound(fileName):
    snd = arcade.load_sound(fileName)
    return snd


def drawText(params):
    # retrieve parameters
    x       = params["x"]
    y       = params["y"]
    message = params["message"]
    size    = 12                if "size"   not in params else params["size"  ]
    color   = (255,255,255,255) if "color"  not in params else params["color" ]
    alignH  = "center"          if "alignH" not in params else params["alignH"]    # left, center, right
    alignV  = "center"          if "alignV" not in params else params["alignV"]    # top, center, bottom
    angle   = 0                 if "angle"  not in params else params["angle" ]
    bold    = False             if "bold"   not in params else params["bold"  ]
    italic  = False             if "italic" not in params else params["italic"]
    # draw text according to configuration
    return arcade.draw_text(text=message,start_x=x,start_y=y,color=color,font_size=size,anchor_x=alignH,anchor_y=alignV,rotation=angle,bold=bold,italic=italic)

def createSimpleSprite(params):
    # retrieve parameters
    filePath    = params["filePath"  ]
    size        = None              if "size"        not in params else params["size"]
    position    = (0,0)             if "position"    not in params else params["position"]
    isMaxRatio  = False             if "isMaxRatio"  not in params else params["isMaxRatio"]
    filterColor = (255,255,255,255) if "filterColor" not in params else params["filterColor"]
    flipH       = False             if "flipH"       not in params else params["flipH"]
    flipV       = False             if "flipv"       not in params else params["flipV"]
    cropBox     = None              if "cropBox"     not in params else params["cropBox"]

    # Get crop zone
    if cropBox != None:
        refX, refY, w, h = cropBox
    else:
        refX, refY, w, h = 0,0,0,0

    # Create Sprite
    spr = arcade.Sprite(filePath,
                        image_x=refX,
                        image_y=refY,
                        image_width=w,
                        image_height=h,
                        flipped_horizontally=flipH,
                        flipped_vertically=flipV)

    # Apply color filter
    spr.color = filterColor

    # Set new scale if needed
    if size != None:
        if isMaxRatio:
            ratio = max(size[0] / spr.width, size[1] / spr.height)
        else:
            ratio = min(size[0]/spr.width, size[1]/spr.height)
        spr.scale = ratio

    # set position (init)
    spr.center_x = position[0]
    spr.center_y = position[1]

    # Return object
    return spr


# TODO : use the Texture Loader !!
def createParticleBurst(params):
    # retrieve parameters
    x0            = params["x0"           ]
    y0            = params["y0"           ]
    partSize      = params["partSize"     ]
    partScale     = params["partScale"    ]
    partSpeed     = params["partSpeed"    ]
    color         = params["color"        ]
    startAlpha    = params["startAlpha"   ]
    endAlpha      = params["endAlpha"     ]
    imagePath     = None if "imagePath" not in params else params["imagePath"]

    partInterval  = params["partInterval" ]
    totalDuration = params["totalDuration"]
    lifeTime      = params["lifeTime"]

    # create particle emitter
    e = arcade.Emitter(
            center_xy=(x0, y0),
            emit_controller=arcade.EmitterIntervalWithTime(partInterval, totalDuration),
            particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=imagePath if imagePath is not None else arcade.make_circle_texture(partSize, color),
            change_xy=arcade.rand_in_circle((0.0, 0.0), partSpeed),
            scale=partScale,
            lifetime=uniform(lifeTime*0.75, lifeTime*1.25),
            start_alpha=startAlpha,
            end_alpha=endAlpha,
        ),
    )
    # return result
    return e


# TODO : use the Texture Loader !!
def createParticleEmitter(params):
    # retrieve parameters
    x0            = params["x0"          ]
    y0            = params["y0"          ]
    partSize      = params["partSize"    ]
    partScale     = params["partScale"   ]
    partSpeed     = params["partSpeed"   ]
    color         = params["color"       ]
    startAlpha    = params["startAlpha"  ]
    endAlpha      = params["endAlpha"    ]

    partNB        = params["partNB"      ]
    maxLifeTime   = params["maxLifeTime" ]

    imagePath     = None  if "imagePath"  not in params else params["imagePath"]
    spriteBox     = None if "spriteBox" not in params else params["spriteBox"]
    spriteSelect  = None if "spriteSelect" not in params else params["spriteSelect"]
    flipH = False if "flipH" not in params else params["flipH"]
    flipV = False if "flipv" not in params else params["flipV"]

    # Prepare Texture
    if imagePath == None:
        tex = arcade.make_circle_texture(partSize, color)
    else:
        nbX, nbY, szW, szH = spriteBox
        x, y = spriteSelect
        tex = arcade.load_texture(imagePath, x * szW, y * szH, szW, szH,
                                  flipped_horizontally=flipH,
                                  flipped_vertically=flipV)
    # Create emitter
    e = arcade.Emitter(
        center_xy        = (x0, y0),
        emit_controller  = arcade.EmitMaintainCount(partNB),
        particle_factory = lambda emitter: arcade.FadeParticle(
            filename_or_texture = tex,
            change_xy           = arcade.rand_in_circle( (0.0,0.0), partSpeed),
            lifetime            = uniform(maxLifeTime/40,maxLifeTime),
            scale = partScale,
            start_alpha=startAlpha,
            end_alpha=endAlpha,
        ),
    )
    return e


