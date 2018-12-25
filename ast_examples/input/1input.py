PAGE_SIZE = 4096

PCI_START = 0xa0000000
PCI_END =   0x100000000
# page number 
NPAGE = 8192
NDMAPAGE = 512
NPROC = 64
# NTSLICE
# max opend file
NOFILE = 16
# max file number
NFILE = 128
# max device number
NPCIDEV = 64
# max intermap number, what is used for?
NINTREMAP = 8

#NPCIPAGE = (PCI_END - PCI_START) / PAGE_SIZE

# use z3py type define c type.
bool_t = z3.BoolSort()

size_t = z3.BitVecSort(64)
uint64_t = z3.BitVecSort(64)
uint32_t = z3.BitVecSort(32)
uint16_t = z3.BitVecSort(16)
uint8_t = z3.BitVecSort(8)


ssize_t = z3.BitVecSort(64)
int64_t = z3.BitVecSort(64)
int32_t = z3.BitVecSort(32)
int16_t = z3.BitVecSort(16)
int8_t = z3.BitVecSort(8)
#int = int32_t

#page number
pn_t = z3.BitVecSort(64)
# dma page number
dmapn_t = z3.BitVecSort(64)
# file number
fn_t = z3.BitVecSort(64)    #typedef uint64_t fn_t;    /* file number */
# file descriptor
fd_t = z3.BitVecSort(32)
# page table entry
pte_t = z3.BitVecSort(64)
dmar_pte_t = z3.BitVecSort(64)
# process id
pid_t = z3.BitVecSort(64)
# ???
off_t = z3.BitVecSort(64)
# device id
devid_t = z3.BitVecSort(16)
# ????
uintptr_t = z3.BitVecSort(64)
# physicall address
#physaddr_t = uintptr_t
# initial process id
INITPID = z3.BitVecVal(1, 32)

MAX_INT64 = z3.BitVecVal(123, 64)

class PCI(Struct):
    owner = Map(devid_t, pid_t)                         # device's process id
    page_table_root = Map(devid_t, pn_t)                # device's page table root


class Vectors(Struct):
    owner = Map(uint8_t, pid_t)                         # interupt vector number corresponding process


class IO(Struct):
    owner = Map(uint16_t, pid_t)                        # IO port to process id.


class Intremap(Struct):                                 # interrupt remmaping
    state = Map(size_t, intremap_state_t)               # 
    devid = Map(size_t, devid_t)
    vector = Map(size_t, uint8_t)                       # address to vector number.


class Page(Struct):
    data = Map(pn_t, uint64_t, uint64_t)                # page num & index --> data; data = page number(52 bit) + permission(12 bit);
    owner = Map(pn_t, pid_t)                            # page --> pid
    type = Map(pn_t, page_type_t)                       # page's type
    pgtable_pn = Map(pn_t, uint64_t, uint64_t)          # (pn, index, pn), i.e.,page number that the page of page table entry i corresponding to .
    pgtable_perm = Map(pn_t, uint64_t, uint64_t)		# (pn, index, perm) page permission that the page of page table entry i corresponding to .
    pgtable_type = Map(pn_t, uint64_t, uint64_t)		# (pn, index, type) page type that the page of page table entry i corresponding to .

    pgtable_reverse_pn = Map(pn_t, pn_t)				# shadow page table
    pgtable_reverse_idx = Map(pn_t, pn_t)				# the front page's page table entry's index.

