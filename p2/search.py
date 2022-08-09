class Node():
    def __init__(self, key):
        self.key = key
        self.values = []
        self.left = None
        self.right = None
        
    def __len__(self):
        size = len(self.values)
        if self.left != None:
            size += len(self.left.values)
        if self.right != None:
            size += len(self.right.values)
        return size
    
    def lookup(self, key):
        if key == self.key:
            return self.values
        elif key < self.key and self.left != None:
            return self.left.lookup(key)
        elif key > self.key and self.right != None:
            return self.right.lookup(key)
        else:
            return []
    
class BST():
    def __init__(self):
        self.root = None

    def add(self, key, val):
        if self.root == None:
            self.root = Node(key)

        curr = self.root
        while True:
            if key < curr.key:
                # go left
                if curr.left == None:
                    curr.left = Node(key)
                curr = curr.left
            elif key > curr.key:
                 # go right
                if curr.right == None:
                    curr.right = Node(key)
                curr = curr.right
            else:
                # found it!
                assert curr.key == key
                break

        curr.values.append(val)
        
    def __dump(self, node):
        if node == None:
            return
        self.__dump(node.right)            
        print(node.key, ":", node.values)  
        self.__dump(node.left)             

    def dump(self):
        self.__dump(self.root)
        
    def __getitem__(self, key):
        return self.root.lookup(key)