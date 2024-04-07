#ifndef LUA2LIB_LUALINKIN_H_
#define LUA2LIB_LUALINKIN_H_

#include <stddef.h>
#include <luajit/luajit.h>

#define LUA_LINKIN "linkin"

LUALIB_API int luaopen_linkin(lua_State *L);

LUALIB_API void linkin_openlib(lua_State *L);


// install linkin library into the global table
void linkin_install(lua_State *L);

void linkin_install_searcher(lua_State *L);

void linkin_lib_add_by_code(lua_State *L, const char *name, const void *code, size_t code_len);

void linkin_lib_add_by_cfunction(lua_State *L, const char *name, lua_CFunction func);





#endif  // LUA2LIB_LUALINKIN_H_