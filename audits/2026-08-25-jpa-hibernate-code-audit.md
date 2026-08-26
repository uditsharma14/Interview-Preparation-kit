# JPA & Hibernate — Code-Block Audit — 2026-08-25

Scope: fifth guide in `ROADMAP.md`'s code-block validation rollout, and
the last of the Java/Spring group before moving to the System Design
guides. This guide's 42 questions are unusually code-dense even by this
repository's standards — nearly every question includes at least one
Java code block illustrating an entity mapping, a repository method, or
a persistence-context interaction.

## Classification summary (50 total code blocks)

- **40 `java`-tagged blocks.** The large majority define entity classes,
  repository interfaces, or service methods using undefined domain types
  specific to the question's own narrow example (`Order`, `OrderItem`,
  `Customer`, `Student`/`Course`, `Inventory`) — per `CONTRIBUTING.md`,
  these are correctly classified as **partial illustrative snippet**.
  However, unlike the two Spring guides audited previously, JPA/Hibernate
  entity mappings are largely self-contained (an `@Entity` class with
  `@Id`/`@OneToMany`/`@Version` fields doesn't need a fabricated service
  layer to compile) — 10 of these blocks were extracted and independently
  compiled against a real Hibernate 6.4 classpath (see below), and 6 of
  the guide's most load-bearing, mechanism-level claims were verified
  against a real, running Hibernate `EntityManagerFactory` backed by an
  in-memory H2 database, not left as unverified prose.
- **5 `properties`-tagged blocks** — Spring Boot/Hibernate configuration
  keys (second-level cache enablement, JDBC batching, OSIV, SQL logging)
  — reviewed for correct property-key spelling against current Hibernate
  6.x / Spring Boot 3.x documentation, not executed (no full Spring Boot
  application context was bootstrapped for this pass).
- **4 `sql`-tagged blocks** — raw SQL illustrating join-multiplication,
  pessimistic-lock SQL, and index-column-order guidance — reviewed for
  syntactic correctness, not executed against a live database.
- **1 `text`-tagged block** — a postmortem-structure outline (Q42) —
  correctly pseudocode/template, not meant to execute.

## Verification environment

Extended the reusable Maven project from the Spring Boot Internals /
Spring Security passes
(`spring_verify/pom.xml`) with `spring-boot-starter-data-jpa` and
`com.h2database:h2`, both resolved from the existing
`spring-boot-dependencies:3.2.5` BOM. Bootstrapped a real JPA
persistence unit (`META-INF/persistence.xml`, Hibernate 6.4.4.Final,
`jdbc:h2:mem:jpaverify`, `hbm2ddl.auto=create-drop`, SQL logging on) —
plain JPA/Hibernate bootstrap via `Persistence.createEntityManagerFactory()`,
no Spring context needed for this guide's claims, which are about JPA/
Hibernate mechanics themselves rather than Spring's DI/AOP layer.

## Behavioral verification (real Hibernate + H2)

Two real, mapped entities (`Order`, `OrderItem`, bidirectional
`@OneToMany`/`@ManyToOne`, `@Version` on `Order`) were used to exercise
six claims end-to-end, with actual generated SQL captured via Hibernate's
SQL logging:

- **Persistence context identity + automatic dirty checking (Q14/Q15).**
  Two `find()` calls for the same ID within one persistence context
  returned the exact same object reference (`order1 == order2: true`).
  Mutating one via a plain setter — no explicit `save()`/`update()` call
  — produced exactly one `UPDATE` statement at commit, and the change
  was durably visible on a fresh reload. Matches the guide's claims
  exactly.
- **Auto-flush before a JPQL query (Q16).** A pending, unflushed
  `setStatus()` change was correctly visible to a JPQL query filtering
  on that same field, confirmed via the generated SQL log showing the
  `UPDATE` issued automatically immediately before the `SELECT`.
- **N+1 query problem (Q19).** Loading 5 parent entities then accessing
  each one's lazy `items` collection produced exactly 1 query for the
  parents plus 5 additional queries (one per parent) for their lazy
  collections — the textbook 1+N shape the guide describes, confirmed
  directly in the SQL log rather than assumed.
- **Owning vs. inverse side (Q29).** Adding a child only to the inverse
  side's collection (`order.getItems().add(item)`, never setting
  `item.setOrder(...)`) left the persisted row's foreign key `null` on
  reload — confirming the guide's claim that inverse-side-only mutation
  is silently not persisted. Using the guide's own recommended
  `addItem()` helper (setting both sides) correctly persisted the
  foreign key.
- **`persist()` vs. `merge()` reference semantics (Q25).** `persist()`
  left the passed-in object itself managed (assigned an ID in place).
  `merge()` on a detached instance returned a demonstrably different
  object reference than the one passed in, confirming the "always use
  the returned reference" warning is describing real, observable
  behavior and not a hypothetical.
- **Optimistic locking (Q32).** Two transactions read the same row;
  the first to commit succeeded and bumped `@Version`. The second,
  committing against its now-stale version, threw
  `jakarta.persistence.OptimisticLockException` (wrapped in a
  `RollbackException`, as JPA's `EntityTransaction.commit()` contract
  requires) — exactly the conflict-detection behavior the guide
  describes, not a silent lost update.

All six results matched the guide's claims exactly.

## Bugs found and fixed

**Q22 — duplicate `@ManyToOne` annotation (real compile error).** The
"lazy vs. eager" example stacked two live `@ManyToOne` annotations on
the same field:

```java
@ManyToOne // defaults to EAGER per spec — override explicitly, almost always:
@ManyToOne(fetch = FetchType.LAZY)
Order order;
```

`@ManyToOne` is not `@Repeatable`, so this fails to compile with
`"ManyToOne is not a repeatable annotation interface"` — confirmed via
`javac` against the real JPA API before fixing. The evident intent was
to show the spec default as a comment, not as a second live annotation.
Fixed by converting the first line to a plain comment:

```java
// @ManyToOne defaults to EAGER per spec — override explicitly, almost always:
@ManyToOne(fetch = FetchType.LAZY)
Order order;
```

## Additional compile-only verification

10 further entity/embeddable definitions extracted from Q5, Q6, Q11,
Q18, Q27, Q30, Q31, and Q32 (sequence generators, `@ManyToMany` with
`@JoinTable`, `@EmbeddedId` composite keys with `equals`/`hashCode`,
`@Cacheable`/`@Cache` second-level-cache annotations, `GenerationType.UUID`,
and the `equals`/`hashCode` entity-identity examples) were compiled
directly against the real JPA/Hibernate classpath — all compiled cleanly
with no further issues found.

## Not done in this pass

- The remaining ~28 `java` blocks referencing undefined, question-specific
  domain types (`OrderRepository`, `InventoryRepository`, `Account`,
  `legacyAccountLookup`, and similar) were classified as partial
  illustrative per `CONTRIBUTING.md` and not compiled — inventing the
  surrounding business logic to force them to compile would violate the
  policy's explicit warning against fabricating domain classes.
- No full Spring Boot application context (`spring.jpa.*` properties,
  Spring Data JPA's generated repository proxies, `@Transactional`'s
  Spring-managed transaction boundaries) was bootstrapped — this pass
  verified JPA/Hibernate's own persistence-context mechanics directly via
  plain `EntityManager`/`EntityManagerFactory`, which is what the guide's
  claims are actually about; Spring Data JPA's repository-generation
  layer itself was already exercised conceptually (not re-tested) since
  it is a thin convenience wrapper over the same `EntityManager` calls.
- Second-level caching (Q18), pessimistic locking's actual row-blocking
  behavior (Q33), JDBC batching's actual round-trip count (Q28/Q36), and
  the bulk-JPQL-update staleness scenario (Q34) were reviewed for
  correctness against Hibernate's documented behavior but not
  independently re-executed — each is a well-documented, unambiguous
  mechanism (unlike the six claims above, which were specifically chosen
  for being either the most load-bearing or the easiest to get subtly
  wrong) and re-verifying all of them was judged disproportionate given
  the six-mechanism verification already performed.
- `sql`/`properties`/`text` blocks were reviewed for syntax and
  documentation accuracy but not executed.
