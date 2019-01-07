include z3.h
include util.h
include datatype.datatypes.h
int sys_reap(pid_t pid){
cond = And(is_pid_valid(pid_t_pid), procs[pid_t_pid].ppid == current, procs
    [pid_t_pid].state == proc_state.PROC_ZOMBIE, procs[pid_t_pid].
    nr_children() == BitVecVal(0, size_t));
procs[pid_t_pid].state = proc_state.PROC_UNUSED;
procs[pid_t_pid].ppid = BitVecVal(0, pid_t);
procs[pid_t_pid].killed = BoolVal(False);
return 0;
}
int sys_set_runnable(pid pid){
cond = And(is_pid_valid(pid_pid), procs[pid_pid].ppid == current, procs[
    pid_pid].state == proc_state.PROC_EMBRYO, Or(pid_pid == current, And(
    procs[pid_pid].ppid == current, procs[pid_pid].state == proc_state.
    PROC_EMBRYO)));
procs[pid_pid].state = procs_state.PROC_RUNNABLE;
return 0;
}
