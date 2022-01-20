from enum import Enum

cmd = ''
exp = ''

def get_arg_value(args):
    return args.split('=')[1]

class DB_STATUS(Enum):
    COMPLETED = 0
    RUNNING = 1


class EX_CODE(Enum):
    SUCCESS = 0
    FAIL = 1


def run(cmd, exp):
	gdb.write(cmd)
	res = gdb.execute(cmd, from_tty=False, to_string=True)
	if exp in res:
		gdb.write('success!')
		gdb.execute('continue')
	else:
		gdb.execute('next')


def check_st(event):
		global cmd
		global exp
		if hasattr (event, 'breakpoints'):
			run(cmd, exp)
		elif hasattr (event, 'exit_code'):
			gdb.events.stop.disconnect(check_st)
			gdb.events.exited.disconnect(check_st)
		else:
			run(cmd, exp)
	

def start_debug(args):
	if '--cmp' in args[2] and '--exp' in args[3]:
		global cmd 
		cmd = get_arg_value(args[2])
		global exp 
		exp = get_arg_value(args[3])
		gdb.events.stop.connect(check_st)
		gdb.events.exited.connect(check_st)

class DebugUntil (gdb.Command):
	"""Debug through the function until the passed condition would be met"""

	def __init__(self):
		super(DebugUntil, self).__init__("debug-until", gdb.COMMAND_USER)


	def invoke(self, arg, from_tty):
		if not  arg:
			return

		args = gdb.string_to_argv(arg)
		start_p = args[0]
		gdb.execute('b {0}'.format(start_p))
			
		start_debug(args)
		
		if '--args' not in arg:
			gdb.execute('run')
		else:
			p_args = get_arg_value(args[1])
			gdb.execute('run {0}'.format(p_args))

DebugUntil()
