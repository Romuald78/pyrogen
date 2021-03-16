
## ============================================================
## IMPORTS
## ============================================================
from pyglet.media import StaticSource
from .component import Component
import pyglet.media as media



## ============================================================
## SFX COMPONENT
## ============================================================


class Music(Component):

    # --------------------------------------------
    # CONSTRUCTOR
    # --------------------------------------------
    def __init__(self, params, compName="SOUND"):
        super().__init__(compName)
        # Retrieve parameters
        sfxPath = params["sfxPath"]
        volume  = 1.0   if not "volume" in params else params["volume"]
        loop    = False if not "loop"   in params else params["loop"  ]
        # store file info
        self._music    = StaticSource(media.load(sfxPath))
        self._player   = media.Player()
        self._volume   = volume
        self._loop     = loop
        # Load music into player
        self._player.queue(self._music)
        self._player.volume = volume
        # Set the looping flag
        if self._loop:
            self._player.eos_action = 'loop'

    # method to get current type
    def getType(self):
        return Component.TYPE_MUSIC

    # Update
    def updateMusic(self, deltaTime):
        pass

    # LOOP
    def isLooping(self):
        return self._loop

    # VOLUME
    def setVolume(self, newVol):
        newVol = min(2.0,max(0.0,newVol))
        self._player.volume = newVol
    def getVolume(self):
        return self._player.volume
    def getVolumePercent(self):
        return (self.getVolume()/2.0)

    # PLAY
    def play(self):
        self._player.play()
    def pause(self):
        self._player.pause()
    def isPlaying(self):
        return self._player.playing
    def seek(self, time):
        self._player.seek(time)


