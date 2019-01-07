import sys
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



