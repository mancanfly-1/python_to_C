import sys
import ast
import astor
from util import *
#from cond_to_if import * 

# Dic_condition = {'funcdef':[['condition',new1, old], ['condition2',new1, new2],...]}, 'funcdef2':{...}}
Dic_condition = {}
# Dic_new_state = {'funcdef':[new, new1, new2...], 'funcdef2':[...]}
Dic_new_state = {}
# Dic_old_state = {'funcdef': old, 'funcdef':old2, ...}
Dic_old_state = {}
# Dic_func_args = {'funcdef': [arg1, arg2...], }
Dic_func_args = {}

Dic_func_bodys = {}

# condition = []
list_lib = []
current_def =''

# get the condtion, state, and function arguments to every function. and get the import information
class CollectVisitor(ast.NodeVisitor):
	def generic_visit(self, node):
		#print type(node).__name__
		ast.NodeVisitor.generic_visit(self, node)
		return node

	def visit_Return(self, node):
		ast.NodeVisitor.generic_visit(self, node)

	def visit_FunctionDef(self, node):
		# initial some global things
		global current_def 
		current_def = node.name
		Dic_condition[current_def] = []
		Dic_new_state[current_def] =[]
		Dic_func_args[current_def] = []
		Dic_func_bodys[current_def] = node.body

		#print current_def
		ast.NodeVisitor.generic_visit(self, node)

	def visit_arguments(self, node):
		if len(node.args) > 0:
			# collect old state
			if not Dic_old_state.has_key(current_def):
				Dic_old_state[current_def] = node.args[0].id
				for item in node.args:
					Dic_func_args[current_def].append(item.id)
		else:
			print('error definition of system call')
			assert(False)
			
		ast.NodeVisitor.generic_visit(self, node)

	def visit_Import(self, node):
		for item in node.names:
			if item.asname == None:
				list_lib.append(item.name)
			else:
				list_lib.append(item.asname)
		ast.NodeVisitor.generic_visit(self, node)

	def visit_ImportFrom(self, node):
		for item in node.names:
			if item.asname == None:
				list_lib.append(item.name)
			else:
				list_lib.append(item.asname)
		ast.NodeVisitor.generic_visit(self, node)

	def visit_Assign(self, node):
		ast.NodeVisitor.generic_visit(self, node)			

	def bool_condtion(self, arg1, arg2):
		if arg1 == Dic_old_state[current_def] or arg2 == Dic_old_state[current_def]:
			return True
		# why and?
		if arg1 in Dic_new_state[current_def] and arg2 in Dic_new_state[current_def]:
			return True
		return False

	def visit_Call(self, node):	
		ast.NodeVisitor.generic_visit(self, node)

	def visit_Return(self, node):
		# util.If(cond, new, old)
		util_if = node.value.elts[1]
		cond = astor.to_source(util_if.args[0])[:-1]
		new1 = astor.to_source(util_if.args[1])[:-1]
		new2 = astor.to_source(util_if.args[2])[:-1]
		tmp_cond = [cond, new1, new2]
		Dic_condition[current_def].append(tmp_cond)
		get_condtions(new1)
		get_condtions(new2)

def node_euqals_util_If(body):
	if type(body) == ast.Call:
		if type(body.func) == ast.Attribute and body.func.attr == 'If' and type(body.func.value) == ast.Name and body.func.value.id == 'util':
			return True
	return False

# reconstruct the function node.
def get_condtions(new1):
	for body in Dic_func_bodys[current_def]:
		if type(body) == ast.Assign and len(body.targets) == 1:	
			if type(body.targets[0]) == ast.Name:
				if body.targets[0].id == new1 and node_euqals_util_If(body.value):
					args = body.value.args
					cond1 = astor.to_source(args[0])[:-1]
					new11 = astor.to_source(args[1])[:-1]
					new22 = astor.to_source(args[2])[:-1]

					tmp_cond = [cond1, new11,new22]
					# print tmp_cond, '----------'
					Dic_condition[current_def].append(tmp_cond)
					get_condtions(new11)
					get_condtions(new22)			
def init_new_state():
	for fun in Dic_condition:
		list_if_condtion = Dic_condition[fun]
		if list_if_condtion != None:
			for item in list_if_condtion:
				if item[2] not in Dic_new_state[fun] and item[2] != Dic_old_state[fun]:
					Dic_new_state[fun].append(item[2])
				if item[1] not in Dic_new_state[fun] and item[1] != Dic_old_state[fun]:
					Dic_new_state[fun].append(item[1])

def Collect(tree):
	codevisitor = CollectVisitor()
	if type(tree) == ast.Module:
		for i in range(0, len(tree.body)):
			codevisitor.visit(tree.body[i])
	init_new_state()
	print 'Dic_condition:', Dic_condition
	print 'Dic_old_state:',Dic_old_state
	print 'Dic_new_state:',Dic_new_state
	print 'Dic_func_args:', Dic_func_args
	print 'list_lib:', list_lib



if __name__ == "__main__":
	if len(sys.argv) > 1:
		code = open(sys.argv[1]).read()
		tree = ast.parse(code, sys.argv[1])
		# get relavent information
		codevisitor = CollectVisitor()
		# codevisitor.visit(tree)

		if type(tree) == ast.Module:
			for i in range(0, len(tree.body)):
				codevisitor.visit(tree.body[i])
		init_new_state()
		print 'Dic_condition:', Dic_condition
		print 'Dic_old_state:', Dic_old_state
		print 'Dic_new_state:', Dic_new_state
		print 'Dic_func_args:', Dic_func_args
	
	else:
		print('Please provdie a filename as arguments!!')

# def get_condtions(node, condition=[]):
# 	if type(node) == ast.Call and type(node.func) == ast.Attribute:
# 		if node.func.value.id == 'util' and node.func.attr == 'If':
# 			for item in node.args:
# 				if type(item) == ast.Call:
# 					get_condtions(item, condition)
# 				else:
# 					if condition.count(node.args[0].id) == 0:
# 						condition.append(node.args[0].id)
# 			return condition
# def get_state(node, state=[]):
# 	if type(node) == ast.Call and type(node.func) == ast.Attribute:
# 		if node.func.value.id == 'util' and node.func.attr == 'If':
# 			for item in node.args:
# 				if type(item) == ast.Call:
# 					get_condtions(item, state)
# 				else:
# 					if state.count(node.args[1].id) == 0 and node.args[1].id != Dic_old_state[current_def]:
# 						state.append(node.args[1].id)
# 					if state.count(node.args[2].id) == 0 and node.args[2].id != Dic_old_state[current_def]:
# 						state.append(node.args[2].id)
# 			return state


