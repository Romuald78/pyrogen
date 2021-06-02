import math
import time
from random import choice, randint

from pyrogen.src.pyrogen.rgrwindow.MAIN.fsgpu2.fsgpu_buffer import FsGpuBuffer


class FsGpuMain():


    # ----------------------------------------------------
    # CONSTRUCTOR
    # ----------------------------------------------------
    def __init__(self, pageSize, nbPages):
        # pageShift is the number of bits to code the pageSize
        # 18 means the page size can be 128kB
        self._pageShift = 18
        # Either page size cannot be more than 2^pageShift
        if pageSize > math.pow(2, self._pageShift):
            raise RuntimeError(f"[ERROR] bad page size : size={pageSize} is too big. Do not use more than {math.pow(2, self._pageShift)} !")
        # Each page is a FsGpuBuffer instance
        self._pageSize = pageSize
        self._nbPages  = nbPages
        # init buffers
        self._clear()

    # ----------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------
    @property
    def pages(self):
        return self._nbPages
    @property
    def pageSize(self):
        return self._pageSize
    @property
    def totalSize(self):
        return self.pageSize * self.pages


    # ----------------------------------------------------
    # PRIVATE METHODS
    # ----------------------------------------------------
    def _clear(self):
        # create buffers
        self._pages = [FsGpuBuffer(self.pageSize) for N in range(self.pages)]
        # Create texture from context
        # TODO

    def _isPageOK(self, pageNum):
        return pageNum >= 0 and pageNum < self.pages

    def _createID(self, offset, page):
        return (page << self._pageShift) + offset

    def _explodeID(self, id):
        offMask  = (1 << self._pageShift) - 1
        pageMask = (1 << (32 - self._pageShift)) - 1
        offset   = id & offMask
        page     = (id >> self._pageShift) & pageMask
        return (offset, page)


    # ----------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------
    # the ascending parameter is used to go through the pages
    # in order to find a valid available space (from tge beginning or the end)
    # The page number AND the buffer offset are gathered and returned as a buffer ID
    def alloc(self, userSize, userType, searchFromEnd=False, data=None):
        # Init vars
        step   = 1
        offset = None
        page = 0
        if searchFromEnd:
            step = -1
            page = len(self._pages)-1
        # Process allocation
        while offset == None:
            # check current page number
            if not self._isPageOK(page):
                dmp = self.dump()
                raise RuntimeError(f"[ERROR] page number is not correct during allocation. May be the memory is full, or the requested start page is not correct. page={page} !\n" + dmp)
            # Try to allocate a block into the current page (can return None if no available space)
            offset = self._pages[page].alloc(userSize, userType)
            # Go to next page (if needed)
            page += step
        # Here we have a valid offset, get block ID (page must be -1 because of the loop)
        id = self._createID(offset, page - step)
        # Fill the buffer if requested
        if data != None:
            self.writeBlock(id, data)
        # return block ID
        return id

    def free(self, blockID):
        # retrieve block position information
        offset, page = self._explodeID(blockID)
        if not self._isPageOK(page):
            raise RuntimeError(f"[ERROR] bad page value from block ID ! id={blockID} - page={page} - offset={offset}")
        # Now free this block from the memory
        self._pages[page].free(offset)

    def readBlock(self, id):
        # retrieve block position information
        offset, page = self._explodeID(id)
        # return block data
        return self._pages[page].read(offset)

    def writeBlock(self, id, data):
        # retrieve block position information
        offset, page = self._explodeID(id)
        # write block data
        self._pages[page].write(offset, data)


    # ----------------------------------------------------
    # DEBUG
    # ----------------------------------------------------
    def display(self, displayData=False):
        print(self.dump(displayData))

    def dump(self, displayData=False):
        out = ""
        i = 0
        for page in self._pages:
            out +=  "=================================================" + "\n"
            out +=  "=================    PAGE %02d    =================" % (i)  + "\n"
            out += f"================= modified={page.modified} =================" + "\n"
            out +=  "=================================================" + "\n"
            i += 1
            out += page.dump(displayData)
        return out

    def test002(self):
        BSIZE = 8
        TYPE  = 1
        data = [10 + i for i in range(BSIZE)]
        allocTime = []
        freeTime  = []
        blockIDs  = []
        # Init buffers
        self._clear()
        # Perform N tests
        for N in range(10000):

            # Try to free up some buffers
            if len(blockIDs) > 10:
                nbRemove = randint(1,len(blockIDs)//10)
                for i in range(nbRemove):
                    # Free block
                    idRemove = choice(blockIDs)
                    time0 = time.time()
                    self.free(idRemove)
                    time1 = time.time()
                    # Add allocation time
                    freeTime.append(time1 - time0)
                    # Remove id from list
                    blockIDs.remove(idRemove)

            # Try to allocate some blocks
            nbAdd = randint(1, 50)
            for i in range(nbAdd):
                # Allocate block
                time0 = time.time()
                id = self.alloc(BSIZE, TYPE, data=data)
                time1 = time.time()
                # Add allocation time
                allocTime.append(time1-time0)
                # Store block ID
                blockIDs.append(id)

        # display FS
        self.display()

        # Compute min, max and average of times
        summ = round(1000*sum(allocTime), 2)
        mini = round(1000*min(allocTime), 2)
        maxi = round(1000*max(allocTime), 2)
        avrg = round(1000*sum(allocTime)/len(allocTime), 2)
        print(f"ALLOC : N={len(allocTime)}")
        print(f"    sum={summ} mini={mini}ms maxi={maxi}ms average={avrg}ms")

        # Compute min, max and average of times
        summ = round(1000 * sum(freeTime),2)
        mini = round(1000*min(freeTime), 2)
        maxi = round(1000*max(freeTime), 2)
        avrg = round(1000*sum(freeTime)/len(freeTime), 2)
        print(f"FREE  : N={len(freeTime)}")
        print(f"    sum={summ} mini={mini}ms maxi={maxi}ms average={avrg}ms")


    def test001(self):

        # Create small blocks until the memory is full
        BSIZE   = 4
        TYPE    = 1
        RETESTS = 1
        data    = [10 + i for i in range(BSIZE)]
        results = {}
        for data2 in [None, data]:
            for NB_SPRITES in [1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192]:
                for retest in range(RETESTS):
                    # Clear buffers
                    self._clear()

                    print(f"TEST : nbSprites={NB_SPRITES} / write={data2==data}")
                    tps = 0
                    for i in range(NB_SPRITES):
                        time0 = time.time()
                        self.alloc(BSIZE, TYPE, data=data)
                        time1 = time.time()
                        tps += time1-time0
                    #tps = 1000*tps/NB_SPRITES
                    if not NB_SPRITES in results:
                        results[NB_SPRITES] = {"alloc":0, "write":0}
                    if data2 == None:
                        results[NB_SPRITES]["alloc"] += 1000*tps
                    else:
                        results[NB_SPRITES]["write"] += 1000*tps

        for sz in results:
            w = results[sz]["write"]
            a = results[sz]["alloc"]
            if results[sz]["write"] < results[sz]["alloc"]:
                results[sz]["alloc"] = w / RETESTS
                results[sz]["write"] = (a - w) / RETESTS
            else:
                results[sz]["alloc"] = a / RETESTS
                results[sz]["write"] = (w - a) / RETESTS

            print(results[sz])

        return

