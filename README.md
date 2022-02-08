# GDB extension for event-based debugging

---

## The idea
In programming it is common task to debug someone other's code, and it could be quite complicated to catch the moment, when something goes wrong, by looking through the code that you don't understand, especially if there are no comments. It is not the best experience in programming... So this little extension with a couple of pyhton scripts and embedded Python interpretor in GDB may enhance your debugging experience. The idea is to specify the behaviour that, as you expect, will be triggered during the program is running, and ```debug-until``` will run through the code, until the specified event will be triggered, so a pretty-formatted message will be printed on the screen.

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
debug-until [<starting breakpoint>] [--args=<inferior args>] [<--step-in>]
            [-r=<number of times program should be executed>] 
                [[--cmp=<shell command> --exp=<expected output>]
                 [--file-created=<file>]
                 [--file-deleted=<file>]
                 [--var-eq=<variable>:<expected value>]]
                [--end=<ending breakpoint>]
```

### Some usage remarks:

***[starting breakpoint]*** - should be passed in the format that is accepted by GDB (e.g. ```<filename>:<line>``` or ```<function name>```).  

***[inferior args]*** - arguments for GDB's ```run``` command required run debugged program.  

***[shell command]*** - the shell command that will be executed after each line of code.  
The output of the shell command will be compared with *expected output* and in case if they are equal ```debug-until``` will report about triggering of an event.

***[<--step-in>]*** - by default ```debug-until``` uses the GDB's ```next``` command to iterate through your code. Add this option to switch from ```next``` to ```step``` command.

##### * run ```debug-until --help``` to get usage info in the terminal.

## Example:

if you want to catch the moment when some variable in your code will have a specific value, you can simply run:
```
debug-until main --args="" --var-eq="my_var:10"
```
inside GDB.

So, the command above will create a breakpoint in 'main' function, run the inferior program without arguments and wait until the variable, called 'my_var', will contain value 10. 'Debug-until' will iterate through each line of your code and report to you, when the condition will return true. 

Some more examples can be found at [examples.md](https://github.com/Viaceslavus/gdb-debug-until/blob/master/examples.md)
