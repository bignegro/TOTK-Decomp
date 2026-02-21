// Pseudocode: orig/pseudocode/0x0000007100794424_sub_7100794424.txt
// Hypothesis: refcounted release (virtual destructor at vtable+24).

#include <stdint.h>

uint64_t *sub_7100794424(uint64_t *obj) {
    if (obj && obj[1]) {
        uint64_t *ref = obj + 2;
        uint64_t prev = __atomic_fetch_sub(ref, 1, __ATOMIC_ACQ_REL);
        if (prev == 1) {
            uint64_t (**vt)(uint64_t *) = (uint64_t (**)(uint64_t *))(*(uint64_t *)obj + 24);
            return vt ? vt(obj) : obj;
        }
    }
    return obj;
}
