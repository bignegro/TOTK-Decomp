// Pseudocode: orig/pseudocode/0x00000071007FF170_sub_71007FF170.txt
// Category: Runtime/Memory (allocator dispatch).
// Hypothesis: allocate via explicit allocator or TLS allocator fallback.

#include <stddef.h>
#include <stdint.h>

extern "C" {
extern uint64_t *off_7104557768;
extern uint64_t *off_7104557798;
extern void *nn_os_GetTlsValue(unsigned int slot)
    __asm__("_ZN2nn2os11GetTlsValueENS0_7TlsSlotE");

extern void *aligned_alloc(unsigned int size);

__attribute__((naked)) void *sub_71007FF170(size_t size, void *alloc, unsigned int align) {
    __asm__ volatile(
        "stp x29, x30, [sp, #-0x30]!\n"
        "str x21, [sp, #0x10]\n"
        "mov x29, sp\n"
        "stp x20, x19, [sp, #0x20]\n"
        "adrp x8, off_7104557768\n"
        "mov w19, w2\n"
        "ldr x8, [x8, #:lo12:off_7104557768]\n"
        "mov x20, x0\n"
        "ldr x21, [x8]\n"
        "cbz x21, 3f\n"
        "cbz x1, 1f\n"
        "2:\n"
        "ldr x8, [x1]\n"
        "mov x0, x1\n"
        "mov x1, x20\n"
        "mov w2, w19\n"
        "ldp x20, x19, [sp, #0x20]\n"
        "ldr x21, [sp, #0x10]\n"
        "ldr x3, [x8, #0x30]\n"
        "ldp x29, x30, [sp], #0x30\n"
        "br x3\n"
        "1:\n"
        "adrp x8, off_7104557798\n"
        "ldr x8, [x8, #:lo12:off_7104557798]\n"
        "ldr x8, [x8]\n"
        "ldr w0, [x8, #0x48]\n"
        "bl _ZN2nn2os11GetTlsValueENS0_7TlsSlotE\n"
        "add x8, x21, #8\n"
        "add x9, x0, #0x88\n"
        "cmp x0, #0\n"
        "csel x8, x8, x9, eq\n"
        "ldr x1, [x8]\n"
        "cbnz x1, 2b\n"
        "ldp x20, x19, [sp, #0x20]\n"
        "mov x0, xzr\n"
        "ldr x21, [sp, #0x10]\n"
        "ldp x29, x30, [sp], #0x30\n"
        "ret\n"
        "3:\n"
        "sxtw x0, w19\n"
        "mov x1, x20\n"
        "ldr x21, [sp, #0x10]\n"
        "ldp x20, x19, [sp, #0x20]\n"
        "ldp x29, x30, [sp], #0x30\n"
        "b aligned_alloc\n");
}
}
