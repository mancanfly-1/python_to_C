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
if (!procs[pid].state == proc_state.PROC_EMBRYO){
return -ECODE;
}
new = copy();
procs[pid].state = proc_state.PROC_RUNNABLE;
return 0;
}
int sys_dup2(fd oldfd,pid_t pid,fd newfd){
if (!is_pid_valid(pid)){
return -ECODE;
}
if (!(pid == current || procs[pid].ppid == current && procs[pid].state ==
    proc_state.PROC_EMBRYO)){
return -ECODE;
}
if (!is_fd_valid(oldfd)){
return -ECODE;
}
if (!is_fn_valid(procs[current].ofile[oldfd])){
return -ECODE;
}
if (!is_fd_valid(newfd)){
return -ECODE;
}
if (current == pid && oldfd == newfd){
return 0;
}
if (is_fn_valid(procs[pid].ofile[newfd])){
newfn = procs[pid].ofile[newfd];
procs[pid].ofile[newfd] = 0;
procs[pid].nr_fds -= 1;
files[newfn].refcnt -= 1;
ref = files[newfn].refcnt();
if (ref == 0){
files[newfn].type = file_type.FD_NONE;
files[newfn].type = files[newfn].type;
}
if (ref == 0){
files[newfn].value = 0;
files[newfn].value = files[newfn].value;
}
if (ref == 0){
files[newfn].offset = 0;
files[newfn].offset = files[newfn].offset;
}
if (ref == 0){
files[newfn].omode = 0;
files[newfn].omode = files[newfn].omode;
}
}
fn = procs[current].ofile[oldfd];
procs[pid].ofile[newfd] = fn;
procs[pid].nr_fds -= 1;
files[fn].refcnt -= 1;
return 0;
}
