from enum import Enum
import gdb

cmd = ''
exp = ''
start_point = None
triggered = 0

LOG_FILE = 'log.txt'
CMD = 'debug-until'

NEXT = 'next'
CONTINUE = 'continue'
RUN = 'run'
LS_ERR = 'ls: cannot access'


def get_arg_value(args):
    return args.split('=')[1]


class DB_STATUS(Enum):
    COMPLETED = 0
    RUNNING = 1


class EX_CODE(Enum):
    SUCCESS = 0
    FAIL = 1


def cmp_output(res):
	global exp
	return exp == res or res.startswith(exp)


def event_triggered():
	gdb.write('\n----------------\n')
	gdb.write('Event triggered!\n')
	gdb.write('----------------\n \n')


def report_debug_failure():
	gdb.write('\n----------------\n')
	gdb.write('Passed condition wasn`t met. Try setting defferent parameters\n')
	gdb.write('----------------\n \n')


def run_shell_command():
	shell_cmd = '{0} > {1} 2>&1'.format(cmd, LOG_FILE)
	gdb.execute(shell_cmd, from_tty=True, to_string=True)
	return open(LOG_FILE).read()


def condition_satisfied():
	gdb.write('\nCondition is already satisfied\n')


def finish_debug():
	global handler
	gdb.events.stop.disconnect(handler)
	gdb.events.exited.disconnect(handler)
	global start_point
	start_point.delete()
	gdb.execute('shell rm ' + LOG_FILE)


def check_trig_event():
	global triggered
	if triggered == 0: 
		event_triggered()
		triggered = 1
		finish_debug()
		gdb.execute(NEXT)
		gdb.execute(CONTINUE)


def run():
	res = run_shell_command()

	if cmp_output(res):
		check_trig_event()
	else:
		gdb.execute(NEXT)


def check_st(event):
		if hasattr (event, 'breakpoints'):
			run()
		elif hasattr (event, 'inferior'):
			res = run_shell_command()

			if cmp_output(res):
				check_trig_event()
			else:
				report_debug_failure()
				finish_debug()
		else:
			run()
	
handler = check_st

def event_subscribe():
	global handler
	gdb.events.stop.connect(handler)
	gdb.events.exited.connect(handler)

def start_debug(args):
	global cmd 
	global exp
	if '--cmp' in args[2] and '--exp' in args[3]:
		cmd = get_arg_value(args[2])
		exp = get_arg_value(args[3])
		res = run_shell_command()

		if cmp_output(res):
			condition_satisfied()
			return DB_STATUS.COMPLETED
		
		event_subscribe()
		return DB_STATUS.RUNNING
	elif '--file-created' in args[2]:
		target_file = get_arg_value(args[2])
		cmd = 'shell ls ' + target_file
		exp = target_file
		res = run_shell_command()

		if cmp_output(res):
			condition_satisfied()
			return DB_STATUS.COMPLETED
		
		event_subscribe()
		return DB_STATUS.RUNNING
	elif '--file-deleted' in args[2]:
		target_file = get_arg_value(args[2])
		cmd = 'shell ls ' + target_file
		exp = LS_ERR
		res = run_shell_command()

		if cmp_output(res):
			condition_satisfied()
			return DB_STATUS.COMPLETED
		
		event_subscribe()
		return DB_STATUS.RUNNING


class DebugUntil (gdb.Command):
	"""Debug through the function until the passed condition would be met"""

	def __init__(self):
		super(DebugUntil, self).__init__(CMD, gdb.COMMAND_USER)


	def invoke(self, arg, from_tty):
		if not  arg:
			return

		args = gdb.string_to_argv(arg)

		db_st = start_debug(args)
		if db_st == DB_STATUS.COMPLETED:
			return
		
		global start_point
		start_point = gdb.Breakpoint(args[0])

		if '--args' not in arg:
			gdb.execute(RUN)
		else:
			p_args = get_arg_value(args[1])
			gdb.execute(RUN + ' ' + p_args)

DebugUntil()
