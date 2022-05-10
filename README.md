# GDB extension for event-based debugging

---

## The idea
It is common task to debug someone other's code, and it could be quite complicated to catch the moment, when something goes wrong, by looking through the code that you don't understand, especially if there are no comments. So this little extension with a couple of pyhton scripts and embedded Python interpretor in GDB may enhance your debugging experience. The idea is to specify the behaviour that, as you expect, will be triggered during the program is running, and ```debug-until``` will run through the code, until the specified event will be triggered, so a pretty-formatted message will be printed on the screen.

</br>

## Getting started
For a quick start you can clone this repo into your current working directory:
```
git clone https://github.com/Viaceslavus/gdb-debug-until.git
```

And run the following gdb command:
```
source gdb-debug-until/debug_until.py
```

To make this extension running every time GDB does, you can add the last command into the ```.gdbinit``` file located in your home directory (if you are on Linux), 
specifying the correct path to the python script.

  
## Usage: 

```
  debug-until <starting breakpoint> [options] [event]

  <starting breakpoint> - should be passed in the format that is accepted by GDB
  (e.g. <filename>:<line> or <function name>)

 Options:
        --args=<inferior args> : arguments to be passed to GDB`s "run" command
        --step-in              : by default debug-until uses the GDB`s "next" command
                                 to iterate through your code.
                                 Add this option to switch from "next" to "step" command

        -r=<num>               : number of times the program should be executed
        -i                     : iterate through assembly code by instruction.

 Events
        --cmp=<shell command> && --exp=<expected output> (Should be used together)
                : <shell command> - the shell command that will be executed after each line of code
                  The output of the <shell command> will be compared with an <expected output>

        --file-created=<file>  : run until the specified file created
        --file-deleted=<file>  : run until the specified file created
        --var-eq=<var>:<val>   : run until the value of variable <var> equals <val>
        --end=<end breakpoint> : run until end brakpoint

```

##### * run ```debug-until --help``` to get usage info in the terminal.

## Example:

if you want to catch the moment when some variable in your code will have a specific value, you can simply run:
```
debug-until main --args="" --var-eq="my_var:10"
```
inside GDB.

So, the command above will create a breakpoint in 'main' function, run the inferior program without arguments and wait until the variable, called 'my_var', will contain value 10. 'Debug-until' will iterate through each line of your code and report to you, when the condition will return true. 

Some more examples can be found at [examples.md](https://github.com/Viaceslavus/gdb-debug-until/blob/master/examples.md)
