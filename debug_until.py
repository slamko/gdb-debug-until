from enum import Enum

cmd = ''
exp = ''
start_point = None

def get_arg_value(args):
    return args.split('=')[1]


class DB_STATUS(Enum):
    COMPLETED = 0
    RUNNING = 1


class EX_CODE(Enum):
    SUCCESS = 0
    FAIL = 1


def finish_debug():
	gdb.events.stop.disconnect(check_st)
	gdb.events.exited.disconnect(check_st)
	global start_point
	start_point.delete()
	gdb.execute("shell rm log.txt")


def run():
	global cmd 
	global exp
	shell_cmd = '{0} > log.txt 2>&1'.format(cmd)
	gdb.execute(shell_cmd, from_tty=True, to_string=True)
	res = open("log.txt").read()

	if exp == res or res.startswith(exp):
		gdb.write(' \n')
		gdb.write('-------------------\n')
		gdb.write('Event triggered!\n')
		gdb.write('-------------------\n')
		gdb.write(' \n')
		gdb.execute('continue')
		finish_debug()
	else:
		gdb.execute('next')


def check_st(event):
		global cmd
		global exp
		if hasattr (event, 'breakpoints'):
			run()
		elif hasattr (event, 'inferior'):
			finish_debug()
		else:
			run()
	

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
		global start_point
		start_point = gdb.Breakpoint(args[0])
			
		start_debug(args)
		
		if '--args' not in arg:
			gdb.execute('run')
		else:
			p_args = get_arg_value(args[1])
			gdb.execute('run {0}'.format(p_args))

DebugUntil()
