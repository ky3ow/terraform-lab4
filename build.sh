#!/usr/bin/env sh

uv pip install -r src/requirements.txt --target build/python

cd build

zip -r python.zip python
rm -r python

cd -
