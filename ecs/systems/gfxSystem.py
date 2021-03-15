# FEATURE : Merge gfx classes
# put a single Sprite in a 1-size-spriteList
# to be more generic ? We would only have GfxSpriteList as gfx components
# that would be easier to handle here. let's see

# FEATURE : when adding a component, check first and last Z Index entries
# before calling the dichotomy process

## ============================================================
## IMPORTS
## ============================================================
from ..components.gfx import Gfx
import sys



## ============================================================
## GFX MANAGER
## ============================================================

class GfxSystem():

    ## -------------------------------------
    ## Constructor
    ## -------------------------------------
    def __init__(self):
        # List of visible Gfx components (sorted by Z, decreasing order)
        self._visibleComps = []
        # List of hidden Gfx components (sorted by Z, decreasing order)
        self._hiddenComps = []


    ## -------------------------------------
    ## Type checking
    ## -------------------------------------
    def __checkType(self, ref):
        if not isinstance(ref, Gfx):
            raise ValueError(f"[ERR] check gfx : bad object type. It should be Gfx !\n{ref}")

    ## -------------------------------------
    ## List management
    ## -------------------------------------
    def _getNextIndex(self, myList, zValue):
        # dichotomy search of the index of a zValue in a descending order sorted list
        # if the value itself is not found, return the index of the value below zValue
        minIdx   = 0
        maxIdx   = len(myList)-1
        midIdx = (minIdx + maxIdx) // 2
        # return if empty list
        if maxIdx == -1:
            return 0
        while maxIdx-minIdx > 0:
            # Compute middle index and value
            midValue = myList[midIdx].getZIndex()
            # check which next range will be
            if midValue > zValue:
                minIdx = midIdx+1
            elif midValue < zValue:
                maxIdx = midIdx-1
            else:
                minIdx = midIdx
                maxIdx = midIdx
            # compute new mid
            midIdx = (minIdx + maxIdx) // 2
        # check if we have to choose min or max index
        res = midIdx
        if res < 0:
            res = 0
        if myList[midIdx].getZIndex() > zValue:
            res += 1
        return res

    def _insertComp(self, myList, cmpRef):
        # Get Z value
        z = cmpRef.getZIndex()
        nextIndex = self._getNextIndex(myList, z)
        myList = myList[:nextIndex] + [cmpRef,] + myList[nextIndex:]
        return myList

    def _addComp(self, cmpRef):
        # Get visibility value
        isVis = cmpRef.isVisible()
        # choose list to insert into
        if isVis:
            self._visibleComps = self._insertComp(self._visibleComps, cmpRef)
        else:
            self._hiddenComps  = self._insertComp(self._hiddenComps, cmpRef)

    def _findCompIndex(self,myList, compRef):
        for i in range(len(myList)):
            if myList[i] == compRef:
                return i
        raise ValueError(f"[ERR] gfxSystem : find comp index : the request comp {compRef} is not present in the list")


    ## -------------------------------------
    ## DEBUG
    ## -------------------------------------
    def getMemoryInfo(self):
        res = {
            "gfxVis": f"{sys.getsizeof(self._visibleComps)}/{len(self._visibleComps)}",
            "gfxHid" :f"{sys.getsizeof(self._hiddenComps)}/{len(self._hiddenComps)}"
        }
        return res


    ## -------------------------------------
    ## Register methods
    ## -------------------------------------
    def registerGfx(self, cmpRef):
        # check type
        self.__checkType(cmpRef)
        # Check presence of comp in both lists
        if cmpRef in self._visibleComps or cmpRef in self._hiddenComps:
            raise ValueError("[ERR] GfxSystem, addComp : ref is already registered in lists !")
        # Add component into lists
        self._addComp(cmpRef)

    def removeGfx(self, cmpRef):
        # check if component is in a list and remove from it
        if cmpRef in self._visibleComps:
            self._visibleComps.remove(cmpRef)
        elif cmpRef in self._hiddenComps:
            self._hiddenComps.remove(cmpRef)
        else:
            raise ValueError("[ERR] removeGfx : component is not found in any list !")
        # Unregister sprite from arcade environment
        cmpRef.kill()



    ## -------------------------------------
    ## Main process methods
    ## -------------------------------------
    def updateAllGfx(self, deltaTime, isOnPause):
        # init list of gfx elements to remove
        ref2Remove = []
        # browse every gfx element in the visible list (not the hidden list) and update
        for cmpRef in self._visibleComps:
            ref   = cmpRef.getGfx()
            type  = cmpRef.getType()
            # Check pause behavior (no update if paused)
            if cmpRef.isEnabledOnPause() or (not isOnPause):
                # Animated sprites or spritelists
                if (type & Gfx.ANIMATED) == Gfx.ANIMATED:
                    # update animated sprites
                    ref.update_animation(deltaTime)
                # Particle emitters
                elif (type & Gfx.SIMPLE) != Gfx.SIMPLE:
                    # update particle emitters (normal or bursts)
                    ref.update()
                    # Remove burst emitters if finished
                    if type == Gfx.TYPE_BURST:
                        if cmpRef.isFinished():
                            ref2Remove.append(cmpRef)
        # Send notification to remove useless gfx components
        for comp in ref2Remove:
            comp.getEntity().removeComponent(comp)

    def drawAllGfx(self):
        # FEATURE : handle drawList in a clever way instead of drawing each component 1-by-1
        for cmpRef in self._visibleComps:
            ref = cmpRef.getGfx()
            ref.draw()


    ## -------------------------------------
    ## COMPONENT NOTIFICATIONS
    ## -------------------------------------
    def notifyUpdateZIndex(self, compRef):
        # check visibility to select the list
        isVis = compRef.isVisible()
        if isVis :
            myList = self._visibleComps
        else:
            myList = self._hiddenComps
        # find comp in the visible list and get the index
        idx = self._findCompIndex(myList, compRef)
        # get previous value
        prevVal = 1000000000
        if idx > 0:
            prevVal = myList[idx-1].getZIndex()
        # get next value
        nextVal = -1000000000
        if idx < len(myList)-1:
            nextVal = myList[idx+1].getZIndex()
        # check if we have to move it
        curVal = compRef.getZIndex()
        if not(prevVal>=curVal and curVal>=nextVal):
            # we have to move it. First remove it from the list
            # then reinsert it using existing method
            # remove ref from visible
            myList.remove(compRef)
            # add ref into correct list
            self._addComp(compRef)

    def notifyUpdateVisible(self, compRef):
        # get visibility field
        newVis = compRef.isVisible()
        # Set to visible
        if newVis:
            if compRef in self._hiddenComps:
                # remove ref from hidden
                self._hiddenComps.remove(compRef)
                # add ref into correct list
                self._addComp(compRef)
        # set to hidden
        else:
            if compRef in self._visibleComps:
                # remove ref from visible
                self._visibleComps.remove(compRef)
                # add ref into correct list
                self._addComp(compRef)
