# inputs:  1  (pid: int)
# outputs: 1  (pid: int)  — pass-through so it can chain further

def print_pid_node(pid: int) -> int:
    print(f"[server] running as pid {pid}")
    return pid