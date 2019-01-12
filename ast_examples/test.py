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
        
        ast.NodeTransformer.generic_visit(self, node)
        return node
    def visit_FunctionDef(self, node):
        ret_str = "return 0"
        node.body =[]
        #print node.body
        #node.body.append(ast.parse(ret_str))
        ast.NodeTransformer.generic_visit(self, node)
        return node
    def visit_AugAssign(self, node):
        value = node.target.value
        node.target = value
        ast.NodeTransformer.generic_visit(self, node)
        return node

if __name__ == "__main__":
    #str_code = 'z3.And(a, z3.Or(c,d))'
    # str_func = 'if is_valid():\n    return a'
    # node = ast.parse(str_func)

    # #a = ast.BoolOp('and',[node, node])
    # print astor.to_source(a)
    if len(sys.argv) > 1:
        code = open(sys.argv[1]).read()
        tree = ast.parse(code, sys.argv[1])
        print astor.to_source(tree)
        #root = add_parent(tree)
        trans = mytransformer()
        root = trans.visit(tree)
        print astor.to_source(root)
    else:
        print 'error'
    