"""
COLAB RUNNER: Run all 10 days in sequence
==========================================
Paste this entire file into a Google Colab notebook and run it.
Or run locally: python colab_all_days.py
"""

print("🚀 DISCORD SHARDING SYSTEM DESIGN — COLAB RUNNER")
print("=" * 60)
print("This file simulates all 10 days in sequence.\n")

import sys, os, importlib

# Make sure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# ─────────────────────────────────────────────
# DAY 1-2
# ─────────────────────────────────────────────

print("\n" + "🔲" * 30)
print("RUNNING: DAY 1-2 — Bottleneck Analysis")
print("🔲" * 30)
from backend.day1_bottlenecks import simulate_user_scaling
simulate_user_scaling()

input("\n⏸ Press ENTER to continue to Day 3-4...")

# ─────────────────────────────────────────────
# DAY 3-4
# ─────────────────────────────────────────────

print("\n" + "🔲" * 30)
print("RUNNING: DAY 3-4 — Single Server Chat")
print("🔲" * 30)
from backend.day3_single_server import run_day3_4
run_day3_4()

input("\n⏸ Press ENTER to continue to Day 5...")

# ─────────────────────────────────────────────
# DAY 5
# ─────────────────────────────────────────────

print("\n" + "🔲" * 30)
print("RUNNING: DAY 5 — Basic Shards")
print("🔲" * 30)
from backend.day5_shards import demo_independent_shards
demo_independent_shards()

input("\n⏸ Press ENTER to continue to Day 6...")

# ─────────────────────────────────────────────
# DAY 6
# ─────────────────────────────────────────────

print("\n" + "🔲" * 30)
print("RUNNING: DAY 6 — User-Based Sharding")
print("🔲" * 30)
from backend.day6_user_sharding import demo_user_sharding_imbalance
demo_user_sharding_imbalance()

input("\n⏸ Press ENTER to continue to Day 7...")

# ─────────────────────────────────────────────
# DAY 7
# ─────────────────────────────────────────────

print("\n" + "🔲" * 30)
print("RUNNING: DAY 7 — Channel-Based Sharding")
print("🔲" * 30)
from backend.day7_channel_sharding import demo_channel_sharding_hotspot
demo_channel_sharding_hotspot()

input("\n⏸ Press ENTER to continue to Day 8...")

# ─────────────────────────────────────────────
# DAY 8
# ─────────────────────────────────────────────

print("\n" + "🔲" * 30)
print("RUNNING: DAY 8 — Hash-Based Sharding")
print("🔲" * 30)
from backend.day8_hash_sharding import demo_hash_sharding
demo_hash_sharding()

input("\n⏸ Press ENTER to continue to Day 9...")

# ─────────────────────────────────────────────
# DAY 9
# ─────────────────────────────────────────────

print("\n" + "🔲" * 30)
print("RUNNING: DAY 9 — Stress Tests & Failures")
print("🔲" * 30)
from backend.day9_stress_test import run_day9
run_day9()

input("\n⏸ Press ENTER to continue to Day 10...")

# ─────────────────────────────────────────────
# DAY 10
# ─────────────────────────────────────────────

print("\n" + "🔲" * 30)
print("RUNNING: DAY 10 — Cross-Shard Query")
print("🔲" * 30)
from backend.day10_cross_shard import demo_cross_shard_query
demo_cross_shard_query()

print("\n" + "=" * 60)
print("🏁 ALL 10 DAYS COMPLETE!")
print("=" * 60)
print("""
NEXT STEPS:
  1. Open the interactive UI:
     streamlit run ui/app.py
     
  2. View README.md for full explanation
  
  3. Run individual day files:
     python backend/day1_bottlenecks.py
     python backend/day9_stress_test.py
     etc.
""")
