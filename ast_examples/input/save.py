def send_recv(old, pid, val, inpn, size, infd, outpn, outfd):
    cond = z3.And(
        is_pid_valid(pid),

        old.procs[pid].state == dt.proc_state.PROC_SLEEPING,

        # inpn is a valid pn and belongs to current
        is_pn_valid(inpn),
        old.pages[inpn].owner == old.current,

        z3.ULE(size, dt.PAGE_SIZE),

        z3.Implies(is_fd_valid(infd),
                   is_fn_valid(old.procs[old.current].ofile(infd))),

        # outpn is a valid pn and belongs to current
        is_pn_valid(outpn),
        old.pages[outpn].owner == old.current,
        old.pages[outpn].type == dt.page_type.PAGE_TYPE_FRAME,

        z3.Implies(is_fd_valid(outfd),
                   z3.Not(is_fn_valid(old.procs[old.current].ofile(outfd)))),

        # if ipc from is set, it must be set to current
        z3.Implies(old.procs[pid].ipc_from != 0,
                   old.procs[pid].ipc_from == old.current)
    )

    new = old.copy()

    new.procs[old.current].ipc_page = outpn
    new.procs[old.current].ipc_fd = outfd

    new.procs[pid].ipc_from = old.current
    new.procs[pid].ipc_val = val

    # memcpy
    new.pages.data = lambda pn0, idx0, oldfn=new.pages.data: \
        util.If(z3.And(pn0 == old.procs[pid].ipc_page, z3.ULT(idx0, size)),
                oldfn(inpn, idx0),
                oldfn(pn0, idx0))

    new.procs[pid].ipc_size = size

    new2 = new.copy()

    cond2 = z3.And(is_fd_valid(infd), is_fd_valid(new2.procs[pid].ipc_fd))

    fn = old.procs[old.current].ofile(infd)
    fd = old.procs[pid].ipc_fd

    new2.procs[pid].ofile[fd] = fn

    # bump proc nr_fds
    new2.procs[pid].nr_fds[fd] += 1

    # bump file refcnt
    new2.files[fn].refcnt[(pid, fd)] += 1

    new3 = util.If(cond2, new2, new)

    new3.procs[old.current].state = dt.proc_state.PROC_SLEEPING
    new3.procs[pid].state = dt.proc_state.PROC_RUNNING

    return cond, util.If(cond, new3, old)

def sys_recv(old, pid, pn, fd):
    cond = z3.And(
        is_pid_valid(pid),
        old.procs[pid].state == dt.proc_state.PROC_RUNNABLE,

        is_pn_valid(pn),
        old.pages[pn].owner == old.current,
        old.pages[pn].type == dt.page_type.PAGE_TYPE_FRAME,

        z3.Implies(is_fd_valid(fd),
                   z3.Not(is_fn_valid(old.procs[old.current].ofile(fd))))
    )

    new = old.copy()

    new.procs[old.current].ipc_from = z3.BitVecVal(0, dt.pid_t)
    new.procs[old.current].ipc_page = pn
    new.procs[old.current].ipc_size = z3.BitVecVal(0, dt.size_t)
    new.procs[old.current].ipc_fd = fd

    new.procs[old.current].state = dt.proc_state.PROC_SLEEPING
    new.procs[pid].state = dt.proc_state.PROC_RUNNING
    new.current = pid

    return cond, util.If(cond, new, old)

