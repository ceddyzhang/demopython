# Environment notes

## Use the WSL venv, not the Windows `.venv`

The Windows `.venv` has `JAVA_HOME` pointing at a nonexistent folder
(`D:\Eclipse Adoptium\jdk-17.18.8` — the real install is
`D:\Eclipse Adoptium\jdk-17.0.18.8-hotspot`). Since PySpark needs to launch
an actual JVM (not just import the `pyspark` Python package), any
`SparkSession.builder.getOrCreate()` call fails there with:

```
The system cannot find the path specified.
```

`.venv-wsl` (WSL Ubuntu-22.04) has a working Java 17 install and is not
affected. Note: WSL and Windows share the same disk — `/mnt/d/...` in WSL
*is* `D:\...` in Windows, just mounted under a different path. Editing
files in Windows (VS Code, etc.) needs no syncing/copying; WSL sees the
same file instantly. Only the interpreter used to *run* the file differs.

## How to run/test

From `D:\python-project\demopython` in PowerShell (works regardless of
which venv, if any, is "activated" in the prompt — this invokes WSL
directly):

```
wsl -d Ubuntu-22.04 pyspark-exercise/run.sh
```

`run.sh` cd's into the script's own directory, activates `.venv-wsl`, and
runs `exercises.py` (which calls `exercise_01().show()` etc. via its
`if __name__ == "__main__":` block).

Equivalent one-liner without `run.sh`, if needed:

```
wsl -d Ubuntu-22.04 -e bash -lc "cd /mnt/d/python-project/demopython/pyspark-exercise && source ../.venv-wsl/bin/activate && python exercises.py"
```

If the Windows `JAVA_HOME` ever gets fixed to point at the real JDK 17
folder, the Windows `.venv` should work too — but until then, use WSL.
