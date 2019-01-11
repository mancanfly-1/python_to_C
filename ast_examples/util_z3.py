import sys
import ast
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


def get_expression(node, str_return=''):
	if not isinstance(node, ast.AST):
		return str_return

	if type(node) == ast.Call and node.func.id in ['And', 'Or']:
		str_return ="("
		# get arguments
		for arg in node.args:
			if type(arg) == ast.Call and arg.func.id in ['And', 'Or']:
				str_return += get_expression(arg)
				str_return = str_return[:-3] + ")"
				if node.func.id == 'And':
					str_return += '&&'
				if node.func.id == 'Or':
					str_return += '||'
			else:
				if node.func.id == 'And':
					str_return += astor.to_source(arg)[:-1] + '&&'
				if node.func.id == 'Or':
					str_return += astor.to_source(arg)[:-1] + '||'

		
		str_return +=")"
		#print str_return
		return str_return
	else:
		return astor.to_source(node)[:-1] + "123"

# the node must be z3.And or z3.Or
def Split_z3_And_Or_condition(node):
	str_return =''
	str_return = get_expression(node)[:-3] + ")"
	return str_return

def Split_z3_Implies_condition(node):

def deal_z3_value(node):
	if type(node) == ast.Call and type(node.func) == ast.Attribute:
		if type(node.func.value) == Name: and node.func.value.id == 'z3':
			if node.func.attr == 'BitVecVal':
				return node.args[0]
	else:
		return None

