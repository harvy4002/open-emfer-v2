# Research Document: All-Time Leaderboard Steps and Daily Resets

## Summary

This document evaluates the architectural design, lazy state evaluation, and serverless data models to implement automated UTC daily resets for participants, while retaining historical event records and exposing cumulative all-time statistics (drinks and steps) on the combined dashboard.

---

## Key Decisions

### 1. Lazy Serverless Daily Resets
*   **Decision**: Implement "Lazy Evaluation" for daily participant-level resets. When any `POST` request is received at the `/beer`, `/steps`, `/sensecap`, `/browan`, or `/monzo-sync-simulation` endpoints, the backend will compare the date portion (YYYY-MM-DD) of the current UTC timestamp against the date portion of the user's `last_updated` (or `last_reset_date`) aggregate record. If they differ, the backend will automatically write a `ResetDay` event to the event store and zero out the active daily total counters (`total_drinks`, `beer_drinks`, `categories` map) before executing the new log action.
*   **Rationale**: Eliminates the need for costly, complex external cron jobs, Lambda schedule timers, or active daemon processes, fully aligning with Principle II (Serverless Simplicity) and keeping operational costs at $0.
*   **Alternatives Considered**: Triggering resets via AWS EventBridge schedules on a cron. Rejected because AWS EventBridge introduces unnecessary infrastructure orchestration overhead and minor per-invocation fees, whereas lazy runtime checks are 100% free and execution-instantaneous.

### 2. Dual-Accumulator Data Structure
*   **Decision**: Store all-time cumulative counters inside the existing singleton aggregate partitions (`camper#aggregates#<user_id>`) under dedicated fields: `all_time_total_drinks` (integer) and `all_time_cumulative_steps` (integer). When daily counters are reset, these all-time accumulators are preserved.
*   **Rationale**: Minimizes DynamoDB query volume and keeps payloads extremely compact. The public dashboard or admin portal can retrieve both daily stats and all-time achievements in a single REST query, complying with Principle IV (Secure DB Modeling) and Principle VII (Static Frontends).
*   **Alternatives Considered**: Creating separate `all_time` records under separate DynamoDB keys. Rejected because doing so would double the required read IOPS and query count per dashboard page load.

### 3. Gamification and Leaderboards on Combined Screen
*   **Decision**: Update the combined aggregate record (`camper#aggregates#combined`) to maintain two distinct ranked lists inside its `totals` sort key:
    1.  `leaderboard` (All-time drinks rank)
    2.  `steps_leaderboard` (All-time steps rank)
    Every time any camper logs steps or a drink, the backend will increment their corresponding all-time accumulators, recalculate their positions, and write the sorted list back to the combined aggregate.
*   **Rationale**: Fully delivers the gamified and fitness comparison desires of the camp participants in a lightweight, pre-aggregated, cost-optimal static delivery format.
