import sys
import ast
import astor
def createNameMap(a, d=None):
	if d == None:
		d = { }
	if not isinstance(a, ast.AST):
		return d
	if type(a) == ast.Module: # Need to go through the functions backwards to make this right
		for i in range(len(a.body) - 1, -1, -1):
			createNameMap(a.body[i], d)
	print type(a)
	for child in ast.iter_child_nodes(a):
		createNameMap(child, d)


if __name__ == "__main__":
	if len(sys.argv) > 1:
		
		code = open(sys.argv[1]).read()
		tree = ast.parse(code, sys.argv[1])
		
		tree.body[0].value.func = ast.Name('abc', ast.Load())

		print ast.dump(tree)
		print astor.to_source(tree)
		print astor.strip_tree(tree)
		print ast.dump(tree)
		createNameMap(tree)
	else:
		print("Please provdie a filename as argument!!")