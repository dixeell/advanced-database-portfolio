"""Portfolio 5: simulations for the University Result Portal.
(1) Sharding: hash vs range shard keys. (2) Replication lag + read-your-writes.
(3) Quorum rule R + W > N. Deterministic (seeded); results saved to output/."""
import json, hashlib, pathlib, random, collections, statistics
HERE = pathlib.Path(__file__).parent; OUT = HERE/"output"; OUT.mkdir(exist_ok=True)
random.seed(8103)
docs = [json.loads(l) for l in open(HERE.parent/"portfolio-4-nosql"/"output"/"students.json")]
log = open(OUT/"distribution_results.txt","w")
def say(*a):
    s=" ".join(map(str,a)); print(s); log.write(s+"\n")

N_SHARDS = 3
def h(key): return int(hashlib.md5(key.encode()).hexdigest(), 16)
say("=== 1. SHARDING 2,000 student documents across", N_SHARDS, "shards ===")
hashed = collections.Counter(h(d["_id"]) % N_SHARDS for d in docs)
say("Hash(matric_no) % 3      :", dict(sorted(hashed.items())), "-> spread (max/min) =", round(max(hashed.values())/min(hashed.values()),2))
years = sorted({d["entryYear"] for d in docs})
rng = {y: i % N_SHARDS for i, y in enumerate(years)}        # range-style: whole intake year on one shard
ranged = collections.Counter(rng[d["entryYear"]] for d in docs)
say("Range(entry_year)         :", dict(sorted(ranged.items())), "-> spread (max/min) =", round(max(ranged.values())/min(ranged.values()),2))
# Hot-spot test: result release day for the newest intake hits only that intake
latest = max(years); hot = collections.Counter(h(d["_id"]) % N_SHARDS if True else 0 for d in docs if d["entryYear"]==latest)
hot_r = collections.Counter(rng[d["entryYear"]] for d in docs if d["entryYear"]==latest)
say(f"Result-release traffic for intake {latest} (hash)  :", dict(sorted(hot.items())), "(load shared by all shards)")
say(f"Result-release traffic for intake {latest} (range) :", dict(sorted(hot_r.items())), "(ONE shard takes everything: hot spot)")
say("Decision: hash on matric_no (_id) for even load; keep cross-student reports in an analytics replica.")

say("\n=== 2. REPLICATION: 1 primary + 2 async replicas, lag 20-120 ms ===")
class Replica:
    def __init__(s,name,lag): s.name,s.lag,s.data=name,lag,{}
primary = {}; reps=[Replica("replica-1",random.randint(20,120)), Replica("replica-2",random.randint(20,120))]
events = []   # (apply_time, replica, key, value)
def write(t,key,val):
    primary[key]=val
    for r in reps: events.append((t+r.lag, r, key, val))
def read(t, r):
    for ev in sorted(events, key=lambda e:e[0]):
        if ev[0] <= t: ev[1].data[ev[2]] = ev[3]
    return r.data.get("MIT/2025/01234:MTH201")
write(0, "MIT/2025/01234:MTH201", "B (65)")
for t in (10, 50, 150):
    say(f"t={t:3d} ms  primary={primary['MIT/2025/01234:MTH201']!r:10} "+"  ".join(f"{r.name}(lag {r.lag}ms)={read(t,r)!r}" for r in reps))
say("Eventual consistency: replicas converge after the lag. Read-your-writes fix: route a student's reads to the primary for a few seconds after a grade change.")

say("\n=== 3. QUORUM: N=3 replicas ===")
for W,R in ((1,1),(2,2),(3,1),(1,3)):
    say(f"W={W}, R={R}: R+W={R+W} -> {'strongly consistent reads (read set overlaps latest write)' if R+W>3 else 'stale reads possible'}; tolerates {3-W} node failure(s) for writes, {3-R} for reads")
log.close()
