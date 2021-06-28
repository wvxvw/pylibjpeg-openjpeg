package:
  name: pylibjpeg-openjpeg
  version: ${version}

source:
  path: ..

build:
  binary_relocation: true

requirements:
  host:
    - pip
    - python==${python_version}
    - numpy
    - cython
    - setuptools

  run:
    - python==${python_version}
    - numpy

test:
  requires:
    - numpy
  imports:
    - openjpeg

about:
  home: https://github.com/pydicom/pylibjpeg-openjpeg
  license: MIT
  summary: >
    A Python wrapper for openjpeg, with a focus on use as a plugin for
    pylibjpeg
