"""
DAY 6: User-Based Sharding
===========================
Route messages by user_id → same user always hits same shard.
PROBLEM: One active user = one shard gets hammered.
"""

import time
import random
import threading
from collections import defaultdict
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from day5_shards import Shard, ShardManager


# ─────────────────────────────────────────────
# USER-BASED SHARD ROUTER
# ─────────────────────────────────────────────

class UserShardRouter:
    """
    Routes messages by user_id.
    shard_id = hash(user_id) % num_shards
    
    ✅ Consistent: same user → same shard
    ✅ Easy to add user-specific features
    ❌ One viral user floods one shard (hotspot!)
    """
    def __init__(self, manager: ShardManager):
        self.manager = manager

    def get_shard_for_user(self, user_id: str) -> Shard:
        shard_id = hash(user_id) % self.manager.num_shards
        shard = self.manager.shards[shard_id]

        # If that shard is dead, find next alive one
        if not shard.is_alive:
            for offset in range(1, self.manager.num_shards):
                fallback_id = (shard_id + offset) % self.manager.num_shards
                if self.manager.shards[fallback_id].is_alive:
                    print(f"  ⚠️  Shard-{shard_id} down. Routing {user_id} → Shard-{fallback_id}")
                    return self.manager.shards[fallback_id]
            return None  # All shards down

        return shard

    def send_message(self, user_id, channel, content):
        shard = self.get_shard_for_user(user_id)
        if shard is None:
            return None, "ALL_SHARDS_DOWN"
        ok, msg = shard.store_message(user_id, channel, content)
        return shard, msg

    def get_user_messages(self, user_id, limit=10):
        shard = self.get_shard_for_user(user_id)
        if shard:
            return shard.user_index.get(user_id, [])[-limit:]
        return []


# ─────────────────────────────────────────────
# IMBALANCE DEMO: One user sends 5000 messages
# ─────────────────────────────────────────────

def demo_user_sharding_imbalance():
    print("=" * 60)
    print("DAY 6: USER-BASED SHARDING")
    print("=" * 60)

    mgr = ShardManager(num_shards=3)
    router = UserShardRouter(mgr)

    # Show which shard each user maps to
    print("\n📌 Step 1: Hash mapping (which shard gets which user?)")
    print("-" * 40)
    sample_users = [f"user_{i}" for i in range(12)]
    shard_assignment = defaultdict(list)
    for u in sample_users:
        sid = hash(u) % 3
        shard_assignment[sid].append(u)
        print(f"  {u} → Shard-{sid}")

    print("\n  Assignment summary:")
    for sid, users in sorted(shard_assignment.items()):
        print(f"  Shard-{sid}: {len(users)} users → {users}")

    # ─────────────────────────────────────────
    # Normal scenario: balanced usage
    # ─────────────────────────────────────────
    print("\n📌 Step 2: Normal load (50 users, 500 messages)")
    print("-" * 40)

    users_normal = [f"user_{i}" for i in range(50)]
    for i in range(500):
        u = random.choice(users_normal)
        ch = random.choice(["general", "gaming", "memes"])
        router.send_message(u, ch, f"msg_{i}")

    mgr.print_cluster_status()

    # ─────────────────────────────────────────
    # IMBALANCE: "spam_king" sends 5000 messages
    # ─────────────────────────────────────────
    print("\n📌 Step 3: VIRAL USER — spam_king sends 5,000 messages!")
    print("         ⚠️  ALL go to same shard!")
    print("-" * 40)

    spam_king = "spam_king"
    target_shard = hash(spam_king) % 3
    print(f"  spam_king is hashed → Shard-{target_shard}")
    print(f"  Sending 5,000 messages from spam_king...")

    start = time.time()
    for i in range(5000):
        router.send_message(spam_king, "general", f"SPAM_{i}")
    elapsed = time.time() - start

    print(f"  Done in {elapsed:.3f}s")
    mgr.print_cluster_status()

    # Show the imbalance dramatically
    print("\n  📊 Load Distribution (with viral user):")
    total = sum(s.write_count for s in mgr.shards.values())
    for shard in mgr.shards.values():
        pct = (shard.write_count / total * 100) if total else 0
        bar = "█" * int(pct / 2)
        flag = " 🔥 HOTSPOT!" if pct > 80 else ""
        print(f"  Shard-{shard.shard_id}: {bar:<25} {pct:.1f}% ({shard.write_count:,} msgs){flag}")

    # ─────────────────────────────────────────
    # USER CONSISTENCY PROOF
    # ─────────────────────────────────────────
    print("\n📌 Step 4: Consistency check — same user always goes same shard")
    print("-" * 40)
    test_user = "alice"
    target = hash(test_user) % 3
    print(f"  'alice' always → Shard-{target} (hash deterministic ✅)")

    alice_msgs = router.get_user_messages("alice")
    print(f"  Alice's messages found in Shard-{target}: {len(alice_msgs)} msgs")

    print("\n" + "=" * 60)
    print("📋 DAY 6 RESULTS — USER SHARDING TRADE-OFFS:")
    print("=" * 60)
    print("""
  ✅ GOOD: Consistent routing — same user, same shard
  ✅ GOOD: Easy to fetch all messages from one user
  ✅ GOOD: User-level features (rate limiting) easy to implement
  
  ❌ BAD: One viral user = one shard overloaded
  ❌ BAD: Unequal user activity = unequal shard load
  ❌ BAD: Popular channels span ALL shards (hard to query)
  ❌ BAD: If spam_king's shard dies, they lose their history
  
  REAL EXAMPLE: Discord initially used user-based routing
  but had to move to channel/guild-based when big servers crashed.
  
  NEXT → Day 7: Channel-Based Sharding (route by channel_id)
""")


if __name__ == "__main__":
    demo_user_sharding_imbalance()
