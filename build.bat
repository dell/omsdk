attrib -r /s *.Monitor 
attrib -r /s *.json
attrib -r  setup.cfg
rmdir /s/q build
rmdir /s/q dist
rmdir /s/q omsdk.egg-info
python setup-omdrivers.py bdist_wheel --universal 
rmdir /s/q build
rmdir /s/q omdrivers.egg-info
python setup-omsdk.py bdist_wheel --universal 
rmdir /s/q build
rmdir /s/q omsdk.egg-info
rem python setup.py bdist_wheel --universal 
python setup-linux.py bdist_egg
rmdir /s/q build
rmdir /s/q omsdk.egg-info
rem python setup.py sdist --formats=gztar
