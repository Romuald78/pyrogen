import sys
from random import random, randint, choice

import numpy as np


class FsGpuBuffer():

    # ----------------------------------------------------
    # CONSTANTS
    # ----------------------------------------------------
    FREE = 0

    LENG = 0        # length of data block
    TYPE = 1        # Type of block (empty, sprite, rectangle, oval, line, text, light, ...)
                    # Types are not handled internally but provided from outside (except the 0/empty value)
    SIZE = 2        # user data size (can be less or equal to LENG)
    CHCK = 3        # Block Checksum

    OVERHEAD = 4    # 4 values as overhead
    MIN_SIZE = 4    # At least 4 values for a user block (that means 50 useful data)


    # ----------------------------------------------------
    # INTEGRITY CHECK
    # ----------------------------------------------------
    def _computeCHK(self, offset):
        v  = self._buffer[offset + FsGpuBuffer.LENG]
        v += self._buffer[offset + FsGpuBuffer.TYPE]
        v += self._buffer[offset + FsGpuBuffer.SIZE]
        return v

    def _verifCHK(self, offset):
        if offset > self.bufferSize:
            dump = self.dump()
            raise RuntimeError(f"[ERROR] bad block offsey @{offset} \n{dump}")
        v = self._computeCHK(offset)
        if self._buffer[offset + FsGpuBuffer.CHCK] != v:
            dump = self.dump()
            raise RuntimeError(f"[ERROR] bad data block integrity (checksum) @offset={offset} \n{dump}")
        if self._buffer[offset + FsGpuBuffer.SIZE] > self._buffer[offset + FsGpuBuffer.LENG]:
            dump = self.dump()
            raise RuntimeError(f"[ERROR] bad data block integrity (lengths) @offset={offset} \n{dump}")


    # ----------------------------------------------------
    # FREE BLOCKS
    # ----------------------------------------------------
    # This must be done when AFTER the block has been freed
    def _addFreeBlock(self, offset):
        # Check offset
        self._verifCHK(offset)
        # Get type
        T = self._buffer[offset + FsGpuBuffer.TYPE]
        if not T == FsGpuBuffer.FREE:
            raise RuntimeError(f"[ERROR] impossible to add a free block as it is not free ! offset={offset}")
        # Get user Length
        L = self._buffer[offset + FsGpuBuffer.LENG]
        # check entry
        if offset in self._freeBlocks:
            raise RuntimeError(f"[ERROR] impossible to add a free block as it is already added ! offset={offset}")
        # add entry
        self._freeBlocks[offset] = L

    # This must be done BEFORE filling it or AFTER erasing it
    def _removeFreeBlock(self, offset):
        # Check offset
        self._verifCHK(offset)
        # Get type
        T = self._buffer[offset + FsGpuBuffer.TYPE]
        if not T == FsGpuBuffer.FREE:
            dmp = self.dump()
            raise RuntimeError(f"[ERROR] impossible to remove a free block as it is not free yet ! offset={offset} T={T}\n"+dmp)
        # check entry
        if offset not in self._freeBlocks:
            raise RuntimeError(f"[ERROR] impossible to remove a free block as it is not added ! offset={offset}")
        # remove entry
        del self._freeBlocks[offset]

    # update is done AFTER the block has been updated
    def _updateFreeBlock(self, offset, newLength):
        # Check offset
        self._verifCHK(offset)
        # Get type
        T = self._buffer[offset + FsGpuBuffer.TYPE]
        if not T == FsGpuBuffer.FREE:
            raise RuntimeError(f"[ERROR] impossible to update a free block as it is not free yet ! offset={offset}")
        # check entry
        if offset not in self._freeBlocks:
            raise RuntimeError(f"[ERROR] impossible to update a free block as it is not added ! offset={offset}")
        # updateentry
        self._freeBlocks[offset] = newLength


    # ----------------------------------------------------
    # CONSTRUCTOR
    # ----------------------------------------------------
    # TODO : update texture on demand (  texture.write(data, viewport=(0, 0, 50, 50))  )
    def __init__(self, W, H=1, nbComp=4):
        # init buffer
        self._size   = W * H * nbComp
        self._buffer = np.zeros(self.bufferSize, np.float32)
        # Set first block as empty
        self._buffer[FsGpuBuffer.TYPE] = FsGpuBuffer.FREE
        self._buffer[FsGpuBuffer.LENG] = self.bufferSize
        self._buffer[FsGpuBuffer.SIZE] = self.bufferSize
        self._buffer[FsGpuBuffer.CHCK] = self._computeCHK(0)
        # Modified
        self._modified = True
        # Keep a list of unused areas
        # dict with offset as key and user size as value
        self._freeBlocks = {}
        self._addFreeBlock(0)


    # ----------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------
    @property
    def bufferSize(self):
        return self._size
    @property
    def modified(self):
        return self._modified


    # ----------------------------------------------------
    # PRIVATE METHODS
    # ----------------------------------------------------
    def _isFree(self, offset):
        T = self._buffer[offset + FsGpuBuffer.TYPE]
        return T == FsGpuBuffer.FREE

    def _isAllocated(self, offset):
        return not self._isFree(offset)

    def _freeBlock(self, offset):
        # Check data integrity
        self._verifCHK(offset)
        # Get current slot information
        if self._isFree(offset):
            raise RuntimeError(f"[ERROR] the block offset {offset} cannot be released as it is ALREADY empty !")
        # Free the block
        self._buffer[offset + FsGpuBuffer.TYPE] = FsGpuBuffer.FREE
        # Do not update block length as it must remain unchanged, but update user size
        self._buffer[offset + FsGpuBuffer.SIZE] = self._buffer[offset + FsGpuBuffer.LENG]
        # recompute new integrity
        self._buffer[offset + FsGpuBuffer.CHCK] = self._computeCHK(offset)
        # Add this block into the free list
        self._addFreeBlock(offset)
        # Try to merge with next buffer if empty too
        self._mergeNext(offset)
        # Free process is ok
        self._modified = True
        return True

    # allocate selected block
    def _allocateSelected(self, userSize, userType, selected, minSize):
        # Set local variables
        L1        = minSize
        offset    = selected
        blockSize = userSize + FsGpuBuffer.OVERHEAD
        # Check if the remaining length is at least enough for another small block
        if L1 - blockSize < FsGpuBuffer.OVERHEAD + FsGpuBuffer.MIN_SIZE:
            # not enough room : take all the room
            blockSize = L1
        # Remove the free block from the list
        self._removeFreeBlock(offset)
        # set the data
        # First set user length and type
        self._buffer[offset + FsGpuBuffer.SIZE] = userSize
        self._buffer[offset + FsGpuBuffer.TYPE] = userType
        # Check if there is at least 4 user bytes available
        if blockSize + FsGpuBuffer.MIN_SIZE > L1:
            blockSize = L1
            self._buffer[offset + FsGpuBuffer.LENG] = blockSize
            self._buffer[offset + FsGpuBuffer.CHCK] = self._computeCHK(offset)
        else:
            self._buffer[offset + FsGpuBuffer.LENG] = blockSize
            self._buffer[offset + FsGpuBuffer.CHCK] = self._computeCHK(offset)
            # Set next block info
            offset2 = offset + blockSize
            self._buffer[offset2 + FsGpuBuffer.TYPE] = FsGpuBuffer.FREE
            self._buffer[offset2 + FsGpuBuffer.LENG] = L1 - blockSize
            self._buffer[offset2 + FsGpuBuffer.SIZE] = L1 - blockSize
            self._buffer[offset2 + FsGpuBuffer.CHCK] = self._computeCHK(offset2)
            # Add the new free block in the list
            self._addFreeBlock(offset2)
        # end of process
        self._modified = True
        return offset

    # Allocation process based on free block list : complexity depends on fragmentation
    def _allocateBlock2(self, userSize, userType):
        # Compute blocksize
        blockSize = userSize + FsGpuBuffer.OVERHEAD
        # Browse each free block from the list
        for offset in self._freeBlocks:
            # Check data integrity
            self._verifCHK(offset)
            # Check it is really free
            if not self._isFree(offset):
                raise RuntimeError(f"[ERROR] there is an error in the free block list : the block @{offset} ith length={L} is not free !")

            # Get length of this free block
            L1 = self._freeBlocks[offset]
            L2 = int(self._buffer[offset + FsGpuBuffer.LENG])
            if L1 != L2:
                raise RuntimeError(
                    f"[ERROR] there is an error in the free block list : the block @{offset} : length is not good L1={L1} L2={L2}!")

            # First check the block size fits
            if blockSize < FsGpuBuffer.OVERHEAD + FsGpuBuffer.MIN_SIZE:
                blockSize = FsGpuBuffer.OVERHEAD + FsGpuBuffer.MIN_SIZE
            # If it finally fits, allocate
            if blockSize <= L1:
                return self._allocateSelected(userSize, userType, offset, L1)

        # If we reach this part of code, no space was available
        # either the memory is full or there are some free blocks
        # too small for the requested usersize
        return None

    def _mergeNext(self, offset):
        while True:
            # Get block data length
            L = self._buffer[offset + FsGpuBuffer.LENG]
            # Get next block offset
            offset2 = int(offset + L)
            # if the table is full
            if offset2 >= self.bufferSize:
                return False
            # Check data integrity of next block
            self._verifCHK(offset2)
            # Check if this new block is empty so we can merge. else we just return
            if self._isFree(offset2):
                # Get next block length
                L2 = self._buffer[offset2 + FsGpuBuffer.LENG]
                # Clear next
                self._buffer[offset2 + FsGpuBuffer.TYPE] = 0
                self._buffer[offset2 + FsGpuBuffer.LENG] = 0
                self._buffer[offset2 + FsGpuBuffer.SIZE] = 0
                self._buffer[offset2 + FsGpuBuffer.CHCK] = 0
                # Remove next block from list
                self._removeFreeBlock(offset2)

                # Update current one (just length and integrity)
                self._buffer[offset + FsGpuBuffer.LENG] = L + L2
                self._buffer[offset + FsGpuBuffer.SIZE] = L + L2
                self._buffer[offset + FsGpuBuffer.CHCK] = self._computeCHK(offset)
                # Update length of current block
                self._updateFreeBlock(offset, L+L2)
                # print(f"merged between @{offset} and @{offset2}")
                return True
            else:
                return False

    # read data
    def _read(self, offset, length=-1, subOffset=0):
        # Check integrity for this block
        self._verifCHK(offset)
        # if length == -1, that means read all the block
        S = self._buffer[offset + FsGpuBuffer.SIZE]
        if length < 0:
            length = S
        # check the requested length is correct
        if length > S - subOffset:
            raise RuntimeError(f"[WARNING] reading too much from buffer - offset={offset} - readLen={length} - subOffset={subOffset}",file=sys.stderr)
        # Read the buffer part and return
        start = int(offset + FsGpuBuffer.OVERHEAD)
        end   = int(start + length)
        out = self._buffer[start:end]
        return out

    # Write data
    def _write(self, offset, values, subOffset=0):
        length = len(values)
        # Check integrity for this block
        self._verifCHK(offset)
        # Get user length of block
        S = self._buffer[offset + FsGpuBuffer.SIZE]
        # check the requested length is correct
        if length > S - subOffset:
            raise RuntimeError(f"[WARNING] writing too much to buffer - offset={offset} - writeLen={length} - subOffset={subOffset}",file=sys.stderr)
        for i in range(length):
            self._buffer[offset+FsGpuBuffer.OVERHEAD+subOffset+i] = values[i]


    # ----------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------
    # this method checks if there is a slot in the allocation table
    # and checks if there is a big enough data block.
    # It returns the block offset( in the current buffer) or None if no space
    def alloc(self, userSize, userType):
        if userType == FsGpuBuffer.FREE:
            raise RuntimeError(f"[ERROR] cannot allocate a block with a 'FREE' type. Type of block must be different from the value '{FsGpuBuffer.FREE}'")
        return self._allocateBlock2(userSize, userType)

    # This method releases a previous reserved block
    def free(self, offset):
        return self._freeBlock(offset)

    # Method used to reset the "modified" flag
    def resetModify(self):
        self._modified = False

    # read one value
    def read(self, offset, length=-1, subOffset=0):
        return self._read(offset, length, subOffset)

    # write one value
    def write(self, offset, values, subOffset=0):
        self._write(offset, values, subOffset)

    # Defrag operation
    # For the moment we only merge free contiguous blocks
    def defrag(self):
        # Each time we browse the free block list, if we merge free blocks,
        # the list is modified while iterating on it : this generates an exception
        # So to avoid problems, the process could stop the loop after one merge
        # has been performed. That would mean we would only merge once per frame
        # in the worst case : this would solve both the modification/iteration issue
        # and would limit the CPU load : it seems to be a good compromise
        for offset in self._freeBlocks:
            # Check data integrity
            self._verifCHK(offset)
            # Get current slot information
            if not self._isFree(offset):
                raise RuntimeError(f"[ERROR] the block offset {offset} cannot be merged as it is not empty : why is it in the free block list !?")
            # merge if possible
            res = self._mergeNext(offset)
            if res:
                return True
        return False


    # ----------------------------------------------------
    # DEBUG
    # ----------------------------------------------------
    def display(self, displayData=False):
        print(self.dump(displayData))

    def dump(self, displayData=False, offset=0):
        CR = "\n"
        msg = ""
        i = 0
        # Dump free block list
        for frOf7 in self._freeBlocks:
            L = int(self._freeBlocks[frOf7])
            msg += f"<FreeBlock @{'0x{0:0{1}X}'.format(frOf7,8)} - L={'0x{0:0{1}X}'.format(L,8)}>" + CR
        # Dump block data
        while offset < self.bufferSize:
            T = int(self._buffer[offset + FsGpuBuffer.TYPE])
            L = int(self._buffer[offset + FsGpuBuffer.LENG])
            U = int(self._buffer[offset + FsGpuBuffer.SIZE])
            C =     self._buffer[offset + FsGpuBuffer.CHCK]
            msg += f"<Block #{i} @{'0x{0:0{1}X}'.format(offset,8)} - blockLen={'0x{0:0{1}X}'.format(L,8)} - type={T} - userLen={'0x{0:0{1}X}'.format(U,8)} - checksum={C}>" + CR
            if displayData and T != FsGpuBuffer.FREE:
                data = []
                of7 = offset + FsGpuBuffer.OVERHEAD
                for i in range(U):
                    v = self._buffer[of7+i]
                    data.append(str(v))
                msg += "    " + "\n    ".join(data) + CR
            offset += int(L)
            i += 1
        return msg

