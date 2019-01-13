import sys
import astor
import ast

def to_source(node):
	return astor.to_source(node)[:-1]

def source_to_node(str_source):
	return ast.parse(str_source).body[0]

def i64(num):
	ret_num = ast.Num()
	ret_num.n = num
	return ret_num

def Deal_util_function(node):
	if type(node) == ast.Call and type(node.func) == ast.Attribute:
		if type(node.func.value) == ast.Name and node.func.value.id == 'util':
			if node.func.attr == 'i64':
				return node.args[0]
			# TODO:
			if node.func.attr == 'others':
				return node
	return node