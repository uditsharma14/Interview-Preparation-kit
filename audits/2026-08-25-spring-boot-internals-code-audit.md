# Spring Boot Internals — Code-Block Audit — 2026-08-25

Scope: third guide in `ROADMAP.md`'s code-block validation rollout, and
the first Spring-based guide audited. Unlike the pure-JDK Java guides
(Java Concurrency, Java JVM & GC), this guide's 37 questions are
overwhelmingly built around Spring annotations and framework behavior, so
a plain `javac` pass isn't sufficient to verify most of its claims — a
real Spring dependency classpath was set up specifically for this pass
(and reused for the Spring Security and JPA & Hibernate guides that
follow it in the rollout).

## Approach

A minimal Maven project (`spring-boot-starter` + `spring-tx`, Spring Boot
3.2.5 / Spring Framework 6.1) was created and its dependencies resolved
from Maven Central (internet access and a local Maven installation were
both available in this environment). This enabled two levels of
verification beyond what a bare-JDK guide gets:

1. **Behavioral verification** — for the guide's most load-bearing,
   checkable claims, a small, real `AnnotationConfigApplicationContext`
   was built and the actual runtime behavior observed, not just the code
   compiled.
2. **Compilation verification** — for code blocks that were self-contained
   enough to compile against Spring's annotations (with at most one
   trivial stub type added, consistent with how the rest of this repo's
   audits have handled a block assuming one undefined collaborator).

The majority of this guide's ~32 `java`-tagged blocks reference domain
types with real business logic not shown in the snippet (`Order`,
`OrderRepository.save()`, `PaymentGateway` implementations with actual
charge logic, `RecommendationClient`, `TracingProperties` usage) — per
`CONTRIBUTING.md`, this is the correct, honest **partial illustrative
snippet** classification for the majority of this guide's examples, not
a shortfall in verification effort. `ROADMAP.md` already anticipated this
exact situation for Spring-heavy guides.

## Behavioral verification (real Spring context, not just compiled)

Three of the guide's central, most consequential technical claims were
independently reproduced against a real Spring context:

- **Q16 (`@Primary` vs. `@Qualifier` resolution)** — built two real beans
  (`StripeGateway` `@Primary`, `PaypalGateway` plain) and two consumers,
  one unqualified and one with an explicit `@Qualifier("paypalGateway")`.
  Confirmed exactly as the guide claims: the unqualified injection point
  resolved to the `@Primary` bean (`stripe`); the explicitly-qualified
  one resolved to `paypal`, correctly overriding `@Primary`.
- **Q23/Q25 (self-invocation bypasses `@Transactional`)** — built a real
  `@Transactional`-driven bean with a recording `PlatformTransactionManager`
  standing in for a real transaction manager. Confirmed the bean was a
  genuine CGLIB proxy (`OrderService$$SpringCGLIB$$0`), that calling the
  `@Transactional` method via self-invocation (`this.processPayment()`
  called from within `placeOrder()`) did **not** start a transaction, and
  that calling the same method directly from outside the bean **did**
  start one — exactly the guide's claimed behavior.
- **Q28 (circular dependencies)** — built two real circularly-dependent
  bean pairs. Field-injection resolved without error via Spring's
  early-reference mechanism (confirmed `a.serviceB.serviceA == a`, i.e.
  the same instance came back through the cycle); constructor-injection
  failed at startup with `UnsatisfiedDependencyException` wrapping a
  `BeanCurrentlyInCreationException` root cause — exactly as claimed.

## Compilation verification

The following blocks were confirmed to compile against a real Spring
Boot 3.2.5 classpath, most with no modification at all: Q1 (with its own
`StripePaymentGateway` stub, already implied by the snippet), Q3
(stereotype annotations), Q6 and its explicit-annotations variant
(`@SpringBootApplication`), Q12 (`@Value`/`@ConfigurationProperties`),
Q14 (component scanning), Q17 (with a one-line `PaymentGateway` interface
stub), Q22 (component-scan exclusion patterns), and Q24 (JDK vs. CGLIB
proxy comparison).

## Bug found and fixed

### Q27 — constructor name didn't match its class name (genuine compile error)

```java
class StatelessOrderService {
    private final OrderRepository repository;
    OrderService(OrderRepository repository) { this.repository = repository; }
```

The class is `StatelessOrderService`, but its constructor was named
`OrderService` — Java requires a constructor's name to exactly match its
enclosing class, so this doesn't compile at all (`javac` reports "invalid
method declaration; return type required," since a method named
differently from its class isn't recognized as a constructor). Almost
certainly a leftover from an earlier draft where the class itself was
named `OrderService`, not caught when it was renamed to
`StatelessOrderService` to make the thread-safety comparison read
clearly against the adjacent `BrokenStatefulService`.

Fixed by renaming the constructor to `StatelessOrderService(...)`.
Re-verified: compiles cleanly.

## Not done in this pass

- The remaining ~20 `java`-tagged blocks (auto-configuration sketches
  referencing `DataSourceProperties`/`RedisTemplate`/`CacheMetricsRegistrar`,
  lifecycle/event demos referencing an undeclared `log` field, startup
  and shutdown examples referencing `Order`/`RecommendationClient`/
  `TracingProperties` with real business logic) were classified as
  partial illustrative snippets per `CONTRIBUTING.md`'s own guidance —
  not compiled, since doing so would require inventing substantial
  fabricated domain logic beyond a trivial stub, which the policy
  explicitly warns against ("do not invent a domain class purely to make
  the snippet compile").
- The `bash`/`yaml`/`properties`/`xml`/`text`-tagged blocks (17 shell
  commands, 4 YAML, 7 properties, 2 XML, 2 text/pseudocode) were reviewed
  for syntax correctness against current Spring Boot 3.2/Spring Framework
  6.1 documentation but not executed — most require a running application
  server, Kubernetes cluster, or GraalVM native-image toolchain to
  meaningfully execute.
- Full end-to-end verification of the auto-configuration mechanism itself
  (`@ConditionalOnClass`/`@ConditionalOnMissingBean` interaction, the
  `AutoConfiguration.imports` file mechanism) was not attempted — this
  would require a more elaborate multi-module Maven setup to properly
  exercise, and was judged disproportionate to this pass's scope given
  the mechanism's behavior is already extensively covered by Spring
  Boot's own test suite and documentation, which this guide's Sources
  section already cites directly.
