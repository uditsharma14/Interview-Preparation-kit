# Computer Science Glossary — Quick Reference

> **Purpose:** a fast, scannable glossary of 222 core CS/software-engineering/ML terms — 2–3 lines each, not full interview answers. **Last verified:** 2026-08-27.

How to use this: this is deliberately a **glossary, not a guide** — no code, no Follow-up, no per-term citation, just a quick, accurate definition to jog your memory or fill a gap before an interview. Where a term already has real interview-depth treatment elsewhere in InterviewSmith, the entry ends with a *See:* pointer — follow it for the version-scoped, staff-level version of the same topic. Terms are grouped by theme in roughly the order a CS curriculum introduces them, not alphabetically, since related terms are easier to hold in your head together.

<!-- toc -->
## Table of Contents

- [Computing Basics](#computing-basics)
- [Programming Fundamentals](#programming-fundamentals)
- [Algorithms Basics](#algorithms-basics)
- [Data Structures](#data-structures)
- [Object-Oriented Programming](#object-oriented-programming)
- [Concurrency & Memory](#concurrency--memory)
- [Databases](#databases)
- [Networking](#networking)
- [Operating Systems](#operating-systems)
- [Software Architecture & Engineering Practice](#software-architecture--engineering-practice)
- [Security](#security)
- [Distributed Systems & Infrastructure](#distributed-systems--infrastructure)
- [Machine Learning Fundamentals](#machine-learning-fundamentals)

<!-- /toc -->

---

## Computing Basics

**Computer** — A programmable machine that accepts input, processes it according to stored instructions, and produces output. Every device in this glossary — a laptop, a phone, a server — is a computer in this sense.

**Hardware** — The physical components of a computer: CPU, RAM, storage, input/output devices, and the circuitry connecting them. Anything you could physically touch or unplug.

**Software** — The instructions (programs) that tell hardware what to do. Divided broadly into system software (the operating system) and application software (everything running on top of it).

**Operating system** — The software layer that manages hardware resources (CPU, memory, storage, devices) and provides a consistent interface for applications to use them, without each application needing to control hardware directly. *See: [Computer Science Fundamentals Q22](Computer_Science_Fundamentals_Interview_Prep.md#22-what-is-an-operating-system-and-what-does-the-kernel-do).*

**CPU** (Central Processing Unit) — The hardware component that executes instructions: fetching, decoding, and running them. Real cores don't strictly run "one at a time" either — pipelining and superscalar/out-of-order execution let a single core have several instructions in flight per cycle, and most CPUs have multiple independent cores besides.

**RAM** (Random Access Memory) — Fast, volatile (cleared on power loss) memory holding data and instructions a running program is actively using. "Volatile" is the key word — unlike storage, nothing in RAM survives a restart.

**Storage** — Persistent memory (an SSD, a hard drive) that retains data across power cycles, unlike RAM. Much slower to access than RAM, which is exactly why RAM exists as a separate, faster tier.

**Input device** — Hardware that feeds data or commands into a computer — a keyboard, mouse, microphone, or network interface receiving data from elsewhere.

**Output device** — Hardware that presents a computer's results to the outside world — a monitor, speaker, or a network interface sending data out.

---

## Programming Fundamentals

**Program** — A set of instructions written to accomplish a specific task, which a computer executes. "Program" and "software" are near-synonyms; "program" more often refers to one specific executable.

**Programming language** — A formal language with defined syntax and semantics for writing instructions a computer (via a compiler or interpreter) can carry out. Java, Python, and SQL are all programming languages, despite being used very differently.

**Source code** — The human-readable text of a program, written in a programming language, before any translation into a form the computer can execute directly.

**Machine code** — The lowest-level form of instructions, expressed in binary, that a CPU can execute directly with no further translation. Source code eventually becomes machine code — sometimes ahead of time, sometimes at runtime.

**Syntax** — The set of rules defining what counts as a structurally valid statement in a given language — the "grammar." Code that violates syntax rules fails to even parse, let alone run.

**Compiler** — A program that translates source code into a lower-level form *ahead of time*, before the program runs. That output isn't always a standalone, independently-runnable executable — `javac` compiles Java to bytecode, which still needs the JVM to run it. *See: [Computer Science Fundamentals Q20](Computer_Science_Fundamentals_Interview_Prep.md#20-whats-the-difference-between-a-compiled-and-an-interpreted-language).*

**Interpreter** — A program that translates and executes code *at runtime* rather than producing a standalone executable ahead of time. This is rarely literal line-by-line translation of source text — CPython, for instance, compiles source to bytecode first, then interprets that. *See: [Computer Science Fundamentals Q20](Computer_Science_Fundamentals_Interview_Prep.md#20-whats-the-difference-between-a-compiled-and-an-interpreted-language).*

**Runtime** — Broadly, "while the program is actually executing" (as opposed to compile time). Also refers specifically to the environment/support system (like the JVM) a program needs present in order to run.

**Variable** — A named storage location holding a value. Despite the name, not every "variable" is actually mutable — many languages let you declare one that can only be assigned once (Java `final`, Kotlin `val`), blurring the line with a constant.

**Constant** — A named value that, once set, cannot be reassigned. Enforcement varies by language: some catch a reassignment at compile time (Java `final`, C `const`), others only at runtime (JavaScript `const`), and some (classic Python) don't enforce it at all — it's just a naming convention.

**Data type** — A classification defining what kind of value a variable can hold and what operations are valid on it — `int`, `String`, `boolean`, and so on. Determines both the value's representation in memory and what the language allows you to do with it.

**Operator** — A symbol representing an operation to perform on one or more values (operands) — `+`, `-`, `==`, `&&`, and so on.

**Expression** — A piece of code that evaluates to a value — `2 + 2`, `user.getName()`, `a && b`. Every expression produces a result; not every statement does.

**Statement** — A complete, executable instruction — an assignment, a loop, a function call used for its side effect. A statement performs an action; it doesn't necessarily produce a usable value the way an expression does.

**Function** — A named, reusable block of code that performs a task, optionally taking inputs and optionally producing an output. "Method" (below) is the OOP-specific term for one attached to a class; the two are used almost interchangeably in most languages, including Java.

**Method** — A function defined as part of a class, operating on (or associated with) instances of that class. Most languages call any class member function a "method" regardless of return type, though some formal traditions reserve "function" for one that returns a value and "procedure" for one that doesn't (a `void` method).

**Parameter** — A named placeholder in a function's definition representing a value the caller will supply — `void greet(String name)`, where `name` is the parameter.

**Argument** — The actual value passed into a function at the point it's called — `greet("Alice")`, where `"Alice"` is the argument. Parameters are defined; arguments are supplied.

**Return value** — The value a function produces and hands back to its caller when it finishes. A function with no meaningful result to hand back is typically declared `void` (Java) or equivalent.

**Scope** — The region of code where a given variable is visible and accessible. A variable declared inside a function is typically only visible within that function ("local scope"), not outside it.

**Conditional statement** — A statement that executes different code depending on whether a condition is true or false — `if`/`else`, `switch`. The mechanism for branching logic.

**Loop** — A control structure that repeats a block of code multiple times, either a fixed number of times (`for`) or until a condition changes (`while`).

**Recursion** — A function solving a problem by calling itself on a smaller version of the same problem, until it reaches a base case simple enough to answer directly. *See: [Computer Science Fundamentals Q18](Computer_Science_Fundamentals_Interview_Prep.md#18-what-is-recursion-and-what-is-a-base-case).*

**Exception** — A signal that an error or unexpected condition occurred during execution, which interrupts normal control flow unless explicitly caught and handled by surrounding code.

**Debugging** — The process of finding and fixing the cause of a bug — reproducing the failure, inspecting program state (via breakpoints, logging, or a debugger), and narrowing down where behavior diverges from what's expected.

---

## Algorithms Basics

**Algorithm** — A precise, finite sequence of steps for solving a specific problem or accomplishing a specific task, independent of any particular programming language.

**Pseudocode** — An informal, language-agnostic way of describing an algorithm's logic using plain structured language, without worrying about a real language's exact syntax — useful for communicating an approach before (or instead of) writing real code.

**Flowchart** — A diagram representing an algorithm or process as a sequence of connected boxes and decision points, showing the flow of control visually rather than as text.

**Time complexity** — A measure of how an algorithm's *running time* grows as its input size grows, typically expressed in Big O notation. Describes a trend, not an exact measured duration.

**Space complexity** — A measure of how an algorithm's *memory usage* grows as its input size grows, expressed the same way as time complexity (Big O). An algorithm can be fast but memory-hungry, or slow but memory-frugal — the two are independent trade-offs.

**Big O notation** — Notation describing the upper-bound growth rate of an algorithm's resource usage (time or space) as input size increases — `O(1)`, `O(n)`, `O(log n)`, `O(n²)`. *See: [Computer Science Fundamentals Q13](Computer_Science_Fundamentals_Interview_Prep.md#13-what-is-big-o-notation-and-why-does-it-matter).*

---

## Data Structures

**Array** — A fixed-size, contiguous block of memory holding elements of the same type, accessed by index in O(1) time. The most basic data structure; most others are built using one internally.

**List** — In the general CS sense, an ordered collection of elements, typically of variable length (unlike a fixed-size array). In Java specifically, `List` is an interface with several implementations (`ArrayList`, `LinkedList`).

**Linked list** — A sequence of nodes where each node holds a value and a reference (pointer) to the next node, rather than being stored contiguously in memory like an array. Insertion/removal at a known position is O(1); indexed access is O(n).

**Stack** — A LIFO (Last In, First Out) data structure — the most recently added element is always the first one removed. *See: [Computer Science Fundamentals Q16](Computer_Science_Fundamentals_Interview_Prep.md#16-what-is-a-stack-and-what-is-a-queue).*

**Queue** — A FIFO (First In, First Out) data structure — the first element added is the first one removed. *See: [Computer Science Fundamentals Q16](Computer_Science_Fundamentals_Interview_Prep.md#16-what-is-a-stack-and-what-is-a-queue).*

**Deque** ("double-ended queue") — A data structure supporting insertion and removal at *both* ends, generalizing both a stack and a queue into one structure.

**Set** — A collection that enforces no duplicate elements, typically with no guaranteed ordering (though ordered/sorted variants exist). Membership testing is the core operation a set is optimized for.

**Map/Dictionary** — A collection of key-value pairs, where each key maps to exactly one value and lookup by key is the primary operation — typically O(1) average for a hash-based implementation.

**Hash table** — The underlying data structure behind most `Map`/`Set` implementations: an array of "buckets," with a hash function mapping each key to a bucket index, giving average O(1) insert/lookup/delete.

**Tree** — A hierarchical data structure with one root node, where every other node has exactly one parent, and there are no cycles. *See: [Computer Science Fundamentals Q17](Computer_Science_Fundamentals_Interview_Prep.md#17-whats-the-difference-between-a-tree-and-a-graph).*

**Binary tree** — A tree where every node has at most two children, conventionally referred to as the left and right child.

**Binary search tree** — A binary tree with an ordering invariant: every node's left subtree contains only smaller values, and its right subtree only larger values — enabling O(log n) search, insert, and delete when the tree is reasonably balanced.

**Heap** — A tree-shaped data structure (usually stored as an array) maintaining the heap property: every parent is less-than-or-equal-to (min-heap) or greater-than-or-equal-to (max-heap) its children, keeping the smallest/largest element instantly accessible at the root.

**Graph** — A data structure of nodes connected by edges, with no restriction on connection pattern — cycles allowed, no single required root, many-to-many relationships expressible. *See: [Computer Science Fundamentals Q17](Computer_Science_Fundamentals_Interview_Prep.md#17-whats-the-difference-between-a-tree-and-a-graph).*

**Node/Vertex** — A single point/element in a tree or graph — "node" is the more common term in tree contexts, "vertex" in graph-theory contexts, but they mean the same thing.

**Edge** — A connection between two nodes/vertices in a graph or tree, optionally carrying a direction (a directed edge) or a weight (a weighted edge).

**Searching** — The process of locating a specific element (or determining it's absent) within a data structure — linear search (O(n)) checks every element; binary search (O(log n)) requires sorted data and repeatedly halves the search space.

**Sorting** — The process of arranging elements into a defined order (ascending/descending, by some comparator) — common algorithms include merge sort and quicksort (both O(n log n) average), and insertion sort (O(n²), but fast for small/nearly-sorted input).

**Traversal** — The process of visiting every node in a tree or graph systematically — depth-first (via a stack, or recursion's own call stack) or breadth-first (via a queue) are the two standard strategies.

---

## Object-Oriented Programming

**Class** — A blueprint/template defining the fields (state) and methods (behavior) that instances (objects) of that type will have. The class itself isn't an object; it's the definition objects are created from.

**Object** — A specific instance of a class, with its own actual field values, created via that class's constructor.

**Constructor** — A special class member invoked when an object is created, responsible for initializing its fields to a valid starting state. In Java specifically, a constructor is formally *not* a method — it has no return type and, per the JLS, is not a class member and is therefore not inherited ([JLS §8.2](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.2)).

**Encapsulation** — Bundling an object's data together with the methods that operate on it, and restricting direct external access to that data, so the object controls how its own state can be read or changed. *See: [Computer Science Fundamentals Q19](Computer_Science_Fundamentals_Interview_Prep.md#19-what-are-the-four-pillars-of-object-oriented-programming).*

**Abstraction** — Exposing only the essential, relevant details of an object's behavior through a simplified interface, while hiding the complex implementation behind it. *See: [Computer Science Fundamentals Q19](Computer_Science_Fundamentals_Interview_Prep.md#19-what-are-the-four-pillars-of-object-oriented-programming).*

**Inheritance** — A class deriving from (extending) another class, automatically gaining its parent's fields and methods while adding or overriding its own. *See: [Computer Science Fundamentals Q19](Computer_Science_Fundamentals_Interview_Prep.md#19-what-are-the-four-pillars-of-object-oriented-programming).*

**Polymorphism** — Objects of different classes being usable through a common interface/supertype, where the specific behavior that runs is determined by the object's actual runtime type, not its declared type. *See: [Computer Science Fundamentals Q19](Computer_Science_Fundamentals_Interview_Prep.md#19-what-are-the-four-pillars-of-object-oriented-programming).*

**Interface** — A contract defining a set of methods a class must implement, with no implementation of its own (or, in modern Java, optionally some default implementation) — lets unrelated classes be used interchangeably as long as they honor the same contract.

**Composition** — Building a class by including instances of other classes as fields ("has-a" relationships), rather than extending them ("is-a," via inheritance) — often the more flexible, less tightly-coupled design choice.

**Immutable object** — An object whose own fields are set once, in the constructor, and never reassigned. That guarantees thread safety only if every referenced field is *also* immutable (or defensively copied) — a `final` field pointing to a mutable `List`, for instance, can still have its contents change out from under you.

---

## Concurrency & Memory

**Process** — An independent, OS-managed unit of execution with its own isolated memory address space. A running program is a process; one program can have multiple processes.

**Thread** — A unit of execution within a process, sharing that process's memory with every other thread in it, but with its own call stack and program counter. *See: [Java Concurrency Interview Prep Q1](../Language/Java_Concurrency_Interview_Prep.md#1-what-is-a-thread-and-how-does-it-differ-from-a-process).*

**Concurrency** — Multiple tasks making progress over overlapping time periods — not necessarily executing at the exact same instant, just interleaved in a way that allows them to logically overlap.

**Parallelism** — Multiple tasks executing *literally simultaneously*, on genuinely separate CPU cores. Parallelism is a specific way to achieve concurrency, but concurrency doesn't require true parallelism (a single core can interleave tasks concurrently without ever running two at once).

**Synchronization** — Coordinating access to shared, mutable state across multiple threads so they don't corrupt it by acting on it simultaneously — via locks, atomic operations, or other coordination primitives.

**Race condition** — A bug where the correctness of a program depends on the relative timing/interleaving of multiple threads accessing shared, mutable state. *See: [Java Concurrency Interview Prep Q4](../Language/Java_Concurrency_Interview_Prep.md#4-what-is-a-race-condition).*

**Deadlock** — Two or more threads each holding a lock the other needs, with neither willing to give up what it holds — so both wait forever. *See: [Java Concurrency Interview Prep Q6](../Language/Java_Concurrency_Interview_Prep.md#6-what-is-a-deadlock-in-the-simplest-terms).*

**Thread safety** — A property of code that behaves correctly when accessed by multiple threads concurrently, with no data corruption or inconsistent state, regardless of how those threads happen to interleave.

**Stack memory** — Per-thread memory holding method call frames, each with that method's local variables — popped automatically the instant its method returns. *See: [Java JVM & GC Interview Prep Q2](../Language/Java_JVM_GC_Interview_Prep.md#2-whats-the-difference-between-stack-memory-and-heap-memory).*

**Heap memory** — Memory shared across all threads in a process, where objects created with `new` conventionally live, reclaimed once nothing references them anymore (garbage collection). Not an absolute rule at runtime, though: a JIT compiler can use escape analysis to prove an object never leaves its creating method and skip the heap allocation entirely. *See: [Java JVM & GC Interview Prep Q2](../Language/Java_JVM_GC_Interview_Prep.md#2-whats-the-difference-between-stack-memory-and-heap-memory) and [Q16 — Escape Analysis](../Language/Java_JVM_GC_Interview_Prep.md#16-what-are-escape-analysis-scalar-replacement-and-lock-elimination).*

**Garbage collection** — The automatic process of reclaiming heap memory occupied by objects no longer reachable from any live reference, so the application never has to explicitly free memory itself. *See: [Java JVM & GC Interview Prep Q3](../Language/Java_JVM_GC_Interview_Prep.md#3-what-is-garbage-collection-and-why-does-java-need-it).*

**Memory leak** — In a garbage-collected language, an object that's still *reachable* (via some live reference chain) even though the application no longer logically needs it — the GC can't reclaim it, since reachability is all it checks. *See: [Java JVM & GC Interview Prep Q10](../Language/Java_JVM_GC_Interview_Prep.md#10-what-is-a-memory-leak-in-java-given-that-it-has-garbage-collection).*

---

## Databases

**Database** — An organized collection of structured data, typically stored persistently and designed to be efficiently queried, inserted into, and updated.

**DBMS** (Database Management System) — Software that manages a database — handling storage, retrieval, concurrent access, and enforcing structure/constraints — PostgreSQL and MySQL are relational DBMSs; MongoDB is a document-store DBMS.

**Table** — In a relational database, a structured collection of rows sharing the same set of columns — the fundamental unit of storage in the relational model.

**Row** — A single record in a table — one entity's worth of data, with a value for each of the table's columns.

**Column** — A single named attribute/field shared by every row in a table, with a defined data type.

**Primary key** — The column (or combination of columns) uniquely identifying each row in a table — no two rows can share the same primary key value.

**Foreign key** — A column in one table that references another table's row, expressing a relationship and letting the database enforce referential integrity. The referenced column doesn't have to be that table's primary key specifically — any column (or set of columns) with a `UNIQUE` constraint qualifies ([PostgreSQL — Foreign Keys](https://www.postgresql.org/docs/current/ddl-constraints.html)).

**SQL** (Structured Query Language) — The standard language for querying and manipulating data in a relational database — `SELECT`, `INSERT`, `UPDATE`, `DELETE`, and schema-definition statements.

**Query** — A request for data (or a data-modifying operation) sent to a database, typically written in SQL for a relational database.

**Index** — An auxiliary data structure (typically a B-tree) built on one or more columns that lets the database find matching rows without scanning the whole table. *See: [Computer Science Fundamentals Q26](Computer_Science_Fundamentals_Interview_Prep.md#26-what-is-a-database-index-and-why-does-it-speed-up-queries).*

**Join** — A SQL operation combining rows from two or more tables based on a related column between them, reassembling data that's been normalized across multiple tables back into one result set.

**Transaction** — A sequence of database operations treated as a single atomic unit — either every operation in it succeeds and is committed, or none of them take effect at all. *See: [Transactions Interview Prep](../System%20Design/Transactions_Interview_Prep.md).*

**Commit** — Finalizing a transaction, making all its changes permanent. *When* other transactions can see those changes depends on their own isolation level — a transaction already mid-flight under snapshot/repeatable-read isolation may not see a commit that happened after its own snapshot was taken. *See: [Transactions Interview Prep — isolation levels](../System%20Design/Transactions_Interview_Prep.md#2-what-anomalies-are-possible-at-each-isolation-level).*

**Rollback** — Undoing a transaction's changes, restoring the database to an earlier state — typically triggered by an error. That earlier state isn't always "before the transaction began": rolling back to a **savepoint** undoes only the work since that point, leaving the rest of the transaction intact. *See: [Transactions Interview Prep — NESTED propagation](../System%20Design/Transactions_Interview_Prep.md#6-explain-required-requiresnew-nested-and-notsupported).*

**ACID** — The four guarantees a transactional database provides: **A**tomicity (all-or-nothing), **C**onsistency (valid state to valid state), **I**solation (concurrent transactions don't interfere), **D**urability (committed data survives a crash). *See: [Transactions Interview Prep](../System%20Design/Transactions_Interview_Prep.md).*

**Schema** — The structural definition of a database — what tables exist, their columns, data types, and constraints. Defines the *shape* data must conform to, not the data itself.

**Normalization** — Organizing a database's tables and columns to reduce data redundancy and avoid update/insert/delete anomalies, expressed as a series of increasingly strict rules (1NF, 2NF, 3NF, ...). *See: [Computer Science Fundamentals Q25](Computer_Science_Fundamentals_Interview_Prep.md#25-what-is-database-normalization-and-what-do-1nf-2nf-and-3nf-mean).*

**NoSQL** — An umbrella term for non-relational databases (document stores, key-value stores, wide-column stores, graph databases) that trade some combination of schema enforcement, native joins, or strict ACID guarantees for flexibility or easier horizontal scaling. *See: [Computer Science Fundamentals Q14](Computer_Science_Fundamentals_Interview_Prep.md#14-whats-the-difference-between-sql-and-nosql-databases).*

---

## Networking

**Network** — A collection of interconnected computers/devices that can exchange data with each other.

**Client** — A program or device that initiates a request to a server, consuming a service the server provides — a web browser, a mobile app, another backend service.

**Server** — A program or device that listens for and responds to requests from clients, providing some service (serving web pages, running queries, returning API data).

**IP address** — A numeric identifier assigned to a device on a network, used to route traffic to it — IPv4 (`93.184.216.34`) or the larger IPv6 address space.

**Domain name** — A human-readable name (`example.com`) standing in for a numeric IP address, resolved to that address via DNS.

**DNS** (Domain Name System) — The distributed, hierarchical directory that translates domain names into IP addresses. *See: [Computer Science Fundamentals Q2](Computer_Science_Fundamentals_Interview_Prep.md#2-what-is-dns-and-how-does-a-domain-name-resolve-to-an-ip-address).*

**Port** — A number identifying a specific application/process on a machine, distinguishing between multiple services reachable at the same IP address. *See: [Computer Science Fundamentals Q3](Computer_Science_Fundamentals_Interview_Prep.md#3-whats-the-difference-between-an-ip-address-and-a-port-number).*

**Protocol** — An agreed-upon set of rules governing how two systems communicate — HTTP, TCP, DNS are all protocols, each defining the exact format and sequence of messages exchanged.

**HTTP** — The application-layer protocol underlying the web and virtually every REST API: a client sends a request, a server sends a response. *See: [Computer Science Fundamentals Q5](Computer_Science_Fundamentals_Interview_Prep.md#5-what-is-http-and-what-does-it-mean-that-its-stateless).*

**HTTPS** — HTTP running over a TLS-encrypted connection, protecting the request/response contents from being read or tampered with in transit. *See: [Computer Science Fundamentals Q11](Computer_Science_Fundamentals_Interview_Prep.md#11-what-is-tls-and-how-does-the-handshake-establish-a-secure-connection).*

**TCP** — A connection-oriented, reliable transport-layer protocol: whatever data arrives is complete, in order, and without duplication, at the cost of handshake and retransmission overhead. That's conditional on the connection succeeding, though — TCP doesn't retry forever; it eventually reports a failure rather than guaranteeing delivery no matter what. *See: [Computer Science Fundamentals Q1](Computer_Science_Fundamentals_Interview_Prep.md#1-whats-the-difference-between-tcp-and-udp).*

**UDP** — A connectionless transport-layer protocol with no delivery, ordering, or retransmission guarantees — lower overhead, used where a late/lost packet is worthless anyway (real-time video, DNS queries). *See: [Computer Science Fundamentals Q1](Computer_Science_Fundamentals_Interview_Prep.md#1-whats-the-difference-between-tcp-and-udp).*

**URL** — A URI that both identifies a resource *and* tells you how to reach it (scheme, host, path). *See: [Computer Science Fundamentals Q4](Computer_Science_Fundamentals_Interview_Prep.md#4-whats-the-difference-between-a-uri-a-url-and-a-urn).*

**Request** — A message a client sends to a server asking it to do something — fetch data, create a resource, perform an action.

**Response** — A message a server sends back to a client after processing a request, including a status and typically a body.

**API** — Any defined contract letting one piece of software interact with another — broader than just network-accessible ("web service"), though used loosely to mean the latter in everyday conversation. *See: [Computer Science Fundamentals Q15](Computer_Science_Fundamentals_Interview_Prep.md#15-what-is-an-api-and-how-does-it-differ-from-a-web-service).*

**REST** (Representational State Transfer) — An architectural style for web APIs built around resources identified by URLs, manipulated via standard HTTP methods. *See: [REST API Design Interview Prep](../System%20Design/REST_API_Design_Interview_Prep.md).*

**JSON** (JavaScript Object Notation) — A lightweight, human-readable, text-based data-interchange format built on key-value pairs and arrays — the dominant format for modern API request/response bodies.

**Latency** — The time delay between sending a request and receiving the first byte of a response (or between an action and its effect being observed) — a measure of *responsiveness*, distinct from throughput.

**Bandwidth** — The maximum rate at which data can be transferred over a network connection — a measure of *capacity*, distinct from latency (a high-bandwidth, high-latency connection can move a lot of data slowly to first respond, but a lot of it once it starts).

**Timeout** — A configured maximum duration to wait for an operation (a network request, a lock acquisition) to complete before giving up and treating it as failed, rather than waiting indefinitely.

---

## Operating Systems

**Kernel** — The OS's privileged core, with direct hardware access, responsible for process scheduling, memory management, and mediating every application's access to hardware. *See: [Computer Science Fundamentals Q22](Computer_Science_Fundamentals_Interview_Prep.md#22-what-is-an-operating-system-and-what-does-the-kernel-do).*

**File system** — The OS component (and on-disk structure) organizing how files and directories are stored, named, and retrieved on persistent storage.

**Scheduler** — The kernel component deciding which process/thread gets the CPU next, and for how long, when there are more runnable tasks than CPU cores to run them on.

**Context switch** — The kernel saving one process/thread's execution state and loading another's, so the CPU can switch which task it's running — necessary overhead every time the scheduler changes which task has the CPU.

**System call** — A controlled request from a user-space application into the kernel, asking it to perform a privileged operation (reading a file, allocating memory, sending network data) the application can't do directly itself. *See: [Computer Science Fundamentals Q22](Computer_Science_Fundamentals_Interview_Prep.md#22-what-is-an-operating-system-and-what-does-the-kernel-do).*

**Virtual memory** — An OS abstraction giving every process its own large, private, isolated address space, transparently mapped to physical RAM (and, when needed, disk) underneath. *See: [Computer Science Fundamentals Q23](Computer_Science_Fundamentals_Interview_Prep.md#23-what-is-virtual-memory-and-what-is-paging).*

**Command line** — A text-based interface for interacting with a computer by typing commands, rather than clicking through a graphical interface.

**Shell** — The program that interprets and executes commands typed at a command line (Bash, Zsh, PowerShell) — the layer between a user typing a command and the OS actually carrying it out.

---

## Software Architecture & Engineering Practice

**Framework** — A reusable, opinionated foundation for building an application, which typically calls *your* code (inversion of control) rather than the other way around, unlike a library. Spring is a framework in this sense.

**Library** — A collection of reusable code (functions, classes) that your application calls directly, as needed — you're in control of when and how it's used, unlike a framework.

**Dependency** — An external library, framework, or service a piece of software relies on to function — managed explicitly in most modern projects via a dependency-management tool (Maven, npm).

**Module** — A self-contained, well-defined unit of code (a package, a library) with a clear boundary and interface, designed to be developed, tested, and reasoned about somewhat independently of the rest of the system.

**Coupling** — The degree to which one module/component depends on the internal details of another. Tight coupling means a change in one place forces changes elsewhere; loose coupling is generally the design goal.

**Cohesion** — The degree to which the responsibilities within a single module/component are closely related to each other and to that module's stated purpose. High cohesion (a module does one clear thing well) is generally the design goal, paired with low coupling between modules.

**Architecture** — The high-level structure of a system — its major components, how they're divided, and how they interact — the decisions that are hardest and most expensive to change later.

**Design pattern** — A named, reusable solution to a commonly recurring software design problem — Singleton, Factory, Observer, Strategy, and others from the classic "Gang of Four" catalog.

**Refactoring** — Restructuring existing code's internal structure to improve readability, maintainability, or design, without changing its external, observable behavior.

**Technical debt** — The implied future cost of choosing an easier, faster solution now over a better, more thorough one — like financial debt, it accrues "interest" (growing cost/friction) the longer it goes unaddressed.

**Unit testing** — Testing a single, small unit of code (one method, one class) in isolation, with external dependencies mocked/stubbed out — fast, cheap, and pinpoints exactly what broke. *See: [Computer Science Fundamentals Q28](Computer_Science_Fundamentals_Interview_Prep.md#28-whats-the-difference-between-unit-integration-and-end-to-end-tests).*

**Integration testing** — Testing that multiple units, or an application and a real external dependency, work correctly together — slower than unit tests, but catches bugs unit tests structurally can't. *See: [Computer Science Fundamentals Q28](Computer_Science_Fundamentals_Interview_Prep.md#28-whats-the-difference-between-unit-integration-and-end-to-end-tests).*

**Regression testing** — Re-running existing tests after a change to verify that previously-working functionality hasn't been broken by the new change — "regressed."

**Version control** — A system for tracking changes to a set of files over time, letting multiple people collaborate on the same codebase without simply overwriting each other's work. *See: [Computer Science Fundamentals Q27](Computer_Science_Fundamentals_Interview_Prep.md#27-what-is-version-control-and-what-does-git-actually-track).*

**Git** — The dominant modern, distributed version control system — every clone holds the entire project history locally, and Git tracks a series of full snapshots rather than line-by-line deltas. *See: [Computer Science Fundamentals Q27](Computer_Science_Fundamentals_Interview_Prep.md#27-what-is-version-control-and-what-does-git-actually-track).*

**Repository** — A Git-tracked project's full set of files plus its complete history of commits — what you clone, push to, and pull from.

**Branch** — An independent, named line of development within a Git repository, letting work happen in isolation before being merged back into a shared line (like `main`).

**Merge** — Combining the changes from one Git branch into another, integrating independently-developed work back together.

**CI/CD** (Continuous Integration / Continuous Delivery or Deployment) — CI automatically builds and tests every change, catching integration problems early. The two CDs aren't the same: **Continuous Delivery** keeps every passing change deployment-ready with a human still approving the release; **Continuous Deployment** skips that gate and ships every passing change to production automatically ([Martin Fowler — Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html)).

**Deployment** — The process of releasing a new version of software into an environment where it actually runs and serves real traffic/users.

---

## Security

**Authentication** — Verifying *who* a caller is — confirming an identity claim, typically via credentials, a token, or a certificate.

**Authorization** — Deciding *what* an already-authenticated caller is allowed to do — a distinct step from authentication, and the source of the classic `401` (not authenticated) vs. `403` (authenticated, but not authorized) distinction. *See: [Spring Security & OAuth2 Interview Prep](../Frameworks/Spring_Security_OAuth2_Interview_Prep.md).*

**Encryption** — Transforming readable data into unreadable ciphertext using a key, reversible only by someone holding the correct key. *See: [Computer Science Fundamentals Q9](Computer_Science_Fundamentals_Interview_Prep.md#9-what-is-encryption-and-whats-the-difference-between-symmetric-and-asymmetric-encryption).*

**Encoding** — Transforming data into a different representation for compatibility or transport reasons (base64, URL encoding) — **not** for secrecy; encoding is trivially reversible by anyone, with no key involved at all.

**Hashing** — A one-way transformation producing a fixed-size digest from any input, used for integrity checks and password verification, not confidentiality. "No way to recover the input" means computationally infeasible for a well-designed hash and non-trivial input, not mathematically impossible — a short or predictable input can still be found via brute force or a precomputed table, which is why passwords also need salting. *See: [Computer Science Fundamentals Q10](Computer_Science_Fundamentals_Interview_Prep.md#10-whats-the-difference-between-encryption-and-hashing).*

**Token** — An opaque or structured piece of data representing an authenticated session or granted access, presented on subsequent requests instead of re-sending credentials every time — a JWT is one common token format.

**Session** — State associated with a particular client's ongoing interaction with an application. Commonly stored server-side and keyed by a session ID in a cookie, but not necessarily — a stateless/client-side session encodes the state directly into a signed or encrypted token the client holds instead.

**Cookie** — A small piece of data the server asks the browser to store and automatically resend on subsequent requests to that domain — the standard mechanism for carrying a session ID (or other small state) across HTTP's otherwise-stateless requests.

**Vulnerability** — A weakness in a system that could be exploited to compromise its confidentiality, integrity, or availability — a specific flaw, distinct from a generic "bug" in that it has security consequences if exploited.

**Firewall** — A network security control that filters incoming/outgoing traffic based on defined rules (source, destination, port, protocol), blocking traffic that doesn't match an allowed pattern.

**Least privilege** — The security principle that any user, process, or system component should have only the minimum access/permissions it genuinely needs to do its job — nothing broader "just in case."

**Multi-factor authentication** (MFA) — Requiring two or more independent proofs of identity (something you know — a password; something you have — a device; something you are — biometrics) before granting access, so compromising one factor alone isn't enough.

---

## Distributed Systems & Infrastructure

**Cache** — A layer that stores a copy of data that's expensive to fetch or compute, so subsequent requests for the same data can be served faster from the cache instead of redoing the expensive work. *See: [Redis & Caching Interview Prep](../System%20Design/Redis_Caching_Interview_Prep.md).*

**Load balancer** — A component that distributes incoming requests across multiple backend server instances, so no single instance is overwhelmed and traffic can keep flowing if one instance fails.

**Proxy** — An intermediary that sits between a client and a server, forwarding requests on the client's behalf — a *forward* proxy represents clients to servers; a *reverse* proxy represents servers to clients.

**Message queue** — A component that holds messages/tasks until a consumer is ready to process them, decoupling producers from consumers in time and load. Strict ordering isn't universal — many implementations only preserve order within a single partition/queue instance (or trade it away entirely for throughput), not across the whole queue. *See: [Kafka Deep-Dive Interview Prep](../System%20Design/Kafka_Interview_Prep.md#2-what-ordering-does-kafka-guarantee).*

**Event** — A record that something happened — an order was placed, a user signed up — typically published to interested consumers rather than the producer calling each consumer directly.

**Microservice** — An independently deployable service, owning a specific, bounded piece of business capability, communicating with other services over the network rather than being compiled into one large deployable unit. *See: [Microservices & Architecture Patterns Interview Prep](../Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md).*

**Distributed system** — A system composed of multiple independent components running on different machines, communicating over a network, that must coordinate to appear (to a user) as one coherent system.

**Scalability** — A system's ability to handle increasing load — more users, more data, more traffic — typically by adding more resources (horizontal: more machines; vertical: bigger machines).

**Availability** — The proportion of time a system is actually up and successfully serving requests, commonly expressed as a percentage ("five nines" = 99.999%).

**Fault tolerance** — A system's ability to continue operating correctly (possibly in a degraded mode) even when some of its components fail, rather than the whole system going down when one part breaks.

**Consistency** — The guarantee that every read reflects the most recent write (strong consistency) or, in a distributed/eventually-consistent system, eventually will (see Eventual consistency below) — a core trade-off dimension in distributed data systems.

**Idempotency** — The property that performing an operation multiple times has the same effect as performing it once — critical for safe retries. *See: [REST API Design Interview Prep](../System%20Design/REST_API_Design_Interview_Prep.md).*

**Retry** — Automatically resending a failed request, typically with backoff (increasing delay between attempts) — only safe to do automatically for idempotent operations, or ones made idempotent via an explicit idempotency key.

**Circuit breaker** — A resilience pattern that detects when a downstream dependency is failing and "trips," failing fast on further calls to it for a period instead of letting every request queue up waiting on a dependency that's clearly not going to respond.

**Container** — A lightweight, isolated unit of execution packaging an application with its dependencies, sharing the host machine's kernel rather than virtualizing an entire separate OS the way a VM does. *See: [Docker & Kubernetes Interview Prep](../Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md).*

**Docker** — The dominant container platform/tooling — building container images, running containers, and managing their lifecycle on a single host.

**Kubernetes** — A container orchestration platform that manages deploying, scaling, networking, and healing containerized applications across a cluster of machines, rather than managing containers on one host manually.

**Cloud computing** — Renting on-demand computing resources (servers, storage, managed databases) from a provider (AWS, GCP, Azure) over the internet, rather than owning and operating physical hardware yourself.

**Logging** — Recording discrete events (an error occurred, a request was handled) as an application runs, for later inspection during debugging or incident investigation.

**Monitoring** — Continuously observing a system's health and behavior (via metrics, logs, and traces) to detect problems, ideally before they become customer-visible incidents.

**Metrics** — Numeric measurements collected over time about a system's behavior (request count, error rate, latency) — the quantitative backbone of monitoring and alerting.

**Alerting** — Automatically notifying a human (or triggering an automated response) when a metric crosses a threshold indicating something needs attention — the active, "wake someone up" counterpart to passive monitoring.

**Tracing** — Following a single logical request as it flows through multiple services in a distributed system, reconstructing the full causal chain as one coherent timeline rather than disconnected per-service logs. *See: [REST API Design Interview Prep](../System%20Design/REST_API_Design_Interview_Prep.md).*

**SLA** (Service Level Agreement) — A formal, often contractual commitment about a service's expected performance/availability, typically with consequences (credits, penalties) if it's not met.

**SLO** (Service Level Objective) — An internal target for a service's reliability (e.g., "99.9% of requests succeed") — the specific, measurable goal a team holds itself to, often stricter than the external SLA it supports.

**Throughput** — The rate at which a system successfully processes work — requests per second, messages per second — a measure of *capacity under load*, distinct from latency (a single request's speed).

**Backpressure** — A mechanism for a system to signal "slow down" to whatever is sending it work, when it can't keep up — rather than silently queuing unboundedly (risking memory exhaustion) or dropping work silently.

**Serialization** — Converting an in-memory object/data structure into a format (JSON, a byte stream) that can be stored or transmitted, and later reconstructed.

**Deserialization** — The reverse of serialization: reconstructing an in-memory object/data structure from its serialized (stored or transmitted) representation.

**API gateway** — A single entry point sitting in front of a set of backend services, handling cross-cutting concerns (routing, authentication, rate limiting) centrally so individual services don't each reimplement them. *See: [Microservices & Architecture Patterns Interview Prep](../Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md).*

**Database replication** — Maintaining copies of a database (or specific tables) on multiple servers, kept in sync, for redundancy (surviving a server failure) and/or read scalability (spreading read load across replicas).

**Database partitioning** — Splitting a large table's data across multiple physical storage units based on some rule (a range of values, a hash), so no single unit has to hold or serve the entire dataset alone.

**Sharding** — Horizontal partitioning specifically applied *across separate database servers/instances* (not just separate tables/files on one server) — each shard holds a distinct subset of the overall dataset.

**CAP theorem** — A distributed system experiencing a network partition must choose between Consistency and Availability — it can't guarantee both at the same time during that partition (Partition tolerance is assumed as a given for any real distributed system). *See: [Microservices & Architecture Patterns Interview Prep](../Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md).*

**Eventual consistency** — A consistency model where, if no new writes occur, all replicas will *eventually* converge to the same value — reads immediately after a write may briefly see stale data, in exchange for higher availability/lower latency than strong consistency.

**Message broker** — Infrastructure (Kafka, RabbitMQ) that receives messages from producers, stores/routes them, and delivers them to consumers — the actual system implementing the message-queue/pub-sub pattern. *See: [Kafka Deep-Dive Interview Prep](../System%20Design/Kafka_Interview_Prep.md).*

**Producer** — A component that creates and publishes messages/events to a message broker or queue, without needing to know who (if anyone) will consume them.

**Consumer** — A component that reads and processes messages/events from a message broker or queue, independent of and decoupled from whatever produced them.

**Idempotent operation** — An operation that produces the same end result no matter how many times it's performed — the specific property that makes automatic retries safe. *See: [REST API Design Interview Prep](../System%20Design/REST_API_Design_Interview_Prep.md).*

---

## Machine Learning Fundamentals

**Supervised learning** — Training a model on labeled data (input paired with the correct output), so it learns to predict the output for new, unseen inputs — classification (predicting a category) and regression (predicting a number) are the two main supervised task types.

**Unsupervised learning** — Training a model on unlabeled data, looking for structure (clusters, patterns) in the data itself rather than predicting a known correct answer — clustering and dimensionality reduction are the classic examples.

**Training set** — The portion of a dataset a model's parameters are actually fit to during training — the data the model directly learns from.

**Validation set** — A separate portion of data, held out from training, used to tune a model's hyperparameters and check its performance *during* development — since it's not used for training, it gives an honest read on generalization, but repeated tuning against it can still indirectly overfit to it.

**Test set** — A final, held-out portion of data touched only once, after all training and tuning is complete, to report a model's true, unbiased performance — using it for any tuning decision defeats its purpose.

**Overfitting** — A model that has learned the training data's noise and specific quirks rather than the underlying general pattern — it performs well on training data but poorly on new, unseen data.

**Underfitting** — A model too simple (or undertrained) to capture the underlying pattern in the data at all — it performs poorly on both training and new data.

**Bias-variance trade-off** — Bias is error from a model being too simple to capture the true pattern (underfitting); variance is error from a model being too sensitive to the specific training data it saw (overfitting) — reducing one typically increases the other, and the practical goal is the best balance for a given task, not minimizing either alone.

**Precision** — Of everything a model *predicted* as positive, the fraction that was actually positive — `TP / (TP + FP)`. High precision means few false alarms.

**Recall** — Of everything that was *actually* positive, the fraction the model correctly identified — `TP / (TP + FN)`. High recall means few missed positives. *See: [Vector Databases & RAG Interview Prep](../AI%20Engineering/Vector_Databases_and_RAG_Interview_Prep.md#9-what-is-retrieval-recall-and-how-do-you-measure-it) for this same metric applied to retrieval specifically.*

**F1 score** — The harmonic mean of precision and recall, `2 × (precision × recall) / (precision + recall)` — a single number balancing both, useful when neither false positives nor false negatives alone tell the whole story and a simple average would be misleadingly dominated by whichever metric is higher.

**ROC-AUC** — The Area Under the Receiver Operating Characteristic curve, which plots a binary classifier's true-positive rate against its false-positive rate across every possible decision threshold — an AUC of 1.0 is a perfect classifier, 0.5 is no better than random guessing, and it measures a model's overall ability to rank positives above negatives, independent of any one specific threshold choice.

**Gradient descent** — The core optimization algorithm behind training most machine learning models: repeatedly compute how a small change in each parameter would affect the loss (the gradient), then adjust every parameter a small step in the direction that reduces loss, until the loss stops meaningfully improving.

**Learning rate** — How large a step gradient descent takes on each update — too high and training can overshoot and never converge (or diverge outright); too low and training converges correctly but impractically slowly.

**Backpropagation** — The algorithm that efficiently computes the gradient (needed for gradient descent) for *every* parameter in a neural network, by applying the chain rule backward from the output layer's error through each preceding layer — without it, computing each parameter's individual contribution to the error would be computationally intractable for a network with many layers.

**Activation function** — A non-linear function applied to a neural network layer's output (ReLU, sigmoid, softmax) — without one, stacking multiple layers would be mathematically equivalent to a single linear layer, no matter how many layers were stacked, since a composition of purely linear functions is itself just another linear function.

**CNN** (Convolutional Neural Network) — A network architecture built around convolutional layers that slide a small learned filter across an input, making it especially effective for spatially-structured data like images, where the same local pattern (an edge, a texture) can appear anywhere in the input.

**RNN / LSTM** (Recurrent Neural Network / Long Short-Term Memory) — Architectures designed for sequential data, processing one element at a time while carrying a hidden state forward — LSTMs add explicit gating mechanisms specifically to help preserve information over longer sequences than a plain RNN can reliably manage. Largely superseded by the Transformer architecture for language tasks. *See: [LLM Fundamentals Interview Prep](../AI%20Engineering/LLM_Fundamentals_Interview_Prep.md#2-what-is-self-attention-and-what-problem-does-it-solve) for exactly why — RNNs process sequentially (slow to train, struggles with long-range dependencies) while self-attention connects any two positions directly and computes in parallel.*

**Cross-entropy loss** — The standard loss function for classification tasks (including next-token prediction in a language model) — it measures how different a model's predicted probability distribution is from the true distribution, penalizing a confident wrong prediction far more heavily than an unconfident one.

**Regularization** — Any technique that discourages a model from overfitting by penalizing excessive complexity — L1/L2 penalties on parameter magnitudes, and techniques like dropout below, are all forms of regularization.

**Batch normalization** — Normalizing a layer's inputs (to zero mean, unit variance) across each training batch before they reach the next layer — stabilizes and speeds up training by keeping the scale of values flowing through the network consistent as parameters update.

**Dropout** — A regularization technique that randomly disables (zeroes out) a fraction of a layer's neurons during each training step — prevents the network from becoming overly reliant on any single neuron or narrow co-adapted group of them, encouraging more robust, redundant representations.

**Distributed transaction** — A transaction spanning multiple database nodes or systems — whether genuinely separate databases or shards of one distributed database — that must all commit or all roll back together. Genuinely hard to achieve reliably (classic two-phase commit has its own failure modes), which is exactly why patterns like the saga and the transactional outbox exist as alternatives. *See: [Transactions Interview Prep](../System%20Design/Transactions_Interview_Prep.md).*
