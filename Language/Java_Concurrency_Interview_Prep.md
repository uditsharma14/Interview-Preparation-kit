# Java Concurrency — Interview Prep, Basic to Staff Level (with Code & Sources)

> **Target level:** Basic → Staff (graduated — see below) · **Baseline:** Java/JDK 21 (LTS); structured concurrency examples target JEP 505 (JDK 25, preview) and are explicitly flagged where later previews (JEP 525/533) change the API · **Last verified:** 2026-08-23 · **Prerequisites:** core Java syntax for the Basic section; [Java Collections](../Language/Java_Collections_Interview_Prep.md) helpful from the Intermediate section onward

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **code snippet** you could sketch on a whiteboard or IDE to back it up, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar isn't reciting API names, it's explaining failure modes, trade-offs, and what you'd actually do at 3am when this breaks in production. Questions are grouped by level (Basic → Intermediate → Staff) so you can calibrate depth to the interview you're prepping for; the later sections assume the earlier ones as background and don't re-explain them.

<!-- toc -->
## Table of Contents

- [Basic](#basic)
  - [1. What Is a Thread, and How Does It Differ From a Process?](#1-what-is-a-thread-and-how-does-it-differ-from-a-process)
  - [2. How Do You Create and Start a Thread in Java?](#2-how-do-you-create-and-start-a-thread-in-java)
  - [3. What Are the States in a Thread's Lifecycle?](#3-what-are-the-states-in-a-threads-lifecycle)
  - [4. What Is a Race Condition?](#4-what-is-a-race-condition)
  - [5. What Does the `synchronized` Keyword Do — Method vs. Block?](#5-what-does-the-synchronized-keyword-do--method-vs-block)
  - [6. What Is a Deadlock, in the Simplest Terms?](#6-what-is-a-deadlock-in-the-simplest-terms)
  - [7. What's the Difference Between `wait()`/`notify()` and `Thread.sleep()`?](#7-whats-the-difference-between-waitnotify-and-threadsleep)
  - [8. What Is a Daemon Thread?](#8-what-is-a-daemon-thread)
- [Intermediate](#intermediate)
  - [9. What Is `ExecutorService`, and Why Prefer It Over Raw Threads?](#9-what-is-executorservice-and-why-prefer-it-over-raw-threads)
  - [10. `Runnable` vs. `Callable` vs. `Future` — What's the Difference?](#10-runnable-vs-callable-vs-future--whats-the-difference)
  - [11. How Do `CountDownLatch`, `CyclicBarrier`, and `Semaphore` Differ?](#11-how-do-countdownlatch-cyclicbarrier-and-semaphore-differ)
  - [12. How Would You Implement the Producer-Consumer Pattern With `BlockingQueue`?](#12-how-would-you-implement-the-producer-consumer-pattern-with-blockingqueue)
  - [13. `synchronized` vs. `ReentrantLock` — the Basic Trade-Off](#13-synchronized-vs-reentrantlock--the-basic-trade-off)
- [Staff Level](#staff-level)
  - [14. Explain Visibility, Atomicity, Ordering, and Happens-Before Relationships](#14-explain-visibility-atomicity-ordering-and-happens-before-relationships)
  - [15. What Does `volatile` Guarantee, and What Does It Not Guarantee?](#15-what-does-volatile-guarantee-and-what-does-it-not-guarantee)
  - [16. Compare `synchronized`, `ReentrantLock`, `ReadWriteLock`, and `StampedLock`](#16-compare-synchronized-reentrantlock-readwritelock-and-stampedlock)
  - [17. How Do Deadlock, Livelock, Thread Starvation, and Priority Inversion Differ?](#17-how-do-deadlock-livelock-thread-starvation-and-priority-inversion-differ)
  - [18. How Would You Identify and Resolve a Production Deadlock?](#18-how-would-you-identify-and-resolve-a-production-deadlock)
  - [19. Explain the Risks of Calling External Services While Holding a Lock](#19-explain-the-risks-of-calling-external-services-while-holding-a-lock)
  - [20. Compare Platform Threads, Virtual Threads, Reactive Execution, and Asynchronous Futures](#20-compare-platform-threads-virtual-threads-reactive-execution-and-asynchronous-futures)
  - [21. Where Do Virtual Threads Help, and Where Might They Not Improve Performance?](#21-where-do-virtual-threads-help-and-where-might-they-not-improve-performance)
  - [22. How Would You Size an Executor for CPU-Bound Versus I/O-Bound Workloads?](#22-how-would-you-size-an-executor-for-cpu-bound-versus-io-bound-workloads)
  - [23. What Happens When an Executor's Queue Fills? How Do Rejection Policies Affect Reliability?](#23-what-happens-when-an-executors-queue-fills-how-do-rejection-policies-affect-reliability)
  - [24. Explain Work Stealing in `ForkJoinPool`](#24-explain-work-stealing-in-forkjoinpool)
  - [25. What Is the Danger of Blocking Inside the Common `ForkJoinPool`?](#25-what-is-the-danger-of-blocking-inside-the-common-forkjoinpool)
  - [26. How Do You Prevent Race Conditions in Lazy Initialization?](#26-how-do-you-prevent-race-conditions-in-lazy-initialization)
  - [27. Explain Safe Publication and Escaping `this` During Construction](#27-explain-safe-publication-and-escaping-this-during-construction)
  - [28. How Would You Implement a Bounded, Thread-Safe Cache?](#28-how-would-you-implement-a-bounded-thread-safe-cache)
  - [29. How Do You Test Concurrent Code Without Relying on Timing-Sensitive Sleeps?](#29-how-do-you-test-concurrent-code-without-relying-on-timing-sensitive-sleeps)
  - [30. When Would You Use Atomic Classes Versus Locks?](#30-when-would-you-use-atomic-classes-versus-locks)
  - [31. What Is the ABA Problem?](#31-what-is-the-aba-problem)
  - [32. How Would You Propagate Logging, Tracing, Security, and Transaction Context Through Asynchronous Work?](#32-how-would-you-propagate-logging-tracing-security-and-transaction-context-through-asynchronous-work)
  - [33. How Do Structured Concurrency Concepts Improve Cancellation and Error Handling?](#33-how-do-structured-concurrency-concepts-improve-cancellation-and-error-handling)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## Basic

### 1. What Is a Thread, and How Does It Differ From a Process?

**Answer:**

"A process is an independent, OS-managed unit of execution with its own isolated memory address space. A thread is a unit of execution *within* a process that shares that process's memory — heap, static fields — with every other thread in the same process, but has its own call stack, program counter, and local variables. Threads in the same process can therefore communicate through shared memory directly, which is fast but requires coordination to avoid corrupting shared state; separate processes need explicit IPC (sockets, pipes, shared memory segments) to talk to each other. One process crashing doesn't directly crash another process, but a fatal, uncaught error on one thread can bring down the whole JVM process, since every thread in it shares the same process.

A Java program starts as a single thread (`main`), and spawning more threads via `Thread` or `ExecutorService` creates additional concurrent units of execution within that same OS process."

**Code:**

```java
Runnable r = () -> System.out.println("Running on: " + Thread.currentThread().getName());
new Thread(r, "worker-1").start();
System.out.println("Running on: " + Thread.currentThread().getName()); // main
```

**Follow-up:**

I'd mention that in modern Java (21+), a "thread" doesn't necessarily mean a 1:1 OS thread anymore — virtual threads are still `java.lang.Thread` instances from the API's perspective, but aren't mapped 1:1 to OS threads. That distinction is covered in depth later in this guide, in the platform-vs-virtual-threads question. At this basic level, the mental model that matters is: process = isolated memory, thread = shared memory plus its own stack.

**Source:** [Oracle Java Tutorials — Processes and Threads](https://docs.oracle.com/javase/tutorial/essential/concurrency/procthread.html)

---

### 2. How Do You Create and Start a Thread in Java?

**Answer:**

"Two classic ways: extend `Thread` and override `run()`, or implement `Runnable` and pass it to a `Thread` constructor. `Runnable` is preferred almost always — Java doesn't support multiple inheritance, so extending `Thread` uses up the class's one shot at extending anything, while implementing an interface leaves it free. It also separates 'the work to do' from 'the mechanism that runs it,' which matters once you move to `ExecutorService` (covered in the Intermediate section) and hand a `Runnable`/`Callable` to a thread pool rather than manage `Thread` objects directly.

Calling `start()` is what actually creates a new OS-backed thread and schedules `run()` to execute on it, asynchronously. Calling `run()` directly just executes the method body synchronously on the calling thread, like any normal method call — a very common beginner mistake is calling `.run()` instead of `.start()` and being confused that everything ran sequentially on the main thread."

**Code:**

```java
// Style 1: extend Thread — rarely the right choice, locks you out of extending anything else
class MyThread extends Thread {
    @Override public void run() { System.out.println("via Thread subclass"); }
}
new MyThread().start();

// Style 2: implement Runnable — the preferred approach
Runnable task = () -> System.out.println("via Runnable");
new Thread(task).start();

// The classic mistake:
new Thread(task).run();   // WRONG — runs synchronously on the CURRENT thread, no new thread created
new Thread(task).start(); // RIGHT — actually schedules it on a new thread
```

**Follow-up:**

I'd mention that calling `start()` twice on the same `Thread` instance throws `IllegalThreadStateException` — a `Thread` object is single-use; it can't be restarted once it's completed or even just been started. That's one more reason production code almost always goes through `ExecutorService` rather than manually managing raw `Thread` objects: creation cost, lifecycle, and reuse are all handled for you by a pool.

**Source:** [Oracle Java Tutorials — Defining and Starting a Thread](https://docs.oracle.com/javase/tutorial/essential/concurrency/runthread.html)

---

### 3. What Are the States in a Thread's Lifecycle?

**Answer:**

"`Thread.State` defines six states: `NEW` (created but `start()` not yet called), `RUNNABLE` (executing or eligible to be scheduled by the OS — Java doesn't distinguish 'running' from 'ready to run,' both are `RUNNABLE`), `BLOCKED` (waiting to acquire a monitor lock held by another thread, e.g., stuck entering a `synchronized` block), `WAITING` (waiting indefinitely for another thread to explicitly wake it up, via `Object.wait()` with no timeout, `Thread.join()` with no timeout, or `LockSupport.park()`), `TIMED_WAITING` (the same as `WAITING` but with a bounded wait — `Thread.sleep(ms)`, `Object.wait(ms)`, `Thread.join(ms)`), and `TERMINATED` (`run()` has completed, normally or via an uncaught exception).

A thread transitions through these based on what it's currently doing. You can inspect the current state via `thread.getState()`, which is especially useful when reading a thread dump during a hang or deadlock investigation."

**Code:**

```java
Thread t = new Thread(() -> {
    try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
});
System.out.println(t.getState()); // NEW
t.start();
System.out.println(t.getState()); // RUNNABLE (briefly), then TIMED_WAITING during sleep
t.join();
System.out.println(t.getState()); // TERMINATED
```

**Follow-up:**

I'd connect this directly to production debugging: a thread dump (`jstack`, or `Thread.getAllStackTraces()`) reports every live thread's state, and `BLOCKED` threads piling up on the same lock, or several threads sitting in `WAITING` on each other, is the first thing to look for when diagnosing a hang — exactly the raw material the deadlock-diagnosis question later in this guide walks through in more depth.

**Source:** [`Thread.State` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.State.html)

---

### 4. What Is a Race Condition?

**Answer:**

"A race condition happens when the correctness of a program depends on the relative timing or interleaving of multiple threads accessing shared, mutable state — if two threads can execute in an order that produces a wrong result, and a different order would have produced the right one, that's a race, whether or not it actually manifests on any given run. That's exactly what makes race conditions painful: the bug is real and present in the code, but might only show up occasionally, under load, under a specific timing window, or a JIT/GC pause that happens to land at the wrong moment.

The textbook example is two threads both doing `counter++` on a shared, non-atomic `int` field: `++` isn't one operation, it's read-modify-write, and if both threads read the same starting value before either writes back, one increment is silently lost."

**Code:**

```java
class Counter {
    int count = 0; // NOT thread-safe — count++ is read-modify-write, not atomic
    void increment() { count++; }
}

// Two threads each call increment() 100,000 times — expected final count: 200,000
// Actual result: reliably LESS than 200,000, because of lost updates from the race
```

**Follow-up:**

I'd distinguish this from a data race in the strict Java Memory Model sense — a *data race* specifically means unsynchronized concurrent access to the same variable where at least one access is a write, with no happens-before ordering between them (covered in the visibility/atomicity/ordering question later in this guide). A *race condition* is the broader, more intuitive term for a timing-dependent bug: every data race is a race condition, but not every race condition is technically a data race — a check-then-act race on an otherwise-synchronized `ConcurrentHashMap` (covered in the Collections guide) has no raw data race, but is still absolutely a race condition.

**Source:** [JLS §17.4 — Memory Model](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4)

---

### 5. What Does the `synchronized` Keyword Do — Method vs. Block?

**Answer:**

"`synchronized` gives a thread exclusive ownership of a monitor (intrinsic lock) tied to a specific object, for the duration of the synchronized code — only one thread can hold a given object's monitor at a time, so any other thread trying to enter code synchronized on the same object blocks until the first thread exits.

A `synchronized` instance method locks on `this` — the object the method was called on. A `synchronized` static method locks on the `Class` object itself, shared across all instances. A `synchronized` block lets you lock on any specific object you choose, which is usually the better choice: it lets you scope the lock as narrowly as possible — only the actually-shared-mutable-state access, not the whole method body — and lock on a dedicated, private lock object rather than `this`. Locking on `this` risks an unrelated external caller also synchronizing on your object and creating contention, or even deadlock, you don't control."

**Code:**

```java
class Counter {
    private int count = 0;
    private final Object lock = new Object(); // dedicated, private lock object

    synchronized void incrementMethod() { count++; }        // locks on `this`

    void incrementBlock() {
        synchronized (lock) { count++; }                     // locks on `lock` — narrower, private
    }

    static synchronized void staticMethod() { /* locks on Counter.class */ }
}
```

**Follow-up:**

I'd flag "lock on a private final object, not `this`" as the single most useful piece of practical advice here — it's the same reasoning `java.util.concurrent` collections apply internally, and it directly prevents a class of bugs where completely unrelated code synchronizes on your public object and either starves your own internal locking or deadlocks against it. This is also exactly the gap `ReentrantLock` fills — explicit, more flexible locking — covered in the Intermediate section and then compared against the other lock types at Staff level later in this guide.

**Source:** [JLS §17.1 — Synchronization](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.1)

---

### 6. What Is a Deadlock, in the Simplest Terms?

**Answer:**

"A deadlock is two or more threads each holding a lock the other one needs, with neither willing to give up what it's already holding — so both wait forever. The classic minimal example: Thread A locks Resource 1, then tries to lock Resource 2; Thread B locks Resource 2, then tries to lock Resource 1. If that interleaving happens, A is stuck waiting for B to release Resource 2, and B is stuck waiting for A to release Resource 1, and neither ever will.

The simplest, most reliable fix is **lock ordering**: if every thread in the system always acquires multiple locks in the same global order — e.g., always lock the lower-numbered or lower-hashcode resource first — the circular-wait condition that causes deadlock can never form, since no thread can ever be holding the 'second' lock while waiting for the 'first.'"

**Code:**

```java
Object lock1 = new Object(), lock2 = new Object();

// DEADLOCK-PRONE: opposite acquisition order between the two threads
Thread a = new Thread(() -> { synchronized (lock1) { synchronized (lock2) { /* work */ } } });
Thread b = new Thread(() -> { synchronized (lock2) { synchronized (lock1) { /* work */ } } });

// FIXED: consistent global order — both threads always lock1 THEN lock2
Thread aFixed = new Thread(() -> { synchronized (lock1) { synchronized (lock2) { /* work */ } } });
Thread bFixed = new Thread(() -> { synchronized (lock1) { synchronized (lock2) { /* work */ } } });
```

**Follow-up:**

This is deliberately the basic version of the topic — the Staff-level section of this guide covers how deadlock differs from livelock, starvation, and priority inversion, and walks through actually diagnosing a real production deadlock from a thread dump. The lock-ordering fix here is the right mental model to start from before that deeper material.

**Source:** [Oracle Java Tutorials — Deadlock](https://docs.oracle.com/javase/tutorial/essential/concurrency/deadlock.html)

---

### 7. What's the Difference Between `wait()`/`notify()` and `Thread.sleep()`?

**Answer:**

"`Thread.sleep(ms)` pauses the *current* thread for roughly the given duration and does **not** release any lock it's currently holding — if the sleeping thread holds a monitor, every other thread wanting that same monitor is blocked for the whole sleep, a common source of accidental contention.

`Object.wait()` is fundamentally different: it must be called from inside a `synchronized` block on that object, and it **releases the object's monitor** while waiting, letting other threads acquire it and do work — typically including calling `notify()`/`notifyAll()` on the same object to wake the waiting thread back up. `wait()`/`notify()` is the classic low-level mechanism for one thread to signal another that some condition it's waiting on has changed, without the waiting thread burning CPU polling in a loop."

**Code:**

```java
// sleep(): does NOT release the lock — other threads wanting `lock` are blocked the whole time
synchronized (lock) {
    Thread.sleep(1000); // holds `lock` for the whole second — bad if others need it
}

// wait()/notify(): releases the lock while waiting, letting other threads make progress
synchronized (lock) {
    while (!conditionMet) {
        lock.wait(); // releases lock HERE, re-acquires it automatically once notified
    }
}
// elsewhere, another thread:
synchronized (lock) {
    conditionMet = true;
    lock.notifyAll(); // wakes waiting threads — they re-acquire the lock before wait() returns
}
```

**Follow-up:**

I'd flag the classic gotcha directly: `wait()` must always be called in a loop re-checking the actual condition (`while`, not `if`), never assumed to mean "the condition I want is now true." A spurious wakeup — the JVM is explicitly allowed to wake a waiting thread without a corresponding `notify()` — or a `notifyAll()` intended for a different waiting condition can both wake the thread with the condition still false, and only re-checking the condition in a loop after waking protects against that. In modern code, this raw pattern is largely superseded by `java.util.concurrent`'s higher-level tools — `BlockingQueue`, `CountDownLatch`, `Condition` — covered in the Intermediate section, which handle exactly this correctly by construction.

**Source:** [`Object#wait()` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html#wait()), [Oracle Java Tutorials — Guarded Blocks](https://docs.oracle.com/javase/tutorial/essential/concurrency/guardmeth.html)

---

### 8. What Is a Daemon Thread?

**Answer:**

"A daemon thread is a background thread the JVM doesn't wait for before exiting — the JVM shuts down once every *non-daemon* ('user') thread has finished, regardless of whether any daemon threads are still running, and any still-running daemon threads are simply terminated abruptly at that point, with no guarantee their code finishes or even that `finally` blocks run.

Regular threads default to non-daemon; you mark one as a daemon via `setDaemon(true)` *before* calling `start()` — calling it after start throws `IllegalThreadStateException`. The typical use case is background housekeeping that should never be the reason the JVM stays alive — a periodic cache-cleanup thread, a metrics-reporting thread — where it would be actively wrong for that thread to block application shutdown."

**Code:**

```java
Thread cleanup = new Thread(() -> {
    while (true) {
        doHousekeeping();
        sleepQuietly(60_000);
    }
});
cleanup.setDaemon(true); // must be called BEFORE start()
cleanup.start();
// The JVM can exit even while `cleanup` is still looping, since it's a daemon thread
```

**Follow-up:**

I'd flag the practical risk directly: because a daemon thread can be killed mid-operation with no cleanup guarantee, it's the wrong choice for anything that needs to finish gracefully — flushing a write buffer, closing a network connection cleanly. That kind of work belongs on a non-daemon thread with an explicit, coordinated shutdown (a shutdown hook, or an `ExecutorService.shutdown()`/`awaitTermination()` sequence), not a daemon thread that just gets cut off.

**Source:** [`Thread#setDaemon(boolean)` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html#setDaemon(boolean))

---

## Intermediate

### 9. What Is `ExecutorService`, and Why Prefer It Over Raw Threads?

**Answer:**

"`ExecutorService` is the `java.util.concurrent` abstraction that decouples 'submitting a task' from 'how and on what thread it actually runs' — you submit `Runnable`/`Callable` tasks, and a thread pool underneath handles thread creation, reuse, scheduling, and queuing, instead of your code manually calling `new Thread(...).start()` for every unit of work.

This solves real problems raw threads have. Creating an OS thread is genuinely expensive — memory for the stack, kernel bookkeeping — so an unbounded 'one thread per task' approach can exhaust memory or file descriptors under load; a pool reuses a bounded number of threads across many tasks, amortizing that cost. `ExecutorService` also gives you a `Future` back from `submit()`, letting you retrieve a result, check completion, or cancel a task — none of which raw `Thread` gives you directly. `Executors` provides common factory presets (`newFixedThreadPool`, `newCachedThreadPool`, `newSingleThreadExecutor`, `newVirtualThreadPerTaskExecutor`), though the Staff-level section of this guide covers why hand-tuning a `ThreadPoolExecutor` directly, rather than reaching for an `Executors` factory blindly, is usually the more defensible production choice."

**Code:**

```java
ExecutorService pool = Executors.newFixedThreadPool(4);

Future<Integer> future = pool.submit(() -> {
    Thread.sleep(100);
    return 42;
});

System.out.println(future.get()); // blocks until the task completes, then returns 42

pool.shutdown(); // stop accepting new tasks, let queued/running ones finish
```

**Follow-up:**

I'd mention that `shutdown()` alone doesn't forcibly stop anything — it just stops accepting new submissions and lets already-submitted work finish. `shutdownNow()` attempts to interrupt actively-running tasks and returns the list of tasks that never started — the tool for "stop everything now," not `shutdown()`. Getting this distinction wrong (assuming `shutdown()` is immediate) is a common cause of an application that "hangs on exit" because it's actually just waiting, correctly, for a long-running queued task.

**Source:** [`ExecutorService` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ExecutorService.html)

---

### 10. `Runnable` vs. `Callable` vs. `Future` — What's the Difference?

**Answer:**

"`Runnable.run()` takes no arguments, returns nothing (`void`), and can't throw a checked exception — it's the original, pre-Java-5 functional shape for 'a unit of work.' `Callable<V>.call()` was added specifically to fix both limitations: it returns a value of type `V`, and it's allowed to throw a checked `Exception`, making it the right choice whenever a task actually produces a result or can fail in a way you want to handle explicitly rather than being forced to swallow it inside `run()`.

`Future<V>` is what you get back from submitting either kind of task to an `ExecutorService` — a `Runnable` submission gives you a `Future<?>` whose `get()` just returns `null` on success. It represents the *eventual result* of an asynchronous computation: `get()` blocks until the task completes and returns the result, or re-throws the task's exception wrapped in `ExecutionException`; `isDone()`/`isCancelled()` let you poll without blocking; and `cancel()` attempts to stop the task if it hasn't started, or interrupt it if it has — best-effort, not guaranteed."

**Code:**

```java
ExecutorService pool = Executors.newFixedThreadPool(2);

Runnable r = () -> System.out.println("no result, can't throw checked exceptions");
Future<?> f1 = pool.submit(r); // Future<?>, get() returns null

Callable<Integer> c = () -> 21 * 2; // CAN return a value, CAN throw checked exceptions
Future<Integer> f2 = pool.submit(c);

try {
    System.out.println(f2.get(2, TimeUnit.SECONDS)); // 42, with a timeout to avoid blocking forever
} catch (TimeoutException e) {
    f2.cancel(true); // best-effort: interrupt the task if it's still running
}
```

**Follow-up:**

I'd bring up `CompletableFuture` as the natural next step once callback-style composition matters — chaining what happens after a `Future` completes (`thenApply`, `thenCompose`, combining multiple futures) is awkward with a plain `Future`, where `get()` is your only real option and it blocks. `CompletableFuture` lets you build a non-blocking pipeline of dependent async steps, which is what most real asynchronous service code actually needs, rather than a single call-and-block `Future`.

**Source:** [`Callable` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Callable.html), [`Future` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Future.html)

---

### 11. How Do `CountDownLatch`, `CyclicBarrier`, and `Semaphore` Differ?

**Answer:**

"All three are `java.util.concurrent` coordination primitives, but they solve different shapes of problem.

`CountDownLatch` lets one or more threads wait until a fixed number of events have happened elsewhere — initialized with a count, other threads call `countDown()` as they finish their part, and any thread blocked on `await()` proceeds once the count hits zero. Critically, it's **one-shot**: once the count reaches zero it can never be reset or reused. `CyclicBarrier` is for making a fixed group of threads all wait for *each other* to reach the same point before any of them proceed — every thread calls `await()`, and none of them continue until all of them have called it. Unlike `CountDownLatch`, it's **reusable**, automatically resetting for the next round, and it optionally runs a single action once the barrier trips. `Semaphore` maintains a set of permits — `acquire()` blocks if none are available and takes one when it is, `release()` returns one — the right tool for limiting concurrent access to a resource with a fixed capacity (e.g., 'at most 10 concurrent connections to this downstream service'), not for one-time or round-based coordination at all."

**Code:**

```java
// CountDownLatch: wait for N things to finish, ONCE
CountDownLatch latch = new CountDownLatch(3);
for (int i = 0; i < 3; i++) pool.submit(() -> { doWork(); latch.countDown(); });
latch.await(); // blocks until all 3 have called countDown()

// CyclicBarrier: N threads wait for EACH OTHER, repeatedly, round after round
CyclicBarrier barrier = new CyclicBarrier(3, () -> System.out.println("round complete"));
Runnable worker = () -> { doWorkForThisRound(); barrier.await(); }; // reusable across rounds

// Semaphore: cap concurrent access to a resource
Semaphore permits = new Semaphore(10); // at most 10 concurrent callers
permits.acquire();
try { callDownstreamService(); } finally { permits.release(); }
```

**Follow-up:**

I'd give the quick decision rule: "wait for N one-time events" → `CountDownLatch`; "N threads must all reach a checkpoint together, possibly repeatedly" → `CyclicBarrier`; "cap concurrent access to a limited resource" → `Semaphore`. A common mistake is reaching for `CountDownLatch` when the real requirement is repeated rounds of synchronization — since it can't be reset, that forces awkward workarounds (creating a new latch every round) where `CyclicBarrier` was the actual right tool from the start.

**Source:** [`CountDownLatch` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CountDownLatch.html), [`CyclicBarrier` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CyclicBarrier.html), [`Semaphore` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Semaphore.html)

---

### 12. How Would You Implement the Producer-Consumer Pattern With `BlockingQueue`?

**Answer:**

"The producer-consumer pattern decouples work that generates tasks (producers) from work that processes them (consumers), connected through a shared queue — producers only need to know how to add items, consumers only need to know how to take them, and neither has to coordinate with the other directly.

`BlockingQueue` is the standard-library tool built for exactly this: `put()` blocks the producer if the queue is full, rather than growing unboundedly and risking an OOM under sustained overload, and `take()` blocks the consumer if the queue is empty, rather than busy-polling and burning CPU. Both sides get correct backpressure and correct waiting behavior for free, without any manual `wait()`/`notify()` bookkeeping. `ArrayBlockingQueue` gives you a fixed-capacity, backpressure-enforcing bound; `LinkedBlockingQueue` can be bounded or effectively unbounded depending on the constructor used."

**Code:**

```java
BlockingQueue<Task> queue = new ArrayBlockingQueue<>(100); // bounded — real backpressure

// Producer
Runnable producer = () -> {
    while (true) {
        Task task = generateNextTask();
        queue.put(task); // blocks here if the queue is already full — natural backpressure
    }
};

// Consumer
Runnable consumer = () -> {
    while (true) {
        Task task = queue.take(); // blocks here if the queue is empty — no busy-polling
        process(task);
    }
};
```

**Follow-up:**

I'd connect this directly back to the earlier `wait()`/`notify()` question — `BlockingQueue` implementations are doing exactly that kind of lock-and-signal coordination internally, just correctly, without you having to hand-write it and get the "always re-check in a loop" subtlety right yourself. I'd also flag the bounded-vs-unbounded choice as a real production decision, not a detail: an unbounded queue between a fast producer and a slow consumer just delays an eventual out-of-memory failure instead of preventing it — bounding the queue converts "silently grow until we crash" into "the producer blocks (or gets an explicit rejection, depending on the chosen `put`/`offer` variant) the moment we're actually behind," a far more diagnosable failure mode.

**Source:** [`BlockingQueue` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/BlockingQueue.html), [`ArrayBlockingQueue` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ArrayBlockingQueue.html)

---

### 13. `synchronized` vs. `ReentrantLock` — the Basic Trade-Off

**Answer:**

"`synchronized` is built into the language, always released automatically — even if an exception is thrown, since it's tied to block/method scope — and needs no explicit unlock call. For straightforward mutual exclusion, it's simpler and harder to get wrong.

`ReentrantLock` (from `java.util.concurrent.locks`) is an explicit, object-based lock that gives you capabilities `synchronized` simply doesn't have: `tryLock()` to attempt acquisition without blocking (or with a timeout), `lockInterruptibly()` to let a thread waiting for the lock be interrupted rather than stuck waiting forever, and a fairness option (`new ReentrantLock(true)`) to reduce the chance of an individual thread being perpetually starved by other threads jumping the queue. The real trade-off, and the reason `synchronized` should still be the default: `ReentrantLock` must be unlocked manually in a `finally` block — forget that, or throw an exception before the `try` even starts, and the lock is never released, which `synchronized` structurally can't get wrong."

**Code:**

```java
// synchronized: automatic release, can't forget to unlock
synchronized (lock) {
    doWork(); // lock released automatically even if doWork() throws
}

// ReentrantLock: explicit, more capable, but YOU are responsible for releasing it
ReentrantLock reentrantLock = new ReentrantLock();
reentrantLock.lock();
try {
    doWork();
} finally {
    reentrantLock.unlock(); // MUST be in finally — forgetting this leaks the lock permanently
}

// The capability synchronized can't offer at all: don't wait forever
if (reentrantLock.tryLock(500, TimeUnit.MILLISECONDS)) {
    try { doWork(); } finally { reentrantLock.unlock(); }
} else {
    handleCouldNotAcquireLock(); // give up gracefully instead of blocking indefinitely
}
```

**Follow-up:**

This is deliberately the basic version — the Staff-level section of this guide compares `synchronized`, `ReentrantLock`, `ReadWriteLock`, and `StampedLock` together, including where `StampedLock`'s optimistic-read mode gives a real throughput advantage `ReentrantLock` can't. The takeaway to carry forward from this basic comparison: default to `synchronized` unless you specifically need `tryLock`, interruptible waiting, or fairness — reaching for `ReentrantLock` "just because it's more powerful" adds real risk (the manual-unlock footgun) for no benefit if you never use the extra capabilities.

**Source:** [`ReentrantLock` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html)

---

## Staff Level

### 14. Explain Visibility, Atomicity, Ordering, and Happens-Before Relationships

**Answer:**

"These are three separate guarantees people often collapse into one, and conflating them is where most concurrency bugs come from.

**Visibility** is about whether a write made by thread A is *ever* guaranteed to be seen by thread B. Without a proper synchronization mechanism, a thread can legally keep reading a stale, cached value of a variable forever — the JIT compiler and CPU are both allowed to cache the value in a register and never re-read main memory, because nothing told them another thread might change it.

**Atomicity** is about whether an operation happens as one indivisible step or can be interleaved with other threads mid-way. `count++` looks like one operation but is actually read-modify-write — three separate steps — so two threads can both read the same value, both increment, both write back, and one increment is silently lost.

**Ordering** is about whether operations can be reordered relative to each other from another thread's point of view. The JVM and CPU are both allowed to reorder independent instructions for performance, as long as it doesn't change the *single-threaded* semantics of the thread doing the reordering — but another thread observing without synchronization can see effects out of the order they were written in source code.

The **happens-before** relationship is the formal contract that ties all three together: if action X happens-before action Y, then X's effects (visibility, ordering) are guaranteed visible to Y. It's established by specific things — a monitor unlock happens-before the next lock on that same monitor, a volatile write happens-before a subsequent volatile read of the same field, a thread's `start()` happens-before anything in the thread it started, the last action in a thread happens-before another thread's successful `join()` on it. Without one of these specific relationships, the JMM makes *no* guarantee about visibility or ordering between those two actions — not 'probably fine,' genuinely not guaranteed. That's a narrower claim than saying the program's behavior is 'undefined' in the C/C++ sense, though: the JMM (JLS Chapter 17) still constrains what a racy program is allowed to do — for ordinary reads/writes it guarantees no 'out of thin air' values, and the language and JVM remain otherwise fully specified. What you lose is the *guarantee* of a particular visible order or a particular value being seen promptly, not all behavioral guarantees whatsoever."

**Code:**

```java
// No synchronization at all — this can loop forever, or read a stale value,
// depending on JIT optimizations and CPU caching. Not guaranteed by the JMM
// (no happens-before edge between the write and the read) — not just
// "unlikely to work in practice," genuinely unspecified by the spec:
class NoVisibility {
    boolean ready = false;
    int value = 0;

    void writer() {
        value = 42;
        ready = true; // no happens-before edge to the reader thread at all
    }

    void reader() {
        while (!ready) { /* might spin forever — never sees the write */ }
        System.out.println(value); // could print 0 even after ready is true,
                                     // because of reordering with no barrier
    }
}

// Fixed with volatile — establishes a happens-before edge on every write/read pair
class WithVisibility {
    volatile boolean ready = false;
    int value = 0; // NOT volatile — but still safe, see explanation below

    void writer() {
        value = 42;          // (1)
        ready = true;         // (2) volatile write
    }

    void reader() {
        while (!ready) {}     // (3) volatile read — happens-after (2)
        System.out.println(value); // guaranteed to see 42, NOT because value
                                     // is volatile, but because (1) happens-before (2),
                                     // and (2) happens-before (3) by the volatile rule —
                                     // happens-before is transitive
    }
}
```

**Follow-up:**

I'd bring up that this is exactly why the Java Memory Model (JMM) exists as a formal specification rather than "whatever the hardware happens to do" — different CPU architectures (x86 vs ARM) have different native memory ordering guarantees, and the JMM gives Java a single, portable contract so the same code behaves correctly regardless of the underlying hardware's memory model. I'd also flag the transitivity point explicitly, since it's the thing that makes the `WithVisibility` example correct despite `value` not being `volatile` itself — happens-before chains compose, which is the actual mechanism behind "publish an object safely by writing it to a volatile/final field, then everything set up before that publish is visible to any thread that reads the field."

**Source:** [JLS §17.4, Memory Model](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4)

---

### 15. What Does `volatile` Guarantee, and What Does It Not Guarantee?

**Answer:**

"`volatile` guarantees visibility and ordering for that specific field — every write is immediately visible to subsequent reads by any thread, and the compiler/CPU can't reorder other reads/writes across a volatile read or write in ways that would break the happens-before chain. It's implemented, roughly, by inserting memory barriers around access to the field.

What it does **not** guarantee is atomicity for compound operations. `volatileCounter++` is still read-modify-write under the hood, and `volatile` does nothing to make that one atomic step — two threads can still race and lose an increment, exactly like a non-volatile field would. This is the single most common `volatile` misuse I see: people reach for `volatile` on a counter expecting thread-safety and get visibility without atomicity, which silently doesn't fix the actual bug."

**Code:**

```java
class BrokenCounter {
    volatile int count = 0;

    void increment() {
        count++; // STILL a race — volatile doesn't make this atomic.
                  // Two threads can both read count=5, both compute 6, both write 6 —
                  // one increment vanishes even though every individual read/write
                  // is perfectly visible to every thread.
    }
}

// The actual fix — either an atomic class, or a lock around the compound operation:
class CorrectCounter {
    private final AtomicInteger count = new AtomicInteger(0);
    void increment() { count.incrementAndGet(); } // genuinely atomic, CAS-based
}
```

**Follow-up:**

I'd give the rule of thumb explicitly: `volatile` is correct for a single field that's *independently* read/written — a flag, a reference being published, a "latest value wins" field — but the moment correctness depends on a *sequence* of operations on that field (increment, compare-then-set, read-modify-write), you need either an atomic class (`AtomicInteger`, `AtomicReference`) or a lock. I'd also mention the classic safe-publication idiom: a `volatile` reference to an immutable object is a cheap, lock-free way to publish a fully-constructed object across threads — every thread that reads the volatile reference sees a fully-initialized object, not a partially-constructed one, because of the happens-before edge on the volatile write that set the reference.

**Source:** [JLS §17.4.5, Happens-before Order (volatile rule)](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4.5), [`AtomicInteger` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html)

---

### 16. Compare `synchronized`, `ReentrantLock`, `ReadWriteLock`, and `StampedLock`

**Answer:**

"`synchronized` is the built-in intrinsic lock — simplest to use, automatically released on exit (even via exception), and JIT-optimized heavily over the years (biased locking historically, lock elision via escape analysis, adaptive spinning). Its limitations: you can't try to acquire it with a timeout, can't interrupt a thread that's blocked waiting for it, and it's strictly block-scoped — you can't acquire in one method and release in another.

`ReentrantLock` gives you all the flexibility `synchronized` lacks: `tryLock()` with a timeout, `lockInterruptibly()` so a blocked thread can actually be interrupted out of the wait, and multiple `Condition` objects per lock instead of just the one implicit wait-set `synchronized` gives you via `wait`/`notify`. The trade-off is you *must* remember to unlock in a `finally` block — nothing does it for you automatically.

`ReadWriteLock` (`ReentrantReadWriteLock`) separates read and write access — multiple readers can hold the read lock concurrently, but a writer needs exclusive access with no readers or other writers present. This is the right tool when reads vastly outnumber writes and you want more parallelism than a single exclusive lock allows.

`StampedLock` goes one step further with **optimistic reads** — a reader doesn't take a lock at all, just reads a stamp, does its work, then validates the stamp wasn't invalidated by a writer in the meantime. If validation fails, it falls back to a real read lock. For read-heavy workloads this can meaningfully outperform `ReadWriteLock` because the common case pays almost no locking cost at all — but it's not reentrant, and using it correctly is genuinely more error-prone."

**Code:**

```java
// ReentrantLock — the disciplined pattern, lock/finally always paired
private final ReentrantLock lock = new ReentrantLock();

void criticalSection() {
    lock.lock();
    try {
        // ... protected work ...
    } finally {
        lock.unlock(); // MUST be in finally — nothing does this automatically
    }
}

// tryLock with timeout — impossible with synchronized
boolean acquired = lock.tryLock(500, TimeUnit.MILLISECONDS);
if (acquired) {
    try { /* ... */ } finally { lock.unlock(); }
} else {
    // back off, fail fast, or retry — your choice, instead of blocking forever
}

// StampedLock optimistic read — the whole point is avoiding lock overhead
private final StampedLock stampedLock = new StampedLock();
private double x, y;

double distanceFromOrigin() {
    long stamp = stampedLock.tryOptimisticRead(); // no actual lock taken
    double curX = x, curY = y;
    if (!stampedLock.validate(stamp)) { // a writer interfered — fall back to a real lock
        stamp = stampedLock.readLock();
        try { curX = x; curY = y; } finally { stampedLock.unlockRead(stamp); }
    }
    return Math.sqrt(curX * curX + curY * curY);
}
```

**Follow-up:**

I'd bring up the reentrancy trap with `StampedLock` explicitly — unlike `ReentrantLock` and intrinsic locks, `StampedLock` is *not* reentrant, so a thread that already holds the write lock and calls back into a method that tries to acquire it again will deadlock against itself, which is a subtle regression risk if someone migrates code from `ReentrantLock` without noticing this difference. I'd also mention that `synchronized` has closed most of its historical performance gap with `ReentrantLock` thanks to JIT improvements — so the decision is rarely "which is faster," it's "do I need `tryLock`, interruptibility, multiple conditions, or read/write separation," and if the answer is no, plain `synchronized` is simpler and harder to misuse (no risk of a forgotten `unlock()`).

**Source:** [`ReentrantLock` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html), [`StampedLock` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/StampedLock.html)

---

### 17. How Do Deadlock, Livelock, Thread Starvation, and Priority Inversion Differ?

**Answer:**

"**Deadlock**: two or more threads each hold a resource the other needs, and each is blocked waiting for the other to release theirs — nobody makes progress, ever, and none of them are consuming CPU. Classic case: thread A locks `mutex1` then wants `mutex2`; thread B locks `mutex2` then wants `mutex1`.

**Livelock**: threads are actively running — not blocked — but they keep responding to each other in a way that prevents any of them from making real progress. The textbook example is two people in a hallway, each stepping aside to let the other pass, and their steps happen to keep mirroring each other forever. In code, this shows up as overly-polite retry/backoff logic where two threads keep detecting contention and yielding to each other in lockstep.

**Starvation**: a thread is technically able to make progress, but a scheduling or fairness issue means it practically never gets CPU time or lock access — e.g. a non-fair lock combined with a flood of higher-priority or more-frequent competitors means one thread's requests keep losing the race indefinitely.

**Priority inversion**: a higher-priority thread is blocked waiting on a lock held by a *lower*-priority thread, and — if the scheduler isn't priority-aware about this — a third, *medium*-priority thread that needs no lock at all can keep preempting the low-priority lock-holder, so the high-priority thread waits far longer than its priority would suggest. This is the actual root cause behind the famous 1997 Mars Pathfinder software reset — a low-priority task held a mutex a high-priority task needed, and medium-priority tasks kept starving the low-priority one out of running long enough to release it."

**Code:**

```java
// Deadlock — classic lock-ordering inversion
Object mutex1 = new Object(), mutex2 = new Object();

// Thread A
synchronized (mutex1) {
    // ... does some work ...
    synchronized (mutex2) { /* ... */ } // waits forever if B holds mutex2 already
}

// Thread B
synchronized (mutex2) {
    synchronized (mutex1) { /* ... */ } // waits forever if A holds mutex1 already
}

// The fix: enforce a GLOBAL, consistent lock acquisition order everywhere —
// e.g. always lock the object with the smaller identityHashCode first.
// If every thread agrees on the same order, circular waiting is structurally impossible.
```

**Follow-up:**

I'd talk about the general prevention strategy rather than just naming the failure modes: deadlock prevention is really about breaking one of the four Coffman conditions (mutual exclusion, hold-and-wait, no preemption, circular wait) — and in practice, enforcing a consistent global lock ordering (breaking circular wait) is the cheapest and most common fix. I'd also mention `Thread.getAllStackTraces()` or a thread dump (`jstack`) as the actual diagnostic tool — the JVM's own deadlock detector in `jstack` output will explicitly print `"Found one Java-level deadlock"` with the exact lock cycle, which is usually the fastest way to confirm a deadlock versus other stalls in production. For priority inversion specifically, I'd mention priority inheritance (temporarily boosting the lock-holder's priority to match the highest-priority waiter) as the real-time-systems fix — Java's default scheduler doesn't do this automatically, which is part of why Java is rarely chosen for hard real-time systems.

**Source:** [`jstack` documentation](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jstack.html), [JLS §17, Threads and Locks](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)

---

### 18. How Would You Identify and Resolve a Production Deadlock?

**Answer:**

"First move is a thread dump — `jstack <pid>`, or `kill -3 <pid>` on the JVM to print it to stdout/logs, or `jcmd <pid> Thread.print` — taken *while the system is still stuck*, not after restarting it, since a restart destroys the evidence. The JVM's own deadlock detector runs on this and, if it's a classic lock-based deadlock, prints exactly which threads are involved and which locks each is holding versus waiting for, right there in the dump output — I don't have to reconstruct it by hand.

From there, resolution has two parts: unblocking the *current* incident (usually a restart, since a genuine deadlock doesn't resolve itself), and the actual fix, which is finding the code paths that acquire the same set of locks in different orders and standardizing the acquisition order — or, more often at staff level, questioning whether two locks need to be held simultaneously at all, since reducing lock scope or redesigning to avoid nested locking is usually a better fix than 'just be more careful about ordering,' which tends to regress the next time someone adds a new code path."

**Code:**

```bash
# Capture a thread dump without killing the process
jstack <pid> > threaddump.txt
# or, without needing jstack installed separately:
jcmd <pid> Thread.print > threaddump.txt

# The jstack output explicitly calls out deadlocks, e.g.:
#   Found one Java-level deadlock:
#   =============================
#   "Thread-A":
#     waiting to lock monitor 0x00007f... (object 0x000000076..., a java.lang.Object),
#     which is held by "Thread-B"
#   "Thread-B":
#     waiting to lock monitor 0x00007f... (object 0x000000076..., a java.lang.Object),
#     which is held by "Thread-A"
```

```java
// The structural fix: consistent lock ordering via a stable, shared tie-breaker
void transfer(Account a, Account b, BigDecimal amount) {
    Account first = a.getId() < b.getId() ? a : b;
    Account second = a.getId() < b.getId() ? b : a;
    synchronized (first) {
        synchronized (second) {
            // now every caller, regardless of argument order, locks in the same
            // global order — a transfer(a, b) and a concurrent transfer(b, a)
            // can never deadlock against each other
        }
    }
}
```

**Follow-up:**

I'd talk about prevention infrastructure, since staff-level answers should go past "how do I fix this one incident": adding a lock-order verifier in tests or as a lightweight runtime check in non-production environments (some APM/observability tools do this, and it's also a known pattern to build in-house — track the lock acquisition graph and flag any edge that would create a cycle) catches ordering violations before they ship, rather than discovering them via a stuck production thread pool. I'd also mention that reducing the *scope* of what's protected by nested locks — restructuring so no code path ever needs two locks held simultaneously in the first place — is often a better long-term fix than "get really disciplined about ordering," because ordering discipline degrades as a codebase grows and more people touch it.

**Source:** [`jcmd` documentation](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html)

---

### 19. Explain the Risks of Calling External Services While Holding a Lock

**Answer:**

"Holding a lock — an in-process `synchronized`/`ReentrantLock`, or worse, a database row lock or distributed lock — while making a network call (an HTTP request, a downstream RPC, a database query to a *different* system) ties the lock's hold duration to that network call's latency, which is now completely outside your control. If that downstream service gets slow — and downstream services get slow far more often than they go fully down — every thread waiting on that lock is now waiting on a slow network call it doesn't even know exists, and the blast radius spreads: the lock holder is blocked, everyone waiting for the lock is blocked, and if this is a shared resource (a connection pool, a widely-used cache lock), the slowdown cascades into what looks like a much bigger outage than the actual root cause.

This is a very common way a single slow downstream dependency turns into a full outage — a thread pool exhausts because every thread is stuck holding a lock waiting on the same slow call, and now unrelated requests that don't even touch that downstream service can't get a thread either."

**Code:**

```java
// DANGEROUS — lock held across a network call
private final ReentrantLock lock = new ReentrantLock();

void updateAndNotify(String id) {
    lock.lock();
    try {
        localState.update(id);
        externalService.notify(id); // network call — could take 30s, or hang, or time out slowly.
                                      // Every other thread wanting this lock is now blocked
                                      // on someone else's HTTP request.
    } finally {
        lock.unlock();
    }
}

// FIXED — do the protected work under the lock, release it, then call out
void updateAndNotifyCorrectly(String id) {
    lock.lock();
    try {
        localState.update(id);
    } finally {
        lock.unlock(); // released BEFORE the network call
    }
    externalService.notify(id); // any slowness here only affects this one call,
                                  // not every other thread needing the lock
}
```

**Follow-up:**

I'd tie this directly into a broader principle: locks should protect the smallest possible critical section, and specifically should never wrap anything with unbounded or externally-controlled latency — that includes network calls, but also file I/O, and even logging to a slow sink. I'd bring up the real production pattern this causes: thread pool exhaustion cascading across unrelated request paths, because the thread pool doesn't know 'these threads are stuck for a legitimate-looking reason' — from the outside it just looks like every thread is busy, and everything using that pool queues up or gets rejected. The actual staff-level fix pattern is: do the minimal state mutation under the lock, release it, then perform the network call outside any lock — and if the network call's result needs to feed back into protected state, re-acquire the lock briefly for that specific update rather than holding it across the whole round trip.

**Source:** [`ReentrantLock` Javadoc — general lock usage guidance](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html)

---

### 20. Compare Platform Threads, Virtual Threads, Reactive Execution, and Asynchronous Futures

**Answer:**

"**Platform threads** are thin wrappers around OS threads — one Java thread maps to one OS thread. They're relatively expensive: megabyte-scale stacks by default, and OS-level context switching costs, so you can realistically run maybe a few thousand of them concurrently before the overhead itself becomes the bottleneck. This is the reason thread-pool-per-request architectures cap out where they do.

**Virtual threads** (Project Loom, standard since Java 21) are JVM-managed lightweight threads — you can spin up millions of them, and they're 'mounted' onto a small pool of underlying platform (carrier) threads only while actually doing CPU work. When a virtual thread blocks on I/O — a JDBC call, an HTTP request, `Thread.sleep()` — the JVM unmounts it from its carrier thread entirely, freeing that carrier to run other virtual threads, and remounts it (potentially on a different carrier) once the I/O completes. The huge win is you keep writing plain, blocking, imperative code — no callbacks, no reactive operators — and still get the scalability of non-blocking I/O under the hood.

**Reactive execution** (Project Reactor, RxJava) achieves similar scalability differently — a small, fixed pool of threads services a much larger number of logical operations via non-blocking, callback/operator-chain-based composition, and no thread is ever dedicated to waiting on one request. It scales extremely well, but at a real cost to code readability and debuggability — stack traces become nearly useless, and the mental model shift (operators, backpressure, schedulers) is substantial.

**Asynchronous futures** (`CompletableFuture`) sit in between — still callback/composition-based, but a more direct, lower-ceremony API than a full reactive library, well suited to orchestrating a handful of async operations without adopting an entire reactive programming model."

**Code:**

```java
// Platform-thread-per-request: caps out because each blocked thread ties up
// a full OS thread and its megabyte-scale stack, purely while doing nothing but waiting
void handleRequestOldWay() {
    String result = restTemplate.getForObject(url, String.class); // blocks the OS thread
}

// Virtual threads: same blocking code, but the underlying carrier thread is freed
// during the block — write it exactly like synchronous code:
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 100_000; i++) {
        executor.submit(() -> {
            String result = restTemplate.getForObject(url, String.class); // blocks the
            // VIRTUAL thread only — the carrier thread is freed to run other work
            return result;
        });
    }
} // millions of these are realistic; the same count of platform threads is not

// CompletableFuture: explicit async composition without a full reactive stack
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> fetchUser(id))
    .thenApply(user -> user.getName())
    .exceptionally(ex -> "fallback");
```

**Follow-up:**

I'd frame this as: virtual threads largely remove the *scalability* argument for reactive programming in a lot of typical request/response services — you get the throughput benefit of non-blocking I/O without paying the readability/debuggability cost of reactive operator chains. But I'd be careful not to overclaim: reactive still earns its place for genuinely stream-oriented workloads (continuous, potentially infinite data streams, real backpressure requirements between producer and consumer, complex operator composition like windowing/merging/throttling multiple streams) — that's a different problem than "many concurrent blocking calls," and virtual threads don't give you backpressure semantics at all. The practical staff-level answer is: default to virtual threads for typical blocking-I/O-bound services now, and reach for reactive specifically when you need actual stream semantics, not just concurrency.

**Source:** [JEP 444, Virtual Threads](https://openjdk.org/jeps/444), [`CompletableFuture` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CompletableFuture.html)

---

### 21. Where Do Virtual Threads Help, and Where Might They Not Improve Performance?

**Answer:**

"Virtual threads help enormously for I/O-bound workloads with high concurrency — a service handling many concurrent requests that each spend most of their time waiting on a database, another service, or a file — because the JVM unmounts a blocked virtual thread from its carrier, so 'thousands of concurrently-waiting requests' stops being expensive. This is squarely the sweet spot: thread-per-request architectures that used to be capped by platform-thread overhead can now scale much further with the same simple, blocking code style.

They do **not** help CPU-bound work at all — if a task is genuinely crunching numbers with no blocking I/O, there's no unmounting opportunity, and you're still fundamentally limited by the number of actual CPU cores available. Spinning up a million virtual threads all doing pure computation just means a million things contending for the same small number of cores — no throughput gain, and likely worse scheduling overhead than a properly-sized platform thread pool would have.

They also don't help — and can actively hurt — when code does something that 'pins' the virtual thread to its carrier: synchronized blocks/methods around blocking I/O historically prevented unmounting (fixed in most cases as of JDK 24, but a real concern on earlier 21/22/23 releases), and native code called via JNI also pins. A pinned virtual thread blocks its carrier exactly like an old-style platform thread would, silently defeating the entire point."

**Code:**

```java
// GOOD fit: I/O-bound, high concurrency, simple blocking code that now scales
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (Order order : pendingOrders) {
        executor.submit(() -> {
            var inventory = inventoryClient.check(order.sku()); // blocks — fine, unmounts
            var payment = paymentClient.charge(order.amount());  // blocks — fine, unmounts
            return process(order, inventory, payment);
        });
    }
}

// BAD fit: CPU-bound — virtual threads add nothing here, still core-limited
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (BigDecimal[] matrix : matrices) {
        executor.submit(() -> computeExpensiveMatrixInversion(matrix)); // no blocking,
        // no unmount opportunity — this is just contending for real CPU cores,
        // a fixed-size platform thread pool sized to core count is the right tool
    }
}

// PINNING trap — synchronized around a blocking call defeats virtual threads
// on JDK versions before this was addressed (JDK 24 significantly reduced this):
synchronized (lock) {
    restTemplate.getForObject(url, String.class); // pins the carrier thread for
    // the whole blocking call duration — exactly the platform-thread cost you
    // were trying to avoid by using virtual threads in the first place
}
```

**Follow-up:**

I'd bring up `jdk.tracePinnedThreads` (a JFR/diagnostic flag) as the actual tool for finding pinning in a real codebase before it becomes a mystery throughput ceiling — it's the difference between "virtual threads didn't help and I don't know why" and "here's the exact synchronized block causing pinning." I'd also flag that virtual threads are unbounded by design — no thread pool queue to naturally provide backpressure — so a system that used to be implicitly rate-limited by "only N platform threads available" can, with virtual threads, happily accept far more concurrent work than a downstream dependency (a database connection pool, a rate-limited external API) can actually handle, so you need to add explicit backpressure (a semaphore, a bounded connection pool) rather than relying on thread-pool sizing to do it for you implicitly like before.

**Source:** [JEP 444, Virtual Threads — Pinning section](https://openjdk.org/jeps/444)

---

### 22. How Would You Size an Executor for CPU-Bound Versus I/O-Bound Workloads?

**Answer:**

"For CPU-bound work, the classic formula is roughly `number of cores` (or `cores + 1` to keep a core busy during the rare page fault or context switch) — beyond that, threads are just fighting over the same fixed compute resource, and adding more only increases context-switching overhead without adding throughput.

For I/O-bound work with platform threads, the calculation is different: threads spend most of their time *waiting*, not computing, so you want more threads than cores — a common heuristic is `cores × (1 + wait_time/compute_time)`. If a task waits on I/O for 90% of its time and computes for 10%, that ratio is 9, so you'd want roughly 10x the core count in threads to keep cores actually busy while others wait.

But at this point I'd flag the more important staff-level answer: with virtual threads now available, this entire sizing exercise for I/O-bound work mostly goes away — you don't size a platform-thread pool for I/O concurrency anymore, you use a virtual-thread-per-task executor and let the JVM handle carrier-thread scheduling. The sizing question becomes much more narrowly about CPU-bound work (still use a fixed platform-thread pool sized to cores) and about applying explicit backpressure/concurrency limits to protect downstream dependencies, which is a different problem from thread-pool sizing."

**Code:**

```java
// CPU-bound — fixed pool sized to available cores
int cores = Runtime.getRuntime().availableProcessors();
ExecutorService cpuPool = Executors.newFixedThreadPool(cores);

// I/O-bound, pre-virtual-threads era — oversized pool to keep cores busy
// while most threads are blocked waiting on network/disk:
double waitToComputeRatio = 9.0; // e.g., 90% waiting / 10% computing
int ioPoolSize = (int) (cores * (1 + waitToComputeRatio));
ExecutorService legacyIoPool = Executors.newFixedThreadPool(ioPoolSize);

// I/O-bound, modern approach — skip the sizing math entirely
ExecutorService ioPool = Executors.newVirtualThreadPerTaskExecutor();
// but STILL bound concurrency against a downstream dependency explicitly,
// since virtual threads removed the accidental backpressure the old pool size gave you:
Semaphore downstreamLimit = new Semaphore(50); // e.g., matches DB connection pool size
```

**Follow-up:**

I'd talk about how thread pool sizing used to double as an accidental backpressure mechanism — a platform-thread pool capped at 200 threads implicitly capped how many concurrent requests could hit a downstream database, because you simply couldn't have more than 200 in flight. Moving to virtual threads removes that accidental cap, which means the *explicit* backpressure now has to live somewhere else — a bounded connection pool, a semaphore, a rate limiter — or a burst of traffic that virtual threads happily accept can overwhelm a downstream dependency that was previously protected only by accident. I'd frame this as the actual mindset shift staff engineers need to make: stop thinking "size my thread pool to protect downstream systems" and start thinking "explicitly protect downstream systems, independent of how many threads I can spin up."

**Source:** [`ThreadPoolExecutor` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)

---

### 23. What Happens When an Executor's Queue Fills? How Do Rejection Policies Affect Reliability?

**Answer:**

"A `ThreadPoolExecutor` has a core pool size, a max pool size, and a bounded work queue. Once the core threads are all busy, new tasks go into the queue. Once the queue is *also* full, and the pool hasn't hit max size yet, new threads get created up to max. Once you're at max threads *and* the queue is full, the next submitted task triggers the configured `RejectedExecutionHandler`.

The default policy, `AbortPolicy`, throws `RejectedExecutionException` right there at the call site — which is actually the *safest* default for reliability, because it fails loudly and immediately, and the caller has to explicitly decide what to do (retry, shed load, return a 503). The alternatives all trade that visibility away: `CallerRunsPolicy` runs the task on the submitting thread itself, which provides a crude form of backpressure (the producer literally can't submit more until it finishes this one) but can stall an unrelated caller (e.g., a request-handling thread) doing work it didn't expect to do. `DiscardPolicy` silently drops the task — genuinely dangerous for anything with business consequences, since nothing logs or signals it happened. `DiscardOldestPolicy` drops the oldest queued task to make room — same silent-loss problem, just applied to a different task."

**Code:**

```java
ExecutorService executor = new ThreadPoolExecutor(
    10,                              // core pool size
    20,                              // max pool size
    60L, TimeUnit.SECONDS,           // idle thread keep-alive
    new ArrayBlockingQueue<>(100),   // bounded queue — unbounded queues are a
                                      // production hazard: memory grows unbounded
                                      // under sustained overload instead of failing fast
    new ThreadPoolExecutor.AbortPolicy() // fail loudly and immediately when overloaded —
                                           // forces the caller to handle backpressure explicitly
);

try {
    executor.submit(() -> processOrder(order));
} catch (RejectedExecutionException e) {
    // explicit, visible handling — e.g. return 503, push to a retry queue,
    // increment a "rejected_tasks" metric that pages someone if it spikes
    metrics.increment("order.executor.rejected");
    throw new ServiceOverloadedException("order processing at capacity", e);
}
```

**Follow-up:**

I'd flag the unbounded queue as the more dangerous default that people reach for without thinking — `Executors.newFixedThreadPool()` actually uses an unbounded `LinkedBlockingQueue` internally, which means under sustained overload the queue just keeps growing, consuming memory until an OOM, rather than failing fast and giving you an early, actionable signal. I'd argue explicitly for bounded queues plus `AbortPolicy` (or a custom handler that at minimum logs/metrics every rejection) as the reliability-first default, because silent degradation (unbounded queue growth, or silently discarded tasks) is much worse operationally than a loud, immediate failure you can alert on and handle at the call site.

**Source:** [`ThreadPoolExecutor` Javadoc — RejectedExecutionHandler section](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)

---

### 24. Explain Work Stealing in `ForkJoinPool`

**Answer:**

"A regular `ThreadPoolExecutor` gives every worker thread tasks from one shared queue. `ForkJoinPool` instead gives each worker its own *deque* (double-ended queue). A worker pushes and pops its own new subtasks from the head of its own deque — normal LIFO order, which is cache-friendly since recently-created subtasks are likely still hot in cache.

The 'work stealing' part: when a worker's own deque runs empty, instead of sitting idle, it goes and *steals* a task from the **tail** of some other busy worker's deque — the opposite end from where that worker is actively popping. Stealing from the tail (rather than the head, where the owner is working) minimizes contention between the owner and the thief, and it also tends to steal the *largest*, oldest-created subtasks, which is usually exactly the coarse-grained work best suited to being redistributed to an idle worker.

This makes `ForkJoinPool` particularly good at recursive divide-and-conquer workloads (`RecursiveTask`/`RecursiveAction`, and it's what parallel streams use under the hood) where the amount of work per subtask is uneven and unpredictable — some branches finish fast, some slow, and idle workers automatically pick up slack from busy ones instead of sitting there unused."

**Code:**

```java
// Classic divide-and-conquer with RecursiveTask — ForkJoinPool distributes
// unevenly-sized subtasks automatically via work stealing
class SumTask extends RecursiveTask<Long> {
    private final long[] array;
    private final int start, end;
    private static final int THRESHOLD = 10_000;

    SumTask(long[] array, int start, int end) {
        this.array = array; this.start = start; this.end = end;
    }

    @Override
    protected Long compute() {
        if (end - start <= THRESHOLD) {
            long sum = 0;
            for (int i = start; i < end; i++) sum += array[i];
            return sum;
        }
        int mid = (start + end) / 2;
        SumTask left = new SumTask(array, start, mid);
        SumTask right = new SumTask(array, mid, end);
        left.fork();                 // pushed onto this worker's own deque
        long rightResult = right.compute(); // computed directly on this thread
        long leftResult = left.join();      // if not yet stolen, just pop it locally;
                                              // if stolen and still running, wait for it
        return leftResult + rightResult;
    }
}

ForkJoinPool pool = ForkJoinPool.commonPool();
long total = pool.invoke(new SumTask(bigArray, 0, bigArray.length));

// Parallel streams use the common ForkJoinPool under the hood, for free:
long total2 = LongStream.of(bigArray).parallel().sum();
```

**Follow-up:**

I'd contrast this with a plain `ThreadPoolExecutor`'s single shared queue explicitly: a shared queue means every worker contends on the same lock/CAS to grab work, and it can't naturally handle recursive task splitting (a task creating more sub-tasks that also need distributing) as gracefully — `ForkJoinPool` was purpose-built for exactly this recursive-splitting shape. I'd also flag that the common pool is shared JVM-wide by default (used by parallel streams and `CompletableFuture`'s async methods without an explicit executor), which sets up the next question about the danger of blocking inside it.

**Source:** [`ForkJoinPool` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ForkJoinPool.html), [`RecursiveTask` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/RecursiveTask.html)

---

### 25. What Is the Danger of Blocking Inside the Common `ForkJoinPool`?

**Answer:**

"The common `ForkJoinPool` is shared, process-wide, and sized by default to `number of cores - 1` — deliberately small, because it's designed for CPU-bound, compute-heavy divide-and-conquer work, not for waiting. If code running inside it — a parallel stream operation, a `CompletableFuture.supplyAsync()` call with no explicit executor, a `.thenApplyAsync()` — makes a *blocking* call (a JDBC query, an HTTP request, `Thread.sleep()`), it ties up one of that small, fixed number of worker threads for the entire duration of the block.

Because the pool is shared across the *entire JVM*, this isn't isolated to your one feature — every other unrelated piece of code in the same process that happens to use parallel streams or the common pool now has fewer workers available, and under enough concurrent blocking calls, the whole pool can be starved, silently degrading throughput for code that has nothing to do with whatever's doing the blocking. This is a genuinely nasty production bug because it's non-local: the fix often isn't in the code that's slow, it's in unrelated code sharing the same global resource."

**Code:**

```java
// DANGEROUS — parallel stream elements do blocking I/O on the shared common pool
List<String> results = ids.parallelStream()
    .map(id -> restTemplate.getForObject(url + id, String.class)) // BLOCKS a
    // common-pool worker thread per call — and the common pool is shared with
    // every other parallel stream and CompletableFuture in this entire JVM process
    .toList();

// Same problem, more explicit — no executor specified means the common pool
CompletableFuture<String> future = CompletableFuture.supplyAsync(() ->
    restTemplate.getForObject(url, String.class) // blocking call on the common pool
);

// FIXED — use a dedicated, appropriately-sized executor for blocking work,
// keeping the common pool free for actual CPU-bound work
ExecutorService ioExecutor = Executors.newVirtualThreadPerTaskExecutor();
CompletableFuture<String> future2 = CompletableFuture.supplyAsync(
    () -> restTemplate.getForObject(url, String.class),
    ioExecutor // explicit executor — isolates blocking work from the shared common pool
);
```

**Follow-up:**

I'd bring up `ManagedBlocker` as the "correct" mechanism if you genuinely must block inside a `ForkJoinPool` task — it lets the pool know a worker is about to block so it can temporarily spin up a compensating thread to keep parallelism roughly constant — but I'd be honest that in practice, the much simpler and more common fix is: never run blocking I/O on the common pool at all, and always pass an explicit, dedicated executor (ideally a virtual-thread executor now) for any `CompletableFuture` async work that involves I/O, reserving the common pool for genuinely CPU-bound parallel computation. I'd also mention this is a good "hidden gotcha" to bring up unprompted — it's the kind of bug that looks like unrelated code getting slower for no reason, and tracing it back to a shared thread pool being starved by blocking calls elsewhere in the same JVM is a genuinely hard-to-diagnose production incident if you don't already know to look for it.

**Source:** [`ForkJoinPool.ManagedBlocker` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ForkJoinPool.ManagedBlocker.html)

---

### 26. How Do You Prevent Race Conditions in Lazy Initialization?

**Answer:**

"The naive lazy-init pattern — `if (instance == null) instance = new Thing();` — is a textbook check-then-act race: two threads can both see `null`, both construct, and depending on the field type, one construction can even leak a *partially-initialized* object to another thread due to instruction reordering (the constructor writes fields, then the reference assignment happens, but without proper synchronization the reference write can be observed before all the constructor's field writes are visible).

The classic broken 'fix' historically was double-checked locking without `volatile` — it looks correct, and for years people wrote it without realizing the reordering hazard, until the JMM was clarified in Java 5 specifically to make `volatile` the piece that closes the gap. With a `volatile` field, double-checked locking is actually correct in modern Java. But honestly, at this point I'd default to simpler idioms that sidestep the whole class of bug: the initialization-on-demand holder idiom (a nested static class, relying on the JVM's own thread-safe class-loading guarantee) for a classic singleton, or just `ConcurrentHashMap.computeIfAbsent()` if the lazy value is keyed."

**Code:**

```java
// BROKEN without volatile — a genuine, non-theoretical bug pre-Java-5 clarification,
// and still broken today if you forget volatile:
class BrokenSingleton {
    private static BrokenSingleton instance; // NOT volatile — reordering hazard

    static BrokenSingleton getInstance() {
        if (instance == null) {                  // first check, no lock
            synchronized (BrokenSingleton.class) {
                if (instance == null) {           // second check, under lock
                    instance = new BrokenSingleton(); // can publish a partially-
                    // constructed reference to another thread without volatile,
                    // because of instruction reordering between the constructor's
                    // field writes and this reference assignment
                }
            }
        }
        return instance;
    }
}

// CORRECT — volatile closes the exact gap the broken version has
class DoubleCheckedSingleton {
    private static volatile DoubleCheckedSingleton instance;

    static DoubleCheckedSingleton getInstance() {
        if (instance == null) {
            synchronized (DoubleCheckedSingleton.class) {
                if (instance == null) {
                    instance = new DoubleCheckedSingleton();
                }
            }
        }
        return instance;
    }
}

// SIMPLER and preferred — initialization-on-demand holder idiom.
// Relies on the JVM's own guarantee: a class isn't initialized until first
// actively used, and class initialization is inherently thread-safe.
class HolderSingleton {
    private HolderSingleton() {}
    private static class Holder {
        static final HolderSingleton INSTANCE = new HolderSingleton();
    }
    static HolderSingleton getInstance() { return Holder.INSTANCE; }
}
```

**Follow-up:**

I'd point out that this whole category of bug is exactly why the holder idiom or `computeIfAbsent` are the practical staff-level recommendation over hand-rolled double-checked locking — they're correct by construction and don't rely on every future maintainer remembering the `volatile` requirement. I'd also mention `enum`-based singletons as another JVM-guaranteed-safe pattern (Effective Java's recommendation) when serialization-safety is also a concern, since enum singletons get free protection against reflection-based and serialization-based singleton-breaking that a plain class doesn't.

**Source:** [JLS §12.4, Initialization of Classes](https://docs.oracle.com/javase/specs/jls/se21/html/jls-12.html#jls-12.4), [JLS §17.4.5 — the volatile happens-before rule that fixes double-checked locking](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4.5)

---

### 27. Explain Safe Publication and Escaping `this` During Construction

**Answer:**

"'Safe publication' means making an object visible to other threads in a way that guarantees they see it in a fully, correctly constructed state — not a half-built object with some fields still at their default values. The JMM gives you specific safe-publication idioms: publishing via a `static` initializer, via a `volatile` field or `AtomicReference`, via a properly locked field, or via a `final` field (with the important caveat below).

'Escaping `this`' is the classic way to accidentally break safe publication from *inside* the constructor itself: if a constructor passes `this` to another object — registers itself as a listener, starts a thread that captures `this`, hands `this` to some other collaborator — before construction has finished, that other code can observe the object *before all its fields are set*, because the reference escaped early. This is dangerous specifically because it looks locally correct — the constructor reads like it 'finishes' before anyone else could see the object — but the escape happens mid-construction, not after."

**Code:**

```java
// BROKEN — this escapes before construction finishes
class ThisEscapes {
    private int value;

    ThisEscapes(EventBus bus) {
        bus.register(this); // DANGER: another thread can now call a method on
        // this object via the event bus BEFORE the line below even runs —
        // it could see value == 0 (the default), not whatever this constructor
        // is about to set it to
        this.value = computeInitialValue();
    }
}

// FIXED — finish construction fully, THEN publish
class SafePublication {
    private final int value;

    private SafePublication(int value) {
        this.value = value; // final field, set entirely within the constructor
    }

    static SafePublication createAndRegister(EventBus bus) {
        SafePublication instance = new SafePublication(computeInitialValue());
        bus.register(instance); // only registered AFTER full construction
        return instance;
    }
}
```

**Follow-up:**

I'd bring up the specific `final`-field guarantee, since it's more precise than people usually state it: the JMM guarantees that if an object is constructed correctly (no `this`-escape during construction) and its `final` fields are set in the constructor, then any thread that gets a reference to the object *after* construction completes is guaranteed to see the correctly initialized values of those `final` fields — without needing any additional synchronization. This is specifically why immutable objects (all fields `final`, no escape) are inherently safe to publish across threads with nothing more than a plain reference handoff, which is the mechanism underpinning why "make it immutable" is such a strong general answer to concurrency questions. I'd also mention that starting a thread from within a constructor is a specific, common instance of `this`-escape people don't always recognize as one — the thread you start can call back into the partially-constructed object before the constructor returns.

**Source:** [JLS §17.5, Final Field Semantics](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.5), *Java Concurrency in Practice* — safe publication idioms (Goetz et al.)

---

### 28. How Would You Implement a Bounded, Thread-Safe Cache?

**Answer:**

"The core building block is `ConcurrentHashMap` for thread-safe storage, but a plain `ConcurrentHashMap` isn't bounded — it'll grow forever unless something actively evicts. So the actual design question is really 'what's the eviction policy and how do I make eviction itself thread-safe without serializing every access.'

For a from-scratch implementation, I'd combine `ConcurrentHashMap` for storage with `computeIfAbsent` for atomic load-if-absent, plus a bounded structure (or an access-order `LinkedHashMap` under a lock, for LRU specifically — though that reintroduces single-lock contention, per question 23 in the collections file). But honestly, at staff level, the correct practical answer is: don't hand-roll this for a production system — reach for **Caffeine**, which gives you a high-performance, thread-safe, bounded cache with size-based and time-based eviction, an approximate LRU/LFU hybrid policy (Window TinyLFU), asynchronous loading, and refresh-ahead semantics, all without the lock-contention or correctness pitfalls of a hand-rolled version. I'd only hand-roll something like this in an interview to demonstrate I understand the underlying mechanics, not as an actual recommendation for real code."

**Code:**

```java
// From-scratch sketch, demonstrating the mechanics (not a production recommendation):
class BoundedCache<K, V> {
    private final int capacity;
    private final ConcurrentHashMap<K, V> map = new ConcurrentHashMap<>();
    private final ConcurrentLinkedQueue<K> insertionOrder = new ConcurrentLinkedQueue<>();

    BoundedCache(int capacity) { this.capacity = capacity; }

    V get(K key, Function<K, V> loader) {
        return map.computeIfAbsent(key, k -> { // atomic load-if-absent
            V value = loader.apply(k);
            insertionOrder.add(k);
            if (map.size() >= capacity) { // >= not > : computeIfAbsent hasn't committed
                                            // this key into the map yet while this
                                            // function is running, so map.size() here
                                            // doesn't include it — ">" would let the
                                            // cache settle at capacity + 1, not capacity
                K oldest = insertionOrder.poll(); // approximate FIFO eviction,
                if (oldest != null) map.remove(oldest); // NOT true LRU — good enough
                                                           // to illustrate the shape,
                                                           // not for production correctness
            }
            return value;
        });
    }
}

// What I'd actually ship:
LoadingCache<String, User> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(Duration.ofMinutes(10))
    .refreshAfterWrite(Duration.ofMinutes(5))   // async refresh-ahead, avoids stampedes
    .recordStats()
    .build(key -> userRepository.load(key));    // synchronous loader; async variant available too
```

**Follow-up:**

I'd emphasize the point explicitly: this is exactly the kind of infrastructure code where hand-rolling introduces subtle bugs (approximate eviction, race conditions between eviction and concurrent reads, no cache stampede protection) that a mature library has already solved correctly and battle-tested at scale — a staff engineer's job here is largely to *recognize* that this is a solved problem and steer the team toward Caffeine (or Guava's older `CacheBuilder`) rather than to demonstrate cleverness by writing a custom one. I'd also connect this forward to the caching category (cache stampede, hot keys, TTL jitter) as the actual production concerns that matter more than "is my map thread-safe" once you're using a real caching library.

**Source:** [Caffeine GitHub / Javadoc](https://github.com/ben-manes/caffeine), [`ConcurrentHashMap#computeIfAbsent` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html#computeIfAbsent(K,java.util.function.Function))

---

### 29. How Do You Test Concurrent Code Without Relying on Timing-Sensitive Sleeps?

**Answer:**

"`Thread.sleep()`-based tests ('sleep 100ms and hope both threads got their turn') are inherently flaky — they pass reliably on a fast, idle CI runner and fail intermittently under load, or on a slower machine, and worse, they can pass 'accidentally' without actually exercising the race condition you're trying to test at all. The core fix is to replace 'wait a fixed amount of time' with 'wait for an explicit, observable signal that the state you care about has actually been reached' — `CountDownLatch`, `CyclicBarrier`, or polling an `AtomicBoolean`/queue with `Awaitility`-style condition-based waiting (which itself polls, but with a real timeout and a real success condition, not a blind sleep).

For actually *provoking* a race rather than just avoiding flaky waits, I'd use `CyclicBarrier` to force multiple threads to hit the contended code at nearly the exact same instant — 'everyone waits at the barrier, then all release together' — which dramatically increases the odds of triggering the actual race condition under test, instead of hoping the OS scheduler happens to interleave them badly during a fixed sleep window."

**Code:**

```java
// FLAKY — the classic anti-pattern
@Test
void flakyTest() throws InterruptedException {
    AtomicInteger counter = new AtomicInteger();
    new Thread(() -> counter.incrementAndGet()).start();
    Thread.sleep(100); // just... hoping the other thread finished by now
    assertEquals(1, counter.get()); // can fail under CI load, or pass without
                                      // meaningfully testing anything concurrent
}

// BETTER — explicit signal instead of a guessed sleep duration
@Test
void deterministicTest() throws InterruptedException {
    AtomicInteger counter = new AtomicInteger();
    CountDownLatch done = new CountDownLatch(1);
    new Thread(() -> {
        counter.incrementAndGet();
        done.countDown(); // explicit "I'm actually finished" signal
    }).start();
    done.await(1, TimeUnit.SECONDS); // waits for the REAL condition, with a timeout as a safety net
    assertEquals(1, counter.get());
}

// FORCING a race with CyclicBarrier — all threads hit the contended code together
@Test
void raceConditionTest() throws InterruptedException {
    int threadCount = 50;
    AtomicInteger counter = new AtomicInteger();
    CyclicBarrier barrier = new CyclicBarrier(threadCount);
    CountDownLatch done = new CountDownLatch(threadCount);

    for (int i = 0; i < threadCount; i++) {
        new Thread(() -> {
            try {
                barrier.await(); // ALL threads release simultaneously — maximizes
                                   // the chance of actually exercising the race
                counter.incrementAndGet();
            } catch (Exception e) { throw new RuntimeException(e); }
            finally { done.countDown(); }
        }).start();
    }
    done.await(5, TimeUnit.SECONDS);
    assertEquals(threadCount, counter.get()); // catches lost updates reliably,
                                                // far more often than a sleep-based test would
}
```

**Follow-up:**

I'd bring up `jcstress` (the JCStress harness, from the same OpenJDK team behind JMH) as the actual tool used for testing subtle memory-model-level correctness issues — it runs the same test scenario millions of times across different thread/core interleavings and aggregates the actual observed outcomes, which is the only reliable way to catch genuinely rare reordering-based bugs that a handful of manual test runs would essentially never hit. For everyday application-level concurrency tests, though, I'd say `CountDownLatch`/`CyclicBarrier` plus running the test with a high iteration count (and ideally on CI with `-XX:+UnlockDiagnosticVMOptions` stress flags, or simply running many repeated iterations) is a pragmatic, sufficient standard — the goal is "makes the race condition much more likely to manifest deterministically," not "mathematically guarantees detection," which even `jcstress` doesn't claim for arbitrary application code.

**Source:** [`CyclicBarrier` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CyclicBarrier.html), [OpenJDK `jcstress` project](https://openjdk.org/projects/code-tools/jcstress/)

---

### 30. When Would You Use Atomic Classes Versus Locks?

**Answer:**

"Atomic classes (`AtomicInteger`, `AtomicLong`, `AtomicReference`, and friends) are the right tool when you have a *single* variable that needs an atomic read-modify-write operation — increment, compare-and-set, accumulate — and nothing more complex than that. They're implemented via CAS (compare-and-swap) hardware instructions rather than OS-level locking, so under low-to-moderate contention they're meaningfully cheaper than acquiring a lock: no thread ever blocks or gets descheduled, it just retries the CAS loop until it succeeds.

Locks become necessary the moment you need to keep *multiple* pieces of state consistent with each other as a unit — e.g., updating a balance and appending to a transaction log together, atomically, as one indivisible operation. There's no atomic-classes way to make 'update these two independent fields together, all-or-nothing' happen without a lock (or a single `AtomicReference` to an immutable object holding both fields together, which is itself a legitimate pattern).

The other place locks win: very high contention. Under heavy contention, a CAS-retry loop can degrade — many threads all failing and retrying repeatedly burns CPU without making progress — whereas a lock puts contending threads to sleep instead of spinning, which can actually be cheaper at extreme contention levels. `LongAdder` is Java's answer to exactly this trade-off for counters specifically: it stripes the counter across multiple internal cells to reduce CAS contention under high concurrency, at the cost of `sum()` being an approximation taken across cells rather than a single atomic read."

**Code:**

```java
// Atomic class: single-variable, no locking needed
AtomicInteger requestCount = new AtomicInteger(0);
requestCount.incrementAndGet(); // CAS-based, no thread ever blocks

// Multi-variable consistency: atomics alone can't do this correctly —
// need a lock, or bundle the fields into one immutable object behind
// a single AtomicReference:
class Account {
    private final ReentrantLock lock = new ReentrantLock();
    private BigDecimal balance;
    private List<String> transactionLog;

    void withdraw(BigDecimal amount) {
        lock.lock();
        try {
            balance = balance.subtract(amount);
            transactionLog.add("withdrew " + amount); // both fields updated
                                                          // together, atomically
        } finally { lock.unlock(); }
    }
}

// High-contention counter: LongAdder over AtomicLong
LongAdder hitCounter = new LongAdder(); // internally striped across cells
hitCounter.increment();                  // much cheaper under high contention
                                          // than AtomicLong.incrementAndGet()
long approxTotal = hitCounter.sum();     // sums across cells — a point-in-time
                                          // approximation under concurrent updates,
                                          // not a single atomic read
```

**Follow-up:**

I'd bring up `LongAdder` explicitly as the thing most engineers don't know exists, since it's the direct, purpose-built answer to "AtomicLong contention is showing up in a profiler for a hot counter" — and I'd flag the actual trade-off honestly: `LongAdder.sum()` is not linearizable the way `AtomicLong.get()` is, so it's the right tool for metrics/counters where an approximately-current total is fine, but the wrong tool if you need a strictly consistent single value (e.g., an inventory count gating a business decision). I'd also mention `VarHandle` as the modern, more flexible low-level tool (superseding a lot of what `sun.misc.Unsafe` used to be used for) for building custom lock-free structures, though I'd be honest that reaching for `VarHandle` directly is rare outside of building concurrency libraries themselves.

**Source:** [`LongAdder` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/LongAdder.html), [`AtomicInteger` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html)

---

### 31. What Is the ABA Problem?

**Answer:**

"CAS (compare-and-swap) works by checking 'is the current value still X?' and if so, swapping it to Y. The ABA problem is when a value starts at A, another thread changes it to B and then back to A again, all in between your thread's read and its CAS attempt. Your CAS sees 'still A' and succeeds — but it's not actually the *same* A in any meaningful sense; the value went on a round trip through a different state you never observed, and if your logic assumed 'unchanged since I last looked' implies 'nothing happened,' that assumption is now false.

This mostly matters for lock-free data structures built on `compareAndSet` over references — a classic example is a lock-free stack: thread 1 reads the head node (A), gets preempted; meanwhile thread 2 pops A, pops the node beneath it (B), then pushes a *new* node that happens to be allocated at the same memory address as A (this specific address-reuse scenario is more of a concern in languages with manual memory management, like C, than in Java where the GC generally prevents that exact address-reuse trap — but the logical version of ABA, where the reference is genuinely the same object again after being removed and re-added, still applies in Java too). Thread 1 resumes, its CAS succeeds because the head reference matches what it originally read, but the stack's internal structure underneath has actually changed in ways thread 1's stale read doesn't account for, corrupting the structure."

**Code:**

```java
// Illustrating the LOGICAL ABA scenario in Java (object identity, not memory-address reuse):
Integer initialValue = 100, midValue = 200; // reused explicitly — see the gotcha noted below
AtomicStampedReference<Integer> ref = new AtomicStampedReference<>(initialValue, 0);

// Thread 1 reads the value and a stamp
int[] stampHolder = new int[1];
Integer value = ref.get(stampHolder); // value=100, stamp=0
int stamp = stampHolder[0];

// Meanwhile, Thread 2 changes 100 -> 200 -> back to 100
ref.compareAndSet(initialValue, midValue, 0, 1);   // stamp now 1
ref.compareAndSet(midValue, initialValue, 1, 2);   // value is 100 again, but stamp is now 2

// Thread 1's plain compareAndSet (ignoring the stamp) would WRONGLY succeed here,
// because the VALUE alone looks unchanged, even though real state transitions happened:
boolean wronglySucceeds = ref.compareAndSet(initialValue, 999, 0, 3); // fails correctly here
// because compareAndSet checks BOTH value AND stamp — stamp mismatch (0 vs actual 2)
// is exactly what AtomicStampedReference is for: it detects the "went through A-B-A"
// history even when the final value looks unchanged.
```

**Follow-up:**

I'd cite `AtomicStampedReference` (adds a version stamp alongside the value, so CAS checks both) and `AtomicMarkableReference` (adds a boolean mark, e.g. for logical deletion) as the JDK's direct answers to this — both exist specifically because plain `AtomicReference.compareAndSet()` can't distinguish "genuinely unchanged" from "changed and changed back." I'd also be honest that this is a real concern mainly when building custom lock-free data structures (stacks, queues, linked structures) — it rarely bites application-level code directly, since most application code uses `ConcurrentHashMap`/`java.util.concurrent` collections that have already handled this correctly internally, but it's a good signal in an interview that you understand *why* those collections are non-trivial to implement correctly. I'd also flag a genuinely easy-to-miss gotcha with `AtomicReference`/`AtomicStampedReference` over a boxed type like `Integer`: `compareAndSet()`'s expected-value check is reference equality (`==`), not `.equals()` — reusing the same `Integer` variable at every call site (as above) is deliberate, since re-autoboxing the literal `200` a second time would create a genuinely different `Integer` object for any value outside the JVM's cached range of `-128` to `127`, and the CAS would then silently fail even though the boxed values are numerically equal.

**Source:** [`AtomicStampedReference` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicStampedReference.html)

---

### 32. How Would You Propagate Logging, Tracing, Security, and Transaction Context Through Asynchronous Work?

**Answer:**

"By default, none of this context comes along for free once you hop threads — `MDC` (logging context, like a request/correlation ID), `SecurityContextHolder` (the authenticated principal), tracing spans, and Spring's transaction context are all typically stored in `ThreadLocal`s, and a `ThreadLocal` is, by definition, local to the thread that set it. The instant you submit work to an executor, publish an async event, or hand off to a virtual thread running on a different carrier, whatever thread actually executes that work has an empty `ThreadLocal` unless you explicitly copy the context across.

The general pattern is: capture the relevant context values on the calling thread *before* handing off, then explicitly restore them on the executing thread at the start of the task, and clean them up afterward (in a `finally`) so they don't leak into whatever unrelated task that thread picks up next — which matters especially in a pooled-thread environment, tying directly back to the `ThreadLocal` leak pattern from the collections file. Modern frameworks give you hooks for this instead of hand-wiring it everywhere: Spring's `TaskDecorator` for `@Async`/executors, Micrometer's/OpenTelemetry's context propagation for tracing, and MDC has its own well-known 'copy in, clear in finally' idiom."

**Code:**

```java
// Spring TaskDecorator — the framework-supported way to propagate context
// across an executor boundary without manually wiring it into every call site
public class ContextCopyingTaskDecorator implements TaskDecorator {
    @Override
    public Runnable decorate(Runnable runnable) {
        Map<String, String> contextMap = MDC.getCopyOfContextMap();
        SecurityContext securityContext = SecurityContextHolder.getContext();

        return () -> {
            try {
                if (contextMap != null) MDC.setContextMap(contextMap);
                SecurityContextHolder.setContext(securityContext);
                runnable.run();
            } finally {
                MDC.clear(); // ALWAYS clean up — this thread will be reused
                             // for an unrelated task next, in a pooled executor
                SecurityContextHolder.clearContext();
            }
        };
    }
}

@Configuration
class AsyncConfig {
    @Bean
    Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setTaskDecorator(new ContextCopyingTaskDecorator());
        executor.initialize();
        return executor;
    }
}
```

**Follow-up:**

I'd bring up `ScopedValue` (finalized alongside virtual threads, JEP 506 as of recent JDKs) as the newer, structurally-safer alternative to `ThreadLocal` for this exact propagation problem — it's immutable for the duration of a well-defined dynamic scope, automatically propagates to child threads/tasks spawned within that scope via structured concurrency, and can't leak past the scope the way a forgotten `ThreadLocal.remove()` can. I'd also flag transaction context specifically as the trickiest of the four to propagate correctly: a database transaction (via Spring's `TransactionSynchronizationManager`, itself `ThreadLocal`-backed) generally should **not** be propagated across an async boundary at all — the whole point of `REQUIRES_NEW`/async offload is usually to get work *off* the thread holding the transaction, and blindly propagating the transaction context to another thread risks the exact "transaction spans a network call" danger from question 19, just moved one level up.

**Source:** [Spring `TaskDecorator` Javadoc](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/core/task/TaskDecorator.html), [JEP 506, Scoped Values](https://openjdk.org/jeps/506)

---

### 33. How Do Structured Concurrency Concepts Improve Cancellation and Error Handling?

**Answer:**

"Without structured concurrency, spawning concurrent subtasks — via a raw executor, `CompletableFuture.allOf()`, or fire-and-forget threads — doesn't give you a clean, single owning scope for their lifetimes. If one subtask fails, the others don't automatically get cancelled; they just keep running, wasting work on a result that's already going to be discarded because the overall operation failed. And if the *parent* is cancelled or times out, there's no automatic mechanism propagating that cancellation down to the child tasks either — they keep running as orphans, potentially past the point their result even matters, holding onto resources (connections, threads) for no reason.

Structured concurrency (`StructuredTaskScope`, a preview API built on virtual threads) fixes this by giving concurrent subtasks a well-defined parent scope with a lexical lifetime — a subtask can't outlive the block that spawned it. Within that scope, a `Joiner` policy (e.g. 'all subtasks must succeed, or fail the whole scope') automatically cancels the sibling subtasks the moment one fails, rather than letting them run to completion pointlessly, and the scope only 'joins' (returns to the caller) once every child is genuinely done, one way or another — so there's no possibility of a subtask outliving the operation that spawned it, unlike a fire-and-forget thread or unmanaged executor submission."

**Code:**

```java
// Without structured concurrency: a failure in one task doesn't cancel the other,
// and error handling is manual, easy to get wrong
CompletableFuture<User> userFuture = CompletableFuture.supplyAsync(() -> fetchUser(id));
CompletableFuture<Order> orderFuture = CompletableFuture.supplyAsync(() -> fetchOrder(id));
// if fetchOrder throws, fetchUser's call keeps running to completion regardless —
// wasted work, and you have to manually wire up cancellation if you want it
CompletableFuture.allOf(userFuture, orderFuture).join();

// With structured concurrency — this targets JEP 505 (5th preview, JDK 25):
// StructuredTaskScope.open(...) + a Joiner, NOT the older ShutdownOnFailure()
// constructor-based API from earlier previews (JEP 453 through JEP 499),
// which JEP 505 removed. The exact factory-method/exception names below are still
// a PREVIEW API and have continued to change in later previews (JEP 525,
// JEP 533) — check the Joiner Javadoc for whatever JDK you're actually on.
try (var scope = StructuredTaskScope.open(Joiner.<Object>allSuccessfulOrThrow())) {
    Subtask<User> userTask = scope.fork(() -> fetchUser(id));
    Subtask<Order> orderTask = scope.fork(() -> fetchOrder(id));

    scope.join(); // waits for both, or returns as soon as one fails and
                   // cancels the other — throws StructuredTaskScope.FailedException
                   // (wrapping the subtask's exception) if any subtask failed

    // if orderTask had failed, userTask would have been cancelled automatically
    // by the scope the moment the failure was detected — no manual wiring
    User user = userTask.get();
    Order order = orderTask.get();
} // scope guarantees no subtask survives past this block, structurally
```

**Failure modes and trade-offs:** `StructuredTaskScope.FailedException` is what `join()` throws under JEP 505/525; JEP 533 (7th preview, targeted at JDK 27) changes that to `ExecutionException` instead — so pin the exact JDK version before writing production code against this, and expect to update the catch clause across JDK previews until the API stabilizes as a permanent (non-preview) feature.

**Follow-up:**

I'd frame the core idea as bringing the same discipline single-threaded code already has for free — a method's call stack has a clean, lexical shape where a child call can't outlive its caller, and an exception naturally propagates up and unwinds everything below it — into the concurrent world, where none of that was previously guaranteed by default. I'd also note this is explicitly still a preview API — it's gone through multiple JEPs (428 → 437 incubating in JDK 19–20, then previewing as 453 → 462 → 480 → 499 → 505 → 525 → 533 from JDK 21 through the JDK 27 preview cycle), with real API-shape changes along the way (the constructor-based `ShutdownOnFailure`/`ShutdownOnSuccess` classes from earlier previews were removed in JEP 505 in favor of `StructuredTaskScope.open(Joiner)`), so I'd flag that in a real system today, achieving similar discipline manually (an explicit 'scope' object that tracks and cancels its own children, propagating cancellation via `Future.cancel()`/interruption) is still the common fallback until the API stabilizes — but the underlying principle (bound the lifetime of concurrent work to an explicit parent scope, propagate failure and cancellation automatically within it) is the actual staff-level insight the interviewer is looking for, independent of which specific preview API version ships it.

**Source:** [JEP 505, Structured Concurrency (fifth preview)](https://openjdk.org/jeps/505), [`StructuredTaskScope.Joiner` Javadoc, JDK 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/StructuredTaskScope.Joiner.html), [JEP 525, Structured Concurrency (sixth preview)](https://openjdk.org/jeps/525), [JEP 533, Structured Concurrency (seventh preview)](https://openjdk.org/jeps/533)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| JLS §17.4 — Memory Model | https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4 |
| JLS §17.4.5 — Happens-before Order (volatile rule) | https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4.5 |
| JLS §17.5 — Final Field Semantics | https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.5 |
| JLS §12.4 — Initialization of Classes | https://docs.oracle.com/javase/specs/jls/se21/html/jls-12.html#jls-12.4 |
| `ReentrantLock` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html |
| `StampedLock` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/StampedLock.html |
| `jstack` documentation | https://docs.oracle.com/en/java/javase/21/docs/specs/man/jstack.html |
| `jcmd` documentation | https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html |
| JEP 444 — Virtual Threads | https://openjdk.org/jeps/444 |
| `CompletableFuture` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CompletableFuture.html |
| `ThreadPoolExecutor` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html |
| `ForkJoinPool` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ForkJoinPool.html |
| `ForkJoinPool.ManagedBlocker` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ForkJoinPool.ManagedBlocker.html |
| `RecursiveTask` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/RecursiveTask.html |
| `LongAdder` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/LongAdder.html |
| `AtomicInteger` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html |
| `AtomicStampedReference` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicStampedReference.html |
| OpenJDK `jcstress` project | https://openjdk.org/projects/code-tools/jcstress/ |
| `CyclicBarrier` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CyclicBarrier.html |
| Spring `TaskDecorator` Javadoc | https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/core/task/TaskDecorator.html |
| JEP 506 — Scoped Values | https://openjdk.org/jeps/506 |
| JEP 505 — Structured Concurrency (5th preview) | https://openjdk.org/jeps/505 |
| `StructuredTaskScope.Joiner` Javadoc, JDK 25 | https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/StructuredTaskScope.Joiner.html |
| JEP 525 — Structured Concurrency (6th preview) | https://openjdk.org/jeps/525 |
| JEP 533 — Structured Concurrency (7th preview) | https://openjdk.org/jeps/533 |
| Caffeine cache library | https://github.com/ben-manes/caffeine |
| *Java Concurrency in Practice* (Goetz et al.) | ISBN 978-0321349606 |
