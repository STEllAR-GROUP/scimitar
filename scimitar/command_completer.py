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
import prompt_toolkit as ptk


class CommandCompleter(ptk.completion.Completer):

    def __init__(self):
        self.current_candidates = []

    def _complete_command(self):
        raise NotImplementedError('Must override _complete_command')

    def _complete_command_arguments(self, command, tokens):
        raise NotImplementedError('Must override _complete_command_arguments')

    def _prune_nonmatches(self, candidates, being_completed):
        if being_completed:
            result = [
                candidate for candidate in candidates
                if candidate.startswith(being_completed)
            ]
        else:
            result = candidates

        # If it's the only choice
        if result and len(result) == 1:
            return [result[0] + ' ']
        return result

    def _build_match_list(self, original_line, begin_index, end_index):
        tokens = original_line.split()
        # if first token
        if not tokens:
            self.matches = self._complete_command()
        else:
            try:
                if begin_index == 0:
                    candidates = self._complete_command()
                else:
                    candidates = self._complete_command_arguments(
                        tokens[0], tokens[1:]
                    )
                self.matches = self._prune_nonmatches(
                    candidates, original_line[begin_index:end_index]
                )
            except (KeyError, IndexError):
                self.matches = []

    def get_completions(self, document, complete_event):
        line_buffer = document.current_line
        begidx = document.cursor_position - len(document.get_word_before_cursor())
        endidx = document.cursor_position

        self._build_match_list(line_buffer, begidx, endidx)

        try:
            if not self.matches:
                return []
            return [ptk.completion.Completion(i, start_position=-len(last_word)) for i in self.matches]
        except IndexError:
            pass
        #except Exception as e:
        #    print 'Error: {0}'.format(repr(e))
        return None

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:
