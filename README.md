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
debug-until [<starting breakpoint>] [--args=<inferior args>] [[--cmp=<shell command> --exp=<expected output>]
                                                              [--file-created=<file>]
                                                              [--file-deleted=<file>]]
```

***[starting break point]*** - should be passed in the format that is accepted by GDB (e.g. ```<filename>:<line>``` or ```<function name>```).  
***[inferior args]*** - arguments for GDB's ```run``` command required run debugged program.  
***[shell command]*** - the shell command that will be executed after each line of code.  
The output of the shell command will be compared with *expected output* and in case is they are equal ```debug-until``` will report about triggering of an event. 
