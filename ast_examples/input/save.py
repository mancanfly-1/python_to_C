import z3
from libirpy import util
import datatype.datatypes as dt

# # reclaim a procs
def int_sys_reap(state_old, pid_t_pid):
    cond = z3.And(
        is_pid_valid(pid_t_pid),
        # Only the owner can reap a child
        state_old.procs[pid_t_pid].ppid == state_old.current,

        # The pid to reap is a zombie
        state_old.procs[pid_t_pid].state == dt.proc_state.PROC_ZOMBIE,

        # The proc has no children
        state_old.procs[pid_t_pid].nr_children() == z3.BitVecVal(0, dt.size_t)
    )
    # set 
    new = state_old.copy()

    new.procs[state_old.current].nr_children[pid_t_pid] -= 1
    #zero out pid's property
    new.procs[pid_t_pid].state = dt.proc_state.PROC_UNUSED
    new.procs[pid_t_pid].ppid = z3.BitVecVal(0, dt.pid_t)
    new.procs[pid_t_pid].killed = z3.BoolVal(False)
    new2 = state_old.copy()
    new3 = util.If(cond, new2, new)

    return cond, util.If(cond, new, state_old)

def int_sys_set_runnable(state_old, pid_pid):
	cond = z3.And(
		is_pid_valid(pid_pid),
		state_old.procs[pid_pid].ppid == state_old.current,
		state_old.procs[pid_pid].state == proc_state.PROC_EMBRYO,
		z3.Or(pid_pid == state_old.current,
              z3.And(
                  state_old.procs[pid_pid].ppid == state_old.current,
                  state_old.procs[pid_pid].state == proc_state.PROC_EMBRYO)))

	new = state_old.copy()
	new.procs[pid_pid].state = procs_state.PROC_RUNNABLE
	return cond, util.If(cond, new, state_old)
