# ⚡ Discord Sharding System Design

> A 10-day hands-on simulation of how Discord handles **50,000 users, viral channels, and server failures** through database sharding.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit&logoColor=white)
![Colab](https://img.shields.io/badge/Google%20Colab-Compatible-orange?logo=googlecolab&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 What This Project Does

This project simulates **exactly what happens** when you build a chat app like Discord and it suddenly gets popular:

- 50,000 users join in minutes
- One channel (`#general`) gets 80% of all messages
- A server crashes mid-traffic
- You need to fetch chat history across multiple servers

Each day introduces a new concept, shows what **breaks**, and evolves the system.

---

## 📁 Folder Structure

```
discord-sharding-system-design/
│
├── backend/
│   ├── day1_bottlenecks.py      # Day 1-2: Single server failure analysis
│   ├── day3_single_server.py    # Day 3-4: Working chat system
│   ├── day5_shards.py           # Day 5:   Shard + ShardManager classes
│   ├── day6_user_sharding.py    # Day 6:   User-based sharding + imbalance
│   ├── day7_channel_sharding.py # Day 7:   Channel-based sharding + hotspot
│   ├── day8_hash_sharding.py    # Day 8:   Hash sharding, all key types
│   ├── day9_stress_test.py      # Day 9:   Stress + failure simulation
│   └── day10_cross_shard.py     # Day 10:  Cross-shard scatter-gather query
│
├── ui/
│   └── app.py                   # Streamlit interactive UI
│
├── colab_all_days.py            # Run all 10 days in sequence (Colab-ready)
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Option 1: Interactive UI (Streamlit)
```bash
pip install -r requirements.txt
streamlit run ui/app.py
```

### Option 2: Run All 10 Days (Terminal / Colab)
```bash
python colab_all_days.py
```

### Option 3: Run Individual Days
```bash
python backend/day1_bottlenecks.py
python backend/day9_stress_test.py
python backend/day10_cross_shard.py
```

### Option 4: Google Colab
1. Upload the entire folder to Google Drive
2. Open `colab_all_days.py` in Colab
3. Run all cells — no GPU or special setup needed

---

## 📅 Day-by-Day Breakdown

### Day 1-2: Single Server Bottleneck Analysis
**Question:** Where exactly does a single server fail?

**Findings:**
- Memory fills up at ~8MB (50K users avg 200 bytes/msg)
- CPU load hits 100% when 5000+ users are concurrent
- `get_channel_messages()` scans ALL messages — O(n) on every read
- `#general` gets 80% traffic → entire server is a bottleneck

```
10 users   → ✅ Works fine
100 users  → ✅ OK
1,000 users → ⚠️ Slowing
10,000 users → ❌ Memory crash, message loss
```

---

### Day 3-4: Working Single-Server Chat
**Built:**
- `Message`, `ChatServer` classes
- Channel index and user index for faster lookups
- Threaded stress test simulating concurrent users

**Key Observations:**
- At 10 users: avg write = 0.01ms ✅
- At 5,000 users: write times increase, max spikes to 5ms+ ⚠️
- Threaded test: lock contention appears at 200+ concurrent writers

---

### Day 5: Independent Shards (No Routing)
**Built:** `Shard` and `ShardManager` classes

**Concepts Introduced:**
- Each shard is fully independent — no shared memory
- Round-robin routing as naive baseline
- Shard kill/revive simulation

**Problem Shown:** Round-robin assigns messages blindly — no awareness of load or channel locality.

---

### Day 6: User-Based Sharding
**Routing:** `shard = hash(user_id) % N`

| Situation | Result |
|---|---|
| Normal 50 users | ✅ Balanced enough |
| `spam_king` sends 5,000 msgs | ❌ 100% to one shard |

**Trade-offs:**
- ✅ User history lives in one shard
- ❌ Viral user = shard dies

---

### Day 7: Channel-Based Sharding
**Routing:** `shard = hash(channel_id) % N`

| Situation | Result |
|---|---|
| Balanced channels | ✅ Even distribution |
| `#general` gets 80% traffic | ❌ One shard gets 80% load |
| That shard dies | ❌ Entire channel unavailable |

**Key Insight:** Discord uses **guild-based (server-based)** sharding, not pure channel sharding, to avoid this.

---

### Day 8: Hash-Based Sharding (Key Comparison)

| Key Type | Viral User | Viral Channel | Consistency |
|---|---|---|---|
| `user_id` | ❌ Hotspot | ✅ Spread | ✅ Per user |
| `channel_id` | ✅ Spread | ❌ Hotspot | ✅ Per channel |
| `composite` | ✅ Spread | ✅ Spread | ❌ None |

**Real Discord Decision:** Uses `guild_id` as shard key. Large guilds (>250K members) get dedicated shards.

---

### Day 9: Full Stress Simulation

**Scenario 1 — Normal Load:** 50 users, 1K messages → ✅ No issues  
**Scenario 2 — Viral Spike:** 80% → #general → ❌ Shard hits 80%+ capacity  
**Scenario 3 — Server Failure:** Shard-1 dies mid-traffic → ❌ Channels on it go dark  
**Scenario 4 — Concurrent Failure:** 100 threads + shard crash → ❌ Messages lost mid-flight  

---

### Day 10: Cross-Shard Query (Scatter-Gather)

**Problem:** "Give me the last 10 messages in #general" — but messages are spread across 3 shards.

**Solution: Scatter-Gather Pattern**
```
1. Fan out → query ALL N shards in parallel
2. Gather  → collect results from alive shards
3. Merge   → sort by timestamp
4. Limit   → return top 10
```

**Cost:** O(N × messages_per_shard per query)

**Real-World Optimizations:**
- Cassandra time-ordered storage
- Snowflake IDs (timestamp embedded in ID)
- Redis cache for hot channel's last N messages
- Read replicas for cross-shard reads

---

## 🧠 System Design Decisions Explained

### Why NOT a single server?
- Single Point of Failure
- Memory bounded (~8-32GB max)
- CPU saturates at ~10K concurrent connections
- One viral channel takes down everything

### Why Sharding?
- Each shard is independent — failure is isolated
- Horizontal scaling: add more shards = more capacity
- Each shard handles only 1/N of the traffic

### Why Does the Routing Key Matter?
The routing key determines WHO gets the load. A bad key means:
- One shard handles 80% of traffic
- That shard dies → 80% of users affected

Discord's answer: Route by `guild_id` (their term for a Discord server), with special handling for mega-servers.

### What Happens When a Shard Dies?
Without replication:
- All messages on that shard are **temporarily inaccessible**
- Writes to channels on that shard are **dropped**
- Shard revival doesn't recover dropped messages

With replication (production systems):
- Primary shard + 1-2 read replicas
- If primary dies, replica is promoted
- Zero data loss

---

## 🖥️ UI Features

The Streamlit UI lets you:
- **Send messages** to any channel as any user
- **Watch shard load** change in real time via bar chart
- **Kill / revive** individual shards
- **Run simulations**: Normal Load, Viral Spike, spam_king attack
- **Query channel history** via cross-shard scatter-gather
- **Switch sharding strategy** on the fly (user/channel/composite)
- **Read the system log** for overload and failure events

---

## 📝 Commit Messages

```
git commit -m "Day 1-2: Add single server bottleneck analysis and memory/CPU failure simulation"
git commit -m "Day 3-4: Implement working ChatServer with channel index, user index, and stress test"
git commit -m "Day 5: Add Shard and ShardManager classes with round-robin routing and kill/revive"
git commit -m "Day 6: Implement user-based sharding router, show spam_king imbalance (5K msgs → 1 shard)"
git commit -m "Day 7: Implement channel-based sharding, demonstrate #general viral hotspot and failure"
git commit -m "Day 8: Add flexible HashShardRouter (user_id/channel_id/composite), full trade-off comparison"
git commit -m "Day 9: Add StressTestEngine with 4 scenarios: normal load, viral spike, shard failure, concurrent failure"
git commit -m "Day 10: Implement CrossShardQueryEngine with scatter-gather, user history, and fan-out broadcast"
git commit -m "UI: Build Streamlit interactive dashboard with shard monitor, load chart, simulations, and query engine"
git commit -m "Docs: Add comprehensive README with day-by-day breakdown, trade-off tables, and system design notes"
```

---

## 💡 Key Takeaways

1. **Single servers always fail at scale** — not a question of if, but when
2. **The routing key is everything** — wrong choice = guaranteed hotspot
3. **Sharding trades global consistency for availability** — no free lunch
4. **Cross-shard queries are expensive** — design to minimize them
5. **Discord's real answer**: guild-based sharding + Cassandra + Snowflake IDs

---

## 📚 Further Reading

- [How Discord Stores Billions of Messages](https://discord.com/blog/how-discord-stores-billions-of-messages)
- [Scaling Discord to Millions of Users](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users)
- [Consistent Hashing](https://en.wikipedia.org/wiki/Consistent_hashing)
- [CAP Theorem](https://en.wikipedia.org/wiki/CAP_theorem)

---

*Built as a system design assignment — demonstrating failure at scale, imbalance, and system evolution.*
