# lua2lib
script to compile lua module as C header file by luajit

## Usage

1. compile a third party lua module as static lib named `clib`
    

2. run lua2lib.py for the lua script in third party module named `libheader`
```
python lua2lib.py <third party module/lua> libheader
```

3. compile your program with `libheader`, [linkin](linkin) and static link with `clib`, libluajit

4. and then your program can run any where without lua environment


see more [exmaple](example)


