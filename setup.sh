#!/bin/sh
#
# Installs dependencies for automated grading scripts
# Author: Fil Zembowicz     fil@filosophy.org
#

mkdir -p third_party
cd third_party

# install PLY
wget http://www.dabeaz.com/ply/ply-3.4.tar.gz
tar -xvf ply-3.4.tar.gz
rm -f ply-3.4.tar.gz
cd ply-3.4/
python setup.py install --user
cd ..

# install pycparser
hg clone https://code.google.com/p/pycparser/
cd pycparser/
python setup.py install --user
cd ..

cd ..
python tests.py
