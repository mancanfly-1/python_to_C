import z3
import ast
import astor
import sys

class mytransformer(ast.NodeTransformer):
    def generic_visit(self, node):
        #print type(node).__name__
        ast.NodeTransformer.generic_visit(self, node)
        return node
    def visit_Assign(self, node):
        if astor.to_source(node)[:-1] == 'new = state_old.copy()':
            newnode = ast.parse('new1 = state_old2.copy()')
            # get current node's index
            idx = node.parent.body.index(node)
            print node.parent.body
            node.parent.body.insert(idx + 1, newnode)
        
        ast.NodeTransformer.generic_visit(self, node)
        return node
    def visit_FunctionDef(self, node):
        ret_str = "return 0"
        node.body =[]
        #print node.body
        #node.body.append(ast.parse(ret_str))
        ast.NodeTransformer.generic_visit(self, node)
        return node

def add_parent(root):
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return root

if __name__ == "__main__":
    #str_code = 'z3.And(a, z3.Or(c,d))'
    if len(sys.argv) > 1:
        code = open(sys.argv[1]).read()
        tree = ast.parse(code, sys.argv[1])
        print astor.to_source(tree)
        root = add_parent(tree)
        trans = mytransformer()
        root = trans.visit(root)
        print astor.to_source(root)
    else:
        print 'error'
    