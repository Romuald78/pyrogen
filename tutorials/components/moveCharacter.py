from ...ecs.components.script import Script


class KeyboardMoveGfx(Script):

    def __init__(self, gfx, keyL, keyR, keyU, keyD, speed):
        super().__init__()
        self._gfx   = gfx
        self._keyL  = keyL
        self._keyR  = keyR
        self._keyU  = keyU
        self._keyD  = keyD
        self._speed = speed

    def updateScript(self, scriptName, deltaTime):
        dx = 0
        dy = 0
        speed = self._speed*60*deltaTime
        if self._keyL.isPressed():
            dx -= speed
        if self._keyR.isPressed():
            dx += speed
        if self._keyU.isPressed():
            dy += speed
        if self._keyD.isPressed():
            dy -= speed
        self._gfx.move(dx, dy)

