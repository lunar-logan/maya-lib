#include <iostream>
#include <sstream>
#include <string>

using namespace std;

class Node {
public:
	int data;
	Node *prev;
	Node *next;
};


class LinkedList {
public:
	LinkedList() {
		head = NULL;
		tail = NULL;
		sz = 0;
	}
	int size() {
		return sz;
	}
	void addLast(int el) {
		if(head == NULL) {
			head = new Node;
			head->data = el;
			head->next = NULL;
			head->prev = NULL;
			tail = head;
		} else {
			Node *t = new Node;
			t->data = el;
			t->next = NULL;
			t->prev = tail;
			tail->next = t;
			tail = t;
		}
		++sz;
	}
	void insert(int at, int e) {
		int i;
		Node *t;
		if(sz == 0) {
			head = initNode(e);
			tail = head;
		}
		t = head;
		for(i=0; i<at && i<sz; ++i) {
			t = t->next;
		}
		Node *n = initNode(e);
		Node *p = t->prev;
		n->prev = t->prev;
		n->next = t;
		t->prev = n;
		if(p != NULL) {
			p->next = n;
		}
		if(at == 0) {
			head = n;
		}
		++sz;
	}
	void addFirst(int e) {
		insert(0, e);
	}
	void get(int at, int *holder, bool rem) {
		Node *t, *r = NULL;
		int i;
		if(sz == 0) {
			holder = NULL;
			return;
		}
		t = head;
		for(i=0; i<at && i<sz; ++i) {
			t = t->next;
		}
		*holder = t->data;
		if(rem) {
			r = t;
			if(sz == 1) {
//				r = head;
				head = tail = NULL;
			} else if(at == 0) {
//				r = head;
				head = t->next;
			} else if(at == (sz-1)) {
//				r = tail;
				if(tail != NULL)
					tail = tail->prev;
			} 
			if(r != NULL) {
				remove(r);
				--sz;
			}
		}
	}
	string toString() {
		Node *h = head;
		stringstream str(stringstream::in | stringstream::out);
		while(h != NULL) {
			str << h->data << " " ;
			h = h->next;
		}
		return str.str();
	}
private:
	Node *head;
	Node *tail;
	int sz;
	Node* initNode(int e) {
		Node *n = new Node;
		n->data = e ;
		n->next = NULL;
		n->prev = NULL;
	}
	void remove(Node *t) {
		if(t != NULL) {
			Node *p = t->prev;
			Node *n = t->next;
			if(p != NULL)
				p->next = n;
			if(n != NULL)
				n->prev = p;
			delete t;
		}
	}
};


int main() {
	LinkedList l;
	for(int i=0; i<20; ++i) {
		l.addLast(i);
		cout << l.toString() << "; Current Size: " << l.size() << endl;
	}
	for(int i=0; i<20; i+=2) {
		l.insert(i, i+9);
		cout << l.toString() << endl;
	}
	cout << endl << " -------------------------------------------------- \n";
	int e;
	for(int i=0; i<l.size(); i+=3) {
		l.get(i, &e, true);
		cout << "Value=" << e << " At=" << i<</*"; " << l.toString() <<*/ endl;
	}
	cout << "Final List : " << l.toString() << endl;
	for(int i=0; i<l.size(); i+=3) {
		l.get(i, &e, false);
		cout << "Value=" << e << " At=" << i<</*"; " << l.toString() <<*/ endl;
	}
	for(int i=0; i<10; i+=2) {
		l.insert(i, i*i);
		cout << l.toString() << endl;
	}
	for(int i=0; i<10; i+=2) {
		l.addFirst(i*i*i);
		cout << l.toString() << endl;
	}
	return 0;
}
