#!/usr/bin/env python
import os, distutils.sysconfig
base = distutils.sysconfig.get_python_lib()
def _rm(name):
	try:
		os.remove(name)
	except (OSError,IOError),e:
		print e
def _rmdir(name):
	try:
		os.removedirs(name)
	except (OSError,IOError),e:
		print e
print '''Uninstallation of PyLog version 2.0
Author: Christophe Delord
Email : christophe.delord@free.fr
Web   : http://christophe.delord.free.fr/en/pylog/
'''
_rm('%s/pylog.py'%base)
_rm('%s/PyLog/License.txt'%base)
_rm('%s/PyLog/pylogsrc.py'%base)
_rm('%s/PyLog/examples/test_unification.py'%base)
_rm('%s/PyLog/examples/likes.py'%base)
_rm('%s/PyLog/examples/path.py'%base)
_rmdir('%s/PyLog/examples'%base)
_rmdir('%s/PyLog'%base)
_rm('%s/uninstall-PyLog-2.0.py'%base)
