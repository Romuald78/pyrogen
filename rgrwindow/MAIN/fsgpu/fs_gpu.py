import random

from pyrogen.src.pyrogen.rgrwindow.MAIN.fsgpu.fs_alloc_table import FsAllocTable
from pyrogen.src.pyrogen.rgrwindow.MAIN.fsgpu.fs_data_block import FsDataBlock


class FsGpu():

    # ----------------------------------------------------
    # Constructor
    # ----------------------------------------------------
    def __init__(self, textureInfo, bufferInfo, textureData, bufferData):
        # Store properties
        self._table = FsAllocTable(textureInfo, bufferInfo)
        self._data  = FsDataBlock (textureData, bufferData)

    # this method checks if there is a slot in the allocation table
    # and checks if there is a big enough data block.
    # It returns the allocation table entry ID
    # or it raises an error if no more memory available (either table or data)
    def reserve(self, userSize, userType):
        # Get info from alloc table and data buffer
        entryID  = self._table.findEmptySlot()
        blockOf7 = self._data.findEmptyBlock(userSize)
        # if not possible to allocate : raise error
        if entryID == None or blockOf7 == None:
            dmp = self._data.dumpBlocks()
            raise RuntimeError(f"[ERROR] impossible to reserve a buffer. userSize={userSize} entryID={entryID} blockOf7={blockOf7}\n"+dmp)
        # Set allocation entry
        self._table.useSlot(entryID, userType, userSize, blockOf7)
        # Set data
        self._data.useBlock(userType, userSize, blockOf7)
        # Return alloc table ID
        return entryID

    # Write data into the file system block
    def writeBlock(self, entryID, buffer):
        # get info on allocation table entry
        info   = self._table.getInfo(entryID)
        # Retrieve data block offset
        offset = info["offset"]
        # Get info from data block and check integrity
        info2  = self._data.getInfo(offset)
        if info["length"] != info2["length"] - FsDataBlock.OVERHEAD:
            raise RuntimeError("[ERROR] CORRUPTION in FS (bad lengths)!")
        # Write buffer into the data block
        self._data.writeData(offset, buffer)

    # This method releases a previous reserved block
    def release(self, entryID):
        # Get data offset from it
        info   = self._table.getInfo(entryID)
        offset = info["offset"]
        info2  = self._data.getInfo(offset)
        if info["length"] != info2["length"] - FsDataBlock.OVERHEAD:
            raise RuntimeError("[ERROR] CORRUPTION in FS (bad lengths)!")

        self._table.release(entryID)
        self._data.release(offset)

    # DEBUG
    def debug(self):
        # For every valid allocation entry
        for i in range(self._table.size):
            entry1  = self._table.getInfo(i)
            type1   = entry1["type"]
            len1    = entry1["length"]
            offset1 = entry1["offset"]
            warn = ""
            if entry1["type"] != 0:
                line   = "<Slot #%02d" % (i) + f" - {type1}"
                entry2 = self._data.getInfo(offset1)
                type2  = entry2["type"]
                len2   = entry2["length"]
                if type1 != type2 or len1 != len2-FsDataBlock.OVERHEAD:
                    warn = " - [CORRUPTED!]"
                # We display the block length (including header length)
                line += f" - @{'0x{0:0{1}X}'.format(offset1,8)} - length={'0x{0:0{1}X}'.format(int(len2),8)}"
                line += f">{warn}"
                print(line)

        self._data.display()

    # TEST
    def test(self):
        sizeMin  = 4
        sizeMax  = 124

        actives  = []
        remove   = True
        reserve  = True
        MAX_ITER = 100000
        for i in range(MAX_ITER):
            if i%1000 == 0:
                progress = round(100*i/MAX_ITER,3)
                print( f"{progress}%" )
            if remove:
                # remove N random block from actives
                N = random.randint(0,len(actives)//3)
                if N > 0:
                    #print(f"> Remove {N} entries out of {len(actives)}")
                    for i in range(N):
                        rem = random.choice(actives)
                        #print(f"    > Remove entry #{rem}")
                        self.release(rem)
                        actives.remove(rem)

            if reserve:
                # reserve N new blocks
                N = random.randint(0, 5)
                if N > 0:
                    #print(f"> Add {N} entries")
                    for i in range(N):
                        try:
                            #print(f"    > Add entry...")
                            siz = random.randint(sizeMin, sizeMax)
                            tabID = self.reserve(siz, random.randint(1,4))
                            if tabID in actives:
                                raise RuntimeError(f"ID already present in the active list ({tabID})")
                            #print(f"        > ...Num #{tabID}")
                            actives.append(tabID)
                        except Exception as ex:
                            # if memory is full : just exit and display
                            print("\n")
                            print(ex)
                            print("MEMORY FULL !!!!!")
                            print("\n")
                            self.debug()
                            exit()

        self.debug()
        exit()