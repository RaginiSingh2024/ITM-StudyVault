"""
DAY 9: Stress Tests + Failure Simulation
==========================================
Three scenarios:
  1. Normal load
  2. Viral spike (80% traffic to one channel)
  3. Server failure (disable one shard mid-traffic)
"""

import time
import random
import threading
from collections import defaultdict
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from day5_shards import Shard, ShardManager
from day8_hash_sharding import HashShardRouter


# ─────────────────────────────────────────────
# STRESS TEST ENGINE
# ─────────────────────────────────────────────

class StressTestEngine:
    def __init__(self, num_shards=3, key_type="channel_id"):
        self.mgr = ShardManager(num_shards=num_shards)
        self.router = HashShardRouter(self.mgr, key_type=key_type)
        self.errors = []
        self.lock = threading.Lock()
        self.log = []

    def _log(self, msg):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        self.log.append(line)
        print(f"  {line}")

    def _send_batch(self, users, channels, num_msgs, hotspot_channel=None, hotspot_pct=0.0):
        success = 0
        fail = 0
        for i in range(num_msgs):
            user = random.choice(users)
            if hotspot_channel and random.random() < hotspot_pct:
                ch = hotspot_channel
            else:
                ch = random.choice(channels)

            shard, result = self.router.send_message(user, ch, f"msg_{i}")
            if shard is None:
                with self.lock:
                    fail += 1
                    self.errors.append(f"msg_{i} dropped: {result}")
            else:
                success += 1
        return success, fail

    def snapshot(self, label=""):
        print(f"\n  📊 {'Snapshot: ' + label if label else 'Current State'}")
        total_msgs = 0
        for shard in self.mgr.shards.values():
            st = shard.status()
            bar = "█" * int(st["load_pct"] / 5)
            alive = "✅" if st["alive"] else "💀"
            over = " 🔥 OVERLOADED" if st["overloaded"] else ""
            print(f"    Shard-{st['shard_id']} {alive}: {bar:<20} {st['load_pct']:.1f}% "
                  f"({st['messages']:,} msgs){over}")
            total_msgs += st["messages"]
        alive_count = len(self.mgr.get_alive_shards())
        print(f"    Total: {total_msgs:,} msgs | Live shards: {alive_count}/{self.mgr.num_shards}")
        if self.errors:
            print(f"    ❌ Errors so far: {len(self.errors)}")


# ─────────────────────────────────────────────
# SCENARIO 1: Normal Load
# ─────────────────────────────────────────────

def scenario_normal_load():
    print("\n" + "=" * 60)
    print("SCENARIO 1: NORMAL LOAD")
    print("=" * 60)
    print("  50 users, balanced channels, 1000 messages\n")

    engine = StressTestEngine(num_shards=3, key_type="channel_id")
    users = [f"user_{i}" for i in range(50)]
    channels = ["general", "memes", "gaming", "music", "random"]

    engine._log("Starting normal load simulation...")
    start = time.time()
    ok, fail = engine._send_batch(users, channels, 1000)
    elapsed = time.time() - start

    engine._log(f"Completed: {ok} sent, {fail} failed in {elapsed:.3f}s")
    throughput = ok / elapsed if elapsed > 0 else 0
    engine._log(f"Throughput: {throughput:.0f} msg/s")

    engine.snapshot("After Normal Load")
    print("\n  ✅ System handled normal load without issues")
    return engine


# ─────────────────────────────────────────────
# SCENARIO 2: Viral Spike
# ─────────────────────────────────────────────

def scenario_viral_spike():
    print("\n" + "=" * 60)
    print("SCENARIO 2: VIRAL SPIKE")
    print("=" * 60)
    print("  50,000 user event  — #general gets 80% traffic\n")

    engine = StressTestEngine(num_shards=3, key_type="channel_id")
    # channel_id routing = #general always hits same shard = WORST CASE
    users = [f"user_{i}" for i in range(500)]
    channels = ["general", "memes", "gaming", "music", "random"]

    engine._log("Phase 1: Pre-spike baseline (200 msgs)")
    engine._send_batch(users, channels, 200)
    engine.snapshot("Pre-Spike Baseline")

    engine._log("Phase 2: VIRAL SPIKE begins (#general 80% traffic)")
    engine._log("Imagine a streamer just said 'go to my Discord!'")

    start = time.time()
    ok, fail = engine._send_batch(
        users, channels,
        num_msgs=3000,
        hotspot_channel="general",
        hotspot_pct=0.80
    )
    elapsed = time.time() - start

    engine._log(f"Spike done: {ok} sent, {fail} failed in {elapsed:.3f}s")
    engine.snapshot("After Viral Spike")

    # How bad is the imbalance?
    total = sum(s.write_count for s in engine.mgr.shards.values())
    hotspot_shard_id = hash("general") % 3
    hotspot_load = engine.mgr.shards[hotspot_shard_id].write_count
    imbalance = (hotspot_load / total) * 100 if total else 0
    print(f"\n  🔥 Hotspot shard holds {imbalance:.1f}% of ALL messages!")

    if imbalance > 70:
        print("  ❌ CRITICAL IMBALANCE — this shard will fail first")
    elif imbalance > 50:
        print("  ⚠️  MODERATE IMBALANCE — shard under pressure")

    print("\n  📋 What should the system do?")
    print("  → Auto-scale: add more shards and re-balance")
    print("  → Rate limiting: slow down #general writes")
    print("  → Read replicas: offload reads from hotspot shard")
    return engine


# ─────────────────────────────────────────────
# SCENARIO 3: Server Failure Mid-Traffic
# ─────────────────────────────────────────────

def scenario_server_failure():
    print("\n" + "=" * 60)
    print("SCENARIO 3: SERVER FAILURE DURING TRAFFIC")
    print("=" * 60)
    print("  Traffic running → suddenly Shard-1 dies\n")

    engine = StressTestEngine(num_shards=3, key_type="channel_id")
    users = [f"user_{i}" for i in range(100)]
    channels = ["general", "memes", "gaming", "music", "random"]

    engine._log("Phase 1: normal traffic (500 msgs)")
    engine._send_batch(users, channels, 500)
    engine.snapshot("Before Failure")

    engine._log("Phase 2: Shard-1 has a hardware failure!")
    engine.mgr.shards[1].kill()

    engine._log("Phase 3: Traffic continues — what happens?")
    ok, fail = engine._send_batch(users, channels, 1000)
    engine.snapshot("After Shard-1 Failure")

    engine._log(f"Results: {ok} delivered, {fail} dropped")

    channels_on_dead_shard = [
        ch for ch in channels
        if hash(ch) % 3 == 1
    ]
    print(f"\n  ❌ Channels on dead Shard-1: {channels_on_dead_shard}")
    print(  "  ❌ ALL messages to these channels are being DROPPED")
    print(  "  ✅ Other channels (on Shard-0 and Shard-2) still work")

    engine._log("Phase 4: Emergency — Shard-1 is replaced/revived")
    engine.mgr.shards[1].revive()
    ok2, fail2 = engine._send_batch(users, channels, 200)
    engine.snapshot("After Shard-1 Revival")

    print(f"\n  ℹ️  Note: Messages dropped during failure are PERMANENTLY LOST")
    print(  "  ℹ️  In real systems: replication would prevent this")
    print(  "  ℹ️  Discord uses: primary + replica shard pairs")
    return engine


# ─────────────────────────────────────────────
# THREADED CONCURRENT FAILURE
# ─────────────────────────────────────────────

def scenario_concurrent_failure():
    print("\n" + "=" * 60)
    print("SCENARIO 4: CONCURRENT USERS + SUDDEN FAILURE")
    print("=" * 60)
    print("  100 threads all writing simultaneously, then shard dies\n")

    engine = StressTestEngine(num_shards=3, key_type="channel_id")
    users = [f"user_{i}" for i in range(100)]
    channels = ["general", "memes", "gaming", "music", "random"]

    results = {"success": 0, "fail": 0}
    r_lock = threading.Lock()

    def worker(uid, n_msgs):
        for j in range(n_msgs):
            ch = random.choice(channels)
            shard, res = engine.router.send_message(uid, ch, f"concurrent_{j}")
            with r_lock:
                if shard:
                    results["success"] += 1
                else:
                    results["fail"] += 1

    # Start 100 threads
    threads = [threading.Thread(target=worker, args=(f"user_{i}", 10)) for i in range(100)]

    start = time.time()
    for t in threads:
        t.start()

    # Kill Shard-0 mid-execution
    time.sleep(0.01)
    engine._log("⚡ Mid-execution: Shard-0 crashes!")
    engine.mgr.shards[0].kill()

    for t in threads:
        t.join()

    elapsed = time.time() - start
    engine._log(f"Completed in {elapsed:.3f}s | Success: {results['success']} | Dropped: {results['fail']}")
    engine.snapshot("Post-Concurrent Failure")


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def run_day9():
    print("=" * 60)
    print("DAY 9: FULL STRESS SIMULATION SUITE")
    print("=" * 60)

    scenario_normal_load()
    scenario_viral_spike()
    scenario_server_failure()
    scenario_concurrent_failure()

    print("\n" + "=" * 60)
    print("📋 DAY 9 EXECUTIVE SUMMARY:")
    print("=" * 60)
    print("""
  Scenario 1 (Normal):
    ✅ System copes well with balanced, moderate load

  Scenario 2 (Viral Spike):
    ❌ Channel-based sharding creates 80%+ imbalance
    → Need: Consistent Hashing + Auto-scaling

  Scenario 3 (Shard Failure):
    ❌ Entire channels go dark when shard dies
    → Need: Replication (primary + replica)

  Scenario 4 (Concurrent + Failure):
    ❌ Messages lost mid-flight when shard goes down
    → Need: Message queue (like Kafka) before shard

  NEXT → Day 10: Cross-Shard Query — fetch channel history
         spanning multiple shards!
""")


if __name__ == "__main__":
    run_day9()
