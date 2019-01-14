include z3.h
include util.h
include hv6py.kernel.spec.datatypes.h
int sys_set_runnable(pit_t pid){
if (!is_pid_valid(pid)){
return -ECODE;
}
if (!procs[pid].ppid == current){
return -ECODE;
}
if (!procs[pid].state == dt.proc_state.PROC_EMBRYO){
return -ECODE;
}
procs[pid].state = dt.proc_state.PROC_RUNNABLE;
return 0;
}
