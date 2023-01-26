#!/bin/bash

cd $1
rm -rf ikfastpy
git clone https://github.com/andyzeng/ikfastpy.git
cd ikfastpy
{
  python setup.py build_ext --inplace
} || {
  python3 setup.py build_ext --inplace
}
