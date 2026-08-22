# Docker & Kubernetes — Interview Prep, Basic to Staff Level (with Code & Sources)

How to use this: each question has an **Answer** written the way it would actually be said out loud in an interview, a **Code** snippet you could sketch on a whiteboard or run in a terminal, and — for the mid and staff-level questions especially — a **Follow-up** section covering failure modes and trade-offs. Questions are grouped by level (Docker Basic → Staff, then Kubernetes Basic → Staff) so you can calibrate depth to the interview you're prepping for; the later sections assume the earlier ones as background and don't re-explain them.

---

## Docker — Basic

### 1. What Is a Container, and How Does It Actually Differ From a VM?

**Answer:**

"A container is an isolated process (or group of processes) running directly on the **host machine's own kernel** — it gets its own filesystem, network interface, and process namespace, but there's no separate operating system booting underneath it. A VM, by contrast, virtualizes hardware and runs a **complete, separate guest OS and kernel** on top of a hypervisor, which is a much heavier abstraction.

The practical consequences follow directly from that: containers start in milliseconds (there's no kernel to boot, just a process to launch) and have a far smaller memory/disk footprint (no duplicate OS per instance), while VMs take tens of seconds to boot and carry the overhead of a full OS per instance. The trade-off is isolation strength — a VM's isolation boundary is enforced by the hypervisor at the hardware-virtualization level, which is a much stronger, more battle-tested security boundary than a container's, which relies entirely on the host kernel correctly enforcing namespace/cgroup isolation (question 13 covers exactly when this distinction becomes a real security concern, not just a performance one)."

**Code:**

```text
VM:        [Hardware] -> [Hypervisor] -> [Guest OS #1 (full kernel)] -> [App A]
                                       -> [Guest OS #2 (full kernel)] -> [App B]
           Each app gets a FULL, separate OS — heavy, slow to start, strong isolation

Container: [Hardware] -> [Host OS + ONE shared kernel] -> [Container A (App A)]
                                                        -> [Container B (App B)]
           Apps SHARE the host kernel — light, fast to start, weaker isolation boundary
```

**Follow-up:**

I'd bring up that this distinction is exactly why containers and VMs are increasingly combined rather than treated as competitors — a managed Kubernetes node is itself usually a VM, and each pod on it is a set of containers, giving you the hypervisor's strong isolation *between* tenants/nodes and the container's fast startup/density *within* a node. I'd also mention microVM technologies (Firecracker, used by AWS Lambda and Fargate) as a middle ground purpose-built for exactly this tension — near-VM isolation strength with near-container startup speed, by stripping the hypervisor down to the bare minimum a container-shaped workload actually needs.

**Source:** [Docker — What Is a Container?](https://docs.docker.com/get-started/docker-overview/)

---

### 2. What Is the Difference Between a Docker Image and a Container?

**Answer:**

"An image is a read-only, layered template — a packaged filesystem snapshot plus metadata (the default command, exposed ports, environment variables) that describes *what* to run. A container is a running (or stopped) **instance** of an image — the same relationship as a class and an object, or an executable file and a running process. You can create many containers from the same image, each with its own writable layer and its own runtime state, without affecting the underlying image or any other container built from it.

Concretely: `docker build` produces an image; `docker run` takes an image and creates a container from it, adding one thin, container-specific writable layer on top of the image's read-only layers (copy-on-write — a file modified inside the container is copied into that writable layer, leaving the underlying image layers untouched). Deleting a container doesn't affect the image it came from, and the same image can be safely used to spin up many independent containers simultaneously."

**Code:**

```bash
docker build -t myapp:1.0 .        # produces an IMAGE — a template, not running anything
docker run -d --name c1 myapp:1.0  # creates CONTAINER c1 from that image
docker run -d --name c2 myapp:1.0  # creates a SEPARATE container c2, same image,
                                     # independent writable layer and runtime state
docker rm c1                        # removes the CONTAINER — the image is untouched,
                                     # c2 keeps running fine
```

**Follow-up:**

I'd bring up that this read-only-image-plus-writable-layer model is exactly why containers are meant to be treated as **disposable and stateless** by default — anything written into that thin writable layer is lost the moment the container is removed, which is precisely the motivation for volumes (question 6) for anything that actually needs to persist, and for building configuration into environment variables/mounted config rather than baking mutable state into the image itself.

**Source:** [Docker — What Is an Image?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/), [Docker — What Is a Container?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)

---

### 3. Explain the Dockerfile Build Process and Layer Caching

**Answer:**

"Each instruction in a Dockerfile (`FROM`, `RUN`, `COPY`, etc.) produces a new, immutable **layer** stacked on top of the previous one, and the final image is just that ordered stack of layers. The build engine caches each layer, keyed by the instruction plus its inputs (the command text for `RUN`, or a hash of the copied files' contents for `COPY`/`ADD`) — if a later build's instruction and its inputs are byte-for-byte identical to a previous build's, Docker reuses the cached layer instead of re-executing it, which is where most of the real speed-up in iterative builds comes from.

The layer that matters most for cache efficiency is the **first one that changes** — once any layer's cache is invalidated, every layer *after* it in the Dockerfile must be rebuilt too, even if those later instructions' own inputs haven't changed, since each layer is built on top of the previous one's actual output. This is exactly why dependency installation (`COPY package.json .` then `RUN npm install`) is conventionally placed *before* copying the full application source in a well-written Dockerfile — application code changes far more often than dependencies, and putting the volatile `COPY . .` last means a typical code-only change only invalidates the last couple of layers, not the expensive dependency-install step."

**Code:**

```dockerfile
# GOOD ordering — volatile source code copied LAST, so a code-only change
# doesn't invalidate (and force a re-run of) the expensive npm install layer
FROM node:20
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install          # cached as long as package*.json is unchanged
COPY . .                  # this layer (and only this one) invalidates on code changes
CMD ["node", "server.js"]

# BAD ordering — copying everything first means ANY file change invalidates
# the cache from that point forward, forcing npm install to re-run every time
FROM node:20
WORKDIR /app
COPY . .
RUN npm install           # re-runs on EVERY build, even a one-line code change
CMD ["node", "server.js"]
```

**Follow-up:**

I'd bring up BuildKit's cache-mount feature (`--mount=type=cache`) as the modern refinement beyond just instruction ordering — it lets a specific directory (like `~/.npm` or `~/.m2`) persist as a *build cache* across otherwise-cache-invalidated builds, independent of layer caching, which is a meaningfully bigger win for compiled/dependency-heavy languages where even a single source-file change would otherwise force re-downloading every dependency from scratch under naive layer caching alone.

**Source:** [Docker — Build Cache](https://docs.docker.com/build/cache/)

---

### 4. What's the Difference Between `CMD` and `ENTRYPOINT`?

**Answer:**

"Both specify what runs when a container starts, but they compose differently. `ENTRYPOINT` sets the actual command that always executes — it's the fixed, non-overridable (without an explicit `--entrypoint` flag) executable for the image. `CMD` sets **default arguments** — if the Dockerfile only has `CMD`, those are the default command and args, fully overridable by anything passed after the image name in `docker run`; if the Dockerfile has *both*, `CMD`'s value becomes the *default arguments to* `ENTRYPOINT`, and a user can override just the arguments at `docker run` time while the entrypoint executable itself stays fixed.

The practical pattern this enables: an image whose whole purpose is running one specific binary (say, a CLI tool) uses `ENTRYPOINT ["mytool"]` with `CMD ["--help"]` as the default arg — running the image with no arguments shows help, but `docker run myimage --version` cleanly overrides just the argument, without needing to know or repeat the underlying binary name."

**Code:**

```dockerfile
ENTRYPOINT ["mytool"]
CMD ["--help"]
```

```bash
docker run myimage              # runs: mytool --help
docker run myimage --version    # runs: mytool --version — CMD's default overridden,
                                   # ENTRYPOINT's "mytool" stays fixed either way
```

**Follow-up:**

I'd flag the shell-form vs. exec-form distinction as the detail that actually causes production bugs — `CMD command arg` (shell form) runs the command through `/bin/sh -c`, which means the actual application process is a *child* of the shell, not PID 1, and it won't receive `SIGTERM` directly when the container is stopped (the shell does, and may or may not forward it) — whereas `CMD ["command", "arg"]` (exec form, JSON array syntax) runs the command directly as PID 1, receiving signals correctly. I'd treat exec form as the default I reach for, specifically to avoid the graceful-shutdown problems shell form introduces (question 10 covers signal handling in more depth).

**Source:** [Dockerfile Reference — CMD and ENTRYPOINT](https://docs.docker.com/reference/dockerfile/)

---

### 5. Explain Docker's Core Networking Modes (Bridge, Host, None)

**Answer:**

"**Bridge** (the default) creates a private, internal virtual network on the host — each container gets its own network namespace and internal IP on that bridge, and Docker sets up NAT rules so the container can reach the outside world and (for published ports) be reached from outside. Containers on the same user-defined bridge network can resolve each other by container name via Docker's built-in DNS, which is what makes multi-container `docker compose` setups work without hardcoding IPs.

**Host** mode removes network isolation entirely — the container shares the host's own network namespace directly, so a service listening on port 8080 inside the container is genuinely listening on port 8080 on the host itself, no port mapping or NAT involved. This is faster (no NAT overhead) but sacrifices network isolation between the container and host, and between that container and any other container also using host networking.

**None** gives the container no network interface at all beyond loopback — genuinely isolated, useful for a workload that has no network need at all (a batch job reading only from a mounted volume) where you want to eliminate network access as an attack surface entirely, not just restrict it."

**Code:**

```bash
docker run --network bridge myapp   # default — isolated, NAT'd, port-mapped
docker run --network host myapp     # shares host's network namespace directly —
                                       # container's port 8080 IS the host's port 8080
docker run --network none myapp     # no network interface at all except loopback
```

**Follow-up:**

I'd bring up that user-defined bridge networks (as opposed to the legacy default `bridge` network) are the practical default for any real multi-container application, specifically because they provide automatic DNS-based service discovery by container name — the legacy default bridge network requires manual `--link` flags or hardcoded IPs, which is fragile and effectively deprecated in favor of just creating your own named bridge network (or using `docker compose`, which does this automatically).

**Source:** [Docker — Networking Overview](https://docs.docker.com/engine/network/)

---

### 6. What Is a Docker Volume, and Why Not Just Write to the Container's Filesystem?

**Answer:**

"A container's own writable layer (question 2) is tied to that specific container's lifecycle — deleting the container deletes anything written there, and two containers (even from the same image) never share that layer. A **volume** is storage managed by Docker itself, living outside any single container's writable layer, that can be mounted into one or more containers — data written to it persists independently of any container's lifecycle, and can be shared between containers running simultaneously.

This matters for exactly the cases where a container's default disposability is the wrong behavior: a database's actual data files (you don't want them wiped every time the container is recreated during a deploy), or a cache/upload directory that needs to survive a container restart. Docker also supports **bind mounts** (mapping a specific host filesystem path directly into the container) — useful for local development (mounting your source code directory so edits on the host are immediately visible inside the container) but generally less portable across environments than a named volume, since it depends on a specific host path existing."

**Code:**

```bash
docker volume create mydata
docker run -v mydata:/var/lib/mysql mysql   # named volume — Docker-managed,
                                               # survives container removal entirely

docker run -v /host/path:/app/src myapp      # bind mount — direct host path,
                                                # common for local dev, less portable
```

**Follow-up:**

I'd bring up that this exact distinction — "the container is disposable, the volume is not" — is the mental model that carries directly into Kubernetes: a Pod's own filesystem is just as ephemeral as a plain container's, and `PersistentVolume`/`PersistentVolumeClaim` objects exist specifically to give storage a lifecycle independent of any single Pod, the same conceptual role a Docker volume plays for a single container, just with a cluster-level abstraction on top.

**Source:** [Docker — Volumes](https://docs.docker.com/engine/storage/volumes/)

---

## Docker — Intermediate

### 7. How Do Multi-Stage Builds Reduce Image Size and Attack Surface?

**Answer:**

"A multi-stage build uses multiple `FROM` instructions in one Dockerfile, where each stage can selectively copy artifacts *from a previous stage* — letting you build with a heavy toolchain (a full JDK, compilers, build tools) in an early stage, and then copy only the final compiled artifact into a lean, minimal final stage, discarding everything else (the build tools, intermediate files, source code) that the running application never actually needs.

This matters for two concrete reasons: **image size** — a build stage might be gigabytes with a full SDK and dependency cache, while the final runtime stage might only need a JRE and a single JAR file, a difference of an order of magnitude or more; and **attack surface** — every tool present in a shipped image is a potential vector (a compiler, a package manager, shell utilities an attacker could use post-compromise), so a final image containing only the runtime and the application artifact, with no build tooling at all, is meaningfully harder to exploit even if a vulnerability is found in the application itself."

**Code:**

```dockerfile
# Stage 1: build — heavy, has the full JDK and Maven, produces a JAR
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src
COPY . .
RUN mvn package -DskipTests

# Stage 2: runtime — lean, ONLY has a JRE and the compiled artifact,
# no Maven, no source code, no build cache
FROM eclipse-temurin:21-jre
COPY --from=build /src/target/app.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

**Follow-up:**

I'd bring up distroless or scratch-based final stages as the further extension of this same principle — a distroless image contains just the application and its runtime dependencies, with no shell, no package manager, and no OS utilities at all, meaning even if an attacker achieves code execution inside the container, they have no shell to interactively explore the filesystem or download further tooling, which is a real, measurable reduction in post-exploitation capability, not just a smaller download size.

**Source:** [Docker — Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)

---

### 8. What Linux Kernel Primitives Actually Implement Container Isolation?

**Answer:**

"Two distinct kernel mechanisms combine to make a container feel isolated, and they solve different halves of the problem. **Namespaces** provide the *what you can see* isolation — a PID namespace means a process inside the container sees only its own process tree (its own process appears as PID 1, with no visibility into host or sibling-container processes); a network namespace gives it its own network interfaces, routing table, and port space; a mount namespace gives it its own filesystem view; and there are equivalents for hostname (UTS), inter-process communication (IPC), and user IDs (user namespace, for UID remapping). Namespaces are what make a container's `ps` output show only its own processes, and what lets two containers both bind to 'port 8080' without conflicting, since each has its own network namespace.

**Cgroups** (control groups) provide the *what you can consume* isolation — CPU shares/quotas, memory limits, block I/O bandwidth, all enforced by the kernel per cgroup, which is what actually stops one container from starving others on the same host of CPU or memory. Namespaces alone don't limit resource consumption at all — a container without cgroup limits can still be seen only within its own process tree, but could still consume all the host's CPU or memory, starving every other container on that host."

**Code:**

```bash
# Inspecting a running container's actual isolation from the host side
docker run -d --name c1 --memory=256m --cpus=0.5 nginx
docker inspect c1 | grep -A2 '"Memory"'   # cgroup memory limit enforced

# From INSIDE a container, PID namespace makes the container's own process
# appear as PID 1 — no visibility into host processes or sibling containers
docker exec c1 ps aux    # shows only nginx's own process tree, not the host's
```

**Follow-up:**

I'd bring up that this namespace-plus-cgroup foundation is exactly why containers share a fundamentally different security model than VMs (question 13) — every container on a host still shares one kernel, so a kernel-level vulnerability (a container-escape CVE) can potentially compromise every container on that host simultaneously, which simply isn't possible across a hypervisor's stronger hardware-virtualization boundary. I'd also mention that `docker run --privileged` (or overly broad `--cap-add` flags) directly weakens this isolation by granting a container capabilities that let it interact with the host kernel far more directly than the default, minimal capability set — a real, common source of container-escape vulnerabilities in practice, and something I'd flag immediately in any security review of a Dockerfile or deployment manifest.

**Source:** [Docker — What Is a Container? (namespaces/cgroups)](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)

---

### 9. How Would You Systematically Reduce a Docker Image's Size and Attack Surface?

**Answer:**

"I'd apply a checklist rather than one single trick, since size and attack surface both compound from several independent sources. **Base image choice** — start from a minimal base (`alpine`, a `-slim` variant, or distroless) rather than a full OS image, which alone often cuts the majority of unnecessary size and tooling. **Multi-stage builds** (question 7) to strip build-time tooling from the shipped image entirely. **Layer consolidation** — chaining related `RUN` commands with `&&` rather than one `RUN` per command, specifically so temporary files created and then deleted within the same logical step don't get baked into a separate, permanent layer (a `RUN apt-get install && rm -rf /var/lib/apt/lists/*` in one layer actually removes that cache from the image; doing the cleanup in a *later*, separate `RUN` only removes it from the final visible filesystem, not from the image's total size, since the earlier layer's data is still stored). **`.dockerignore`** to prevent copying unnecessary files (`.git`, local `node_modules`, test fixtures) into the build context at all. And **explicit, minimal `COPY`** — copying only the specific files/directories actually needed, rather than a broad `COPY . .` that pulls in everything in the build context regardless of whether the running application needs it."

**Code:**

```dockerfile
# Layer consolidation — cleanup MUST be in the SAME RUN instruction to
# actually reduce image size, not just the final visible filesystem
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
# vs. the anti-pattern: a separate RUN rm -rf /var/lib/apt/lists/* AFTERWARD
# still leaves that data in the EARLIER layer, permanently part of the image
```

```text
# .dockerignore — keeps unnecessary files out of the build context entirely
.git
node_modules
*.test.js
Dockerfile
.env
```

**Follow-up:**

I'd bring up that size reduction and attack-surface reduction, while correlated, aren't quite the same goal, and I'd be explicit about which one a given change actually serves — switching to Alpine reduces size meaningfully, but Alpine's use of musl libc instead of glibc has occasionally caused subtle runtime behavior differences for some applications, which is a real compatibility risk worth testing for, not assuming away; distroless images address attack surface (no shell, no package manager) more directly than size alone, and I'd pick the specific technique based on which of the two goals actually matters most for the workload in question, rather than treating "smaller is unconditionally better" as the only consideration.

**Source:** [Docker — Building Best Practices](https://docs.docker.com/build/building/best-practices/)

---

### 10. Why Does a Containerized Process Sometimes Not Respond to `SIGTERM` the Way You'd Expect, and What Is `--init` For?

**Answer:**

"Every container has a PID 1 process, and PID 1 has special, historically kernel-enforced behavior in Linux: it does **not** get a default signal handler installed for signals like `SIGTERM` the way every other process does — if PID 1 doesn't explicitly register its own handler for a signal, that signal is simply ignored, rather than falling back to the default action (which, for `SIGTERM`, would normally be 'terminate the process'). Most application binaries (a Node.js app, a Python script, a JVM) were never written expecting to run as PID 1 and don't register these handlers — so `docker stop` (which sends `SIGTERM`, waits, then sends `SIGKILL` if the process hasn't exited) can end up doing nothing but wait out the full grace period and hard-kill the process, skipping any graceful-shutdown logic the application actually has, purely because the signal was never delivered to code that would act on it.

A second, related PID 1 problem: **zombie process reaping**. On a normal Linux system, PID 1 (`init`/`systemd`) is responsible for reaping (cleaning up) any orphaned child processes whose parent has exited. If your containerized application spawns child processes (a shell script forking subprocesses) and is itself PID 1, it needs to explicitly reap them too, or they accumulate as zombie processes.

Docker's `--init` flag solves both problems by inserting a minimal init process (`tini`) as the actual PID 1, which correctly forwards signals to your real application process (now running as PID 2) and reaps zombies correctly — your application code doesn't need to handle either concern itself."

**Code:**

```bash
docker run --init myapp
# tini becomes PID 1: correctly forwards SIGTERM to the real app (now PID 2),
# and reaps any zombie child processes the app spawns — neither of which
# most application code handles correctly on its own if run directly as PID 1
```

```dockerfile
# Alternative — bake it into the image directly via exec form + tini,
# rather than relying on every `docker run` caller remembering --init
FROM node:20-alpine
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--", "node", "server.js"]
```

**Follow-up:**

I'd bring up that this exact problem is precisely why Kubernetes Pod termination has its own grace-period mechanism (`terminationGracePeriodSeconds`, and the container's PID 1 signal-handling behavior directly determines whether that grace period is actually used productively for a clean shutdown, or wasted waiting out a signal that was silently ignored) — a containerized application that doesn't correctly handle `SIGTERM` as PID 1 will behave identically badly whether it's stopped via plain `docker stop` or via a Kubernetes rolling update, and I'd treat "does this container gracefully shut down on SIGTERM" as a concrete, testable thing to verify (`docker stop <container>` and check whether in-flight requests actually complete, or connections are cut immediately) before ever deploying it into an environment that depends on graceful termination for zero-downtime rollouts.

**Source:** [Docker CLI Reference — `docker run` (`--init`)](https://docs.docker.com/reference/cli/docker/container/run/)

---

## Docker — Staff Level

### 11. How Do You Manage Secrets in Docker Without Baking Them Into the Image?

**Answer:**

"The fundamental rule: a secret baked into an image layer (via `ENV`, or a `COPY` of a credentials file, or passed as a build `ARG` without care) is **permanently embedded in that layer**, retrievable by anyone with access to the image — including from a layer that was later 'removed' by a subsequent instruction, since removal in a later layer doesn't delete the data from the earlier layer's history; it just hides it from the final filesystem view. Environment variables set via `ENV` or `docker run -e` are also visible to anything that can inspect the container (`docker inspect`, or any process running inside it querying its own environment), which is a real exposure for a shared or multi-tenant host.

The correct approach depends on the phase. **At build time**: BuildKit's `--secret` flag mounts a secret into a specific `RUN` step's filesystem *only for that step's duration* — it's never written to any image layer, and isn't visible in the final image or its history at all, which is the right tool for something like a private package-registry credential needed only during `npm install`. **At runtime**: Docker Swarm (or, more commonly today, the container orchestrator — Kubernetes Secrets, or an external secrets manager like Vault/AWS Secrets Manager) injects the secret as a mounted file (preferred over an environment variable, since a mounted file isn't visible via `docker inspect`'s environment listing and can have stricter filesystem permissions) or an environment variable set only within the running container's process environment, never baked into any image."

**Code:**

```dockerfile
# BuildKit secret mount — visible ONLY during this RUN step,
# never written to any image layer or the final image at all
# syntax=docker/dockerfile:1
FROM node:20
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) npm install
```

```bash
docker build --secret id=npm_token,src=./npm_token.txt -t myapp .
# the secret file's content is available ONLY to the RUN step that
# explicitly mounts it, and never persists in the built image
```

**Follow-up:**

I'd bring up that `docker history --no-trunc <image>` and simply extracting an image's layers (`docker save` + `tar`) are both trivial ways to recover anything accidentally baked into an `ENV` or a `COPY`'d file, even after a later layer appears to remove it — I've seen real incidents where a team believed a secret was "deleted" because a later Dockerfile instruction removed the file, without realizing the original layer containing it was still fully present and extractable in the shipped image. I'd treat "grep the built image's layer history for anything secret-shaped" as a legitimate, worthwhile CI check, not just a policy relying on developer discipline never to make this mistake in the first place.

**Source:** [Docker — Build Secrets](https://docs.docker.com/build/building/secrets/)

---

### 12. How Would You Secure a Container Image Supply Chain End to End?

**Answer:**

"I'd think about this as several distinct, compounding risks, each needing its own control, rather than one single 'scan the image' step being sufficient on its own. **Base image provenance** — pin base images to a specific, immutable digest (`FROM node:20@sha256:...`) rather than a mutable tag like `node:20`, since a mutable tag can be silently repointed to different (and potentially compromised) content without any change to your own Dockerfile. **Vulnerability scanning** — scan built images for known CVEs in OS packages and application dependencies (Docker Scout, Trivy, Grype), ideally as a blocking CI gate for anything above an agreed severity threshold, not just an informational dashboard nobody acts on. **Provenance and signing** — sign images at build time (via Sigstore/cosign, or Docker Content Trust) so a deploying system can cryptographically verify an image actually came from your legitimate build pipeline and hasn't been tampered with or substituted in the registry. **Dependency pinning** — lockfiles for application dependencies (not just base images), so a build isn't silently pulling a different, potentially compromised version of a transitive dependency between builds. **Least-privilege runtime** — running as a non-root user inside the container (`USER` instruction) and dropping unnecessary Linux capabilities, so even a successfully exploited vulnerability in the running application has a smaller blast radius."

**Code:**

```dockerfile
FROM node:20-alpine@sha256:abc123...   # pinned to an immutable digest,
                                          # not a mutable tag that can be repointed
RUN addgroup -S app && adduser -S app -G app
USER app                                 # non-root at runtime — limits blast
                                          # radius of a successful exploit
```

```bash
# Blocking CI gate — fail the build on high/critical CVEs, not just report them
docker scout cves myapp:latest --exit-code --only-severity critical,high
```

**Follow-up:**

I'd bring up that "scan the image" alone is a weaker control than it appears, since a scanner can only flag *known* CVEs against packages it can actually identify — a base image built from source, or a dependency with an unpublished/not-yet-disclosed vulnerability, or a maliciously *modified* (not merely outdated) package, all slip past pure vulnerability scanning. Signing and provenance verification (SLSA-style supply-chain attestation, or at minimum cosign-signed images with an admission-controller-enforced policy requiring a valid signature before deployment) address a genuinely different threat — "is this the artifact my pipeline actually produced" rather than "does this artifact contain known-bad code" — and I'd treat both as complementary, not redundant, layers of the same overall supply-chain security posture.

**Source:** [Docker Scout](https://docs.docker.com/scout/)

---

### 13. What Are the Real Security Boundaries of a Container Versus a VM, and When Is That Boundary Insufficient?

**Answer:**

"Building directly on question 8, a container's isolation is entirely enforced by the **host kernel** correctly implementing namespace and cgroup boundaries — every container on a host shares that one kernel, so a kernel vulnerability that allows a process to escape its namespace confines (a container-escape CVE) potentially compromises every other container on that same host, since there's no additional hardware-enforced boundary between them. A VM's isolation is enforced by the **hypervisor**, at the hardware-virtualization level — a guest VM breakout requires exploiting the hypervisor itself, a much smaller, more specialized, and more heavily scrutinized piece of software than a general-purpose OS kernel, making VM-escape vulnerabilities meaningfully rarer in practice than container-escape ones.

This distinction becomes a real, practical concern specifically in **multi-tenant** scenarios where you're running genuinely untrusted or adversarial workloads (a platform running arbitrary customer-submitted code, a CI system executing untrusted pull-request code) alongside other tenants — the assumption 'containers are isolated enough' is a reasonable bet for your own trusted internal services sharing a host, but a much riskier bet when one tenant might be actively trying to escape into another's data. For that specific threat model, I'd reach for one of the stronger-isolation options purpose-built for exactly this gap: **gVisor** (a userspace kernel that intercepts and re-implements syscalls, so a container never talks to the real host kernel directly) or **Kata Containers** (running each container inside its own lightweight, hardware-virtualized microVM) — both give container-like density and speed with meaningfully closer-to-VM isolation guarantees."

**Code:**

```text
Standard container:      [App] -> syscalls -> [SHARED host kernel]
                          -- kernel vulnerability = potential cross-container compromise

gVisor (runsc runtime):  [App] -> syscalls -> [gVisor userspace kernel] -> [host kernel]
                          -- most syscalls intercepted/re-implemented in userspace,
                             narrowing what actually reaches the real host kernel

Kata Containers:         [App] -> [container] -> [dedicated microVM] -> [host kernel]
                          -- each container gets its OWN lightweight VM boundary,
                             not sharing a kernel with other containers at all
```

**Follow-up:**

I'd bring up that this is a genuine, concrete design decision I'd expect to make explicitly on a platform team — "what's our actual tenant-trust model, and does plain container isolation (fine for our own internal services) actually match the threat model for this specific workload (arbitrary customer code)" — rather than defaulting to standard containers everywhere purely because that's what most of the platform already uses. I'd point to exactly this reasoning as why serverless platforms running untrusted customer code (AWS Lambda, Google Cloud Run) use Firecracker microVMs rather than plain containers underneath, despite the added overhead, precisely because their tenant-isolation requirements are stricter than a typical internal multi-container deployment's.

**Source:** [gVisor](https://gvisor.dev/), [Kata Containers](https://katacontainers.io/)

---

## Kubernetes — Basic

### 14. What Is a Pod, and Why Does Kubernetes Never Schedule a Bare Container Directly?

**Answer:**

"A Pod is Kubernetes' smallest deployable unit — one or more containers that are **always scheduled together on the same node**, share the same network namespace (same IP address and port space — containers in a Pod reach each other via `localhost`) and can share storage volumes. Kubernetes never schedules a container directly; everything, even a single-container workload, is wrapped in a Pod, because the Pod is the actual unit the scheduler reasons about for placement, networking, and lifecycle.

The multi-container case is the more interesting design point: a Pod with more than one container models things that genuinely need to be co-located and share a lifecycle — a 'sidecar' container (a log shipper, a service-mesh proxy) that augments a main application container, where it only makes sense for both to start, stop, and be network-adjacent together. If two containers *don't* need this tight co-location (they could reasonably scale independently, or fail independently without taking the other down), they belong in separate Pods, not the same one — bundling them together needlessly couples their scaling and failure characteristics."

**Code:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:1.0
  - name: log-shipper       # sidecar — shares network/lifecycle with "app",
    image: fluent-bit:latest  # reaches "app" via localhost, always co-scheduled
```

**Follow-up:**

I'd bring up that you almost never create a bare Pod directly in a real deployment — you create a **Deployment** (or StatefulSet, DaemonSet, Job) that *manages* Pods on your behalf, because a bare Pod has no self-healing behavior at all: if the node it's on dies, or the Pod is deleted, nothing recreates it. The controller (question 15) is what actually watches for that and ensures the desired number of Pods keeps existing, which is the behavior almost every real workload actually needs.

**Source:** [Kubernetes — Pods](https://kubernetes.io/docs/concepts/workloads/pods/)

---

### 15. Explain the Relationship Between a Deployment, a ReplicaSet, and Pods

**Answer:**

"These three form a layered chain of responsibility, each managing the layer below it. A **Deployment** is what you actually create and edit — it declares the desired state (which container image, how many replicas, update strategy) and manages rolling out changes to that state over time. A Deployment doesn't manage Pods directly; it creates and manages a **ReplicaSet**, whose one job is simpler and narrower: ensure exactly N Pods matching a specific Pod template exist at any given time, creating new ones if any are deleted or die, and deleting extras if there are too many.

The reason for this extra layer: when you update a Deployment (a new image version), it doesn't mutate the existing ReplicaSet's Pods in place — it creates a **new** ReplicaSet with the updated Pod template, and gradually shifts the desired replica count from the old ReplicaSet to the new one (the rolling update mechanism, question 23), while keeping the old ReplicaSet around (scaled to zero) specifically to make **rollback** trivial — reverting a Deployment just means shifting replica count back to the old ReplicaSet rather than needing to reconstruct the previous Pod template from scratch."

**Code:**

```text
Deployment "myapp" (what you edit — desired state, rollout strategy)
     |
     +--> ReplicaSet "myapp-abc123" (image v1) — scaled to 0 after a rollout
     +--> ReplicaSet "myapp-def456" (image v2) — CURRENT, scaled to desired replica count
                |
                +--> Pod, Pod, Pod  (actual running instances, matching v2's template)
```

```bash
kubectl get deployments,replicasets,pods -l app=myapp
# shows the full chain: one Deployment, its ReplicaSet(s), and the actual Pods
```

**Follow-up:**

I'd bring up that old ReplicaSets aren't kept around forever — `revisionHistoryLimit` on the Deployment spec controls how many old, scaled-to-zero ReplicaSets are retained for potential rollback, and I'd flag that this is a real, if small, operational trade-off (more retained history means more possible rollback targets and slightly more etcd/API-object overhead; too few means losing the ability to roll back several versions if a problem isn't caught immediately) worth setting deliberately rather than leaving at whatever the cluster's default happens to be.

**Source:** [Kubernetes — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

---

### 16. What Is a Service, and How Does It Differ From an Ingress?

**Answer:**

"A **Service** provides a stable network identity (a fixed ClusterIP and DNS name) for a *set* of Pods, selected by label, that would otherwise come and go with no stable address — Pods are ephemeral (recreated with new IPs constantly by their ReplicaSet), so anything wanting to reliably reach 'the current set of healthy pods matching this selector' needs a Service in front of them rather than hardcoding individual Pod IPs. A Service operates at the transport layer (TCP/UDP, by IP and port) and is fundamentally about **internal** (or, for certain Service types, basic external) load-balanced access to a group of Pods.

**Ingress** operates one layer up, at the HTTP/HTTPS layer, and solves a different problem: routing **external** traffic into the cluster based on hostname and URL path (`api.example.com/users` to one Service, `api.example.com/orders` to another), plus TLS termination — capabilities a plain Service (even a `LoadBalancer`-type one, which just exposes one Service externally via one cloud load balancer, with no path/host-based routing) doesn't provide on its own. In practice, a typical setup layers them: Ingress handles external HTTP routing and TLS, forwarding to one or more internal `ClusterIP`-type Services, each of which load-balances across its own set of Pods."

**Code:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: orders-service
spec:
  selector:
    app: orders          # routes to any Pod with this label, regardless of
  ports:                    # which specific Pods currently exist
  - port: 80
    targetPort: 8080
  type: ClusterIP          # internal-only, stable DNS name "orders-service"
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /orders
        pathType: Prefix
        backend:
          service:
            name: orders-service   # Ingress routes HTTP traffic INTO the Service
            port:
              number: 80
```

**Follow-up:**

I'd bring up that "Ingress" is a Kubernetes API *resource* describing desired routing rules, but it does nothing on its own without an **Ingress Controller** (nginx-ingress, Traefik, a cloud provider's own controller) actually running in the cluster to read those rules and configure a real load balancer/proxy accordingly — a common early confusion is creating an Ingress resource and expecting it to "just work" with no controller installed to actually implement it, which silently does nothing at all.

**Source:** [Kubernetes — Service](https://kubernetes.io/docs/concepts/services-networking/service/), [Kubernetes — Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)

---

### 17. What Is the Difference Between a ConfigMap and a Secret?

**Answer:**

"Both externalize configuration from a container image so the same image can run with different settings across environments without rebuilding — mounted as files or exposed as environment variables to a Pod. The distinction is purely about **intent and handling**, not encryption by default: a `ConfigMap` is for non-sensitive configuration (a feature flag, a log level, a service URL); a `Secret` is for sensitive values (passwords, API keys, TLS certificates) and gets handled with additional care by the cluster — stored base64-encoded (not encrypted, just encoded, unless you separately enable encryption-at-rest for etcd) and `kubectl describe secret` specifically redacts the values (it prints byte counts, not content) the way it doesn't for a ConfigMap, reducing accidental shoulder-surfing exposure during routine `describe`-driven debugging. That redaction is `describe`-specific, though — it's not a general access control: `kubectl get secret -o yaml` (or `-o json`) prints the full `data` block, and the values there are only base64-encoded, not encrypted, so anyone who can run that command can trivially decode them. Actually restricting who can read a Secret's contents means RBAC on the `secrets` resource, not relying on `describe`'s redaction.

The genuinely important caveat: a plain Kubernetes Secret, without encryption-at-rest enabled on etcd, is only *encoded*, not encrypted — anyone with API access to read the Secret object (or direct etcd access) can trivially decode it. For real secret-management rigor, most teams either enable etcd encryption-at-rest, or use an external secrets manager (Vault, AWS Secrets Manager, cloud-provider secret stores) integrated via a CSI driver or an operator that syncs secrets into the cluster."

**Code:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "info"          # plain text, visible via `kubectl get configmap -o yaml`
---
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  password: cGFzc3dvcmQ=      # base64-ENCODED, not encrypted — trivially reversible
```

```yaml
# Consuming both in a Pod, identically shaped despite the different sensitivity
env:
- name: LOG_LEVEL
  valueFrom:
    configMapKeyRef: { name: app-config, key: LOG_LEVEL }
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef: { name: db-credentials, key: password }
```

**Follow-up:**

I'd bring up that this base64-not-encryption gap is a genuinely common misunderstanding worth correcting explicitly in a design review — a team that treats "we're using Kubernetes Secrets" as equivalent to "our secrets are encrypted" without separately verifying etcd encryption-at-rest is enabled has a real, if easily-fixed, gap; and I'd also mention that mounting a Secret as a **file** (rather than an environment variable) is generally the safer default, since environment variables are more easily leaked (accidentally logged, exposed via a debugging endpoint, inherited by child processes) than a file with restricted permissions.

**Source:** [Kubernetes — ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/), [Kubernetes — Secret](https://kubernetes.io/docs/concepts/configuration/secret/)

---

### 18. Explain Declarative vs. Imperative Management in `kubectl`

**Answer:**

"**Imperative** commands tell Kubernetes exactly what action to take right now — `kubectl run`, `kubectl expose`, `kubectl scale` — directly mutating cluster state via a specific command. This is fast for one-off exploration or debugging, but it doesn't leave behind any durable, reviewable record of what was done or why, and running the same imperative command twice can behave inconsistently depending on current state.

**Declarative** management instead describes the *desired end state* in a YAML manifest and applies it via `kubectl apply -f`, letting Kubernetes compute and execute whatever changes are needed to reconcile current state with that desired state — and critically, `kubectl apply` is safely **idempotent**: applying the exact same manifest repeatedly produces the same end result, and applying a *changed* manifest only touches the fields that actually differ, using a three-way diff (comparing the manifest, the last-applied-configuration annotation, and live cluster state) rather than blindly overwriting the whole object. This is what makes declarative manifests suitable for storing in version control and applying via CI/CD (GitOps) — the manifest itself is the durable, reviewable source of truth, and the cluster is just a reflection of whatever's currently committed."

**Code:**

```bash
# Imperative — fast, but no durable record of what was done or why
kubectl run myapp --image=myapp:1.0
kubectl scale deployment myapp --replicas=5

# Declarative — desired state in a version-controlled file, idempotent to apply
kubectl apply -f deployment.yaml
# running this again with the SAME file: no-op, nothing changes
# running it again with an UPDATED replica count in the file: only that field changes
```

**Follow-up:**

I'd bring up GitOps (Argo CD, Flux) as the natural extension of the declarative model — instead of a human or CI pipeline running `kubectl apply` directly against the cluster, a GitOps controller running *inside* the cluster continuously watches a Git repository and reconciles cluster state to match whatever's committed there, which gives you both an audit trail (every cluster change corresponds to a Git commit) and drift detection (if someone manually changes something in the cluster outside of Git, the controller notices the divergence from the declared state and can automatically revert it, or at minimum alert on it).

**Source:** [Kubernetes — Object Management](https://kubernetes.io/docs/concepts/overview/working-with-objects/object-management/)

---

## Kubernetes — Intermediate

### 19. Explain the Kubernetes Control Plane Components and What Each One Actually Does

**Answer:**

"The control plane is the set of components that make cluster-wide decisions and maintain desired state, distinct from the worker nodes that actually run application Pods.

**`kube-apiserver`** is the single front door to the cluster — every read and write (from `kubectl`, from other control-plane components, from controllers) goes through it; it validates and persists objects, and exposes the REST API everything else is built on. **`etcd`** is the cluster's actual database — a distributed, consistent key-value store holding every object's state (question 30 covers why its health is disproportionately critical). **`kube-scheduler`** watches for newly-created Pods with no assigned node and decides which node each should run on, based on resource requests, constraints, and policies (question 22). **`kube-controller-manager`** runs the various controller loops (the ReplicaSet controller, the Node controller, and others) that continuously watch actual state versus desired state and take action to reconcile any difference — this is the actual mechanism behind 'Kubernetes self-heals,' not magic, just a continuous watch-and-reconcile loop per resource type. **`cloud-controller-manager`** (in a cloud-managed cluster) handles cloud-provider-specific integration — provisioning a real cloud load balancer when a `LoadBalancer`-type Service is created, for instance — keeping that cloud-specific logic out of the core Kubernetes codebase."

**Code:**

```text
kube-apiserver   <-- single entry point, ALL reads/writes go through here
      |
      v
   etcd          <-- the actual persisted state (every object, every status)
      ^
      |
kube-scheduler          <-- watches for unscheduled Pods, assigns a node
kube-controller-manager <-- watches desired vs actual state, reconciles
cloud-controller-manager <-- cloud-provider-specific integration (LBs, volumes)
```

```bash
kubectl get componentstatuses    # (deprecated, but illustrative) — or, in a
                                    # modern cluster, check control-plane Pod
                                    # health directly in the kube-system namespace
kubectl get pods -n kube-system
```

**Follow-up:**

I'd bring up that the "controller" pattern (watch actual state, compare to desired state, reconcile the difference, repeat) is the single unifying design principle behind almost everything Kubernetes does — Deployments, HPA, and even most third-party Operators are all instances of exactly this same reconciliation-loop pattern applied to different resource types, and understanding that one pattern deeply explains far more of Kubernetes' actual behavior than memorizing each controller's specific behavior independently.

**Source:** [Kubernetes — Components](https://kubernetes.io/docs/concepts/overview/components/)

---

### 20. What Is the Kubelet, and How Does the Container Runtime Interface (CRI) Fit In?

**Answer:**

"The **kubelet** is the node-level agent running on every worker node — it's the thing that actually watches the API server for Pods assigned to *its* node, and makes them real: pulling images, starting/stopping containers, running probes (question 21), and reporting the node's and Pods' status back to the API server. It's the bridge between 'the control plane decided this Pod should run here' and 'a container is actually running.'

The kubelet doesn't run containers itself directly — it delegates that to a separate **container runtime** (containerd, CRI-O) via the **Container Runtime Interface (CRI)**, a standardized gRPC API. This decoupling exists specifically so Kubernetes doesn't need to hardcode support for one specific container runtime — any runtime that implements the CRI contract can be used interchangeably, which is exactly why Kubernetes was able to drop direct Docker Engine support (Docker itself doesn't implement CRI natively; it historically needed a shim, `dockershim`, which was deprecated in Kubernetes v1.20 and removed in v1.24) without breaking compatibility with images or workloads at all, since the *image format* (OCI-compliant) is separate from the runtime that executes it."

**Code:**

```text
kube-apiserver
      |
      v (Pod assigned to Node X)
  kubelet (on Node X)
      |
      v  CRI (gRPC)
  containerd / CRI-O   <-- actually creates/manages the container
      |
      v  OCI runtime spec
  runc (or gVisor/Kata, question 13) <-- actually creates the isolated process
```

```bash
# Checking which container runtime a node is actually using
kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.containerRuntimeVersion}'
```

**Follow-up:**

I'd bring up the Docker/dockershim deprecation specifically as a good, concrete illustration of why this layered abstraction (CRI, and separately OCI for images and runtimes) matters operationally, not just architecturally — plenty of teams were understandably alarmed when "Docker support" was removed from Kubernetes, but since images remained OCI-compliant and containerd (which Docker itself is built on) fully implements CRI, workloads kept running completely unaffected; the actual impact was almost entirely limited to teams who had built tooling that directly depended on the Docker Engine socket being present on nodes, not on anything about how their images or Pods behaved.

**Source:** [Kubernetes — Container Runtime Interface (CRI)](https://kubernetes.io/docs/concepts/architecture/cri/)

---

### 21. Explain Readiness, Liveness, and Startup Probes — and What Happens If You Configure Them Wrong

**Answer:**

"These three probes answer different questions, and conflating them is one of the most common real production mistakes in Kubernetes manifests. **Readiness** asks 'can this Pod currently accept traffic' — failing readiness removes the Pod from Service endpoints (it stops receiving new requests) but does **not** restart it; this is the right probe for a temporary, recoverable condition (warming a cache, a brief downstream dependency blip) where you want traffic paused, not the Pod killed. **Liveness** asks 'is this Pod in a broken state that only a restart can fix' — failing liveness causes the kubelet to **kill and restart** the container; this should only reflect genuinely unrecoverable application-level deadlock or corruption, never a transient external dependency issue. **Startup** exists specifically for slow-starting applications — it delays liveness/readiness checks from even beginning until the startup probe first succeeds, preventing a legitimately slow-to-initialize application from being killed by liveness checks that fire before it's ever had a chance to become healthy.

The most damaging misconfiguration, and one I'd specifically watch for in review: wiring a liveness probe to check a downstream dependency (a database connection) rather than pure internal application health — if that dependency has a brief, shared outage, **every** Pod's liveness probe fails simultaneously, and Kubernetes restarts every Pod at once, turning a transient, recoverable downstream blip into a self-inflicted, cluster-wide restart storm, exactly the same failure mode covered in the Spring Boot Internals file's liveness/readiness question, just at the Kubernetes-probe-configuration layer instead of the application-code layer."

**Code:**

```yaml
livenessProbe:            # ONLY checks genuinely internal, restart-fixable health —
  httpGet:
    path: /healthz/live      # NEVER a downstream dependency check
  periodSeconds: 10
  failureThreshold: 3
readinessProbe:           # can legitimately reflect downstream dependency health —
  httpGet:                   # a failure here PAUSES traffic, doesn't restart the Pod
    path: /healthz/ready
  periodSeconds: 5
startupProbe:             # delays liveness checks until the app has genuinely
  httpGet:                   # finished a slow initialization, avoiding a premature kill
    path: /healthz/startup
  failureThreshold: 30
  periodSeconds: 10          # up to 300s of startup grace before liveness even begins
```

**Follow-up:**

I'd bring up this exact restart-storm failure mode as a required design-review question for any new service's probe configuration — "if our primary database has a brief outage, do all of our Pods restart simultaneously, or do they correctly just stop receiving traffic and recover on their own once the database returns" — and I'd treat a liveness probe that transitively depends on any external system as a defect to fix immediately, since it converts an external, recoverable degradation into a self-inflicted, synchronized restart across the entire fleet at precisely the worst possible moment.

**Source:** [Kubernetes — Configure Liveness, Readiness, and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

---

### 22. How Does Kubernetes Decide Which Node to Schedule a Pod On?

**Answer:**

"The scheduler's decision has two phases. **Filtering**: eliminate every node that can't possibly run the Pod at all — insufficient available CPU/memory relative to the Pod's resource **requests** (question 26), a node explicitly tainted against this Pod without a matching toleration, a node that doesn't satisfy the Pod's required node affinity/anti-affinity rules, or a node with insufficient available ports/volumes. **Scoring**: among the remaining, viable nodes, rank them by a set of weighted priority functions — spreading Pods across nodes/zones for availability, balancing resource utilization across the cluster, preferring nodes that already have the Pod's image cached (faster startup), and any custom scoring policies configured — and pick the highest-scoring node.

**Taints and tolerations** work as an explicit repel-unless-tolerated mechanism: a taint on a node (`kubectl taint nodes node1 dedicated=gpu:NoSchedule`) means no Pod schedules there *unless* that Pod explicitly declares a matching toleration — the right tool for reserving specific nodes (GPU nodes, for instance) for only the workloads that specifically need them, rather than having every general-purpose Pod compete for that specialized capacity. **Node affinity/anti-affinity** works the opposite direction — expressing a Pod's *preference or requirement* for particular node characteristics (a specific zone, a specific hardware label), or, via Pod anti-affinity, a requirement to *avoid* being co-located with other specific Pods (spreading replicas of the same Deployment across different nodes/zones for resilience)."

**Code:**

```bash
kubectl taint nodes gpu-node-1 dedicated=gpu:NoSchedule
# repels EVERY Pod from this node UNLESS it explicitly tolerates this taint
```

```yaml
spec:
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"       # this Pod CAN be scheduled on the tainted node
  affinity:
    podAntiAffinity:            # spread replicas across different nodes,
      requiredDuringSchedulingIgnoredDuringExecution:  # not clustered on one
      - labelSelector:
          matchExpressions:
          - {key: app, operator: In, values: [myapp]}
        topologyKey: "kubernetes.io/hostname"
```

**Follow-up:**

I'd bring up "IgnoredDuringExecution" (the suffix on both affinity rule types) as a specific, easy-to-miss detail: these rules are only evaluated *at scheduling time* — if a node's labels change, or another Pod is added later such that an existing Pod's affinity/anti-affinity rule would now be violated, Kubernetes does **not** retroactively evict or reschedule the already-running Pod to correct it; the rule only ever gates *new* placement decisions, not the ongoing validity of already-scheduled Pods, which is worth knowing explicitly rather than assuming affinity rules are continuously, actively enforced.

**Source:** [Kubernetes — Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/), [Kubernetes — Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)

---

### 23. Explain How a Deployment Performs a Rolling Update, and How a Rollback Actually Works

**Answer:**

"By default, a Deployment update uses the `RollingUpdate` strategy, governed by two parameters: `maxSurge` (how many *extra* Pods beyond the desired count can exist temporarily during the rollout) and `maxUnavailable` (how many of the desired count can be unavailable at once during the rollout). The rollout proceeds incrementally: create a few new-version Pods (up to `maxSurge` above the target count), wait for them to pass their readiness probe, then remove an equivalent number of old-version Pods, repeating this cycle until every Pod is running the new version — at no point does the total available capacity drop below `desired - maxUnavailable`, and the whole process is naturally paced by how quickly new Pods actually become ready, tying directly into question 21's readiness-probe correctness (a broken readiness probe that always reports 'ready' immediately would let a rollout to a genuinely broken new version proceed at full speed, defeating the entire safety mechanism).

A **rollback** (`kubectl rollout undo`) is mechanically the exact same rolling-update process, just targeting the previous ReplicaSet's Pod template as the new desired state instead of a forward change — which is exactly why old ReplicaSets are kept around (question 15) rather than deleted after a successful rollout: a rollback needs that previous template readily available to roll back *to*, without needing to reconstruct it from scratch."

**Code:**

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # up to 1 EXTRA pod above desired count during rollout
      maxUnavailable: 0    # NEVER drop below desired count — zero-downtime rollout
  replicas: 3
```

```bash
kubectl rollout status deployment/myapp     # watch the rollout progress live
kubectl rollout history deployment/myapp     # see previous revisions
kubectl rollout undo deployment/myapp        # roll back to the PREVIOUS revision
kubectl rollout undo deployment/myapp --to-revision=2   # roll back to a SPECIFIC one
```

**Follow-up:**

I'd bring up that `maxUnavailable: 0` combined with `maxSurge: 1` (or higher) is the correct configuration for genuinely zero-downtime rollouts specifically because it guarantees capacity never drops below the desired count at any point, at the cost of briefly running more total Pods than the steady-state desired count (temporarily needing the cluster capacity headroom to support that surge) — and I'd flag that a rollout can still appear to "succeed" from Kubernetes' perspective (every new Pod passed its readiness probe) while the application is actually broken in a way the readiness probe doesn't detect, which is exactly why readiness-probe *quality* — not just its presence — is the real safety mechanism underlying the whole rolling-update guarantee, tying directly back to the Spring Boot Internals file's discussion of what a readiness probe should actually check.

**Source:** [Kubernetes — Deployments (Rolling Update)](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

---

### 24. How Does Kubernetes Networking Actually Work End to End?

**Answer:**

"Kubernetes itself doesn't implement Pod networking directly — it delegates to a **CNI (Container Network Interface)** plugin (Calico, Cilium, Flannel, or a cloud provider's own VPC-native CNI), which is responsible for satisfying Kubernetes' core networking requirement: every Pod gets its own IP address, and every Pod can reach every other Pod's IP directly, cluster-wide, without NAT — a flat networking model, regardless of which nodes the two Pods happen to be on.

**Service** ClusterIPs are a layer on top of that Pod networking, implemented by **kube-proxy** running on every node — it watches the API server for Service and Endpoint changes, and programs the node's networking rules (via iptables, or the more modern and performant IPVS mode) so that traffic sent to a Service's stable ClusterIP gets transparently load-balanced across the actual, current set of healthy backing Pod IPs. This is why a Service's ClusterIP is stable even as its backing Pods are constantly recreated with new IPs — kube-proxy continuously updates the underlying routing rules to reflect current Endpoint membership, and clients never need to know or care about individual Pod IPs at all."

**Code:**

```text
Pod A (10.244.1.5) -- wants to reach Service "orders-service" (10.96.0.50)
      |
      v
kube-proxy's iptables/IPVS rules on Pod A's node (programmed from watching
Endpoints for "orders-service") transparently rewrite the destination to
one of the CURRENT healthy backing Pods, e.g. 10.244.2.9
      |
      v
Pod B (10.244.2.9) -- receives the traffic, Pod A never knew its actual IP
```

```bash
kubectl get endpoints orders-service    # the ACTUAL current Pod IPs backing
                                           # this Service's stable ClusterIP right now
```

**Follow-up:**

I'd bring up that CNI plugin choice is a genuinely consequential platform decision, not an interchangeable implementation detail — Cilium (eBPF-based) offers meaningfully better performance and much richer network-policy capabilities (including L7-aware policies) than a basic iptables-based CNI, at the cost of a steeper learning curve and, historically, requiring a sufficiently modern kernel; I'd frame the choice as depending on whether the cluster's actual network-policy and performance requirements genuinely need that added capability, rather than defaulting to whichever CNI happened to be the cloud provider's out-of-the-box default without evaluating it against real requirements.

**Source:** [Kubernetes — Service Networking](https://kubernetes.io/docs/concepts/services-networking/), [Container Network Interface (CNI)](https://www.cni.dev/)

---

### 25. When Do You Need a StatefulSet Instead of a Deployment?

**Answer:**

"A Deployment treats its Pods as fully interchangeable — any Pod can be replaced by any other, they get random names/IPs, and there's no notion of a specific Pod's individual identity or storage persisting across a restart. A **StatefulSet** exists specifically for workloads where individual Pod identity genuinely matters: each Pod gets a **stable, predictable name** (`myapp-0`, `myapp-1`, `myapp-2` — not a random suffix), a **stable network identity** (a predictable DNS name per Pod, via a headless Service), and, critically, **stable, per-Pod persistent storage** — `myapp-1`'s `PersistentVolumeClaim` follows *that specific Pod* across restarts/rescheduling, rather than a Deployment's Pods, which get an entirely fresh volume (or none) each time they're recreated.

This matters for exactly the workloads where 'which specific instance this is, and what data it already has' is meaningful — a database cluster (each replica has its own distinct data directory and needs to consistently reconnect to the *same* data on restart, not an arbitrary sibling's), or any distributed system doing its own internal leader election/quorum where node identity matters (a Kafka broker, a Zookeeper/etcd cluster member). StatefulSets also, by default, create and scale Pods **sequentially and in order** (`myapp-0` must be Running and Ready before `myapp-1` is created), which matters for systems with ordered startup dependencies between replicas."

**Code:**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: myapp
spec:
  serviceName: "myapp-headless"    # headless Service — enables per-Pod stable DNS
  replicas: 3
  volumeClaimTemplates:              # each Pod gets its OWN PVC, following IT
  - metadata: { name: data }           # specifically across restarts/rescheduling
    spec:
      accessModes: ["ReadWriteOnce"]
      resources: { requests: { storage: 10Gi } }
```

```text
myapp-0.myapp-headless.default.svc.cluster.local   <- stable per-Pod DNS name
myapp-1.myapp-headless.default.svc.cluster.local   <- each Pod individually addressable
```

**Follow-up:**

I'd bring up that many teams reach for a StatefulSet reflexively for "anything with a database in the name," when a large fraction of genuinely stateful workloads today are actually better served by a managed cloud database service (RDS, Cloud SQL) rather than self-hosting a StatefulSet-based database inside Kubernetes at all — running your own stateful data store on Kubernetes is a real, ongoing operational commitment (backup/restore, failover, version upgrades all become your team's responsibility rather than a managed provider's), and I'd treat "should this actually run as a StatefulSet in our own cluster, or should it be a managed external service" as the prior, more important question before getting into StatefulSet configuration details at all.

**Source:** [Kubernetes — StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)

---

### 26. Explain Resource Requests/Limits and Kubernetes' QoS Classes

**Answer:**

"A **request** is what the scheduler uses to decide placement — it's the amount of CPU/memory a container is guaranteed to get, and the sum of all requests on a node can never exceed that node's allocatable capacity (this is what the scheduler's filtering phase, question 22, actually checks). A **limit** is the hard ceiling — a container can burst above its request (using spare, currently-unused capacity on the node) up to its limit, but never beyond it: exceeding a CPU limit gets the process throttled; exceeding a memory limit gets the container **OOM-killed** by the kernel, restarted by the kubelet.

These two settings, present or absent, determine a Pod's **QoS class**, which matters directly for eviction order under node pressure. **Guaranteed** (every container's limits equal its requests, for both CPU and memory) is evicted last — Kubernetes gives these the strongest guarantee since their resource usage is fully predictable and bounded. **Burstable** (requests set, but limits absent or higher than requests) is evicted before Guaranteed but after BestEffort. **BestEffort** (no requests or limits set at all) is evicted first under any node memory pressure, since it's providing zero guarantee of its actual needs to the scheduler at all."

**Code:**

```yaml
resources:
  requests:
    cpu: "500m"          # guaranteed floor — scheduler uses this for placement
    memory: "256Mi"
  limits:
    cpu: "500m"           # equal to requests -> Guaranteed QoS, evicted LAST
    memory: "256Mi"          # under node memory pressure

# vs. Burstable:
resources:
  requests: { cpu: "250m", memory: "128Mi" }
  limits:   { cpu: "1000m", memory: "512Mi" }   # can burst up to 4x request —
                                                    # evicted BEFORE Guaranteed pods
```

**Follow-up:**

I'd bring up that unset resource requests are a common, genuinely dangerous production gap — a Pod with no requests/limits at all gets BestEffort QoS (first to be evicted under any pressure) but *also* provides the scheduler zero information to make a sound placement decision with, meaning it can be scheduled onto an already-heavily-loaded node with no safeguard at all; I'd treat "every container has an explicit, deliberately-chosen request and limit" as close to a hard requirement for any production workload, and I'd specifically flag CPU limits as worth extra scrutiny — a CPU limit that's set too tight silently throttles a Pod (degrading its actual performance) without ever killing or restarting it, which is a much harder failure mode to notice and diagnose than an OOM-kill, since there's no crash or restart event, just quietly degraded latency.

**Source:** [Kubernetes — Managing Resources for Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), [Kubernetes — Pod Quality of Service Classes](https://kubernetes.io/docs/tasks/configure-pod-container/quality-service-pod/)

---

### 27. How Does the Horizontal Pod Autoscaler Work?

**Answer:**

"The HPA is a controller (following the same watch-and-reconcile pattern from question 19) that periodically checks a Pod's actual observed metric (CPU utilization by default, but also custom or external metrics via the metrics API) against a target value you configure, and adjusts a Deployment's (or StatefulSet's) replica count up or down to try to bring the observed metric back toward that target. Concretely: if you target 50% average CPU utilization and observed utilization across all Pods averages 80%, the HPA computes a new desired replica count roughly proportional to the ratio (current replicas × current-metric/target-metric) and scales up; if utilization drops well below target, it scales down, subject to a stabilization window that prevents rapid oscillation (scaling up and down repeatedly in response to noisy, short-lived metric spikes).

The HPA requires the **Metrics Server** (or a custom/external metrics adapter, for anything beyond basic CPU/memory) to be running in the cluster to actually source the utilization data it needs — without it, the HPA has nothing to make scaling decisions against at all, and simply can't function, which is a common gap in a newly-set-up cluster that hasn't had the metrics pipeline configured yet."

**Code:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50    # target 50% average CPU across all Pods
```

```bash
kubectl get hpa myapp-hpa    # watch current replicas vs. target metric live
```

**Follow-up:**

I'd bring up that CPU-based autoscaling is a poor fit for a genuinely large class of real workloads — a service whose actual bottleneck is I/O-bound (waiting on a downstream call or a database, per the concurrency file's discussion) can have low CPU utilization while still being genuinely overloaded and needing more replicas, which is exactly the kind of workload where custom-metric-based autoscaling (queue depth, request latency, in-flight request count) is a much more accurate scaling signal than CPU alone — and I'd treat "does our chosen scaling metric actually correlate with real overload for this specific workload" as a question worth validating empirically, not assuming CPU utilization is automatically the right proxy for every service.

**Source:** [Kubernetes — Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

---

## Kubernetes — Staff Level

### 28. How Would You Design Multi-Tenancy on a Shared Kubernetes Cluster?

**Answer:**

"I'd apply layered isolation, since no single Kubernetes primitive provides complete tenant isolation on its own — this mirrors exactly the tenant-isolation discipline from the Spring Security file, just implemented at the cluster-infrastructure layer instead of the application layer. **Namespaces** as the primary organizational and API-scoping boundary — every tenant's resources live in their own namespace(s), which is what most other isolation mechanisms attach to. **RBAC**, scoped per-namespace via `RoleBinding` (not `ClusterRoleBinding`), so a tenant's own service accounts and users can only act within their own namespace, never across tenant boundaries. **`NetworkPolicy`** to actually enforce network-level isolation between tenants' Pods — without an explicit deny-by-default NetworkPolicy, every Pod in the cluster can reach every other Pod's IP directly regardless of namespace (question 24's flat networking model), so namespaces alone provide *zero* network isolation on their own; NetworkPolicy is what actually closes that gap. **`ResourceQuota`** per namespace to prevent one tenant from consuming disproportionate cluster capacity and starving others (a noisy-neighbor problem, directly connecting to the concurrency file's bulkhead-isolation principle, applied at the cluster level). And for genuinely untrusted tenants specifically (question 13's threat-model distinction), dedicated node pools with taints reserving those nodes for that tenant's Pods only, or a stronger-isolation runtime (gVisor/Kata) rather than relying on standard container isolation alone."

**Code:**

```yaml
# Deny-by-default NetworkPolicy — WITHOUT this, namespaces provide ZERO
# actual network isolation between tenants at all
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-cross-namespace
  namespace: tenant-a
spec:
  podSelector: {}              # applies to EVERY pod in this namespace
  policyTypes: ["Ingress"]
  ingress:
  - from:
    - namespaceSelector:
        matchLabels: { name: tenant-a }   # ONLY allow traffic from the SAME tenant
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-a-quota
  namespace: tenant-a
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    pods: "50"                  # bounds this tenant's TOTAL resource consumption,
```                              # preventing a noisy-neighbor impact on other tenants

**Follow-up:**

I'd bring up that "namespace-based soft multi-tenancy" (what the above achieves) is a genuinely different, weaker guarantee than "hard multi-tenancy" (separate clusters per tenant, or the gVisor/Kata-strengthened isolation from question 13) — and I'd make the actual trade-off explicit in a design review: soft multi-tenancy is far cheaper to operate (one cluster, shared control-plane overhead, easier cross-tenant platform tooling) but ultimately still shares one kernel and one control plane across tenants, which is an acceptable risk for internal teams that trust each other but a much harder sell for genuinely adversarial or contractually-isolated external tenants, where separate clusters (accepting the real operational cost multiplication) is often the more defensible choice regardless of the added infrastructure overhead.

**Source:** [Kubernetes — RBAC Good Practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/), [Kubernetes — Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/), [Kubernetes — Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)

---

### 29. A Pod Is Stuck in `CrashLoopBackOff` / `Pending` / `ImagePullBackOff` — Walk Through Your Diagnosis

**Answer:**

"Each of these three points at a genuinely different failure category, and I'd branch the investigation immediately based on which one it is, rather than one generic 'the pod is broken' response.

**`Pending`** means the Pod hasn't even been scheduled to a node yet — the cause lives in the scheduler's filtering phase (question 22): insufficient cluster capacity for the Pod's resource requests anywhere, an unsatisfiable node affinity/taint requirement, or (for a StatefulSet/PVC-backed Pod) a `PersistentVolumeClaim` that can't be bound to any available storage. `kubectl describe pod` surfaces the exact scheduling failure reason directly in its Events section — this is almost always the fastest path to the answer, not something requiring deeper log-diving.

**`ImagePullBackOff`** means the kubelet can't pull the specified container image — wrong image name/tag, a private registry requiring credentials the node doesn't have (missing or misconfigured `imagePullSecrets`), or a network-level inability to reach the registry from that node. Again, `kubectl describe pod` shows the exact pull error message directly.

**`CrashLoopBackOff`** means the container *is* starting, but exiting (crashing, or completing and exiting cleanly when it's expected to be a long-running process) repeatedly, with Kubernetes applying exponential backoff between restart attempts. Here I'd go straight to `kubectl logs <pod> --previous` (the *previous* crashed instance's logs, since the current instance may not have logged anything meaningful yet, or may already be in another crash) to see the actual application-level error causing the exit — a missing required environment variable, a failed startup dependency check, or an uncaught exception during initialization are the most common real causes."

**Code:**

```bash
kubectl describe pod myapp-xyz
# Events section shows the EXACT reason: scheduling failure details,
# image pull error message, or OOMKilled/exit-code details

kubectl logs myapp-xyz --previous
# the actual application output from the PREVIOUS (crashed) instance —
# critical for CrashLoopBackOff, since the CURRENT instance may have crashed
# again before producing any useful log output at all

kubectl get events --sort-by='.lastTimestamp' -n mynamespace
# broader event timeline — useful when the Pod's OWN description doesn't
# fully explain it (e.g., a node-level issue affecting several Pods at once)
```

**Follow-up:**

I'd bring up that `CrashLoopBackOff` specifically deserves a follow-up question before diving into logs: was the container OOM-killed (`kubectl describe pod` shows `Reason: OOMKilled` in the last-state section) rather than crashing due to an application bug — this is a completely different root cause (the memory limit, question 26, is too tight for the application's actual working set, not a code defect) requiring a completely different fix (raise the limit, or find and fix a genuine memory leak) than an application-level exception would, and conflating the two by jumping straight to reading application logs without first checking the exit reason/code is a common, avoidable diagnostic misstep.

**Source:** [Kubernetes — Debug Running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/)

---

### 30. Why Is `etcd` the Piece of the Cluster You Should Worry About Most, Operationally?

**Answer:**

"Every single piece of cluster state — every object, every status, every configuration — lives in etcd, and the API server is fundamentally a thin layer in front of it; nothing else in the control plane has any independent memory of cluster state at all. This means etcd's health directly gates the health of the *entire* control plane: if etcd is slow, every API server request (from `kubectl`, from every controller's watch loop, from the scheduler) is slow; if etcd loses quorum or its data, the cluster's control plane has effectively lost its mind — it may not even know what Pods are supposed to be running, let alone be able to reconcile toward that state.

etcd is a **Raft-based consensus store**, meaning it requires a strict majority of its members to be healthy and reachable to accept writes at all — a 3-node etcd cluster tolerates exactly 1 node failure; a 5-node cluster tolerates 2; but a 2-node cluster (an easy, tempting cost-cutting mistake) tolerates **zero** failures despite technically having 'redundancy,' since losing either of 2 nodes breaks the majority-quorum requirement entirely. This is exactly why etcd cluster sizing needs to be an odd number, deliberately chosen, not an arbitrary 'more nodes = more redundant' assumption — and why etcd's own disk I/O latency (it's highly sensitive to slow disk writes, since every write must be durably committed to a majority of members before being acknowledged) is one of the most important, and most commonly under-monitored, health signals for an entire cluster's actual responsiveness."

**Code:**

```bash
# etcd's own health/performance, DIRECTLY affects EVERY control-plane operation
etcdctl endpoint health --cluster
etcdctl endpoint status --cluster -w table   # check leader, DB size, latency

# Disk I/O latency is THE critical etcd health metric — slow disks make
# EVERY cluster operation slow, cluster-wide, regardless of node/pod count
```

```text
etcd cluster size vs. fault tolerance (requires STRICT MAJORITY to keep writing):
  1 node:  tolerates 0 failures
  3 nodes: tolerates 1 failure  (majority = 2 of 3)
  5 nodes: tolerates 2 failures (majority = 3 of 5)
  2 nodes: tolerates 0 failures — WORSE than 1 node in terms of real fault
           tolerance despite "looking" more redundant (majority of 2 = 2)
```

**Follow-up:**

I'd bring up that this is exactly why managed Kubernetes offerings (EKS, GKE, AKS) hide etcd entirely from the user and manage it as part of the control-plane SLA — for a self-managed cluster, I'd treat etcd backup/restore procedures (genuinely tested, not just configured and assumed to work) as one of the single highest-priority operational readiness items, since a cluster that loses etcd with no working backup has, in practice, lost the entire cluster's state — every Deployment, Service, Secret, and ConfigMap definition — with no path back except rebuilding everything from external source-of-truth manifests (which is exactly why GitOps, question 18, is also a disaster-recovery strategy, not just a deployment-workflow convenience).

**Source:** [etcd Documentation](https://etcd.io/docs/latest/)

---

### 31. How Do You Actually Achieve Zero-Downtime Deployments on Kubernetes?

**Answer:**

"This requires several distinct mechanisms working together, and missing any one of them reintroduces a brief window of dropped requests during an otherwise-successful-looking rollout. **Correct readiness probes** (question 21) so traffic is never sent to a Pod before it's actually ready to handle it, and rolling-update parameters (question 23, `maxUnavailable: 0`) so capacity never dips below the desired count during the rollout itself.

**Graceful termination**: when a Pod is being terminated (during a rollout, a scale-down, or a node drain), Kubernetes sends `SIGTERM`, waits up to `terminationGracePeriodSeconds` (default 30s), then `SIGKILL`s anything still running — but critically, the Pod is *simultaneously* removed from Service endpoints (so no *new* traffic routes to it) while still being given time to finish in-flight requests; an application that doesn't correctly handle `SIGTERM` (question 10's PID-1-signal-handling problem, applied here at the orchestration layer) gets hard-killed mid-request instead of finishing gracefully. There's also a real, easy-to-miss race here: the 'remove from Service endpoints' signal and the 'send SIGTERM' signal happen concurrently, not endpoint-removal-then-signal — meaning a very small window can exist where a request is routed to a Pod that's already begun terminating; a brief `preStop` hook sleep (a few seconds) is a common, pragmatic mitigation specifically to cover the propagation delay before the container actually starts shutting down.

**`PodDisruptionBudget` (PDB)** to protect against *voluntary* disruptions (a node drain for maintenance, a cluster-autoscaler scale-down) evicting too many replicas of the same application simultaneously — without a PDB, a node drain could legally evict every replica of a Deployment at once if they all happened to be co-located, which no rolling-update parameter alone protects against, since a PDB constrains voluntary eviction operations specifically, a different code path than a Deployment's own rollout."

**Code:**

```yaml
spec:
  terminationGracePeriodSeconds: 30
  containers:
  - name: app
    lifecycle:
      preStop:
        exec:
          command: ["sh", "-c", "sleep 5"]  # covers the endpoint-removal
    # propagation gap BEFORE the app actually starts shutting down
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2       # a voluntary disruption (node drain, autoscaler) can
  selector:                # NEVER evict enough Pods to drop below this,
    matchLabels: { app: myapp }  # regardless of how many nodes are being drained at once
```

**Follow-up:**

I'd bring up that this exact combination — graceful termination, correct readiness probes, `maxUnavailable: 0`, and a PDB — is precisely the Kubernetes-native version of the same zero-downtime discipline covered in the Spring Boot Internals file's graceful-shutdown question, and I'd make that connection explicit in an interview: the application needs to cooperate correctly (handle `SIGTERM`, have an accurate readiness check) *and* the orchestration layer needs to be configured correctly (PDB, rollout parameters) — neither one alone is sufficient, and a genuinely zero-downtime deployment requires getting both halves right simultaneously, which is exactly why this is a recurring, multi-layered checklist rather than a single flag to set.

**Source:** [Kubernetes — Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), [Kubernetes — Configure PodDisruptionBudget](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)

---

### 32. How Would You Secure a Kubernetes Cluster End to End?

**Answer:**

"I'd layer this across the same categories a mature cluster's security posture actually needs, rather than treating any single control as sufficient. **Authentication and RBAC** — every human and service account should authenticate with a real identity (not a shared, broadly-scoped token) and be granted the minimum RBAC permissions actually needed for their role, scoped to specific namespaces via `RoleBinding` rather than cluster-wide `ClusterRoleBinding` wherever possible (question 28's multi-tenancy discipline, applied generally). **Pod Security Standards** — enforcing that Pods can't run as root, can't mount the host filesystem, can't use host networking/PID namespaces, and can't run in privileged mode unless there's a specific, reviewed exception — via the built-in Pod Security Admission controller (which replaced PodSecurityPolicy — deprecated in v1.21, removed in v1.25) applied at the namespace level. **Admission controllers** more broadly — beyond just Pod Security Standards, tools like OPA Gatekeeper or Kyverno let you enforce custom policy (require resource limits on every Pod, require images to come only from an approved registry, require a valid image signature per question 12) as a blocking gate on the API server, rather than relying on manual review to catch violations. **Network policy** (question 28) as deny-by-default rather than allow-by-default. **Secrets handling** (question 17) with etcd encryption-at-rest enabled, and ideally an external secrets manager rather than relying on plain Kubernetes Secrets alone. And **supply-chain security** (question 12) for every image actually running in the cluster, enforced via admission policy rather than just recommended practice."

**Code:**

```yaml
# Pod Security Standards enforced at the NAMESPACE level — blocks
# privileged/root/host-access Pods from ever being admitted at all
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
```

```yaml
# Kyverno/OPA Gatekeeper-style policy — blocking admission control,
# not just a recommendation developers might forget to follow
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-signed-images
spec:
  validationFailureAction: Enforce   # BLOCKS admission, doesn't just warn
  rules:
  - name: verify-image-signature
    match:
      resources: { kinds: ["Pod"] }
    verifyImages:
    - imageReferences: ["registry.mycompany.com/*"]
      attestors:
      - entries:
        - keys: { publicKeys: "..." }   # only admits images signed by a
```                                        # trusted key (question 12's supply-chain control)

**Follow-up:**

I'd bring up that the single highest-leverage shift in this whole list is moving from *advisory* policies (documentation saying "don't run containers as root") to *admission-enforced* ones (a policy that structurally makes it impossible to admit a Pod violating the rule) — exactly the same "make the right path the easy path, and the wrong path structurally impossible" principle from the Tech Leadership file's platform-standards discussion, applied here to cluster security specifically; a security posture that depends entirely on every engineer remembering and correctly following a written guideline, with no automated enforcement backing it, degrades in practice as an organization and its Kubernetes usage grow.

**Source:** [Kubernetes — Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/), [Kubernetes — Admission Controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/), [Kubernetes — RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

---

### 33. How Does a Service Mesh Relate to What Kubernetes Already Provides — and When Do You Actually Need One?

**Answer:**

"Kubernetes' built-in Service/kube-proxy mechanism (question 24) gives you basic load-balancing and service discovery, but nothing beyond that — no automatic mTLS between Pods, no fine-grained traffic-shaping (canary releases by percentage, retries/timeouts/circuit-breaking configured centrally rather than per-application), and no uniform, automatic per-service observability. A **service mesh** (Istio, Linkerd) adds all of this by deploying a sidecar proxy (question 11 in the Microservices & Architecture Patterns file covers the sidecar pattern in depth) alongside every Pod, intercepting all inbound/outbound traffic transparently, with a central control plane configuring every sidecar's behavior consistently across the whole mesh.

I'd apply exactly the same decision framework the Microservices & Architecture Patterns file lays out for service meshes generally: genuinely valuable for a large, polyglot fleet that needs uniform mTLS, consistent retry/circuit-breaking policy, and rich per-service traffic metrics without reimplementing them per-language — and a real, non-trivial operational cost (an extra network hop per call, a new critical piece of infrastructure, and real care needed to avoid retry-policy conflicts between the mesh layer and application-level resilience code, per that file's discussion) that isn't justified for a small-to-moderate single-language deployment where the framework's own built-in resilience features (or Kubernetes' native NetworkPolicy plus a simpler mTLS solution like cert-manager-issued certificates) already cover the actual requirement."

**Code:**

```text
WITHOUT a mesh — Kubernetes-native, basic load balancing only:
  Pod A --(kube-proxy routed)--> Pod B
  -- no automatic mTLS, no centrally-configured retries/circuit-breaking,
  -- no uniform per-call observability across services

WITH a mesh — sidecar intercepts ALL traffic, uniformly, per-Pod:
  Pod A [+ Envoy sidecar] --(mTLS, retries, metrics — ALL automatic)--> [+ Envoy sidecar] Pod B
  -- centrally configured via the mesh's control plane (Istio/Linkerd),
  -- consistent regardless of which language each Pod's app is written in
```

**Follow-up:**

I'd bring up that this is a direct, deliberate cross-reference to the Microservices & Architecture Patterns file's sidecar/service-mesh questions rather than a separate topic — the Kubernetes-specific detail worth adding is that a mesh's sidecar injection is usually implemented via a **Mutating Admission Webhook** (the same admission-control mechanism from question 32, applied here to automatically inject a sidecar container into every Pod matching a label, rather than requiring every team to manually add it to their own manifests) — which is itself a good, concrete example of admission control being used for automatic infrastructure injection, not just policy enforcement/blocking.

**Source:** [Istio Documentation](https://istio.io/latest/docs/concepts/what-is-istio/)

---

### 34. How Would You Approach Kubernetes Cluster Capacity Planning and Cost Optimization?

**Answer:**

"I'd start from **accurate resource requests** (question 26) as the actual foundation everything else depends on — the scheduler and the cluster autoscaler both make decisions based on requested (not actual) resource consumption, so a cluster full of Pods requesting far more than they actually use looks 'full' and forces unnecessary node scale-up, while a cluster full of Pods requesting far less than they actually use risks node-level oversubscription and noisy-neighbor problems; getting requests genuinely close to real observed usage (via historical metrics, or a tool like Kubernetes' Vertical Pod Autoscaler in recommendation-only mode) is the single highest-leverage lever for both cost and stability.

Beyond that: the **Cluster Autoscaler** adds/removes actual *nodes* based on aggregate Pod scheduling pressure (distinct from the HPA, question 27, which adds/removes *Pods* — the two work together, HPA deciding how many Pods are needed, Cluster Autoscaler ensuring enough node capacity exists to actually schedule them). **Bin-packing** — consolidating workloads onto fewer, more fully-utilized nodes rather than spreading them thin across many partially-empty ones, which most cluster autoscaler configurations and node-pool sizing strategies can be tuned toward. And **spot/preemptible instances** for workloads that can tolerate interruption (stateless, horizontally-scaled services with good readiness-probe and PDB discipline, question 31) at a substantial cost discount versus on-demand instances, reserved specifically for workloads where an occasional forced eviction is a genuinely acceptable trade, not applied blindly to stateful or interruption-sensitive workloads."

**Code:**

```yaml
# Vertical Pod Autoscaler in RECOMMENDATION-ONLY mode — surfaces what
# requests SHOULD be based on actual historical usage, without automatically
# changing anything, a good first step before tuning requests manually
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: myapp-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: myapp
  updatePolicy:
    updateMode: "Off"    # "Off" = recommendations only, doesn't auto-apply anything
```

```text
HPA vs Cluster Autoscaler — distinct, complementary layers:
  HPA:               "how many PODS do we need for current load?"
  Cluster Autoscaler: "do we have enough NODE capacity to actually schedule
                        the number of Pods HPA/scheduling currently wants?"
  -- HPA scaling UP Pods that then can't be scheduled (Pending, question 29)
  -- due to insufficient node capacity is EXACTLY what triggers Cluster
  -- Autoscaler to provision more nodes
```

**Follow-up:**

I'd bring up that cost optimization and reliability are in real, direct tension here and I'd be explicit about that trade-off rather than presenting cost-cutting as free — aggressive bin-packing and heavy spot-instance usage both increase the *rate* of Pod disruption/rescheduling events, which only stays safe if the corresponding reliability mechanisms (PDBs, readiness probes, graceful termination, question 31) are genuinely solid; I'd treat "how aggressively can we cost-optimize" as a question whose safe answer depends entirely on how mature those underlying reliability mechanisms already are, not a purely financial decision made independently of them.

**Source:** [Kubernetes Cluster Autoscaler](https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/README.md), [Kubernetes — Nodes](https://kubernetes.io/docs/concepts/architecture/nodes/)

---

### 35. Describe a Production Kubernetes Incident and How You'd Diagnose It

**Answer:**

"I'd walk through a representative shape rather than claim one specific universal story, mirroring the same honest framing this kit uses elsewhere for postmortem-style questions: a service's p99 latency degraded sharply during a routine, otherwise-unremarkable rolling deployment, and several requests failed outright during the rollout window — despite the Deployment's rollout status reporting success and every new Pod passing its readiness probe.

Root-causing followed the layered diagnostic sequence this file has built up: first, checking whether this was a scheduling/capacity issue (question 29) — ruled out, Pods scheduled and started normally. Second, checking the readiness probe's actual behavior versus what it *should* have verified — it turned out the probe checked only a shallow `/healthz` endpoint that returned healthy before the application had actually finished warming an in-memory cache used on the hot request path, so traffic was routed to 'ready' Pods that were still meaningfully slower than steady-state for their first several seconds of real traffic — exactly the readiness-probe-quality gap flagged in question 21/23, just discovered via a real incident rather than caught in review beforehand. Third, confirming via `kubectl logs` and request-tracing that the failed requests specifically correlated with the exact window each new Pod had just been marked ready, not spread randomly across the rollout — the smoking gun tying the failures directly to the probe gap rather than a broader, unrelated cause."

**Code:**

```text
Postmortem structure I'd actually use for this:

  1. TIMELINE — correlate the latency/error spike PRECISELY against rollout
     start/end times and individual Pod ready-transition timestamps
     (kubectl get events --sort-by=.lastTimestamp, cross-referenced against
     request-tracing data for the same window)

  2. ROOT CAUSE — readiness probe checked shallow liveness, not actual
     functional readiness (a warmed cache the hot path genuinely depended on)

  3. CONTRIBUTING FACTORS — no load-based validation of readiness-probe
     correctness before this went to production (question 21's guidance
     treated as a checklist item, not something actually TESTED against
     real startup behavior under real traffic); maxSurge/maxUnavailable
     configuration meant several under-warmed Pods received full traffic
     share simultaneously rather than one at a time

  4. WHAT WENT WELL — the Deployment's OWN rollout mechanics worked exactly
     as designed; this was a probe-CORRECTNESS gap, not a Kubernetes
     mechanism failure, which narrowed the fix to one specific, containable
     change rather than a deeper platform issue

  5. ACTION ITEMS:
     - immediate: fix the readiness probe to verify actual cache-warm
       completion, not just process liveness
     - systemic: add a load-test step in CI/staging that specifically
       exercises the FIRST-N-seconds-after-ready behavior for any service
       with a meaningful warm-up cost, not just steady-state performance
     - systemic: consider a startup probe (question 21) with a longer,
       deliberate grace period specifically for cache-warming services,
       so "ready" genuinely means "performing at steady-state," not just
       "the process is up"
```

**Follow-up:**

I'd tie the actual generalizable lesson directly back to question 21 and the Spring Boot Internals file's own readiness-probe discussion — "the rollout reported success" and "the deployment was actually safe" are not the same claim, and the gap between them is entirely a function of how accurately the readiness probe reflects genuine request-serving fitness; I'd frame the durable fix as treating readiness-probe *correctness* (not just presence) as something explicitly tested under realistic load before a service goes to production, the same rigor this kit applies to test suites and eval suites elsewhere — a probe that's never been validated against the specific failure mode it's meant to catch is a false sense of safety, not a real one.

**Source:** [Kubernetes — Debug Running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/), [Google SRE Book — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Docker — What Is a Container? | https://docs.docker.com/get-started/docker-overview/ |
| Docker — What Is an Image? | https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/ |
| Docker — Build Cache | https://docs.docker.com/build/cache/ |
| Dockerfile Reference | https://docs.docker.com/reference/dockerfile/ |
| Docker — Networking Overview | https://docs.docker.com/engine/network/ |
| Docker — Volumes | https://docs.docker.com/engine/storage/volumes/ |
| Docker — Multi-Stage Builds | https://docs.docker.com/build/building/multi-stage/ |
| Docker — Building Best Practices | https://docs.docker.com/build/building/best-practices/ |
| Docker CLI Reference — `docker run` | https://docs.docker.com/reference/cli/docker/container/run/ |
| Docker — Build Secrets | https://docs.docker.com/build/building/secrets/ |
| Docker Scout | https://docs.docker.com/scout/ |
| gVisor | https://gvisor.dev/ |
| Kata Containers | https://katacontainers.io/ |
| Kubernetes — Pods | https://kubernetes.io/docs/concepts/workloads/pods/ |
| Kubernetes — Deployments | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ |
| Kubernetes — Service | https://kubernetes.io/docs/concepts/services-networking/service/ |
| Kubernetes — Ingress | https://kubernetes.io/docs/concepts/services-networking/ingress/ |
| Kubernetes — ConfigMap | https://kubernetes.io/docs/concepts/configuration/configmap/ |
| Kubernetes — Secret | https://kubernetes.io/docs/concepts/configuration/secret/ |
| Kubernetes — Object Management | https://kubernetes.io/docs/concepts/overview/working-with-objects/object-management/ |
| Kubernetes — Components | https://kubernetes.io/docs/concepts/overview/components/ |
| Kubernetes — Container Runtime Interface | https://kubernetes.io/docs/concepts/architecture/cri/ |
| Kubernetes — Probes | https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ |
| Kubernetes — Assigning Pods to Nodes | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| Kubernetes — Taints and Tolerations | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ |
| Kubernetes — Service Networking | https://kubernetes.io/docs/concepts/services-networking/ |
| Container Network Interface (CNI) | https://www.cni.dev/ |
| Kubernetes — StatefulSets | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ |
| Kubernetes — Managing Resources for Containers | https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ |
| Kubernetes — Pod Quality of Service | https://kubernetes.io/docs/tasks/configure-pod-container/quality-service-pod/ |
| Kubernetes — Horizontal Pod Autoscaling | https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ |
| Kubernetes — RBAC Good Practices | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ |
| Kubernetes — RBAC Reference | https://kubernetes.io/docs/reference/access-authn-authz/rbac/ |
| Kubernetes — Network Policies | https://kubernetes.io/docs/concepts/services-networking/network-policies/ |
| Kubernetes — Resource Quotas | https://kubernetes.io/docs/concepts/policy/resource-quotas/ |
| Kubernetes — Debug Running Pods | https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/ |
| etcd Documentation | https://etcd.io/docs/latest/ |
| Kubernetes — Pod Lifecycle | https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/ |
| Kubernetes — PodDisruptionBudget | https://kubernetes.io/docs/tasks/run-application/configure-pdb/ |
| Kubernetes — Pod Security Standards | https://kubernetes.io/docs/concepts/security/pod-security-standards/ |
| Kubernetes — Admission Controllers | https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/ |
| Istio Documentation | https://istio.io/latest/docs/concepts/what-is-istio/ |
| Kubernetes Cluster Autoscaler | https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/README.md |
| Kubernetes — Nodes | https://kubernetes.io/docs/concepts/architecture/nodes/ |
| Google SRE Book — Postmortem Culture | https://sre.google/sre-book/postmortem-culture/ |
