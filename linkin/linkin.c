#include "linkin.h"

#include <stddef.h>

#include <luajit/lauxlib.h>

static int linkin_searcher(lua_State *L)
{
    const char *name = luaL_checkstring(L, 1);

    // get linkin.lib[name]
    lua_getglobal(L, "linkin");
    if (!lua_istable(L, -1)) {
        lua_pop(L, 1);
        return luaL_error(L, "linkin table not found");
    }

    lua_getfield(L, -1, "lib");
    lua_getfield(L, -1, name);

    if (lua_isstring(L, -1)) {
        size_t len;
        const char *code = lua_tolstring(L, -1, &len);
        lua_pop(L, 3);

        if (luaL_loadbuffer(L, code, len, name) != LUA_OK) {
            return luaL_error(L, "error loading module '%s' (%s)", name,
                              lua_tostring(L, -1));
        }

        return 1;
    } else if (lua_iscfunction(L, -1)) {
        lua_CFunction func = lua_tocfunction(L, -1);
        lua_pop(L, 3);
        lua_pushcfunction(L, func);
        return 1;
    } else if (lua_isfunction(L, -1)) {
        lua_remove(L, -2);
        lua_remove(L, -2);
        return 1;
    }

    lua_pop(L, 3);
    return luaL_error(L, "library '%s' not found", name);
}

static const luaL_Reg linkin_lib[] = {{"searcher", linkin_searcher},
                                      {NULL, NULL}};

int luaopen_linkin(lua_State *L)
{
    luaL_newlib(L, linkin_lib);
    lua_newtable(L);
    lua_setfield(L, -2, "lib");

    lua_pushvalue(L, -1);
    lua_setglobal(L, "linkin");

    return 1;
}

void linkin_openlib(lua_State *L)
{
    // package.preload['linkin'] = luaopen_linkin
    lua_getglobal(L, "package");
    lua_getfield(L, -1, "preload");
    lua_pushcfunction(L, luaopen_linkin);
    lua_setfield(L, -2, "linkin");

    lua_pop(L, 2);
}

void linkin_install_searcher(lua_State *L)
{
    luaL_dostring(L, "linkin = require(\"linkin\")\n"
    "table.insert(package.searchers, linkin.searcher)\n");
}

void linkin_lib_add_by_code(lua_State *L, const char *name, const char *code, size_t code_len)
{
    // linkin.lib[name] = code
    lua_getglobal(L, "linkin");
    lua_getfield(L, -1, "lib");
    lua_pushlstring(L, code, code_len);
    lua_setfield(L, -2, name);
    lua_pop(L, 2);
}

void linkin_lib_add_by_cfunction(lua_State *L, const char *name, lua_CFunction func)
{
    // linkin.lib[name] = func
    lua_getglobal(L, "linkin");
    lua_getfield(L, -1, "lib");
    lua_pushcfunction(L, func);
    lua_setfield(L, -2, name);
    lua_pop(L, 2);
}