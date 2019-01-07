import ast
import astor
import sys
import collector

src_code = []
list_args = []
cond_body_node = None
current_func = ''
current_node = None
del_node = []

class mytransformer(ast.NodeTransformer):
	"""docstring for mytransformer"""
	def generic_visit(self, node):
		#print type(node).__name__
		ast.NodeTransformer.generic_visit(self, node)
		return node

	def visit_Attribute(self, node):
		if hasattr(node.value, "id") and node.value.id in collector.list_lib:
			node = ast.Name(str(node.attr), ast.Load())
		ast.NodeTransformer.generic_visit(self, node)
		return node

	def visit_arguments(self, node):
		if len(node.args) > 0:
			# for item in (node.args):
			# 	if right_arg(item.id):
			# 		list_args.append(item.id)
			# 	else:
			# 		print('the argument type has a error type!')
			# 		assert(False)
			node.args.remove(node.args[0])
		ast.NodeTransformer.generic_visit(self, node)
		return node 

	def visit_Return(self, node):
		if type(node.value) == ast.Tuple:
			node.value = ast.Num(0)
		ast.NodeTransformer.generic_visit(self, node)
		return node

	def visit_FunctionDef(self, node):
		global current_func
		current_func = node.name

		list_body = node.body
		index = 0
		for item_body in list_body:
			if type(item_body) == ast.Assign:
				if len(item_body.targets) == 1 and \
					type(item_body.targets[0]) == ast.Name and \
						item_body.targets[0].id in collector.Dic_condition[current_func]:
					print '=========?'
					index = list_body.index(item_body)
					# if the condition 
					if type(item_body.value) == ast.Call:
						if type(item_body.value.func) == ast.Attribute and item_body.value.func.attr == 'And' and item_body.value.func.value == 'z3':
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
						else:
							# todo: we must deal with not start with z3.And.
							continue
					# todo: we must deal with not function assignment.
					else:
						continue

				# delete all of 'new = old.copy' similiar operation
				if len(item_body.targets) ==1 and type(item_body.targets[0]) == ast.Name:
					# print collector.Dic_new_state
					# print item_body.targets[0], collector.Dic_new_state[current_func]
					if item_body.targets[0].id in collector.Dic_new_state[current_func]:
						list_body.remove(item_body)
		ast.NodeTransformer.generic_visit(self, node)
		return node

	def visit_Name(self, node):
		# if node.id in list_args:
		# 	if node.id != collector.
		# 	node.id = get_arg_name(node.id)
		if node.id in list_args and node.id != collector.Dic_old_state[current_func]:
			node.id = get_arg_name(node.id)
		ast.NodeTransformer.generic_visit(self, node)
		return node
	#def visit_Assign(self, node):

	# change z3.ULT Div and so on to symbol
	def visit_Call(self, node):
		namespace = ''
		method = ''
		if node.func == ast.Attribute:
			if node.func.value == ast.Name:
				# get z3 and operation
				namespace = node.func.value.id
				method = node.func.attr
				args = node.args
				

		ast.NodeTransformer.generic_visit(self, node)
		return node
	def visit_Assign(self, node):
		# if type(node.targets[0]) == ast.Name and node.targets[0].id in Dic_condition[current_func]:
		# 	if type(node.value) == ast.Call:

		
		
		ast.NodeTransformer.generic_visit(self, node)
		return node


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
		for arg in collector.Dic_func_args[current_func]:
			# dic_old_state is  a dic like "{'func',''}",the value is not a list
			if not arg == collector.Dic_old_state[current_func]:
				arg_type = get_arg_type(arg)
				arg_name = get_arg_name(arg)
				func_arguments += arg_type + " " + arg_name + ","
				print func_arguments

		# remove the last ','
		if len(collector.Dic_func_args[current_func]) > 1:
			func_arguments = func_arguments[:-1]
		func_arguments += ")"
		print(func_return_type + ' ' + func_name + func_arguments + "{")
		src_code.append(func_return_type+' ' + func_name + func_arguments + "{")
		ast.NodeVisitor.generic_visit(self, node)
		print("}")
		src_code.append('}')

	def visit_Import(self, node):
		for item in node.names:
			str_temp = "include " + item.name + ".h"
			print str_temp
			src_code.append(str_temp)
			
		ast.NodeVisitor.generic_visit(self, node)
		return node

	def visit_ImportFrom(self, node):
		for item in node.names:
			str_temp = "include " + item.name + ".h"
			print str_temp
			src_code.append(str_temp)
		ast.NodeVisitor.generic_visit(self, node)
		return node
	# def visit_Call(self, node):
	# 	ast.NodeVisitor.generic_visit(self, node)

def Translate(root_node):
	trans = mytransformer()
	return trans.visit(root_node)