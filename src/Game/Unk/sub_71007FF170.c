// Pseudocode: orig/pseudocode/0x00000071007FF170_sub_71007FF170.txt
// Hypothesis: allocate via explicit allocator or TLS allocator fallback.

#include <stddef.h>
#include <stdint.h>

extern uint64_t *off_7104557768;
extern uint64_t *off_7104557798;
extern void *nn_os_GetTlsValue(unsigned int slot)
    __asm__("_ZN2nn2os11GetTlsValueENS0_7TlsSlotE");

extern void *aligned_alloc(unsigned int size);

typedef struct AllocatorVtable {
    void *pad0[6];
    void *(*alloc)(void *self, size_t size, unsigned int align);
} AllocatorVtable;

static void *alloc_with_allocator(void *alloc, size_t size, unsigned int align) {
    if (!alloc) {
        return 0;
    }
    AllocatorVtable **vt = (AllocatorVtable **)alloc;
    if (!vt || !*vt || !(*vt)->alloc) {
        return 0;
    }
    return (*vt)->alloc(alloc, size, align);
}

void *sub_71007FF170(size_t size, void *alloc, unsigned int align) {
    uint64_t base = off_7104557768 ? *off_7104557768 : 0;
    if (!base) {
        return aligned_alloc((unsigned int)align);
    }
    if (alloc) {
        return alloc_with_allocator(alloc, size, align);
    }

    uint64_t tls = 0;
    if (off_7104557798 && *off_7104557798) {
        unsigned int slot = *(unsigned int *)(*off_7104557798 + 72);
        tls = (uint64_t)nn_os_GetTlsValue(slot);
    }

    uint64_t *slot_ptr = (uint64_t *)(base + 8);
    if (tls) {
        slot_ptr = (uint64_t *)(tls + 136);
    }

    alloc = (void *)*slot_ptr;
    if (alloc) {
        return alloc_with_allocator(alloc, size, align);
    }
    return 0;
}
