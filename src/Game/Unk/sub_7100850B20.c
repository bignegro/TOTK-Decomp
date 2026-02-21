// Pseudocode: orig/pseudocode/0x0000007100850B20_sub_7100850B20.txt
// Hypothesis: destructor/cleanup with refcount and external hooks.

#include <stdint.h>

extern uint64_t off_71044FA6F0;
extern uint64_t *off_7104557D28;

extern uint64_t sub_7100AF8500(void);
extern uint64_t sub_7100819CE8(uint64_t a1, uint64_t a2);
extern uint64_t sub_71006993F8(uint64_t a1, uint64_t a2);

uint64_t sub_7100850B20(uint64_t *a1) {
    uint64_t result = 0;

    a1[0] = off_71044FA6F0;

    uint64_t *slot = a1 + 5;
    result = a1[5];
    if (result) {
        for (;;) {
            uint64_t expected = result;
            if (__atomic_compare_exchange_n(slot, &expected, 0, 0, __ATOMIC_ACQ_REL, __ATOMIC_RELAXED)) {
                result = sub_7100AF8500();
                break;
            }
            if (expected != result) {
                break;
            }
        }
    }

    uint64_t v4 = a1[2];
    if (v4) {
        for (;;) {
            int state = *(int *)(v4 + 356);
            if (state == 1) {
                break;
            }
            int *state_ptr = (int *)(v4 + 356);
            int expected = state;
            if (__atomic_compare_exchange_n(state_ptr, &expected, state - 1, 0, __ATOMIC_ACQ_REL, __ATOMIC_RELAXED)) {
                goto finalize;
            }
            v4 = a1[2];
        }

        uint64_t mgr = off_7104557D28 ? *off_7104557D28 : 0;
        if (mgr) {
            uint64_t obj = *(uint64_t *)(mgr + 24);
            uint64_t (**vt)(uint64_t, uint64_t) = (uint64_t (**)(uint64_t, uint64_t))(*(uint64_t *)obj + 32);
            result = vt ? vt(obj, v4) : 0;
            if (result & 1) {
                *(uint8_t *)(*(int *)(v4 + 64) + *(uint64_t *)(v4 + 56) - 1) = 0;
                uint64_t len = *(uint64_t *)(v4 + 56);
                uint64_t (**vt2)(uint64_t) = (uint64_t (**)(uint64_t))(*(uint64_t *)(v4 + 336) + 96);
                uint64_t val = vt2 ? vt2(*(uint64_t *)(v4 + 336)) : 0;
                uint64_t key = sub_7100819CE8(len, val);
                result = sub_71006993F8(mgr + 96, key);
            }
        }

        int *state_ptr2 = (int *)(a1[2] + 356);
        for (;;) {
            int expected = __atomic_load_n(state_ptr2, __ATOMIC_RELAXED);
            if (expected != 1) {
                v4 = a1[2];
                if (v4) {
                    continue;
                }
                break;
            }
            if (__atomic_compare_exchange_n(state_ptr2, &expected, 0, 0, __ATOMIC_ACQ_REL, __ATOMIC_RELAXED)) {
                break;
            }
        }
finalize:
        a1[2] = 0;
    }

    return result;
}
