import sys
import ast
import astor
from cond_to_if import * 

# Dic_condition = {'funcdef':{'condition':[new1, old], 'condition2':[new1, new2],...}, 'funcdef2':{...}}
Dic_condition = {}
# Dic_new_state = {'funcdef':[new, new1, new2...], 'funcdef2':[...]}
Dic_new_state = {}
# Dic_old_state = {'funcdef': old, 'funcdef':old2, ...}
Dic_old_state = {}
# Dic_func_args = {'funcdef': [arg1, arg2...], }
Dic_func_args = {}

# condition = []
list_lib = []
current_def =''


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
		Dic_condition[current_def] = {}
		Dic_new_state[current_def] =[]
		Dic_func_args[current_def] = []

		# Traversal
		for item in node.body:

		#print current_def
		ast.NodeVisitor.generic_visit(self, node)

	def visit_arguments(self, node):
		if len(node.args) > 0:
			# collect old state
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
		# collect new state
		if type(node.value) == ast.Call and type(node.value.func) == ast.Attribute:
			if type(node.value.func.value) == ast.Name and node.value.func.attr == 'copy':
				if node.value.func.value.id in Dic_old_state[current_def] or Dic_new_state[current_def]:
					Dic_new_state[current_def].append(node.targets[0].id)
			if type(node.value.func.value) == ast.Name and node.value.func.attr == 'If':
				list_args = node.value.args
				# utile.If(a,b,c)
				a = list_args[1]
				b = list_args[2]
				if a.id in Dic_new_state[current_def] and b.id in Dic_new_state[current_def]:
					Dic_new_state[current_def].append(node.targets[0].id)
		ast.NodeVisitor.generic_visit(self, node)			

	def visit_Call(self, node):	
		# collect condtions	
		if type(node.func) == ast.Attribute:
			# check if invoke util.If function
			if node.func.attr == 'If' and type(node.func.value) == ast.Name and node.func.value.id == 'util':
				# new3 = util.If(cond2, new2, new)
				# get argument[1][2]
				list_args = node.value.args
				a = list_args[1]
				b = list_args[2]
				if type(a) == ast.Name and type(b) == ast.Name:					
					if a.id in Dic_new_state[current_def] and b.id in Dic_new_state[current_def]:
						Dic_new_state[current_def].append(list_args[0].id)
					if Dic_condition[current_def].count(astor.to_source(node.args[0])[:-1]) == 0:
						Dic_condition[current_def].append(astor.to_source(node.args[0])[:-1])
			

		ast.NodeVisitor.generic_visit(self, node)

class ConditionVisitor(ast.NodeVisitor):
	def generic_visit(self, node):
		ast.NodeVisitor.generic_visit(self, node)
		return node



def Collect(node):
	codevisitor = CollectVisitor()
	codevisitor.visit(node)

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
		print Dic_condition
		print list_lib
		print Dic_old_state
		print Dic_new_state
		print Dic_func_args
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


