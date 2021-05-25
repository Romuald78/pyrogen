from random import randint, random

# /!\ all lengths are in nbComponent unit /!\
# that means 1 unit can contains N 32-bit values

class FsDataBlock():

    # ----------------------------------------------------
    # CONSTANTS
    # ----------------------------------------------------
    EMPTY  = 0

    LENG  = 0   # length of data block
    TYPE  = 1   # Type of block (empty, sprite, rectangle, oval, line, text, light, ...)
                # Types are not handled internally but provided from outside (except the 0/empty value)
    RAND  = 2   # random value for checksum
    CHK   = 3   # Block Checksum

    OVERHEAD = 4    # 4 values as overhead


    # ----------------------------------------------------
    # Simple integrity check
    # ----------------------------------------------------
    def _computeCHK(self, offset):
        v  = self._buffer[offset+FsDataBlock.LENG]
        v += self._buffer[offset+FsDataBlock.TYPE]
        v += self._buffer[offset+FsDataBlock.RAND]
        return v

    def _verifCHK(self, offset):
        v = self._computeCHK(offset)
        if self._buffer[offset+FsDataBlock.CHK] != v:
            dump = self.dumpBlocks()
            raise RuntimeError(f"[ERROR] bad data block integrity @offset={offset} nbComponents={self.components}\n{dump}")


    # ----------------------------------------------------
    # Constructor
    # ----------------------------------------------------
    def __init__(self, texture, buffer):
        # Store properties
        self._texture = texture
        self._buffer  = buffer
        self._size    = texture.width*texture.height
        # Fill Table with 0 to indicate the slots are available
        self._buffer.fill(FsDataBlock.EMPTY)
        # set first block
        self._buffer[FsDataBlock.TYPE] = FsDataBlock.EMPTY
        self._buffer[FsDataBlock.LENG] = self.size
        self._buffer[FsDataBlock.RAND] = random() + 0.1
        self._buffer[FsDataBlock.CHK]  = self._computeCHK(0)



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
        T = self._buffer[offset + FsDataBlock.TYPE]
        return T == FsDataBlock.EMPTY

    def findEmptyBlock(self, userSize, offset=0):
        while True:
            # if the table is full
            if offset >= self.size:
                return None
            # Check data integrity
            self._verifCHK(offset)
            # Get current slot information
            if self._isEmpty(offset):
                # We have found an empty block
                # First try to merge it with next blocks in order to reduce fragmentation
                self._mergeNext(offset)
                # Then get current block length (may have been merged)
                L = int(self._buffer[offset + FsDataBlock.LENG])
                if L <= 0:
                    raise RuntimeError("[ERROR] Bad length \n"+self.dumpBlocks())
                # then check if size is enough
                if userSize + FsDataBlock.OVERHEAD <= L - FsDataBlock.OVERHEAD:
                    return offset

            # Get current block length
            L = int(self._buffer[offset + FsDataBlock.LENG])
            # check next slot because either current one is not available nor big enough
            offset += L

    def isEmpty(self, offset):
        # if the table is full
        if offset >= self.size:
            return None
        # Check data integrity
        self._verifCHK(offset)
        return self._isEmpty(offset)

    def isBusy(self, offset):
        return not self.isEmpty(offset)

    def getInfo(self, offset):
        # if the table is full
        if offset >= self.size:
            return None
        # Check data integrity
        self._verifCHK(offset)
        # prepare output
        L = self._buffer[offset+FsDataBlock.LENG]
        T = self._buffer[offset+FsDataBlock.TYPE]
        R = self._buffer[offset+FsDataBlock.RAND]
        C = self._buffer[offset+FsDataBlock.CHK ]
        return {"length": L, "type": T, "random": R, "checksum": C}


    # ----------------------------------------------------
    # Use a slot
    # ----------------------------------------------------
    def _use(self, type, offset, userLen):
        blockLen = userLen + FsDataBlock.OVERHEAD
        # Get block data
        L = self._buffer[offset + FsDataBlock.LENG]
        # check if the block can contains all the user data and let space for at least one header + 0 data byte
        if blockLen > L - FsDataBlock.OVERHEAD:
            raise RuntimeError(f"[ERROR] block offset {offset} cannot contains {userLen}+{FsDataBlock.OVERHEAD} values")

        # update current block (transform from empty to 'type')
        self._buffer[offset + FsDataBlock.TYPE] = type
        self._buffer[offset + FsDataBlock.LENG] = blockLen
        self._buffer[offset + FsDataBlock.RAND] = random()+0.1
        self._buffer[offset + FsDataBlock.CHK ] = self._computeCHK(offset)

        if blockLen < L:
            # Update remaining empty block (if needed)
            offset += blockLen
            self._buffer[offset + FsDataBlock.TYPE] = FsDataBlock.EMPTY
            self._buffer[offset + FsDataBlock.LENG] = L-blockLen
            self._buffer[offset + FsDataBlock.RAND] = random() + 0.1
            self._buffer[offset + FsDataBlock.CHK]  = self._computeCHK(offset)

    def useBlock(self, type, userLen, offset):
        # if the table is full
        if offset >= self.size:
            return None
        # check user type
        if type == FsDataBlock.EMPTY:
            raise RuntimeError("[ERROR] bad user type={type}. Cannot reserve an empty block !")
        # Check data integrity
        self._verifCHK(offset)
        # Get current slot information
        if self._isEmpty(offset):
            self._use(type, offset, userLen)
        else:
            raise RuntimeError(f"[ERROR] the block offset {offset} cannot be used as it is NOT empty !")


    # ----------------------------------------------------
    # Release slot
    # ----------------------------------------------------
    def _mergeNext(self, offset):
        # Get block data length
        L = self._buffer[offset + FsDataBlock.LENG]
        # Get next block offset
        offset2 = int(offset + L)
        # if the table is full
        if offset2 >= self.size:
            return None
        # Check data integrity
        self._verifCHK(offset2)
        # Check if this new block is empty so we can merge. else we just return
        if self._isEmpty(offset2):
            # Get next block length
            L2 = self._buffer[offset2 + FsDataBlock.LENG]
            # Clear next
            self._buffer[offset2 + FsDataBlock.TYPE] = 0
            self._buffer[offset2 + FsDataBlock.LENG] = 0
            self._buffer[offset2 + FsDataBlock.RAND] = 0
            self._buffer[offset2 + FsDataBlock.CHK ] = 0
            # Update current one (just length and integrity)
            self._buffer[offset + FsDataBlock.LENG]  = L+L2
            self._buffer[offset + FsDataBlock.CHK ]  = self._computeCHK(offset)
            # Check if another block can be merged once again
            #print(f"merged between @{offset} and @{offset2}")
            self._mergeNext(offset)

    def _release(self, offset):
        self._buffer[offset + FsDataBlock.TYPE] = FsDataBlock.EMPTY
        # Do not update block length as it must remain unchanged
        # Do no update random value as it may remain unchanged
        # recompute new integrity
        self._buffer[offset + FsDataBlock.CHK ] = self._computeCHK(offset)
        # Try to merge with next buffer if empty too
        self._mergeNext(offset)

    def release(self, offset):
        # if the table is full
        if offset >= self.size:
            return None
        # Check data integrity
        self._verifCHK(offset)
        # Get current slot information
        if not self._isEmpty(offset):
            self._release(offset)
        else:
            raise RuntimeError(f"[ERROR] the block offset {offset} cannot be released as it is ALREADY empty !")

    # ----------------------------------------------------
    # Write operations
    # ----------------------------------------------------
    def writeData(self, offset, buffer):
        # if the table is full
        if offset >= self.size :
            raise RuntimeError(f"[ERROR] Bad offset @{offset} ")
        # Check integrity
        self._verifCHK(offset)
        # Check length
        L1 = len(buffer)
        L2 = self._buffer[offset+FsDataBlock.LENG]
        if L1 > L2 - FsDataBlock.OVERHEAD:
            raise RuntimeError(f"[ERROR] cannot write data (L={L1}) @{offset} (available={L2})")
        # Copy data into block
        start = offset+FsDataBlock.OVERHEAD
        end   = start + L1
        self._buffer[start:end] = buffer
        # Copy data into texture too
        # TODO : update texture into GPU ,because for the moment only the CPU buffers are up to date

    # ----------------------------------------------------
    # Debug
    # ----------------------------------------------------
    def display(self):
        print(self.dumpBlocks())

    def dumpBlocks(self, offset=0):
        CR = "\n"
        msg = "--------------" + CR
        i = 0
        while offset < self.size:
            T = int(self._buffer[offset + FsDataBlock.TYPE])
            L = int(self._buffer[offset + FsDataBlock.LENG])
            R = self._buffer[offset + FsDataBlock.RAND]
            C = self._buffer[offset + FsDataBlock.CHK ]
            msg += f"<Block #{i} @{'0x{0:0{1}X}'.format(offset,8)} - length={'0x{0:0{1}X}'.format(L,8)}\t type={T}\t random={R}\t checksum={C}>" + CR
            offset += int(L)
            i += 1
        return msg