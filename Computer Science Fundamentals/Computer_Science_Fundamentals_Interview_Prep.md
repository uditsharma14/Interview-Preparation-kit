# Computer Science Fundamentals — Interview Prep (Basic Level, with Code & Sources)

> **Target level:** Basic (foundational — no graduation to Staff in this guide; see "How to use this" below) · **Baseline:** HTTP semantics per RFC 9110, TLS 1.3 per RFC 8446, DNS per RFC 1035 · **Last verified:** 2026-08-23 · **Prerequisites:** none — this is the foundational layer the rest of this kit assumes

How to use this: unlike most guides in this kit, this one is deliberately **Basic-only** — networking, security, and general CS terminology genuinely foundational enough that every other guide here assumes it without re-explaining it. If a term in another guide (TLS, symmetric encryption, TCP, Big-O) isn't landing, it's worth checking here first. Each question has **the answer the way I'd actually say it out loud**, a **code/diagram snippet** to back it up, and a **Follow-up** pointing to where the *real* depth on that topic lives elsewhere in this kit — this guide intentionally stays shallow so those other guides don't have to re-teach the basics every time.

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

"Both are transport-layer protocols that sit on top of IP, but they make opposite trade-offs between reliability and speed. **TCP** (Transmission Control Protocol) is connection-oriented and reliable: before any data flows, client and server perform a handshake to establish a connection, and TCP guarantees delivered data arrives complete, in order, and without duplication — retransmitting anything lost and reassembling anything that arrived out of order. That reliability costs latency (the handshake itself, plus retransmission delays when packets are lost) and overhead (sequencing and acknowledgment bookkeeping on every packet).

**UDP** (User Datagram Protocol) is connectionless and makes no reliability guarantee at all — a packet ('datagram') is just fired off, with no handshake, no guaranteed delivery, no ordering, and no automatic retransmission. That sounds strictly worse, but it's exactly right for use cases where a lost or late packet is worthless anyway (a live video frame, a real-time game position update) and low latency matters more than perfect delivery — retransmitting a video frame that's already too old to display would be pure wasted effort."

**Code:**

```text
TCP: [SYN] -> [SYN-ACK] -> [ACK]  (handshake, THEN data flows)
     -> data packet 1 (acknowledged)
     -> data packet 2 (lost — automatically RETRANSMITTED)
     -> data packet 3 (acknowledged)
     Application sees: 1, 2, 3 — in order, complete, guaranteed

UDP: -> datagram 1 (delivered)
     -> datagram 2 (lost — GONE, no retransmission, no notification)
     -> datagram 3 (delivered)
     Application sees: 1, 3 — whatever arrived, in whatever order it arrived
```

**Follow-up:**

I'd mention that most application-layer protocols this kit covers are built on TCP — HTTP, and therefore essentially every REST API and web request in the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md), rides on TCP specifically because losing or reordering part of an API response would be unacceptable. UDP shows up more in specialized cases: DNS (covered next) uses UDP for its typically-small queries (falling back to TCP for larger responses), and QUIC — the transport HTTP/3 is built on, covered later in this guide — is UDP-based despite HTTP/3 still needing reliability, because QUIC reimplements reliability *itself* on top of UDP rather than using TCP, specifically to fix a TCP limitation covered in the HTTP/3 question.

**Source:** [RFC 9293 — Transmission Control Protocol (TCP)](https://datatracker.ietf.org/doc/html/rfc9293), [RFC 768 — User Datagram Protocol](https://datatracker.ietf.org/doc/html/rfc768)

---

### 2. What Is DNS, and How Does a Domain Name Resolve to an IP Address?

**Answer:**

"DNS (Domain Name System) is the internet's distributed, hierarchical directory that translates human-readable domain names (`example.com`) into the numeric IP addresses computers actually use to route traffic — nobody has to remember a server's IP address, just its name. Resolution happens through a chain of lookups: a client's DNS resolver (often run by the ISP or a public service like `8.8.8.8`) first asks a **root** nameserver, which doesn't know the answer but knows which **top-level-domain (TLD)** nameserver handles `.com`; that TLD nameserver, in turn, doesn't know the final answer either but knows which **authoritative** nameserver is responsible for `example.com` specifically; and that authoritative nameserver finally returns the actual IP address.

In practice, this full chain rarely runs on every single request — DNS responses are heavily **cached** at every layer (the browser, the OS, the resolver, intermediate nameservers) for a duration set by the record's TTL (time-to-live), which is exactly why DNS changes (pointing a domain at a new server) don't take effect everywhere instantly — some caches are still serving the old, cached answer until their TTL expires."

**Code:**

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

**Follow-up:**

I'd bring up DNS as a genuinely common source of confusing production incidents, worth knowing the shape of even at a basic level: a service migration that changes a domain's IP but forgets that DNS caching means some fraction of traffic keeps hitting the *old* IP until every cache layer's TTL expires, which is why a low TTL is often set deliberately *before* a planned migration (giving caches less time to hold a stale answer) rather than discovered as a problem during the migration itself.

**Source:** [RFC 1035 — Domain Names, Implementation and Specification](https://datatracker.ietf.org/doc/html/rfc1035)

---

### 3. What's the Difference Between an IP Address and a Port Number?

**Answer:**

"An **IP address** identifies a specific *machine* (or network interface) on a network — where to deliver a packet, at the level of 'which computer.' A **port number** identifies a specific *application/process* running on that machine — which of potentially many programs listening on that machine should actually receive the data. A single server might run a web server, a database, and an SSH daemon simultaneously, all reachable at the same IP address, distinguished only by which port each is listening on (conventionally 80/443 for HTTP/HTTPS, 5432 for PostgreSQL, 22 for SSH) — the IP address alone can't disambiguate between them.

Together, an IP address plus a port number form a **socket** — the actual endpoint a connection is made to (`93.184.216.34:443`), which is why a URL implicitly or explicitly includes a port (`https://example.com:8443/path` makes the port explicit; `https://example.com/path` implies the protocol's default port, 443 for HTTPS)."

**Code:**

```text
One machine, IP address 93.184.216.34, running THREE services simultaneously:

93.184.216.34:80    -> web server (HTTP)
93.184.216.34:443   -> web server (HTTPS)
93.184.216.34:5432  -> PostgreSQL database
93.184.216.34:22    -> SSH daemon

Same IP address for all four — the PORT is what routes an incoming
connection to the correct listening application on that machine.
```

**Follow-up:**

I'd mention that ports below 1024 are conventionally reserved as "well-known ports" (80, 443, 22, 5432 among them) and, on most operating systems, require elevated privileges to bind to — which is exactly why a web server sometimes needs to run as root (or, more safely, use a reverse proxy or capability grant) just to listen on port 80/443 directly, and why containerized services often listen on a higher, unprivileged port internally (8080) with the container platform mapping that to the standard external port instead, covered in the [Docker & Kubernetes guide](../Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md).

**Source:** [IANA — Service Name and Transport Protocol Port Number Registry](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml)

---

### 4. What's the Difference Between a URI, a URL, and a URN?

**Answer:**

"**URI** (Uniform Resource Identifier) is the umbrella term — any string that identifies a resource, full stop. **URL** (Uniform Resource Locator) and **URN** (Uniform Resource Name) are the two functional roles a URI can play, and the RFC's own framing is useful here: a URI can be a locator, a name, or both. A URL identifies a resource *and* tells you how to actually reach it — a scheme, a host, a path (`https://example.com/orders/123`) — you can act on it directly. A URN identifies a resource by a persistent, location-independent *name*, with no information about where to actually find it (`urn:isbn:0451450523` names a specific book by ISBN, regardless of which library, bookstore, or website might currently have a copy).

In everyday engineering conversation, 'URL' and 'URI' get used almost interchangeably, and that's rarely a real problem — URNs are comparatively rare in practice outside specific standardized-identifier contexts (ISBNs, some XML namespaces) — but the precise distinction is that every URL is a URI, not every URI is a URL, and URN is a different, non-overlapping way a URI can behave."

**Code:**

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

**Follow-up:**

I'd connect this directly to REST API design, since it's where this distinction actually shows up in practice: every REST endpoint discussed in the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md) (`GET /orders/123`) is really a URL — a locator that both identifies the `Order` resource and tells the client exactly how to fetch it — which is precisely the "URI as locator" role, not the "URI as pure name" role a URN plays; REST's resource-oriented design leans on URLs specifically because dereferenceability (being able to actually act on the identifier, not just name the thing) is the whole point.

**Source:** [RFC 3986 — Uniform Resource Identifier (URI): Generic Syntax](https://datatracker.ietf.org/doc/html/rfc3986)

---

## HTTP

### 5. What Is HTTP, and What Does It Mean That It's "Stateless"?

**Answer:**

"HTTP (HyperText Transfer Protocol) is the application-layer protocol that essentially the entire web — and virtually every REST API — is built on: a client sends a **request** (a method, a target resource, headers, optionally a body) to a server, and the server sends back a **response** (a status code, headers, optionally a body). It's a simple request/response model, not a persistent conversation the protocol itself remembers.

'Stateless' means the server doesn't retain any memory of previous requests from a given client, purely at the protocol level — each HTTP request must carry everything the server needs to understand and process it, since the server treats every request as if it's the very first one it's ever seen from that client. This is precisely why 'staying logged in' isn't something HTTP does for you automatically — it's built *on top of* HTTP, via a session cookie or a bearer token the client re-sends on every subsequent request, simulating continuity that the underlying protocol itself doesn't provide."

**Code:**

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

**Follow-up:**

I'd tie this directly to why session-based authentication and token-based authentication both exist as *application-layer* workarounds for statelessness, not protocol features — covered in real depth in the [Spring Security & OAuth2 guide](../Frameworks/Spring_Security_OAuth2_Interview_Prep.md)'s cookie/session and bearer-token questions — and that statelessness is actually a deliberate, valuable design choice for scalability, not an accidental limitation: a stateless server doesn't need to remember anything about which client it talked to previously, which is exactly what lets any request be routed to any server instance behind a load balancer, with no need for "sticky sessions" pinning a client to one specific backend server.

**Source:** [RFC 9110 — HTTP Semantics](https://datatracker.ietf.org/doc/html/rfc9110)

---

### 6. What's the Difference Between HTTP/1.1, HTTP/2, and HTTP/3?

**Answer:**

"**HTTP/1.1** sends requests as plain text over a TCP connection, and its major limitation is **head-of-line blocking**: while multiple requests can technically share one TCP connection, they're processed strictly one at a time in order — a slow response blocks every response queued behind it on that same connection, which is why browsers historically opened several parallel TCP connections per domain just to work around this. **HTTP/2** fixes that specific problem at the HTTP layer: it introduces binary framing and true **multiplexing** — many requests and responses can be interleaved concurrently over a single TCP connection, so one slow response no longer blocks the others behind it on the same connection.

**HTTP/3** goes a step further by replacing the transport underneath entirely: instead of TCP, it runs over **QUIC**, a UDP-based transport — this eliminates a *different*, lower-level head-of-line blocking problem that HTTP/2 still has (a single lost TCP packet blocks *every* multiplexed stream on that connection, since TCP itself guarantees strict in-order delivery across the whole connection); QUIC implements its own reliability *per-stream*, so one stream's lost packet no longer stalls the others."

**Code:**

```text
HTTP/1.1: one request/response processed at a time PER connection
          [req A] --wait for response A--> [req B] --wait--> [req C]
          (workaround: browsers open several parallel TCP connections)

HTTP/2:   many requests MULTIPLEXED over ONE TCP connection
          [req A, req B, req C all in flight simultaneously, interleaved]
          BUT: one lost TCP packet still blocks ALL streams (TCP-level HOL blocking)

HTTP/3:   runs over QUIC (UDP-based) instead of TCP
          [req A, req B, req C multiplexed, EACH with its own independent reliability]
          A lost packet on stream B does NOT block streams A or C
```

**Follow-up:**

I'd mention that HTTP/2 and HTTP/3 are both essentially transparent to application code written against a standard HTTP client/server library — a Spring Boot REST controller doesn't need to know or care which HTTP version actually carried a given request, since the version negotiation and framing differences are handled entirely at the transport/protocol layer beneath the application. What *does* change in practice is deployment and infrastructure configuration (TLS is effectively mandatory for HTTP/2 and HTTP/3 in virtually every real deployment, even though the spec doesn't strictly require it for HTTP/2) and performance characteristics under real-world packet loss, not anything about how you'd design a REST API's resources or semantics, covered in the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md).

**Source:** [RFC 9113 — HTTP/2](https://datatracker.ietf.org/doc/html/rfc9113), [RFC 9114 — HTTP/3](https://datatracker.ietf.org/doc/html/rfc9114)

---

### 7. What Do the HTTP Status Code Categories (1xx–5xx) Mean, at a Glance?

**Answer:**

"HTTP status codes are grouped into five categories by their first digit, and knowing the *category* meaning is genuinely more useful day-to-day than memorizing every individual code. **1xx (Informational)** — the request was received and processing continues; rare to encounter directly in application code (`100 Continue` is the main one, used internally by clients/servers negotiating a large request body). **2xx (Success)** — the request was received, understood, and accepted (`200 OK`, `201 Created`, `204 No Content`). **3xx (Redirection)** — further action is needed to complete the request, typically following a different URL (`301 Moved Permanently`, `302 Found`). **4xx (Client Error)** — the request itself has a problem the *client* needs to fix (`400 Bad Request`, `401 Unauthorized`, `404 Not Found`). **5xx (Server Error)** — the request was valid, but the *server* failed to fulfill it (`500 Internal Server Error`, `503 Service Unavailable`).

The 4xx-versus-5xx distinction is the single most operationally useful one: a spike in 4xx responses usually means clients are doing something wrong (a buggy client, a bad integration, expired credentials), while a spike in 5xx responses means the *server* is broken — very different signals for very different on-call responses, which is exactly why 4xx/5xx rates are tracked as separate, distinct metrics in almost any production monitoring setup."

**Code:**

```text
1xx  Informational   100 Continue
2xx  Success          200 OK · 201 Created · 204 No Content
3xx  Redirection      301 Moved Permanently · 302 Found · 304 Not Modified
4xx  Client Error     400 Bad Request · 401 Unauthorized · 403 Forbidden · 404 Not Found · 429 Too Many Requests
5xx  Server Error     500 Internal Server Error · 502 Bad Gateway · 503 Service Unavailable
```

**Follow-up:**

I'd point toward the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md)'s dedicated question for exactly when to use which *specific* code within these categories (`200` vs. `201` vs. `202` vs. `204`, `400` vs. `409` vs. `422`) — that's real design nuance beyond what this foundational overview covers — and the [Spring Security & OAuth2 guide](../Frameworks/Spring_Security_OAuth2_Interview_Prep.md)'s treatment of the specific, commonly-confused `401` (not authenticated) versus `403` (authenticated, but not authorized) distinction within the 4xx category.

**Source:** [RFC 9110 §15 — HTTP Status Codes](https://datatracker.ietf.org/doc/html/rfc9110#section-15)

---

### 8. What's the Difference Between an HTTP Header and the Request/Response Body?

**Answer:**

"**Headers** are metadata *about* the request or response — key-value pairs describing things like content type (`Content-Type: application/json`), authentication credentials (`Authorization: Bearer ...`), caching directives (`Cache-Control: no-cache`), or the response's size (`Content-Length`) — information a client or server (or an intermediary like a proxy or CDN) needs in order to correctly *handle* the message, without necessarily needing to parse or understand the actual payload itself. The **body** is the actual payload/content being transferred — the JSON representing an order, the HTML of a web page, the bytes of an uploaded image.

Not every request or response has a body at all — a `GET` request typically has none (there's nothing to send, only something being asked for), and a `204 No Content` response explicitly has none by definition — but every request and response has headers, even if just a couple of basic ones, since headers are what make the message meaningfully interpretable in the first place."

**Code:**

```http
POST /orders HTTP/1.1                    <- request line
Host: example.com                          <- HEADER
Content-Type: application/json              <- HEADER: "the body is JSON"
Authorization: Bearer eyJhbGc...             <- HEADER: credentials
Content-Length: 47                            <- HEADER: "the body is 47 bytes"

{"sku": "WIDGET-1", "quantity": 2}          <- BODY: the actual payload
```

**Follow-up:**

I'd mention that headers are exactly where a lot of the mechanisms covered elsewhere in this kit actually live — idempotency keys, rate-limit signals (`RateLimit-Remaining`), `ETag`/`If-Match` for optimistic concurrency, `Deprecation`/`Sunset` for API lifecycle management, all covered in depth in the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md) — headers are the standard, HTTP-native place to carry structured metadata that intermediaries (caches, gateways, proxies) can act on without needing to parse and understand the request/response body at all.

**Source:** [RFC 9110 §6 — Message Content](https://datatracker.ietf.org/doc/html/rfc9110#section-6), [RFC 9110 §5 — Field Values (Headers)](https://datatracker.ietf.org/doc/html/rfc9110#section-5)

---

## Encryption & Security

### 9. What Is Encryption, and What's the Difference Between Symmetric and Asymmetric Encryption?

**Answer:**

"Encryption transforms readable data ('plaintext') into unreadable data ('ciphertext') using a key, such that only someone with the correct key can reverse the transformation and recover the original plaintext — the whole point is that data can be safely stored or transmitted somewhere an attacker might see it, without the attacker being able to actually read it.

**Symmetric encryption** uses the exact same key for both encrypting and decrypting — fast and computationally cheap, which makes it the right choice for encrypting large amounts of data (AES is the standard modern symmetric algorithm), but it has a real practical problem: both parties need the *same* secret key, so that key has to be shared between them somehow, securely, before any encrypted communication can happen at all — and if that key-sharing step itself isn't secure, the whole scheme is compromised. **Asymmetric encryption** (public-key cryptography) uses a *pair* of mathematically related keys: a public key (freely shareable with anyone) and a private key (kept secret, never shared) — data encrypted with the public key can only be decrypted with the corresponding private key. This solves the key-distribution problem symmetric encryption has (the public key can be shared openly, with no secure channel needed), but it's computationally far more expensive than symmetric encryption, which is exactly why real-world systems (TLS, covered next) typically use asymmetric encryption only briefly, to securely exchange a symmetric key, then switch to fast symmetric encryption for the actual bulk data."

**Code:**

```text
SYMMETRIC (e.g., AES): ONE shared secret key, used for both directions
  Alice: plaintext --[key K]--> ciphertext  --sends ciphertext-->  Bob: ciphertext --[key K]--> plaintext
  Problem: Alice and Bob both need key K — how do they exchange K securely in the first place?

ASYMMETRIC (e.g., RSA): a KEY PAIR — public key (shareable) + private key (secret)
  Alice encrypts with Bob's PUBLIC key --sends ciphertext--> Bob decrypts with his OWN PRIVATE key
  No shared secret ever needs to be exchanged — Bob's public key can be posted anywhere openly
```

**Follow-up:**

I'd bring up the practical hybrid approach directly, since it's what virtually every real secure system actually does rather than picking purely one or the other: use asymmetric encryption briefly, just to securely establish a shared symmetric key between two parties who've never communicated before, then switch to fast symmetric encryption for the actual bulk of the data — this is exactly what happens inside a TLS handshake, covered next, and it's the reason HTTPS can encrypt an entire web session's worth of data without paying asymmetric encryption's much higher computational cost for every single byte transferred.

**Source:** [NIST — Cryptographic Standards and Guidelines](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines)

---

### 10. What's the Difference Between Encryption and Hashing?

**Answer:**

"Encryption is explicitly **reversible**, given the right key — that's the entire point, since the legitimate recipient needs to recover the original plaintext. Hashing is explicitly **one-way**: a hash function takes an input of any size and produces a fixed-size output (a 'digest'), but there's no key and no way to reverse the process to recover the original input from the digest alone — a good cryptographic hash function is specifically *designed* to make that infeasible.

They solve fundamentally different problems, which is why confusing them is a real, consequential mistake, not just imprecise terminology: encryption is for *confidentiality* — protecting data so only someone with the key can read it, while still being able to recover the original data when needed. Hashing is for *integrity and verification* — proving data hasn't changed (comparing a file's hash against a known-good hash) or verifying a match without ever needing to store or recover the original value at all, which is exactly why passwords are **hashed**, never merely encrypted: the application should never need to recover a user's actual plaintext password — it only ever needs to verify that a freshly-submitted password produces the same hash as the one stored at registration time, covered in depth in the [Spring Security & OAuth2 guide](../Frameworks/Spring_Security_OAuth2_Interview_Prep.md)'s `BCryptPasswordEncoder` question."

**Code:**

```text
ENCRYPTION (reversible, with the right key):
  plaintext "hello" --[encrypt with key K]--> ciphertext "x7Gk..." --[decrypt with key K]--> "hello"

HASHING (one-way, no key involved at all):
  "hello" --[hash function]--> "2cf24dba5fb0a30e..."
  There is NO operation that takes "2cf24dba..." and recovers "hello" — it's not reversible by design.

  Verifying a password: hash("submitted-password") == stored-hash ?
  The application NEVER decrypts anything to check this — there's nothing to decrypt.
```

**Follow-up:**

I'd flag the specific, common confusion this question is testing: "should we encrypt passwords or hash them" is actually a trick framing, since the correct answer (hash them, with a purpose-built slow algorithm like bcrypt) reflects that the application should genuinely *never* be able to recover a user's actual password at all — not even the application's own operators, not even with full database access — which is a stronger, more defensible security property than "encrypted, but technically recoverable by whoever holds the encryption key."

**Source:** [NIST SP 800-107 — Recommendation for Applications Using Approved Hash Algorithms](https://csrc.nist.gov/pubs/sp/800/107/r1/final)

---

### 11. What Is TLS, and How Does the Handshake Establish a Secure Connection?

**Answer:**

"TLS (Transport Layer Security, the modern successor to SSL) is the protocol that encrypts a connection between a client and server — HTTPS is simply HTTP running over a TLS-encrypted connection instead of a plain one. Before any actual application data flows, TLS runs a **handshake** that accomplishes two things: the client verifies the server is genuinely who it claims to be (via the server's digital certificate, covered next), and both sides agree on a shared symmetric key for the rest of the session — combining exactly the asymmetric-then-symmetric pattern from the encryption question earlier in this guide.

In TLS 1.3 (the current version), the handshake is deliberately streamlined compared to older TLS versions specifically to reduce connection-setup latency: the client and server can typically agree on a shared key and start exchanging encrypted application data after just one round trip, rather than the several round trips earlier TLS versions required — a real, measurable improvement for anything latency-sensitive, since every additional handshake round trip directly adds to how long a user waits before a page starts loading."

**Code:**

```text
TLS 1.3 handshake (simplified):

1. Client -> Server: "Here are the encryption algorithms I support, and my key-exchange info"
2. Server -> Client: "Here's my certificate (proving who I am), my chosen algorithm,
                      my key-exchange info, and a computed shared secret"
   -- at this point, both sides can independently compute the SAME symmetric key --
3. Client verifies the server's certificate (via the CA chain, covered next),
   then both sides switch to fast SYMMETRIC encryption using that shared key
   for the actual application data (the real HTTP request/response)

Only ~1 round trip needed before encrypted application data can start flowing.
```

**Follow-up:**

I'd connect this directly back to the [Spring Security & OAuth2 guide](../Frameworks/Spring_Security_OAuth2_Interview_Prep.md)'s treatment of why HTTPS is a hard prerequisite for every authentication mechanism it covers — Basic Auth, form login, bearer tokens — since none of those mechanisms protect credentials *in transit* on their own; TLS is specifically what's doing that job underneath, and understanding the handshake here is what makes it clear *why* base64-encoding or hashing credentials isn't a substitute for actual transport encryption.

**Source:** [RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3](https://datatracker.ietf.org/doc/html/rfc8446)

---

### 12. What Is a Digital Certificate, and What Role Does a Certificate Authority Play?

**Answer:**

"A digital certificate is a file that binds a public key to an identity (a domain name, an organization) and is itself digitally signed by a trusted third party vouching that the binding is genuine — it's how a client can trust that the public key it's about to use during a TLS handshake actually belongs to `example.com`, and not to an attacker impersonating `example.com`. Without this, asymmetric encryption alone doesn't prevent impersonation: anyone can generate a public/private key pair and claim to be `example.com`; a certificate is what lets a client verify that claim rather than just trusting it blindly.

A **Certificate Authority (CA)** is that trusted third party — an organization (Let's Encrypt, DigiCert, and others) that verifies a domain's ownership before issuing a certificate for it, and whose own signing key is itself trusted by essentially every browser and operating system out of the box (pre-installed as a 'root certificate'). When a browser receives a server's certificate during a TLS handshake, it checks that the certificate was signed by a CA it already trusts (following a **chain of trust** from the server's certificate up through one or more intermediate certificates to a trusted root) — if that chain checks out, the browser trusts the server's identity; if the certificate is expired, self-signed without being explicitly trusted, or signed by an unrecognized authority, the browser shows the familiar 'connection is not private' warning."

**Code:**

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
If the chain is broken, expired, or ends at an unrecognized root -> WARNING.
```

**Follow-up:**

I'd mention Let's Encrypt specifically as a genuinely significant, relatively recent shift in this space: it offers free, automatable certificate issuance (via the ACME protocol), which meaningfully lowered the barrier to universal HTTPS adoption across the web compared to the earlier era of paid, manually-issued certificates — most modern deployment pipelines (including typical Kubernetes ingress setups, covered in the [Docker & Kubernetes guide](../Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md)) now provision and renew TLS certificates automatically via exactly this kind of mechanism, rather than as a manual, infrequent operational task.

**Source:** [NIST SP 800-57 — Recommendation for Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final), [RFC 5280 — Internet X.509 Public Key Infrastructure Certificate](https://datatracker.ietf.org/doc/html/rfc5280)

---

## General CS & Software Terminology

### 13. What Is Big-O Notation, and Why Does It Matter?

**Answer:**

"Big-O notation describes how an algorithm's resource usage (time, or sometimes memory) grows as the size of its input (conventionally called `n`) grows — it's specifically about the *growth rate/trend*, not an exact measurement of real-world speed for any particular input size. `O(1)` (constant time) means the operation takes roughly the same time regardless of how large the input is (a hash map lookup, on average). `O(n)` (linear time) means the work grows proportionally with input size (scanning every element of a list once). `O(log n)` (logarithmic time) means the work grows very slowly as input size increases (a binary search, or navigating a balanced tree) — doubling the input size adds only a small, roughly constant amount of extra work. `O(n²)` (quadratic time) means the work grows with the *square* of the input size (a naive nested loop comparing every pair of elements) — this gets expensive very fast as input grows.

Big-O matters because an algorithm that looks fine in testing (small `n`) can become a genuine production problem at real scale (large `n`) if its growth rate is bad — an `O(n²)` algorithm that's imperceptibly slow for 100 items can become unusably slow for 100,000, which is exactly the kind of gap between 'works in dev' and 'falls over in production' this notation exists to help reason about *before* it becomes an incident."

**Code:**

```java
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

**Follow-up:**

I'd connect this directly to concrete examples elsewhere in this kit rather than leaving it purely abstract — the [Java Collections guide](../Language/Java_Collections_Interview_Prep.md) covers exactly this kind of trade-off repeatedly and concretely (`ArrayList.get()` is O(1), `LinkedList.get()` is O(n); `HashMap` operations are O(1) average, `TreeMap` operations are O(log n)) — and I'd mention that Big-O specifically describes the *worst case* (or sometimes average case, depending on context) asymptotic behavior, not a guarantee about any single specific run, which is why two algorithms with the same Big-O complexity can still have meaningfully different real-world performance due to constant factors Big-O deliberately ignores.

**Source:** [MIT OpenCourseWare — Introduction to Algorithms, Asymptotic Notation](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)

---

### 14. What's the Difference Between SQL and NoSQL Databases?

**Answer:**

"**SQL (relational) databases** (PostgreSQL, MySQL) store data in tables with a fixed, predefined schema — every row in a table has the same set of columns, relationships between tables are expressed via foreign keys, and the database enforces the schema and referential integrity for you. They're queried with SQL, support complex multi-table joins natively, and virtually all of them provide strong ACID transaction guarantees, covered in depth in the [Transactions guide](../System%20Design/Transactions_Interview_Prep.md).

**NoSQL** is a broad umbrella term covering several genuinely different data models, not one single alternative to SQL: **document stores** (MongoDB) store flexible, JSON-like documents with no enforced schema across documents; **key-value stores** (Redis, covered in depth in the [Redis & Caching guide](../System%20Design/Redis_Caching_Interview_Prep.md)) store simple key-to-value pairs, optimized for extremely fast lookups; **wide-column stores** (Cassandra) are built for very high write throughput across huge, horizontally-distributed datasets; **graph databases** (Neo4j) are optimized specifically for traversing richly-interconnected relationships. What most NoSQL options actually trade away, relative to a traditional SQL database, is some combination of strict schema enforcement, native multi-record join support, and (for many, though not all) full ACID guarantees — in exchange for easier horizontal scaling, more flexible/evolvable schemas, or a data model that fits a specific access pattern more naturally than tables and joins would."

**Code:**

```text
SQL (relational) — fixed schema, tables, foreign keys, joins, strong ACID:

  orders table:           order_items table:
  id | customer_id | ...  id | order_id | sku | qty
  1  | 42          | ...  1  | 1        | ... | 2
                                 ^ foreign key relationship, enforced by the database

NoSQL document store — flexible, no enforced cross-document schema:

  { "_id": 1, "customerId": 42, "items": [{"sku": "...", "qty": 2}] }
  // the order and its items live in ONE document — no separate table/join needed,
  // and a different document in the same collection could have a different shape
```

**Follow-up:**

I'd give the practical decision framing rather than presenting this as "NoSQL is more modern/better": the right choice genuinely depends on the actual access pattern and consistency requirements — a payments/financial system almost always wants a SQL database's strong transactional guarantees (covered in the [Transactions guide](../System%20Design/Transactions_Interview_Prep.md)), while a system needing to horizontally scale writes across many nodes with a simpler, more flexible data model might be a better fit for a NoSQL option — and I'd mention that many real production systems use *both*, deliberately, for different parts of the same system, rather than treating it as an all-or-nothing architectural commitment.

**Source:** [PostgreSQL Documentation](https://www.postgresql.org/docs/current/), [MongoDB Documentation — Data Modeling Introduction](https://www.mongodb.com/docs/manual/core/data-modeling-introduction/)

---

### 15. What Is an API, and How Does It Differ From a Web Service?

**Answer:**

"An **API** (Application Programming Interface) is, in the broadest sense, any defined contract that lets one piece of software interact with another — a library's public method signatures are an API, an operating system's system calls are an API, and a network-accessible HTTP endpoint is *also* an API. The term itself doesn't imply network communication at all; it just means 'a defined interface for programs to talk to each other,' whatever form that takes.

A **web service** is more specific: it's an API that's specifically accessible *over a network*, using standard web protocols (almost always HTTP). So a REST API — the subject of the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md) — is a web service, and a web service is a kind of API, but not every API is a web service (a Java library's public class methods are an API you call in-process, with no network involved at all). In casual, everyday engineering conversation, 'API' is very often used loosely to mean specifically 'a web service/HTTP endpoint,' since that's overwhelmingly the most common context the term comes up in day-to-day — but the precise relationship is that 'web service' is the narrower, network-specific term, and 'API' is the broader umbrella."

**Code:**

```text
API (broad umbrella — ANY defined interface between two pieces of software):

  - A Java library's public methods:        list.add(item);          <- in-process, NOT a web service
  - An operating system's system calls:      read(fd, buffer, size);  <- in-process, NOT a web service
  - An HTTP endpoint:                        GET /orders/123          <- OVER A NETWORK — this IS a web service

Web service = an API specifically exposed over a network via standard web protocols
```

**Follow-up:**

I'd mention that within "web service," there have historically been multiple competing styles — SOAP (XML-based, heavier, with a formal contract language called WSDL, largely legacy in most new development today) and REST (resource-oriented, HTTP-native, the dominant modern style, covered in full depth in the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md)) — and that GraphQL is a more recent third style worth knowing exists, letting a client specify exactly the shape of data it wants in a single request rather than working against a fixed set of REST endpoints, with its own real trade-offs covered in that same guide's discussion of REST versus GraphQL.

**Source:** [W3C — Web Services Architecture](https://www.w3.org/TR/ws-arch/)

---

## Data Structures & Algorithms

### 16. What Is a Stack, and What Is a Queue?

**Answer:**

"These are two of the most fundamental abstract data types, defined purely by their access order, independent of any specific language's implementation. A **stack** is LIFO — Last In, First Out — the most recently added element is always the first one removed, like a physical stack of plates: you add to the top and remove from the top. A **queue** is FIFO — First In, First Out — the first element added is the first one removed, like a line at a store: whoever got in line first gets served first.

Both are used constantly in real systems: a stack models function-call bookkeeping (the JVM's own call stack, covered in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md), works exactly this way — the most recently called function is the first one to return), undo/redo functionality, and depth-first traversal; a queue models task processing in arrival order, breadth-first traversal, and any producer-consumer pipeline, covered concretely with `BlockingQueue` in the [Java Concurrency guide](../Language/Java_Concurrency_Interview_Prep.md)."

**Code:**

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

**Follow-up:**

I'd flag "stack" specifically as overloaded terminology worth being precise about: this data-structure meaning (LIFO access order) is a completely different concept from "stack memory" (the per-thread call-frame region covered in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md)) — they share a name because stack memory happens to *behave* like the LIFO data structure (frames are pushed and popped in strict call/return order), but one is an abstract data type and the other is a specific region of a running program's memory; conflating them in an answer is a common, easy-to-avoid mix-up.

**Source:** [MIT OpenCourseWare — Introduction to Algorithms, Stacks and Queues](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)

---

### 17. What's the Difference Between a Tree and a Graph?

**Answer:**

"Both are data structures built from **nodes** connected by **edges**, but a tree is a specific, more constrained kind of graph. A **tree** has exactly one root node, every other node has exactly one parent, there's exactly one path between any two nodes, and — critically — it has no cycles (you can't follow edges and end up back where you started). A **graph** is the more general structure: nodes can connect to any number of other nodes in any pattern, cycles are allowed, and there's no requirement of a single root or a unique path between any two nodes at all.

Put differently: every tree is technically a graph (a constrained, cycle-free, single-rooted one), but most graphs are not trees. Trees show up constantly in this kit — `TreeMap`/`TreeSet`'s red-black tree (covered in the [Java Collections guide](../Language/Java_Collections_Interview_Prep.md)), a database's B-tree index (covered later in this guide) — while graphs model genuinely many-to-many relationships: a social network's connections, a service-dependency map in a microservices architecture, or the entity-relationship graph a `@ManyToMany` mapping represents (covered in the [JPA & Hibernate guide](../Frameworks/JPA_Hibernate_Interview_Prep.md))."

**Code:**

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

**Follow-up:**

I'd mention that this distinction matters directly for traversal strategy: both trees and graphs are traversed via depth-first search (DFS, using a stack — explicitly or via recursion's own call stack) or breadth-first search (BFS, using a queue), but graph traversal specifically needs to track **visited nodes** explicitly to avoid infinite loops around a cycle, which a tree traversal never has to worry about at all, since a tree's acyclic structure guarantees a traversal can never revisit the same node by construction.

**Source:** [MIT OpenCourseWare — Introduction to Algorithms, Graphs](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)

---

### 18. What Is Recursion, and What Is a Base Case?

**Answer:**

"Recursion is when a function solves a problem by calling *itself* on a smaller version of the same problem, progressively shrinking the problem until it reaches a case simple enough to answer directly without any further recursive calls — that simplest, directly-answerable case is the **base case**. Without a correctly-defined base case (or with one that's never actually reached because of a logic error), a recursive function calls itself forever, which in practice means it keeps pushing new stack frames onto the call stack until it exhausts available stack space and throws `StackOverflowError`, covered in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md).

Every correct recursive function needs exactly two things: a base case that terminates the recursion, and a recursive case that makes genuine progress toward that base case on every call (not the same problem size again, or the recursion never terminates even with a technically-correct base case defined)."

**Code:**

```java
// Classic example: factorial
int factorial(int n) {
    if (n <= 1) return 1;           // BASE CASE — no further recursion needed
    return n * factorial(n - 1);    // RECURSIVE CASE — smaller problem (n-1), makes progress
}

factorial(5) 
  -> 5 * factorial(4)
       -> 4 * factorial(3)
            -> 3 * factorial(2)
                 -> 2 * factorial(1)
                      -> 1  (BASE CASE reached — starts returning back up)
```

**Follow-up:**

I'd bring up tail recursion and its practical limitation in Java specifically: some languages automatically optimize a recursive call that's the very last operation in a function ('tail position') into a loop internally, avoiding growing the call stack at all — but the JVM does **not** perform this optimization, so a deeply recursive Java function, even a "tail-recursive-shaped" one, still risks `StackOverflowError` for large enough input, which is exactly why an iterative (loop-based) rewrite is often the practical, production-safe choice for genuinely deep recursion in Java, rather than trusting the compiler to optimize it away the way it might in a language like Scheme or Scala.

**Source:** [MIT OpenCourseWare — Introduction to Algorithms, Recursion](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)

---

## Programming Languages & OOP

### 19. What Are the Four Pillars of Object-Oriented Programming?

**Answer:**

"**Encapsulation** — bundling an object's data (fields) together with the methods that operate on it, and restricting direct external access to that data (via `private` fields and `public` methods), so the object controls how its own state can be read or changed rather than exposing raw internals for anyone to mutate freely. **Inheritance** — a class can derive from (extend) another class, automatically gaining its parent's fields and methods while adding or overriding its own, letting a hierarchy of related types share common behavior without duplicating it. **Polymorphism** — objects of different classes can be treated through a common interface/supertype, and the *specific* behavior that actually runs is determined by the object's real, runtime type, not the declared type of the variable referring to it ('virtual method invocation'). **Abstraction** — exposing only the essential, relevant details of an object's behavior through a simplified interface, while hiding the complex implementation details behind it, so a caller can use something correctly without needing to understand how it works internally.

These four aren't independent, unrelated rules — they reinforce each other: encapsulation is what makes abstraction possible (hiding internals is how you expose only what's essential), and polymorphism is what makes inheritance genuinely useful beyond code reuse (letting different subclasses respond differently to the same method call)."

**Code:**

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

Shape s = new Circle(5);
s.area(); // calls Circle's area() — determined by the ACTUAL object type, not the declared "Shape" type
```

**Follow-up:**

I'd connect this directly to where these pillars show up throughout the rest of this kit rather than leaving them purely theoretical: Spring's dependency injection (covered in the [Spring Boot Internals guide](../Frameworks/Spring_Boot_Internals_Interview_Prep.md)) leans heavily on polymorphism and abstraction — injecting a class against an *interface* type, with the concrete implementation swappable, is exactly the "program to the abstraction, not the implementation" principle these pillars enable; and `equals()`/`hashCode()` overriding, covered in the [Java Collections guide](../Language/Java_Collections_Interview_Prep.md), is a direct, everyday application of polymorphism — a collection calling `equals()` on an object gets whatever behavior that object's *actual* class defines, not `Object`'s default.

**Source:** [Oracle Java Tutorials — Object-Oriented Programming Concepts](https://docs.oracle.com/javase/tutorial/java/concepts/index.html), [Oracle Java Tutorials — Polymorphism](https://docs.oracle.com/javase/tutorial/java/IandI/polymorphism.html)

---

### 20. What's the Difference Between a Compiled and an Interpreted Language?

**Answer:**

"A **compiled** language is translated, ahead of time, from source code directly into machine code (or another lower-level form) *before* the program ever runs — the compiler does the translation work once, upfront, producing an executable that runs directly on the target hardware without needing the original source code or the compiler present at runtime (C and C++ are the classic examples). An **interpreted** language is translated and executed line-by-line (or statement-by-statement) *at runtime*, by a separate program (the interpreter) that reads the source and carries out its instructions on the fly, with no separate compilation step producing a standalone executable (classic Python and Ruby usage are common examples).

In practice, this binary compiled-vs-interpreted framing is an oversimplification for many modern languages, including Java specifically — Java source is *compiled* (via `javac`) to an intermediate form (bytecode), but that bytecode is then *interpreted* (and, for hot code paths, further JIT-compiled to real machine code at runtime) by the JVM, covered in depth in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md) — Java is genuinely both, at different stages, which is exactly why 'is Java compiled or interpreted' is a common but slightly trick interview question."

**Code:**

```text
COMPILED (e.g., C):
  source.c --[compiler, ONCE, ahead of time]--> machine code executable
  Running it later needs NO compiler present at all — just the executable.

INTERPRETED (e.g., classic Python usage):
  source.py --[interpreter reads and executes EACH LINE, at runtime]--> program behavior
  The interpreter must be present every time the program runs.

JAVA (genuinely BOTH, at different stages):
  source.java --[javac, ahead of time]--> bytecode (.class)
  bytecode --[JVM interprets, then JIT-compiles hot paths]--> actual execution
```

**Follow-up:**

I'd mention the practical trade-off this distinction is really getting at: ahead-of-time compilation to native machine code generally gives faster startup and predictable peak performance with no runtime translation overhead, while interpretation trades some raw performance for portability and development convenience (no separate compile step to run/test a change) — and I'd bring up GraalVM's native-image compilation (mentioned in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md)) as a modern example of applying ahead-of-time compilation *to* Java specifically, trading away the JIT's warmup-then-peak-throughput behavior for near-instant startup, which matters for short-lived workloads like serverless functions.

**Source:** [Oracle Java Tutorials — javac and the JVM](https://docs.oracle.com/javase/tutorial/getStarted/intro/definition.html)

---

### 21. What's the Difference Between Static and Dynamic Typing?

**Answer:**

"In a **statically-typed** language (Java, C++), every variable's type is fixed and checked at **compile time** — the compiler verifies that every operation is valid for the declared types before the program ever runs, and a type mismatch (assigning a `String` to an `int` variable) is a compile error, caught before deployment, not a runtime surprise. In a **dynamically-typed** language (Python, JavaScript), a variable's type isn't fixed at all — the same variable name can hold an integer at one point and a string moments later — and type checking happens at **runtime**, as each operation actually executes, so a type mismatch only surfaces as an error when that specific line of code actually runs, potentially in production, if the code path wasn't exercised during testing.

The trade-off: static typing catches a real class of bugs earlier (at compile time, the cheapest point to fix them) and lets tooling (IDEs, refactoring tools) reason precisely about a codebase, at the cost of more verbose declarations; dynamic typing is more flexible and typically faster to write quickly, at the cost of type-related bugs only surfacing when the specific buggy code path actually executes, which is exactly why comprehensive test coverage matters even more in dynamically-typed codebases."

**Code:**

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

**Follow-up:**

I'd mention TypeScript as a genuinely relevant, increasingly common middle ground worth knowing about: it adds an optional static type-checking layer on top of JavaScript (which is dynamically typed), catching type errors at compile/build time while still compiling down to plain, dynamically-typed JavaScript for actual execution — a deliberate attempt to get static typing's earlier-error-detection benefit in an ecosystem that's historically been dynamically typed, without abandoning JavaScript's runtime and ecosystem entirely.

**Source:** [JLS §4 — Types, Values, and Variables](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html)

---

## Operating Systems

### 22. What Is an Operating System, and What Does the Kernel Do?

**Answer:**

"An operating system is the software layer that manages a computer's hardware resources (CPU, memory, storage, network devices) and provides a consistent, higher-level interface for applications to use those resources, without every single application needing to know how to directly control the underlying hardware itself. The **kernel** is the OS's core — the part with direct, privileged access to hardware, responsible for the most fundamental resource-management decisions: which process gets the CPU next (scheduling), which physical memory a process can access (covered in the virtual-memory question next), and mediating every application's access to hardware devices.

The kernel runs in a privileged execution mode ('kernel space') that regular application code ('user space') cannot directly access — an application requests kernel services (reading a file, allocating memory, sending network data) through a controlled interface called a **system call**, rather than touching hardware or protected memory directly; this separation is a deliberate security and stability boundary, preventing one misbehaving application from corrupting the kernel or directly interfering with other applications' resources."

**Code:**

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

**Follow-up:**

I'd connect this directly to the JVM's own position in this stack, since it's a concrete, already-covered example: the JVM itself is a user-space application running on top of the OS — when Java code allocates an object on the heap, the JVM (not the application code directly) is the one making the underlying system calls to request memory from the OS kernel, and this OS-level process/memory management is a genuinely separate layer beneath everything the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md) covers about the JVM's *own* internal heap/stack/generation management — the JVM manages memory *within* the chunk the OS kernel has already granted it, not the machine's physical memory directly.

**Source:** [Operating Systems: Three Easy Pieces — Remzi H. Arpaci-Dusseau & Andrea C. Arpaci-Dusseau](https://pages.cs.wisc.edu/~remzi/OSTEP/)

---

### 23. What Is Virtual Memory, and What Is Paging?

**Answer:**

"Virtual memory is an abstraction the OS provides so that every process believes it has its own large, private, contiguous address space, completely isolated from every other process's memory — even though the underlying physical RAM is actually a shared, finite resource split across every running process (and possibly not even large enough to hold everything every process thinks it has). The OS (with hardware support) translates each process's virtual addresses to actual physical memory addresses transparently, and this indirection is exactly what makes one process's memory bugs unable to directly corrupt another process's memory, or the kernel's own memory.

**Paging** is the specific mechanism most modern OSes use to implement virtual memory: physical memory is divided into fixed-size chunks called **pages** (commonly 4KB), and a process's virtual address space is divided into pages of the same size, with a **page table** mapping each virtual page to a physical page frame. Critically, not every virtual page needs to be backed by physical memory *simultaneously* — a page not currently in active use can be swapped out to disk, freeing physical memory for pages that are actually needed right now, and transparently swapped back in (a 'page fault,' handled by the kernel) the moment the process actually accesses that virtual address again."

**Code:**

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

**Follow-up:**

I'd tie this directly to a concrete failure mode covered elsewhere in this kit: when a containerized JVM's memory footprint (heap plus metaspace plus thread stacks plus everything else, covered in the [Java JVM & GC guide](../Language/Java_JVM_GC_Interview_Prep.md)) exceeds the container's memory limit, the container runtime's OOM killer terminates the process — that's a *cgroup*-enforced limit sitting on top of this virtual-memory system, a genuinely different mechanism from the OS swapping individual pages to disk under normal memory pressure, worth not conflating: a container getting OOM-killed isn't the OS "running out of virtual memory," it's the container's own configured resource limit being exceeded.

**Source:** [Operating Systems: Three Easy Pieces — Paging chapters](https://pages.cs.wisc.edu/~remzi/OSTEP/)

---

### 24. What Is CPU Caching, and Why Does It Matter for Performance?

**Answer:**

"CPU caching is small, extremely fast memory built directly into (or very close to) the processor, sitting between the CPU and main RAM, holding copies of recently/frequently-accessed data so the CPU doesn't have to wait for the comparatively much slower trip to main memory on every single access. Modern CPUs have multiple cache levels — L1 (smallest, fastest, per-core), L2 (larger, still per-core or shared between a couple of cores), L3 (largest, shared across all cores) — each level trading capacity for speed, with main RAM as the final, much slower fallback if data isn't found in any cache level ('a cache miss').

This matters for performance far beyond just 'caches make things faster' as a vague idea — it directly explains a genuinely counterintuitive result covered concretely in the [Java Collections guide](../Language/Java_Collections_Interview_Prep.md): `ArrayList`'s contiguous memory layout means sequentially accessing its elements tends to pull several useful elements into cache at once (good 'locality of reference'), while `LinkedList`'s scattered, individually-heap-allocated nodes mean each element access is likely a fresh cache miss requiring a trip to main memory — which is exactly why `LinkedList`'s theoretical Big-O insertion advantage often loses to `ArrayList` in real, measured performance, despite what the raw complexity analysis alone would suggest."

**Code:**

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

**Follow-up:**

I'd mention that this is a case where understanding the underlying hardware behavior directly changes a design decision that pure algorithmic (Big-O) analysis alone would get wrong — the [Java Collections guide](../Language/Java_Collections_Interview_Prep.md)'s `ArrayList` vs. `LinkedList` comparison is the concrete worked example, and the general lesson worth carrying forward: for anything but very large N, cache-friendliness (data locality, sequential access patterns) frequently dominates real-world performance more than asymptotic complexity does, which is exactly why "measure, don't just theorize" is the right instinct once a genuine performance question is on the table.

**Source:** [Operating Systems: Three Easy Pieces — Remzi H. Arpaci-Dusseau & Andrea C. Arpaci-Dusseau](https://pages.cs.wisc.edu/~remzi/OSTEP/)

---

## Databases

### 25. What Is Database Normalization, and What Do 1NF, 2NF, and 3NF Mean?

**Answer:**

"Normalization is the process of organizing a relational database's tables and columns specifically to reduce data redundancy and avoid update/insert/delete anomalies — situations where the same fact is stored in multiple places, and those copies can drift out of sync with each other, or where you can't insert one piece of information without also being forced to insert an unrelated one. It's expressed as a series of increasingly strict rules called normal forms.

**1NF (First Normal Form)**: every column holds a single, atomic value — no repeating groups or comma-separated lists crammed into one column (a `phone_numbers` column holding `"555-1234, 555-5678"` violates 1NF; it should be a separate related table instead). **2NF**: satisfies 1NF, and every non-key column depends on the *entire* primary key, not just part of it — relevant specifically for tables with a composite key (covered in the [JPA & Hibernate guide](../Frameworks/JPA_Hibernate_Interview_Prep.md)), where a column depending on only one part of a multi-column key is a 2NF violation. **3NF**: satisfies 2NF, and no non-key column depends on *another non-key column* (a 'transitive dependency') — storing both `zip_code` and `city` in an `orders` table, where `city` is actually fully determined by `zip_code` rather than by the order itself, is a classic 3NF violation, since updating one order's zip code without also updating its city risks the two falling out of sync."

**Code:**

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
  | 1        | 10001    | New York |   <- if zip_code determines city, storing
  | 2        | 10001    | New York |      BOTH here risks them drifting out of sync

3NF FIX: city belongs in a separate zip_code -> city lookup table instead
```

**Follow-up:**

I'd give the practical, staff-level framing rather than presenting normalization as an unconditional goal: fully normalized schemas minimize redundancy and anomaly risk, but every join required to reassemble related data back together at query time has a real performance cost — which is exactly why **denormalization** (deliberately reintroducing some redundancy, for read performance) is a legitimate, common trade-off for read-heavy workloads, not a mistake — the [REST API Design guide](../System%20Design/REST_API_Design_Interview_Prep.md)'s composite/aggregate-endpoint question and the general caching material in the [Redis & Caching guide](../System%20Design/Redis_Caching_Interview_Prep.md) both cover different angles of this same normalized-versus-denormalized trade-off.

**Source:** [MIT OpenCourseWare — Database, Internet, and Systems Integration Technologies, Data Normalization](https://ocw.mit.edu/courses/1-264j-database-internet-and-systems-integration-technologies-fall-2013/resources/mit1_264jf13_lect_11/)

---

### 26. What Is a Database Index, and Why Does It Speed Up Queries?

**Answer:**

"Without an index, finding rows matching a condition (`WHERE email = 'alice@example.com'`) requires the database to scan every single row in the table, checking each one — a 'full table scan,' whose cost grows linearly with table size (O(n), covered in the Big-O question earlier in this guide). An index is a separate, auxiliary data structure — typically a B-tree, a balanced, sorted tree structure (tying to the tree-vs-graph question earlier in this guide) — built on one or more columns, that lets the database jump almost directly to matching rows instead of scanning everything, turning an O(n) lookup into roughly O(log n).

This isn't free, though: an index has to be **maintained** — kept up to date — on every `INSERT`, `UPDATE`, or `DELETE` affecting an indexed column, which adds real write overhead, and the index itself consumes additional storage space. The practical trade-off: indexes are worth adding for columns genuinely queried/filtered/joined-on frequently (especially in read-heavy workloads), but indexing every column reflexively 'just in case' pays a real, ongoing write-performance and storage cost for indexes that may rarely, if ever, actually get used by a query."

**Code:**

```sql
-- WITHOUT an index: full table scan — checks EVERY row, O(n)
SELECT * FROM users WHERE email = 'alice@example.com';

-- Add an index on the column actually being filtered on:
CREATE INDEX idx_users_email ON users(email);

-- The SAME query now seeks directly via the index's B-tree structure — roughly O(log n),
-- instead of scanning every row in the table
SELECT * FROM users WHERE email = 'alice@example.com';
```

**Follow-up:**

I'd connect this directly to the [JPA & Hibernate guide](../Frameworks/JPA_Hibernate_Interview_Prep.md)'s question on how database indexes interact with Hibernate-generated queries specifically — an ORM can generate a query that's logically correct but doesn't actually use an available index efficiently (a function applied to the indexed column in the `WHERE` clause, for instance, can prevent the database from using a plain index on that column at all) — which is exactly why checking the *actual generated SQL* and its query plan, not just assuming "I added an index, so it must be fast now," is the real staff-level diagnostic discipline once a query is underperforming.

**Source:** [PostgreSQL Documentation — Indexes](https://www.postgresql.org/docs/current/indexes.html)

---

## Software Engineering Practices

### 27. What Is Version Control, and What Does Git Actually Track?

**Answer:**

"Version control is a system for tracking changes to a set of files over time, letting you see history, revert to a previous state, and — critically for team development — let multiple people work on the same codebase concurrently without simply overwriting each other's changes. Git is by far the dominant modern version control system, and it's specifically **distributed**: every clone of a repository has the *entire* project history locally, not just the current state, unlike older centralized systems that required contacting a central server for most operations (viewing history, committing).

The detail worth knowing precisely: Git doesn't track changes as a list of line-by-line diffs the way older systems (Subversion, CVS) conceptually do — it tracks a **series of snapshots**. Every commit is essentially a complete snapshot of every tracked file at that moment (though Git optimizes storage internally, avoiding literally duplicating unchanged files) — a genuinely different underlying model from delta-based tracking, even though the day-to-day experience of writing and reviewing a `diff` looks similar either way."

**Code:**

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

**Follow-up:**

I'd mention branching strategy as the practical, team-level concern that sits on top of Git's own mechanics — trunk-based development, Git Flow, and various other conventions all answer the same underlying question (how do multiple people's concurrent work get integrated safely and reviewably) differently, and the specific strategy a team uses matters far more day-to-day than Git's internal snapshot-vs-delta model; I'd also note that a pull/merge request — the review gate most teams put in front of merging a branch — is a workflow convention layered on top of Git by hosting platforms (GitHub, GitLab), not a feature of Git itself.

**Source:** [Git — Getting Started: What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)

---

### 28. What's the Difference Between Unit, Integration, and End-to-End Tests?

**Answer:**

"These form what's commonly called the 'test pyramid,' differing in scope and what they're actually verifying. **Unit tests** verify a single, small unit of code (one method, one class) in isolation, with any external dependencies (a database, a network call) replaced by a mock/stub — they're fast, cheap to run in large numbers, and pinpoint exactly which unit broke when one fails. **Integration tests** verify that multiple units, or an application and a real external dependency (an actual database, a real message broker), work correctly *together* — slower and more expensive than unit tests, but they catch a real category of bug unit tests structurally can't: two units that each pass their own unit tests in isolation, but don't actually integrate correctly together. **End-to-end (E2E) tests** verify a complete, real user-facing workflow through the *entire* running system (often literally driving a browser against a fully-deployed application) — the slowest and most expensive of the three, but the closest to actually verifying 'does this work correctly for a real user.'

The 'pyramid' shape describes the recommended proportion: many fast unit tests as the foundation, a moderate number of integration tests, and comparatively few E2E tests — inverting that shape (many slow E2E tests, few unit tests) is a common, real anti-pattern that produces a slow, flaky, expensive-to-maintain test suite."

**Code:**

```text
        /\
       /E2E\        <- FEW: slow, expensive, tests the whole real system end to end
      /------\
     /  Integ  \    <- SOME: tests real interaction between components/external systems
    /------------\
   /     Unit      \ <- MANY: fast, cheap, tests one isolated unit at a time
  /------------------\
```

```java
// Unit test — OrderService tested in ISOLATION, PaymentGateway is a mock
@Test
void placesOrderSuccessfully() {
    PaymentGateway mockGateway = mock(PaymentGateway.class);
    when(mockGateway.charge(any())).thenReturn(success());
    OrderService service = new OrderService(mockGateway);
    // ... assert on OrderService's behavior alone, no real payment gateway involved
}
```

**Follow-up:**

I'd bring up test flakiness as the practical, staff-level reason the pyramid shape matters beyond just "unit tests are faster" — E2E tests, by nature of exercising the entire real system (network calls, timing, a real browser), are inherently more prone to intermittent, non-deterministic failures unrelated to an actual bug, and a test suite dominated by flaky E2E tests erodes a team's trust in CI signal over time (people start re-running failed builds reflexively rather than investigating), which is a genuine, common, and expensive organizational problem — not just a testing-strategy nitpick.

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
| RFC 9113 — HTTP/2 | https://datatracker.ietf.org/doc/html/rfc9113 |
| RFC 9114 — HTTP/3 | https://datatracker.ietf.org/doc/html/rfc9114 |
| NIST — Cryptographic Standards and Guidelines | https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines |
| NIST SP 800-107 — Approved Hash Algorithms | https://csrc.nist.gov/pubs/sp/800/107/r1/final |
| RFC 8446 — TLS 1.3 | https://datatracker.ietf.org/doc/html/rfc8446 |
| NIST SP 800-57 — Recommendation for Key Management | https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final |
| RFC 5280 — Internet X.509 Public Key Infrastructure Certificate | https://datatracker.ietf.org/doc/html/rfc5280 |
| MIT OpenCourseWare — Introduction to Algorithms | https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/ |
| PostgreSQL Documentation | https://www.postgresql.org/docs/current/ |
| MongoDB Documentation — Data Modeling Introduction | https://www.mongodb.com/docs/manual/core/data-modeling-introduction/ |
| W3C — Web Services Architecture | https://www.w3.org/TR/ws-arch/ |
| Oracle Java Tutorials — Object-Oriented Programming Concepts | https://docs.oracle.com/javase/tutorial/java/concepts/index.html |
| Oracle Java Tutorials — Polymorphism | https://docs.oracle.com/javase/tutorial/java/IandI/polymorphism.html |
| Oracle Java Tutorials — javac and the JVM | https://docs.oracle.com/javase/tutorial/getStarted/intro/definition.html |
| JLS §4 — Types, Values, and Variables | https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html |
| Operating Systems: Three Easy Pieces (Arpaci-Dusseau) | https://pages.cs.wisc.edu/~remzi/OSTEP/ |
| MIT OpenCourseWare — Database, Internet, and Systems Integration Technologies, Data Normalization | https://ocw.mit.edu/courses/1-264j-database-internet-and-systems-integration-technologies-fall-2013/resources/mit1_264jf13_lect_11/ |
| PostgreSQL Documentation — Indexes | https://www.postgresql.org/docs/current/indexes.html |
| Git — Getting Started: What is Git? | https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F |
| Martin Fowler — The Practical Test Pyramid | https://martinfowler.com/articles/practical-test-pyramid.html |
