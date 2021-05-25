from random import randint


class FsAllocTable():

    # ----------------------------------------------------
    # CONSTANTS
    # ----------------------------------------------------
    EMPTY = 0

    LENG  = 0   # length of data block
    TYPE  = 1   # Type of table entry (busy or not)
    OF7   = 2   # Offset of block in data texture
    CHK   = 3


    # ----------------------------------------------------
    # Simple integrity check
    # ----------------------------------------------------
    def _computeCHK(self, offset):
        v  = self._buffer[offset+FsAllocTable.LENG]
        v ^= self._buffer[offset+FsAllocTable.TYPE]
        v ^= self._buffer[offset+FsAllocTable.OF7 ]
        return v

    def _verifCHK(self, offset):
        v = self._computeCHK(offset)
        if self._buffer[offset+FsAllocTable.CHK] != v:
            id = offset//self.components
            raise RuntimeError(f"[ERROR] bad alloc table integrity @offset={offset} id={id} nbComponents={self.components}")


    # ----------------------------------------------------
    # Constructor
    # ----------------------------------------------------
    def __init__(self, texture, buffer):
        # Store properties
        self._texture = texture
        self._buffer  = buffer
        self._size    = texture.width*texture.height
        # Fill Table with 0 to indicate the slots are available
        self._buffer.fill(FsAllocTable.EMPTY)


    # ----------------------------------------------------
    # Properties
    # ----------------------------------------------------
    @property
    def size(self):
        return self._size

    @property
    def components(self):
        return self._texture.components


    # ----------------------------------------------------
    # Search for empty slot
    # ----------------------------------------------------
    def _isEmpty(self, offset):
        T = self._buffer[offset + FsAllocTable.TYPE]
        return T == FsAllocTable.EMPTY

    def findEmptySlot(self, entryID=0):
        while True:
            # if the table is full
            if entryID >= self.size:
                return None
            # Get offset from entry ID
            offset = entryID * self.components
            # Check data integrity
            self._verifCHK(offset)
            # Get current slot information
            if self._isEmpty(offset):
                # We have found an empty slot
                return entryID
            # check next slot if previous were not available
            entryID += 1

    def isEmpty(self, entryID):
        # if the table is full
        if entryID >= self.size:
            return None
        # Get offset from entry ID
        offset = entryID * self.components
        # Check data integrity
        self._verifCHK(offset)
        return self._isEmpty(offset)

    def isBusy(self, entryID):
        return not self.isEmpty(entryID)


    # ----------------------------------------------------
    # Get info from a slot
    # ----------------------------------------------------
    def getInfo(self, entryID):
        # if the table is full
        if entryID >= self.size:
            return None
        # Get offset from entry ID
        offset = entryID * self.components
        # Check data integrity
        self._verifCHK(offset)
        # prepare data
        L = self._buffer[offset + FsAllocTable.LENG]
        T = self._buffer[offset + FsAllocTable.TYPE]
        O = self._buffer[offset + FsAllocTable.OF7]
        C = self._buffer[offset + FsAllocTable.CHK]
        return {"length":L,"type":T,"offset":O,"checksum":C}

    # ----------------------------------------------------
    # Use a slot
    # ----------------------------------------------------
    def _use(self, offset, userType, userSize, blockOf7):
        self._buffer[offset + FsAllocTable.LENG] = userSize
        self._buffer[offset + FsAllocTable.TYPE] = userType
        self._buffer[offset + FsAllocTable.OF7 ] = blockOf7
        self._buffer[offset + FsAllocTable.CHK ] = self._computeCHK(offset)

    def useSlot(self, entryID, userType, userSize, blockOF7):
        # if the table is full
        if entryID >= self.size:
            return None
        # Get offset from entry ID
        offset = entryID * self.components
        # Check data integrity
        self._verifCHK(offset)
        # Get current slot information
        if self._isEmpty(offset):
            self._use(offset, userType, userSize, blockOF7)
        else:
            raise RuntimeError(f"[ERROR] the slot {entryID} cannot be used as it is NOT empty !")


    # ----------------------------------------------------
    # Release slot
    # ----------------------------------------------------
    def _release(self, offset):
        self._buffer[offset + FsAllocTable.TYPE] = FsAllocTable.EMPTY
        self._buffer[offset + FsAllocTable.LENG] = 0
        self._buffer[offset + FsAllocTable.OF7 ] = 0
        self._buffer[offset + FsAllocTable.CHK ] = 0

    def release(self, entryID):
        # if the table is full
        if entryID >= self.size:
            return None
        # Get offset from entry ID
        offset = entryID * self.components
        # Check data integrity
        self._verifCHK(offset)
        # Get current slot information
        if not self._isEmpty(offset):
            self._release(offset)
        else:
            raise RuntimeError(f"[ERROR] the slot {entryID} cannot be released as it is ALREADY empty !")

