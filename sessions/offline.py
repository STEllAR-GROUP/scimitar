# -*- coding: utf-8 -*-
#
# Scimitar: Ye Distributed Debugger
# 
# Copyright (c) 2016 Parsa Amini
# Copyright (c) 2016 Hartmut Kaiser
# Copyright (c) 2016 Thomas Heller
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
import re
import modes
import errors
import pexpect
import console
from util import config, print_ahead, configuration
from terminals import LocalTerminal, RemoteTerminal
#######################
# mode: offline
#######################

base_machine = None

def job(args):
    try:
        pids = []
        for arg in args:
            pids.append(int(arg))
        _local_s.launch(pids)
        return (modes.to_local, None)
    except ValueError:
        raise BadArgsError(
            'job', 'Was expecting PIDs, received non-integer(s): {0}'.
            format(repr(args))
        )
    raise errors.CommandImplementationIncompleteError
    #_local_s.launch(pids)
    #raise CommandImplementationIncompleteError
    #return (modes.job, None)


def attach(args):
    args_string = ' '.join(args)
    # Verify command syntax
    if len(args) < 1 or not re.match('(?:(?:\w+:)?\d+|\s)+', args_string):
        raise errors.BadArgsError('attach', 'attach [<host>:]<pid>[ [<host>:]<pid> [...]]')

    # Group by host
    pid_list = {}
    for app_instance in re.finditer('((?:(\w+):)?(\d+))', args_string):
        host = app_instance.group(2) # or base_machine
        pid = int(app_instance.group(3))

        if pid_list.has_key(host):
            pid_list[host] += [pid]
        else:
            pid_list[host] = [pid]

    # Check the status of all provided PIDs
    dead_pids = []
    for host in pid_list.iterkeys():
        # Establish a connection per each process
        with console.Terminal(host) as term:
            for pid in pid_list[host]:
                if not term.is_pid_alive(pid):
                    host_path = '.'.join(console.list_hops())
                    if host:
                        host_path += '.' + host
                    dead_pids.append('{host}:{pid}'.format(host=host_path, pid=pid))

    # Stop if all processes are alive
    if len(dead_pids) != 0:
        raise errors.CommandFailedError(
            'attach', 'Invalid PIDs provided: {0}'.format(
            ' ,'.join(dead_pids)))

    for host in pid_list.iterkeys():
        for pid in pid_list[host]:

            # Start all GDB instances
            gdb_config = configuration.get_gdb_config()
            gdb_cmd = gdb_config['cmd']

            # Build the command line and launch GDB
            gdb_cmd += [gdb_config['attach'].format(pid = pid)]
            #cmd = ['ssh', host].extend(gdb_cmd)
            cmd_str = ' '.join(gdb_cmd)

            term = console.Terminal(host)
            term.connect()

            try:
                term.set_prompt('\(gdb\)\ \r\n')
                print(term.query(cmd_str))
            except pexpect.ExceptionPexpect as e:
                raise errors.CommandFailedError('attach', 'attach', e)

    console.current_session_id = console.newest_session_id

    return modes.debugging, None


def quit(args):
    return modes.quit, None


def add_hop(args):
    # Verify command syntax
    if len(args) < 1:
        raise errors.BadArgsError('hop', 'hop <host>[ [<host> [...]]')

    for host in args:
        console.add_hop(host)

    return modes.offline, None


def pop_hop(args):
    # Verify command syntax
    if len(args) > 0:
        raise errors.BadArgsError('pop', 'No arguments.\r\nSyntax:\r\n\tpop')

    try:
        console.pop_hop();
    except errors.CommandFailedError as e:
        raise e

    return modes.offline, None


def list_hops(args):
    items = console.list_hops()
    hops_str = '\r\n    '.join(items) if items else '\r\n    None'
    return modes.offline, 'Current hops:' + hops_str


def debug(args):
    import pdb
    pdb.set_trace()

    return modes.offline, None


commands = {
    'chain': add_hop,
    'pop': pop_hop,
    'hops': list_hops,
    'job': job,
    'attach': attach,
    'debug': debug, # HACK: For debugging only
    'quit': quit,
}


def process(cmd, args):
    if cmd in commands:
        return commands[cmd](args)
    raise errors.UnknownCommandError(cmd)

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:
