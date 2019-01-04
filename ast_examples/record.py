def int_sys_set_runnable(state_old, pid_pid):
	cond = z3.And(
		is_pid_valid(pid),
		state_old.procs[pid].ppid == old.current,
		state_old.procs[pid].state == dt.proc_state.PROC_EMBRYO)

	new = state_old.copy()
	new.procs[pid_pid].state = dt.procs_state.PROC_RUNNABLE
	return cond, util.If(cond, new, state_old)

def int_sys_set_runnable(pid_pid):
	cond.And(
		is_pid_valid(pid_pid)
		procs[pid].ppid == current,
		procs[pid].state == proc_state.PROC_EMBRYO)

	procs[pid_pid].state = procs_state.PROC_RUNNABLE
	return 0

int sys_set_runnable(pid pid){
	if(!is_pid_valid(pid)){
		return -3;
	}
	if(procs[pid].ppid == current){
		return -2;
	}
	if(procs[pid].state == proc_state.PROC_EMBRYO)){
		return -3;
	}
	procs[pid_pid].state = procs_state.PROC_RUNNABLE;
	return 0;
}

