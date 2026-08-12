"""
DAY 8: Hash-Based Sharding (Flexible Key Selection)
=====================================================
Choose the sharding key: user_id OR channel_id OR composite.
Understand the trade-offs of each choice clearly.
"""

import time
import random
import hashlib
from collections import defaultdict
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from day5_shards import Shard, ShardManager


# ─────────────────────────────────────────────
# GENERIC HASH ROUTER
# ─────────────────────────────────────────────

class HashShardRouter:
    """
    Flexible hash-based router — choose your sharding key.
    
    key_type options:
      "user_id"    → consistent for users, bad for viral users
      "channel_id" → consistent for channels, bad for viral channels
      "composite"  → hash(user_id + channel_id) — more spread, less consistency
    """
    def __init__(self, manager: ShardManager, key_type: str = "user_id"):
        self.manager = manager
        self.key_type = key_type
        self.route_log = []  # Track routing decisions

    def _hash_key(self, user_id: str, channel: str) -> int:
        if self.key_type == "user_id":
            raw = user_id
        elif self.key_type == "channel_id":
            raw = channel
        elif self.key_type == "composite":
            raw = f"{user_id}:{channel}"
        else:
            raw = user_id

        # Use MD5 for more uniform distribution than Python's hash()
        digest = hashlib.md5(raw.encode()).hexdigest()
        return int(digest, 16) % self.manager.num_shards

    def send_message(self, user_id, channel, content):
        shard_id = self._hash_key(user_id, channel)
        shard = self.manager.shards[shard_id]

        if not shard.is_alive:
            # Try consecutive shards (linear probing fallback)
            for offset in range(1, self.manager.num_shards):
                alt_id = (shard_id + offset) % self.manager.num_shards
                if self.manager.shards[alt_id].is_alive:
                    shard = self.manager.shards[alt_id]
                    break
            else:
                return None, "ALL_SHARDS_DOWN"

        ok, msg = shard.store_message(user_id, channel, content)
        self.route_log.append({"user": user_id, "channel": channel, "shard": shard.shard_id})
        return shard, msg

    def get_distribution(self):
        dist = defaultdict(int)
        for entry in self.route_log:
            dist[entry["shard"]] += 1
        return dict(dist)

    def reset_log(self):
        self.route_log = []


# ─────────────────────────────────────────────
# COMPARE ALL THREE STRATEGIES
# ─────────────────────────────────────────────

def demo_hash_sharding():
    print("=" * 60)
    print("DAY 8: HASH-BASED SHARDING (KEY COMPARISON)")
    print("=" * 60)

    CHANNELS = ["general", "memes", "gaming", "music", "random"]
    USERS = [f"user_{i}" for i in range(50)]
    NUM_MESSAGES = 1000
    NUM_SHARDS = 3

    strategies = ["user_id", "channel_id", "composite"]

    for strategy in strategies:
        mgr = ShardManager(num_shards=NUM_SHARDS)
        router = HashShardRouter(mgr, key_type=strategy)

        print(f"\n📌 Strategy: key_type = '{strategy}'")
        print("-" * 40)

        # Normal load
        for i in range(NUM_MESSAGES):
            user = random.choice(USERS)
            ch = random.choice(CHANNELS)
            router.send_message(user, ch, f"msg_{i}")

        dist = router.get_distribution()
        total = sum(dist.values())

        # Distribution chart
        for sid in range(NUM_SHARDS):
            count = dist.get(sid, 0)
            pct = (count / total * 100) if total else 0
            bar = "█" * int(pct / 3)
            print(f"  Shard-{sid}: {bar:<25} {pct:.1f}% ({count} msgs)")

        values = list(dist.values())
        if values:
            imbalance = (max(values) - min(values)) / (total / NUM_SHARDS) * 100
            print(f"  Imbalance score: {imbalance:.1f}% {'✅ Balanced' if imbalance < 20 else '⚠️ Unbalanced'}")

    # ─────────────────────────────────────────
    # Viral User Test per Strategy
    # ─────────────────────────────────────────
    print("\n📌 Viral User Test: 'spam_king' sends 2000 msgs")
    print("-" * 40)
    print("  (Shows WHICH strategy isolates the damage)\n")

    for strategy in strategies:
        mgr = ShardManager(num_shards=NUM_SHARDS)
        router = HashShardRouter(mgr, key_type=strategy)

        # Background: 50 normal users, 500 msgs
        for i in range(500):
            user = random.choice([f"user_{j}" for j in range(50)])
            router.send_message(user, random.choice(CHANNELS), f"bg_{i}")

        router.reset_log()

        # Viral user
        for i in range(2000):
            ch = random.choice(CHANNELS)
            router.send_message("spam_king", ch, f"spam_{i}")

        dist = router.get_distribution()
        total = sum(dist.values())
        print(f"  [{strategy:>12}] Spam distribution:")
        for sid in range(NUM_SHARDS):
            count = dist.get(sid, 0)
            pct = (count / total * 100) if total else 0
            flag = " 🔥 HOTSPOT" if pct > 80 else ""
            print(f"    Shard-{sid}: {pct:.1f}%{flag}")
        print()

    # ─────────────────────────────────────────
    # Viral Channel Test per Strategy
    # ─────────────────────────────────────────
    print("\n📌 Viral Channel Test: #general gets 80% traffic")
    print("-" * 40)

    for strategy in strategies:
        mgr = ShardManager(num_shards=NUM_SHARDS)
        router = HashShardRouter(mgr, key_type=strategy)
        router.reset_log()

        for i in range(2000):
            user = random.choice([f"user_{j}" for j in range(50)])
            ch = "general" if random.random() < 0.8 else random.choice(CHANNELS[1:])
            router.send_message(user, ch, f"msg_{i}")

        dist = router.get_distribution()
        total = sum(dist.values())
        print(f"  [{strategy:>12}] Traffic distribution:")
        for sid in range(NUM_SHARDS):
            count = dist.get(sid, 0)
            pct = (count / total * 100) if total else 0
            flag = " 🔥 HOTSPOT" if pct > 75 else ""
            print(f"    Shard-{sid}: {pct:.1f}%{flag}")
        print()

    print("=" * 60)
    print("📋 DAY 8 TRADE-OFF SUMMARY:")
    print("=" * 60)
    print("""
  ┌─────────────────┬──────────────┬──────────────┬──────────────┐
  │ Strategy        │ Consistency  │ Viral User   │ Viral Chan   │
  ├─────────────────┼──────────────┼──────────────┼──────────────┤
  │ user_id         │ ✅ Per user  │ ❌ Hotspot   │ ✅ Spread   │
  │ channel_id      │ ✅ Per chan  │ ✅ Spread    │ ❌ Hotspot  │
  │ composite       │ ⚠️  None     │ ✅ Spread    │ ✅ Spread   │
  └─────────────────┴──────────────┴──────────────┴──────────────┘
  
  COMPOSITE is most balanced but loses consistency guarantees.
  
  REAL DISCORD: Uses guild_id (Discord server ID) as shard key.
  A whole Discord server (guild) lives on one shard.
  Large servers (>250K members) get their own dedicated shard.
  
  NEXT → Day 9: Stress tests + server failure simulation
""")


if __name__ == "__main__":
    demo_hash_sharding()
