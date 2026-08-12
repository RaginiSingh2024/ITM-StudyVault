"""
DAY 5: Basic Shards — No Routing Logic Yet
==========================================
Split storage across 3 independent shard servers.
No smart routing — just proves shards can work independently.
"""

import time
import random
import threading
from collections import defaultdict

# ─────────────────────────────────────────────
# SHARD: One independent server
# ─────────────────────────────────────────────

class Shard:
    def __init__(self, shard_id, max_messages=100_000):
        self.shard_id = shard_id
        self.messages = []
        self.channel_index = defaultdict(list)
        self.user_index = defaultdict(list)
        self.lock = threading.Lock()
        self.max_messages = max_messages

        # Per-shard health metrics
        self.write_count = 0
        self.read_count = 0
        self.is_alive = True
        self.overloaded = False
        self.load_threshold = max_messages * 0.85  # 85% = overloaded

    def store_message(self, user_id, channel, content, timestamp=None):
        """Store a message directly — no routing here."""
        if not self.is_alive:
            return False, "SHARD_DOWN"

        with self.lock:
            if len(self.messages) >= self.max_messages:
                self.overloaded = True
                return False, "SHARD_FULL"

            msg = {
                "id": len(self.messages) + 1,
                "user_id": user_id,
                "channel": channel,
                "content": content,
                "timestamp": timestamp or time.time(),
                "shard": self.shard_id,
            }
            self.messages.append(msg)
            self.channel_index[channel].append(msg)
            self.user_index[user_id].append(msg)
            self.write_count += 1

            if len(self.messages) >= self.load_threshold:
                self.overloaded = True

        return True, msg

    def get_messages(self, channel=None, limit=20):
        with self.lock:
            self.read_count += 1
            if channel:
                return self.channel_index[channel][-limit:]
            return self.messages[-limit:]

    def kill(self):
        """Simulate server failure."""
        self.is_alive = False
        print(f"  💀 SHARD {self.shard_id} IS DOWN!")

    def revive(self):
        self.is_alive = True
        print(f"  💚 SHARD {self.shard_id} revived")

    def status(self):
        load_pct = (len(self.messages) / self.max_messages) * 100
        return {
            "shard_id": self.shard_id,
            "alive": self.is_alive,
            "messages": len(self.messages),
            "max_messages": self.max_messages,
            "load_pct": round(load_pct, 1),
            "overloaded": self.overloaded,
            "channels": list(self.channel_index.keys()),
            "writes": self.write_count,
            "reads": self.read_count,
        }

    def __repr__(self):
        s = self.status()
        alive = "✅" if s["alive"] else "💀"
        load = "🔥" if s["overloaded"] else " "
        return (f"  Shard-{self.shard_id} {alive}{load} | "
                f"{s['messages']:,} msgs | Load: {s['load_pct']}%")


# ─────────────────────────────────────────────
# SHARD MANAGER: Knows about all shards
# (No routing logic yet — just orchestration)
# ─────────────────────────────────────────────

class ShardManager:
    def __init__(self, num_shards=3):
        self.shards = {
            i: Shard(shard_id=i, max_messages=50_000)
            for i in range(num_shards)
        }
        self.num_shards = num_shards

    def get_shard(self, shard_id):
        return self.shards.get(shard_id)

    def get_all_shards(self):
        return list(self.shards.values())

    def get_alive_shards(self):
        return [s for s in self.shards.values() if s.is_alive]

    def broadcast_to_all(self, user_id, channel, content):
        """
        Naive: Send same message to ALL shards.
        This is WRONG — causes duplication. We'll fix this in Day 6-8.
        """
        results = []
        for shard in self.get_alive_shards():
            ok, result = shard.store_message(user_id, channel, content)
            results.append((shard.shard_id, ok, result))
        return results

    def round_robin_store(self, user_id, channel, content):
        """
        Simple round-robin: message n goes to shard n % num_shards.
        Still naive — no awareness of load or channels.
        """
        if not hasattr(self, '_rr_counter'):
            self._rr_counter = 0
        self._rr_counter += 1
        target = self._rr_counter % self.num_shards

        # Skip dead shards
        attempts = 0
        while not self.shards[target].is_alive and attempts < self.num_shards:
            target = (target + 1) % self.num_shards
            attempts += 1

        if attempts == self.num_shards:
            return None, "ALL_SHARDS_DOWN"

        ok, result = self.shards[target].store_message(user_id, channel, content)
        return self.shards[target], result

    def print_cluster_status(self):
        print("\n  📊 CLUSTER STATUS:")
        print("  " + "-" * 50)
        for shard in self.shards.values():
            print(shard)
        alive = len(self.get_alive_shards())
        print(f"  {'='*50}")
        print(f"  ✅ Alive: {alive}/{self.num_shards} shards")

    def total_messages(self):
        return sum(s.write_count for s in self.shards.values())


# ─────────────────────────────────────────────
# DEMO: Shards working independently
# ─────────────────────────────────────────────

def demo_independent_shards():
    print("=" * 60)
    print("DAY 5: BASIC SHARDS (3 Independent Servers)")
    print("=" * 60)

    mgr = ShardManager(num_shards=3)

    print("\n📌 Step 1: Write directly to individual shards")
    print("-" * 40)

    # Write to each shard independently
    mgr.shards[0].store_message("alice", "general", "Hello from shard 0!")
    mgr.shards[0].store_message("bob", "gaming", "GG!")
    mgr.shards[1].store_message("charlie", "memes", "lol")
    mgr.shards[1].store_message("diana", "general", "hey!")
    mgr.shards[2].store_message("eve", "music", "🎵")
    mgr.shards[2].store_message("frank", "random", "what's up")

    print("  ✅ Each shard received its own messages independently")
    print("  ❓ Problem: No one knows WHERE to route new messages yet")
    mgr.print_cluster_status()

    print("\n📌 Step 2: Round-robin routing (naive — no awareness)")
    print("-" * 40)
    channels = ["general", "memes", "gaming", "music", "random"]
    users = [f"user_{i}" for i in range(20)]

    for i in range(30):
        user = random.choice(users)
        channel = random.choice(channels)
        shard, result = mgr.round_robin_store(user, channel, f"msg_{i}")
        if i < 5:
            print(f"  Message {i+1} → Shard-{shard.shard_id} | #{channel}")

    print(f"  ... (30 messages sent via round-robin)")
    mgr.print_cluster_status()

    print("\n📌 Step 3: One shard fails — round-robin skips it")
    print("-" * 40)
    mgr.shards[1].kill()

    for i in range(10):
        user = random.choice(users)
        shard, result = mgr.round_robin_store(user, "general", f"failover_msg_{i}")

    mgr.print_cluster_status()

    print("\n📌 Step 4: Shard revives")
    mgr.shards[1].revive()
    mgr.print_cluster_status()

    print("\n" + "=" * 60)
    print("📋 DAY 5 TAKEAWAYS:")
    print("=" * 60)
    print("""
  ✅ 3 shards can store data independently
  ✅ When shard dies, others continue
  ⚠️  Round-robin ignores load — might overload one shard
  ❌ No channel awareness — same channel split across shards
  ❌ Cross-shard reads need to check ALL shards
  
  NEXT → Day 6: User-Based Sharding (route by user_id)
""")


if __name__ == "__main__":
    demo_independent_shards()
