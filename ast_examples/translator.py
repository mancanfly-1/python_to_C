import ast
import astor
import sys
from collector import *
from util_z3 import *

src_code = []
list_args = []
cond_body_node = None
current_func = ''
current_node = None
del_node = []
Dic_count = {'process': ['nr_children', 'nr_fds', 'nr_pages', 'nr_dmapages', 'nr_devs', 'nr_ports', 'nr_vectors', 'nr_intremaps']}
Dic_file_count = {'file':['refcnt']}

class CondtionTransformer(ast.NodeTransformer):
	"""docstring for mytransformer"""
	def generic_visit(self, node):
		#print type(node).__name__
		ast.NodeTransformer.generic_visit(self, node)
		return node
	# Dic_condition = {'funcdef':{'condition':[new1, old], 'condition2':[new1, new2],...}, 'funcdef2':{...}}
	def get_cond_target(self, cond_name):		
		index = 0
		for node in Dic_func_bodys[current_func]:
			if type(node) ==  ast.Assign and len(node.targets) == 1 and type(node.targets[0]) == ast.Name and node.targets[0].id == cond_name:
				return node, index
			index +=1
		return None, index

	def get_state_target(self, state_name):
		if state_name in [Dic_old_state[current_func] + '.copy', Dic_old_state[current_func]]:
			return None, 0
		index = 0
		for node in Dic_func_bodys[current_func]:
			if type(node) ==  ast.Assign and len(node.targets) == 1 and type(node.targets[0]) == ast.Name and node.targets[0].id == state_name:
				return node, index
			index +=1
		return None, index

	def clear_body(self, node):
		node.body =[]

	def splite_cond(self, node):
		func_args = node.value.args
		str_temp = ''
		temp_list_insert = []
		for arg in func_args:
			str_temp += 'if not '
			str_temp += astor.to_source(arg)[:-1] + ':' + '\n'
			str_temp += '    '
			str_temp += 'return -ECODE' + '\n'
			#print str_temp

			temp_node = ast.parse(str_temp)
			temp_list_insert.append(temp_node)
			str_temp = ''
		return temp_list_insert

	def get_start_new(self, assign_name):
		index = 0
		for item in Dic_func_bodys[current_func]:
			if type(item) == ast.Assign and len(item.targets) == 1 and type(item.targets[0]) == ast.Name and item.targets[0].id == assign_name:
				return index
			index += 1
		return index

	# TODO: this must be some error in there.
	def get_end_new(self, assign_name, start_index):
		index = start_index
		while index < len(Dic_func_bodys[current_func]):
			item = Dic_func_bodys[current_func][index]

			if ast.Return == type(item):
				return index
			if ast.Assign == type(item):
				if len(item.targets) == 1 and type(item.targets[0]) == ast.Name and item.targets[0].id in Dic_new_state[current_func] and item.targets[0].id != assign_name:
					return index
			# assgin type
			if ast.Assign == type(item) or ast.AugAssign == type(item):
				str_split = astor.to_source(item)[:-1].split('.')
				if str_split != [] and str_split[0] in Dic_new_state[current_func] and str_split[0] != assign_name:
					return index				
			index +=1
		return index - 1	

			# other type?

	# some problem. it's always append, we need insert.
	def add_body(self, insert_node, state_name):
		# get above information
		state_top_node, index_top = self.get_state_target(state_name)

		str_value = astor.to_source(state_top_node.value)[:-1]

		if str_value.split('.')[0] in Dic_new_state[current_func] and str_value.split('.')[1] == 'copy()':
			print '-------------'
			self.add_body(insert_node, str_value.split('.')[0])

		start_index = self.get_start_new(state_name)
		end_index = self.get_end_new(state_name, start_index)
		for i in range(0,len(Dic_func_bodys[current_func])):
			if i >= start_index and i < end_index:
				insert_node.append(Dic_func_bodys[current_func][i])
	
	def func_insert_list(self, froms, to, index):
		i = index
		for item in froms:
			to.insert(i, item)
			i+=1

	def get_insert_list(self, state_name):
		list_ret = []
		start_index = self.get_start_new(state_name)
		end_index = self.get_end_new(state_name, start_index)
		for i in range(0,len(Dic_func_bodys[current_func])):
			if i >= start_index and i < end_index:
				list_ret.append(Dic_func_bodys[current_func][i])
		return list_ret

	def visit_FunctionDef(self, node):
		print 'visit_FunctionDef'
		global current_func
		current_func = node.name
		insert_index = 0
		insert_node = node
		# clear all of current node
		self.clear_body(node)
		# get the first condition position.
		# Dic_condition = {'funcdef':[['condition',new1, old], ['condition2',new1, new2],...]}, 'funcdef2':{...}}
		first_cond_name = Dic_condition[current_func][0][0]
		# 'cond = z3.And(..,..)'
		cond_node, index = self.get_cond_target(first_cond_name)
		if cond_node == None:
			return None
		i = 0
		# Add the node before first condtion 	
		if index > 0:			
			while i < index:
				node.body.append(Dic_func_bodys[current_func][i])
				i+=1
		insert_index += i
		print astor.to_source(node)
		# traverse the condition
		i = 0
		while i < len(Dic_condition[current_func]):
			cond_i = Dic_condition[current_func][i]
			cond_name = cond_i[0]
			state_name_1 = cond_i[1]
			state_name_2 = cond_i[2]
			# new1 = old.copy()			
			# new2 = util.If(is_fn_valid(old.procs[pid].ofile(newfd)), new1, old.copy())
			# new3 = util.If(z3.And(old.current == pid, oldfd == newfd), old.copy(), new2)
			# return cond, util.If(cond, new3, old)
			state_node_1, index_1 = self.get_state_target(state_name_1) # new1 = ...
			state_node_2, index_2 = self.get_state_target(state_name_2)	# new2 = ...

			cond_node, index = self.get_cond_target(cond_name)
			# create build node
			if i == 0 and state_name_2 == Dic_old_state[current_func]:
				# get cond_name mapping to the condition node.
				list_cond = self.splite_cond(cond_node)
				a = 0
				# add the many if condtion to body
				for item in list_cond:
					insert_node.body.append(item)	# insert below there.
				insert_index += len(list_cond)
				# TODO:
				self.add_body(insert_node.body, state_name_1)
				insert_node.body.append(ast.parse('return 0'))
				#print astor.to_source(insert_node)
			else:
				# util.if(cond, new1,new2)
				str_cond_node = ''
				if type(cond_node) == ast.Assign:
					str_cond_node = astor.to_source(cond_node.value)
				else:
					str_cond_node = cond_name
				# insert this node, why not work use ast.parse(string)????
				if_node = ast.If(cond_node.value, [], [])
				#if_node = ast.parse("if " + str_cond_node + ":\n" + "    " + "a=1")
				insert_node.body.insert(insert_index, if_node)
				# bodies
				if state_node_1 != None:
					#self.add_body(if_node.body, state_name_1)
					# get all of statement with specific name
					list_insert = self.get_insert_list(state_name_1)
					for item in list_insert:
						if item != cond_node:
							if_node.body.append(item)
					#insert_node.body.insert(insert_index, if_node)
				else:
					if state_name_1 == Dic_old_state[current_func] + '.copy()':
						if_node.body.append(astor.to_source('return 0'))
						insert_index += 1
				# else bodies
				if state_node_2 != None:
					#self.add_body(insert_node, state_name_2)
					list_insert = self.get_insert_list(state_name_2)
					self.func_insert_list(list_insert, insert_node.body, insert_index)
			i +=1
		ast.NodeTransformer.generic_visit(self, node)
		return node
# TODO:z3.Implies; lamda expression; Map and Refcont of the struct must change to number.
class DetailTransformer(ast.NodeTransformer):
	def generic_visit(self, node):
		#print type(node).__name__
		ast.NodeTransformer.generic_visit(self, node)
		return node
	def visit_If(self, node):
		if type(node.test) == ast.UnaryOp and type(node.test.operand) == ast.Call:
			# get function name
			if type(node.test.operand.func) == ast.Attribute and node.test.operand.func.attr == 'Implies' and node.test.operand.func.value.id == 'z3':
				str = astor.to_source(node.test.operand.args[0])[:-1] + ' and ' + astor.to_source(node.test.operand.args[1])[:-1]
				node_test = ast.parse(str)
				# why not work?
				content = ast.BoolOp()
				content.op = ast.And()
				content.values = node.test.operand.args
				
				#node.test = node_test.body[0].value
				node.test = content
		ast.NodeTransformer.generic_visit(self, node)
		return node

	# def visit_Call(self, node):
	# 	node = Deal_z3_function(node)
	# 	print astor.to_source(node)
	# 	ast.NodeTransformer.generic_visit(self, node)
	# 	return node

	def visit_FunctionDef(self, node):
		current_func = node.name
		ast.NodeTransformer.generic_visit(self, node)
		current_node = node
		return node

	def visit_arguments(self, node):
		if len(node.args) > 0:
			for item in node.args:
				if type(item) == ast.Name and item.id == Dic_old_state[current_func]:
					node.args.remove(item)
		else:
			print('error definition of system call')
			assert(False)
		ast.NodeTransformer.generic_visit(self, node)
		return node
	
	def visit_Assign(self, node):
		node = self.remove_state(node)
		if node != None:
			ast.NodeTransformer.generic_visit(self, node)
			return node

	def visit_AugAssign(self, node):
		node = self.remove_state(node)
		if node != None:
			ast.NodeTransformer.generic_visit(self, node)
			return node

	def visit_Call(self, node):
		if len(node.args) > 0:
			index = 0
			for index in range(0, len(node.args)):
				arg = node.args[index]
				str_arg = astor.to_source(arg)[:-1].split('.')
				if len(str_arg) > 0 and str_arg[0] in Dic_new_state[current_func]:
					new_arg = astor.to_source(arg)[:-1][len(str_arg[0]) + 1:]
					# the type of ast.parse(new_arg) is a module			
					node.args[index] = ast.parse(new_arg).body[0].value
		node = Deal_z3_function(node)
		print astor.to_source(node)
		# translate like 'process[pid].ofile(fd)' to process[pid].ofile
		# TODO: ofile must in a collection!!! and the head must be 'process'
		if type(node) == ast.Call and type(node.func) == ast.Attribute:
			if node.func.attr == 'ofile':
				Name = ast.Name();
				Name.ctx = ast.Load()
				Name.id = node.args[0].id
				Index = ast.Index(Name)
				Subscript = ast.Subscript()
				Subscript.ctx = ast.Load()
				Subscript.slice = Index
				Subscript.value = node.func
				node = Subscript
			if type(node) == ast.Call and type(node.func) == ast.Attribute and node.func.attr in Dic_count['process']:
				node = node.func
		ast.NodeTransformer.generic_visit(self, node)
		return node		

	def visit_Subscript(self, node):
		if type(node.value) == ast.Attribute and node.value.attr in Dic_count['process']:
			node = node.value
		if type(node.value) == ast.Attribute and node.value.attr in Dic_file_count['file']:
			node = node.value
		ast.NodeTransformer.generic_visit(self, node)
		return node	

	def remove_state(self, node):
		if type(node) == ast.AugAssign:
		# more than one return is not allowed.
			str_assgin = astor.to_source(node.target)[:-1]
		elif type(node) == ast.Assign:
			str_assgin = astor.to_source(node.targets[0])[:-1]
		if str_assgin in Dic_new_state[current_func]:
			# get parent node and delete this node
			#node.parent.body.remove(node)
			node = None
			return node
		state = str_assgin.split('.')[0]

		if state in Dic_new_state[current_func]:
			if type(node) == ast.AugAssign:
				addorsub = ''
				if node.op == 'Add':
					addorsub = ' += '
				else:
					addorsub = ' -= '
				str_assgin = str_assgin[len(state) + 1:] + addorsub + astor.to_source(node.value)[:-1]
			elif type(node) == ast.Assign:
				str_assgin = str_assgin[len(state) + 1:] +' = '+ astor.to_source(node.value)[:-1]
			node = ast.parse(str_assgin)
		return node

def Translate(root_node):
	# second, detail translate
	trans = CondtionTransformer()
	tree = trans.visit(root_node)

	print astor.to_source(tree)
	detailTrans = DetailTransformer()
	tree = detailTrans.visit(tree)
	# delete all of new and old state.
	for i in range(0, len(tree.body)):
		node = tree.body[i]
		if type(node) == ast.FunctionDef:
			function_name = node.name
			print function_name
			str_del_new_old_state = astor.to_source(node)[:-1]
			for new_state in Dic_new_state[function_name]:
				
				str_del_new_old_state = str_del_new_old_state.replace(new_state + '.', '')
			str_del_new_old_state = str_del_new_old_state.replace(Dic_old_state[function_name] + '.', '')
			tree.body[i] = ast.parse(str_del_new_old_state)
	# translate condtions jump.
	print astor.to_source(tree)
	
	
