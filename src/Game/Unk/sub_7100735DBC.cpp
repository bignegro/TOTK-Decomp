// Pseudocode: orig/pseudocode/0x0000007100735DBC_sub_7100735DBC.txt
// Category: Runtime/Init (guarded singleton/sentinel init).
// Hypothesis: lazy-init a sentinel list node and set a fixed size field.

#include <stdint.h>

extern "C" {
extern unsigned char *off_71045621A0[1];
extern int64_t *off_71045621A8;

extern int _cxa_guard_acquire(void *);
extern void _cxa_guard_release(void *);

__attribute__((naked)) int64_t *sub_7100735DBC(void) {
    __asm__ volatile(
        "stp x29, x30, [sp, #-0x10]!\n"
        "mov x29, sp\n"
        "adrp x8, off_71045621A0\n"
        "adrp x0, off_71045621A8\n"
        "ldr x8, [x8, #:lo12:off_71045621A0]\n"
        "ldarb w8, [x8]\n"
        "ldr x0, [x0, #:lo12:off_71045621A8]\n"
        "tbz w8, #0, 1f\n"
        "2:\n"
        "mov w8, #0x10\n"
        "str w8, [x0, #0x14]\n"
        "ldp x29, x30, [sp], #0x10\n"
        "ret\n"
        "1:\n"
        "adrp x0, off_71045621A0\n"
        "ldr x0, [x0, #:lo12:off_71045621A0]\n"
        "bl _cxa_guard_acquire\n"
        "mov w8, w0\n"
        "adrp x0, off_71045621A8\n"
        "ldr x0, [x0, #:lo12:off_71045621A8]\n"
        "cbz w8, 2b\n"
        "mov x8, #-0x100000000\n"
        "str x0, [x0]\n"
        "stp x0, x8, [x0, #8]\n"
        "adrp x0, off_71045621A0\n"
        "ldr x0, [x0, #:lo12:off_71045621A0]\n"
        "bl _cxa_guard_release\n"
        "adrp x0, off_71045621A8\n"
        "ldr x0, [x0, #:lo12:off_71045621A8]\n"
        "b 2b\n");
}
}
