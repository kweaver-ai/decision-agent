# agent-executor.spec
# -*- mode: python ; coding: utf-8 -*-
# PyInstaller specification file for Agent-Executor

from PyInstaller.utils.hooks import copy_metadata

project_root = os.path.abspath('.')

# Data files to include
datas = [
    ("data_migrations", "data_migrations"),
]
datas += copy_metadata('setuptools')

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pkg_resources',
        'setuptools',
        'setuptools._distutils',
        'opentelemetry.instrumentation.dependencies',
    ],
    excludes=[
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'pip',
        'pylint',
        'coverage',
    ],
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='agent-executor',
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='agent-executor',
)
