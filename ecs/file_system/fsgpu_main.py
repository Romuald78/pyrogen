import math
import time
from array import array
from random import choice, randint

from .fsgpu_buffer import FsGpuBuffer


class FsGpuMain():

    USE_LOCAL_FS_BUFFER = False

    __slots__ = ['_pageShift',
                 '_maxPages',
                 '_pageSize',
                 '_pageMask',
                 '_nbPages',
                 '_nbComp',
                 '_ctx',
                 '_texture',
                 '_pages',
                ]

    # ----------------------------------------------------
    # CONSTRUCTOR
    # ----------------------------------------------------
    def __init__(self, ctx, pageSize, nbPages):
        # pageShift is the number of bits to code the pageSize
        # 18 means the page size can be 128kB = 32kB texture width
        # We store the page number on the 14 remaining bits (to stay in unsigned 32 bits range)
        self._pageShift = 18
        self._pageMask  = (1 << (32 - self._pageShift)) - 1
        self._maxPages  = math.pow(2, 32-self._pageShift)
        # Either page size cannot be more than 2^pageShift
        if pageSize > math.pow(2, self._pageShift):
            raise RuntimeError(f"[ERROR] bad page size : size={pageSize} is too big. Do not use more than {math.pow(2, self._pageShift)} !")
        if nbPages > self._maxPages:
            raise RuntimeError(f"[ERROR] bad NB pages : nbPages={nbPages} maxPages={self._maxPages} pageSize={pageSize} !")

        # Each page is a FsGpuBuffer instance
        self._pageSize = pageSize
        self._nbPages  = nbPages
        self._nbComp   = 4
        # Store gl context
        self._ctx = ctx
        # init buffers and texture
        self._clear()


    # ----------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------
    def getMaxPages(self):
        return self._maxPages
    def getNbPages(self):
        return self._nbPages
    def getPageSize(self):
        return self._pageSize
    def getTotalSize(self):
        return self._pageSize * self._nbPages
    def getTexture(self):
        return self._texture


    # ----------------------------------------------------
    # PRIVATE METHODS
    # ----------------------------------------------------
    def _clear(self):
        # create buffers
        self._pages = [FsGpuBuffer(self._pageSize) for N in range(self._nbPages)]

        # Create texture from context
        print(f"Create texture W={self._pageSize} H={self._nbPages} C={self._nbComp}")
        self._texture = self._ctx.texture((self._pageSize, self._nbPages), self._nbComp, dtype="f4")

    def _isPageOK(self, pageNum):
        return pageNum >= 0 and pageNum < self._nbPages

    def _createID(self, offset, page):
        return int((page << self._pageShift) + offset)

    def _explodeID(self, id):
        offMask  = (1 << self._pageShift) - 1
        offset   = id & offMask
        page     = (id >> self._pageShift) & self._pageMask
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
            self.write2Texture(id, data)
        # return block ID
        return id

    def free(self, blockID):
        # retrieve block position information
        offset, page = self._explodeID(blockID)
        if not self._isPageOK(page):
            raise RuntimeError(f"[ERROR] bad page value from block ID ! id={blockID} - page={page} - offset={offset}")
        # Now free this block from the memory
        self._pages[page].free(offset)


    def readFromTexture(self, id):
        # retrieve block position information
        offset, page = self._explodeID(id)
        # Get data from texture (GPU)
        gpuData = 0 # TODO : retrieve data from texture directly (is this method useful ?
                    # TODO : as there is alreasdy the Sprite instances that contain everything ?
        # Get block data (local CPU buffer)
        if FsGpuMain.USE_LOCAL_FS_BUFFER :
            cpuData = self._pages[page].read(offset)
            # compare gpuData and cpuData to be sure there is no issue somewhere in the dataflow
            # TODO

    def write2Texture(self, id, data):
        # retrieve block position information
        offset, page = self._explodeID(id)
        # Write into the CPU array.array (that is a CPU copy of the file system)
        if FsGpuMain.USE_LOCAL_FS_BUFFER :
            self._pages[page].write(offset, data)
        # write block data directly to texture
        offset = (offset + FsGpuBuffer.OVERHEAD)//self._nbComp
        self._texture.write(data, viewport=(offset, page, len(data)//self._nbComp, 1))


    # ----------------------------------------------------
    # APP PROCESS
    # ----------------------------------------------------
    def update(self, deltaTime):

        # ~~~~~~~~~~~~~~~~~~~~~~~~
        # We will call the page buffer defrag process, and according
        # to the frame time, we will see how many pages we can defrag in-a-row
        # ~~~~~~~~~~~~~~~~~~~~~~~~
        # TODO : For the moment we only defrag one page
        # TODO : improve defrag process (or algorithm underneath) because it drops the perfs !!
#        for page in self._pages:
#            res = page.defrag()
#            if res:
#                break

        # ~~~~~~~~~~~~~~~~~~~~~~~~
        # Browse all buffers and check their 'modified' property
        # copy the buffer data into the texture and call resetModify()
        # when finished
        # ~~~~~~~~~~~~~~~~~~~~~~~~
        # As there is a way to fill data from the bottom page of the FS
        # this could be efficient to put all static blocks at the end of the
        # memory, and the static ones at the beginning

        # TODO : may be force a page to allocate blocks, in order to handle
        # which pages are willing to be modified or not
        # TODO : this process can be improved by getting the small parts
        #        of the buffers that have been modified, instead of rewriting
        #        the whole buffer
        i = 0
        while i < self._nbPages:
            p = self._pages[i]
            if p.isModified():
                # print(f"[FS GPU] Writing page #{i} into the GPU texture")
                # write this page into the texture
#                self._texture.write(p.getData(), viewport=(0, i, self._pageSize, 1))
                # buffer has been updated into the texture
                # reset flag
                p.resetModify()
            # print(f"PAGE WRITE = {lap2-lap1}")
            i += 1

    def render(self):
        pass


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
            out += f"================= modified={page.isModified()} =================" + "\n"
            out +=  "=================================================" + "\n"
            i += 1
            out += page.dump(displayData)

        out += "\n"
        return out


    # ----------------------------------------------------
    # TESTS
    # ----------------------------------------------------
    def test002(self):
        TEST_NUMS = [10,20,50,100,200,500,1000,2000,5000,10000,20000]
        BSIZE = 8
        TYPE  = 1
        data = [10 + i for i in range(BSIZE)]
        results = []
        results.append("Nalloc\tTalloc\tNfree\tTfree")
        for T in TEST_NUMS:
            # Init buffers
            allocTime = []
            freeTime = []
            blockIDs = []
            self._clear()

            # Perform tests
            print("------------------------------------")
            for N in range(T):
                # Defrag FS
                self.update(1/60)

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
            #self.display()

            res = ""
            # Compute min, max and average of times
            summ = round(1000 * sum(allocTime), 2)
            mini = round(1000 * min(allocTime), 2)
            maxi = round(1000 * max(allocTime), 2)
            avrg = round(1000 * sum(allocTime)/len(allocTime), 2)
            res += f"{len(allocTime)}\t{summ}\t"
            print(f"ALLOC : N={len(allocTime)}")
            print(f"    sum={summ}ms mini={mini}ms maxi={maxi}ms average={avrg}ms")
            # Compute min, max and average of times
            summ = round(1000 * sum(freeTime), 2)
            mini = round(1000 * min(freeTime), 2)
            maxi = round(1000 * max(freeTime), 2)
            avrg = round(1000 * sum(freeTime)/len(freeTime), 2)
            res += f"{len(freeTime)}\t{summ}\t"
            print(f"FREE  : N={len(freeTime)}")
            print(f"    sum={summ} mini={mini}ms maxi={maxi}ms average={avrg}ms")
            res = res.replace(".",",")
            results.append(res)

        print()
        print("====================================")
        for r in results:
            print(r)