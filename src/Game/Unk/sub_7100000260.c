// IDA: sub_7100000260
// Calls sub_7100000330(a1, 0, qword_7104597A78) and returns 0.

extern void sub_7100000330(long long a1, long long a2, long long a3);
extern long long qword_7104597A78;

long long sub_7100000260(long long a1) {
    sub_7100000330(a1, 0, qword_7104597A78);
    return 0;
}
