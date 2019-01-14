import ast
import astor
import sys
from collector import *
#from translator import *
from util import * 
from util_z3 import * 
from cond_to_if import *

src_code = []
cond_body_node = None
current_func = ''
current_node = None




# the node must be z3.And or z3.Or
def print_z3_And_Or_condition(node):
	str_return =''
	str_return = get_expression(node)[:-3] + ")"
	return str_return

def replace(line):
	line = line.replace(' and ', ' && ')
	line = line.replace(' or ', ' || ')
	line = line.replace(' not ', '!')
	# line = line.replace('(and ', ' && ')
	# line = line.replace('(or ', ' || ')
	line = line.replace('Not(', '!(')
	return line
def Python_to_C(root, path):
	# first repalce and do other thing
	cv = CodeVisitor()
	cv.visit(root)
	file = open(path, 'w')
	#print src_code
	global src_code
	for line in src_code:
		line = replace(line)
		line = file.write(line + '\n')
	src_code = []
	return True

class CodeVisitor(ast.NodeVisitor):
	def generic_visit(self, node):
		#print type(node).__name__
		ast.NodeVisitor.generic_visit(self, node)
		return node

	def visit_bodys(self, node):
		if type(node) == ast.Assign or type(node) == ast.AugAssign or type(node) == ast.Return or type(node) == ast.Call:
			print(to_source(node) + ';')
			src_code.append(to_source(node) + ';')
		if type(node) == ast.If:
			self.visit_If(node)

	def visit_If(self, node):
		cond = to_source(node.test)
		str_src = "if (" + cond + "){"
		print str_src
		src_code.append(str_src)
		for itm in node.body:
			self.visit_bodys(itm)
		print '}'
		src_code.append('}')
		if len(node.orelse) > 0:
			str_src = 'else {'
			print str_src
			src_code.append(str_src)
			for itm in node.orelse:
				self.visit_bodys(itm)
			print ("}")
			src_code.append('}')
		return node

	def visit_Assign(self, node): 	
		print(astor.to_source(node)[:-1] + ';')
		src_code.append(astor.to_source(node)[:-1] + ';')
		# ast.NodeVisitor.generic_visit(self, node)
		return node

	def visit_AugAssign(self, node):
		print(astor.to_source(node)[:-1] + ';')
		src_code.append(astor.to_source(node)[:-1] + ';')
		ast.NodeVisitor.generic_visit(self, node)
		return node

	def visit_Return(self, node):
		
		print (get_node_code(node) + ';')
		src_code.append(get_node_code(node) + ';')
		# ast.NodeVisitor.generic_visit(self, node)
		return node

	def visit_Call(self, node):
		print (get_node_code(node) + ';')
		src_code.append(get_node_code(node) + ';')
		# ast.NodeVisitor.generic_visit(self, node)
		return node

	def visit_FunctionDef(self, node):
		current_func = node.name
		func_return_type = get_func_type(node.name)
		func_name = get_func_name(node.name)
		func_arguments = ''
		for arg in Dic_func_args[current_func]:
			# dic_old_state is  a dic like "{'func',''}",the value is not a list
			if not arg == Dic_old_state[current_func]:
				arg_type = get_arg_type(arg)
				arg_name = get_arg_name(arg)
				func_arguments += arg_type + " " + arg_name + ","
		
		func_arguments = '(' + func_arguments[:-1] + ')'
		print(func_return_type + ' ' + func_name + func_arguments + "{")
		src_code.append(func_return_type+' ' + func_name + func_arguments + "{")
		ast.NodeVisitor.generic_visit(self, node)
		print("}")
		src_code.append('}')
		#ast.NodeVisitor.generic_visit(self, node)
		return node

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
