import ast
import sys
import os

opened_c_file = 0	
list1 = []
type_define = 0
type_class = 0

def createNameMap(a, d=None):
	global type_define
	global type_class
	print ast.dump(a)
	if d == None:
		d = { }
	if not isinstance(a, ast.AST):
		print 'not instance'
		return d
	if type(a) == ast.Module: # Need to go through the functions backwards to make this right
		print len(a.body)
		for i in range(0, len(a.body)):
			print type(a.body[i])
			if type(a.body[i]) == ast.ClassDef:
				type_class = 1
				type_define = 0
			elif type(a.body[i]) == ast.Assign:
				type_class = 0
				type_define = 1
			createNameMap(a.body[i], d)
			if type(a.body[i]) == ast.ClassDef:
				opened_c_file.write("};\n")
		return d
	# class define
	if type(a) in [ast.ClassDef]:
		if hasattr(a, "name"):
			opened_c_file.write("struct " + a.name + "{\n")			
		else:
			assert("There is an error in Class node!");
	# assign define
	elif type(a) == ast.Assign:	
		# class assign 	
		if type_class:
			# write type
			if hasattr(a, "value"):
				assert("There is an error in Assign node!");
			# funcation name right or not
			if a.value.func.id not in ["Refcnt2","Refcnt","Map"]:
				assert("abstarct data struct wrong!");

			# variant name
			list2 = a.value.args
			v_type = list2[-1].id

			if hasattr(a, "targets"):
				assert("There is an error in Assign node!");
			v_name = str((a.targets[0]).id)
			print v_type + " " + v_name + ";\n"
			opened_c_file.write("	"+v_type + " " + v_name + ";\n")
		# derictry assgin
		if type_define:
			# z3.BitVecSort
			if type(a.value) == ast.Call:
				if a.value.func.value.id == 'z3':
					if a.value.func.attr == 'BitVecSort':
						length = a.value.args[0].n
						v_name = str((a.targets[0]).id)
						if length == 64:
							opened_c_file.write("typedef " + "unsigned long long int " + v_name + "\n")
						if length == 32:
							opened_c_file.write("typedef " + "unsigned long int " + v_name + "\n")
						if length == 16:
							opened_c_file.write("typedef " + "unsigned int " + v_name + "\n")
						if length == 8:
							opened_c_file.write("typedef " + "unsigned char " + v_name + "\n")
					if a.value.func.attr == 'BitVecVal':
						v_name = str((a.targets[0]).id)
						value = a.value.args[0].n
						length = a.value.args[1].n
						if length == 64:
							opened_c_file.write("unsigned long long int " + v_name + "=" + str(value) + ";\n")
						if length == 32:
							opened_c_file.write("unsigned long int " + v_name + "=" + str(value) + ";\n")
						if length == 16:
							opened_c_file.write("unsigned int " + v_name + "=" + str(value) + ";\n")
						if length == 8:
							opened_c_file.write("unsigned char " + v_name + "=" + str(value) + ";\n")
				else:
					assert("it is not z3 BitVecXXX type!");
			else:
				v_name = str((a.targets[0]).id)
				print a.value.n
				v_vlaue = a.value.n
				opened_c_file.write("#define " + v_name + " " + str(v_vlaue) + "\n")

	for child in ast.iter_child_nodes(a):
		createNameMap(child, d)
	return d 

if __name__ == "__main__":
	if len(sys.argv) > 1:
		py_file = os.path.split(sys.argv[1])[-1]
		print py_file
		c_file = (py_file).split(".", 1)[0]
		print c_file
		c_file = c_file + (".c")
		print c_file
		opened_c_file = open(c_file, 'w')

		code = open(sys.argv[1]).read()
		tree = ast.parse(code, sys.argv[1])
		d = createNameMap(tree)
		opened_c_file.close()
		print d
	else:
		print("Please provdie a filename as argument!!")