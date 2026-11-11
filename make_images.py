import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
BG="#fcfcfb"; INK="#0b0b0b"; INK2="#52514e"; MUTED="#a3a29c"; GRID="#e6e5e0"
BLUE="#2a78d6"; ORANGE="#eb6834"; AQUA="#1baf7a"; YEL="#eda100"; RED="#e34948"
plt.rcParams.update({"font.family":"DejaVu Sans","text.color":INK,"figure.facecolor":BG,"axes.facecolor":BG})
TC=[BLUE,ORANGE,AQUA,"#6250d6"]

def box(ax,x,y,w,h,c,r=0.06):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0,rounding_size={r}",fc=c,ec=BG,lw=2))

def timeline(ax,x0,y0,gil,width=5.6,label=True):
    # 4 threads, 4 units of work each
    for t in range(4):
        y=y0-t*0.55
        if label: ax.text(x0-0.15,y+0.2,f"Thread {t+1}",ha="right",va="center",fontsize=12,color=INK2)
        ax.plot([x0,x0+width],[y+0.2,y+0.2],color=GRID,lw=1,zorder=0)
        if gil:
            u=width/16
            for k in range(4): box(ax,x0+(k*4+t)*u,y,u,0.4,TC[t],0.03)
        else:
            box(ax,x0,y,width/4,0.4,TC[t])

# 1. HERO --------------------------------------------------------------
fig,ax=plt.subplots(figsize=(14,7)); ax.axis("off"); ax.set_xlim(0,14); ax.set_ylim(-0.3,7)
ax.text(0.6,6.1,"Python just let go of the GIL.",fontsize=34,weight="bold")
ax.text(0.6,5.4,"Same 4 threads, same work. Watch the clock.",fontsize=17,color=INK2)
ax.text(2.0,4.6,"With the GIL: one at a time",fontsize=14,weight="bold",color=ORANGE)
timeline(ax,2.0,3.9,True,width=10.8)
ax.text(2.0,1.8,"Free-threaded: all at once",fontsize=14,weight="bold",color=BLUE)
for t in range(4):
    box(ax,2.0,1.2-t*0.4,10.8/4,0.32,TC[t])
ax.plot([2.0+10.8/4]*2,[-0.15,1.6],color=INK2,lw=1.5,ls="--")
ax.text(2.0+10.8/4+0.15,0.75,"done, ~4x sooner (on 4+ cores)",va="center",fontsize=13,color=INK2)
fig.savefig("img/01_hero.png",dpi=110,bbox_inches="tight",pad_inches=0.3); plt.close()

# 2. TIMELINE DIAGRAM ----------------------------------------------------
fig,axes=plt.subplots(1,2,figsize=(14,4.4))
for ax,gil,title,c in [(axes[0],True,"Standard Python (GIL on)",ORANGE),(axes[1],False,"Free-threaded Python (GIL off)",BLUE)]:
    ax.axis("off"); ax.set_xlim(-1.3,6); ax.set_ylim(-1.6,1.4)
    ax.text(-1.3,1.05,title,fontsize=15,weight="bold",color=c)
    timeline(ax,0,0.3,gil)
    ax.annotate("",xy=(5.7,-1.45),xytext=(0,-1.45),arrowprops=dict(arrowstyle="->",color=MUTED))
    ax.text(5.7,-1.55,"time",ha="right",va="top",fontsize=11,color=INK2)
axes[0].text(-1.3,-2.05,"Threads take turns holding the lock → CPU work never overlaps",fontsize=11.5,color=INK2)
axes[1].text(-1.3,-2.05,"Each thread runs on its own core → work overlaps",fontsize=11.5,color=INK2)
fig.savefig("img/02_gil_timeline.png",dpi=110,bbox_inches="tight",pad_inches=0.3); plt.close()

# 3. VERSION ROADMAP -----------------------------------------------------
fig,ax=plt.subplots(figsize=(15,4)); ax.axis("off"); ax.set_xlim(0,15); ax.set_ylim(0,4)
ax.plot([0.6,14.6],[2,2],color=MUTED,lw=2)
steps=[(1.4,"≤ 3.12","GIL only",MUTED),(4.4,"3.13 · Oct 2024","Free-threaded build\nappears (experimental)",YEL),
       (7.4,"3.14 · Oct 2025","Officially supported\n(PEP 779), still opt-in",AQUA),
       (10.4,"3.15 · Oct 2026","macOS installer now includes it,\nstable ABI for C extensions",BLUE)]
for x,v,d,c in steps:
    ax.plot(x,2,"o",ms=18,color=c,mec=BG,mew=3)
    ax.text(x,2.6,v,ha="center",fontsize=13,weight="bold"); ax.text(x,1.35,d,ha="center",va="top",fontsize=11,color=INK2)
ax.text(14.6,2.6,"Default?",ha="right",fontsize=13,color=INK2,style="italic"); ax.text(14.6,1.35,"not decided\nyet",ha="right",va="top",fontsize=11,color=INK2)
ax.text(0.6,3.6,"The road to a GIL-free Python",fontsize=18,weight="bold")
fig.savefig("img/03_roadmap.png",dpi=110,bbox_inches="tight",pad_inches=0.3); plt.close()

# 4. CHEAT SHEET -----------------------------------------------------------
fig,ax=plt.subplots(figsize=(16,6.4)); ax.axis("off"); ax.set_xlim(0,16); ax.set_ylim(0,6.4)
ax.text(0.2,5.95,"Threads, asyncio or processes? (2026 edition)",fontsize=24,weight="bold")
rows=[("Your code is mostly…","Reach for","Why"),
      ("Waiting on network / DB / APIs (lots of it)","asyncio","Thousands of waits on one thread, tiny overhead"),
      ("Waiting on I/O, but using sync libraries","threads","Works with requests, DB drivers; GIL is released while waiting"),
      ("Pure-Python CPU work, free-threaded build","threads (3.14t / 3.15t)","Real parallelism, shared memory, no pickling"),
      ("Pure-Python CPU work, normal Python","processes","Each process has its own GIL. Costs memory + pickling"),
      ("NumPy / PyTorch / heavy C code","threads (any build)","These release the GIL already — free win")]
y=5.15
for i,(a,b,c) in enumerate(rows):
    if i==0:
        for x,t in [(0.2,a),(7.0,b),(10.2,c)]: ax.text(x,y,t,fontsize=12.5,color=INK2,weight="bold")
        ax.plot([0.2,15.8],[y-0.3]*2,color=MUTED,lw=1)
    else:
        ax.text(0.2,y,a,fontsize=12.5,va="center"); ax.text(7.0,y,b,fontsize=12.5,weight="bold",color=BLUE,va="center")
        ax.text(10.2,y,c,fontsize=11,color=INK2,va="center")
        ax.plot([0.2,15.8],[y-0.42]*2,color=GRID,lw=1)
    y-=0.85 if i else 0.75
fig.savefig("img/04_cheatsheet.png",dpi=110,bbox_inches="tight",pad_inches=0.3); plt.close()
print("ok")
