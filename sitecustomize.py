# Copyright 2013 SAP AG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http: //www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an 
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific 
# language governing permissions and limitations under the License.

# Patches needed to compile the binary extension on Windows

import sys

if sys.platform.startswith('win'):

    def fixed_mingw32_init(self, verbose=0, dry_run=0, force=0):
        """ Fixed initialization to remove broken -mno-cygwin flag
        """
        from distutils.cygwinccompiler import CygwinCCompiler
        from distutils.cygwinccompiler import get_msvcr
        CygwinCCompiler.__init__ (self, verbose, dry_run, force)

        # ld_version >= "2.13" support -shared so use it instead of
        # -mdll -static
        if self.ld_version >= "2.13":
            shared_option = "-shared"
        else:
            shared_option = "-mdll -static"

        # A real mingw32 doesn't need to specify a different entry point,
        # but cygwin 2.91.57 in no-cygwin-mode needs it.
        if self.gcc_version <= "2.91.57":
            entry_point = '--entry _DllMain@12'
        else:
            entry_point = ''

        self.set_executables(compiler='gcc -O -Wall',
                             compiler_so='gcc -mdll -O -Wall',
                             compiler_cxx='g++ -O -Wall',
                             linker_exe='gcc',
                             linker_so='%s %s %s'
                                        % (self.linker_dll, shared_option,
                                           entry_point))
        # Maybe we should also append -mthreads, but then the finished
        # dlls need another dll (mingwm10.dll see Mingw32 docs)
        # (-mthreads: Support thread-safe exception handling on `Mingw32')

        # no additional libraries needed
        self.dll_libraries=[]

        # Include the appropriate MSVC runtime library if Python was built
        # with MSVC 7.0 or later.
        self.dll_libraries = get_msvcr()


    from distutils.cygwinccompiler import Mingw32CCompiler
    Mingw32CCompiler.__init__ = fixed_mingw32_init
