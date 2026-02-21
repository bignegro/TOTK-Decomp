// Pseudocode: orig/pseudocode/0x000000710070096C_sub_710070096C.txt
// Hypothesis: test if pointer matches one of several singleton sentinels.

#include <stdint.h>

extern unsigned char *off_7104563400[1];
extern int64_t *off_7104563408;
extern unsigned char off_71042E47D0;

extern unsigned char *off_7104563410[1];
extern int64_t *off_7104563418;
extern unsigned char *off_7104563118;

extern unsigned char *off_71045630C0[1];
extern int64_t *off_71045630C8;
extern unsigned char *off_7104562268;

extern unsigned char *off_71045621C0[1];
extern int64_t *off_71045621C8;
extern unsigned char *off_7104559C58;

extern unsigned char *off_7104559B20[1];
extern int64_t *off_7104559B28;
extern unsigned char *off_7104559C60;

extern unsigned char *off_7104559C08[1];
extern int64_t *off_7104559C10;
extern unsigned char *off_7104557808;

extern int _cxa_guard_acquire(void *);
extern void _cxa_guard_release(void *);

static inline int64_t *ensure_ptr(unsigned char **guard, int64_t **slot, int64_t init) {
    if (guard && guard[0]) {
        unsigned char state = __atomic_load_n(guard[0], __ATOMIC_RELAXED);
        if ((state & 1) == 0) {
            if (_cxa_guard_acquire(guard[0])) {
                *slot = (int64_t *)init;
                _cxa_guard_release(guard[0]);
            }
        }
    }
    return slot ? *slot : 0;
}

int64_t sub_710070096C(int64_t result, int64_t *ptr) {
    int64_t *v3 = ensure_ptr(off_7104563400, &off_7104563408, (int64_t)&off_71042E47D0);
    if (ptr == v3) {
        return result;
    }

    int64_t *v5 = ensure_ptr(off_7104563410, &off_7104563418, (int64_t)(off_7104563118 + 16));
    if (ptr == v5) {
        return result;
    }

    int64_t *v7 = ensure_ptr(off_71045630C0, &off_71045630C8, (int64_t)(off_7104562268 + 16));
    if (ptr == v7) {
        return result;
    }

    int64_t *v9 = ensure_ptr(off_71045621C0, &off_71045621C8, (int64_t)(off_7104559C58 + 16));
    if (ptr == v9) {
        return result;
    }

    int64_t *v11 = ensure_ptr(off_7104559B20, &off_7104559B28, (int64_t)(off_7104559C60 + 16));
    if (ptr == v11) {
        return result;
    }

    int64_t *v13 = ensure_ptr(off_7104559C08, &off_7104559C10, (int64_t)(off_7104557808 + 16));
    if (ptr == v13) {
        return result;
    }

    return 0;
}
