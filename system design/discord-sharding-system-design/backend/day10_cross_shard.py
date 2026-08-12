"""
DAY 10: Cross-Shard Query
==========================
"Fetch the last 10 messages from #general"
When messages are spread across multiple shards, you must
query ALL shards and merge the results.
"""

import time
import random
import heapq
from collections import defaultdict
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from day5_shards import Shard, ShardManager
from day8_hash_sharding import HashShardRouter


# ─────────────────────────────────────────────
# CROSS-SHARD QUERY ENGINE
# ─────────────────────────────────────────────

class CrossShardQueryEngine:
    """
    Handles queries that span multiple shards.
    
    For channel-based sharding: usually one shard per channel.
    For user-based / composite sharding: messages scattered across shards.
    We simulate the WORST CASE: composite sharding (messages spread everywhere).
    """

    def __init__(self, manager: ShardManager, router: HashShardRouter):
        self.manager = manager
        self.router = router
        self.query_stats = []

    def query_channel_messages(self, channel: str, limit: int = 10) -> list:
        """
        Scatter-gather pattern:
        1. Fan out: Query all alive shards for channel messages
        2. Gather: Collect responses
        3. Merge: Sort all results by timestamp
        4. Limit: Return top N most recent
        """
        start = time.perf_counter()
        all_results = []
        shards_queried = 0
        shards_alive = 0
        shards_dead = 0

        for shard in self.manager.shards.values():
            if not shard.is_alive:
                shards_dead += 1
                print(f"    ⚠️  Shard-{shard.shard_id} is DOWN — skipping (partial results!)")
                continue

            shards_alive += 1
            # Each shard returns its messages for this channel
            msgs = shard.get_messages(channel=channel, limit=limit)
            shards_queried += 1
            all_results.extend(msgs)

        # Sort by timestamp (merge step)
        all_results.sort(key=lambda m: m["timestamp"], reverse=True)
        final = all_results[:limit]

        elapsed = (time.perf_counter() - start) * 1000

        self.query_stats.append({
            "channel": channel,
            "shards_queried": shards_queried,
            "shards_dead": shards_dead,
            "total_found": len(all_results),
            "returned": len(final),
            "latency_ms": round(elapsed, 3),
        })

        return final

    def query_user_history(self, user_id: str, limit: int = 10) -> list:
        """
        For user_id-based sharding: query only one shard.
        For composite/channel sharding: must query all shards.
        """
        start = time.perf_counter()
        all_results = []

        for shard in self.manager.shards.values():
            if not shard.is_alive:
                continue
            msgs = shard.user_index.get(user_id, [])[-limit:]
            all_results.extend(msgs)

        all_results.sort(key=lambda m: m["timestamp"], reverse=True)
        final = all_results[:limit]

        elapsed = (time.perf_counter() - start) * 1000
        return final, round(elapsed, 3)

    def fanout_broadcast(self, channel: str) -> dict:
        """
        Simulate broadcasting a message to N users in a channel.
        In real Discord: Gateway servers handle fan-out.
        """
        results = {}
        for shard in self.manager.get_alive_shards():
            # Simulates notifying users connected to this shard
            users_on_shard = len(shard.user_index)
            results[shard.shard_id] = {
                "notified_users": users_on_shard,
                "latency_ms": random.uniform(1, 10),
            }
        return results

    def print_query_stats(self):
        print("\n  📊 Query Performance Log:")
        print("  " + "-" * 55)
        print(f"  {'Channel':<15} {'Shards':<8} {'Found':<8} {'Returned':<10} {'Latency':<10}")
        print("  " + "-" * 55)
        for q in self.query_stats:
            dead_note = f"({q['shards_dead']} dead)" if q['shards_dead'] else ""
            print(f"  #{q['channel']:<14} {q['shards_queried']:<8} "
                  f"{q['total_found']:<8} {q['returned']:<10} "
                  f"{q['latency_ms']:.3f}ms {dead_note}")


# ─────────────────────────────────────────────
# DEMO: Cross-Shard Queries
# ─────────────────────────────────────────────

def demo_cross_shard_query():
    print("=" * 60)
    print("DAY 10: CROSS-SHARD QUERY")
    print("=" * 60)
    print("  Goal: Fetch last 10 messages of a channel")
    print("  Problem: Messages may be spread across all shards\n")

    # Use composite sharding (worst case — messages scattered)
    mgr = ShardManager(num_shards=3)
    router = HashShardRouter(mgr, key_type="composite")
    engine = CrossShardQueryEngine(mgr, router)

    CHANNELS = ["general", "memes", "gaming", "music", "random"]
    USERS = [f"user_{i}" for i in range(50)]

    # ─────────────────────────────────────────
    # Populate system with messages
    # ─────────────────────────────────────────
    print("📌 Step 1: Populate shards with 2000 messages")
    print("-" * 40)

    for i in range(2000):
        user = random.choice(USERS)
        # Hotspot: 80% to #general
        ch = "general" if random.random() < 0.8 else random.choice(CHANNELS[1:])
        router.send_message(user, ch, f"Message from {user}: content_{i}")

    # Show distribution
    print("  Messages per shard after population:")
    for shard in mgr.shards.values():
        general_count = len(shard.channel_index.get("general", []))
        total = shard.write_count
        print(f"  Shard-{shard.shard_id}: {total:,} total | {general_count} in #general")

    # ─────────────────────────────────────────
    # Cross-shard query: all channels
    # ─────────────────────────────────────────
    print("\n📌 Step 2: Cross-Shard Query — All Shards Healthy")
    print("-" * 40)

    for ch in CHANNELS:
        results = engine.query_channel_messages(ch, limit=10)
        print(f"  Query #{ch}: found {len(results)} messages")
        if results:
            latest = results[0]
            print(f"    Latest: [{latest['user_id']}] {latest['content'][:40]}...")

    engine.print_query_stats()

    # ─────────────────────────────────────────
    # Query with shard failure (partial results)
    # ─────────────────────────────────────────
    print("\n📌 Step 3: Query with Shard-1 DOWN (partial results)")
    print("-" * 40)
    mgr.shards[1].kill()

    engine.query_stats = []  # Reset stats

    for ch in ["general", "gaming"]:
        results = engine.query_channel_messages(ch, limit=10)
        print(f"  Query #{ch}: {len(results)} results (with 1 shard down)")

    engine.print_query_stats()
    print("\n  ⚠️  Partial results — some messages permanently unavailable!")

    mgr.shards[1].revive()

    # ─────────────────────────────────────────
    # User history cross-shard query
    # ─────────────────────────────────────────
    print("\n📌 Step 4: User History Query (cross-shard search)")
    print("-" * 40)

    target_user = "user_5"
    msgs, lat = engine.query_user_history(target_user, limit=10)
    print(f"  History of '{target_user}': {len(msgs)} msgs found in {lat}ms")
    for m in msgs[:3]:
        print(f"  [{m['shard']}] #{m['channel']}: {m['content'][:40]}")

    # ─────────────────────────────────────────
    # Fan-out broadcast latency
    # ─────────────────────────────────────────
    print("\n📌 Step 5: Fan-Out Broadcast Simulation")
    print("-" * 40)
    print("  When someone sends to #general, ALL shard users must be notified")

    fanout = engine.fanout_broadcast("general")
    total_notified = sum(r["notified_users"] for r in fanout.values())
    max_latency = max(r["latency_ms"] for r in fanout.values())

    for sid, r in fanout.items():
        print(f"  Shard-{sid}: notified {r['notified_users']} users | latency: {r['latency_ms']:.2f}ms")
    print(f"  Total: {total_notified} users notified | Worst-case latency: {max_latency:.2f}ms")

    print("\n" + "=" * 60)
    print("📋 DAY 10 COMPLETE — SYSTEM DESIGN SUMMARY:")
    print("=" * 60)
    print("""
  The Cross-Shard Query (scatter-gather) is expensive:
  
  ┌─────────────────────────────────────────────────────────┐
  │  Steps in a cross-shard query:                         │
  │  1. Fan out to N shards (parallel)                     │
  │  2. Wait for all to respond (tail latency issue)       │
  │  3. Merge & sort results by timestamp                  │
  │  4. Paginate and return                                │
  │                                                        │
  │  Cost: O(N × messages_per_shard) where N = shards      │
  └─────────────────────────────────────────────────────────┘
  
  OPTIMIZATIONS (used in real Discord):
  ─────────────────────────────────────
  ✅ Channel-based sharding: query only ONE shard for channel history
  ✅ Cassandra/ScyllaDB: append-only, time-ordered storage per channel
  ✅ Snowflake IDs: timestamp-embedded IDs → sort without querying all
  ✅ Read replicas: offload cross-shard reads from write path
  ✅ Redis cache: hot channel's last N messages cached in-memory
  
  YOU BUILT:
  ─────────────────────────────────────
  ✅ Day 1-2: Bottleneck analysis
  ✅ Day 3-4: Working single-server chat
  ✅ Day 5:   3-shard cluster (independent)
  ✅ Day 6:   User-based sharding (+ imbalance)
  ✅ Day 7:   Channel-based sharding (+ hotspot)
  ✅ Day 8:   Hash-based sharding (all 3 strategies)
  ✅ Day 9:   Stress tests + failure simulation
  ✅ Day 10:  Cross-shard scatter-gather query

  OPEN THE UI (streamlit run ui/app.py) for interactive demo!
""")


if __name__ == "__main__":
    demo_cross_shard_query()
