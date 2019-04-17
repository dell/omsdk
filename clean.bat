@echo off
rmdir /s/q omsdk.egg-info
rmdir /s/q omdrivers.egg-info
rmdir /s/q dist
rmdir /s/q build
for /F %%i in ('dir /s/b __pycache__') do @(
    echo rmdir  %%i
    rmdir /s/q %%i
) 
