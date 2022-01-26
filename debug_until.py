import gdb
import os
import sys
from enum import Enum

cmd = ''
exp = ''
start_point = None
triggered = 0
subscribed = 0
rec = 1
iter = 0

LOG_FILE = 'log.txt'
CMD = 'debug-until'

NEXT = 'next'
CONTINUE = 'continue'
RUN = 'run'
LS_ERR = 'ls: cannot access'

HELP = '--help'
ARGS = '--args'
EXP = '--exp'
CMP = '--cmp'
FILE_CREATED = '--file-created'
FILE_DELETED = '--file-deleted'


def get_arg_value(args, key):
	arr = args.split('=')
	if len(arr) == 2 and arr[1]:
		return arr[1]
	else:
		key_arr = args.split(key)
		if not key_arr[1]:
			finish_debug('"{0}" parameter wasn`t assinged.'.format(key))
		else: 
			return key_arr[1]


class DB_STATUS(Enum):
	COMPLETED = 0
	RUNNING = 1


def cmp_output(res):
	global exp
	return exp == res or res.startswith(exp)

def die(error):
	if error:
		raise gdb.GdbError('error: ' + error)

def event_triggered():
	gdb.write('\n--------------\n')
	gdb.write('Event triggered!\n')
	gdb.write('----------------\n \n')


def report_debug_failure():
	gdb.write('\n-------------------------------------------------------------\n')
	gdb.write('Passed condition wasn`t met. Try setting different parameters\n')
	gdb.write('-------------------------------------------------------------\n \n')


def print_usage():
	gdb.write('\Decription:\n')
	gdb.write('\nDebug through the code until the passed event will be triggered.\n\n')
	gdb.write('Usage:\n')
	gdb.write('debug-until [<starting breakpoint>] [--args=<inferior args>] [[--cmp=<shell command> --exp=<expected output>]\n')
	gdb.write('                                                              [--file-created=<file>]\n')
	gdb.write('                                                              [--file-deleted=<file>]\n\n')
	gdb.write('[starting break point] - should be passed in the format that is accepted by GDB \
		(e.g. <filename>:<line> or <function name>).\n')
	gdb.write('[inferior args] - arguments for GDB`s run command required run debugged program.\n')
	gdb.write('[shell command] - the shell command that will be executed after each line of code.\n')
	gdb.write('The output of the <shell command> will be compared with <expected output> \
		and in case is they are equal debug-until will report about triggering of an event.\n')


def run_shell_command():
	shell_cmd = '{0} > {1} 2>&1'.format(cmd, LOG_FILE)
	gdb.execute(shell_cmd, from_tty=True, to_string=True)
	return open(LOG_FILE).read()


def condition_satisfied():
	gdb.write('\nCondition is already satisfied\n')


def dispose():
	global subscribed
	global triggered
	global cmd
	global exp
	global start_point
	global rec
	global iter

	if subscribed:
		global handler
		gdb.events.stop.disconnect(handler)
		gdb.events.exited.disconnect(handler)

	global start_point
	if start_point != None:
		start_point.delete()

	if os.path.isfile(LOG_FILE):
		gdb.execute('shell rm ' + LOG_FILE)
		
	gdb.execute('set pagination on')
	subscribed = 0
	triggered = 0
	rec = 1
	iter = 0
	cmd = ''
	exp = ''
	start_point = None


def finish_debug(error_msg=None):
	dispose()
	die(error_msg)


def check_trig_event():
	global triggered
	if not triggered: 
		event_triggered()
		triggered = 1
		gdb.execute(NEXT)
		gdb.execute(CONTINUE)
		finish_debug()


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

			global iter
			global rec
			if cmp_output(res):
				check_trig_event()
			elif rec <= iter + 1:
				report_debug_failure()
				finish_debug()
		else:
			run()


def check_if_true_on_start(res):
	if cmp_output(res):
			condition_satisfied()
			return DB_STATUS.COMPLETED
		
	event_subscribe()
	return DB_STATUS.RUNNING
	
handler = check_st

def event_subscribe():
	global handler
	global subscribed 
	subscribed = 1
	gdb.events.stop.connect(handler)
	gdb.events.exited.connect(handler)


def start_debug(args):
	global cmd 
	global exp
	args_len = len(args) 

	if CMP in args[args_len - 2] and EXP in args[args_len - 1]:
		cmd = get_arg_value(args[args_len - 2], CMP)
		exp = get_arg_value(args[args_len - 1], EXP)
		res = run_shell_command()

		return check_if_true_on_start(res)
	elif FILE_CREATED in args[args_len - 1]:
		target_file = get_arg_value(args[args_len - 1], FILE_CREATED)
		cmd = 'shell ls ' + target_file
		exp = target_file
		res = run_shell_command()

		return check_if_true_on_start(res)
	elif FILE_DELETED in args[args_len - 1]:
		target_file = get_arg_value(args[args_len - 1], FILE_DELETED)
		cmd = 'shell ls ' + target_file
		exp = LS_ERR
		res = run_shell_command()

		return check_if_true_on_start(res)
	else:
		gdb.write('error: Some parameters aren`t specified.\n')
		print_usage()
		return DB_STATUS.COMPLETED


class DebugUntil (gdb.Command):
	def __init__(self):
		super(DebugUntil, self).__init__(CMD, gdb.COMMAND_USER)


	def invoke(self, arg, from_tty):
		if not arg:
			print_usage()
			return
				
		gdb.execute('set pagination off')
		args = gdb.string_to_argv(arg)

		if HELP in args[0]:
			print_usage()
			return

		if start_debug(args) == DB_STATUS.COMPLETED:
			return

		global rec
		if '-r' in args[2]:
			rec = int(get_arg_value(args[2], '-r'))
		
		global start_point
		start_point = gdb.Breakpoint(args[0])

		global triggered
		global iter
		if ARGS not in arg:
			for it in range(0, rec):
				if triggered:
					break
				if it != rec:
					iter = it
					gdb.execute(RUN)
		else:
			p_args = get_arg_value(args[1], ARGS)
			for it in range(0, rec):
				
				if triggered:
					break
				if it != rec:
					iter = it
					gdb.execute(RUN + ' ' + p_args)

DebugUntil()
