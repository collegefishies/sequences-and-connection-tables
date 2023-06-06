$userprofile=$env:USERPROFILE
echo $userprofile
cd $userprofile\labscript-suite\userlib\labscriptlib\ybclock
& "C:\ProgramData\Anaconda3\shell\condabin\conda-hook.ps1"
conda activate ybclock
cd $userprofile\labscript-suite\userlib\labscriptlib\ybclock
pdoc3 -c latex_math=True --html labscript --force --skip-errors --output-dir ./docs
pdoc3 -c latex_math=True --html lyse --force --skip-errors --output-dir ./docs
pdoc3 -c latex_math=True --html blacs --force --skip-errors --output-dir ./docs
pdoc3 -c latex_math=True --html labscript_devices --force --skip-errors --output-dir ./docs
pdoc3 -c latex_math=True --html runmanager --force --skip-errors --output-dir ./docs

