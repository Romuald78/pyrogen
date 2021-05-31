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
        v = self._computeCHK(offset)
        if self._buffer[offset + FsGpuBuffer.CHCK] != v:
            dump = self.dump()
            raise RuntimeError(f"[ERROR] bad data block integrity @offset={offset} \n{dump}")


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
    # PRIVATE API
    # ----------------------------------------------------
    def _isFree(self, offset):
        T = self._buffer[offset + FsGpuBuffer.TYPE]
        return T == FsGpuBuffer.FREE

    def _isAllocated(self, offset):
        return not self._isFree(offset)

    def _freeBlock(self, offset):
        # if the table is full
        if offset >= self.bufferSize:
            return None
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
        # Try to merge with next buffer if empty too
        self._mergeNext(offset)

    def _allocateBlock(self, userSize, userType, offset=0):
        while True:
            # if the table is full
            if offset >= self.bufferSize:
                raise RuntimeError(f"[ERROR] Cannot alocate userLen={userSize} because either all memory is occupied, or there is smaller blocks available !")
            # Check data integrity
            self._verifCHK(offset)
            # Get current slot information
            if self._isFree(offset):
                # We have found an empty block
                # First try to merge it with next blocks in order to reduce fragmentation
                self._mergeNext(offset)
                # Then get current block length (may have been merged)
                L = int(self._buffer[offset + FsGpuBuffer.LENG])
                if L <= 0:
                    raise RuntimeError(f"[ERROR] Bad length 0 @offset={offset} !\n" + self.dump())
                # then check if size is enough
                blockSize = userSize + FsGpuBuffer.OVERHEAD
                # Check the minimum  block size
                if blockSize < FsGpuBuffer.OVERHEAD + FsGpuBuffer.MIN_SIZE:
                    blockSize = FsGpuBuffer.OVERHEAD + FsGpuBuffer.MIN_SIZE
                # Check if the remaining length is at least enough for another small block
                if L - blockSize < FsGpuBuffer.OVERHEAD + FsGpuBuffer.MIN_SIZE:
                    # not enough room : take all the room
                    blockSize = L
                if blockSize <= L:
                    # OK block found : set the data
                    # First set user length and type
                    self._buffer[offset + FsGpuBuffer.SIZE] = userSize
                    self._buffer[offset + FsGpuBuffer.TYPE] = userType
                    # Check if there is at least 4 user bytes available
                    if blockSize + FsGpuBuffer.MIN_SIZE > L:
                        blockSize = L
                        self._buffer[offset + FsGpuBuffer.LENG] = blockSize
                        self._buffer[offset + FsGpuBuffer.CHCK] = self._computeCHK(offset)
                    else:
                        self._buffer[offset + FsGpuBuffer.LENG] = blockSize
                        self._buffer[offset + FsGpuBuffer.CHCK] = self._computeCHK(offset)
                        # Set next block info
                        offset2 = offset + blockSize
                        self._buffer[offset2 + FsGpuBuffer.TYPE] = FsGpuBuffer.FREE
                        self._buffer[offset2 + FsGpuBuffer.LENG] = L - blockSize
                        self._buffer[offset2 + FsGpuBuffer.SIZE] = L - blockSize
                        self._buffer[offset2 + FsGpuBuffer.CHCK] = self._computeCHK(offset2)
                    # end of process
                    return offset
                else:
                    # check next slot because current is too small
                    offset += L
            else:
                # Then get current block length
                L = int(self._buffer[offset + FsGpuBuffer.LENG])
                # check next slot because current is already allocated
                offset += L

    def _mergeNext(self, offset):
        while True:
            # Get block data length
            L = self._buffer[offset + FsGpuBuffer.LENG]
            # Get next block offset
            offset2 = int(offset + L)
            # if the table is full
            if offset2 >= self.bufferSize:
                return
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
                # Update current one (just length and integrity)
                self._buffer[offset + FsGpuBuffer.LENG] = L + L2
                self._buffer[offset + FsGpuBuffer.SIZE] = L + L2
                self._buffer[offset + FsGpuBuffer.CHCK] = self._computeCHK(offset)
                # Check if another block can be merged once again
                # print(f"merged between @{offset} and @{offset2}")
            else:
                return

    # read data
    def _read(self, offset, length=-1):
        # TODO
        pass

    # Write data
    def _write(self, offset, length=-1):
        # TODO
        pass


    # ----------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------
    # this method checks if there is a slot in the allocation table
    # and checks if there is a big enough data block.
    # It returns the allocation table entry ID
    # or it raises an error if no more memory available (either table or data)
    def alloc(self, userSize, userType):
        offset = self._allocateBlock(userSize, userType, 0)
        return offset

    # This method releases a previous reserved block
    def free(self, offset):
        self._freeBlock(offset)

    # Read block data
    def readBlock(self, offset):
        # TODO
        pass

    # Update a buffer block
    def writeBlock(self, offset, values):
        # TODO
        pass

    # read one value
    def readValue(self, offset, subOffset):
        # TODO
        pass

    # write one value
    def writeValue(self, offset, subOffset, value):
        # TODO
        pass


    # ----------------------------------------------------
    # DEBUG
    # ----------------------------------------------------
    def display(self):
        print(self.dump())

    def dump(self, offset=0):
        CR = "\n"
        msg = "--------------" + CR
        i = 0
        while offset < self.bufferSize:
            T = int(self._buffer[offset + FsGpuBuffer.TYPE])
            L = int(self._buffer[offset + FsGpuBuffer.LENG])
            U = int(self._buffer[offset + FsGpuBuffer.SIZE])
            C =     self._buffer[offset + FsGpuBuffer.CHCK]
            msg += f"<Block #{i} @{'0x{0:0{1}X}'.format(offset,8)}/{offset} - blockLen={'0x{0:0{1}X}'.format(L,8)} - type={T} - userLen={'0x{0:0{1}X}'.format(U,8)} - checksum={C}>" + CR
            offset += int(L)
            i += 1
        return msg

    def test(self):
        MINI = 1
        MAXI = 23
        offsets  = []
        remove   = True
        reserve  = True
        MAX_ITER = 200000
        for i in range(MAX_ITER):
            if i%1000 == 0:
                progress = round(100*i/MAX_ITER,3)
                print( f"{progress}%" )
            if remove:
                # remove N random block from actives
                N = randint(0,len(offsets)//3)
                if N > 0:
                    for i in range(N):
                        try:
                            rem = choice(offsets)
                            #print(f"<<<<<<<<<<<<<<<<<<<< Remove @{rem}")
                            self.free(rem)
                            offsets.remove(rem)
                        except Exception as ex:
                            # if memory is full : just exit and display
                            print("\n")
                            print(ex)
                            print("\n")
                            self.display()
                            print(offsets)
                            exit()

            if reserve:
                # reserve N new blocks
                N = randint(0, 5)
                if N > 0:
                    for i in range(N):
                        try:
                            siz = randint(MINI, MAXI)
                            offset = self.alloc(siz, randint(1,4))
                            if offset in offsets:
                                raise RuntimeError(f"Offset already present in the active list ({offset})")
                            #print(f">>>>>>>>>>>>>>>>>>>> Add @{offset}")
                            offsets.append(offset)
                        except Exception as ex:
                            # if memory is full : just exit and display
                            print("--------------------------------")
                            print(ex)
                            print("--------------------------------")
                            self.display()
                            exit()

        self.display()
        exit()