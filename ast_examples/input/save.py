def int_sys_set_runnable(state_old, pid_pid):
	cond = z3.And(
		is_pid_valid(pid_pid),
		state_old.procs[pid_pid].ppid == state_old.current,
		state_old.procs[pid_pid].state == proc_state.PROC_EMBRYO,
		z3.Or(pid_pid == state_old.current,
              z3.And(
                  state_old.procs[pid_pid].ppid == state_old.current,
                  state_old.procs[pid_pid].state == proc_state.PROC_EMBRYO)),)

	new = state_old.copy()
	new.procs[pid_pid].state = procs_state.PROC_RUNNABLE
	return cond, util.If(cond, new, state_old)
