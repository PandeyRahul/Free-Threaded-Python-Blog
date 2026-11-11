"""GIL vs free-threaded Python: the same code, raced 4 ways.

Run it twice on a free-threaded build (3.14t / 3.15t), toggling the GIL:
    PYTHON_GIL=1 python3.15t bench_gil.py      # GIL forced ON
    PYTHON_GIL=0 python3.15t bench_gil.py      # GIL OFF (free-threaded)
(On Windows PowerShell:  $env:PYTHON_GIL=1; python3.15t bench_gil.py)
Then:  python bench_gil.py --plot    -> results.png
"""
import asyncio, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

WORKERS = min(os.cpu_count() or 4, 8)
N = 5_000_000           # loop size per CPU task
IO_TASKS, IO_DELAY = 200, 0.05


def cpu_task(n=N):
    # pure-Python number crunching: sum of squares of odd numbers
    total = 0
    for i in range(n):
        if i % 2:
            total += i * i
    return total


def timed(fn):
    t0 = time.perf_counter(); fn(); return time.perf_counter() - t0


def cpu_sequential():
    for _ in range(WORKERS): cpu_task()

def cpu_threads():
    with ThreadPoolExecutor(WORKERS) as ex: list(ex.map(cpu_task, [N] * WORKERS))

def cpu_processes():
    with ProcessPoolExecutor(WORKERS) as ex: list(ex.map(cpu_task, [N] * WORKERS))

def io_threads():
    with ThreadPoolExecutor(50) as ex: list(ex.map(lambda _: time.sleep(IO_DELAY), range(IO_TASKS)))

def io_asyncio():
    async def main(): await asyncio.gather(*(asyncio.sleep(IO_DELAY) for _ in range(IO_TASKS)))
    asyncio.run(main())


def race_counter(threads=WORKERS, per_thread=200_000):
    """Classic race: counter += 1 from many threads WITHOUT a lock."""
    import threading
    box = {"n": 0}
    def work():
        for _ in range(per_thread): box["n"] += 1
    ts = [threading.Thread(target=work) for _ in range(threads)]
    [t.start() for t in ts]; [t.join() for t in ts]
    return threads * per_thread - box["n"]   # lost updates


def run():
    gil = sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True
    mode = "GIL on" if gil else "GIL off"
    print(f"{sys.version.split()[0]} | {mode} | {WORKERS} workers")
    res = {"mode": mode, "python": sys.version.split()[0], "workers": WORKERS}
    for name, fn in [("CPU: sequential", cpu_sequential), ("CPU: threads", cpu_threads),
                     ("CPU: processes", cpu_processes), ("I/O: threads", io_threads),
                     ("I/O: asyncio", io_asyncio)]:
        res[name] = min(timed(fn) for _ in range(3))
        print(f"  {name:18s} {res[name]:6.2f} s")
    res["lost updates (no lock)"] = race_counter()
    print(f"  lost updates without a lock: {res['lost updates (no lock)']:,}")
    path = "results.json"
    data = json.load(open(path)) if os.path.exists(path) else {}
    data[mode] = res
    json.dump(data, open(path, "w"), indent=2)


def plot():
    import matplotlib.pyplot as plt
    data = json.load(open("results.json"))
    keys = ["CPU: sequential", "CPU: threads", "CPU: processes", "I/O: threads", "I/O: asyncio"]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    colors = {"GIL on": "#eb6834", "GIL off": "#2a78d6"}
    w = 0.38
    for i, mode in enumerate(["GIL on", "GIL off"]):
        if mode not in data: continue
        vals = [data[mode][k] for k in keys]
        xs = [x + (i - 0.5) * w for x in range(len(keys))]
        ax.bar(xs, vals, width=w - 0.04, color=colors[mode], label=mode)
        for x, v in zip(xs, vals): ax.text(x, v, f"{v:.2f}s", ha="center", va="bottom", fontsize=10)
    ax.set_xticks(range(len(keys)), keys)
    ax.set_ylabel("seconds (lower is better)")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.legend(frameon=False)
    w_ = next(iter(data.values()))["workers"]
    ax.set_title(f"Same code, GIL on vs off — Python {next(iter(data.values()))['python']}, {w_} workers",
                 loc="left", fontsize=14, weight="bold")
    fig.tight_layout(); fig.savefig("results.png", dpi=130)
    print("saved results.png")


if __name__ == "__main__":
    plot() if "--plot" in sys.argv else run()
