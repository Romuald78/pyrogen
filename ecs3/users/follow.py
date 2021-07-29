from ..components.script import Script


class GfxFollowGfx(Script):

    def __init__(self, gfxTarget, gfxFollower, offset=(0,0), setAngle=False, offAngle=0, priority=0, name="GfxFollowGfx"):
        super().__init__(priority, name)
        self._target   = gfxTarget
        self._follower = gfxFollower
        self._setAngle = setAngle
        self._offset   = offset
        self._offAngle = offAngle

    def updateScript(self, deltaTime, systemTime):
        # Take target position
        x,y = self._target.getPosition()
        # Add offset
        x += self._offset[0]
        y += self._offset[1]
        # Set follower position
        self._follower.setPosition(x, y)
        # Check if we must set the angle too
        if self._setAngle:
            # Get target angle
            angle = self._target.getAngle()
            # add angle offset
            angle += self._offAngle
            # Set follower angle
            self._follower.setAngle(angle)
