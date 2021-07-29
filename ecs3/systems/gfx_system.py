from array import array


class GfxSystem():

    _glData = None

    @staticmethod
    def setOpenGlData(glData):
        GfxSystem._glData= glData

    # Recursive Dichotomy method to add the component at the correct place (sorted by Z)
    def _addComponent(self, ref, left, right):
        # We reached the end of the dichotomy process
        if right - left == -1:
            # We went too far, take the "left" index
            right = left
        # Compute middle index
        mid = (left + right) // 2
        # Get index
        curZ = self._compByRef[mid].getZIndex()
        newZ = ref.getZIndex()
        if left == right:
            if newZ > curZ:
                left += 1
            # add the component add the left position
            self._compByRef.insert(left, ref)
            return
        else:
            if newZ == curZ:
                # Insert at the mid index
                self._compByRef.insert(mid, ref)
                return
            elif newZ > curZ:
                # move left border
                left = mid+1
                self._addComponent(ref, left, right)
            else:
                # move left border
                right = mid-1
                self._addComponent(ref, left, right)

    def _genVertexBuffer(self):
        for c in self._compByRef:
            yield c.getBlockID()

    def __init__(self):
        # Store components (by Ref, sorted by Z Index)
        self._compByRef  = []

    def addComponent(self, ref):
        #print(f"Adding {ref.getName()} @ Z={ref.getZIndex()} ...")
        if ref in self._compByRef:
            raise RuntimeError(f"[ERROR] cannot add the Gfx {ref} twice !")
        if len(self._compByRef) == 0:
            self._compByRef.append(ref)
        else:
            self._addComponent(ref, 0, len(self._compByRef)-1)

    def removeComponent(self, ref):
        if ref not in self._compByRef:
            raise RuntimeError(f"[ERROR] cannot remove the Gfx {ref} !")
        self._compByRef.remove(ref)

    def notifyChangeZ(self, ref):
        # Remove the component and add it once again
        self.removeComponent(ref)
        self.addComponent(ref)

    def update(self, deltaTime, systemTime):
        # Update all the gfx components
        for c in self._compByRef:
            c.update(deltaTime)
        # Update the GPU file system
        GfxSystem._glData.update(deltaTime, systemTime)

    def render(self):
        vb = array("l", self._genVertexBuffer())
        GfxSystem._glData.updateVertexBuffer( vb, len(self._compByRef) )
        GfxSystem._glData.render()
