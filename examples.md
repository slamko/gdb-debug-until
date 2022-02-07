## Here are some practical examples of using ```debug-until``` for event-based debugging.
---
- ### ```--cmp``` ; ```--exp```

So, Historically one the first options that were available in this repo were ```--cmp``` and ```--exp```
That is the most flexible way of doing things here. Basically you are just passing a command that should be executed inside GDB and an expected output of that command:

```
debug-until main --cmp="shell ls" --exp="somefile"
```

```shell ls``` command will be executed after each line of your code, and if the output equals or starts with an expected value - event triggering will be reported:
```
(gdb) debug-until main --cmp="shell ls" --exp="dummy"
Breakpoint 1 at 0x1169: file some.c, line 3.

Breakpoint 1, main () at some.c:3
3       int main(void) {
4               int dummy = 0;
5               printf("Hello");
7               if(dummy == 0){
8                       FILE *f = fopen ("dummy", "w");
10              return 0;

----------------
Event triggered!
----------------

11      }
Hello[Inferior 1 (process 38) exited normally]
```

Keep in mind that you should only use ```--cmp``` and ```--exp``` in pair.

Also it worth mentioning that you can short ```debug-until``` to  ```deb``` and write the command like this:
```
deb main --cmp="shell ls" --exp="somefile"
```

- ### ```--file-created``` ; ```--file-deleted```

Here it is pretty simple: you should just give the name of the file that as you exepct will be created or deleted while the program running. 
This option may be useful if you are debugging someone else's code, and you want to figure what part of the program creates/deletes the file.

```
debug-until main --args="" --file-created="myfile.txt"
```

Note that those options do not apply to directories, only regular files.

- ### ```--end```
  
  This option may be used separetely or in conjunction with the others.
  It basically specifies the ending breakpoint, where debugging should be stopped.
  When using separetely this option may be useful to show some part of the programs code:
  ```
  (gdb) deb main --end="some.c:13" -r=2
  Breakpoint 1 at 0x11d3: file some.c, line 13.
  Breakpoint 2 at 0x1180: file some.c, line 3.

  Breakpoint 2, main () at some.c:3
  3       int main(void) {
  4               int dummy = 0;
  5               printf("dummy is 0\n");
  dummy is 0
  11              dummy_void(dummy);
  12              printf("dummy is 0\n");
  dummy is 0
  
  Breakpoint 1, main () at some.c:13
  13              return 0;
  [Inferior 1 (process 103) exited normally]

  Breakpoint 2, main () at some.c:3
  3       int main(void) {
  4               int dummy = 0;
  5               printf("dummy is 0\n");
  dummy is 0
  11              dummy_void(dummy);
  12              printf("dummy is 0\n");
  dummy is 0

  Breakpoint 1, main () at some.c:13
  13              return 0;
  [Inferior 1 (process 107) exited normally]
  ```
  
- ### ```--var-eq``` 

Probably the most useful option here. This one allows you to find the exact place when some variable in your program holds the specified value: 
```
(gdb) deb main --args="" --var-eq="dummy:9"
Breakpoint 1 at 0x1157: file some.c, line 6.

Breakpoint 1, main () at some.c:6
6       int main(void) {
7               int dummy = 0;
8               printf("dummy is 0\n");
dummy is 0
10              printf("dummy is still 0\n");
dummy is still 0
12              if(dummy == 0){
13                      dummy = 9;
14                      get_dummy(dummy);

----------------
Event triggered!
----------------

17              printf("dummy is nine\n");
dummy is nine
[Inferior 1 (process 78) exited normally]
```

### Note that equality sign after the options above may be omitted, but quotes must present if there is more than one word.
```
deb main --args="" --var-eqdummy:9
```

```
deb main --cmp"shell ls" --expsomefile
```

- ## Some other options

  + ```-i``` option basically means that ```debug-until``` gonna use ```nexti``` instead of ```next``` 
    (or ```stepi``` instead of ```step``` if ```--step-in``` option was specified):  
    
    ```
    (gdb) deb main --args="" --var-eqdummy:9 -i
    Breakpoint 1 at 0x1157: file some.c, line 6.

    Breakpoint 1, main () at some.c:6
    6               return 0;
    0x000000000800115b      6               return 0;
    0x000000000800115c      6               return 0;
    0x000000000800115f      6               return 0;
    7       }
    0x0000000008001171      dummy is 0
    0x000000000800117d      dummy is still 0
    0x0000000008001186
    ----------------
    Event triggered!
    ----------------

    0x0000000008001192      dummy is nine
    [Inferior 1 (process 90) exited normally]
    ```
    </br>
    
  + ```-r``` option specifies the number of times the program will be executed (default is 1; in case of negative or 0 value ```debug-until``` returns an error)
