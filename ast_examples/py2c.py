import ast
import astor
import sys
import collector
import translater


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
def print_z3_And_Or_condition(node):
	str_return =''
	str_return = get_expression(node)[:-3] + ")"
	return str_return

def Python_to_C(root, path):
	return True