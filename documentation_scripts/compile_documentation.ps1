$userprofile=$env:USERPROFILE
echo $userprofile
cd $userprofile\labscript-suite\userlib\labscriptlib\ybclock
& "C:\ProgramData\Anaconda3\shell\condabin\conda-hook.ps1"
conda activate ybclock
cd $userprofile\labscript-suite\userlib\labscriptlib\ybclock
pdoc3 -c latex_math=True --html labscriptlib.ybclock --force --output-dir ./docs

