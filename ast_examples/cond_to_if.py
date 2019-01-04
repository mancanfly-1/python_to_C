import sys
import ast
import astor
from util_z3 import *

# And(is_pid_valid(pid_pid),And(a,b))
# And(And(a,b),c)
def createNameMap(a, d=None):
	if d == None:
		d = { }
	if not isinstance(a, ast.AST):
		return d
	if type(a) == ast.Module: # Need to go through the functions backwards to make this right
		for i in range(len(a.body) - 1, -1, -1):
			createNameMap(a.body[i], d)
	# print type(a)
	for child in ast.iter_child_nodes(a):
		createNameMap(child, d)

def right_arg(argument):
	if len(argument.split('_')) > 1:
		return True
	else:
		return False

def get_arg_type(argument):
    if right_arg(argument):
        str_ret = ''
        list_arg = argument.split('_')
        list_arg = list_arg[0:(len(list_arg) -1)]
        for item in list_arg:
            str_ret += str(item) + '_'
        str_ret = str_ret[:-1]
        return str_ret
    else:
        print('the argument type has a error type!')
        assert(False)

def get_arg_name(argument):
    if right_arg(argument):
        str_ret = ''
        list_arg = argument.split('_')
        list_arg = list_arg[len(list_arg) -1: len(list_arg)]

        for item in list_arg:
            str_ret += str(item) + '_'
        str_ret = str_ret[:-1]
        return str_ret
    else:
        print('the argument name has a error type!')
        assert(False)


def get_func_type(func):
	if len(func.split('_')) > 1:
		#print type(func.split('_',1)[0])
		return func.split('_',1)[0]
	else:
		print('the argument type has a error type!')
		assert(False)

def get_func_name(func):
	if len(func.split('_')) > 1:
		return func.split('_',1)[1]
	else:
		print('the argument name has a error type!')
		assert(False)

def get_error_code(node):
	return '-ECODE'

def get_node_code(node):
	return astor.to_source(node)[:-1]

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

def get_condition_expression(node):
	str_return =''
	str_return = get_expression(node)[:-3] + ")"
	return str_return

# if __name__ == "__main__":
# 	if len(sys.argv) > 1:
		
# 		code = open(sys.argv[1]).read()
# 		tree = ast.parse(code, sys.argv[1])

# 		str_return = ''
# 		print '=========='
# 		str_return = get_condition_expression(tree.body[0].value)
# 		print str_return
# 		#print str_return
# 		# transformer = mytransformer()
# 		# if type(tree) == ast.Module:
# 		# 	for i in range(0, len(tree.body)):
# 		# 		if type(tree.body[i]) == ast.FunctionDef:
# 		# 			#print(astor.to_source(tree))
# 		# 			node = transformer.visit(tree.body[i])
# 		# 			print astor.to_source(node)				
					
# 	else:
# 		print("Please provdie a filename as argument!!")
