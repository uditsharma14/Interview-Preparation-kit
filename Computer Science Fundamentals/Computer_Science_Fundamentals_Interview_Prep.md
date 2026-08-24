# Computer Science Fundamentals — Interview Prep (Basic Level, with Code & Sources)

> **Target level:** Basic (foundational — no graduation to Staff in this guide; see "How to use this" below) · **Baseline:** HTTP semantics per RFC 9110, HTTP/1.1 message syntax per RFC 9112, TLS 1.3 per RFC 8446, DNS per RFC 1035 · **Last verified:** 2026-08-23 · **Prerequisites:** none — this is the foundational layer the rest of InterviewSmith assumes

How to use this: unlike most guides in InterviewSmith, this one is deliberately **Basic-only** — networking, security, and general CS terminology genuinely foundational enough that every other guide here assumes it without re-explaining it. If a term in another guide (TLS, symmetric encryption, TCP, Big-O) isn't landing, it's worth checking here first. Each question has a short **spoken answer** (80–150 words, plain language, no Staff-level complexity), **one focused example**, a **"Go deeper"** section for the advanced nuance that belongs in whichever guide actually covers that topic in depth, and a **source**. This guide intentionally stays shallow so those other guides don't have to re-teach the basics every time. A note on the Example code blocks: most are self-contained and compilable as shown (verified directly); a few are deliberately partial fragments illustrating one idea (a loop shape, an API call) without full class/import scaffolding, or deliberately show code that doesn't compile or run cleanly to make a specific point — those are marked as such in their own comments.

<!-- toc -->
## Table of Contents

- [Networking](#networking)
  - [1. What's the Difference Between TCP and UDP?](#1-whats-the-difference-between-tcp-and-udp)
  - [2. What Is DNS, and How Does a Domain Name Resolve to an IP Address?](#2-what-is-dns-and-how-does-a-domain-name-resolve-to-an-ip-address)
  - [3. What's the Difference Between an IP Address and a Port Number?](#3-whats-the-difference-between-an-ip-address-and-a-port-number)
  - [4. What's the Difference Between a URI, a URL, and a URN?](#4-whats-the-difference-between-a-uri-a-url-and-a-urn)
- [HTTP](#http)
  - [5. What Is HTTP, and What Does It Mean That It's "Stateless"?](#5-what-is-http-and-what-does-it-mean-that-its-stateless)
  - [6. What's the Difference Between HTTP/1.1, HTTP/2, and HTTP/3?](#6-whats-the-difference-between-http11-http2-and-http3)
  - [7. What Do the HTTP Status Code Categories (1xx–5xx) Mean, at a Glance?](#7-what-do-the-http-status-code-categories-1xx5xx-mean-at-a-glance)
  - [8. What's the Difference Between an HTTP Header and the Request/Response Body?](#8-whats-the-difference-between-an-http-header-and-the-requestresponse-body)
- [Encryption & Security](#encryption--security)
  - [9. What Is Encryption, and What's the Difference Between Symmetric and Asymmetric Encryption?](#9-what-is-encryption-and-whats-the-difference-between-symmetric-and-asymmetric-encryption)
  - [10. What's the Difference Between Encryption and Hashing?](#10-whats-the-difference-between-encryption-and-hashing)
  - [11. What Is TLS, and How Does the Handshake Establish a Secure Connection?](#11-what-is-tls-and-how-does-the-handshake-establish-a-secure-connection)
  - [12. What Is a Digital Certificate, and What Role Does a Certificate Authority Play?](#12-what-is-a-digital-certificate-and-what-role-does-a-certificate-authority-play)
- [General CS & Software Terminology](#general-cs--software-terminology)
  - [13. What Is Big-O Notation, and Why Does It Matter?](#13-what-is-big-o-notation-and-why-does-it-matter)
  - [14. What's the Difference Between SQL and NoSQL Databases?](#14-whats-the-difference-between-sql-and-nosql-databases)
  - [15. What Is an API, and How Does It Differ From a Web Service?](#15-what-is-an-api-and-how-does-it-differ-from-a-web-service)
- [Data Structures & Algorithms](#data-structures--algorithms)
  - [16. What Is a Stack, and What Is a Queue?](#16-what-is-a-stack-and-what-is-a-queue)
  - [17. What's the Difference Between a Tree and a Graph?](#17-whats-the-difference-between-a-tree-and-a-graph)
  - [18. What Is Recursion, and What Is a Base Case?](#18-what-is-recursion-and-what-is-a-base-case)
- [Programming Languages & OOP](#programming-languages--oop)
  - [19. What Are the Four Pillars of Object-Oriented Programming?](#19-what-are-the-four-pillars-of-object-oriented-programming)
  - [20. What's the Difference Between a Compiled and an Interpreted Language?](#20-whats-the-difference-between-a-compiled-and-an-interpreted-language)
  - [21. What's the Difference Between Static and Dynamic Typing?](#21-whats-the-difference-between-static-and-dynamic-typing)
- [Operating Systems](#operating-systems)
  - [22. What Is an Operating System, and What Does the Kernel Do?](#22-what-is-an-operating-system-and-what-does-the-kernel-do)
  - [23. What Is Virtual Memory, and What Is Paging?](#23-what-is-virtual-memory-and-what-is-paging)
  - [24. What Is CPU Caching, and Why Does It Matter for Performance?](#24-what-is-cpu-caching-and-why-does-it-matter-for-performance)
- [Databases](#databases)
  - [25. What Is Database Normalization, and What Do 1NF, 2NF, and 3NF Mean?](#25-what-is-database-normalization-and-what-do-1nf-2nf-and-3nf-mean)
  - [26. What Is a Database Index, and Why Does It Speed Up Queries?](#26-what-is-a-database-index-and-why-does-it-speed-up-queries)
- [Software Engineering Practices](#software-engineering-practices)
  - [27. What Is Version Control, and What Does Git Actually Track?](#27-what-is-version-control-and-what-does-git-actually-track)
  - [28. What's the Difference Between Unit, Integration, and End-to-End Tests?](#28-whats-the-difference-between-unit-integration-and-end-to-end-tests)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## Networking

### 1. What's the Difference Between TCP and UDP?

**Answer:**

"Both are transport-layer protocols that sit on top of IP, but they trade reliability for speed in opposite ways. TCP (Transmission Control Protocol) is connection-oriented and reliable: before any data flows, the client and server perform a handshake to set up a connection. TCP then makes sure the data that arrives is complete, in order, and without duplicates — it retransmits anything lost and reassembles anything that arrives out of order. UDP (User Datagram Protocol) is connectionless and makes no such guarantee: a packet is just sent, with no handshake, no guaranteed delivery, and no reordering. That sounds strictly worse, but it's the right choice when a late packet is useless anyway — a live video frame, a real-time game position update — and low latency matters more than perfect delivery."

**Example:**

```text
TCP: [SYN] -> [SYN-ACK] -> [ACK]  (handshake, THEN data flows)
     -> data packet 1 (acknowledged)
     -> data packet 2 (lost — automatically RETRANSMITTED)
     -> data packet 3 (acknowledged)
     Application sees: 1, 2, 3 — in order, complete, no duplicates

UDP: -> datagram 1 (delivered)
     -> datagram 2 (lost — GONE, no retransmission, no notification)
     -> datagram 3 (delivered)
     Application sees: 1, 3 — whatever arrived, in whatever order, with no error
     reported even when a datagram never showed up at all.
```

**Go deeper:**

TCP's reliability guarantee is conditional, not absolute: if the connection is genuinely broken, TCP doesn't retry forever — it eventually reports the failure back to the application (a timeout or a reset) rather than delivering the data some other way. Most protocols covered in InterviewSmith ride on TCP: HTTP, and therefore essentially every REST API in the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md), needs guaranteed, in-order delivery. UDP shows up in more specialized cases — DNS (covered next) uses it for small queries, falling back to TCP for larger ones, and QUIC, the transport HTTP/3 is built on, is UDP-based even though HTTP/3 still needs reliability, because QUIC reimplements reliability itself on top of UDP rather than using TCP.

**Source:** [RFC 9293 §3.6 — Closing a Connection (reliable delivery is conditional on the connection closing successfully)](https://datatracker.ietf.org/doc/html/rfc9293#section-3.6), [RFC 768 — User Datagram Protocol](https://datatracker.ietf.org/doc/html/rfc768)

---

### 2. What Is DNS, and How Does a Domain Name Resolve to an IP Address?

**Answer:**

"DNS (Domain Name System) is the internet's directory service — it translates human-readable domain names, like `example.com`, into the numeric IP addresses computers actually use to route traffic, so nobody has to remember a server's IP address, just its name. Resolution happens through a chain of lookups: a resolver first asks a **root** nameserver, which points it to the right **top-level-domain (TLD)** nameserver, the one handling `.com`, say; that TLD nameserver points to the **authoritative** nameserver responsible for the specific domain; and that authoritative nameserver finally returns the actual IP address. In practice, this full chain rarely runs on every request, because DNS answers are cached at every layer — the browser, the OS, the resolver — for a duration set by the record's TTL (time-to-live)."

**Example:**

```text
Client wants: example.com -> ?

1. Client's resolver asks a ROOT nameserver: "example.com?"
   Root: "I don't know, but ask the .com TLD nameserver"
2. Resolver asks the .com TLD nameserver: "example.com?"
   TLD: "I don't know the IP, but example.com's authoritative nameserver is ns1.example.com"
3. Resolver asks ns1.example.com (the AUTHORITATIVE nameserver): "example.com?"
   Authoritative: "93.184.216.34" (the actual answer, with a TTL, e.g. 3600 seconds)
4. Resolver returns 93.184.216.34 to the client, AND caches it for 3600 seconds
```

**Go deeper:**

DNS caching is a genuinely common source of confusing production incidents: a service migration that changes a domain's IP has to account for the fact that some fraction of traffic keeps hitting the *old* IP until every cache layer's TTL expires. That's exactly why a low TTL is often set deliberately *before* a planned migration — giving caches less time to hold a stale answer — rather than discovered as a problem during the migration itself.

**Source:** [RFC 1035 — Domain Names, Implementation and Specification](https://datatracker.ietf.org/doc/html/rfc1035)

---

### 3. What's the Difference Between an IP Address and a Port Number?

**Answer:**

"An **IP address** identifies a specific *machine*, or network interface, on a network — where to deliver a packet, at the level of 'which computer.' A **port number** identifies a specific *application or process* running on that machine — which of potentially many programs listening on that machine should actually receive the data. A single server might run a web server, a database, and an SSH daemon simultaneously, all reachable at the same IP address, distinguished only by which port each is listening on — conventionally 80/443 for HTTP/HTTPS, 5432 for PostgreSQL, or 22 for SSH. Together, an IP address plus a port number form a **socket** — the actual endpoint a connection is made to, like `93.184.216.34:443`."

**Example:**

```text
One machine, IP address 93.184.216.34, running THREE services simultaneously:

93.184.216.34:80    -> web server (HTTP)
93.184.216.34:443   -> web server (HTTPS)
93.184.216.34:5432  -> PostgreSQL database
93.184.216.34:22    -> SSH daemon

Same IP address for all four — the PORT is what routes an incoming
connection to the correct listening application on that machine.
```

**Go deeper:**

IANA splits the port space into three ranges. **System Ports** (0–1023, colloquially "well-known ports" — 80, 443, and 22 among them) require elevated privileges to bind to on most operating systems, which is exactly why a web server sometimes needs to run as root, or more safely use a reverse proxy, just to listen on port 80/443 directly, and why containerized services often listen on a higher, unprivileged port internally, like 8080, with the container platform mapping that to the standard external port instead, covered in the [Docker & Kubernetes guide](../Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md). PostgreSQL's 5432 is a useful contrast: it falls in the **User Ports** range (1024–49151), so it needs no special privilege at all, which is why a PostgreSQL server normally runs under an ordinary, unprivileged account.

**Source:** [IANA — Service Name and Transport Protocol Port Number Registry](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml)

---

### 4. What's the Difference Between a URI, a URL, and a URN?

**Answer:**

"**URI** (Uniform Resource Identifier) is the umbrella term — any string that identifies a resource, full stop. **URL** (Uniform Resource Locator) and **URN** (Uniform Resource Name) are the two roles a URI can play. A URL identifies a resource *and* tells you how to actually reach it — a scheme, a host, a path, like `https://example.com/orders/123` — so you can act on it directly. A URN identifies a resource by a persistent, location-independent *name*, with no information about where to actually find it — `urn:isbn:0451450523` names a specific book by ISBN, regardless of which library, bookstore, or website might currently have a copy. In everyday conversation, 'URL' and 'URI' get used almost interchangeably, and that's rarely a real problem, since URNs are comparatively rare outside specific standardized-identifier contexts."

**Example:**

```text
URI (umbrella term): any resource identifier

  URL (locator — tells you HOW to reach it):
    https://example.com/orders/123
    ftp://files.example.com/report.pdf
    mailto:someone@example.com

  URN (name — identifies WHAT it is, not where to find it):
    urn:isbn:0451450523          <- a specific book, by ISBN, no location info at all
    urn:uuid:6ba7b810-9dad-...   <- a specific, globally-unique identifier
```

**Go deeper:**

Every REST endpoint discussed in the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md), like `GET /orders/123`, is really a URL — it both identifies the `Order` resource and tells the client exactly how to fetch it, which is the "URI as locator" role, not the "URI as pure name" role a URN plays. RFC 3986 §1.1.3 itself explicitly recommends that "future specifications and related documentation should use the general term 'URI' rather than the more restrictive terms 'URL' and 'URN'" — so the everyday habit of saying 'URL' loosely for 'URI' is close to what the spec now suggests, even though the locator/name distinction underneath is still worth knowing precisely.

**Source:** [RFC 3986 §1.1.3 — URI, URL, and URN](https://datatracker.ietf.org/doc/html/rfc3986#section-1.1.3)

---

## HTTP

### 5. What Is HTTP, and What Does It Mean That It's "Stateless"?

**Answer:**

"HTTP (HyperText Transfer Protocol) is the application-layer protocol that essentially the entire web, and virtually every REST API, is built on: a client sends a **request** — a method, a target resource, headers, optionally a body — and the server sends back a **response** — a status code, headers, optionally a body. It's a simple request/response model, not a persistent conversation the protocol itself remembers. 'Stateless' means the server doesn't retain any memory of previous requests from a given client at the protocol level — each request must carry everything the server needs to process it, since the server treats every request as if it's the very first one it's ever seen from that client. That's exactly why 'staying logged in' isn't something HTTP does automatically — it's built on top of HTTP, via a session cookie or a token the client re-sends on every request."

**Example:**

```http
GET /orders/123 HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGc...

# Every SINGLE request must be self-sufficient — the server has NO memory
# of any earlier request from this client at the protocol level. If the
# Authorization header were omitted here, the server has no other way
# to know who's asking, even if this exact client made an identical,
# authenticated request one second earlier.
```

**Go deeper:**

Session-based authentication and token-based authentication both exist as *application-layer* workarounds for statelessness, not protocol features — covered in real depth in the [Spring Security & OAuth2 guide](../Frameworks/Spring_Security_OAuth2_Interview_Prep.md). Statelessness is actually a deliberate, valuable design choice for scalability, not an accidental limitation: a stateless server doesn't need to remember anything about which client it talked to previously, which is exactly what lets any request be routed to any server instance behind a load balancer, with no need for "sticky sessions" pinning a client to one specific backend server.

**Source:** [RFC 9110 — HTTP Semantics](https://datatracker.ietf.org/doc/html/rfc9110)

---

### 6. What's the Difference Between HTTP/1.1, HTTP/2, and HTTP/3?

**Answer:**

"HTTP/1.1 sends requests as plain text over a TCP connection, and in practice handles one request/response at a time per connection — the next request can't be sent until the current response finishes. That creates **head-of-line blocking**: a slow response holds up everything queued behind it, which is why browsers historically opened several parallel connections to work around it. HTTP/2 fixes this at the HTTP layer with **multiplexing**: many requests and responses can be interleaved concurrently over a single TCP connection, so one slow response no longer blocks the others behind it. HTTP/3 goes further by replacing TCP with **QUIC**, a UDP-based transport, which removes a deeper blocking problem: on HTTP/2, one lost packet still blocks every multiplexed stream, since TCP delivers everything strictly in order. QUIC gives each stream its own independent reliability, so a lost packet on one stream doesn't stall the others."

**Example:**

```text
HTTP/1.1: one request/response handled at a time PER connection
          [req A] --wait for response A--> [req B] --wait--> [req C]

HTTP/2:   many requests MULTIPLEXED over ONE TCP connection
          [req A, req B, req C all in flight simultaneously, interleaved]
          BUT: one lost TCP packet still blocks ALL streams (TCP-level HOL blocking)

HTTP/3:   runs over QUIC (UDP-based) instead of TCP
          [req A, req B, req C multiplexed, EACH with its own independent reliability]
          A lost packet on stream B does NOT block streams A or C
```

**Go deeper:**

The HTTP/1.1 spec technically allows a client to **pipeline** requests — sending several without waiting for each response — but a server must still send responses back in the exact order requested, so a slow response still blocks every faster one queued behind it; pipelining was rarely deployed in practice, since buggy intermediaries made it unreliable enough that browsers dropped support, so most real connections just handle one request/response cycle at a time instead, with the identical bottleneck. HTTP/2 and HTTP/3 are both essentially transparent to application code — a Spring Boot REST controller doesn't need to know which HTTP version carried a given request. What *does* change is deployment (TLS is effectively mandatory for HTTP/2 and HTTP/3 in virtually every real deployment) and performance under real-world packet loss, not anything about how you'd design a REST API's resources, covered in the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md).

**Source:** [RFC 9112 §9.3.2 — Pipelining](https://datatracker.ietf.org/doc/html/rfc9112#section-9.3.2), [RFC 9112 §9.4 — Concurrency (head-of-line blocking)](https://datatracker.ietf.org/doc/html/rfc9112#section-9.4), [RFC 9113 — HTTP/2](https://datatracker.ietf.org/doc/html/rfc9113), [RFC 9114 — HTTP/3](https://datatracker.ietf.org/doc/html/rfc9114)

---

### 7. What Do the HTTP Status Code Categories (1xx–5xx) Mean, at a Glance?

**Answer:**

"HTTP status codes are grouped into five categories by their first digit, and knowing the *category* meaning is more useful day-to-day than memorizing every individual code. **1xx (Informational)** means the request was received and processing continues — rare to encounter directly in application code. **2xx (Success)** means the request was received, understood, and accepted, like `200 OK` or `201 Created`. **3xx (Redirection)** means further action is needed to complete the request, typically following a different URL. **4xx (Client Error)** means the request itself has a problem the *client* needs to fix, like `400 Bad Request` or `404 Not Found`. **5xx (Server Error)** means the request was valid, but the *server* failed to fulfill it, like `500 Internal Server Error`. The 4xx-versus-5xx distinction is the single most operationally useful one: a spike in 4xx usually means clients are doing something wrong, while a spike in 5xx means the server is broken."

**Example:**

```text
1xx  Informational   100 Continue
2xx  Success          200 OK · 201 Created · 204 No Content
3xx  Redirection      301 Moved Permanently · 302 Found · 304 Not Modified
4xx  Client Error     400 Bad Request · 401 Unauthorized · 403 Forbidden · 404 Not Found · 429 Too Many Requests
5xx  Server Error     500 Internal Server Error · 502 Bad Gateway · 503 Service Unavailable
```

**Go deeper:**

The [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md) has a dedicated question for exactly when to use which *specific* code within these categories — `200` vs. `201` vs. `202` vs. `204`, `400` vs. `409` vs. `422` — real design nuance beyond what this foundational overview covers. The [Spring Security & OAuth2 guide](../Frameworks/Spring_Security_OAuth2_Interview_Prep.md) covers the specific, commonly-confused `401` (not authenticated) versus `403` (authenticated, but not authorized) distinction within the 4xx category.

**Source:** [RFC 9110 §15 — HTTP Status Codes](https://datatracker.ietf.org/doc/html/rfc9110#section-15)

---

### 8. What's the Difference Between an HTTP Header and the Request/Response Body?

**Answer:**

"**Headers** are metadata *about* the request or response — key-value pairs describing things like content type (`Content-Type: application/json`), authentication credentials (`Authorization: Bearer ...`), caching directives, or the response's size (`Content-Length`) — information a client, server, or an intermediary like a proxy needs in order to correctly *handle* the message, without necessarily needing to parse the actual payload itself. The **body** is the actual payload being transferred — the JSON representing an order, the HTML of a web page, the bytes of an uploaded image. Not every request or response has a body: a `GET` request typically has none, since there's nothing to send, and a `204 No Content` response has none by definition — but every request and response has headers, even if just a couple of basic ones, since headers are what make the message meaningfully interpretable in the first place."

**Example:**

```http
POST /orders HTTP/1.1                    <- request line
Host: example.com                          <- HEADER
Content-Type: application/json              <- HEADER: "the body is JSON"
Authorization: Bearer eyJhbGc...             <- HEADER: credentials
Content-Length: 47                            <- HEADER: "the body is 47 bytes"

{"sku": "WIDGET-1", "quantity": 2}          <- BODY: the actual payload
```

**Go deeper:**

Headers are exactly where a lot of mechanisms covered elsewhere in InterviewSmith actually live — idempotency keys, rate-limit signals (`RateLimit-Remaining`), `ETag`/`If-Match` for optimistic concurrency, `Deprecation`/`Sunset` for API lifecycle management, all covered in depth in the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md). Headers are the standard, HTTP-native place to carry structured metadata that intermediaries like caches, gateways, and proxies can act on without needing to parse and understand the request/response body at all.

**Source:** [RFC 9110 §6 — Message Content](https://datatracker.ietf.org/doc/html/rfc9110#section-6), [RFC 9110 §5 — Field Values (Headers)](https://datatracker.ietf.org/doc/html/rfc9110#section-5)

---

## Encryption & Security

### 9. What Is Encryption, and What's the Difference Between Symmetric and Asymmetric Encryption?

**Answer:**

"Encryption transforms readable data ('plaintext') into unreadable data ('ciphertext') using a key, so only someone with the correct key can reverse it and recover the original — the point is to let data be stored or sent somewhere an attacker might see it, without the attacker being able to actually read it. **Symmetric encryption** uses the exact same key for both encrypting and decrypting. It's fast and cheap, which makes it the right choice for encrypting large amounts of data — AES is the standard modern algorithm — but both parties need the same secret key, so it has to be shared securely beforehand. **Asymmetric encryption** (public-key cryptography) uses a *pair* of related keys instead: a public key anyone can have, and a private key kept secret. Data encrypted with the public key can only be decrypted with the matching private key — but it's much more computationally expensive than symmetric encryption."

**Example:**

```text
SYMMETRIC (e.g., AES): ONE shared secret key, used for both directions
  Alice: plaintext --[key K]--> ciphertext  --sends ciphertext-->  Bob: ciphertext --[key K]--> plaintext
  Problem: Alice and Bob both need key K — how do they exchange K securely in the first place?

ASYMMETRIC (e.g., RSA): a KEY PAIR — public key (shareable) + private key (secret)
  Alice encrypts with Bob's PUBLIC key --sends ciphertext--> Bob decrypts with his OWN PRIVATE key
  No shared secret ever needs to be exchanged — Bob's public key can be posted anywhere openly
```

**Go deeper:**

Asymmetric encryption solves symmetric encryption's key-distribution problem, since the public key can be shared openly with no secure channel needed — but its computational cost is exactly why real systems don't use it for bulk data. TLS, covered next, uses asymmetric encryption only briefly, just to securely exchange a symmetric key, then switches to fast symmetric encryption for the actual bulk data. This hybrid approach is exactly what happens inside a TLS handshake, and it's why HTTPS can encrypt an entire web session's worth of data without paying asymmetric encryption's much higher cost for every single byte transferred.

**Source:** [NIST — Cryptographic Standards and Guidelines](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines)

---

### 10. What's the Difference Between Encryption and Hashing?

**Answer:**

"Encryption is explicitly **reversible**, given the right key — the legitimate recipient needs to recover the original plaintext. Hashing is explicitly **one-way**: a hash function takes an input of any size and produces a fixed-size output, a 'digest,' with no key and no way to reverse the process and recover the original input. They solve different problems: encryption is for *confidentiality* — protecting data so only someone with the key can read it, while still recovering the original when needed. Hashing is for *integrity and verification* — proving data hasn't changed, or checking a match, without ever recovering the original value. That's exactly why passwords are **hashed**, never merely encrypted: the application should never need to recover a user's actual password, only verify that a freshly-submitted password produces the same hash as the one stored at registration."

**Example:**

```text
ENCRYPTION (reversible, with the right key):
  plaintext "hello" --[encrypt with key K]--> ciphertext "x7Gk..." --[decrypt with key K]--> "hello"

HASHING (one-way, no key involved at all):
  "hello" --[hash function]--> "2cf24dba5fb0a30e..."
  There is NO operation that takes "2cf24dba..." and recovers "hello" — it's not reversible by design.

  Verifying a password: hash("submitted-password") == stored-hash ?
  The application NEVER decrypts anything to check this — there's nothing to decrypt.
```

**Go deeper:**

This distinction is what makes "should we encrypt passwords or hash them" a bit of a trick question: the correct answer, hash them with a purpose-built slow algorithm like bcrypt, covered in the [Spring Security & OAuth2 guide](../Frameworks/Spring_Security_OAuth2_Interview_Prep.md)'s `BCryptPasswordEncoder` question, means the application should genuinely *never* be able to recover a user's actual password at all — not even the application's own operators, not even with full database access. That's a stronger, more defensible security property than "encrypted, but technically recoverable by whoever holds the encryption key."

**Source:** [NIST SP 800-107 — Recommendation for Applications Using Approved Hash Algorithms](https://csrc.nist.gov/pubs/sp/800/107/r1/final)

---

### 11. What Is TLS, and How Does the Handshake Establish a Secure Connection?

**Answer:**

"TLS (Transport Layer Security, the modern successor to SSL) is the protocol that encrypts a connection between a client and server — HTTPS is simply HTTP running over a TLS-encrypted connection instead of a plain one. Before any actual application data flows, TLS runs a **handshake** that accomplishes two things: the client verifies the server is genuinely who it claims to be, via the server's digital certificate, covered next, and both sides agree on a shared symmetric key for the rest of the session — combining exactly the asymmetric-then-symmetric pattern from the encryption question earlier in this guide. In TLS 1.3, the current version, this handshake is deliberately streamlined compared to older TLS versions: the client and server can typically agree on a shared key and start exchanging encrypted application data after just one round trip, rather than the several round trips earlier TLS versions required."

**Example:**

```text
TLS 1.3 handshake (simplified):

1. Client -> Server: "Here are the encryption algorithms I support, and my key-exchange info"
2. Server -> Client: "Here's my certificate (proving who I am), my chosen algorithm,
                      my key-exchange info, and a computed shared secret"
   -- at this point, both sides can independently compute the SAME symmetric key --
3. Client verifies the server's certificate (via the CA chain, covered next),
   then both sides switch to fast SYMMETRIC encryption for the actual application data

Only ~1 round trip needed before encrypted application data can start flowing.
```

**Go deeper:**

Fewer round trips is a real, measurable improvement for anything latency-sensitive, since every additional handshake round trip directly adds to how long a user waits before a page starts loading. The [Spring Security & OAuth2 guide](../Frameworks/Spring_Security_OAuth2_Interview_Prep.md) treats HTTPS as a hard prerequisite for every authentication mechanism it covers — Basic Auth, form login, bearer tokens — since none of those mechanisms protect credentials *in transit* on their own; TLS is specifically what's doing that job underneath, which is why base64-encoding or hashing credentials is never a substitute for actual transport encryption.

**Source:** [RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3](https://datatracker.ietf.org/doc/html/rfc8446)

---

### 12. What Is a Digital Certificate, and What Role Does a Certificate Authority Play?

**Answer:**

"A digital certificate is a file that binds a public key to an identity — a domain name, an organization — and is itself digitally signed by a trusted third party vouching that the binding is genuine. It's how a client can trust that the public key it's about to use during a TLS handshake actually belongs to `example.com`, and not to an attacker impersonating `example.com`. Without this, anyone can generate a public/private key pair and claim to be `example.com`; a certificate is what lets a client verify that claim rather than just trusting it blindly. A **Certificate Authority (CA)** is that trusted third party — an organization, like Let's Encrypt or DigiCert, that verifies a domain's ownership before issuing a certificate for it, and whose own signing key is itself pre-trusted by essentially every browser and operating system out of the box."

**Example:**

```text
Chain of trust:

[Root CA certificate]           <- pre-installed, trusted by the OS/browser by default
        |  signs
        v
[Intermediate CA certificate]   <- signed BY the root CA
        |  signs
        v
[example.com's certificate]     <- signed by the intermediate CA, contains example.com's PUBLIC KEY

Browser verifies: does this chain, link by link, lead back to a root
certificate I already trust? If yes -> the server's identity is verified.
```

**Go deeper:**

When a browser receives a server's certificate, it checks that the certificate was signed by a CA it already trusts, following this **chain of trust** up through one or more intermediate certificates to a trusted root — if the chain is broken, expired, or ends at an unrecognized authority, the browser shows the familiar "connection is not private" warning. Let's Encrypt is a genuinely significant, relatively recent shift in this space: it offers free, automatable certificate issuance via the ACME protocol, which meaningfully lowered the barrier to universal HTTPS adoption. Most modern deployment pipelines, including typical Kubernetes ingress setups covered in the [Docker & Kubernetes guide](../Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md), now provision and renew TLS certificates automatically this way, rather than as a manual, infrequent task.

**Source:** [NIST SP 800-57 — Recommendation for Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final), [RFC 5280 — Internet X.509 Public Key Infrastructure Certificate](https://datatracker.ietf.org/doc/html/rfc5280)

---

## General CS & Software Terminology

### 13. What Is Big-O Notation, and Why Does It Matter?

**Answer:**

"Big-O notation describes how an algorithm's resource usage, usually time, grows as the size of its input, conventionally called `n`, grows — it's about the *growth trend*, not an exact measurement of real-world speed for any particular input size. `O(1)` (constant time) means the work stays roughly the same no matter how large the input is, like a hash map lookup. `O(n)` (linear time) means the work grows in direct proportion to the input, like scanning every element of a list once. `O(log n)` (logarithmic time) means the work grows very slowly as input grows, like a binary search — doubling the input barely adds any extra work. `O(n²)` (quadratic time) means the work grows with the *square* of the input, like a nested loop comparing every pair of elements, which gets expensive fast as input grows."

**Example:**

```java
// Four independent fragments, not one program — each assumes its own
// already-declared map/items/sortedList/target variables.

// O(1) — constant time, regardless of map size
map.get(key);

// O(n) — linear: work scales directly with the list's size
for (Item item : items) { /* ... */ }

// O(log n) — logarithmic: doubling the input adds only a small constant amount of work
Collections.binarySearch(sortedList, target);

// O(n²) — quadratic: a nested loop comparing every pair — gets expensive FAST as n grows
for (Item a : items) {
    for (Item b : items) {
        if (a.matches(b)) { /* ... */ }
    }
}
```

**Go deeper:**

Big-O matters because an algorithm that looks fine in testing, with small `n`, can become a genuine production problem at real scale, with large `n`, if its growth rate is bad — an `O(n²)` algorithm that's imperceptibly slow for 100 items can become unusably slow for 100,000. The [Java Collections guide](../Language/Java_Collections_Interview_Prep.md) covers exactly this trade-off repeatedly and concretely (`ArrayList.get()` is O(1), `LinkedList.get()` is O(n); `HashMap` operations are O(1) average, `TreeMap` operations are O(log n)). Big-O specifically describes the *worst case*, or sometimes average case, asymptotic behavior, not a guarantee about any single specific run, which is why two algorithms with the same Big-O complexity can still have meaningfully different real-world performance due to constant factors Big-O deliberately ignores.

**Source:** [MIT OpenCourseWare — Introduction to Algorithms, Asymptotic Notation](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)

---

### 14. What's the Difference Between SQL and NoSQL Databases?

**Answer:**

"**SQL (relational) databases**, like PostgreSQL and MySQL, store data in tables with a fixed, predefined schema — every row in a table has the same set of columns, relationships between tables are expressed via foreign keys, and the database enforces the schema and referential integrity for you. They're queried with SQL, support complex multi-table joins natively, and virtually all provide strong ACID transaction guarantees, covered in the [Transactions guide](../System%20Design/Transactions_Interview_Prep.md). **NoSQL** is a broad umbrella term covering several genuinely different data models, not one single alternative to SQL: **document stores**, like MongoDB, store flexible, JSON-like documents with no enforced schema across documents; **key-value stores**, like Redis, store simple key-to-value pairs optimized for extremely fast lookups; **wide-column stores**, like Cassandra, are built for very high write throughput across huge, distributed datasets; **graph databases**, like Neo4j, are optimized for traversing richly-interconnected relationships."

**Example:**

```text
SQL (relational) — fixed schema, tables, foreign keys, joins, strong ACID:

  orders table:           order_items table:
  id | customer_id | ...  id | order_id | sku | qty
  1  | 42          | ...  1  | 1        | ... | 2
                                 ^ foreign key relationship, enforced by the database

NoSQL document store — flexible, no enforced cross-document schema:

  { "_id": 1, "customerId": 42, "items": [{"sku": "...", "qty": 2}] }
  // the order and its items live in ONE document — no separate table/join needed
```

**Go deeper:**

Most mainstream SQL databases, including PostgreSQL, also let you store a flexible JSON blob in a single column — Postgres's `jsonb` type is the common example — but that's a deliberate escape hatch for one column, not a way around the table having a fixed set of columns overall. What most NoSQL options actually trade away, relative to SQL, is some combination of strict schema enforcement, native multi-record joins, and, for many though not all, full ACID guarantees, in exchange for easier horizontal scaling or a data model that fits a specific access pattern more naturally. The right choice genuinely depends on the access pattern: a payments system almost always wants SQL's strong transactional guarantees, while a system needing to scale writes across many nodes might fit NoSQL better — and many real systems use both, deliberately, for different parts of the same system.

**Source:** [PostgreSQL Documentation](https://www.postgresql.org/docs/current/), [PostgreSQL Documentation — JSON Types](https://www.postgresql.org/docs/current/datatype-json.html), [MongoDB Documentation — Data Modeling Introduction](https://www.mongodb.com/docs/manual/core/data-modeling-introduction/)

---

### 15. What Is an API, and How Does It Differ From a Web Service?

**Answer:**

"An **API** (Application Programming Interface) is, in the broadest sense, any defined contract that lets one piece of software interact with another — a library's public method signatures are an API, an operating system's system calls are an API, and a network-accessible HTTP endpoint is *also* an API. The term itself doesn't imply network communication at all; it just means 'a defined interface for programs to talk to each other.' A **web service** is more specific: it's an API that's specifically accessible *over a network*, using standard web protocols, almost always HTTP. So a REST API — the subject of the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md) — is a web service, and a web service is a kind of API, but not every API is a web service, since a Java library's public class methods are an API you call in-process, with no network involved at all."

**Example:**

```text
API (broad umbrella — ANY defined interface between two pieces of software):

  - A Java library's public methods:        list.add(item);          <- in-process, NOT a web service
  - An operating system's system calls:      read(fd, buffer, size);  <- in-process, NOT a web service
  - An HTTP endpoint:                        GET /orders/123          <- OVER A NETWORK — this IS a web service

Web service = an API specifically exposed over a network via standard web protocols
```

**Go deeper:**

In casual, everyday engineering conversation, 'API' is very often used loosely to mean specifically 'a web service/HTTP endpoint,' since that's overwhelmingly the most common context the term comes up in day-to-day — but the precise relationship is that 'web service' is the narrower, network-specific term, and 'API' is the broader umbrella. Within "web service," there have historically been multiple competing styles — SOAP (XML-based, heavier, largely legacy in most new development today) and REST (resource-oriented, HTTP-native, the dominant modern style, covered in full depth in the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md)) — and GraphQL is a more recent third style, letting a client specify exactly the shape of data it wants in a single request rather than working against a fixed set of REST endpoints.

**Source:** [W3C — Web Services Architecture](https://www.w3.org/TR/ws-arch/)

---

## Data Structures & Algorithms

### 16. What Is a Stack, and What Is a Queue?

**Answer:**

"These are two of the most fundamental data structures, defined purely by their access order. A **stack** is LIFO — Last In, First Out — the most recently added element is always the first one removed, like a physical stack of plates: you add to the top and remove from the top. A **queue** is FIFO — First In, First Out — the first element added is the first one removed, like a line at a store: whoever got in line first gets served first. Both are used constantly in real systems: a stack models function-call bookkeeping and undo/redo functionality, while a queue models task processing in arrival order and any producer-consumer pipeline."

**Example:**

```text
STACK (LIFO) — push/pop from the SAME end:
  push(1) push(2) push(3)  ->  [1, 2, 3]
  pop() -> 3  (most recently added comes out FIRST)
  pop() -> 2

QUEUE (FIFO) — add at one end, remove from the other:
  enqueue(1) enqueue(2) enqueue(3)  ->  [1, 2, 3]
  dequeue() -> 1  (first added comes out FIRST)
  dequeue() -> 2
```

**Go deeper:**

The JVM's own call stack, covered in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md), works exactly like a stack — the most recently called function is the first one to return. A queue shows up concretely as `BlockingQueue` in a producer-consumer pipeline, covered in the [Java Concurrency guide](../Language/Java_Concurrency_Interview_Prep.md). Worth being precise about: "stack" as this data structure, a LIFO access order, is a completely different concept from "stack memory," the per-thread call-frame region — they share a name because stack memory happens to *behave* like the LIFO structure, but one is an abstract data type and the other is a specific region of a running program's memory.

**Source:** [MIT OpenCourseWare — Introduction to Algorithms, Stacks and Queues](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)

---

### 17. What's the Difference Between a Tree and a Graph?

**Answer:**

"Both are data structures built from **nodes** connected by **edges**, but a tree is a specific, more constrained kind of graph. A **tree** has exactly one root node, every other node has exactly one parent, there's exactly one path between any two nodes, and — critically — it has no cycles, meaning you can't follow edges and end up back where you started. A **graph** is the more general structure: nodes can connect to any number of other nodes in any pattern, cycles are allowed, and there's no requirement of a single root or a unique path between any two nodes at all. Put differently: every tree is technically a graph, a constrained, cycle-free, single-rooted one, but most graphs are not trees."

**Example:**

```text
TREE — one root, no cycles, exactly one path between any two nodes:
        A
       / \
      B   C
     /
    D

GRAPH — any connection pattern, cycles allowed, no single required root:
    A---B
    |   |
    C---D    (A-B-D-C-A is a CYCLE — impossible in a tree)
```

**Go deeper:**

Trees show up constantly in InterviewSmith — `TreeMap`/`TreeSet`'s red-black tree, covered in the [Java Collections guide](../Language/Java_Collections_Interview_Prep.md), and a database's B-tree index, covered later in this guide — while graphs model genuinely many-to-many relationships: a social network's connections, a service-dependency map in a microservices architecture, or the relationships a `@ManyToMany` mapping represents, covered in the [JPA & Hibernate guide](../Frameworks/JPA_Hibernate_Interview_Prep.md). Both are traversed via depth-first search, using a stack, or breadth-first search, using a queue, but graph traversal specifically needs to track **visited nodes** explicitly to avoid infinite loops around a cycle — a tree traversal never has to worry about that, since a tree's acyclic structure guarantees it can never revisit the same node.

**Source:** [MIT OpenCourseWare — Introduction to Algorithms, Graphs](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)

---

### 18. What Is Recursion, and What Is a Base Case?

**Answer:**

"Recursion is when a function solves a problem by calling *itself* on a smaller version of the same problem, progressively shrinking the problem until it reaches a case simple enough to answer directly, with no further recursive calls — that simplest, directly-answerable case is the **base case**. Without a correctly-defined base case, or with one that's never actually reached because of a logic error, a recursive function calls itself forever, which in practice means it keeps pushing new stack frames onto the call stack until it exhausts available stack space and throws `StackOverflowError`. Every correct recursive function needs exactly two things: a base case that terminates the recursion, and a recursive case that makes genuine progress toward that base case on every call."

**Example:**

```java
class Factorial {
    static int factorial(int n) {
        if (n <= 1) return 1;           // BASE CASE — no further recursion needed
        return n * factorial(n - 1);    // RECURSIVE CASE — smaller problem (n-1), makes progress
    }

    // factorial(5) unwinds as:
    //   5 * factorial(4)
    //     -> 4 * factorial(3)
    //          -> 3 * factorial(2)
    //               -> 2 * factorial(1)
    //                    -> 1  (BASE CASE reached — starts returning back up)
}
```

**Go deeper:**

Some languages automatically optimize a recursive call that's the very last operation in a function ('tail position') into a loop internally, avoiding growing the call stack at all — but the JVM does **not** perform this optimization, covered in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md), so a deeply recursive Java function, even a "tail-recursive-shaped" one, still risks `StackOverflowError` for large enough input. That's exactly why an iterative, loop-based rewrite is often the practical, production-safe choice for genuinely deep recursion in Java, rather than trusting the compiler to optimize it away the way it might in a language like Scheme or Scala.

**Source:** [MIT OpenCourseWare — Introduction to Algorithms, Recursion](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)

---

## Programming Languages & OOP

### 19. What Are the Four Pillars of Object-Oriented Programming?

**Answer:**

"**Encapsulation** means bundling an object's data together with the methods that operate on it, and restricting direct outside access to that data, usually with `private` fields and `public` methods, so the object controls how its own state is read or changed. **Inheritance** means a class can derive from, or extend, another class, automatically gaining its parent's fields and methods while adding or overriding its own. **Polymorphism** means objects of different classes can be treated through a common interface, and the *specific* behavior that actually runs is determined by the object's real, runtime type, not the declared type of the variable referring to it. **Abstraction** means exposing only the essential, relevant details of an object's behavior through a simplified interface, while hiding the complex implementation behind it, so a caller can use something correctly without needing to understand how it works internally."

**Example:**

```java
abstract class Shape {                 // ABSTRACTION — a simplified common interface
    abstract double area();             // callers don't need to know HOW each shape computes area
}

class Circle extends Shape {           // INHERITANCE — Circle IS-A Shape
    private double radius;              // ENCAPSULATION — radius is private, controlled access only

    Circle(double radius) { this.radius = radius; }

    @Override
    double area() { return Math.PI * radius * radius; } // POLYMORPHISM — Circle's OWN implementation
}

class Square extends Shape {
    private double side;
    Square(double side) { this.side = side; }
    @Override
    double area() { return side * side; }                // a DIFFERENT implementation, same method name
}

class ShapeDemo {
    public static void main(String[] args) {
        Shape s = new Circle(5);
        s.area(); // calls Circle's area() — determined by the ACTUAL object type, not the declared "Shape" type
    }
}
```

**Go deeper:**

These four aren't independent, unrelated rules — they reinforce each other: encapsulation is what makes abstraction possible, since hiding internals is how you expose only what's essential, and polymorphism is what makes inheritance genuinely useful beyond code reuse, letting different subclasses respond differently to the same method call. Spring's dependency injection, covered in the [Spring Boot Internals guide](../Frameworks/Spring_Boot_Internals_Interview_Prep.md), leans heavily on polymorphism and abstraction — injecting against an *interface* type, with the concrete implementation swappable. Overriding `equals()`/`hashCode()`, covered in the [Java Collections guide](../Language/Java_Collections_Interview_Prep.md), is a direct, everyday application of polymorphism.

**Source:** [Oracle Java Tutorials — Object-Oriented Programming Concepts](https://docs.oracle.com/javase/tutorial/java/concepts/index.html), [Oracle Java Tutorials — Polymorphism](https://docs.oracle.com/javase/tutorial/java/IandI/polymorphism.html)

---

### 20. What's the Difference Between a Compiled and an Interpreted Language?

**Answer:**

"A **compiled** language is translated, ahead of time, from source code into machine code, or another lower-level form, *before* the program ever runs — the compiler does this work once, upfront, producing an executable that runs directly on the hardware without needing the compiler present afterward (C and C++ are the classic examples). An **interpreted** language is translated and executed *at runtime* by a separate program, the interpreter, with no standalone machine-code executable produced ahead of time (classic Python and Ruby usage are common examples) — the interpreter has to be present every time the program runs. Java sits genuinely in between: Java source is compiled ahead of time, via `javac`, into an intermediate form called bytecode, but that bytecode is then interpreted, and for hot code paths further compiled to real machine code at runtime, by the JVM."

**Example:**

```text
COMPILED (e.g., C):
  source.c --[compiler, ONCE, ahead of time]--> machine code executable
  Running it later needs NO compiler present at all — just the executable.

INTERPRETED (e.g., classic Python usage):
  source.py --[compiled to bytecode (.pyc), THEN interpreted, at runtime]--> program behavior
  No standalone executable is produced — the interpreter must be present every run.

JAVA (genuinely BOTH, at different stages):
  source.java --[javac, ahead of time]--> bytecode (.class)
  bytecode --[JVM interprets, then JIT-compiles hot paths]--> actual execution
```

**Go deeper:**

This binary framing is an oversimplification for many modern languages — CPython, for instance, first compiles Python source into an internal bytecode representation, caching it in `.pyc` files, and it's *that* bytecode the interpreter actually executes, not the raw source text line-by-line, a milder version of the same blurring Java shows more clearly, covered in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md). Ahead-of-time compilation generally gives faster startup and predictable peak performance with no runtime translation overhead, while interpretation trades some raw performance for portability and development convenience. GraalVM's native-image compilation, mentioned in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md), applies ahead-of-time compilation to Java itself, trading the JIT's warmup-then-peak-throughput behavior for near-instant startup, useful for short-lived workloads like serverless functions.

**Source:** [Oracle Java Tutorials — javac and the JVM](https://docs.oracle.com/javase/tutorial/getStarted/intro/definition.html), [Python Glossary — bytecode](https://docs.python.org/3/glossary.html#term-bytecode)

---

### 21. What's the Difference Between Static and Dynamic Typing?

**Answer:**

"In a **statically-typed** language, like Java or C++, every variable's type is fixed and checked at **compile time** — the compiler verifies that every operation is valid for the declared types before the program ever runs, so a type mismatch, like assigning a `String` to an `int` variable, is a compile error, caught before deployment, not a runtime surprise. In a **dynamically-typed** language, like Python or JavaScript, a variable's type isn't fixed — the same variable name can hold an integer at one point and a string moments later — and type checking happens at **runtime**, as each operation actually executes, so a type mismatch only surfaces as an error when that specific line of code actually runs, potentially in production. Static typing catches a real class of bugs earlier, at the cheapest point to fix them; dynamic typing is more flexible and typically faster to write quickly."

**Example:**

```java
// Statically typed (Java) — caught at COMPILE TIME, before the program ever runs
int count = 5;
count = "hello"; // COMPILE ERROR — incompatible types, caught immediately, never even builds
```

```python
# Dynamically typed (Python) — no error until this specific line actually RUNS
count = 5
count = "hello"       # perfectly legal — count just now holds a string instead
result = count + 10   # RUNTIME error — only surfaces IF and WHEN this line executes
```

**Go deeper:**

Static typing also lets tooling, like IDEs and refactoring tools, reason precisely about a codebase, at the cost of more verbose declarations; dynamic typing's flexibility comes at the cost of type-related bugs only surfacing when the specific buggy code path actually executes, which is exactly why comprehensive test coverage matters even more in dynamically-typed codebases. TypeScript is a genuinely relevant, increasingly common middle ground: it adds an optional static type-checking layer on top of JavaScript, catching type errors at compile/build time while still compiling down to plain, dynamically-typed JavaScript for actual execution.

**Source:** [JLS §4 — Types, Values, and Variables](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html)

---

## Operating Systems

### 22. What Is an Operating System, and What Does the Kernel Do?

**Answer:**

"An operating system is the software layer that manages a computer's hardware resources — CPU, memory, storage, network devices — and provides a consistent, higher-level interface for applications to use those resources, without every single application needing to know how to directly control the underlying hardware itself. The **kernel** is the OS's core — the part with direct, privileged access to hardware, responsible for the most fundamental resource-management decisions: which process gets the CPU next (scheduling), which physical memory a process can access, and mediating every application's access to hardware devices. The kernel runs in a privileged execution mode ('kernel space') that regular application code ('user space') cannot directly access — an application requests kernel services, like reading a file or allocating memory, through a controlled interface called a **system call**, rather than touching hardware or protected memory directly."

**Example:**

```text
User space (applications):     Your Java app, a web browser, a text editor
                                   |
                                   |  system calls (read, write, malloc, etc.)
                                   v
Kernel space (privileged):     Process scheduling, memory management,
                                device drivers, filesystem, networking

User-space code CANNOT directly touch hardware or another process's memory —
it must go THROUGH the kernel via a system call, which enforces the boundary.
```

**Go deeper:**

This separation is a deliberate security and stability boundary, preventing one misbehaving application from corrupting the kernel or directly interfering with other applications' resources. The JVM itself is a user-space application running on top of the OS — when Java code allocates an object on the heap, the JVM, not the application code directly, is the one making the underlying system calls to request memory from the OS kernel. This OS-level process/memory management is a genuinely separate layer beneath everything the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md) covers about the JVM's *own* internal heap/stack/generation management.

**Source:** [Operating Systems: Three Easy Pieces — Remzi H. Arpaci-Dusseau & Andrea C. Arpaci-Dusseau](https://pages.cs.wisc.edu/~remzi/OSTEP/)

---

### 23. What Is Virtual Memory, and What Is Paging?

**Answer:**

"Virtual memory is an abstraction the OS provides so that every process believes it has its own large, private, contiguous address space, completely isolated from every other process's memory — even though the underlying physical RAM is actually a shared, finite resource split across every running process. The OS, with hardware support, translates each process's virtual addresses to actual physical memory addresses transparently, and this indirection is exactly what makes one process's memory bugs unable to directly corrupt another process's memory, or the kernel's own memory. **Paging** is the specific mechanism most modern OSes use to implement virtual memory: physical memory is divided into fixed-size chunks called **pages**, commonly 4KB, and a **page table** maps each virtual page to a physical page frame. A page not currently in active use can be swapped out to disk, freeing physical memory, and swapped back in the moment the process actually needs it again."

**Example:**

```text
Process A's virtual address space:        Physical RAM (shared, limited):
  [page 0] -----------> maps to -------->  [physical frame 12]
  [page 1] -----------> maps to -------->  [physical frame 4]
  [page 2] -----------> SWAPPED OUT to disk (not currently in physical RAM at all)

Process B's virtual address space:
  [page 0] -----------> maps to -------->  [physical frame 7]
  (Process B's "page 0" and Process A's "page 0" are DIFFERENT physical
   locations — each process's virtual address space is fully isolated)
```

**Go deeper:**

That swap-back-in moment is called a 'page fault,' and it's handled by the kernel. This is a genuinely different mechanism from a container's memory limit, worth not conflating: when a containerized JVM's memory footprint, heap plus metaspace plus thread stacks, covered in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md), exceeds the container's configured memory limit, the container runtime's OOM killer terminates the process — that's a *cgroup*-enforced limit sitting on top of this virtual-memory system, not the OS "running out of virtual memory."

**Source:** [Operating Systems: Three Easy Pieces — Paging chapters](https://pages.cs.wisc.edu/~remzi/OSTEP/)

---

### 24. What Is CPU Caching, and Why Does It Matter for Performance?

**Answer:**

"CPU caching is small, extremely fast memory built directly into, or very close to, the processor, sitting between the CPU and main RAM, holding copies of recently or frequently-accessed data so the CPU doesn't have to wait for the much slower trip to main memory on every single access. Modern CPUs have multiple cache levels — L1 (smallest, fastest, per-core), L2 (larger, still fast), L3 (largest, shared across all cores) — with main RAM as the much slower fallback if data isn't found in any cache level, called 'a cache miss.' This matters for performance because accessing data that's already in cache is dramatically faster than fetching it from RAM, and how a program lays out and accesses its data in memory can make a real, measurable difference to how often that happens."

**Example:**

```text
CPU  <-> L1 cache (~1ns access)   <- smallest, fastest, per-core
     <-> L2 cache (~4ns access)   <- larger, still fast
     <-> L3 cache (~15ns access)  <- largest, shared across cores
     <-> Main RAM (~100ns access) <- MUCH slower — the fallback on a cache miss

Sequential array access: elements are CONTIGUOUS in memory ->
  accessing element[0] pulls element[1], [2], [3]... into cache too (good locality)

Linked-list traversal: each node is a SEPARATE heap allocation, scattered in memory ->
  accessing each node is likely a FRESH cache miss — no benefit from the previous access
```

**Go deeper:**

This directly explains a genuinely counterintuitive result covered concretely in the [Java Collections guide](../Language/Java_Collections_Interview_Prep.md): `ArrayList`'s contiguous memory layout means sequentially accessing its elements tends to pull several useful elements into cache at once, good 'locality of reference,' while `LinkedList`'s scattered, individually-heap-allocated nodes mean each element access is likely a fresh cache miss requiring a trip to main memory. That's exactly why `LinkedList`'s theoretical Big-O insertion advantage often loses to `ArrayList` in real, measured performance, despite what the raw complexity analysis alone would suggest — for anything but very large `n`, cache-friendliness frequently dominates real-world performance more than asymptotic complexity does.

**Source:** [Operating Systems: Three Easy Pieces — Remzi H. Arpaci-Dusseau & Andrea C. Arpaci-Dusseau](https://pages.cs.wisc.edu/~remzi/OSTEP/)

---

## Databases

### 25. What Is Database Normalization, and What Do 1NF, 2NF, and 3NF Mean?

**Answer:**

"Normalization is the process of organizing a relational database's tables and columns to reduce data redundancy and avoid update, insert, and delete anomalies — situations where the same fact is stored in multiple places, and those copies can drift out of sync with each other. It's expressed as a series of increasingly strict rules called normal forms. **1NF (First Normal Form)**: every column holds a single, atomic value — no repeating groups or comma-separated lists crammed into one column. **2NF**: satisfies 1NF, and every non-key column depends on the *entire* primary key, not just part of it — relevant for tables with a composite key. **3NF**: satisfies 2NF, and no non-key column depends on *another non-key column* — storing both `zip_code` and `city` in an `orders` table, where `city` is actually determined by `zip_code`, is a classic 3NF violation, since updating one without the other risks them drifting out of sync."

**Example:**

```text
1NF VIOLATION: repeating values crammed into one column
  | order_id | items                        |
  | 1        | "widget, gadget, gizmo"       |   <- NOT atomic, violates 1NF

1NF FIX: a separate related table, one row per item
  orders: | order_id |          order_items: | order_id | item   |
          | 1        |                       | 1        | widget |
                                               | 1        | gadget |

3NF VIOLATION: city is TRANSITIVELY dependent on zip_code, not on order_id directly
  | order_id | zip_code | city     |
  | 1        | 10001    | New York |   <- storing BOTH here risks them drifting out of sync
```

**Go deeper:**

Fully normalized schemas minimize redundancy and anomaly risk, but every join required to reassemble related data back together at query time has a real performance cost. That's exactly why **denormalization** — deliberately reintroducing some redundancy, for read performance — is a legitimate, common trade-off for read-heavy workloads, not a mistake. The [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md)'s composite/aggregate-endpoint question and the general caching material in the [Redis & Caching guide](../System%20Design/Redis_Caching_Interview_Prep.md) both cover different angles of this same normalized-versus-denormalized trade-off.

**Source:** [MIT OpenCourseWare — Database, Internet, and Systems Integration Technologies, Data Normalization](https://ocw.mit.edu/courses/1-264j-database-internet-and-systems-integration-technologies-fall-2013/resources/mit1_264jf13_lect_11/)

---

### 26. What Is a Database Index, and Why Does It Speed Up Queries?

**Answer:**

"Without an index, finding rows matching a condition, like `WHERE email = 'alice@example.com'`, requires the database to scan every single row in the table, checking each one — a 'full table scan,' whose cost grows linearly with table size. An index is a separate, auxiliary data structure, typically a B-tree, a balanced, sorted tree structure, built on one or more columns, that lets the database jump almost directly to matching rows instead of scanning everything — turning a linear-time lookup into roughly logarithmic time. This isn't free: an index has to be **maintained** — kept up to date — on every `INSERT`, `UPDATE`, or `DELETE` affecting an indexed column, which adds real write overhead, and the index itself consumes additional storage space."

**Example:**

```sql
-- WITHOUT an index: full table scan — checks EVERY row
SELECT * FROM users WHERE email = 'alice@example.com';

-- Add an index on the column actually being filtered on:
CREATE INDEX idx_users_email ON users(email);

-- The SAME query now seeks directly via the index's B-tree structure,
-- instead of scanning every row in the table
SELECT * FROM users WHERE email = 'alice@example.com';
```

**Go deeper:**

The practical trade-off: indexes are worth adding for columns genuinely queried, filtered, or joined on frequently, especially in read-heavy workloads, but indexing every column reflexively "just in case" pays a real, ongoing write-performance and storage cost for indexes that may rarely, if ever, actually get used. The [JPA & Hibernate guide](../Frameworks/JPA_Hibernate_Interview_Prep.md) covers how an ORM can generate a query that's logically correct but doesn't actually use an available index efficiently — a function applied to the indexed column in the `WHERE` clause, for instance, can prevent the database from using a plain index on that column at all — which is why checking the actual generated SQL, not just assuming "I added an index, so it must be fast now," matters once a query is underperforming.

**Source:** [PostgreSQL Documentation — Indexes](https://www.postgresql.org/docs/current/indexes.html)

---

## Software Engineering Practices

### 27. What Is Version Control, and What Does Git Actually Track?

**Answer:**

"Version control is a system for tracking changes to a set of files over time, letting you see history, revert to a previous state, and, critically for team development, let multiple people work on the same codebase concurrently without simply overwriting each other's changes. Git is by far the dominant modern version control system, and it's specifically **distributed**: every clone of a repository has the *entire* project history locally, not just the current state, unlike older centralized systems that required contacting a central server for most operations. The detail worth knowing: Git doesn't track changes as a list of line-by-line diffs the way older systems conceptually do — it tracks a **series of snapshots**. Every commit is essentially a complete snapshot of every tracked file at that moment, though Git optimizes storage internally, avoiding literally duplicating unchanged files."

**Example:**

```bash
git init                          # start tracking a project
git add file.txt                  # stage a change for the next commit
git commit -m "Add feature"       # SNAPSHOT the current state of all staged files

git branch feature-x              # create an independent line of development
git checkout feature-x            # switch to it — work without affecting main
git merge feature-x                # bring feature-x's changes back into the current branch

# Every clone has the FULL history locally — no central server needed to view it:
git log
```

**Go deeper:**

That's a genuinely different underlying model from delta-based tracking used by older systems like Subversion or CVS, even though the day-to-day experience of writing and reviewing a `diff` looks similar either way. Branching strategy is the practical, team-level concern that sits on top of Git's own mechanics — trunk-based development, Git Flow, and various other conventions all answer the same underlying question, how multiple people's concurrent work gets integrated safely, differently, and it matters far more day-to-day than Git's internal snapshot-vs-delta model. A pull or merge request, the review gate most teams put in front of merging a branch, is a workflow convention layered on top of Git by hosting platforms like GitHub or GitLab, not a feature of Git itself.

**Source:** [Git — Getting Started: What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)

---

### 28. What's the Difference Between Unit, Integration, and End-to-End Tests?

**Answer:**

"These form what's commonly called the 'test pyramid,' differing in scope and what they're actually verifying. **Unit tests** verify a single, small unit of code, one method or one class, in isolation, with any external dependencies replaced by a mock or stub — they're fast, cheap to run in large numbers, and pinpoint exactly which unit broke when one fails. **Integration tests** verify that multiple units, or an application and a real external dependency like an actual database, work correctly *together* — slower than unit tests, but they catch a real category of bug unit tests structurally can't: two units that each pass their own unit tests in isolation, but don't actually integrate correctly together. **End-to-end (E2E) tests** verify a complete, real user-facing workflow through the *entire* running system — the slowest and most expensive of the three, but the closest to actually verifying 'does this work correctly for a real user.'"

**Example:**

```text
        /\
       /E2E\        <- FEW: slow, expensive, tests the whole real system end to end
      /------\
     /  Integ  \    <- SOME: tests real interaction between components/external systems
    /------------\
   /     Unit      \ <- MANY: fast, cheap, tests one isolated unit at a time
  /------------------\
```

**Go deeper:**

The 'pyramid' shape describes the recommended proportion: many fast unit tests as the foundation, a moderate number of integration tests, and comparatively few E2E tests — inverting that shape, many slow E2E tests, few unit tests, is a common, real anti-pattern that produces a slow, flaky, expensive-to-maintain test suite. E2E tests, by nature of exercising the entire real system, network calls, timing, a real browser, are inherently more prone to intermittent, non-deterministic failures unrelated to an actual bug, and a test suite dominated by flaky E2E tests erodes a team's trust in CI signal over time, since people start re-running failed builds reflexively rather than investigating.

**Source:** [Martin Fowler — The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| RFC 9293 — Transmission Control Protocol (TCP) | https://datatracker.ietf.org/doc/html/rfc9293 |
| RFC 768 — User Datagram Protocol (UDP) | https://datatracker.ietf.org/doc/html/rfc768 |
| RFC 1035 — Domain Names, Implementation and Specification | https://datatracker.ietf.org/doc/html/rfc1035 |
| IANA — Service Name and Transport Protocol Port Number Registry | https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml |
| RFC 3986 — URI Generic Syntax | https://datatracker.ietf.org/doc/html/rfc3986 |
| RFC 9110 — HTTP Semantics | https://datatracker.ietf.org/doc/html/rfc9110 |
| RFC 9112 — HTTP/1.1 | https://datatracker.ietf.org/doc/html/rfc9112 |
| RFC 9113 — HTTP/2 | https://datatracker.ietf.org/doc/html/rfc9113 |
| RFC 9114 — HTTP/3 | https://datatracker.ietf.org/doc/html/rfc9114 |
| NIST — Cryptographic Standards and Guidelines | https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines |
| NIST SP 800-107 — Approved Hash Algorithms | https://csrc.nist.gov/pubs/sp/800/107/r1/final |
| RFC 8446 — TLS 1.3 | https://datatracker.ietf.org/doc/html/rfc8446 |
| NIST SP 800-57 — Recommendation for Key Management | https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final |
| RFC 5280 — Internet X.509 Public Key Infrastructure Certificate | https://datatracker.ietf.org/doc/html/rfc5280 |
| MIT OpenCourseWare — Introduction to Algorithms | https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/ |
| PostgreSQL Documentation | https://www.postgresql.org/docs/current/ |
| PostgreSQL Documentation — JSON Types | https://www.postgresql.org/docs/current/datatype-json.html |
| MongoDB Documentation — Data Modeling Introduction | https://www.mongodb.com/docs/manual/core/data-modeling-introduction/ |
| W3C — Web Services Architecture | https://www.w3.org/TR/ws-arch/ |
| Oracle Java Tutorials — Object-Oriented Programming Concepts | https://docs.oracle.com/javase/tutorial/java/concepts/index.html |
| Oracle Java Tutorials — Polymorphism | https://docs.oracle.com/javase/tutorial/java/IandI/polymorphism.html |
| Oracle Java Tutorials — javac and the JVM | https://docs.oracle.com/javase/tutorial/getStarted/intro/definition.html |
| JLS §4 — Types, Values, and Variables | https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html |
| Python Glossary — bytecode | https://docs.python.org/3/glossary.html#term-bytecode |
| Operating Systems: Three Easy Pieces (Arpaci-Dusseau) | https://pages.cs.wisc.edu/~remzi/OSTEP/ |
| MIT OpenCourseWare — Database, Internet, and Systems Integration Technologies, Data Normalization | https://ocw.mit.edu/courses/1-264j-database-internet-and-systems-integration-technologies-fall-2013/resources/mit1_264jf13_lect_11/ |
| PostgreSQL Documentation — Indexes | https://www.postgresql.org/docs/current/indexes.html |
| Git — Getting Started: What is Git? | https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F |
| Martin Fowler — The Practical Test Pyramid | https://martinfowler.com/articles/practical-test-pyramid.html |
