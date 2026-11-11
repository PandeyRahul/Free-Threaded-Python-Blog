# Python Finally Let Go of the GIL — code for the blog

Code for my Medium post racing threads, asyncio and processes on free-threaded Python.

| File | What it does |
|---|---|
| `bench_gil.py` | Runs the same work 5 ways (CPU sequential / threads / processes, I/O threads / asyncio) + a lock-free counter race. Appends results to `results.json`. `--plot` makes `results.png`. |
| `make_images.py` | Builds the concept figures (GIL timeline, roadmap, cheat sheet) into `img/`. |

## Run

```bash
# 1. get a free-threaded Python
uv python install 3.15t

# 2. same interpreter, GIL on vs off
PYTHON_GIL=1 uv run --python 3.15t python bench_gil.py
PYTHON_GIL=0 uv run --python 3.15t python bench_gil.py
#   Windows PowerShell:
#   $env:PYTHON_GIL=1; uv run --python 3.15t python bench_gil.py
#   $env:PYTHON_GIL=0; uv run --python 3.15t python bench_gil.py

# 3. chart (use your normal Python, it needs matplotlib)
pip install matplotlib
python bench_gil.py --plot      # -> results.png

python make_images.py           # concept figures -> img/
```

Check you really have the GIL off:

```python
import sys; print(sys._is_gil_enabled())   # False = GIL off
```
