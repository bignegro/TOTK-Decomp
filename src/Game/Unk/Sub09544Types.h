// Inferred types for sub_7100954470.
// These are placeholders and will be refined as the function is decompiled.
#pragma once

#include <stddef.h>
#include <stdint.h>

typedef struct AllocatorVTable {
    uint64_t pad_0[6];
    void *(*alloc)(void *self, size_t size, size_t align);
} AllocatorVTable;

typedef struct Allocator {
    AllocatorVTable *vtable;
} Allocator;

typedef struct AllocatorHolder {
    uint64_t pad_0;
    Allocator *allocator;
} AllocatorHolder;

typedef struct Sub09544Entry {
    uint32_t count;      // +0
    uint32_t pad_4;
    void *data;          // +8
    uint16_t field_16;   // +16
    uint16_t pad_18;
    uint32_t pad_1c;
} Sub09544Entry;

typedef struct Sub09544Bucket {
    uint64_t entry;  // +0
    uint32_t count;  // +8
    uint32_t pad_c;  // +12
    uint64_t filters; // +16
} Sub09544Bucket;

typedef struct Sub09544ShapeInfo {
    uint8_t pad_0[4];
    uint8_t flags;
    uint8_t pad_5[93];
    uint16_t field_98;
    uint16_t field_100;
    uint16_t field_102;
    uint16_t field_104;
    uint16_t field_108;
} Sub09544ShapeInfo;

typedef struct Sub09544ShapeEntry {
    Sub09544ShapeInfo *info; // +0
    uint8_t pad_8[24];
} Sub09544ShapeEntry;

typedef struct Sub09544Context {
    uint8_t pad_0[8];       // +0
    uint32_t entry_count;   // +8
    uint32_t pad_c;
    Sub09544Entry *entries; // +16
    uint8_t pad_18[72 - 24];
    uint32_t field_72;      // +72
    uint32_t pad_76;
    void *field_80;         // +80
    uint8_t pad_88[144 - 88];
    uint32_t field_144;     // +144
    uint32_t pad_148;
    void *field_152;        // +152
    uint32_t bucket_count;  // +160
    uint32_t pad_164;
    Sub09544Bucket *buckets; // +168
    uint16_t field_176;     // +176
    uint16_t field_178;     // +178
    uint16_t field_180;     // +180
    uint16_t field_182;     // +182
    uint16_t field_184;     // +184
    uint16_t field_186;     // +186
    uint8_t pad_188[216 - 188];
    uint32_t list_count;    // +216
    uint32_t list_cap;      // +220
    void **list_ptr;        // +224
    uint8_t pad_232[240 - 232];
    uint32_t max_records;   // +240
    uint8_t pad_244[2];
    uint16_t max_metric_a;  // +246
    uint16_t max_metric_b;  // +248
    uint16_t field_250;     // +250
} Sub09544Context;

typedef struct Sub09544Data {
    uint8_t pad_0[16];
    uint32_t field_16;
    uint8_t pad_20[24 - 20];
    void *field_24;
    uint32_t field_32;
    uint32_t pad_36;
    void *field_40;
    uint8_t pad_48[584 - 48];
    uint16_t field_584;
} Sub09544Data;

typedef struct Sub09544Opts {
    uint8_t pad_0[4];
    uint32_t field_4;
    uint32_t field_8;
    uint8_t pad_12[1];
    uint8_t field_13;
    uint8_t field_14;
    uint8_t pad_15[1];
    void *field_16;
} Sub09544Opts;
