#!/usr/bin/env python
# coding: utf-8
'''
    Scimitar: Ye Distributed Debugger
    ~~~~~~~~
    :copyright:
    Copyright (c) 2016 Parsa Amini
    Copyright (c) 2016 Hartmut Kaiser
    Copyright (c) 2016 Thomas Heller

    :license:
    Distributed under the Boost Software License, Version 1.0. (See accompanying
    file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
'''

import signal
from sys import stdout
import time
import _thread
import threading
from util import config, vt100, print_out, print_ahead, print_error, raw_input_async, repr_str
import session

# Constants
BANNER = '''
                                                                          7?$7: 
   ____       _           _ _                                          +DDO7I~+.
  / ___|  ___(_)_ __ ___ (_) |_ __ _ _ __                    .I:    .NDDOZ?. ...
  \___ \ / __| | '_ ` _ \| | __/ _` | '__|                    .+~  DDD8Z+.      
   ___) | (__| | | | | | | | || (_| | |                       .7?IDD8Z+.        
  |____/ \___|_|_| |_| |_|_|\__\__,_|_|   (alpha)            .$?I+=$=.          
                                                          .?77$=+..?.           
            0.3.193 build 3109                          .III77777,.:I.          
                                                     .~?????I,?.    .~.         
                                                  ..?++++?=?+.                  
                                                .?+++++I 7:                     
                                             .+????+I.$+.                       
                                          .+?????I,7+.                          
                                    ..:=+++++?I:7=.                             
+.                       .       ,~~~===++++,$=.                                
 .:77$7777I?~~++=?IIII?++++=====~~~~~~=~.$?,                                    
    .=777777III????????+++?=:?~=~~,.?I~..                                       
        ,+77I????++++++=+++=,,I7+:.                                             
           . ..,:~====~::,.                                                     

Copyright (C) 2016 Parsa Amini
Copyright (C) 2016 Hartmut Kaiser
Copyright (C) 2016 Thomas Heller

Be licensed under Boost Software License, Version 1.0
<http://www.boost.org/LICENSE_1_0.txt>
'tis be free software; ye be free to change 'n redistribute it. Thar be NO
warranty; not even for MERCHANTABILITY or FITNESS FER A PARTICULAR PURPOSE.
'''

# HACK: Test async output printing
def noise():
    pass
    #print_ahead('Noise.', config.settings['ui']['prompt'])
#    for _ in range(20):
#        time.sleep(4)
#
#        print_ahead('Noise.', config.settings['ui']['prompt'])

# Dispatch the command and its arguments to the appropriate mode's processor
command_switcher = {
    session.modes.offline: session.offline.process,
    session.modes.local: session.local.process,
    session.modes.remote: session.remote.process,
    session.modes.debugging: session.debugging.process,
}

def main():
    # Clear the terminal
    vt100.terminal.reset()
    # Ahoy
    print_out(BANNER)

    # Initial session mode
    state = session.modes.offline

    # Async output printing
    _thread.start_new_thread(noise, ())

    # Main loop
    while state != session.modes.quit:
        vt100.unlock_keyboard()
        # FIXME: raw_input_async still is a blocking call. Have found no way to
        # avoid it. Reason: readline initiates a system call that I have no
        # clue to get out of.
        user_input, key_seq = raw_input_async(config.settings['ui']['prompt'])
        # HACK: Temporarily disabled for debugging
        #vt100.lock_keyboard()
        ## HACK: Display the user's input
        #print_out(str(user_input.encode('unicode_escape'), 'ascii') if user_input else '')

        # An empty string is a valid empty
        # If the input was a control signal split might just remove it
        cmd, *args = user_input if user_input else key_seq
        # Run the appropriate mode's processing function
        cmd_processor_fn = command_switcher.get(state)

        try:
            state, update_msg = cmd_processor_fn(cmd, args)
            if update_msg:
                print_out(update_msg)
        except session.UnknownCommandError as e:
            print_error('Unknown command: {u1}{cmd}{u0}', cmd=repr_str(e.expression))
        except session.BadArgsError as e:
            print_error('Command "{u1}{cmd}{u0}" cannot be initiated with the arguments provided.\n{msg}', cmd=e.expression, msg=e.message)
        except session.BadConfigError as e:
            print_error('The command encountered errors with the provided arguments.\n{u1}{cmd}{u0}: {msg}.', cmd=e.expression, msg=e.message)
        except session.CommandFailedError as e:
            print_error('The command encountered an error and did not run properly.\n{u1}{cmd}{u0}: {msg}.', cmd=e.expression, msg=e.message)
        except session.CommandImplementationIncompleteError:
            print_error('The implementation of command "{u1}{cmd}{u0}" is not complete yet.', cmd=cmd)
        except KeyboardInterrupt:
            print_error('Action cancelled by the user.')

if __name__ == '__main__':
    # NOTE: Multiple SIGKILLs required to force close.
    raw_input_async.last_kill_sig = None
    try:
        main()
    finally:
        # Clean up the terminal before letting go
        vt100.unlock_keyboard()
        vt100.format.clear_all_chars_attrs()
