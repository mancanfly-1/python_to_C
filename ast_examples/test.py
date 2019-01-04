import z3
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

def simplify(expression):
    args = {'algebraic_number_evaluator': False,
            'arith_lhs': False,
            'bit2bool': False,
            'blast_distinct': False,
            'blast_distinct_threshold': False,
            'blast_eq_value': False,
            'bv_extract_prop': False,
            'bv_ineq_consistency_test_max': False,
            'bv_ite2id': False,
            'bv_le_extra': False,
            'bv_not_simpl': False,
            'bv_sort_ac': False,
            'bv_trailing': False,
            'bv_urem_simpl': False,
            'bvnot2arith': False,
            'cache_all': False,
            'elim_and': False,
            'elim_rem': False,
            'elim_sign_ext': False,
            'elim_to_real': False,
            'eq2ineq': False,
            'expand_power': False,
            'expand_select_store': False,
            'expand_store_eq': False,
            'expand_tan': False,
            'flat': False,
            'gcd_rounding': False,
            'hi_div0': False,
            'hoist_cmul': False,
            'hoist_mul': False,
            'ite_extra_rules': False,
            'local_ctx': False,
            'local_ctx_limit': False,
            'max_degree': False,
            'max_memory': False,
            'max_steps': False,
            'mul2concat': False,
            'mul_to_power': False,
            'pull_cheap_ite': False,
            'push_ite_arith': False,
            'push_ite_bv': False,
            'push_to_real': False,
            'som': False,
            'som_blowup': False,
            'sort_store': False,
            'sort_sums': False,
            'split_concat_eq': False,
            'udiv2mul': False}
    return z3.simplify(expression, **args)

def is_true(cond):
    """Same as z3.is_true but supports python booleans"""
    if hasattr(cond, 'sexpr'):
    	print 'sexpr'
        return z3.is_true(simplify(cond))
    assert isinstance(cond, bool)
    return cond


def If(cond, a, b):
	cond = simplify(cond)
	if is_true(cond):
		print 'is_true'
		return a
print get_arg_name('pid_t_pid')