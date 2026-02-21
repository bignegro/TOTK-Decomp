// Pseudocode: orig/pseudocode/0x0000007100701F98_sub_7100701F98.txt
// Hypothesis: intrusive list insert (head).

#include <stdint.h>

typedef struct HNode {
    struct HNode *next;
    struct HNode **pprev;
} HNode;

HNode **sub_7100701F98(HNode **head, HNode *node) {
    HNode *old = *head;
    *head = node;
    node->next = old;
    node->pprev = head;
    if (old) {
        old->pprev = &node->next;
    }
    return head;
}
