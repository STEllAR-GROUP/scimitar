# -*- coding: utf-8 -*-
#
# Scimitar: Ye Distributed Debugger
#
# Copyright (c) 2016-2017 Parsa Amini
# Copyright (c) 2016 Hartmut Kaiser
# Copyright (c) 2016 Thomas Heller
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#

from __future__ import unicode_literals

settings = {
    'ui': {
        'prompts': [
            '# ',  # Level 0: Offline mode
            '$ ',  # Level 1: Debugging mode
        ],
    },
    'signals': {
        'sigkill':
            5,
        'sigkill_last':
            1,
        # TODO: See if we need to handle the other signals. These maybe:
        ## EOF
        ## SIGALRM
        ## SIGINT
        ## SIGQUIT
        ## SIGTERM
        ## SIGSTOP
    },
    'gdb': {
        # GDB command line
        # Supress banner, interactive mode
        'cmd': [
            'gdb',
            '-interpreter=mi2',  # Use GDB/MI2 interface
            '-quiet',  # Suppress banner
            '--nx',  # Don't load any .gdbinits whatsoever
        ],
        'attach':
            '--pid={pid}',
    },
    'sessions': {
        'history_length': 100
    },
}
