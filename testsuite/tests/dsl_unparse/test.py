"""
Test that dsl_unparse does not crash on libadalang.
"""
import os
from os import path as P
import subprocess
import sys


unparse_dest = os.path.abspath('lal.lkt')
unparse_script = 'to:{},lexer,grammar,nodes'.format(unparse_dest)

subprocess.check_call(
    [sys.executable,
     os.path.join(os.environ['LIBADALANG_ROOTDIR'], 'manage.py'),
     'generate',
     '-v=none', '-E', '--unparse-script', unparse_script,

     # The call to "generate" will generate not only the concrete DSL, but also
     # the Ada sources. Target a build directory that is local to this
     # testcase's working directory to avoid messing with the sources of the
     # library we are currently testing, as this could trigger parallel
     # compilations of Libadalang, leading to obscure failures.
     '--build-dir', os.path.abspath('build')]
)

try:
    with open(unparse_dest, 'r') as lkt_file:
        next(lkt_file)
    print("Successfully unparsed libadalang.")
except IOError:
    print("{} not found, unparsing libadalang failed.".format(
        unparse_dest
    ))
except StopIteration:
    print("{} is empty, unparsing libadalang failed.".format(
        unparse_dest
    ))

sys.stdout.flush()
subprocess.check_call(
    [
        P.join(
            os.environ['LIBADALANG_ROOTDIR'],
            'langkit',
            'contrib',
            'lkt',
            'build',
            'obj-mains',
            'dev',
            'lkt_parse',
        ),
        '-s',
        '-f',
        unparse_dest,
    ]
)
