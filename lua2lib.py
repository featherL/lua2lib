import argparse
import os
import sys
import subprocess


class LuaJit:
    def __init__(self, bin_path):
        if '/' in bin_path:
            self.bin_path = os.path.abspath(bin_path)
            self.env = {'LUA_PATH': os.path.dirname(self.bin_path) + os.sep + '?.lua;;'}
        else:
            # search from PATH
            self.bin_path = None
            for p in os.environ.get('PATH').split(':'):
                path = os.path.join(p, bin_path)
                if os.path.exists(path):
                    self.bin_path = path
                    break

            self.env = None

    def compile(self, lua_file, mod_name):
        try:
            return subprocess.check_output([self.bin_path, '-b', lua_file, '-n', mod_name, '-t', 'raw', '-'], env=self.env)
        except subprocess.CalledProcessError as e:
            return None


class LuaObject:
    def __init__(self, file_path, byte_code, mode_name):
        self.file_path = file_path
        self.byte_code = byte_code
        self.mode_name = mode_name


class Lua2Lib:
    def __init__(self, input_dir, luajit='luajit', prefix=''):
        self.input_dir = os.path.abspath(input_dir)
        self.luajit = LuaJit(luajit)
        self.prefix = prefix
        self.info = []

    def byte_code_to_c_array(self, byte_code):
        return '{' + ', '.join(["0x{:02X}".format(b) for b in byte_code]) + '}'
    

    def generate_code(self):
        if not self.info:
            self.compile_all()

        code = '#include "linkin/linkin.h"\n\n'

        vars_code = ''
        var_template = 'static const unsigned char {}[] = {};\n\n'

        install_code = 'static void {}_install_all(lua_State *L)\n{{\n'.format(self.prefix)

        for obj in self.info:
            var_name = self.prefix + '_' + obj.mode_name.replace('.', '_') + '_bc'
            byte_code = self.byte_code_to_c_array(obj.byte_code)
            vars_code += var_template.format(var_name, byte_code)

            install_code += '    linkin_lib_add_by_code(L, "{}", {}, sizeof({}));\n'.format(obj.mode_name, var_name, var_name)

        install_code += '}'

        code += vars_code + install_code

        return code

    def compile_all(self):
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith('.lua'):
                    lua_file = os.path.join(root, file)
                    relative_path = os.path.relpath(lua_file, self.input_dir)
                    mod_name = os.path.splitext(relative_path)[0].replace(os.sep, '.')
                    byte_code = self.luajit.compile(lua_file, mod_name)

                    if not byte_code:
                        print("Error compiling {}".format(lua_file), file=sys.stderr)
                        continue

                    self.info.append(LuaObject(lua_file, byte_code, mod_name))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Lua to C header files for build library")
    parser.add_argument("--luajit", default='luajit',help="luajit executable path")
    parser.add_argument("--prefix", default='',help="prefix for generated code")
    parser.add_argument("inputdir", help="input lua directory")
    parser.add_argument("output", help="output c header file")
    args = parser.parse_args()

    l = Lua2Lib(args.inputdir, args.luajit, args.prefix)
    code = l.generate_code()

    if args.output == '-':
        print(code)
    else:
        with open(args.output, 'w') as f:
            f.write(code)

