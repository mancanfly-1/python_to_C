aList = [123, 'xyz', 'zara', 'abc']
insert_list = ['123','234']
# for item in insert_list:
# 	aList.insert(3, item)	
a = 'new.process[id].id = z3.And'
state = a.split('.')[0]
a = a[len(state) + 1: ]
print a

# print "Final List : ", aList

def func_insert_list(froms, to, index):
	i = index
	for item in froms:
		to.insert(i, item)
		i+=1
func_insert_list(insert_list,aList, 3)
print 'After insert:', aList
