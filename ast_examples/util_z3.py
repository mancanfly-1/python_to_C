import sys
import ast
import astor
from util import * 
def z3_First_Order_Operate(type, *args):
	assert(type in ["AND","OR"])

	if type == 'AND':
		type = "&&"
	if type == 'OR':
		type = '||'
	lens = len(args)
	if lens < 2:
		assert("arguments must bigger than 2...")
	else:
		result = str(args[0])
		print result
		i = 0
		operator = " " + type + " "

		while i < (lens - 1):
			result += operator + str(args[i+1])
			i += 1
		result = "(" + result + ")"
		return result

def And(*args):
	lens = len(args)
	assert(lens >1)
	result = str(args[0])
	print result
	i = 0
	operator = " && "

	while i < (lens - 1):
		result += operator + str(args[i+1])
		i += 1
	result = "(" + result + ")"
	return result

def Or(*args):
	lens = len(args)
	assert(lens >1)
	i = 0
	operator = " || "
	result = str(args[0])
	while i < (lens - 1):
		result += operator + str(args[i+1])
		i += 1
	result = "(" + result + ")"
	return result

def UDiv(a, b):
	result = ''
	return '('+ str(a)+ ' / ' + str(b) + ')'

def ULT(a, b):
	result = ''
	return '('+ str(a)+ ' < ' + str(b) + ')'

# the node must be z3.And or z3.Or
def Split_z3_And_Or_condition(node):
	str_return =''
	str_return = get_expression(node)[:-3] + ")"
	return str_return



def Deal_z3_function(node):
	if type(node) == ast.Call and type(node.func) == ast.Attribute:
		#print node.func.value
		if type(node.func.value) == ast.Name and node.func.value.id == 'z3':
			args = node.args
			if node.func.attr == 'BitVecVal':
				return args[0]
			if node.func.attr == 'And' or node.func.attr == 'Or':			
				content = ast.BoolOp()
				if node.func.attr == 'And':
					content.op = ast.And()
				else:
					content.op = ast.Or()
				content.values = args
				return content
				
			if node.func.attr == 'ULT':
				str = to_source(args[0]) + ' < ' + to_source(args[1])
				return source_to_node(str)
			if node.func.attr == 'ULE':
				str = to_source(args[0]) + ' > ' + to_source(args[1])
				return source_to_node(str)

			if node.func.attr == 'Not':
				# get argument of the z3.Not
				content = ast.UnaryOp()
				content.op = ast.Not()
				content.operand = args[0]
				return content
	return node

