import os
class TreeNode:
    def __init__(self, name, path):
        self.name = name
        self.children = []
        self.children_names = set()
        self.counter = 0
        self.children_idx_map = {}
        self.path = path
    def add_child(self, node):
        self.children.append(node)
        self.children_names.add(node.name)
        self.children_idx_map[node.name] = self.counter 
        self.counter += 1
    def get_child(self, node_name):
        idx = self.children_idx_map[node_name]
        return self.children[idx]


def generate_tree_structure(filepath_list):
    node = head = TreeNode('root','/root')
    for filename in filepath_list:
        node = head
        filename = os.path.normpath(filename)
        split_list = filename.split(os.sep)
        for s in split_list:   
            if s not in node.children_names:
                child_node = TreeNode(s,filename)
                node.add_child(child_node)
            else:
                child_node = node.get_child(s)
            node = child_node
            
    return head



def prefix_traversal(root, issues_flag_default, checked_files):
    res = "<li>"
    if root.children:
        
        res += '<label>' + root.name +'</label>'
    else:
        if issues_flag_default or root.path in checked_files:
            res += '<label><input id="'+root.path+'" name="'+root.path+'" type="checkbox" value="yes" checked />' + root.name +'</label>'
        else:
            res += '<label><input id="'+root.path+'" name="'+root.path+'" type="checkbox" />' + root.name +'</label>'
    i=0
    for child in root.children:
        if i==0:
            res += '<ul>'
        res += prefix_traversal(child, issues_flag_default, checked_files)
    res += "</li></ul>"
    return res

def generate_tree_html(head, issues_flag_default, checked_files):
    res = ""
    for child in head.children:
        res += '<ul>'
        res += prefix_traversal(child, issues_flag_default, checked_files)
    return res
