import sys

from string import Template
from subprocess import check_output, CalledProcessError
from glob import glob

python_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)

try:
    tag = check_output([
        'git',
        '--no-pager',
        'describe',
        '--abbrev=0',
        '--tags',
    ]).strip().decode()
except CalledProcessError as e:
    print(e.output)
    tag = 'v0.0.0'

version = tag[1:]

with open('./conda-pkg/meta.yaml.tpl') as r:
    tpl = Template(r.read())
    with open('./conda-pkg/meta.yaml', 'w') as w:
        w.write(tpl.substitute(
            version=version,
            python_version=python_version,
        ))


with open('./conda-pkg/bld.bat.tpl') as r:
    wheel = glob('./dist/*.whl')
    tpl = Template(r.read())
    with open('./conda-pkg/bld.bat', 'w') as w:
        w.write(tpl.substitute(
            wheel=wheel[0],
        ))
