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
    plugins = ["no:lock"]

```
