#!/bin/sh

# build dolua
set -x
workdir=$(pwd)

# first, build the luajit
export LUAJIT_SRC_ROOT=/path/to/LuaJIT
ln -s $LUAJIT_SRC_ROOT/src ./luajit

# second, build the luasocke, install to $LUASOCKET_SRC_ROOT/src/installdir
export LUASOCKET_SRC_ROOT=/path/to/luasocket
ln -s $LUASOCKET_SRC_ROOT/src ./luasocket
cd ./luasocket && ar rcs libluasocket.a *.o

# then, convert luasocket *.lua to *.h
cd $workdir
python3 ../lua2lib.py --luajit luajit/luajit ./luasocket/installdir/share/lua/5.1/  ./lua2lib

# finally, build dolua
gcc -static -o dolua dolua.c ../linkin/linkin.c -I.. -I. -L./luajit -lluajit -lm -ldl -L./luasocket -lluasocket
