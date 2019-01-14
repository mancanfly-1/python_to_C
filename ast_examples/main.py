import ast
import astor
import sys
from collector import *
from translator import *
from py2c import *


def main(root_node, path):
	# collect information of current py file.
		Collect(root_node)
		# translate current py to different type of py
		root = Translate(root_node)
		# translate py to C code.
		#Python_to_C(root, path)
def add_parent(root):
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return root

if __name__ == "__main__":
	if len(sys.argv) > 1:
		code = open(sys.argv[1]).read()
		tree = ast.parse(code, sys.argv[1])
		# collect a lot of things
		print '================== Start Collect Information =================='
		Collect(tree)
		print '================== end Collect Information ==================\n'
		# add parent node 
		add_parent(tree)
		print '================== Start translate structure =================='
		Translate(tree)
		print '================== end translate structure ==================\n'
		path = sys.argv[1][:-2] + "c"
		print '================== start parsing python to C =================='
		Python_to_C(tree, path)
		print '================== end parsing python to C =================='
		#main(tree, path)
	else:
		print('Please provdie a filename as arguments!!')