// Large-function reimplementation (partial).
// Source pseudocode: orig/pseudocode_sub_7100954470.txt
// Hypothesis: builds internal tables from a list of objects, computing two
// per-object maxima (vtable+48, vtable+200) and allocating per-entry buffers.
// TODO: finish translating the remaining body into clean C/C++.

#include "Sub09544Types.h"

extern long long *off_7104557768;
extern long long *off_7104557798;
extern unsigned char *off_7104558670[];
extern unsigned long long *off_7104558678;
extern unsigned char *off_7104559A58;

extern void *nn_os_GetTlsValue(unsigned int slot)
    __asm__("_ZN2nn2os11GetTlsValueENS0_7TlsSlotE");
extern int _cxa_guard_acquire(void *);
extern void _cxa_guard_release(void *);

extern int sub_71009572C0(unsigned long long a1, unsigned long long a2);
extern void sub_7100C73C20(void *a1);
extern void sub_7100957480(void *a1, unsigned long long a2);
extern void sub_7100957520(void *a1, void *a2, void *a3, unsigned int a4);
extern void sub_7100957644(void *a1, void *a2, void *a3, unsigned int a4);

static void *alloc_aligned_fallback(size_t size, size_t align) {
    (void)align;
    (void)size;
    return 0;
}

static Allocator *get_tls_allocator(AllocatorHolder *holder) {
    if (holder && holder->allocator) {
        return holder->allocator;
    }
    if (!off_7104557768 || !*off_7104557768) {
        return 0;
    }
    uint8_t *global_base = (uint8_t *)(*off_7104557768);
    uint8_t *tls_base = 0;
    if (off_7104557798 && *off_7104557798) {
        unsigned int slot = *(unsigned int *)((uint8_t *)(*off_7104557798) + 72);
        tls_base = (uint8_t *)nn_os_GetTlsValue(slot);
    }
    Allocator **slot_ptr = (Allocator **)(global_base + 8);
    if (tls_base) {
        slot_ptr = (Allocator **)(tls_base + 136);
    }
    return *slot_ptr;
}

static void *alloc_with_allocator(AllocatorHolder *holder, size_t size, size_t align) {
    if (off_7104557768 && *off_7104557768) {
        Allocator *alloc = get_tls_allocator(holder);
        if (alloc && alloc->vtable && alloc->vtable->alloc) {
            return alloc->vtable->alloc(alloc, size, align);
        }
    }
    return alloc_aligned_fallback(size, align);
}

static inline void atomic_inc_u32(volatile uint32_t *ptr) {
    __atomic_fetch_add(ptr, 1, __ATOMIC_RELAXED);
}

static void init_obj_list(Sub09544Context *ctx, void **src, int count, AllocatorHolder *holder) {
    if (count < 1) {
        return;
    }
    void *mem = alloc_with_allocator(holder, (size_t)count * 8u, 8);
    if (mem) {
        ctx->list_ptr = (void **)mem;
        ctx->list_count = 0;
        ctx->list_cap = (uint32_t)count;
    }
    for (int i = 0; i < count; ++i) {
        uint32_t idx = ctx->list_count;
        if ((int)idx < (int)ctx->list_cap) {
            ctx->list_ptr[idx] = src[i];
            ++ctx->list_count;
        }
        atomic_inc_u32((volatile uint32_t *)((uint8_t *)src[i] + 696));
    }
}

static void init_entries(Sub09544Context *ctx, Sub09544Data *data, AllocatorHolder *holder, unsigned int *counts) {
    uint32_t entry_count = data->field_32;
    if ((int)entry_count < 1) {
        return;
    }
    Sub09544Entry *entries = (Sub09544Entry *)alloc_with_allocator(holder, (size_t)entry_count * 24u, 8);
    if (entries) {
        for (uint32_t i = 0; i < entry_count; ++i) {
            entries[i].count = 0;
            entries[i].data = 0;
        }
        ctx->entry_count = entry_count;
        ctx->entries = entries;
    }

    if (!ctx->entry_count) {
        return;
    }

    for (uint32_t i = 0; i < ctx->entry_count; ++i) {
        uint32_t want = *counts;
        if ((int)want < 1) {
            ctx->entries[i].field_16 = 0;
            continue;
        }
        void *buf = alloc_with_allocator(holder, (size_t)want * 2u, 8);
        if (buf) {
            ctx->entries[i].count = want;
            ctx->entries[i].data = buf;
            for (uint32_t j = 0; j < want; ++j) {
                ((uint16_t *)ctx->entries[i].data)[j] = 0;
            }
        } else {
            if ((int)ctx->entries[i].count >= 1) {
                for (uint32_t j = 0; j < ctx->entries[i].count; ++j) {
                    ((uint16_t *)ctx->entries[i].data)[j] = 0;
                }
            }
            ctx->entries[i].field_16 = 0;
        }
    }
}

static inline uint16_t min_u16_u32(uint16_t a, uint32_t b) {
    return (uint32_t)a < b ? a : (uint16_t)b;
}

static uint32_t call_vfunc_u32(void *obj, size_t vtable_offset) {
    if (!obj) {
        return 0;
    }
    void **vtable = *(void ***)obj;
    if (!vtable) {
        return 0;
    }
    size_t index = vtable_offset / sizeof(void *);
    uint32_t (*fn)(void *) = (uint32_t (*)(void *))vtable[index];
    return fn ? fn(obj) : 0;
}

static uint16_t compute_max_metric(Sub09544Data *data, size_t vtable_offset) {
    uint16_t limit = min_u16_u32(data->field_584, data->field_16);
    if (!limit) {
        return 0;
    }
    uint8_t *cursor = (uint8_t *)data->field_24;
    uint16_t max_value = 0;
    for (uint16_t i = 0; i < limit; ++i) {
        void *obj = *(void **)cursor;
        uint32_t value = call_vfunc_u32(obj, vtable_offset);
        if (max_value <= value) {
            max_value = (uint16_t)value;
        }
        cursor += 56;
    }
    return max_value;
}

static uint16_t get_obj_u16(void *obj, size_t index) {
    return ((uint16_t *)obj)[index];
}

static uint32_t sum_obj_fields(Sub09544Context *ctx, uint32_t sums[6]) {
    for (int i = 0; i < 6; ++i) {
        sums[i] = 0;
    }
    uint32_t count = ctx->list_count;
    for (uint32_t i = 0; i < count; ++i) {
        void *obj = ctx->list_ptr[i];
        sums[0] += get_obj_u16(obj, 52);
        sums[1] += get_obj_u16(obj, 53);
        sums[2] += get_obj_u16(obj, 54);
        sums[3] += get_obj_u16(obj, 55);
        sums[4] += get_obj_u16(obj, 56);
        sums[5] += get_obj_u16(obj, 57);
    }
    return sums[0] + sums[1] + sums[2] + sums[3] + sums[4] + sums[5];
}

static void init_buckets(Sub09544Context *ctx, uint32_t total, AllocatorHolder *holder) {
    if (!total) {
        return;
    }
    Sub09544Bucket *buckets =
        (Sub09544Bucket *)alloc_with_allocator(holder, (size_t)total * sizeof(Sub09544Bucket), 8);
    if (!buckets) {
        return;
    }
    for (uint32_t i = 0; i < total; ++i) {
        buckets[i].entry = 0;
        buckets[i].count = 0;
        buckets[i].filters = 0;
    }
    ctx->bucket_count = total;
    ctx->buckets = buckets;
}

static void update_shape_bounds(Sub09544ShapeInfo *shape, uint64_t stats[4]) {
    uint16_t v98 = shape->field_98;
    if ((uint32_t)stats[0] >= v98) {
        v98 = (uint16_t)stats[0];
    }
    stats[0] = (stats[0] & 0xFFFFFFFF00000000ULL) | v98;

    uint16_t v104 = shape->field_104;
    uint16_t v102 = shape->field_102;
    uint32_t sum_104_102 = (uint32_t)(v104 + v102);
    if ((int)(uint32_t)stats[1] >= (int)sum_104_102) {
        sum_104_102 = (uint32_t)stats[1];
    }
    stats[1] = (stats[1] & 0xFFFFFFFF00000000ULL) | sum_104_102;

    uint16_t v100 = shape->field_100;
    if ((int)(uint32_t)stats[2] >= (int)v100) {
        v100 = (uint16_t)stats[2];
    }
    stats[2] = (stats[2] & 0xFFFFFFFF00000000ULL) | v100;

    uint16_t v108 = shape->field_108;
    if ((int)(uint32_t)(stats[1] >> 32) >= (int)v108) {
        v108 = (uint16_t)(stats[1] >> 32);
    }
    stats[1] = (stats[1] & 0xFFFFFFFFULL) | ((uint64_t)v108 << 32);

    stats[2] |= ((shape->flags & 1) == 0) ? (1ULL << 40) : 0;
}

static inline Sub09544ShapeEntry *get_obj_shapes(void *obj) {
    return *(Sub09544ShapeEntry **)((uint8_t *)obj + 56);
}

static inline Sub09544ShapeInfo *get_shape_info(Sub09544ShapeEntry *entry) {
    return entry ? entry->info : 0;
}

static void ensure_global_8678(void) {
    if (!off_7104558670[0]) {
        return;
    }
    unsigned char state = __atomic_load_n(off_7104558670[0], __ATOMIC_RELAXED);
    if ((state & 1) == 0 && _cxa_guard_acquire(off_7104558670[0])) {
        if (off_7104558678) {
            *off_7104558678 = (unsigned long long)(off_7104559A58 + 16);
        }
        _cxa_guard_release(off_7104558670[0]);
    }
}

static uint32_t collect_filters(
    Sub09544Data *data,
    Sub09544ShapeEntry *entry,
    int max_filters,
    int *out_indices,
    int out_capacity
) {
    if (!data || !entry || max_filters <= 0) {
        return 0;
    }
    uint32_t count = 0;
    for (int i = 0; i < max_filters; ++i) {
        void **fn_table = (void **)data->field_40;
        void *filter = 0;
        if (fn_table) {
            filter = *(void **)((uint8_t *)fn_table + 8 * i);
        }
        if (filter) {
            ensure_global_8678();
            void *result = (*(void ***)filter)[0]
                ? ((void *(*)(void *, void *))(*(void ***)filter)[0])(filter, off_7104558678)
                : 0;
            if (result) {
                unsigned long long rhs = *(unsigned long long *)(*(unsigned long long *)(*(unsigned long long *)((uint8_t *)result + 312) + 96));
                if (sub_71009572C0((unsigned long long)entry, rhs) & 1) {
                    if (count < (uint32_t)out_capacity) {
                        out_indices[count++] = i;
                    }
                }
            }
        }
    }
    return count;
}

long long sub_7100954470(
    Sub09544Context *ctx,
    void **src,
    long long a3,
    int count,
    unsigned int *counts,
    Sub09544Data *data,
    Sub09544Opts *opts,
    AllocatorHolder *holder
) {
    (void)a3;
    (void)opts;

    init_obj_list(ctx, src, count, holder);
    init_entries(ctx, data, holder, counts);

    ctx->max_metric_a = compute_max_metric(data, 48);
    ctx->max_metric_b = compute_max_metric(data, 200);

    if (counts[1] && ctx->max_metric_b) {
        uint32_t sums[6];
        uint32_t total = sum_obj_fields(ctx, sums);
        if (total) {
            ctx->field_176 = (uint16_t)sums[0];
            ctx->field_178 = (uint16_t)(sums[0] + sums[1]);
            ctx->field_180 = (uint16_t)(sums[0] + sums[1] + sums[2]);
            ctx->field_182 = (uint16_t)(sums[0] + sums[1] + sums[2] + sums[3]);
            ctx->field_184 =
                (uint16_t)(sums[0] + sums[1] + sums[2] + sums[3] + sums[4]);
            ctx->field_186 =
                (uint16_t)(sums[0] + sums[1] + sums[2] + sums[3] + sums[4] + sums[5]);
            init_buckets(ctx, total, holder);

            if (ctx->field_176) {
                uint64_t stats[4];
                uint64_t scratch[1536];
                int tmp_indices[3072];

                for (size_t z = 0; z < 1536; ++z) {
                    scratch[z] = 0;
                }
                stats[0] = ((uint64_t)ctx->max_metric_b << 32);
                stats[1] = (uint64_t)-1;
                stats[2] = (uint64_t)-1;
                stats[3] = 0;

                uint32_t obj_count = ctx->list_count;
                uint32_t shape_index = 0;
                for (uint32_t i = 0; i < obj_count; ++i) {
                    uint8_t *obj = (uint8_t *)ctx->list_ptr[i];
                    uint32_t count = get_obj_u16(obj, 52);
                    if (!count) {
                        continue;
                    }
                    Sub09544ShapeEntry *shapes = get_obj_shapes(obj);
                    for (uint32_t j = 0; j < count; ++j) {
                        Sub09544ShapeEntry *entry = (Sub09544ShapeEntry *)((uint8_t *)shapes + 32u * j);
                        Sub09544ShapeInfo *shape = get_shape_info(entry);
                        if (shape) {
                            update_shape_bounds(shape, stats);
                        }

                        uint32_t bucket_index = ctx->bucket_count <= shape_index ? 0 : shape_index;
                        Sub09544Bucket *bucket = &ctx->buckets[bucket_index];
                        bucket->entry = (uint64_t)entry;

                        if (ctx->entry_count < 1) {
                            continue;
                        }

                        uint32_t match_count =
                            collect_filters(data, entry, (int)data->field_32, tmp_indices, 3072);
                        if (match_count) {
                            uint16_t *out = (uint16_t *)alloc_with_allocator(
                                holder, (size_t)match_count * sizeof(uint16_t), 8);
                            if (out) {
                                bucket->count = match_count;
                                bucket->filters = (uint64_t)out;
                            }
                        }

                        if (bucket->count) {
                            uint16_t *out = (uint16_t *)bucket->filters;
                            uint32_t to_copy = bucket->count;
                            for (uint32_t k = 0; k < to_copy; ++k) {
                                out[k] = (uint16_t)tmp_indices[k];
                            }
                        }
                        ++shape_index;
                    }
                }

                sub_7100C73C20(scratch);
                if ((uint32_t)scratch[3] >= ctx->max_records) {
                    ctx->max_records = (uint32_t)scratch[3];
                }
            }
        }
    }

    // TODO: continue translating the rest of the function body.
    return 0;
}
