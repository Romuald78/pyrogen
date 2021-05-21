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

    # this method checks if there is a slot in the allocation
    # table+ a big enough data block. It returns the allocation table
    # entry ID or raise an error if no more memory available
    def reserve(self, userSize, userType):
        # Get info from alloc table and data buffer
        entryID  = self._table.findEmptySlot()
        blockOf7 = self._data.findEmptyBlock(userSize)
        # if not possible to allocate : raise error
        if entryID == None or blockOf7 == None:
            raise RuntimeError(f"[ERROR] impossible to reserve a buffer. userSize={userSize} entryID={entryID} blockOf7={blockOf7}")
        # Set allocation entry
        self._table.useSlot(entryID, userSize, blockOf7)
        # Set data
        self._data.useBlock(userType, blockOf7, userSize)

    # DEBUG
    def debug(self):
        # For every valid allocation entry
        for i in range(self._table.size):
            entry = self._table.getInfo(i)
            if entry["type"] != 0:
                offset = entry["offset"]
                block = self._data.getInfo(offset)

                print(entry)
