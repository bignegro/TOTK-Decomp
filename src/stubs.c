// Link-time stubs for unresolved symbols.
// Replace these with real implementations as you decompile.

__attribute__((weak)) long long qword_7104597A78;

__attribute__((weak, naked)) void sub_7100000330(long long a1, long long a2, long long a3) {
    __asm__ volatile("ret");
}

__attribute__((weak)) long long *off_7104557768;
__attribute__((weak)) long long *off_7104557798;

__attribute__((weak)) void *nn_os_GetTlsValue(unsigned int slot)
    __asm__("_ZN2nn2os11GetTlsValueENS0_7TlsSlotE");
__attribute__((weak)) void *nn_os_GetTlsValue(unsigned int slot) {
    (void)slot;
    return 0;
}

__attribute__((weak)) unsigned char *off_7104558670[1];
__attribute__((weak)) unsigned long long *off_7104558678;
__attribute__((weak)) unsigned char *off_7104559A58;

__attribute__((weak)) int _cxa_guard_acquire(void *guard) {
    (void)guard;
    return 0;
}
__attribute__((weak)) void _cxa_guard_release(void *guard) {
    (void)guard;
}

__attribute__((weak)) int sub_71009572C0(unsigned long long a1, unsigned long long a2) {
    (void)a1;
    (void)a2;
    return 0;
}

__attribute__((weak)) void sub_7100C73C20(void *a1) {
    (void)a1;
}
__attribute__((weak)) void sub_7100957480(void *a1, unsigned long long a2) {
    (void)a1;
    (void)a2;
}
__attribute__((weak)) void sub_7100957520(void *a1, void *a2, void *a3, unsigned int a4) {
    (void)a1;
    (void)a2;
    (void)a3;
    (void)a4;
}
__attribute__((weak)) void sub_7100957644(void *a1, void *a2, void *a3, unsigned int a4) {
    (void)a1;
    (void)a2;
    (void)a3;
    (void)a4;
}
