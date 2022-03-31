# psutil


[https://psutil.readthedocs.io/en/latest/](https://psutil.readthedocs.io/en/latest/)
## demo
``` python
def psutilDemo():
    p = psutil.Process()
    for proc in psutil.process_iter(['pid', 'ppid', 'cmdline', 'name', 'username']):
        print(proc.pid)
    # p.as_dict().keys()
    # dict_keys(['nice', 'open_files', 'cpu_affinity', 'threads', 'environ', 'username', 'cmdline', 'memory_full_info', 'num_handles', 'ionice', 'num_ctx_switches', 'io_counters', 'cpu_times', 'num_threads', 'status', 'exe', 'memory_percent', 'pid', 'memory_maps', 'cwd', 'name', 'create_time', 'cpu_percent', 'connections', 'memory_info', 'ppid'])
    """
    with p.oneshot():
        p.name()  # execute internal routine once collecting multiple info
        p.cpu_times()  # return cached value
        p.cpu_percent()  # return cached value
        p.create_time()  # return cached value
        p.ppid()  # return cached value
        p.status()  # return cached value
        p.cwd()  # return cached value
        p.cmdline()
    """

```