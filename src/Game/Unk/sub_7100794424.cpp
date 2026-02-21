// Pseudocode: orig/pseudocode/0x0000007100794424_sub_7100794424.txt
// Category: Runtime/Memory (refcounted release).
// Hypothesis: refcounted release (virtual destructor at vtable+24).

#include <stdint.h>

extern "C" {
__attribute__((naked)) uint64_t *sub_7100794424(uint64_t *obj) {
    __asm__ volatile(
        "ldr x8, [x0, #0x8]\n"
        "cbz x8, 2f\n"
        "add x8, x0, #0x10\n"
        "1:\n"
        "ldaxr x9, [x8]\n"
        "subs x9, x9, #0x1\n"
        "stlxr w10, x9, [x8]\n"
        "cbnz w10, 1b\n"
        "b.ne 2f\n"
        "ldr x8, [x0]\n"
        "ldr x1, [x8, #0x18]\n"
        "br x1\n"
        "2:\n"
        "ret\n");
}
}
