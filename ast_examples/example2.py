import sys
import ast
import astor
from cond_to_if import *
from util_z3 import *
# from exmaple1 import type_class

src_code = []
list_args = []
cond_body_node = None

class mytransformer(ast.NodeTransformer):
	"""docstring for mytransformer"""
	def generic_visit(self, node):
		#print type(node).__name__
		ast.NodeTransformer.generic_visit(self, node)
		return node

	def visit_Attribute(self, node):
		#print type(node).__name__ + "=="
		
		if hasattr(node, "attr") and (node.attr in ["And", "Or",'BitVecVal']):
			if hasattr(node.value, "id") and node.value.id == "z3":
				print('== we have visit z3.And or z3.OR ==')
				node = ast.Name(str(node.attr), ast.Load())
		if hasattr(node, "value"):
			if hasattr(node.value, "id") and node.value.id == "state_old":
				node = ast.Name(str(node.attr), ast.Load())
		if hasattr(node, "value"):
			if hasattr(node.value, "id") and node.value.id == "old":
				print('== we have visit old ==')
				node = ast.Name(str(node.attr), ast.Load())
		if hasattr(node, "value"):
			if hasattr(node.value, "id") and node.value.id == "new":
				print('== we have visit new ==')
				node = ast.Name(str(node.attr), ast.Load())
		ast.NodeTransformer.generic_visit(self, node)
		return node

	def visit_arguments(self, node):
		if len(node.args) > 0:
			for item in (node.args):
				if right_arg(item.id):
					list_args.append(item.id)
				else:
					print('the argument type has a error type!')
					assert(False)
		ast.NodeTransformer.generic_visit(self, node)
		return node 

	def visit_Return(self, node):
		print ('we have visit return node')
		if type(node.value) == ast.Tuple:
			node.value = ast.Num(0)
		ast.NodeTransformer.generic_visit(self, node)
		return node

	def visit_FunctionDef(self, node):
		list_body = node.body
		index = 0
		for item_body in list_body:
			if type(item_body) == ast.Assign:
				if len(item_body.targets) ==1 and type(item_body.targets[0]) == ast.Name and item_body.targets[0].id == "cond":
					
					index = list_body.index(item_body)
					if type(item_body.value) == ast.Call:
						if type(item_body.value.func) == ast.Attribute and item_body.value.func.attr == 'And':
							# get all condition's all arguments
							temp_list_args = item_body.value.args
							str_temp = ''
							temp_list_insert = []
							for arg in temp_list_args:
								str_temp += 'if '
								str_temp += astor.to_source(arg)[:-1] + ':' + '\n'
								str_temp += '    '
								str_temp += 'return -ECODE' + '\n'
								#print str_temp

								temp_node = ast.parse(str_temp)
								temp_list_insert.append(temp_node)
								str_temp = ''
							#print temp_list_insert
							for arg in temp_list_insert:
								list_body.insert(index, arg)
								index +=1	
							list_body.remove(item_body)

				if len(item_body.targets) ==1 and type(item_body.targets[0]) == ast.Name and item_body.targets[0].id == "new":
					list_body.remove(item_body)
		ast.NodeTransformer.generic_visit(self, node)
		return node

	def visit_Name(self, node):
		if node.id in list_args:
			print node.id
			node.id = get_arg_name(node.id)
			print node.id
		ast.NodeTransformer.generic_visit(self, node)
		return node
	#def visit_Assign(self, node):

	#def visit_Call(self, node):



# stdout print...		
class CodeVisitor(ast.NodeVisitor):
	def generic_visit(self, node):
		#print type(node).__name__
		ast.NodeVisitor.generic_visit(self, node)
		return node
 
	def visit_Attribute(self, node):
		# if hasattr(node, "attr") and (node.attr in ["And", "Or",'BitVecVal']):
		# 	if hasattr(node.value, "id") and node.value.id == "z3":
		# 		print('== we have visit z3.And or z3.OR ==')
		# 		node = ast.Name(str(node.attr), ast.Load())
		ast.NodeVisitor.generic_visit(self, node)  

	def visit_If(self, node):
		# strif = astor.to_source(node.test).replace("and", "&&")
		# strif = strif.replace("or", "||")
		# print ('if ('+ strif+"){")
		# src_code.append('if ('+ strif+"){")
		cond = get_condition_expression(node.test)
		str_src = "if (" + str(cond) + "){"
		print str_src
		src_code.append(str_src)
		
		ast.NodeVisitor.generic_visit(self, node)
		print ("}")
		src_code.append("}")

	def visit_Assign(self, node): 
		
		print(astor.to_source(node)[:-1] + ';')
		src_code.append(astor.to_source(node)[:-1] + ';')
		ast.NodeVisitor.generic_visit(self, node)

	def visit_Return(self, node):
		print (get_node_code(node) + ';')
		src_code.append(get_node_code(node) + ';')
		ast.NodeVisitor.generic_visit(self, node)

	def visit_FunctionDef(self, node):
		func_return_type = get_func_type(node.name)
		func_name = get_func_name(node.name)
		# parameters
		func_arguments = "("
		print list_args
		for arg in list_args:
			arg_type = get_arg_type(arg)
			arg_name = get_arg_name(arg)
			if not arg_type == 'state':
				func_arguments += arg_type + " " + arg_name + ","
		# remove the last ','
		if len(list_args) > 0:
			func_arguments = func_arguments[:-1]
		func_arguments += ")"
		print(func_return_type + ' ' + func_name + func_arguments + "{")
		src_code.append(func_return_type+' ' + func_name + func_arguments + "{")
		ast.NodeVisitor.generic_visit(self, node)
		print("}")
		src_code.append('}')

	# def visit_Call(self, node):
	# 	ast.NodeVisitor.generic_visit(self, node)
if __name__ == "__main__":
	if len(sys.argv) > 1:
		code = open(sys.argv[1]).read()
		tree = ast.parse(code, sys.argv[1])
		transformer = mytransformer()
		if type(tree) == ast.Module:
			for i in range(0, len(tree.body)):
				if type(tree.body[i]) == ast.FunctionDef:
					#print(astor.to_source(tree))
					print 'begin transformer...'
					node = transformer.visit(tree.body[i])
					print astor.to_source(node)		
					print 'transform end...'		
					codevisitor = CodeVisitor()
					node = codevisitor.visit(node)
					list_args = []
					src_code.append('\n')
		path = sys.argv[1][:-2] + "c"

		file = open(path, 'w')
		for line in src_code:
			file.write(line + '\n')
		src_code = []	
		# print ast.dump(tree)
		# print 'After translate'
		# tree.body[0].value.func = ast.Name('abc', ast.Load())

		# print ast.dump(tree)
		# print astor.to_source(tree)
		# print astor.strip_tree(tree)
		# print ast.dump(tree)
		# createNameMap(tree)
	else:
		print("Please provdie a filename as argument!!")