#!/usr/bin/env python
import shutil, os, distutils.sysconfig
base = distutils.sysconfig.get_python_lib()
def _mkdir(path):
	try:
		os.makedirs(path)
	except (OSError,IOError),e:
		print e
def _cp(src,dst):
	try:
		shutil.copyfile(src,dst)
	except (OSError,IOError),e:
		print e
def _chmod(mod,dst):
	try:
		os.chmod(dst,mod)
	except (OSError,IOError),e:
		print e
print '''Installation of PyLog version 2.1
Author: Christophe Delord
Email : christophe.delord@free.fr
Web   : http://christophe.delord.free.fr/en/pylog/
'''
_cp('pylog.py','%s/pylog.py'%base)
_mkdir('%s/PyLog'%base)
_cp('PyLog/License.txt','%s/PyLog/License.txt'%base)
_cp('PyLog/pylogsrc.py','%s/PyLog/pylogsrc.py'%base)
_mkdir('%s/PyLog/examples'%base)
_cp('PyLog/examples/test_unification.py','%s/PyLog/examples/test_unification.py'%base)
_cp('PyLog/examples/likes.py','%s/PyLog/examples/likes.py'%base)
_cp('PyLog/examples/path.py','%s/PyLog/examples/path.py'%base)
