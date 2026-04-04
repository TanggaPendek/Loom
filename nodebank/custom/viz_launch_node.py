# inputs:  1  (full_config: dict)
# outputs: 1  (pid: int)

import subprocess
import sys
import tempfile
import os

def viz_launch_node(full_config: dict) -> int:

    import random as _random
    array        = full_config.get("array", [50, 30, 80, 20, 60])
    if isinstance(array, int):
        array = [_random.randint(10, 400) for _ in range(max(1, array))]
    viz          = full_config.get("viz", {})
    window       = full_config.get("window", {})

    width        = window.get("width", 800)
    height       = window.get("height", 500)
    title        = window.get("title", "Sorting Visualizer")
    algorithm    = viz.get("algorithm", "bubble")
    speed        = viz.get("speed", 30)
    bar_color    = viz.get("bar_color", "#4fc3f7")
    hi_color     = viz.get("highlight_color", "#ff6b6b")

    lines = [
        "import tkinter as tk",
        "import time,copy",

        f"ARRAY={repr(array)}",
        f"ALGORITHM={repr(algorithm)}",
        f"SPEED={speed}",
        f"BAR_COLOR={repr(bar_color)}",
        f"HI_COLOR={repr(hi_color)}",
        f"W={width}",
        f"H={height}",
        f"TITLE={repr(title)}",

        "root=tk.Tk()",
        "root.title(TITLE)",
        "root.resizable(False,False)",
        "root.configure(bg='#1a1a2e')",

        # top bar
        "top=tk.Frame(root,bg='#16213e',pady=6)",
        "top.pack(fill='x')",
        "tk.Label(top,text=TITLE,bg='#16213e',fg='#e0e0e0',font=('Consolas',13,'bold')).pack(side='left',padx=14)",
        "alg_label=tk.Label(top,text=f'algorithm: {ALGORITHM}',bg='#16213e',fg='#4fc3f7',font=('Consolas',10))",
        "alg_label.pack(side='left',padx=10)",
        "cmp_label=tk.Label(top,text='comparisons: 0',bg='#16213e',fg='#a0a0a0',font=('Consolas',10))",
        "cmp_label.pack(side='right',padx=14)",
        "status_label=tk.Label(top,text='press Start',bg='#16213e',fg='#ffcc02',font=('Consolas',10))",
        "status_label.pack(side='right',padx=10)",

        # canvas
        "canvas=tk.Canvas(root,width=W,height=H,bg='#1a1a2e',highlightthickness=0)",
        "canvas.pack(padx=10,pady=6)",

        # bottom bar
        "bot=tk.Frame(root,bg='#16213e',pady=6)",
        "bot.pack(fill='x')",
        "btn_start=tk.Button(bot,text='Start',bg='#4fc3f7',fg='#1a1a2e',font=('Consolas',10,'bold'),relief='flat',padx=16,cursor='hand2')",
        "btn_start.pack(side='left',padx=14)",
        "btn_reset=tk.Button(bot,text='Reset',bg='#444466',fg='#e0e0e0',font=('Consolas',10),relief='flat',padx=16,cursor='hand2')",
        "btn_reset.pack(side='left',padx=4)",
        "tk.Label(bot,text=f'speed: {SPEED}ms',bg='#16213e',fg='#a0a0a0',font=('Consolas',9)).pack(side='right',padx=14)",

        # state
        "arr=list(ARRAY)",
        "running=[False]",
        "comparisons=[0]",

        "def draw(arr,highlights=[]):",
        "    canvas.delete('all')",
        "    n=len(arr)",
        "    bar_w=max(1,W//n)",
        "    mx=max(arr) if arr else 1",
        "    for i,v in enumerate(arr):",
        "        x0=i*bar_w+2",
        "        y0=H-int(v/mx*(H-10))",
        "        x1=x0+bar_w-2",
        "        y1=H",
        "        color=HI_COLOR if i in highlights else BAR_COLOR",
        "        canvas.create_rectangle(x0,y0,x1,y1,fill=color,outline='')",
        "    root.update()",

        # --- bubble sort generator ---
        "def bubble_gen(a):",
        "    n=len(a)",
        "    for i in range(n):",
        "        for j in range(n-i-1):",
        "            yield a,{j,j+1}",
        "            if a[j]>a[j+1]: a[j],a[j+1]=a[j+1],a[j]",
        "    yield a,set()",

        # --- quick sort generator ---
        "def quick_gen(a):",
        "    def _qs(lo,hi):",
        "        if lo<hi:",
        "            pivot=a[hi]; i=lo-1",
        "            for j in range(lo,hi):",
        "                yield a,{j,hi}",
        "                if a[j]<=pivot:",
        "                    i+=1; a[i],a[j]=a[j],a[i]",
        "            a[i+1],a[hi]=a[hi],a[i+1]",
        "            yield a,{i+1}",
        "            yield from _qs(lo,i); yield from _qs(i+2,hi)",
        "    yield from _qs(0,len(a)-1)",
        "    yield a,set()",

        # --- merge sort generator ---
        "def merge_gen(a):",
        "    def _ms(lo,hi):",
        "        if hi-lo<2: return",
        "        mid=(lo+hi)//2",
        "        yield from _ms(lo,mid); yield from _ms(mid,hi)",
        "        buf=a[lo:hi]; i=lo; l=0; r=mid-lo",
        "        while l<mid-lo and r<hi-lo:",
        "            yield a,{i,lo+r}",
        "            if buf[l]<=buf[r]: a[i]=buf[l]; l+=1",
        "            else: a[i]=buf[r]; r+=1",
        "            i+=1",
        "        while l<mid-lo: a[i]=buf[l]; l+=1; i+=1",
        "        while r<hi-lo: a[i]=buf[r]; r+=1; i+=1",
        "    yield from _ms(0,len(a))",
        "    yield a,set()",

        "GENS={'bubble':bubble_gen,'quick':quick_gen,'merge':merge_gen}",

        "def run_sort():",
        "    if running[0]: return",
        "    running[0]=True",
        "    btn_start.config(state='disabled')",
        "    status_label.config(text='sorting...',fg='#4fc3f7')",
        "    comparisons[0]=0",
        "    gen=GENS[ALGORITHM](arr)",
        "    def step():",
        "        if not running[0]: return",
        "        try:",
        "            a,hl=next(gen)",
        "            comparisons[0]+=1",
        "            cmp_label.config(text=f'comparisons: {comparisons[0]}')",
        "            draw(a,hl)",
        "            root.after(SPEED,step)",
        "        except StopIteration:",
        "            draw(arr)",
        "            running[0]=False",
        "            status_label.config(text='done!',fg='#a8ff78')",
        "            btn_start.config(state='normal')",
        "    root.after(10,step)",

        "def reset():",
        "    running[0]=False",
        "    import random,copy",
        "    arr.clear(); arr.extend(copy.copy(ARRAY))",
        "    comparisons[0]=0",
        "    cmp_label.config(text='comparisons: 0')",
        "    status_label.config(text='press Start',fg='#ffcc02')",
        "    btn_start.config(state='normal')",
        "    draw(arr)",

        "btn_start.config(command=run_sort)",
        "btn_reset.config(command=reset)",
        "draw(arr)",
        "root.mainloop()",
    ]

    script = "\n".join(lines)
    script_path = os.path.join(tempfile.gettempdir(), "sorting_viz.py")
    with open(script_path, "w") as f:
        f.write(script)

    python = sys.executable
    proc = subprocess.Popen(
        ["powershell", "-NoExit", "-Command", f'& "{python}" "{script_path}"'],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    print(f"[launch_sorter] pid={proc.pid}  algorithm={algorithm}  array_size={len(array) if isinstance(array, (list, tuple)) else array}")
    return proc.pid