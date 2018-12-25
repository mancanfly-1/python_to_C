#define PAGE_SIZE 4096
#define PCI_START 2684354560
#define PCI_END 4294967296
#define NPAGE 8192
#define NDMAPAGE 512
#define NPROC 64
#define NOFILE 16
#define NFILE 128
#define NPCIDEV 64
#define NINTREMAP 8
typedef unsigned long long int size_t
typedef unsigned long long int uint64_t
typedef unsigned long int uint32_t
typedef unsigned int uint16_t
typedef unsigned char uint8_t
typedef unsigned long long int ssize_t
typedef unsigned long long int int64_t
typedef unsigned long int int32_t
typedef unsigned int int16_t
typedef unsigned char int8_t
typedef unsigned long long int pn_t
typedef unsigned long long int dmapn_t
typedef unsigned long long int fn_t
typedef unsigned long int fd_t
typedef unsigned long long int pte_t
typedef unsigned long long int dmar_pte_t
typedef unsigned long long int pid_t
typedef unsigned long long int off_t
typedef unsigned int devid_t
typedef unsigned long long int uintptr_t
unsigned long int INITPID=1;
unsigned long long int MAX_INT64=123;
struct PCI{
	pid_t owner;
	pn_t page_table_root;
};
struct Vectors{
	pid_t owner;
};
struct IO{
	pid_t owner;
};
struct Intremap{
	intremap_state_t state;
	devid_t devid;
	uint8_t vector;
};
struct Page{
	uint64_t data;
	pid_t owner;
	page_type_t type;
	uint64_t pgtable_pn;
	uint64_t pgtable_perm;
	uint64_t pgtable_type;
	pn_t pgtable_reverse_pn;
	pn_t pgtable_reverse_idx;
};
