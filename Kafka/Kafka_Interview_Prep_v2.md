# Kafka Interview Prep — The Plain-English Version

Each answer follows the same shape: **the simple idea → why it matters → the trap people fall into**. Read it like you're explaining it to a smart colleague on a whiteboard, not reciting documentation.

---

# PART 1: THE BUILDING BLOCKS

## 1. Topics, Partitions, Offsets, Brokers, Producers, Consumers, Consumer Groups

Think of a **topic** as a filing cabinet's label — like "Customer Orders." It doesn't hold anything itself; it's just a name.

The actual drawers inside that cabinet are **partitions**. Each drawer is a stack of papers you can only add to the top of, and once a paper's in there, it never moves. Each paper has a page number — that's the **offset** — but page 5 in drawer 1 has nothing to do with page 5 in drawer 2. They're independent.

A **broker** is one physical server holding some of these drawers. A cluster is a room full of brokers, and each drawer has one broker in charge of it (the **leader**) plus backup copies on other brokers (**followers**), so if one server dies, the drawer isn't lost.

A **producer** is whoever's filing new papers in. A **consumer** is whoever's reading them. And a **consumer group** is a team of readers who agree "we'll split up the drawers so we're not all reading the same one" — Kafka makes sure no two people on the team ever read the same drawer at the same time, which is what lets you scale reading by just adding more people to the team.

**The one thing to remember:** ordering only exists *within one drawer*. Across drawers, all bets are off.

---

## 2. What Ordering Does Kafka Guarantee?

Just one thing: **records in the same partition come out in the same order they went in.** That's it. Nothing across partitions, even in the same topic, even if they were sent a millisecond apart.

**Why this trips people up:** "Kafka preserves order" sounds like a blanket promise. It's not — it's scoped to a single drawer. If you need "all events for order #123 to happen in sequence," that only works if all of order #123's events land in the *same* drawer. Which brings us to keys.

---

## 3. How Message Keys Influence Correctness and Scalability

A **key** is how you tell Kafka "these records belong together." Kafka hashes the key and always sends that same key to the same partition — so all events for `orderId=123` line up in order, every time.

**The catch:** this is a trade-off, not a free lunch.
- Pick a good key (like `userId`, spread evenly across millions of users) → traffic spreads nicely across partitions, everyone scales well.
- Pick a bad key (like `country`, where "US" dominates) → one partition gets slammed while others sit idle. This is called a **hot partition**, and it's a classic real-world bug: you can add ten more consumers and it won't help, because only *one* consumer can ever read that overloaded partition at a time.

**Takeaway for interviews:** picking a key is really picking *your unit of ordering* — how much you group together — versus *your unit of parallelism* — how thin you can slice the work. Too coarse a key and you bottleneck; too fine a key and you lose the ordering you needed.

---

## 4. What Happens During a Consumer-Group Rebalance?

A rebalance is Kafka reshuffling "who reads which drawer" whenever the team changes — someone joins, someone leaves, someone's presumed dead.

In the classic (older) version, here's the blunt part: **the entire team stops reading**, everyone hands back their drawers, and then Kafka reassigns everything from scratch — even to people whose assignment isn't actually changing. Then everyone picks back up their new assignments and resumes.

**Why it matters:** this is a full-team pause, not a quiet handoff. If your team is large and this happens often (like during every deploy), you're pausing your whole pipeline repeatedly for no good reason.

---

## 5. Eager vs. Cooperative Rebalancing

| | Eager (the old way) | Cooperative (the modern way) |
|---|---|---|
| What happens | Everyone drops everything, then gets reassigned from scratch | Only the people whose drawers are actually changing hand anything back |
| Disruption | Whole team pauses | Just the affected slice pauses |
| Setting | `RangeAssignor` / `RoundRobinAssignor` | `CooperativeStickyAssignor` (recommended default now) |

**Real-world impact:** picture a rolling deploy restarting pods one at a time. With eager rebalancing, *every single restart* pauses the whole consumer group for a moment. With cooperative rebalancing, only the pod that's actually moving gets touched — everyone else keeps working. If you're deploying often, this difference adds up fast.

---

## 6. Static Consumer Memberships

Normally, if a consumer restarts — even for two seconds during a routine deploy — Kafka treats it as "a member left, a new member joined" and triggers a full rebalance. Which is silly, because it's the exact same process coming right back.

**Static membership** fixes this: the consumer registers a stable ID (`group.instance.id`). If it comes back within a set window, Kafka just says "oh, it's you again" and hands back the same assignment — no rebalance needed.

**Best for:** consumers that carry local state (like Kafka Streams apps with data cached on disk), where a rebalance would mean re-downloading all that state to a new machine — expensive and slow. Skipping the rebalance entirely on routine restarts is a big win.

**One catch:** if that consumer actually dies for good, Kafka will patiently wait for it to come back (since that's the whole point of static membership) before reassigning its work — so you need to tune the timeout to strike a balance between "don't rebalance unnecessarily" and "don't leave work stranded too long."

---

## 7. At-Most-Once, At-Least-Once, and Exactly-Once Delivery

This all comes down to one question: **do you mark the message as "done" before or after you actually finish the work?**

- **At-most-once**: You mark it done *before* you finish (or don't wait to confirm). Crash mid-work? That message is gone — Kafka thinks it's handled, so it'll never come back. Good for: things where losing a little data is fine (like a metrics counter).
- **At-least-once**: You mark it done *after* you finish. Crash mid-work? The message comes back and you do it again. You might process something twice, but you'll never silently lose it. This is the default most production systems use.
- **Exactly-once**: Kafka can bundle "write my output" and "mark the input as done" into one atomic all-or-nothing move — using transactions. But — and this is the part interviewers love to probe — this guarantee only covers stuff happening *inside Kafka*. The second your code calls an external database or API, that promise doesn't reach that far (see next question).

---

## 8. Why Must Consumers Remain Idempotent Even When Kafka Transactions Are Used?

Here's the scenario that makes this click: your consumer reads a message, calls a payment API to charge a card, the charge goes through successfully — and *then* the process crashes before Kafka commits the transaction. Kafka rolls back. The message never got marked "processed." On restart, Kafka redelivers it. Your code charges the card *again*.

Kafka did everything right — it correctly noticed the transaction didn't finish and retried. But the *external* thing — the actual card charge — already happened once, and Kafka has zero visibility into that and zero ability to undo it.

**The lesson:** Kafka's exactly-once guarantee stops at Kafka's front door. Anything that reaches outside — a database write, an API call, an email — needs to be made safe-to-repeat on its own, usually with a unique ID per event that you check against before acting ("have I already done this?").

---

## 9. How Do Idempotent Producers and Transactional Producers Differ?

**Idempotent producer**: Solves one narrow problem — *the producer accidentally sending the same batch twice because of a network retry.* Kafka tags each batch with a sequence number, and if a retry lands after the original already succeeded, the broker just throws away the duplicate. Scope: one partition, one producer session.

**Transactional producer**: A bigger promise — *multiple writes across multiple partitions or topics all succeed or all fail together*, including the offset commit itself. This is what lets you do "read a message, write to two output topics, and mark the input as processed" as one atomic unit — the actual mechanism behind exactly-once processing.

**Simple way to remember it:** idempotence = "don't duplicate my own retries." Transactions = "make a multi-step operation all-or-nothing."

---

## 10. `acks`, Retries, `min.insync.replicas`, and Replication Factor

**`acks`** = how many "yes, I got it" confirmations the producer waits for:
- `acks=0`: Fire and forget. Fastest, riskiest.
- `acks=1`: Just the leader confirms. If the leader dies a split second later before backups catch up, that message can vanish.
- `acks=all`: Every current backup confirms before the producer is told "success." Strongest guarantee.

**`retries`**: How many times the producer auto-retries a failed send before giving up and telling your app.

**`min.insync.replicas`**: Only matters if you're using `acks=all`. It's the minimum number of backups that must confirm for a write to count as successful. If not enough backups are healthy, writes flat-out fail rather than quietly accepting a riskier write.

**Replication factor**: How many total copies of each drawer exist (leader + backups). Factor 3 means you can lose 2 out of 3 copies and still have your data.

**Common durable setup**: replication factor 3, `min.insync.replicas=2`, `acks=all` — survives losing any one server with zero data loss.

---

## 11. What Trade-Offs Does `acks=all` Introduce?

You get the strongest safety net — nothing's lost even if the leader dies right after confirming. But you pay for it:

- **Slower**: You're waiting on the slowest backup, not just the leader.
- **Lower throughput**: More waiting per message, generally.
- **Can outright refuse writes**: If too many backups are down to satisfy `min.insync.replicas`, Kafka won't quietly accept a less-safe write — it just rejects the write entirely. So during a partial outage, `acks=all` can mean "no writes at all" rather than "writes with reduced safety," which is a deliberate choice, but a real one.

It's the classic durability-vs-speed trade-off. For something like payments, that trade is usually worth it. For a high-volume, low-stakes log stream, maybe not.

---

## 12. What Happens When a Producer Retry Changes Event Ordering?

Picture this: your producer fires off Batch A, then — without waiting — fires off Batch B right behind it (this is allowed when multiple requests can be "in flight" at once). Batch A's confirmation gets lost in the network, so the producer retries it. Meanwhile, Batch B's original send actually landed fine and got written *first*.

Now the log has B before A — even though your code called `send()` for A first. And nothing throws an error. The data's just quietly out of order.

**This only happens when:** you allow more than one request in flight per connection **and** idempotence is off. It's sneaky because it's intermittent — only shows up when a retry actually happens.

---

## 13. How Do `max.in.flight.requests.per.connection` and Idempotence Interact?

The old-school fix for question 12's problem was: only allow **one** request in flight at a time. Safe, but slow — you're waiting for each batch to confirm before sending the next.

With idempotence turned on, Kafka lets you safely run up to **5** requests in flight at once, because each batch carries a sequence number, and the broker can detect and correctly handle any retry that arrives out of order — so you get both speed (multiple things in flight) *and* correctness. Beyond 5, the guarantee isn't supported, so that's the hard ceiling.

---

## 14. When Should an Offset Be Committed?

Only once you've genuinely finished the work — including anything the message triggered, like a database write or downstream event. Commit too early, and a crash means that work is lost forever (Kafka thinks it's done). If your processing has multiple steps, "done" means *all* the steps that need to succeed together, not just the first one.

---

## 15. What Happens if the Process Crashes After the Database Commit But Before the Offset Commit?

This is the classic **"two systems, no shared safety net"** problem. Your database now has the update. Kafka doesn't know you're done, because the offset was never committed. On restart, Kafka redelivers the same message, and your code runs the database write *again*.

**This isn't a bug — it's at-least-once doing exactly what it's supposed to do:** favor "maybe do it twice" over "maybe lose it." The fix isn't to try to force two unrelated systems to commit together like magic — it's to make the database write itself safe to repeat. An `UPSERT` keyed on a unique event ID instead of a blind `INSERT` does the trick — running it twice just overwrites with the same result. Some teams go further and store "have I processed this?" inside the same database transaction as the actual write, so the check and the write are atomic together at the database level.

---

## 16. Compare Automatic, Synchronous, and Asynchronous Offset Commits

- **Automatic**: Kafka commits on a timer, every few seconds, whether or not your code actually finished processing. This is the dangerous default — a crash right after the timer fires but before your work is done means silent data loss. Avoid for anything that matters.
- **Synchronous**: You explicitly commit after finishing, and you *wait* for confirmation before moving on. Safe, but adds a small delay every time.
- **Asynchronous**: You explicitly commit, but don't wait — you keep working and get notified later if it failed. Faster, but you need to be careful: if an old async commit fails right after a newer one already succeeded, blindly retrying the old one could accidentally move your position *backward*. Common pattern: use async commits during normal operation for speed, but do one final synchronous commit on shutdown to make sure the very last one actually lands.

---

## 17. What Happens When Message Processing Exceeds `max.poll.interval.ms`?

This setting (default 5 minutes) is Kafka's way of asking "are you actually still working, or are you just stuck?" If you don't call `poll()` again within that window — because you're buried in slow processing — Kafka assumes you're dead, kicks you out of the group, and hands your drawers to someone else. Even though your process is technically fine, just slow.

**Common trap:** a consumer doing slow, blocking work per message (a slow database call, a slow third-party API) combined with a large batch size can blow past this window easily. Fixes: process smaller batches at a time, move slow work to a background thread while the main loop keeps polling to stay "alive," or — if the work is legitimately just slow — raise the timeout to match reality instead of fighting it.

---

## 18. How Would You Handle Poison Messages?

A poison message is one that fails *every single time*, no matter how many retries — a bad payload, a bug that always throws for this specific input. The problem: since a partition has to be processed in order, a poison message at position 5 blocks positions 6, 7, 8... forever, even though those might be perfectly fine.

**The playbook:** retry a few times to rule out "maybe it was just a temporary hiccup." If it still fails, ship it off to a dead-letter queue and move on — commit the offset so the pipeline isn't stuck — and make sure something actually *alerts* someone that this happened, so it doesn't just quietly pile up unnoticed.

---

## 19. Retry Topics, Delayed Retry, Blocking Retry, and DLQs — How They Fit Together

Think of these as **layers**, not competing choices:

- **Blocking retry**: Try again immediately, right there in the loop. Simple, but it holds up the whole partition while it retries — and immediate retries often don't give a struggling downstream system enough time to actually recover.
- **Retry topic**: Instead of blocking, ship the failed message to a separate "retry" topic and move on immediately. A different, dedicated process handles retries on its own time, without holding up the main flow.
- **Delayed retry**: Same idea, but you deliberately wait before retrying — 5 seconds, then 30 seconds, then 5 minutes. This matters because a lot of real failures need a little time to clear up, and hammering a struggling system immediately can make things worse.
- **DLQ**: The final stop after retries are exhausted. Not for automatic reprocessing — it's a place for a human to look at what failed and why.

**A realistic flow:** a couple of quick blocking retries → a few delayed retries with increasing wait times → DLQ if it still won't go through.

---

## 20. What Metadata Must a DLQ Record Preserve?

A DLQ record that's just "the payload that broke" is nearly useless later. You want:

- Where it came from (original topic, partition, offset)
- The original key and value, untouched
- Original headers (tracing/correlation IDs, so you can find related logs)
- What actually went wrong (the error, ideally a stack trace)
- How many times it was retried, and over what timeframe
- When it originally happened, and when it landed in the DLQ
- Who produced it, and which service failed to process it

Without this, six months later someone opens the DLQ and has no idea what happened or whether it's even safe to try again.

---

## 21. How Should Replay Be Designed to Avoid Repeating Irreversible Side Effects?

The scary part of replaying old messages: some actions can't be undone. You don't want to accidentally re-charge a card or re-send an email just because you replayed a backlog.

**How to make replay safe:**
- Give every event a stable, unique ID, and make every action check "have I already done this?" before doing it.
- Keep a small record of what's already been processed, so replays can check against it.
- If the external system supports its own idempotency keys (Stripe does, for example), pass your event ID through as that key — now even a genuine duplicate on your end gets caught by *their* system too, as a second layer of protection.
- For truly irreversible stuff without built-in protection, write down your *intent* first ("about to charge card for order X") before doing it, and check that intent log before acting — so a replay reads the already-made decision instead of blindly redoing it.

---

## 22. Schema Compatibility: Avro, Protobuf, JSON Schema

All three usually pair with a schema registry that versions schemas and enforces rules about how they're allowed to change, so producers and consumers can update independently without a coordinated "everyone deploy at once" event.

- **Avro**: The old reliable of the Kafka world. Compact on the wire, mature tooling for handling schema changes gracefully.
- **Protobuf**: Uses field *numbers* (not names) as the actual identity of a field on the wire, which makes some changes (like renaming a field) safer since the number, not the name, is what matters. Popular where you've got many languages talking to each other.
- **JSON Schema**: Easiest to read with your own eyes — no special tooling needed to peek at a message. Costs you in payload size and generally has less mature evolution tooling.

---

## 23. How Do Backward, Forward, and Full Compatibility Differ?

- **Backward compatible**: New code can read old data. This is what lets you upgrade your *consumers* first, safely, while producers are still catching up.
- **Forward compatible**: Old code can still read new data. This is what lets you upgrade your *producers* first, safely, while consumers are still catching up.
- **Full compatible**: Both directions work. Nobody has to coordinate deployment order with anybody — upgrade whoever, whenever, in any order. For a shared topic with lots of different teams consuming it, this is usually the safest default, because it removes the need to babysit rollout sequencing across teams you don't control.

---

## 24. How Would You Remove a Field From an Event Schema?

Only safe if the field has a default value — because after it's gone, anyone still expecting it needs *something* to fall back to.

**Sequence:** check who's actually using the field → stop relying on it in your own code first, while still sending it → remove it from the schema (the default is what makes this backward compatible) → deploy and watch for errors → clean up old code once you're confident nobody needed it.

If the field is *required* with no default, this isn't a quiet edit — it's a breaking change that needs its own coordinated migration.

---

## 25. How Would You Migrate to a New Partitioning Key?

Changing how you key your data means the same entity's future events might land in a *different* drawer than its past ones did — which breaks ordering right at the seam.

**Don't try to re-key an existing topic in place.** Instead: spin up a new topic with the new key scheme → dual-write to both old and new during a transition → move consumers over to the new topic one at a time, checking ordering holds → backfill history into the new topic if anyone needs it → retire the old topic once everyone's moved.

---

## 26. What Happens When the Number of Partitions Increases?

Two things, and people usually only remember one:

1. New empty drawers show up. Existing data doesn't move — it stays exactly where it was.
2. But the *math* for "which drawer does this key go to" changes going forward, because that math depends on the total partition count. So a key that used to always land in drawer 3 might now land in drawer 7 for anything new — silently splitting that key's history across two drawers with no ordering relationship between them.

**Practical implication:** bumping partition count isn't free for anything relying on per-key order. It's worth over-provisioning up front rather than treating it as a casual "just add more partitions" operational tweak later.

---

## 27. How Do You Diagnose Consumer Lag?

1. Look **per partition**, not at one average number — a single overloaded drawer can hide behind a bunch of healthy ones.
2. Check the trend: is lag *growing* (you genuinely can't keep up — a capacity problem) or *flat and stuck* (something died or froze — a different problem entirely)?
3. Check what's actually slow on the consumer side — a slow database call, a slow API, garbage-collection pauses.
4. Check if work is spread unevenly across consumers — a sign of key skew.
5. Don't forget to check the broker side too — sometimes the bottleneck isn't your code at all.

---

## 28. Why Is Consumer Lag Alone an Incomplete Health Metric?

A few reasons this number lies to you:

- 10,000 tiny lagging messages might be seconds of real delay; 10 huge, slow ones might be an hour. Count alone doesn't tell you real-world impact.
- A consumer can show *zero* lag while quietly doing the wrong thing — silently swallowing errors, or marking things "done" before they're actually done. Zero lag isn't the same as healthy.
- Lag tells you *something's* wrong, never *what*. Could be a slow downstream call, not enough consumers, a stuck thread, a broker problem — the number alone doesn't distinguish between them.

Better practice: pair message-count lag with **time-based** lag (how many minutes behind, not how many messages), since that maps much more directly to "how stale is our data right now" — which is usually the actual business question.

---

## 29. How Do Retention and Compaction Differ?

- **Retention**: Delete stuff once it's old enough or the log's too big, no matter what key it belongs to. Think of it as a rolling window — good for things where old data just stops mattering, like raw logs.
- **Compaction**: Keep only the *latest* value per key, no matter how old — good for "current state" data, like "what's the latest known address for customer X."

You can combine both — keep only the latest per key, but also cap how long even that latest value sticks around if it stops getting updated.

---

## 30. What Guarantees Does a Compacted Topic Provide?

You'll always be able to find the *most recent* value for any key that still has one — Kafka won't ever throw away the newest copy. Deleting a key is done by publishing a "tombstone" (a record with an empty value), which sticks around for a bit so consumers can see it happened, before it's cleaned up too.

**What it does NOT give you:** a full history. Compaction is explicitly allowed to erase old superseded updates over time — so if you need "every historical value this key ever had," a compacted topic alone won't give you that. You'd need a separate, uncompacted topic for full history.

---

## 31. How Would You Implement Database-to-Kafka Publication Reliably?

The mirror image of question 15's problem — this time it's "how do I make sure the database write and the Kafka publish happen together, reliably?"

**Standard answer: the Transactional Outbox pattern.**
1. In the *same* database transaction as your real business write, also insert a row into an "outbox" table describing the event to publish. Same transaction means they succeed or fail together — no gap between them.
2. A separate process (ideally something like Debezium reading the database's internal change log, not a fragile custom polling script) reads that outbox table and publishes to Kafka.
3. Mark outbox rows as published once confirmed.
4. Downstream consumers should still be idempotent anyway, as a backup layer — this pattern gets you very close to exactly-once, but "very close" is still worth defending against.

---

## 32. How Do You Conduct a Blue-Green Deployment of Kafka Consumers?

Unlike a web service, you can't just flip traffic over — you don't want two live copies of the same consumer both committing offsets for the same drawers at once, since that risks double-processing.

**The trick: give the new ("green") version its own consumer group ID.** Since Kafka tracks progress separately per group, green can read the same topic in parallel with the old ("blue") version without stepping on its toes at all. Validate green's behavior against real traffic (without letting it cause real side effects yet), then either promote green to take over blue's original group ID once you're confident, or just cut blue off and let green become the new live version.

---

## 33. How Can Green Be Prevented From Processing Production Messages Before Cutover?

Giving green its own consumer group ID stops it from interfering with blue — but it doesn't stop green from *reading and processing* messages, since it's now fully independent. If you need green to not have real-world impact yet, that needs a separate safeguard: point its actual side-effecting calls (payments, emails, writes) at a sandbox or a no-op during validation, or wrap those calls behind a feature flag you can flip on deliberately at cutover time. Kafka's group isolation and "don't cause real effects yet" are two different problems that need two different fixes.

---

## 34. Compare Same-Group, Shadow-Group, and Separate-Topic Deployment Strategies

| Strategy | What it is | Best for |
|---|---|---|
| **Same-group** | Green instances gradually replace blue *within* the same group — a normal rolling deploy | Pure logic changes, no schema/partitioning change — lowest overhead |
| **Shadow-group** | Green runs as its own group alongside blue, purely to validate against real traffic before going live | Bigger logic changes you want to test-drive against production data first, safely |
| **Separate-topic** | Producer writes to both an old-format and new-format topic; green only reads the new one | Changes to the actual data shape (schema or partitioning), where a shadow group reading the same old-format topic wouldn't prove anything |

Pick based on *what's actually changing* — logic-only changes fit the first two; anything touching the data contract needs the third.

---

## 35. How Would You Migrate Between Kafka Clusters?

1. Set up continuous replication (MirrorMaker 2 is the standard tool) — it copies not just the data, but also consumer group offsets, from old cluster to new.
2. Check the data actually matches before touching anything live — counts, checksums, spot checks.
3. Move consumers over first (reading from the now-validated new cluster) while producers keep writing to the old one — lower risk than flipping the write path first.
4. Handle offset translation carefully — the new cluster doesn't automatically use the same offset numbers, so there's a translation step to make sure consumers resume from the right spot, not from zero or some random point.
5. Run both in parallel for a while, watch closely, then retire the old cluster once you're confident. Gradual and reversible beats a single big-bang cutover.

---

## 36. How Do Backpressure and Overload Propagate Through an Event-Driven System?

Kafka's design means a slow consumer doesn't block the producer at all — the durable log just absorbs the mismatch, and it shows up as growing lag instead of a hard failure. This is genuinely one of Kafka's best features: producers stay decoupled from consumer health.

**The trade-off:** because it fails quietly instead of loudly, a real problem can build up for a long time before anyone notices — if nobody's watching lag properly. And in multi-hop pipelines (topic A feeds a processor that writes to topic B, which feeds another consumer), a slowdown at one stage can ripple forward as delayed, bursty data hitting the next stage — even if that next stage was individually fine.

---

## 37. When Is Kafka the Wrong Messaging Technology?

- You need an instant, synchronous answer (like a normal API call) — Kafka's built for async streams, not request/response.
- You need fancy routing logic — priority queues, per-message expiration, fine-grained "retry this one specific message right now" control. A traditional broker like RabbitMQ fits that better.
- Your actual need is small — a simple task queue for modest volume. Kafka's operational overhead may not be worth it; something like SQS might be simpler.
- You genuinely need strict ordering across an *entire* high-volume topic. Since Kafka only orders within one partition, that forces you into a single partition — which kills your scalability, the whole reason you'd reach for Kafka.
- You're moving big files or blobs. Kafka wants small, frequent messages — publish a link to the file (like an S3 URL) instead of the file itself.

---

## 38. Design: Ordering-Sensitive Payment Workflow Using Kafka

**What matters here:** order has to be preserved per account/payment, nothing can be lost, and duplicates need to be caught, given it's money.

- **Key by `accountId`** (or `paymentId`) so each entity's full lifecycle stays in order in one drawer.
- **Producer settings:** `acks=all`, idempotence on, `min.insync.replicas=2`, replication factor 3 — survive a server dying without losing anything.
- **Topic layout:** either split by event type (`payment-initiated`, `payment-authorized`, `payment-settled`) or one topic with an event-type field — depends how different your consumers' needs are.
- **Consumer side:** idempotent by unique event ID, transactional outbox for database writes, Kafka transactions if it's also producing downstream events.
- **Failure handling:** the layered retry approach from question 19, ending in a well-tagged DLQ.
- **The extra safety net:** run a periodic reconciliation job comparing what Kafka processed against the actual ledger. Even a well-built streaming pipeline usually isn't treated as sufficient on its own for money — this catches the rare thing that slips through.

---

## 39. Design: Replay Strategy for Correcting a Faulty Consumer Deployment

**Scenario:** a bug shipped, processed some messages wrong for a window of time, now it's fixed and you need to safely redo that window.

1. Pin down exactly which offsets/timeframe the buggy version touched — use deployment timestamps against offset history. Be a little generous with the boundary rather than too tight.
2. Fix the bug and validate the fix *first* — ideally as a shadow group against real traffic — before touching any replay.
3. Reset offsets for just that window — best done via a separate, temporary consumer group so you don't disturb the live one.
4. Make sure everything downstream is idempotent — including for records in that window that were actually fine the first time, since you don't want to double-apply things that weren't even broken.
5. Check the output actually matches what it should before calling it done.
6. Tell anyone downstream of you that this window was corrected, so they can account for it on their end too.

---

## 40. Describe the Metrics and Alerts Required for a Critical Kafka Pipeline

**Watch on the brokers:** under-replicated partitions (should be zero, always), how many controllers are active (should be exactly one), how saturated the request threads are, disk usage trending toward full.

**Watch on producers:** send latency (especially the slow tail, not just average), error and retry rates, batching efficiency.

**Watch on consumers:** lag — both count *and* time-based — how often rebalances happen (frequent ones mean something's unstable), how long processing actually takes per batch, offset commit failures.

**Watch on topics:** production rate versus consumption rate over time, and whether load is spread evenly across partitions or piling up on one.

**What should actually page someone for a critical pipeline:** any under-replication, lag crossing a real time-based SLA (not just a raw count), a spike in DLQ writes, rebalances happening in a loop, and — easy to miss — production rate suddenly dropping near zero, which usually means something upstream silently broke. Every one of these should point to a runbook, not leave someone guessing during an incident.

---

# PART 2: SCENARIO QUESTIONS — "HERE'S WHAT'S BROKEN, FIGURE OUT WHY"

### S1. One partition out of twelve is way behind on lag; the other eleven are fine. What's going on?

This smells like a hot key, not a capacity problem — if you were just under-provisioned, you'd expect lag spread more evenly across all twelve. Check: is one key (or a small handful) dominating traffic into that one drawer? Also check if that drawer just happens to have unusually large or slow messages. Fix, once confirmed: pick a better-distributed key, or if it's one dominant entity (like a massive customer), consider giving it dedicated infrastructure instead of forcing it into the shared pool.

---

### S2. Every pod restart during a rolling deploy triggers a rebalance, even though each pod comes right back in seconds. How do you fix it?

Classic case for static membership. Set `group.instance.id`, give `session.timeout.ms` enough room for a normal restart, and Kafka will recognize the returning pod as "the same guy" instead of treating it as a whole new join. Worth also confirming you're on `CooperativeStickyAssignor`, so even rebalances that *do* need to happen stay small and targeted instead of pausing everyone.

---

### S3. You need to add a required field to a shared schema, but twelve teams consume it and you can't coordinate a synchronized rollout. What do you do?

You can't make it "required" on day one — that breaks anyone who hasn't updated yet. Add it as *optional with a sensible default* first. Let every producer team migrate on their own schedule. Track adoption. Only if you truly need it to be strictly required later — which is rare once a good default is in place — do you revisit making it mandatory, and even then, central enforcement across independent teams is hard, so a solid default is often just... the actual answer.

---

### S4. A payment consumer occasionally double-charges customers, but you've confirmed Kafka transactions are configured correctly and committing fine. What's wrong?

Kafka being correct doesn't mean you're safe — its guarantee stops at Kafka's edge (see question 8). This is almost certainly the payment API call itself not being idempotent: the charge succeeds, then a crash happens before Kafka's transaction commits, Kafka rolls back and redelivers, and the charge fires again. Fix: pass a stable idempotency key (from your event's unique ID) through to the payment gateway's own idempotency support — most major processors have this — so even a genuine duplicate attempt gets caught on their end too.

---

### S5. Leadership wants to cut costs by dropping replication factor from 3 to 2 across the board, including payments. How do you respond?

Not a blanket "yes" or "no" — it depends on the topic. Dropping to replication factor 2 removes the buffer that lets you survive one server dying without either losing data or losing write availability. For low-stakes, easily-reconstructible data (like raw telemetry), fine, go ahead. For payments specifically — the exact reason it was set to 3 with `min.insync.replicas=2` in the first place — this directly undoes the safety net that design decision was built around. Recommend applying the cost cut selectively, and explicitly carve out payments (and anything similarly critical).

---

### S6. A Kafka Streams app has been stable for months. After adding new local-state logic, the consumer group starts rebalancing randomly every few minutes — no deploys, no scaling events happening.

Nothing changed at the infrastructure level, so look at what *did* change: the new state-store logic is probably occasionally slow enough (a slow disk operation, a blocking call) to blow past `max.poll.interval.ms`, getting the instance kicked out and triggering a rebalance — even though the process itself is fine, just briefly stuck. Check processing-time metrics around the rebalance events to confirm. Fix: optimize the slow path, process smaller batches, or just raise the timeout if the new work is legitimately that much slower now.

---

### S7. Company's moving from on-prem Kafka to a managed cloud service, with a hard requirement of zero downtime and zero data loss. Walk through it.

Set up MirrorMaker 2 to replicate data *and* offsets to the new cluster continuously. Validate the data actually matches before touching production. Move consumers first — reading from the now-validated cloud cluster while producers still write on-prem — then cut producers over once consumer stability is proven. Handle offset translation carefully so consumers resume from the right spot, not zero. Run both clusters in parallel through a real validation window before shutting down on-prem — gradual and reversible, not a single risky flip of a switch.

---

### S8. A teammate wants to switch the payments topic to `acks=1` "for speed, since payments are important." How do you respond?

That logic is backwards. `acks=1` only confirms the leader got it — if the leader dies a moment later before backups catch up, that payment event is just gone, silently, after the producer was already told "success." "Payments are important" is actually the argument *for* `acks=all`, not against it — a bounded, predictable latency cost beats an unbounded, unpredictable risk of quietly losing a transaction. If speed is genuinely the goal, look at batching and compression first — they don't cost you durability the way this would.

---

### S9. You want to switch a compacted topic to plain time-based retention. What could break?

Compacted topics usually exist because something depends on "latest value per key, forever" — like a current-state snapshot. Switch to pure time-based retention, and any key that hasn't been updated recently (older than the retention window) just vanishes, even though nothing about it actually changed. Anyone reading the topic expecting a complete, current picture of every key will silently lose entries for anything that's gone quiet. Before flipping this, audit who actually relies on that "complete snapshot" guarantee — if anyone does, you need a proper migration (like exporting current state first), not a simple settings change.

---

### S10. A new engineer sets `enable.auto.commit=true` on an order-processing consumer "to keep it simple." Weeks later, some orders were silently never processed after a crash.

Auto-commit advances the offset on a fixed timer, with zero awareness of whether your code actually finished. If the timer fires and *then* the process crashes before those specific orders were done, Kafka thinks they're handled — they're gone, permanently skipped on restart. Fix: turn off auto-commit, switch to manual `commitSync()` right after each order (or batch) genuinely finishes, so the offset only ever moves once the work is actually done. Also worth checking if any other consumers share this same "simple" default, since it's an easy trap to leave lying around.

---

### S11. Monitoring shows zero lag on a critical pipeline, but a downstream dashboard has been stale for two hours. How's that possible?

Zero lag only tells you the consumer's caught up with whatever's *currently* in the topic — it says nothing about whether new data is actually arriving, or whether processing is actually working correctly. Two likely culprits: the *producer* silently stopped sending data (check production rate, not just lag), or the consumer is committing fine but silently failing to do its actual job (a swallowed error, a broken write nobody caught). Fix going forward: alert on production-rate drops and downstream data freshness directly — this incident proves lag alone would never have caught either cause.

---

### S12. A consumer team deploys their updated code a full week before the producer finishes rolling out a schema change. What compatibility mode should have prevented this from being an issue?

Backward compatibility — new consumer code needs to be able to read old-schema data, since that's exactly what's still arriving for that week. If the registry enforced `BACKWARD` (or `FULL`), this rollout order is a non-issue by design — the registry would've rejected any schema change that wasn't safe this way in the first place. If only `FORWARD` was enforced, this is exactly the *unsafe* direction. Bigger lesson: which deployment orders are "safe" is a direct, predictable consequence of the compatibility mode you enforce — pick `FULL` for shared topics you don't tightly control, and this whole class of problem disappears.

---

### S13. The team wants to size a new topic's partition count around today's consumer count ("we have 4 pods, so 4 partitions"). What's wrong with that?

Growing partition count later isn't a clean operation — it silently changes which drawer a key maps to going forward, without moving existing data, which can break ordering right at that seam. Since it's easy to over-provision now but risky to expand later, size for where you expect to be in a year, not where you are today. There's a small overhead per extra partition, so it's not "add as many as possible" — but under-provisioning is the more expensive mistake to fix later.

---

### S14. A DLQ has quietly built up messages for three months. Nobody noticed until a customer complained about a transaction that never finished.

The DLQ did its job — the actual failure is that nobody was watching it. A DLQ with no alerting is basically slow-motion silent data loss dressed up as a safety net. Fix: alert on any sustained DLQ write activity, not just log it — and set up an actual ownership process (who reviews it, how often, what's the SLA to investigate). It's also worth checking if the backlog even has enough metadata (question 20) to be diagnosed and safely replayed now — if it wasn't captured at the time, some of it may be a lot harder to untangle three months later.

---

### S15. Leadership asks: "If Kafka guarantees order within a partition, how did we get an incident where two updates to the same customer got applied out of order?"

Kafka's guarantee is real, but scoped tightly to one partition — so this almost always traces back to one of a few things: (1) were both updates actually using the *exact* same key — a formatting mismatch (like inconsistent casing) would silently route them to different drawers, where ordering simply doesn't apply between them; (2) did a partition count change happen between the two updates, shifting the key-to-drawer mapping in between; (3) was this a producer retry reordering issue from having multiple requests in flight without idempotence turned on; (4) or — often overlooked — did Kafka actually deliver them in the right order, but the *consumer's own code* processed them out of order because of its own multi-threading, unrelated to Kafka at all. Framing this as "the guarantee held, here's the specific gap in how we used it" is both more accurate and more useful than "Kafka failed."
