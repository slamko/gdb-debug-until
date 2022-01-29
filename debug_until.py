import gdb
import os
from enum import Enum

cmd = ''
exp = ''
start_point = None
end_point = None
triggered = 0
break_hit = 0
subscribed = 0
runable_after_exit = 1
rec = 1
iter = 0
observing_mode = 0
arg_dict = {}

LOG_FILE = 'log.txt'
CMD = 'debug-until'

NEXT = 'next'
CONTINUE = 'continue'
RUN = 'run'
LS_ERR = 'ls: cannot access'
PRINT = 'print '
SHELL = 'shell'

HELP = '--help'
ARGS = '--args'
EXP = '--exp'
CMP = '--cmp'
FILE_CREATED = '--file-created'
FILE_DELETED = '--file-deleted'
REC = '-r'
VAR_EQ = '--var-eq'
END = '--end'

commands = []
commands.append(HELP)
commands.append(ARGS)
commands.append(EXP)
commands.append(CMP)
commands.append(FILE_CREATED)
commands.append(FILE_DELETED)
commands.append(VAR_EQ)
commands.append(REC)
commands.append(END)


def get_arg_value(key):
	arg = get_arg(key)
	arr = arg.split('=')
	if len(arr) == 2 and arr[1]:
		return arr[1]
	else:
		key_arr = arg.split(key)
		if not key_arr[1]:
			finish_debug('"{0}" parameter wasn`t assinged.'.format(key))
		else: 
			return key_arr[1]


class DEBUG_ST(Enum):
	COMPLETED = 0
	RUNNING = 1


def check_file_exist():
	global exp
	return os.path.isfile(exp)


def cmp_command_output():
	res = run_shell_command()
	global exp
	return exp == res or res.startswith(exp)


def cmp_var():
	res = run_shell_command()
	res_val = res.split('=')[1].strip().strip()
	global exp
	return exp == res_val


def die(error):
	if error:
		raise gdb.GdbError('error: ' + error)


def event_triggered():
	gdb.write('\n----------------\n')
	gdb.write('Event triggered!\n')
	gdb.write('----------------\n \n')


def report_debug_failure():
	gdb.write('\n-------------------------------------------------------------\n')
	gdb.write('Passed condition wasn`t met. Try setting different parameters\n')
	gdb.write('-------------------------------------------------------------\n \n')

def print_usage():
	gdb.write('Usage:\n')
	gdb.write('debug-until [<starting breakpoint>] [--args=<inferior args>] [-r=<number of times program should be executed>] \n')
	gdb.write('                                                             [[--cmp=<shell command> --exp=<expected output>]\n')
	gdb.write('                                                              [--file-created=<file>]\n')
	gdb.write('                                                              [--file-deleted=<file>]\n')
	gdb.write('                                                              [--var-eq=<variable>:<expected value>]]\n\n')
	gdb.write('[starting break point] - should be passed in the format that is accepted by GDB\
(e.g. <filename>:<line> or <function name>).\n')
	gdb.write('[inferior args] - arguments for GDB`s run command required run debugged program.\n')
	gdb.write('[shell command] - the shell command that will be executed after each line of code.\n')
	gdb.write('The output of the <shell command> will be compared with <expected output>\
and in case if they are equal debug-until will report about triggering of an event.\n')
	gdb.write('\nGet more info on https://github.com/Viaceslavus/gdb-debug-until\n')


def print_full_info():
	gdb.write('\Decription:\n')
	gdb.write('\nDebug through the code until the passed event will be triggered.\n\n')
	print_usage()

def run_shell_command():
	try:
		if cmd.startswith(SHELL):
			shell_cmd = '{0} > {1} 2>&1'.format(cmd, LOG_FILE)
			gdb.execute(shell_cmd, from_tty=True, to_string=True)
			return open(LOG_FILE).read()
		else:
			return gdb.execute(cmd, from_tty=True, to_string=True)
	except Exception:
		pass
	

def condition_satisfied():
	gdb.write('\nCondition is already satisfied\n')


def get_triggered():
	global triggered
	return triggered


def dispose():
	global subscribed
	global triggered
	global cmd
	global exp
	global start_point
	global rec
	global iter
	global comparer
	global arg_dict
	global runable_after_exit
	global break_hit
	global end_point
	global observing_mode

	if subscribed:
		global handler
		gdb.events.stop.disconnect(handler)
		gdb.events.exited.disconnect(handler)

	global start_point
	if start_point != None:
		start_point.delete()

	if end_point != None:
		end_point.delete()

	if os.path.isfile(LOG_FILE):
		gdb.execute('shell rm ' + LOG_FILE)
		
	gdb.execute('set pagination on')
	subscribed = 0
	triggered = 0
	rec = 1
	iter = 0
	break_hit = 0
	observing_mode = 0
	runable_after_exit = 1
	cmd = ''
	exp = ''
	start_point = None
	end_point = None
	arg_dict = {}
	comparer = cmp_command_output


def finish_debug(error_msg=None):
	dispose()
	die(error_msg)


def try_trig_event():
	global triggered
	if not triggered: 
		event_triggered()
		triggered = 1
		gdb.execute(NEXT)
		gdb.execute(CONTINUE)


def run():
	if comparer():
		try_trig_event()
	else:
		gdb.execute(NEXT)


def finish():
	global observing_mode
	if not observing_mode:
		report_debug_failure()
	finish_debug()


def check_st(event):
		global break_hit
		if hasattr(event, 'breakpoints'):
			break_hit = 1
			if end_point != None:
				if event.breakpoints[0].location == end_point.location:
					gdb.execute(CONTINUE)
					return
			run()
		elif hasattr(event, 'inferior'):
			if not break_hit:
				gdb.write('error: Breakpoint wasn`t initialized.\n')
				finish_debug()
			else: 
				break_hit = 0
				global runable_after_exit
				if not triggered:
					global iter
					global rec
					if runable_after_exit:
						if comparer():
							try_trig_event()
						elif rec <= iter + 1:
							finish()
					else: 
						if rec <= iter + 1:
							finish()
		else:
			run()


def subscribe():
	event_subscribe()
	return DEBUG_ST.RUNNING


def check_if_true_on_start():
	if comparer():
			condition_satisfied()
			finish_debug()
			return DEBUG_ST.COMPLETED
		
	return subscribe()
	
handler = check_st

comparer = cmp_command_output

def event_subscribe():
	global handler
	global subscribed 
	subscribed = 1
	gdb.events.stop.connect(handler)
	gdb.events.exited.connect(handler)


def start_debug():
	global cmd 
	global exp
	global comparer

	if has_arg(CMP) and has_arg(EXP):
		cmd = get_arg_value(CMP)
		exp = get_arg_value(EXP)
		comparer = cmp_command_output

		return check_if_true_on_start()
	elif has_arg(FILE_CREATED):
		target_file = get_arg_value(FILE_CREATED)
		exp = target_file
		comparer = check_file_exist

		return check_if_true_on_start()
	elif has_arg(FILE_DELETED):
		target_file = get_arg_value(FILE_DELETED)
		exp = LS_ERR
		comparer = lambda : not check_file_exist()

		return check_if_true_on_start()
	elif has_arg(VAR_EQ):
		arg = get_arg_value(VAR_EQ)
		var = arg.split(':')[0]
		val = arg.split(':')[1]
		cmd = PRINT + var
		exp = val
		global runable_after_exit
		runable_after_exit = 0
		comparer = cmp_var

		return subscribe()
	elif has_arg(END):
		end_p = get_arg_value(END)
		global end_point
		end_point = gdb.Breakpoint(end_p)
		global observing_mode
		observing_mode = 1
		comparer = lambda : False

		return subscribe()
	else:
		gdb.write('error: The event isn`t specified.\n\n')
		print_usage()
		return DEBUG_ST.COMPLETED


def get_arg(com):
	global arg_dict
	return arg_dict.get(com)


def has_arg(com):
	return get_arg(com) is not None


def args_to_dictionary(args):
	global arg_dict
	global commands
	for arg in args:
		for com in commands:
			if arg is not None and arg.startswith(com):
				arg_dict.setdefault(com, arg)
				break


class DebugUntil (gdb.Command):
	def __init__(self):
		super(DebugUntil, self).__init__(CMD, gdb.COMMAND_USER)


	def complete(self, text, word):
		finish_debug()


	def invoke(self, arg, from_tty):
		if not arg:
			print_full_info()
			return
				
		args = gdb.string_to_argv(arg)
		args_to_dictionary(args)

		if has_arg(HELP):
			print_full_info()
			return

		global rec
		if has_arg(REC):
			rec = int(get_arg_value(REC))
			if rec <= 0:
				finish_debug('invalid "-r" parameter.')
				return
		
		if start_debug() == DEBUG_ST.COMPLETED:
			finish_debug()
			return

		global start_point
		start_point = gdb.Breakpoint(args[0])

		gdb.execute('set pagination off')
		global iter
		if not has_arg(ARGS):
			for it in range(0, rec):
				if get_triggered():
					break

				iter = it
				gdb.execute(RUN)
		else:
			p_args = get_arg_value(ARGS)
			for it in range(0, rec):
				if get_triggered():
					break

				iter = it
				gdb.execute(RUN + ' ' + p_args)
		finish_debug()

DebugUntil()
