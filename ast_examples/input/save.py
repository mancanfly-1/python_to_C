import z3
from libirpy import util
import hv6py.kernel.spec.datatypes as dt

def int_sys_set_runnable(old, pid_t_pid):
    cond = z3.And(
        is_pid_valid(pid),
        old.procs[pid].ppid == old.current,
        old.procs[pid].state == dt.proc_state.PROC_EMBRYO)
    print old.procs[old.current].state
    new = old.copy()
    new.procs[pid].state = dt.proc_state.PROC_RUNNABLE
    return cond, util.If(cond, new, old)

def int_sys_dup2(old, fd_oldfd, pid_t_pid, fd_newfd):
    cond = z3.And(
        is_pid_valid(pid),

        # the pid is either current or an embryo belonging to current
        z3.Or(pid == old.current,
              z3.And(
                  old.procs[pid].ppid == old.current,
                  old.procs[pid].state == dt.proc_state.PROC_EMBRYO)),

        is_fd_valid(oldfd),
        is_fn_valid(old.procs[old.current].ofile(oldfd)),

        is_fd_valid(newfd),
    )

    new1 = old.copy()

    newfn = new1.procs[pid].ofile(newfd)

    # If fn != 0

    new1.procs[pid].ofile[newfd] = z3.BitVecVal(0, dt.fn_t)

    new1.procs[pid].nr_fds[newfd] -= 1

    # decrement file refcnt
    new1.files[newfn].refcnt[(pid, newfd)] -= 1

    ref = new1.files[newfn].refcnt()

    # If the refcnt is zero, clear the file slot

    new1.files[newfn].type = util.If(ref == 0, dt.file_type.FD_NONE, new1.files[newfn].type)
    new1.files[newfn].value = util.If(ref == 0, z3.BitVecVal(0, dt.uint64_t), new1.files[newfn].value)
    new1.files[newfn].offset = util.If(ref == 0, z3.BitVecVal(0, dt.off_t), new1.files[newfn].offset)
    new1.files[newfn].omode = util.If(ref == 0, z3.BitVecVal(0, dt.uint64_t), new1.files[newfn].omode)

    cond1 = is_fn_valid(old.procs[pid].ofile(newfd))
    
    new2 = util.If(cond1, new1, old.copy())

    # un-conditional

    fn = new2.procs[old.current].ofile(oldfd)

    new2.procs[pid].ofile[newfd] = fn

    new2.procs[pid].nr_fds[newfd] += 1

    # bump file refcnt
    new2.files[fn].refcnt[(pid, newfd)] += 1

    # posix: if fds are the same, do nothing
    cond2 = z3.And(old.current == pid, oldfd == newfd)
    new3 = util.If(cond2, old.copy(), new2)

    return cond, util.If(cond, new3, old)
