#include <iostream>
#include <cstdlib>
#include <cstdio>

using namespace std;

typedef struct _E {
	int val;
	struct _E *next;
}QueueNode;

typedef struct _Q {
	QueueNode *head;
	QueueNode *tail;
}Queue;

void enqueue(Queue *q, int val) {
	if(q != NULL) {
		if(q->head != NULL) {
			QueueNode *t = q->tail;
			//assert(t->next == NULL);
			t->next = (QueueNode*)malloc(sizeof(QueueNode*)); //this next value if definitly a NULL
			//assert(t->next != NULL);
			t->next->val = val;
			t->next->next = NULL;
			q->tail = t->next;
		} else {
			q->head = (QueueNode*)malloc(sizeof(QueueNode*));
		//	assert(q->head != NULL);
			q->head->val = val;
			q->head->next = NULL;
			q->tail = q->head;
		}
	}
}
int dequeue(Queue *q) {
//	assert(q!=NULL);
	if(q->head != NULL) {
		QueueNode *t = q->head;
		q->head = q->head->next;
		int val = t->val;
		free(t);
		return val;
	}
	return 0;
}
void DumpQueue(Queue *q) {
//	assert(q != NULL);
	QueueNode *h = q->head;
	while(h != NULL) {
		cout << h->val << " ";
		h = h->next;
	}
	cout <<endl;
}
int main(int argc, char **argv) {
	Queue q;
	int i;
	for(i=1; i<10; ++i) {
		enqueue(&q, i);
		DumpQueue(&q);
	}
	DumpQueue(&q);
	for(i=0; i<5; ++i) {
		cout << dequeue(&q) << "\n";
		DumpQueue(&q);
	}
	DumpQueue(&q);

	return 0;
}
