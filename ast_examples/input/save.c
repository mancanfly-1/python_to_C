int sys_dup2(fd oldfd,pid_t pid,fd newfd){
if (!is_pid_valid(pid)){
return -ECODE;
}
if (!(pid == current || procs[pid].ppid == current && procs[pid].state ==
    dt.proc_state.PROC_EMBRYO)){
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
files[newfn].type = util.If(ref == 0, dt.file_type.FD_NONE, files[newfn].type);
files[newfn].value = util.If(ref == 0, 0, files[newfn].value);
files[newfn].offset = util.If(ref == 0, 0, files[newfn].offset);
files[newfn].omode = util.If(ref == 0, 0, files[newfn].omode);
}
fn = procs[current].ofile[oldfd];
procs[pid].ofile[newfd] = fn;
procs[pid].nr_fds -= 1;
files[fn].refcnt -= 1;
return 0;
}
