# pipen-lock

Process lock for pipen to prevent multiple runs at the same time

## Installation

```bash
pip install -U pipen-lock
```

## Enable/Disable

The plugin is enabled by default. To disable it, either uninstall it or:

```python
from pipen import Proc, Pipen

# process definition

class MyPipeline(Pipen):
    plugins = ["-lock"]

```

## Configuration

- `lock_soft`: Whether to use soft lock. Default: `False`
    non-soft lock is platform dependent while soft lock only watches the existence of the lock file.
    See more details <https://py-filelock.readthedocs.io/en/latest/index.html#filelock-vs-softfilelock>
    for the difference between `FileLock` and `SoftFileLock`
