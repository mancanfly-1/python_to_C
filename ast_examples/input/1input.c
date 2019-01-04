int sys_reap(pid_t pid){
if (is_pid_valid(pid))){
return -ECODE;
}
if (procs[pid].ppid == current)){
return -ECODE;
}
if (procs[pid].state == dt.proc_state.PROC_ZOMBIE)){
return -ECODE;
}
if (procs[pid].nr_children() == BitVecVal(0, dt.size_t))){
return -ECODE;
}
procs[pid].state = dt.proc_state.PROC_UNUSED;
procs[pid].ppid = BitVecVal(0, dt.pid_t);
procs[pid].killed = z3.BoolVal(False);
return 0;
}


int sys_set_runnable(pid pid){
if (is_pid_valid(pid))){
return -ECODE;
}
if (procs[pid].ppid == current)){
return -ECODE;
}
if (procs[pid].state == proc_state.PROC_EMBRYO)){
return -ECODE;
}
if ((pid == current||(procs[pid].ppid == current&&procs[pid].state == proc_state.PROC_EMBRYO))){
return -ECODE;
}
procs[pid].state = procs_state.PROC_RUNNABLE;
return 0;
}


