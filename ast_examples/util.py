import sys
import astor
import ast
# from collector import *
import collector

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
			if node.func.attr == 'If':
				return node
	return node
def util_if(node, func_name):
	if type(node) != ast.Assign:
		return node
	targets = node.targets
	value = node.value
	if len(targets) > 1:
		return node
	if not bool_util_if(value):
		return node
	args = value.args
	if type(targets[0]) != ast.Name:
		if_node = ast.If()
		if_node.test = args[0]
		if_node.body = []
		if_node.body.append(source_to_node(to_source(targets[0]) + ' = ' + astor.to_source(args[1])))
		if_node.orelse = []
		if_node.orelse.append(source_to_node(to_source(targets[0]) + ' = ' + astor.to_source(args[2])))
		node = if_node
	if type(targets[0]) == ast.Name and targets[0].id not in collector.Dic_new_state[func_name] and targets[0].id not in collector.Dic_old_state[func_name]:
		print '--------------'
		if targets[0].id not in get_all_condtions(targets[0].id, func_name):
			if_node = ast.If()
			if_node.test = args[0]
			if_node.body = []
			if_node.body.append(source_to_node(targets[0].id + ' = ' + astor.to_source(args[1])))
			if_node.orelse = []
			if_node.orelse.append(source_to_node(targets[0].id + ' = ' + astor.to_source(args[2])))
			node = if_node
	return node

def bool_util_if(node):
	if type(node) == ast.Call and type(node.func) == ast.Attribute \
	and type(node.func.value) == ast.Name and node.func.attr == 'If' and node.func.value.id == 'util':
		return True
	return False


def get_all_conditions(target_name, func_name):
	list_cond = collector.Dic_condtion[func_name]
	for sublist in list_cond:
		if target_name in sublist:
			return True
	return False