// Pseudocode: orig/pseudocode/0x0000007100F52E9C_sub_7100F52E9C.txt
// Hypothesis: nested pointer accessor.

#include <stdint.h>

uint64_t sub_7100F52E9C(uint64_t a1) {
    uint64_t p1 = *(uint64_t *)(a1 + 8);
    uint64_t p2 = *(uint64_t *)(p1 + 8);
    return *(uint64_t *)(p2 + 504);
}
