import argparse
import os
import sys
import subprocess


class Lua2Lib:
    def __init__(self, input_dir, output_dir, luajit, prefix=''):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.luajit = luajit or '/usr/bin/luajit'
        self.luajit = os.path.abspath(self.luajit)
        self.lua_path = os.path.abspath(os.path.dirname(self.luajit)) if luajit else None
        self.prefix = prefix
        self.info = []

    def parse_filename(self, luafile):
        relative_path = os.path.relpath(luafile, self.input_dir)
        relative_dir = os.path.dirname(relative_path)
        mod_name = relative_path.split('.')[0].replace(os.sep, '.')
        
        if self.prefix:
            mod_name = self.prefix + '.' + mod_name

        mod_name_c = mod_name.replace('.', '_')
        var_name = 'luaJIT_BC_{}'.format(mod_name_c)
        var_size = '{}_SIZE'.format(var_name)

        return mod_name, mod_name_c, var_name, var_size, relative_dir
    
    def convert_lua(self, lua_file, output_file, mod_name_c):
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            subprocess.check_call([self.luajit, '-b', lua_file, output_file, '-n', mod_name_c], env={'LUA_PATH': self.lua_path + os.sep + '?.lua;;'} if self.lua_path else None)
        except subprocess.CalledProcessError as e:
            print("Error compiling {}: {}".format(lua_file, e), file=sys.stderr)
    
    def parse(self):
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith('.lua'):
                    lua_file = os.path.join(root, file)
                    
                    mod_name, mod_name_c, var_name, var_size, relative_dir = self.parse_filename(lua_file)
                    output_file = os.path.join(self.output_dir, relative_dir, file.replace('.lua', '.h'))

                    self.convert_lua(lua_file, output_file, mod_name_c)

                    self.info.append({
                        'lua_file': lua_file,
                        'mod_name': mod_name,
                        'mod_name_c': mod_name_c,
                        'var_name': var_name,
                        'var_size': var_size,
                        'output_file': output_file,
                        'include_name': os.path.relpath(output_file, self.output_dir).replace(os.sep, '/')
                    })

                    print("Compiled {} to {}".format(lua_file, output_file))

    def generate_c_code(self):
        template = """
#include "{include_name}"

static void install_{mod_name_c}(lua_State *L)
{{
    linkin_lib_add_by_code(L, "{mod_name}", {var_name}, {var_size});
}}


"""

        header_content = '#include "linkin/linkin.h"\n'
        header_installer = 'static void {}_install_all(lua_State *L)\n{{\n'.format(self.prefix)

        for i in self.info:
            mod_name = i['mod_name']
            var_name = i['var_name']
            var_size = i['var_size']
            include_name = i['include_name']
            mod_name_c = i['mod_name_c']

            tmp = template.format(mod_name=mod_name, var_name=var_name, var_size=var_size, include_name=include_name, mod_name_c=mod_name_c)
            header_content += tmp

            header_installer += '    install_{mod_name_c}(L);\n'.format(mod_name_c=mod_name_c)
        
        header_content += header_installer + '}\n\n'

        with open(os.path.join(self.output_dir, 'install.h'), 'w') as f:
            f.write(header_content)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Lua to C header files for build library")
    parser.add_argument("--luajit", default='',help="luajit executable path")
    parser.add_argument("-m", "--mod", default='', help="module name prefix")
    parser.add_argument("input", help="input lua directory")
    parser.add_argument("output", help="output c library source directory")
    args = parser.parse_args()

    l = Lua2Lib(args.input, args.output, args.luajit, args.mod)
    l.parse()
    l.generate_c_code()


