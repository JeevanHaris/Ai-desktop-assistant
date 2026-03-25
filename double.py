class node:
    def __init__(self,data):
        self.data=data
        self.previous=None
        self.next=None
class Double:
    def __init__(self):
        self.head=None
        self.tail=None

    def add(self,data):
        newnode=node(data)
        if self.head is None:
            self.head=self.tail=newnode
            self.head.previous=None
            self.head.next=None
        else:
            self.tail.next=newnode
            newnode.previous=self.tail
            self.tail=newnode
            self.tail.next=None

    def display(self):
        current=self.head
        if current is None:
            print("empty")
            return
        print("the nodes of linked",end='')
        while current is not None:
            print(current.data,end='')
            current=current.next
        print()


d=Double()
d.add(1)
d.add(2)
d.add(3)

d.display()


