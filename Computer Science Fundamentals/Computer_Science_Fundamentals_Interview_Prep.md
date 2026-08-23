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
