"""
DAY 7: Channel-Based Sharding
==============================
Route messages by channel_id → all messages in one channel go to one shard.
PROBLEM: One viral channel = one shard dies.
"""

import time
import random
import threading
from collections import defaultdict
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from day5_shards import Shard, ShardManager


# ─────────────────────────────────────────────
# CHANNEL-BASED SHARD ROUTER
# ─────────────────────────────────────────────

class ChannelShardRouter:
    """
    Routes messages by channel_id.
    shard_id = hash(channel_id) % num_shards
    
    ✅ All messages in a channel are on ONE shard → fast reads
    ✅ Channel history is always consistent
    ❌ Viral channel → one shard gets 80% of traffic  
    ❌ Shard for #general = bottleneck for whole system
    """
    def __init__(self, manager: ShardManager):
        self.manager = manager
        self.channel_map = {}  # channel → shard_id

    def get_shard_for_channel(self, channel: str) -> Shard:
        if channel not in self.channel_map:
            shard_id = hash(channel) % self.manager.num_shards
            self.channel_map[channel] = shard_id

        shard_id = self.channel_map[channel]
        shard = self.manager.shards[shard_id]

        if not shard.is_alive:
            print(f"  💀 Shard-{shard_id} (for #{channel}) is DOWN!")
            # Channel messages are LOST — no easy fallback without replication
            return None

        return shard

    def send_message(self, user_id, channel, content):
        shard = self.get_shard_for_channel(channel)
        if shard is None:
            return None, "CHANNEL_SHARD_DOWN"
        ok, msg = shard.store_message(user_id, channel, content)
        return shard, msg

    def get_channel_messages(self, channel, limit=20):
        """
        ✅ ADVANTAGE: No cross-shard query needed — all in ONE shard!
        """
        shard = self.get_shard_for_channel(channel)
        if shard:
            return shard.get_messages(channel=channel, limit=limit)
        return []

    def show_channel_to_shard_map(self):
        print("\n  📋 Channel → Shard Mapping:")
        for ch, sid in sorted(self.channel_map.items()):
            alive = "✅" if self.manager.shards[sid].is_alive else "💀"
            print(f"  #{ch:<15} → Shard-{sid} {alive}")


# ─────────────────────────────────────────────
# HOTSPOT DEMO: One channel goes viral
# ─────────────────────────────────────────────

def demo_channel_sharding_hotspot():
    print("=" * 60)
    print("DAY 7: CHANNEL-BASED SHARDING")
    print("=" * 60)

    mgr = ShardManager(num_shards=3)
    router = ChannelShardRouter(mgr)

    CHANNELS = ["general", "memes", "gaming", "music", "random", "announcements"]
    USERS = [f"user_{i}" for i in range(100)]

    # Pre-warm channel map
    for ch in CHANNELS:
        router.get_shard_for_channel(ch)

    router.show_channel_to_shard_map()

    # Find which shard #general maps to
    general_shard_id = hash("general") % 3
    print(f"\n  ⚠️  #general → Shard-{general_shard_id}")
    print(f"  This shard WILL become the hotspot!\n")

    # ─────────────────────────────────────────
    # Normal: Balanced channel traffic
    # ─────────────────────────────────────────
    print("\n📌 Step 1: Normal load (balanced across channels)")
    print("-" * 40)
    for i in range(300):
        user = random.choice(USERS)
        channel = random.choice(CHANNELS)  # Uniform distribution
        router.send_message(user, channel, f"msg_{i}")

    mgr.print_cluster_status()

    # ─────────────────────────────────────────
    # VIRAL CHANNEL: #general gets 80% traffic
    # ─────────────────────────────────────────
    print("\n📌 Step 2: VIRAL CHANNEL — #general gets 80% traffic!")
    print("         ⚠️  All go to Shard-" + str(general_shard_id))
    print("-" * 40)

    viral_count = 0
    normal_count = 0
    start = time.time()

    for i in range(2000):
        user = random.choice(USERS)
        if random.random() < 0.80:
            channel = "general"  # Viral!
            viral_count += 1
        else:
            channel = random.choice([c for c in CHANNELS if c != "general"])
            normal_count += 1
        router.send_message(user, channel, f"viral_msg_{i}")

    elapsed = time.time() - start
    print(f"  Done: {elapsed:.3f}s | Viral: {viral_count} | Normal: {normal_count}")

    # Show imbalance
    print("\n  📊 Shard Load after Viral Channel Spike:")
    total = sum(s.write_count for s in mgr.shards.values())
    for shard in mgr.shards.values():
        pct = (shard.write_count / total * 100) if total else 0
        bar = "█" * int(pct / 2)
        flag = " 🔥 #general HERE" if shard.shard_id == general_shard_id else ""
        print(f"  Shard-{shard.shard_id}: {bar:<25} {pct:.1f}% ({shard.write_count:,} msgs){flag}")

    # ─────────────────────────────────────────
    # Channel Read Advantage
    # ─────────────────────────────────────────
    print("\n📌 Step 3: Channel read — no cross-shard query needed!")
    print("-" * 40)
    start = time.time()
    msgs = router.get_channel_messages("general", limit=10)
    elapsed = time.time() - start

    print(f"  Fetched last 10 msgs from #general in {elapsed*1000:.3f}ms")
    print(f"  All on Shard-{general_shard_id} — single shard query ✅")

    # ─────────────────────────────────────────
    # Failure: Viral shard crashes
    # ─────────────────────────────────────────
    print("\n📌 Step 4: FAILURE — Shard-" + str(general_shard_id) + " crashes!")
    print("-" * 40)
    mgr.shards[general_shard_id].kill()

    msgs = router.get_channel_messages("general")
    if not msgs:
        print(f"  ❌ #general is COMPLETELY UNAVAILABLE!")
        print(f"  ❌ No fallback — channel-based sharding has no replication")
        print(f"  ❌ This is the SINGLE POINT OF FAILURE for viral channels")

    print(f"  Other channels (on other shards) still work:")
    for ch in ["memes", "gaming", "music"]:
        sid = router.channel_map.get(ch, -1)
        if sid != general_shard_id:
            msgs = router.get_channel_messages(ch, limit=3)
            print(f"  #{ch} → Shard-{sid} ✅ ({len(msgs)} msgs available)")

    print("\n" + "=" * 60)
    print("📋 DAY 7 RESULTS — CHANNEL SHARDING TRADE-OFFS:")
    print("=" * 60)
    print("""
  ✅ GOOD: All messages in a channel → same shard (fast reads!)
  ✅ GOOD: Channel history is consistent (no merge needed)
  ✅ GOOD: Easy to implement channel-level features
  
  ❌ BAD: Viral channel (#general) = shard hotspot
  ❌ BAD: If that shard dies → entire channel goes down
  ❌ BAD: Uneven server load if channels have different sizes
  
  REAL WORLD: Discord uses guild-based (server-based) sharding
  to keep all channels of a Discord server on the same shard.
  
  NEXT → Day 8: Hash-Based Sharding (choose your key!)
""")


if __name__ == "__main__":
    demo_channel_sharding_hotspot()
