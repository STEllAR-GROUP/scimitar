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
import gdb
import scimitar


class CombinedTaggedStatePrinter(object):

    def __init__(self, val, type_):
        self.val = val
        self.type_ = type_
        # Values
        self.state_ = self.val['state_']
        thread_state_enum_t = gdb.lookup_type(
            'hpx::threads::thread_state_enum'
        )
        self.state = ((self.state_ >> 56) & 0xff).cast(thread_state_enum_t)
        thread_state_ex_enum_t = gdb.lookup_type(
            'hpx::threads::thread_state_ex_enum'
        )
        self.state_ex = ((self.state_ >> 48) &
                         0xff).cast(thread_state_ex_enum_t)
        self.tag = self.state_ & 0xffffffffffff

    def to_string(self):
        display_string = 'state=%s, state_ex=%s, tag=%s' % (
            self.state,
            self.state_ex,
            self.tag,
        )
        return "%s: {{ %s }} %s" % (
            self.type_,
            display_string,
            self.val.address,
        )

    def children(self):
        return [('state',
                 self.state, ),
                ('state_ex',
                 self.state_ex, ),
                ('tag',
                 self.tag, ), ]


scimitar.pretty_printers['hpx::threads::detail::combined_tagged_state<'
                         'enum hpx::threads::thread_state_enum, '
                         'enum hpx::threads::thread_state_ex_enum '
                         '>'] = CombinedTaggedStatePrinter


class AtomicCombinedTaggedStatePrinter(object):

    def __init__(self, val, type_):
        self.val = val
        self.type_ = type_
        # Values
        self.m_storage = self.val['m_storage']
        thread_state_enum_t = gdb.lookup_type(
            'hpx::threads::thread_state_enum'
        )
        self.state = ((self.m_storage >> 56) & 0xff).cast(thread_state_enum_t)

        thread_state_ex_enum_t = gdb.lookup_type(
            'hpx::threads::thread_state_ex_enum'
        )
        self.state_ex = ((self.state_ >> 48) &
                         0xff).cast(thread_state_ex_enum_t)

        self.tag = self.m_storage & 0xffffffffffff

    def to_string(self):
        display_string = 'state=%s, state_ex=%s, tag=%s' % (
            self.state,
            self.state_ex,
            self.tag,
        )
        return "%s: {{ %s }} %s" % (
            self.type_,
            display_string,
            self.val.address,
        )

    def children(self):
        return [('state',
                 self.state, ),
                ('state_ex',
                 self.state_ex, ),
                ('tag',
                 self.tag, ), ]


scimitar.pretty_printers['boost::atomics::atomic<'
                         'hpx::threads::detail::combined_tagged_state<'
                         'enum hpx::threads::thread_state_enum, '
                         'enum hpx::threads::thread_state_ex_enum'
                         '>'
                         '>'] = AtomicCombinedTaggedStatePrinter
