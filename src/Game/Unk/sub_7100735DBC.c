// Pseudocode: orig/pseudocode/0x0000007100735DBC_sub_7100735DBC.txt
// Hypothesis: lazy-init a sentinel list node and set a fixed size field.

#include <stdint.h>

extern unsigned char *off_71045621A0[1];
extern int64_t *off_71045621A8;

extern int _cxa_guard_acquire(void *);
extern void _cxa_guard_release(void *);

int64_t *sub_7100735DBC(void) {
    int64_t *result = off_71045621A8;
    if (off_71045621A0[0]) {
        unsigned char state = __atomic_load_n(off_71045621A0[0], __ATOMIC_RELAXED);
        if ((state & 1) == 0) {
            if (_cxa_guard_acquire(off_71045621A0[0])) {
                result = off_71045621A8;
                result[0] = (int64_t)off_71045621A8;
                result[1] = (int64_t)result;
                result[2] = 0xFFFFFFFF00000000LL;
                _cxa_guard_release(off_71045621A0[0]);
                result = off_71045621A8;
            }
        }
    }
    ((uint32_t *)result)[5] = 16;
    return result;
}
