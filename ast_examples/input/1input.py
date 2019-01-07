import z3
from libirpy import util
import datatype.datatypes as dt
import common
import sys

#specification

#def is_pid_valid(pid):
#    return z3.And(pid > 0, pid < dt.NPROC)

def init_proc(kernelstate, pid):
    kernelstate.procs[pid].ppid = z3.BitVecVal(0, 64)
    kernelstate.procs[pid].state = dt.proc_state.PROC_UNUSED
    kernelstate.procs[pid].killed = z3.BoolVal(False)
    #kernelstate.procs[pid].launched = z3.BoolVal(False)
    #kernelstate.procs[pid].nr_children() == z3.BitVecVal(0, dt.size_t)
    kernelstate.procs[pid].ipc_from = z3.BitVecVal(0, dt.pid_t)
    kernelstate.procs[pid].ipc_val = z3.BitVecVal(0, dt.uint64_t)
    kernelstate.procs[pid].ipc_size = z3.BitVecVal(0, dt.size_t)
    # nr_children = Refcnt(pid_t, pid_t, size_t, initial_offset=1)

def alloc_proc(old, pid):
    cond = z3.And(
        common.is_pid_valid(pid),
        old.procs[pid].state == dt.proc_state.PROC_UNUSED,
        common.is_pid_valid(old.current))
    new = old.copy()
    init_proc(new, pid)
    
    new.procs[pid].ppid = new.current
    new.procs[pid].state = dt.proc_state.PROC_EMBRYO
    new.procs[old.current].nr_children[pid] += 1
    return cond, util.If(cond, new, old)

# set current procs to PROC_RUNNABLE
def sys_set_runnable(old, pid):
    cond = z3.And(
        common.is_pid_valid(pid),
        old.procs[pid].ppid == old.current,
        old.procs[pid].state == dt.proc_state.PROC_EMBRYO)
    new = old.copy()
    new.procs[pid].state = dt.proc_state.PROC_RUNNABLE
    return cond, util.If(cond, new, old)

# reclaim a procs
def sys_reap(old, pid):
    cond = z3.And(
        common.is_pid_valid(pid),
        # Only the owner can reap a child
        old.procs[pid].ppid == old.current,

        # The pid to reap is a zombie
        old.procs[pid].state == dt.proc_state.PROC_ZOMBIE,

        # The proc has no children
        old.procs[pid].nr_children() == z3.BitVecVal(0, dt.size_t)
    )
    # set 
    new = old.copy()

    new.procs[old.current].nr_children[pid] -= 1
    #zero out pid's property
    new.procs[pid].state = dt.proc_state.PROC_UNUSED
    new.procs[pid].ppid = z3.BitVecVal(0, dt.pid_t)
    new.procs[pid].killed = z3.BoolVal(False)
    return cond, util.If(cond, new, old)

def sys_kill(old, pid):
    cond = z3.And(
        common.is_pid_valid(pid),
        old.procs[pid].state != dt.proc_state.PROC_UNUSED,
        old.procs[pid].state != dt.proc_state.PROC_ZOMBIE
    )

    new = old.copy()
    new.procs[pid].killed = z3.BoolVal(True)
    new.procs[pid].state = util.If(
        old.procs[pid].state != dt.proc_state.PROC_RUNNING, dt.proc_state.PROC_ZOMBIE, old.procs[pid].state)

    return cond, util.If(cond, new, old)

def sys_switch(old, pid):
    cond = z3.And(
        common.is_pid_valid(pid),
        old.procs[pid].state == dt.proc_state.PROC_RUNNABLE,

        # This is implied by pid having state runnable,
        # current is always running
        old.current != pid,
    )

    new = old.copy()
    # before switch, if the current procs' is killed, this procs' state must ZOMBIE after switch
    new.procs[old.current].state = util.If(
        old.procs[old.current].killed, dt.proc_state.PROC_ZOMBIE, dt.proc_state.PROC_RUNNABLE)
    # current's state must be PROC_RUNNING.
    new.procs[pid].state = dt.proc_state.PROC_RUNNING
    new.current = pid

    return cond, util.If(cond, new, old)

# reparent only take pid to INITPID's children
def sys_reparent(old, pid):
    cond = z3.And(
        common.is_pid_valid(pid),
        common.is_pid_valid(old.procs[pid].ppid),
        old.procs[old.procs[pid].ppid].state == dt.proc_state.PROC_ZOMBIE,

        z3.Or(
            old.procs[dt.INITPID].state == dt.proc_state.PROC_RUNNABLE,
            old.procs[dt.INITPID].state == dt.proc_state.PROC_RUNNING,
        ),
    )

    new = old.copy()

    new.procs[dt.INITPID].nr_children[pid] += 1
    new.procs[old.procs[pid].ppid].nr_children[pid] -= 1

    new.procs[pid].ppid = dt.INITPID

    return cond, util.If(cond, new, old)

def sys_set_proc_name(old, name0, name1):
    # We don't model proc names.
    # The syscall should not change the state.
    return z3.BoolVal(True), old



