#-*-*- encoding: utf-8 -*-*-
from setuptools import setup

classifiers=[
    "Development Status :: 3 - Alpha",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: Freely Distributable",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
]

cp_license="MIT"

setup(name='g4l_rlms_unr',
      version='0.1',
      description="FCEIA/Universidad Nacional del Rosario physics laboratory plug-in in the gateway4labs project",
      classifiers=classifiers,
      author='Pablo Orduña, Federico Lerro',
      author_email='pablo.orduna@deusto.es, flerro2@yahoo.com.ar',
      url='http://github.com/gateway4labs/rlms_unr/',
      license=cp_license,
      py_modules=['g4l_rlms_unr'],
     )
