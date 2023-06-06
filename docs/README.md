# pdoc Installation

`pdoc` was installed via 

```
conda activate ybclock
conda install pip 
echo '#in case the venv doesn't have pip'
C:\Users\Boris\anaconda3\envs\ybclock\Scripts\pip install pdoc3
echo '#uses the venv pip to ensure it installs in the venv'
```

# pdoc Usage

```
ls ./documentation_htmls
pdoc3 --html labscriptlib.ybclock --force
```

The last line generates documentation for the parent folder.

If things aren't working, try 
```
pdoc3 --html pdoc --force
```
to see an example of working behaviour.

# pdoc Failed! Why?

pdoc documents by importing every single module then pulling docstrings. If any of your code has an error or requires unspecified arguments, the documentation build will fail.

If you have quit() sequences that get called, that'll break the build process.
Place your scripts inside `if __name__ == "__main__":` blocks if you don't want your code
to run when being imported by pdoc.

# Can pdoc just ignore errors?

Yes, I just learned about this. Add `--skip-errors` at the end of the CLI call.