#include <linkin/linkin.h>
#include <luajit-2.1/lua.h>
#include <luajit/luajit.h>
#include <luajit/lauxlib.h>
#include <luajit/lualib.h>
#include <stdio.h>

#include "lua2lib/install.h"


extern int luaopen_socket_core(lua_State *L);
extern int luaopen_mime_core(lua_State *L);

int main(int argc, char *argv[]) 
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s <lua-script>\n", argv[0]);
        return 1;
    }
    lua_State *L = lua_open();
    luaL_openlibs(L);

    linkin_openlib(L);  // add linkin to package.preload
    linkin_install_searcher(L);  // add linkin.searcher to package.loaders/package.searchers

    _install_all(L);  // install all luasocket *.lua

    // install c modules of luasocket
    linkin_lib_add_by_cfunction(L, "socket.core", luaopen_socket_core);
    linkin_lib_add_by_cfunction(L, "mime.core", luaopen_mime_core);

    // set arg
    lua_createtable(L, argc - 2, 0);
    lua_pushstring(L, argv[1]);
    lua_rawseti(L, -2, 0);

    for (int i = 2; i < argc; i++) {
        lua_pushstring(L, argv[i]);
        lua_rawseti(L, -2, i - 1);
    }
    lua_setglobal(L, "arg");

    if (luaL_dofile(L, argv[1]) != 0) {
        fprintf(stderr, "%s\n", lua_tostring(L, -1));
        return 1;
    }

    lua_close(L);
    return 0;
}
