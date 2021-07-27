

class BaseSystem():

    # Recursive Dichotomy method to add the component at the correct place (sorted by priority)
    def _addComponent(self, ref, left, right):
        # Compute middle index
        mid = (left + right) // 2
        # Get index
        curP = self._compByRef[mid].getPriority()
        newP = ref.getPriority()
        # We reached the end of the dichotomy process
        if left == right:
            if newP > curP:
                left += 1
            # add the component add the left position
            self._compByRef.insert(left, ref)
            return
        else:
            if newP == curP:
                # Insert at the mid index
                self._compByRef.insert(mid, ref)
                return
            elif newP > curP:
                # move left border
                left += 1
                self._addComponent(ref, left, right)
            else:
                # move left border
                right -= 1
                self._addComponent(ref, left, right)


    def __init__(self):
        # Store components (by Ref, sorted by Priority)
        self._compByRef  = []

    def addComponent(self, ref):
        if ref in self._compByRef:
            raise RuntimeError(f"[ERROR] cannot add the component {ref} twice in system {self} !")
        if len(self._compByRef) == 0:
            self._compByRef.append(ref)
        else:
            self._addComponent(ref, 0, len(self._compByRef)-1)

    def removeComponent(self, ref):
        if ref not in self._compByRef:
            raise RuntimeError(f"[ERROR] cannot remove the component {ref} from system {ref} !")
        self._compByRef.remove(ref)

