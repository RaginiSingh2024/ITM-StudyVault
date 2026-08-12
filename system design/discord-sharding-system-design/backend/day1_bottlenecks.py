"""
DAY 1-2: Single Server Bottleneck Analysis
==========================================
Shows WHERE and WHY a single server fails under Discord-like load.
50,000 users, one viral channel = disaster.
"""

import time
import random
import threading
from collections import defaultdict

# ─────────────────────────────────────────────
# SINGLE SERVER: No sharding, no distribution
# ─────────────────────────────────────────────

class SingleServer:
    def __init__(self, memory_limit_mb=512):
        self.messages = []           # All messages in ONE list
        self.users_online = set()
        self.memory_limit = memory_limit_mb * 1024  # bytes approximation
        self.cpu_load = 0.0
        self.lock = threading.Lock()
        self.dropped_messages = 0
        self.total_received = 0

    def _estimate_memory_usage(self):
        # Each message ~200 bytes (user_id, channel, content, timestamp)
        return len(self.messages) * 200

    def _estimate_cpu_load(self, active_users):
        # CPU spikes with connections: each user = ~0.002% CPU
        return min(100.0, active_users * 0.002)

    def send_message(self, user_id, channel, content):
        with self.lock:
            self.total_received += 1
            mem_used = self._estimate_memory_usage()

            # ❌ BOTTLENECK 1: Memory exhaustion
            if mem_used > self.memory_limit:
                self.dropped_messages += 1
                return False, "MEMORY_FULL"

            # ❌ BOTTLENECK 2: CPU overload causes slow writes
            if self.cpu_load > 80:
                time.sleep(0.001)  # Simulated CPU lag

            self.messages.append({
                "user_id": user_id,
                "channel": channel,
                "content": content,
                "timestamp": time.time()
            })
            self.users_online.add(user_id)
            return True, "OK"

    def get_channel_messages(self, channel):
        # ❌ BOTTLENECK 3: Full scan on every query (no indexing)
        return [m for m in self.messages if m["channel"] == channel]

    def status(self):
        mem_mb = self._estimate_memory_usage() / 1024
        return {
            "total_messages": len(self.messages),
            "memory_used_mb": round(mem_mb, 2),
            "memory_limit_mb": self.memory_limit // 1024,
            "memory_pct": round((mem_mb / (self.memory_limit // 1024)) * 100, 1),
            "cpu_load_pct": round(self.cpu_load, 1),
            "users_online": len(self.users_online),
            "dropped_messages": self.dropped_messages,
            "total_received": self.total_received,
        }


# ─────────────────────────────────────────────
# SCENARIO: Channel Hotspot (80% traffic → 1 channel)
# ─────────────────────────────────────────────

def simulate_channel_hotspot(server, total_messages=500):
    channels = ["general", "memes", "gaming", "music", "random"]
    hotspot = "general"

    print("\n📡 Simulating Channel Hotspot...")
    print(f"   80% of traffic → #{hotspot} (viral channel)")
    print("-" * 50)

    channel_counts = defaultdict(int)

    for i in range(total_messages):
        user_id = f"user_{random.randint(1, 1000)}"

        # 80% traffic hits ONE channel
        if random.random() < 0.80:
            channel = hotspot
        else:
            channel = random.choice([c for c in channels if c != hotspot])

        ok, reason = server.send_message(user_id, channel, f"msg_{i}")
        channel_counts[channel] += 1

    print("\n📊 Channel Traffic Distribution:")
    total = sum(channel_counts.values())
    for ch, count in sorted(channel_counts.items(), key=lambda x: -x[1]):
        pct = (count / total) * 100
        bar = "█" * int(pct / 2)
        print(f"  #{ch:<10} {bar:<25} {pct:.1f}% ({count} msgs)")

    print(f"\n  🔥 #{hotspot} is a HOTSPOT — single server handles ALL of this!")


# ─────────────────────────────────────────────
# SCENARIO: Scaling Users (shows memory crash)
# ─────────────────────────────────────────────

def simulate_user_scaling():
    print("\n" + "=" * 60)
    print("DAY 1-2: SINGLE SERVER FAILURE ANALYSIS")
    print("=" * 60)

    scale_tests = [
        (10,    100,   "Small (10 users)"),
        (100,   1000,  "Medium (100 users)"),
        (1000,  5000,  "Large (1,000 users)"),
        (10000, 20000, "Overload (10,000 users)"),
    ]

    for users, msgs, label in scale_tests:
        # Small memory limit to demonstrate failure
        server = SingleServer(memory_limit_mb=8)
        server.cpu_load = users * 0.002  # Simulate CPU pressure

        print(f"\n🧪 TEST: {label} | {msgs} messages")
        print("-" * 40)

        start = time.time()
        for i in range(msgs):
            uid = f"user_{i % users}"
            channel = "general" if random.random() < 0.8 else "random"
            server.send_message(uid, channel, f"hello_{i}")

        elapsed = time.time() - start
        s = server.status()

        print(f"  ✅ Stored:    {s['total_messages']:,} messages")
        print(f"  ❌ Dropped:   {s['dropped_messages']:,} messages")
        print(f"  💾 Memory:    {s['memory_used_mb']} MB / {s['memory_limit_mb']} MB ({s['memory_pct']}%)")
        print(f"  🔥 CPU Load:  {s['cpu_load_pct']}%")
        print(f"  ⏱️  Time:      {elapsed:.3f}s")

        if s['dropped_messages'] > 0:
            print(f"  ⚠️  MESSAGE LOSS DETECTED — {s['dropped_messages']} msgs dropped!")
        if s['cpu_load_pct'] > 80:
            print(f"  🚨 CPU OVERLOADED — responses slowing down!")
        if s['memory_pct'] > 90:
            print(f"  🚨 MEMORY CRITICAL — approaching crash zone!")

    # Hotspot demo
    demo_server = SingleServer(memory_limit_mb=64)
    demo_server.cpu_load = 5000 * 0.002
    simulate_channel_hotspot(demo_server, total_messages=1000)

    print("\n" + "=" * 60)
    print("📋 IDENTIFIED BOTTLENECKS:")
    print("=" * 60)
    bottlenecks = [
        ("Memory Exhaustion",    "All messages in RAM. 50K users × avg msgs = crash"),
        ("CPU Hotspot",          "One server handles ALL connections, ALL broadcasts"),
        ("Channel Hotspot",      "80% traffic to #general — no load distribution"),
        ("Full Table Scan",      "get_channel_messages() scans entire message list"),
        ("No Fault Tolerance",   "Server dies → ALL users disconnected, data lost"),
        ("Single Write Path",    "All messages queue to ONE writer → bottleneck"),
    ]
    for i, (name, desc) in enumerate(bottlenecks, 1):
        print(f"\n  {i}. ❌ {name}")
        print(f"     → {desc}")

    print("\n✅ SOLUTION PREVIEW: Sharding splits load across multiple servers")
    print("   Next: Day 3-4 builds the first working chat system\n")


if __name__ == "__main__":
    simulate_user_scaling()
