from enum import Enum
import gdb

cmd = ''
exp = ''
start_point = None
triggered = 0

LOG_FILE = 'log.txt'
GDB_LOG = 'gdblog.txt'

def get_arg_value(args):
    return args.split('=')[1]


class DB_STATUS(Enum):
    COMPLETED = 0
    RUNNING = 1


class EX_CODE(Enum):
    SUCCESS = 0
    FAIL = 1


def finish_debug():
	global handler
	gdb.events.stop.disconnect(handler)
	gdb.events.exited.disconnect(handler)
	global start_point
	start_point.delete()
	gdb.execute('shell rm {0}'.format(LOG_FILE))
	gdb.execute('set logging off')


def run():
	global cmd 
	global exp
	shell_cmd = '{0} > {1} 2>&1'.format(cmd, LOG_FILE)
	gdb.execute(shell_cmd, from_tty=True, to_string=True)
	res = open(LOG_FILE).read()

	if exp == res or res.startswith(exp):
		global triggered
		if triggered == 0: 
			gdb.write(' \n')
			gdb.write('----------------\n')
			gdb.write('Event triggered!\n')
			gdb.write('----------------\n')
			gdb.write(' \n')
			triggered = 1
			finish_debug()
			gdb.execute('next')
			gdb.execute('continue')
	else:
		gdb.execute('next')


def check_st(event):
		if hasattr (event, 'breakpoints'):
			run()
		elif hasattr (event, 'inferior'):
			finish_debug()
		else:
			run()
	
handler = check_st

def start_debug(args):
	if '--cmp' in args[2] and '--exp' in args[3]:
		global cmd 
		cmd = get_arg_value(args[2])
		global exp 
		exp = get_arg_value(args[3])

		shell_cmd = '{0} > {1} 2>&1'.format(cmd, LOG_FILE)
		gdb.execute(shell_cmd, from_tty=True, to_string=True)
		res = open(LOG_FILE).read()
		if res == exp or res.startswith(exp):
			gdb.write(' \n')
			gdb.write('Condition is already satisfied\n')
			return DB_STATUS.COMPLETED
		
		global handler
		gdb.events.stop.connect(handler)
		gdb.events.exited.connect(handler)
		return DB_STATUS.RUNNING


class DebugUntil (gdb.Command):
	"""Debug through the function until the passed condition would be met"""

	def __init__(self):
		super(DebugUntil, self).__init__("debug-until", gdb.COMMAND_USER)


	def invoke(self, arg, from_tty):
		if not  arg:
			return

		gdb.execute('set logging file {0}'.format(GDB_LOG))
		gdb.execute('set logging on')

		args = gdb.string_to_argv(arg)
		global start_point
		start_point = gdb.Breakpoint(args[0])

		db_st = start_debug(args)
		if db_st == DB_STATUS.COMPLETED:
			return
		
		if '--args' not in arg:
			gdb.execute('run')
		else:
			p_args = get_arg_value(args[1])
			gdb.execute('run {0}'.format(p_args))

DebugUntil()
