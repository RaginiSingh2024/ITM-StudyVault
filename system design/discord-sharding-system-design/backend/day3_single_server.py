"""
DAY 3-4: Working Single-Server Chat System
==========================================
Real chat with users, channels, messages.
10 users → works fine. 10,000 users → shows strain.
"""

import time
import random
import threading
from collections import defaultdict
from datetime import datetime

# ─────────────────────────────────────────────
# CORE CHAT SYSTEM (Single Server)
# ─────────────────────────────────────────────

class Message:
    def __init__(self, msg_id, user_id, channel, content):
        self.msg_id = msg_id
        self.user_id = user_id
        self.channel = channel
        self.content = content
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.msg_id,
            "user": self.user_id,
            "channel": self.channel,
            "content": self.content,
            "timestamp": self.timestamp,
        }

    def __repr__(self):
        return f"[{self.timestamp}] #{self.channel} | {self.user_id}: {self.content}"


class ChatServer:
    def __init__(self, server_id="server-1"):
        self.server_id = server_id
        self.messages = []
        self.channel_index = defaultdict(list)   # Fast channel lookup
        self.user_index = defaultdict(list)       # Fast user lookup
        self.online_users = set()
        self.msg_counter = 0
        self.lock = threading.Lock()

        # Performance metrics
        self.metrics = {
            "write_times": [],
            "read_times": [],
            "peak_users": 0,
            "total_writes": 0,
            "total_reads": 0,
        }

    def connect_user(self, user_id):
        with self.lock:
            self.online_users.add(user_id)
            if len(self.online_users) > self.metrics["peak_users"]:
                self.metrics["peak_users"] = len(self.online_users)

    def disconnect_user(self, user_id):
        with self.lock:
            self.online_users.discard(user_id)

    def send_message(self, user_id, channel, content):
        t_start = time.perf_counter()
        with self.lock:
            self.msg_counter += 1
            msg = Message(self.msg_counter, user_id, channel, content)
            self.messages.append(msg)
            self.channel_index[channel].append(msg)
            self.user_index[user_id].append(msg)
            self.metrics["total_writes"] += 1
        elapsed = time.perf_counter() - t_start
        self.metrics["write_times"].append(elapsed)
        return msg

    def get_channel_messages(self, channel, limit=20):
        t_start = time.perf_counter()
        with self.lock:
            msgs = self.channel_index[channel][-limit:]
            self.metrics["total_reads"] += 1
        elapsed = time.perf_counter() - t_start
        self.metrics["read_times"].append(elapsed)
        return msgs

    def get_user_messages(self, user_id, limit=20):
        return self.user_index[user_id][-limit:]

    def stats(self):
        wt = self.metrics["write_times"]
        rt = self.metrics["read_times"]
        return {
            "server_id": self.server_id,
            "total_messages": len(self.messages),
            "channels": len(self.channel_index),
            "online_users": len(self.online_users),
            "peak_users": self.metrics["peak_users"],
            "avg_write_ms": round(sum(wt) / len(wt) * 1000, 4) if wt else 0,
            "avg_read_ms": round(sum(rt) / len(rt) * 1000, 4) if rt else 0,
            "max_write_ms": round(max(wt) * 1000, 4) if wt else 0,
            "max_read_ms": round(max(rt) * 1000, 4) if rt else 0,
        }


# ─────────────────────────────────────────────
# SIMULATION ENGINE
# ─────────────────────────────────────────────

CHANNELS = ["general", "memes", "gaming", "music", "random", "announcements"]
MESSAGE_TEMPLATES = [
    "Hey everyone!", "lol that's funny", "did you see this?",
    "anyone online?", "checking in", "what's up", "nice!", "agreed",
    "let's go!", "this is broken", "help me pls", "GG", "bruh moment",
]

def generate_message():
    return random.choice(MESSAGE_TEMPLATES) + f" ({random.randint(1,999)})"

def simulate_scenario(num_users, num_messages, label, hotspot_pct=0.5):
    """Run a simulation scenario and return stats."""
    server = ChatServer()
    users = [f"user_{i}" for i in range(num_users)]

    # Connect all users
    for u in users:
        server.connect_user(u)

    print(f"\n  🧪 {label}")
    print(f"     Users: {num_users:,} | Messages: {num_messages:,} | Hotspot: {int(hotspot_pct*100)}% → #general")

    start = time.time()
    for i in range(num_messages):
        user = random.choice(users)
        # Hotspot: X% of messages go to #general
        if random.random() < hotspot_pct:
            channel = "general"
        else:
            channel = random.choice(CHANNELS[1:])

        server.send_message(user, channel, generate_message())

    # Also simulate reads (users fetching history)
    for _ in range(min(100, num_messages // 10)):
        server.get_channel_messages(random.choice(CHANNELS))

    elapsed = time.time() - start
    s = server.stats()

    print(f"     ⏱️  Completed in: {elapsed:.3f}s")
    print(f"     📝 Messages stored: {s['total_messages']:,}")
    print(f"     ✍️  Avg write time: {s['avg_write_ms']} ms | Max: {s['max_write_ms']} ms")
    print(f"     👁️  Avg read time:  {s['avg_read_ms']} ms  | Max: {s['max_read_ms']} ms")

    # Warn on degradation
    if s["avg_write_ms"] > 0.5:
        print(f"     ⚠️  WRITE SLOWDOWN: avg {s['avg_write_ms']}ms — lock contention")
    if s["max_read_ms"] > 5.0:
        print(f"     ⚠️  READ SPIKE: max {s['max_read_ms']}ms — index struggling")

    return server


# ─────────────────────────────────────────────
# MULTI-THREADED STRESS TEST
# ─────────────────────────────────────────────

def threaded_stress_test(num_users=500, msgs_per_user=20):
    """Simulates concurrent users all writing at the same time."""
    server = ChatServer()
    errors = []
    threads = []

    def user_session(uid):
        server.connect_user(uid)
        for _ in range(msgs_per_user):
            try:
                ch = "general" if random.random() < 0.7 else random.choice(CHANNELS)
                server.send_message(uid, ch, generate_message())
                time.sleep(random.uniform(0, 0.001))  # Small random delay
            except Exception as e:
                errors.append(str(e))

    print(f"\n  🔀 Threaded Stress Test: {num_users} concurrent users")
    start = time.time()
    for i in range(num_users):
        t = threading.Thread(target=user_session, args=(f"user_{i}",))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    elapsed = time.time() - start
    s = server.stats()

    print(f"     ⏱️  Total time: {elapsed:.3f}s")
    print(f"     📝 Messages stored: {s['total_messages']:,}")
    print(f"     ✍️  Max write time: {s['max_write_ms']} ms")
    if errors:
        print(f"     ❌ Errors: {len(errors)}")
    else:
        print(f"     ✅ No errors — threading lock held correctly")

    if elapsed > 5.0:
        print(f"     🚨 SLOW: {elapsed:.1f}s for {num_users * msgs_per_user} msgs — single server strain!")

    return server


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def run_day3_4():
    print("=" * 60)
    print("DAY 3-4: SINGLE SERVER CHAT SYSTEM")
    print("=" * 60)

    print("\n📌 Sequential Load Tests:")
    print("-" * 40)

    # 10 users — works fine
    s1 = simulate_scenario(
        num_users=10, num_messages=100,
        label="10 Users — Normal Chat", hotspot_pct=0.3
    )

    # 100 users — still ok
    s2 = simulate_scenario(
        num_users=100, num_messages=1000,
        label="100 Users — Light Load", hotspot_pct=0.5
    )

    # 1,000 users — begins to strain
    s3 = simulate_scenario(
        num_users=1000, num_messages=5000,
        label="1,000 Users — Medium Load", hotspot_pct=0.7
    )

    # 10,000 users — heavy load
    s4 = simulate_scenario(
        num_users=5000, num_messages=10000,
        label="5,000 Users — Heavy Load (slowing!)", hotspot_pct=0.8
    )

    print("\n📌 Concurrent User Stress Test:")
    print("-" * 40)
    threaded_stress_test(num_users=200, msgs_per_user=10)

    print("\n" + "=" * 60)
    print("📋 DAY 3-4 TAKEAWAYS:")
    print("=" * 60)
    print("""
  ✅ System works for small loads (< 1K users)
  ⚠️  At 5K users: write times increase, locks contend
  ❌ At 50K users: single server WILL crash
  ❌ All state in one place = single point of failure
  ❌ Hotspot channel (#general) gets ALL the load
  
  NEXT STEP → Day 5: Introduce multiple shards!
""")


if __name__ == "__main__":
    run_day3_4()
