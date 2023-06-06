set WINUSER=YbClockReloaded
set VENV=ybclock
set root=C:\Users\%WINUSER%\.conda\envs\%VENV%
set CODEDIRECTORY=%USERPROFILE%\labscript-suite\userlib\labscriptlib\%VENV% 
call %windir%\System32\WindowsPowerShell\v1.0\powershell.exe -ExecutionPolicy ByPass -NoExit -Command "& 'C:\ProgramData\Anaconda3\shell\condabin\conda-hook.ps1' ; conda activate 'C:\ProgramData\Anaconda3'; conda activate ybclock;"

conda
cd %CODEDIRECTORY%
call pdoc3 -c latex_math=True --html --output-dir ./docs --force
pause
