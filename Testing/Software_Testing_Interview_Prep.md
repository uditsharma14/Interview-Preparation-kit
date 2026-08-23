# Software Testing — Interview Prep, Basic to Staff Level (with Code & Sources)

> **Target level:** Basic → Staff (graduated — see below) · **Baseline:** JUnit 6.x (Jupiter programming model — annotations covered here are unchanged from JUnit 5, but JUnit 6 requires Java 17+ and is the current major version) · Mockito 5.x · Spring Framework 6.x/Spring Boot 3.4+ testing support (`@MockitoBean`, the current annotation — the older `@MockBean` was deprecated in Spring Boot 3.4) · Testcontainers · **Last verified:** 2026-08-23 · **Prerequisites:** [Java Collections](../Language/Java_Collections_Interview_Prep.md) for the Basic section; [Spring Boot Internals](../Frameworks/Spring_Boot_Internals_Interview_Prep.md) helpful from the Intermediate section onward, [JPA & Hibernate](../Frameworks/JPA_Hibernate_Interview_Prep.md) helpful for the `@DataJpaTest`/Testcontainers questions

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **code snippet** you could sketch on a whiteboard or IDE to back it up, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar isn't naming annotations, it's explaining how you'd actually test something genuinely hard to test (an external dependency, async code, a flaky suite) and why. Questions are grouped by level (Basic → Intermediate → Staff, with Staff specifically organized as scenario-based questions) so you can calibrate depth to the interview you're prepping for; the later sections assume the earlier ones as background and don't re-explain them.

<!-- toc -->
## Table of Contents

- [Basic](#basic)
  - [1. What Is JUnit, and What Do `@Test`, `@BeforeEach`, and `@AfterEach` Do?](#1-what-is-junit-and-what-do-test-beforeeach-and-aftereach-do)
  - [2. What's the Difference Between an Assertion Failure and an Exception in a Test?](#2-whats-the-difference-between-an-assertion-failure-and-an-exception-in-a-test)
  - [3. What Is the AAA (Arrange-Act-Assert) Pattern?](#3-what-is-the-aaa-arrange-act-assert-pattern)
  - [4. What's the Difference Between a Mock, a Stub, and a Spy?](#4-whats-the-difference-between-a-mock-a-stub-and-a-spy)
  - [5. What Is Mockito, and How Do You Create and Use a Basic Mock?](#5-what-is-mockito-and-how-do-you-create-and-use-a-basic-mock)
  - [6. What's the Difference Between `@Mock` and `@InjectMocks`?](#6-whats-the-difference-between-mock-and-injectmocks)
  - [7. What Makes a Good Test Name, and Why Does It Matter?](#7-what-makes-a-good-test-name-and-why-does-it-matter)
  - [8. What Is Test Coverage, and Why Isn't 100% Coverage the Goal?](#8-what-is-test-coverage-and-why-isnt-100-coverage-the-goal)
- [Intermediate](#intermediate)
  - [9. What Are `@ParameterizedTest`, `@ValueSource`, and `@CsvSource`, and When Would You Use Them?](#9-what-are-parameterizedtest-valuesource-and-csvsource-and-when-would-you-use-them)
  - [10. How Do You Test That a Method Throws the Expected Exception?](#10-how-do-you-test-that-a-method-throws-the-expected-exception)
  - [11. What's the Difference Between `@SpringBootTest`, `@WebMvcTest`, and `@DataJpaTest`?](#11-whats-the-difference-between-springboottest-webmvctest-and-datajpatest)
  - [12. What Is `MockMvc`, and How Do You Use It to Test a REST Controller?](#12-what-is-mockmvc-and-how-do-you-use-it-to-test-a-rest-controller)
  - [13. What's the Difference Between `@Mock` and `@MockitoBean`?](#13-whats-the-difference-between-mock-and-mockitobean)
  - [14. Why Should Tests Be Independent of Each Other, and What Breaks That Independence?](#14-why-should-tests-be-independent-of-each-other-and-what-breaks-that-independence)
  - [15. What Is Testcontainers, and What Problem Does It Solve?](#15-what-is-testcontainers-and-what-problem-does-it-solve)
- [Staff Level — Scenario-Based Testing](#staff-level--scenario-based-testing)
  - [16. How Would You Test a Service That Calls an External Payment Gateway?](#16-how-would-you-test-a-service-that-calls-an-external-payment-gateway)
  - [17. How Would You Test an `@Async` Method or a Scheduled Task?](#17-how-would-you-test-an-async-method-or-a-scheduled-task)
  - [18. How Would You Test a Kafka Producer/Consumer?](#18-how-would-you-test-a-kafka-producerconsumer)
  - [19. How Would You Diagnose and Fix a Flaky Test?](#19-how-would-you-diagnose-and-fix-a-flaky-test)
  - [20. How Would You Test Code That Depends on the Current Time?](#20-how-would-you-test-code-that-depends-on-the-current-time)
  - [21. How Would You Manage Test Data for Integration Tests Against a Real Database?](#21-how-would-you-manage-test-data-for-integration-tests-against-a-real-database)
  - [22. How Would You Decide Between Mocking a Dependency and Using Testcontainers for It?](#22-how-would-you-decide-between-mocking-a-dependency-and-using-testcontainers-for-it)
  - [23. How Would You Design a Test Strategy for a Legacy Codebase With No Existing Tests?](#23-how-would-you-design-a-test-strategy-for-a-legacy-codebase-with-no-existing-tests)
  - [24. How Should Test Suites Be Structured and Run in CI to Avoid Becoming a Bottleneck?](#24-how-should-test-suites-be-structured-and-run-in-ci-to-avoid-becoming-a-bottleneck)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## Basic

### 1. What Is JUnit, and What Do `@Test`, `@BeforeEach`, and `@AfterEach` Do?

**Answer:**

"JUnit is the standard testing framework for Java — it provides the annotations, assertion methods, and test-running infrastructure that let you write, organize, and execute automated tests. `@Test` marks a method as an actual test case — the test runner discovers every `@Test`-annotated method in a class and executes each one independently. `@BeforeEach` marks a method that runs *before every single test* in the class, typically used to set up fresh state (a new object under test, reset mocks) so each test starts from a known, clean baseline. `@AfterEach` marks a method that runs *after every single test*, typically used for cleanup (closing a resource, resetting a shared static field).

The current major version is JUnit 6 (a modernization release — Java 17+ minimum, unified module versioning — but the core Jupiter programming model these annotations belong to is unchanged from JUnit 5, so existing test code written against JUnit 5's annotations still works)."

**Code:**

```java
class CalculatorTest {
    private Calculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new Calculator(); // fresh instance before EVERY test — no shared state carried over
    }

    @Test
    void addsTwoPositiveNumbers() {
        int result = calculator.add(2, 3);
        assertEquals(5, result);
    }

    @Test
    void addsNegativeNumbers() {
        int result = calculator.add(-2, -3);
        assertEquals(-5, result); // completely independent of the test above — fresh `calculator`
    }

    @AfterEach
    void tearDown() {
        calculator = null; // rarely strictly necessary for a plain object, but shown for the pattern
    }
}
```

**Follow-up:**

I'd mention `@BeforeAll`/`@AfterAll` as the class-level counterparts (run once for the whole class, not once per test — must be `static` by default, since they run before any test instance exists) — the right tool specifically for expensive, genuinely shareable setup (starting a Testcontainers container, covered later in this guide) where per-test setup would be wastefully slow, as long as what's being shared is read-only or the tests are written to not depend on each other's mutations to it.

**Source:** [JUnit User Guide — `@Test`, `@BeforeEach`, `@AfterEach`](https://docs.junit.org/6.0.2/writing-tests/annotations.html)

---

### 2. What's the Difference Between an Assertion Failure and an Exception in a Test?

**Answer:**

"An **assertion failure** happens when a test explicitly checks an expected outcome (`assertEquals(5, result)`) and that check fails — JUnit throws `AssertionError` internally, catches it as part of the test-running framework's own machinery, and reports the test as **failed**. An unexpected **exception** — a `NullPointerException` from a bug in the code under test, an `IOException` from a real file operation gone wrong — also causes the test to stop and be reported as failed, but for a different underlying reason: the code under test broke in a way the test never anticipated checking for, rather than the test's own explicit expectation not being met.

Most test runners and CI dashboards distinguish these two outcomes explicitly — a 'failure' (an assertion didn't hold) versus an 'error' (an unexpected exception propagated up) — because they point at different things: a failure usually means the code's behavior genuinely doesn't match what's expected (a real bug, or a test that needs updating), while an error more often means something crashed outright, which is worth investigating differently."

**Code:**

```java
@Test
void assertionFailure() {
    int result = calculator.add(2, 2);
    assertEquals(5, result); // ASSERTION FAILURE — the check ran, but 4 != 5
}

@Test
void unexpectedException() {
    Order order = null;
    orderService.process(order); // ERROR — NullPointerException, never even reached an assertion
}
```

**Follow-up:**

I'd mention that this distinction matters practically when triaging a batch of CI failures after a change: a spike in "errors" (unexpected exceptions) across many unrelated tests often points at something structural breaking (a bean failing to wire, a database connection issue in a shared test fixture), while a handful of specific "failures" (assertions not matching) more often points at an actual behavior change in the code under test — worth checking which bucket a failure lands in before diving into individual test output.

**Source:** [JUnit User Guide — Assertions](https://docs.junit.org/6.0.2/writing-tests/assertions.html)

---

### 3. What Is the AAA (Arrange-Act-Assert) Pattern?

**Answer:**

"AAA is a simple, widely-used convention for structuring the *body* of an individual test into three clear phases. **Arrange**: set up everything the test needs — construct the object under test, prepare input data, configure mocks. **Act**: perform the single action actually being tested — call the one method whose behavior this test verifies. **Assert**: check that the outcome matches what's expected — one or more assertions confirming the actual result.

The value isn't the labels themselves (most real test methods don't have literal comments marking each phase) — it's the discipline of keeping these three concerns visually and logically separate within a test, rather than interleaving setup, action, and checks throughout the method. A test that's hard to read is often a test that's mixed these phases together; restructuring it into clean AAA sections is frequently enough to make an otherwise-confusing test immediately clear."

**Code:**

```java
@Test
void processesOrderSuccessfully() {
    // ARRANGE
    Order order = new Order("SKU-123", 2);
    when(inventoryService.hasStock("SKU-123", 2)).thenReturn(true);

    // ACT
    OrderResult result = orderService.process(order);

    // ASSERT
    assertEquals(OrderStatus.CONFIRMED, result.status());
    verify(inventoryService).reserveStock("SKU-123", 2);
}
```

**Follow-up:**

I'd flag the most common violation of this pattern worth watching for in code review: a test with **multiple, unrelated Act+Assert pairs** crammed into one test method ("test everything about `OrderService` in one giant test") — this makes it genuinely hard to tell, from a failure alone, *which* specific behavior actually broke, and it's exactly why the convention is one test method per behavior being verified, even if that means more, smaller test methods rather than fewer, larger ones.

**Source:** [Martin Fowler — GivenWhenThen (the same pattern, BDD-flavored naming)](https://martinfowler.com/bliki/GivenWhenThen.html)

---

### 4. What's the Difference Between a Mock, a Stub, and a Spy?

**Answer:**

"All three are 'test doubles' — objects substituted for a real dependency during a test — but they differ in what they're actually for. A **stub** is a test double that returns pre-programmed, canned responses to calls made on it, with no verification of *how* it was called — its job is purely to let the code under test run without needing the real dependency. A **mock** goes further: beyond returning canned responses, a mock lets the test explicitly **verify** that specific interactions actually happened — that a method was called, how many times, with what arguments — turning 'did my code call the payment gateway correctly' into an assertion the test can make directly. A **spy** wraps a *real* object, letting real method calls happen by default, while still letting the test selectively override specific methods' behavior or verify specific calls — useful when you want most of the real behavior but need to intercept one particular method.

In everyday conversation, especially with Mockito specifically, 'mock' is often used loosely to mean 'any test double,' but the precise distinction (return canned data vs. verify interactions vs. wrap a real object) is worth having exactly right for a staff-level answer."

**Code:**

```java
// STUB — just returns canned data, no verification of how it was called
PaymentGateway stubGateway = mock(PaymentGateway.class);
when(stubGateway.charge(any())).thenReturn(PaymentResult.success());

// MOCK — same object, but the test explicitly VERIFIES the interaction happened
verify(stubGateway).charge(argThat(request -> request.amount().equals(new BigDecimal("99.99"))));

// SPY — wraps a REAL object; real methods run unless explicitly overridden
List<String> realList = new ArrayList<>();
List<String> spyList = spy(realList);
spyList.add("real item");           // this ACTUALLY runs on the real underlying ArrayList
doReturn(999).when(spyList).size(); // but THIS specific call is overridden
```

**Follow-up:**

I'd bring up the practical guidance for choosing between them: reach for a stub/mock when the dependency being replaced is genuinely external or slow (a payment gateway, a network call) and the test cares about the code under test's own logic, not the dependency's real behavior; reach for a spy specifically when you need most of an object's real behavior intact but need to intercept or verify one narrow piece of it — overusing spies on your own application's core classes is often a sign the class itself should be broken into smaller, more independently-testable pieces instead.

**Source:** [Martin Fowler — Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)

---

### 5. What Is Mockito, and How Do You Create and Use a Basic Mock?

**Answer:**

"Mockito is the standard mocking framework for Java — it lets you create test doubles (mocks) for any class or interface at runtime, without hand-writing a fake implementation class yourself. The core workflow is three steps: create a mock (`mock(SomeClass.class)`), tell it what to return when a specific method is called (`when(mock.someMethod()).thenReturn(value)` — 'stubbing'), and, if you want to verify an interaction happened, call `verify(mock).someMethod()` after exercising the code under test.

Mockito works by generating a dynamic proxy (or, for classes, a subclass via byte-code generation) at runtime that intercepts every method call, checks whether it's been stubbed, and either returns the stubbed value or, for interactions later checked with `verify()`, records that the call happened for later assertion — none of this requires the real class's actual implementation to run at all, which is exactly what makes it fast and safe to use for dependencies you don't want a unit test actually invoking."

**Code:**

```java
import static org.mockito.Mockito.*;

@Test
void chargesCustomerSuccessfully() {
    PaymentGateway gateway = mock(PaymentGateway.class);       // 1. create the mock
    when(gateway.charge(new BigDecimal("50.00")))               // 2. stub its behavior
        .thenReturn(PaymentResult.success());

    PaymentResult result = new CheckoutService(gateway).charge(new BigDecimal("50.00")); // exercise the code

    assertTrue(result.isSuccess());
    verify(gateway).charge(new BigDecimal("50.00"));            // 3. verify the interaction happened
}
```

**Follow-up:**

I'd mention that an *unstubbed* mock method call doesn't throw an error — it returns a sensible default (`null` for objects, `0`/`false`/an empty collection for primitives/collections) rather than failing loudly, which is a real, common source of confusing test failures: forgetting to stub a method the code under test actually calls silently returns `null` where real code expected a value, producing a `NullPointerException` several lines later that looks like a bug in the code, when it's actually a missing stub in the test.

**Source:** [Mockito — Official Site and API Overview](https://site.mockito.org/)

---

### 6. What's the Difference Between `@Mock` and `@InjectMocks`?

**Answer:**

"`@Mock` (Mockito's annotation form) creates a mock of the annotated field's type — equivalent to calling `mock(SomeClass.class)` yourself, but declared declaratively and initialized automatically by Mockito's test runner integration (`@ExtendWith(MockitoExtension.class)` in JUnit 5/6). `@InjectMocks` marks the field that should have every other `@Mock`-annotated field in the test class **injected into it automatically** — Mockito inspects the target class's constructor (preferring constructor injection if one exists) and attempts to match each mock to a constructor parameter or field by type.

This is genuinely convenient for a class with several dependencies, since it avoids manually wiring `new OrderService(mockGateway, mockInventory, mockNotifier)` by hand — but it's worth knowing its limits: `@InjectMocks` can only match mocks it actually has (a dependency with no corresponding `@Mock` field is left `null` or default-constructed, which can produce a confusing `NullPointerException` unrelated to the actual behavior being tested), and its matching logic can pick the wrong mock in genuinely ambiguous cases (two constructor parameters of the same type)."

**Code:**

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private PaymentGateway paymentGateway;   // creates a mock

    @Mock
    private InventoryService inventoryService; // creates another mock

    @InjectMocks
    private OrderService orderService; // Mockito injects BOTH mocks above into OrderService's constructor

    @Test
    void processesOrder() {
        when(inventoryService.hasStock(any(), anyInt())).thenReturn(true);
        // orderService already has paymentGateway and inventoryService wired in — no manual `new` needed
        orderService.process(new Order("SKU-1", 1));
    }
}
```

**Follow-up:**

I'd flag that `@InjectMocks` has a real, if mild, downside worth being aware of: it hides the class's actual dependency wiring behind Mockito's own reflection-based matching, which can make a test harder to follow than just explicitly constructing the object under test with its mocks passed in by hand (`new OrderService(paymentGateway, inventoryService)`) — some teams deliberately avoid `@InjectMocks` for exactly this readability reason, preferring the small amount of extra boilerplate in exchange for the wiring being visible directly in the test.

**Source:** [Mockito — `@InjectMocks` Javadoc](https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/InjectMocks.html)

---

### 7. What Makes a Good Test Name, and Why Does It Matter?

**Answer:**

"A good test name describes **what's being tested, under what condition, and what the expected outcome is** — reading the name alone should tell you what broke without needing to open the test body at all. A common, effective convention is `methodName_condition_expectedResult` (`withdraw_insufficientBalance_throwsException`) or a more sentence-like style (`shouldThrowExceptionWhenBalanceIsInsufficient`) — the exact convention matters less than consistently following *some* convention that encodes condition and expectation, not just the method under test.

This matters practically far more than it might seem: when a CI run reports fifteen failing tests by name alone, a well-named test suite tells you immediately which specific behaviors broke, while a suite full of `test1`, `test2`, or `testWithdraw` (with no indication of *which* withdraw scenario) forces you to open every failing test body just to understand what's actually wrong — a real, compounding cost every single time the suite fails."

**Code:**

```java
// BAD — tells you almost nothing from the name alone
@Test void test1() { /* ... */ }
@Test void testWithdraw() { /* ... */ }

// GOOD — condition and expected outcome are both explicit in the name
@Test void withdraw_insufficientBalance_throwsInsufficientFundsException() { /* ... */ }
@Test void withdraw_sufficientBalance_decreasesBalanceByWithdrawnAmount() { /* ... */ }
```

**Follow-up:**

I'd mention JUnit's `@DisplayName` annotation as a complementary tool worth knowing, not a replacement for a good method name: it lets a test show a more readable, free-form description in test-runner output and IDE test trees (`@DisplayName("throws when balance is insufficient")`) — genuinely useful for readability in reports, but the underlying method name itself should still be descriptive on its own, since `@DisplayName` isn't always what shows up in every tool (a stack trace, a command-line test runner) that might reference the failing test.

**Source:** [JUnit User Guide — `@DisplayName`](https://docs.junit.org/6.0.2/writing-tests/annotations.html)

---

### 8. What Is Test Coverage, and Why Isn't 100% Coverage the Goal?

**Answer:**

"Test coverage is a metric measuring what proportion of a codebase's lines, branches, or paths are actually executed while running the test suite — a coverage tool (JaCoCo, for Java) instruments the code and reports which lines ran during testing and which never did. It's a genuinely useful *diagnostic* signal: a class with 0% coverage almost certainly has untested behavior, and coverage reports are a fast way to find code nobody's actually exercising with a test.

It's a poor *target* to optimize for directly, though, because coverage measures whether a line **executed**, not whether the test that executed it **actually verified the right thing happened** — a test that calls a method with no assertions at all achieves 100% line coverage on that method while verifying literally nothing about its correctness. High coverage with weak assertions gives a false sense of safety that's arguably worse than honestly knowing coverage is low, since a team can point at the coverage number and believe the code is well-tested when it isn't."

**Code:**

```java
// This achieves 100% LINE COVERAGE of calculateDiscount() —
// every line executes — but verifies NOTHING about correctness:
@Test
void testCalculateDiscount() {
    pricingService.calculateDiscount(order); // called, but no assertion at all — worthless as a test
}

// This achieves the SAME coverage, but actually verifies the behavior:
@Test
void calculateDiscount_appliesTenPercentForOrdersOverHundredDollars() {
    BigDecimal discount = pricingService.calculateDiscount(orderOf(new BigDecimal("150.00")));
    assertEquals(new BigDecimal("15.00"), discount); // this is what actually makes the test meaningful
}
```

**Follow-up:**

I'd give the practical framing: use coverage as a *floor-finding* tool (identifying genuinely untested code, especially error-handling branches that are easy to forget) rather than a target number to chase — a team mandating "90% coverage" as a hard CI gate, with no attention to assertion quality, tends to get exactly the hollow, assertion-free tests in the example above, written specifically to satisfy the number rather than to actually verify behavior, which is a worse outcome than having an honest, lower coverage number with genuinely meaningful tests.

**Source:** [JaCoCo — Java Code Coverage Library](https://www.jacoco.org/jacoco/trunk/doc/)

---

## Intermediate

### 9. What Are `@ParameterizedTest`, `@ValueSource`, and `@CsvSource`, and When Would You Use Them?

**Answer:**

"`@ParameterizedTest` lets a single test method run multiple times with different input values, instead of writing a nearly-identical `@Test` method per input case — reducing duplication when you're testing the same logic against several inputs that should each produce a predictable, related output. `@ValueSource` is the simplest argument source: a single array of literal values (`@ValueSource(ints = {1, 2, 3})`), providing exactly one argument per invocation. `@CsvSource` supports multiple arguments per invocation, expressed as comma-separated value rows directly in the annotation — the natural choice once a test needs more than one input value per run (an input and its expected output, say).

This is the right tool specifically for **boundary and equivalence-class testing** — verifying the same logic against several representative inputs (a negative number, zero, a large number, a boundary value) without the copy-paste duplication of writing one near-identical `@Test` method per case."

**Code:**

```java
@ParameterizedTest
@ValueSource(ints = {-1, 0, 1, 100})
void isValidAge_acceptsNonNegativeAges(int age) {
    // runs FOUR times, once per value — but -1 would need its own assertion logic;
    // ValueSource alone doesn't pair an input with an expected output
}

@ParameterizedTest
@CsvSource({
    "2, 3, 5",     // input1, input2, expected — one row per test invocation
    "-1, 1, 0",
    "0, 0, 0"
})
void add_returnsCorrectSum(int a, int b, int expected) {
    assertEquals(expected, calculator.add(a, b));
}
```

**Follow-up:**

I'd mention `@MethodSource` as the escape hatch once test data gets too complex for a literal annotation value to express cleanly — it points at a separate method that programmatically builds and returns the arguments (as a `Stream<Arguments>`), letting you construct genuinely complex objects or load data from a file, rather than being limited to what fits legibly inside an annotation's literal arguments.

**Source:** [JUnit User Guide — Parameterized Tests](https://docs.junit.org/6.1.0/writing-tests/parameterized-classes-and-tests.html)

---

### 10. How Do You Test That a Method Throws the Expected Exception?

**Answer:**

"JUnit's `assertThrows()` is the standard tool: it takes the expected exception type and a lambda wrapping the call expected to throw, executes that lambda, and either returns the caught exception (letting you make further assertions on it — its message, its cause) if it matched the expected type, or fails the test if either no exception was thrown at all, or a *different* exception type was thrown than expected. This is more precise than the older JUnit 4 style of putting `@Test(expected = SomeException.class)` on the whole method, since `assertThrows()` scopes the expectation to one specific line/lambda — if an earlier line in the test unexpectedly throws the same exception type, `assertThrows()` correctly still fails (since that earlier throw wasn't inside the wrapped lambda), whereas the annotation-based style would have passed incorrectly."

**Code:**

```java
@Test
void withdraw_insufficientBalance_throwsInsufficientFundsException() {
    Account account = new Account(new BigDecimal("50.00"));

    InsufficientFundsException exception = assertThrows(
        InsufficientFundsException.class,
        () -> account.withdraw(new BigDecimal("100.00")) // ONLY this specific call is checked
    );

    // Can make further assertions on the caught exception itself:
    assertEquals("Insufficient funds: balance 50.00, requested 100.00", exception.getMessage());
}
```

**Follow-up:**

I'd bring up the precision benefit directly with a concrete failure mode it prevents: if `account.withdraw(...)` were preceded, inside the same test, by some other line that could *also* throw `InsufficientFundsException` due to an unrelated bug, `assertThrows()`'s lambda-scoping means only the intended line is actually checked — a genuinely different (and more correct) guarantee than the old `@Test(expected = ...)` style, which just checked "did *any* line in this entire test method throw this exception type," a much weaker and more easily accidentally-satisfied assertion.

**Source:** [JUnit User Guide — Assertions, `assertThrows`](https://docs.junit.org/6.0.2/writing-tests/assertions.html)

---

### 11. What's the Difference Between `@SpringBootTest`, `@WebMvcTest`, and `@DataJpaTest`?

**Answer:**

"These are Spring Boot's 'test slice' annotations, each loading a different, deliberately-scoped subset of the full application context, trading off realism against test speed. `@SpringBootTest` loads the **entire** application context — every bean, exactly as it would be wired in production (optionally with a real or mock web environment) — the most realistic option, but also the slowest, since the whole application has to actually start up for each test class using it. `@WebMvcTest` loads **only** the web layer — controllers, `@ControllerAdvice`, Spring MVC infrastructure — auto-configures `MockMvc` (covered next), and explicitly does *not* load service or repository beans, which must be mocked (typically via `@MockitoBean`, covered later in this guide) if the controller depends on them. `@DataJpaTest` loads **only** the JPA/persistence layer — repositories, the `EntityManager` — and, by default, configures an in-memory embedded database, replacing your real database configuration, specifically so persistence-layer tests run fast and don't touch a real database at all unless explicitly configured otherwise.

The general principle: pick the narrowest slice that actually exercises what the test needs to verify — a controller test doesn't need the real database wired up, and a repository test doesn't need the web layer — since a narrower context loads faster and fails more precisely when something breaks."

**Code:**

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class FullIntegrationTest {
    // loads the ENTIRE application — slowest, most realistic
}

@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @Autowired private MockMvc mockMvc;
    @MockitoBean private OrderService orderService; // MUST mock — service beans aren't loaded here at all
}

@DataJpaTest
class OrderRepositoryTest {
    @Autowired private OrderRepository orderRepository; // real repository, real (embedded) database
    // no web layer, no service layer loaded — just the persistence slice
}
```

**Follow-up:**

I'd mention the practical trade-off worth stating explicitly: `@DataJpaTest`'s default embedded database (typically H2) is fast, but it's not necessarily the *same* database engine as production (PostgreSQL, say) — SQL dialect differences, or database-specific features a query relies on, can pass against H2 and fail against real PostgreSQL, or vice versa. This is exactly the gap Testcontainers (covered later in this guide) closes, by running the *actual* production database engine in a container for the test instead of a different, embedded substitute.

**Source:** [Spring Boot Reference — Testing Spring Boot Applications](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html)

---

### 12. What Is `MockMvc`, and How Do You Use It to Test a REST Controller?

**Answer:**

"`MockMvc` lets you test Spring MVC controllers by simulating HTTP requests **without actually starting a real HTTP server or making real network calls** — it dispatches a request through Spring MVC's actual dispatcher servlet and routing/argument-resolution machinery, so a `MockMvc` test genuinely exercises the same request-handling pipeline production traffic would go through (URL matching, request-body deserialization, validation, exception-handler mapping), just without the overhead and flakiness risk of a real network round trip. It's auto-configured for you when using `@WebMvcTest` (covered in the previous question), or can be set up explicitly against a full `@SpringBootTest` context.

The typical pattern: build a request (`MockMvcRequestBuilders.get(...)`/`.post(...)`, with headers/body as needed), perform it, and chain assertions on the resulting status code, headers, and body content — all fluent, readable, and without any actual socket ever being opened."

**Code:**

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @Autowired private MockMvc mockMvc;
    @MockitoBean private OrderService orderService;

    @Test
    void getOrder_existingId_returns200WithOrderBody() throws Exception {
        when(orderService.findById(123L)).thenReturn(new Order(123L, "SKU-1", 2));

        mockMvc.perform(get("/orders/123"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.sku").value("SKU-1"))
            .andExpect(jsonPath("$.quantity").value(2));
    }

    @Test
    void getOrder_missingId_returns404() throws Exception {
        when(orderService.findById(999L)).thenThrow(new OrderNotFoundException(999L));

        mockMvc.perform(get("/orders/999"))
            .andExpect(status().isNotFound());
    }
}
```

**Follow-up:**

I'd mention that `MockMvc`'s "no real HTTP server" trade-off has one genuine, non-trivial gap worth being aware of: since it dispatches through Spring MVC's machinery directly, some behavior that only exists at the actual servlet-container/filter level (a genuinely custom `Filter`, some container-specific behavior) may not be exercised the same way it would be with a truly full end-to-end HTTP call — `@SpringBootTest(webEnvironment = RANDOM_PORT)` combined with a real HTTP client (`TestRestTemplate`, `WebTestClient`) is the tool to reach for when a test genuinely needs to exercise the real network/servlet-container path.

**Source:** [Spring Framework Reference — `MockMvc`](https://docs.spring.io/spring-framework/reference/testing/mockmvc.html)

---

### 13. What's the Difference Between `@Mock` and `@MockitoBean`?

**Answer:**

"`@Mock` is plain Mockito — it creates a mock object as a local field, entirely outside of any Spring context, for use in a plain unit test that doesn't involve Spring at all. `@MockitoBean` is Spring-specific: it creates a Mockito mock **and registers it in the Spring application context**, replacing whatever real bean of that type would otherwise have been wired in — so any *other* bean in the context that autowires a dependency of that type receives the mock instead of the real implementation.

`@MockitoBean` is the current annotation for this (part of Spring Framework's own testing support as of Spring Framework 6.2/Spring Boot 3.4) — it replaces the older `@MockBean`, which was deprecated in Spring Boot 3.4 in favor of `@MockitoBean` being promoted from a Boot-specific extension into core Spring Framework testing support. Existing code using `@MockBean` still works for now, but new code (and this guide) should reach for `@MockitoBean`."

**Code:**

```java
// Plain @Mock — NO Spring context involved at all, a pure unit test
@ExtendWith(MockitoExtension.class)
class OrderServiceUnitTest {
    @Mock private PaymentGateway gateway;
    @InjectMocks private OrderService orderService;
    // orderService is constructed directly by Mockito — Spring never runs here
}

// @MockitoBean — the mock is registered INTO the Spring context itself
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @MockitoBean private OrderService orderService; // replaces the REAL OrderService bean in the context
    // OrderController (loaded by Spring) autowires THIS mock, not the real service
}
```

**Follow-up:**

I'd flag the practical trigger for choosing between them directly: if the test needs a real, running (even if partial) Spring context — a `@WebMvcTest`, `@DataJpaTest`, or full `@SpringBootTest` — and needs to replace one of the beans *within* that context, `@MockitoBean` is the tool, since plain `@Mock` has no mechanism to insert itself into Spring's wiring at all. For a pure, Spring-free unit test constructing the object under test directly, plain `@Mock`/`@InjectMocks` is simpler and doesn't pay any Spring-context startup cost at all.

**Source:** [Spring Framework Reference — `@MockitoBean` and `@MockitoSpyBean`](https://docs.spring.io/spring-framework/reference/testing/annotations/integration-spring/annotation-mockitobean.html)

---

### 14. Why Should Tests Be Independent of Each Other, and What Breaks That Independence?

**Answer:**

"Test independence means any single test's outcome (pass or fail) doesn't depend on whether some *other* test ran before it, or in what order tests happen to execute — each test should be runnable completely on its own and produce the same result regardless of what ran before it. This matters for two concrete, practical reasons: test frameworks don't guarantee a specific execution order by default (and even when they do, relying on it is fragile), and independence is exactly what makes **parallel test execution** possible at all — tests that secretly depend on shared, mutated state can't be safely run concurrently, since one test's mutation can race with or corrupt another's expectations.

The most common ways independence breaks: a shared, mutable `static` field that one test modifies and a later test implicitly depends on; a shared database row/table that one test's data setup or cleanup affects; or a test relying on file-system state left behind by a previous test. `@BeforeEach` resetting state to a known baseline (covered in Question 1) is the standard defense against the first category; careful, per-test data setup/teardown is the defense against the other two."

**Code:**

```java
// BAD — implicitly depends on execution order and shared static state
class BadCounterTest {
    static int counter = 0; // SHARED across every test — a real independence violation

    @Test
    void firstTest() { counter++; assertEquals(1, counter); } // only passes if it runs FIRST

    @Test
    void secondTest() { counter++; assertEquals(2, counter); } // only passes if it runs SECOND, after firstTest
}

// GOOD — each test starts from a known, independent baseline
class GoodCounterTest {
    private Counter counter;

    @BeforeEach
    void setUp() { counter = new Counter(); } // fresh instance, every single test

    @Test
    void increment_fromZero_resultsInOne() {
        counter.increment();
        assertEquals(1, counter.value()); // correct regardless of what ran before this test, or in what order
    }
}
```

**Follow-up:**

I'd tie this directly to test-suite performance at scale: a large, slow test suite is often made tractable specifically by running tests in parallel — but that's only safe if every test is genuinely independent, which is exactly why "our tests can't be parallelized" is frequently, on investigation, actually "our tests have hidden shared-state dependencies," a real, fixable design problem rather than an inherent property of the codebase — this connects directly to the CI-test-structuring question covered later in this guide.

**Source:** [JUnit User Guide — Test Execution Order (and why it's discouraged to rely on)](https://docs.junit.org/6.0.2/writing-tests/test-execution-order.html)

---

### 15. What Is Testcontainers, and What Problem Does It Solve?

**Answer:**

"Testcontainers is a Java library that programmatically starts real, throwaway Docker containers — a real PostgreSQL instance, a real Kafka broker, a real Redis instance — for the duration of a test, and tears them down automatically afterward. It exists specifically to close the gap between 'my tests pass against an embedded/in-memory substitute' and 'my code actually works against the real thing' — an in-memory H2 database (covered in the `@DataJpaTest` question earlier) is fast but isn't PostgreSQL, and a hand-rolled fake Kafka isn't real Kafka; Testcontainers lets integration tests run against the genuine dependency, with real version-specific behavior, without needing a shared, manually-managed test environment that every developer and CI run has to coordinate around.

The practical trade-off versus mocking or an embedded substitute: Testcontainers tests are slower (starting a real container takes real time) and require Docker to be available wherever the tests run (a genuine CI/local-dev environment requirement), but they catch a category of bug — a real SQL dialect incompatibility, a real client-library version mismatch — that mocks and embedded substitutes structurally can't."

**Code:**

```java
@SpringBootTest
@Testcontainers
class OrderRepositoryIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

    @DynamicPropertySource
    static void configureDataSource(DynamicPropertyRegistry registry) {
        // point the application's real datasource config at THIS throwaway container
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired private OrderRepository orderRepository;

    @Test
    void savesAndRetrievesOrder() {
        Order saved = orderRepository.save(new Order("SKU-1", 2));
        assertTrue(orderRepository.findById(saved.getId()).isPresent());
        // this ran against a REAL PostgreSQL instance, not an H2 substitute
    }
}
```

**Follow-up:**

I'd mention container reuse/lifecycle management as the practical performance lever once a suite has many Testcontainers-backed tests: starting a fresh container per test class is correct but can add real minutes to a CI run at scale, so sharing one container across an entire test class (a `static` field, as in the example, scoped to the class rather than per-test) — or, more aggressively, Testcontainers' own container-reuse feature across an entire test *run* — is the standard way to keep the realism benefit without paying a fresh container-startup cost for every single test.

**Source:** [Testcontainers — Official Documentation](https://testcontainers.com/), [Testcontainers for Java — Spring Boot Integration](https://testcontainers.com/guides/testing-spring-boot-rest-api-using-testcontainers/)

---

## Staff Level — Scenario-Based Testing

### 16. How Would You Test a Service That Calls an External Payment Gateway?

**Answer:**

"I'd test this at multiple levels, each answering a different question, rather than trying to get one test to cover everything. At the **unit level**, I'd mock the payment gateway client entirely (via `@Mock`/Mockito) and test `OrderService`'s own logic in isolation — does it correctly handle a success response, a decline, a timeout, mapping each to the right internal state — without any real network call, fast and deterministic. At the **integration level**, if the gateway provides an official sandbox/test environment (most real payment providers do — Stripe's test mode, for instance), I'd run a smaller number of tests against that sandbox specifically to verify the actual request/response contract still matches what the unit tests assumed, since a mocked contract can silently drift from the real API's actual behavior over time.

I would **not** call the real production payment gateway from an automated test suite at all — that's slow, potentially costs real money or creates real side effects, and makes the suite's reliability depend on a third party's uptime, none of which belongs in a test suite that needs to run reliably and repeatedly in CI."

**Code:**

```java
// UNIT level — mock the gateway entirely, fast, tests OrderService's OWN logic
@Test
void chargeCard_gatewayDeclines_marksOrderAsPaymentFailed() {
    when(paymentGateway.charge(any())).thenReturn(PaymentResult.declined("insufficient_funds"));

    OrderResult result = orderService.process(order);

    assertEquals(OrderStatus.PAYMENT_FAILED, result.status());
    assertEquals("insufficient_funds", result.failureReason());
}

// INTEGRATION level — a SMALL number of tests against the provider's real sandbox,
// verifying the actual API contract, not exhaustively re-testing OrderService's logic
@Test
@Tag("sandbox-integration") // run less frequently than the unit suite — a real network dependency
void stripeSandbox_validCardCharge_returnsSuccessResult() {
    PaymentResult result = realStripeClient.charge(sandboxTestCard, new BigDecimal("10.00"));
    assertTrue(result.isSuccess());
}
```

**Follow-up:**

I'd bring up **contract testing** as the more scalable answer once this pattern repeats across many external dependencies, not just one payment gateway — rather than each team hand-maintaining its own understanding of "what does this external API actually return," a formalized contract (verified against the real provider, where the provider supports it, or maintained as an explicitly-owned, versioned fixture otherwise) catches drift between what your mocks assume and what the real dependency actually does, systematically rather than relying on someone noticing a production incident first — the same underlying idea covered for internal service-to-service contracts in the [Microservices & Architecture Patterns guide's consumer-driven contract testing question](../Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md).

**Source:** [Martin Fowler — Testing Strategies in a Microservice Architecture](https://martinfowler.com/articles/microservice-testing/)

---

### 17. How Would You Test an `@Async` Method or a Scheduled Task?

**Answer:**

"The core challenge is that both run on a *different* thread than the test method itself, so a naive test that calls the async method and immediately asserts afterward will very likely run the assertion before the async work has actually finished — a classic race condition in the test itself, not the code under test. For an `@Async` method, the cleanest fix is having it return a `CompletableFuture` (rather than `void`) — the test can then simply call `.get()` (with a timeout) on the returned future, which blocks the *test* thread until the async work genuinely completes, turning an inherently asynchronous operation into something the test can wait on deterministically rather than guessing at timing.

For a `@Scheduled` task specifically, I'd generally avoid testing the *scheduling* itself (waiting for a real trigger to fire is slow and flaky) and instead **extract the actual logic into a separate, directly-callable method**, testing that method as an ordinary synchronous unit test — the `@Scheduled`-annotated method becomes a thin wrapper that just calls it, and that thin wrapper doesn't need its own elaborate test, since there's very little logic left in it worth testing."

**Code:**

```java
// @Async returning a CompletableFuture — the test can await it deterministically
@Async
public CompletableFuture<NotificationResult> sendNotificationAsync(String userId) {
    return CompletableFuture.completedFuture(doSend(userId));
}

@Test
void sendNotificationAsync_completesSuccessfully() throws Exception {
    CompletableFuture<NotificationResult> future = notificationService.sendNotificationAsync("user-1");
    NotificationResult result = future.get(2, TimeUnit.SECONDS); // BLOCKS the test thread until done
    assertTrue(result.isSuccess());
}

// @Scheduled — extract the real logic so IT can be tested directly, synchronously
@Scheduled(cron = "0 0 * * * *")
void runHourlyCleanup() {
    performCleanup(); // thin wrapper — nothing meaningful to unit-test here beyond calling this
}

@Test
void performCleanup_removesExpiredSessions() {
    sessionRepository.save(expiredSession());
    cleanupService.performCleanup(); // call the LOGIC directly, synchronously — no waiting on a real schedule
    assertTrue(sessionRepository.findAll().isEmpty());
}
```

**Follow-up:**

I'd mention Awaitility as the right tool for the genuinely harder case — an async operation with no future/callback to await at all, running on its own executor with no direct handle the test can block on — `await().atMost(2, SECONDS).until(() -> someCondition())` polls a condition until it's true (or times out and fails), which is a real, deliberate library-supported alternative to hand-rolling a sleep-then-check loop, tying directly to the flaky-test and timing-sensitive-testing discipline covered in the [Java Concurrency guide's testing-without-sleeps question](../Language/Java_Concurrency_Interview_Prep.md#29-how-do-you-test-concurrent-code-without-relying-on-timing-sensitive-sleeps) and covered again from the flaky-test angle later in this guide.

**Source:** [Spring Framework Reference — Task Execution and Scheduling](https://docs.spring.io/spring-framework/reference/integration/scheduling.html), [Awaitility](https://github.com/awaitility/awaitility)

---

### 18. How Would You Test a Kafka Producer/Consumer?

**Answer:**

"I'd use different tools at different levels, matching the payment-gateway pattern from earlier in this guide. For a **producer**, the standard tool is `MockProducer` (from the Kafka client library itself) — it records every message the code under test attempts to send, without any real broker involved, letting the test assert exactly what topic, key, and value were published, and simulate a send failure to verify the producer's own error handling. For a **consumer**, `EmbeddedKafka` (Spring Kafka's test support) spins up an actual, in-process, lightweight Kafka broker for the test — genuinely closer to real Kafka behavior (real serialization, real partition assignment) than hand-mocking the consumer's `poll()` loop, without needing an external broker running.

For a higher-fidelity integration test — verifying the application's actual configuration (serializers, consumer group settings, error handling) works correctly, not just the business logic — Testcontainers' Kafka module (covered generally in the Testcontainers question earlier in this guide) runs a real Kafka broker in a container, the most realistic option, at the cost of being the slowest of the three."

**Code:**

```java
// Producer — MockProducer, no real broker, verifies exactly what was published
@Test
void publishOrderCreated_sendsToCorrectTopicWithCorrectKey() {
    MockProducer<String, OrderEvent> mockProducer = new MockProducer<>(true, new StringSerializer(), new OrderEventSerializer());
    OrderEventPublisher publisher = new OrderEventPublisher(mockProducer);

    publisher.publishOrderCreated(new Order("order-123", "SKU-1"));

    ProducerRecord<String, OrderEvent> record = mockProducer.history().get(0);
    assertEquals("order-events", record.topic());
    assertEquals("order-123", record.key());
}

// Consumer — EmbeddedKafka, a real (lightweight, in-process) broker
@SpringBootTest
@EmbeddedKafka(partitions = 1, topics = "order-events")
class OrderEventConsumerTest {
    @Autowired private KafkaTemplate<String, OrderEvent> kafkaTemplate;

    @Test
    void consumesOrderCreatedEvent_updatesOrderStatus() {
        kafkaTemplate.send("order-events", "order-123", new OrderEvent("order-123", "CREATED"));
        // poll/await for the consumer to actually process it, then assert on the resulting side effect
    }
}
```

**Follow-up:**

I'd flag ordering and partition-assignment specifics as the thing that's genuinely hard to fake convincingly with a mock and is exactly why `EmbeddedKafka`/Testcontainers matter here more than in some other dependency-testing scenarios: a consumer's correctness often depends on real partition/consumer-group behavior (which the [Kafka guide](../System%20Design/Kafka_Interview_Prep.md) covers in depth) that a hand-rolled mock consumer would have to reimplement correctly to be a trustworthy test double at all — at that point, using the real (embedded or containerized) broker is usually less work and more trustworthy than maintaining a faithful hand-rolled fake.

**Source:** [Apache Kafka — `MockProducer` Javadoc](https://kafka.apache.org/40/javadoc/org/apache/kafka/clients/producer/MockProducer.html), [Spring for Apache Kafka — Testing](https://docs.spring.io/spring-kafka/reference/testing.html)

---

### 19. How Would You Diagnose and Fix a Flaky Test?

**Answer:**

"A flaky test is one that sometimes passes and sometimes fails against the *same* code, with no actual code change between runs — which means the test's outcome depends on something the test doesn't fully control: timing, execution order, shared state, or genuine non-determinism (a random value, network variance). My diagnostic sequence: first, actually **reproduce it reliably** — run the specific test in a tight loop (dozens or hundreds of times) locally, since a test that fails 1-in-50 runs in CI needs to fail more frequently in a controlled loop to be debuggable at all. Second, look for the classic causes in order of likelihood: a **timing assumption** (a hard-coded `Thread.sleep()` a slow CI runner sometimes doesn't beat — the exact anti-pattern the async-testing question earlier in this guide avoids), **shared state leaking between tests** (covered in the test-independence question earlier), or **test-order dependence** (a test that only passes when a specific other test happens to run first).

Once identified, the fix is almost always removing the actual source of non-determinism, not adding a workaround like a longer sleep or an automatic retry-on-failure — a retry can mask the flakiness in CI output without actually fixing the underlying race, and the same race can eventually manifest as a *real* bug in production under the right timing, not just an annoying flaky test."

**Code:**

```bash
# Reproduce reliably: run the ONE suspect test many times in a tight loop
for i in $(seq 1 100); do
  ./gradlew test --tests "OrderServiceTest.processesOrderWithConcurrentRequests" || echo "FAILED on run $i"
done
```

```java
// The anti-pattern — a hard-coded sleep, "usually" enough time, sometimes not:
Thread.sleep(500); // flaky under CI load — 500ms isn't always enough
assertEquals(ExpectedState.DONE, service.getState());

// The fix — poll a condition with a bounded timeout, instead of guessing a fixed delay:
await().atMost(5, TimeUnit.SECONDS).until(() -> service.getState() == ExpectedState.DONE);
```

**Follow-up:**

I'd bring up the organizational discipline this points at, beyond the individual fix: a team that routinely quarantines/skips flaky tests without ever coming back to actually fix them is slowly eroding the entire suite's signal — eventually, a real failure gets dismissed as "oh, that one's just flaky," which is exactly the failure mode that lets a genuine regression ship. I'd advocate for tracking flaky tests explicitly (a dashboard, a tagged-and-triaged backlog) with an actual ownership expectation, rather than letting `@Disabled`/skip annotations become a silent, permanent graveyard nobody revisits.

**Source:** [Google Testing Blog — Flaky Tests at Google and How We Mitigate Them](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)

---

### 20. How Would You Test Code That Depends on the Current Time?

**Answer:**

"Code that calls `LocalDateTime.now()` (or `Instant.now()`, `System.currentTimeMillis()`) directly is genuinely hard to test deterministically — the 'current time' is different every time the test runs, so an assertion like 'this should be marked expired' only reliably passes or fails depending on exactly when the test happens to execute, which is a real source of tests that pass locally but intermittently fail in CI (or vice versa) purely based on timing.

The standard fix is **dependency-injecting a `Clock`** instead of calling `Instant.now()`/`LocalDateTime.now()` directly inside business logic — `java.time.Clock` is designed exactly for this: production code wires in `Clock.systemDefaultZone()` (the real clock), while a test constructs a `Clock.fixed(specificInstant, zone)` and injects that instead, making 'what time is it right now, from this code's perspective' completely deterministic and fully under the test's control."

**Code:**

```java
// HARD TO TEST — calls Instant.now() directly, buried inside the business logic
class SessionValidator {
    boolean isExpired(Session session) {
        return session.getExpiresAt().isBefore(Instant.now()); // non-deterministic in a test
    }
}

// TESTABLE — Clock is injected, not called globally/statically
class SessionValidator {
    private final Clock clock;
    SessionValidator(Clock clock) { this.clock = clock; }

    boolean isExpired(Session session) {
        return session.getExpiresAt().isBefore(clock.instant()); // deterministic given a fixed Clock
    }
}

@Test
void isExpired_sessionExpiredInThePast_returnsTrue() {
    Instant fixedNow = Instant.parse("2026-01-01T12:00:00Z");
    Clock fixedClock = Clock.fixed(fixedNow, ZoneOffset.UTC);
    SessionValidator validator = new SessionValidator(fixedClock);

    Session expiredSession = new Session(Instant.parse("2026-01-01T11:00:00Z")); // expired ONE HOUR before "now"
    assertTrue(validator.isExpired(expiredSession)); // deterministic — never depends on when the test actually runs
}
```

**Follow-up:**

I'd mention that this same dependency-injection principle generalizes well beyond just the clock: any ambient, globally-called source of non-determinism inside business logic (the current time, a random number, an environment variable read directly) makes that logic harder to test deterministically for the exact same underlying reason — injecting the source (a `Clock`, a `Random`, a configuration value) as an explicit dependency, rather than calling a static/global source directly, is the general pattern that keeps business logic testable, and it's the same underlying discipline the [Spring Boot Internals guide's dependency-injection content](../Frameworks/Spring_Boot_Internals_Interview_Prep.md) covers for the broader "why DI matters" question.

**Source:** [`java.time.Clock` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/Clock.html)

---

### 21. How Would You Manage Test Data for Integration Tests Against a Real Database?

**Answer:**

"The core tension: integration tests need real, representative data in the database to be meaningful, but that data has to be set up predictably and cleaned up reliably, or tests start interfering with each other (violating the independence principle covered earlier in this guide) or accumulating stale data that makes results harder to reason about over time. My default approach: wrap each test in a **transaction that's rolled back at the end** (Spring's `@Transactional` on a test class does exactly this automatically) — the test's own data setup and the code under test's writes both happen inside that transaction, and rolling it back afterward means the database is left exactly as it was before the test ran, with zero manual cleanup code needed.

The one thing this doesn't work for: testing genuine cross-transaction behavior (verifying what a *different* connection/transaction sees while the first is still in-flight) — that specific class of test needs deliberate, explicit setup and teardown instead, since wrapping the whole test in one rolled-back transaction would hide the very cross-transaction behavior being tested."

**Code:**

```java
@SpringBootTest
@Transactional // the ENTIRE test method runs inside one transaction, rolled back automatically after
class OrderRepositoryIntegrationTest {

    @Autowired private OrderRepository orderRepository;

    @Test
    void findByCustomerId_returnsOnlyThatCustomersOrders() {
        orderRepository.save(new Order("customer-1", "SKU-1")); // written inside the test's transaction
        orderRepository.save(new Order("customer-2", "SKU-2"));

        List<Order> results = orderRepository.findByCustomerId("customer-1");

        assertEquals(1, results.size());
        // after this test method returns, Spring ROLLS BACK the transaction —
        // both saved orders are gone, no manual cleanup, no leftover data for the NEXT test
    }
}
```

**Follow-up:**

I'd bring up test data **builders**/factory methods as the practical tool for keeping data setup itself readable at scale — a raw `new Order("customer-1", "SKU-1", ...)` with a dozen constructor arguments, repeated across many tests, becomes unreadable and brittle to constructor changes; a builder (`anOrder().withCustomer("customer-1").withSku("SKU-1").build()`) with sensible defaults for everything not explicitly overridden keeps each test's setup focused on the one or two fields that specific test actually cares about, which is a real, compounding readability win once a test suite has hundreds of tests each needing slightly different data.

**Source:** [Spring Framework Reference — Transaction Management in Tests](https://docs.spring.io/spring-framework/reference/testing/testcontext-framework/tx.html)

---

### 22. How Would You Decide Between Mocking a Dependency and Using Testcontainers for It?

**Answer:**

"This is fundamentally a speed-versus-fidelity trade-off, and I'd frame the decision around what the specific test is actually trying to verify. **Mock the dependency** when the test's goal is to verify *my own code's logic* — how `OrderService` reacts to a payment success versus a decline, independent of how the real payment gateway's network protocol actually works — since a mock is fast, deterministic, and keeps the test focused narrowly on the logic actually being tested, without the overhead or setup complexity of a real dependency. **Use Testcontainers** (or another real-dependency approach) when the test's goal is to verify the **integration itself** — does my actual SQL query run correctly against real PostgreSQL, does my actual Kafka consumer configuration correctly deserialize a real message — since these are exactly the class of bug a mock, by construction, can never catch (a mock only ever behaves exactly as programmed, never surprises you the way a real dependency's actual behavior can).

In practice, a well-designed test suite uses both, deliberately, at different layers: many fast unit tests using mocks for business-logic coverage, and a smaller number of Testcontainers-backed integration tests specifically covering the handful of places the application actually talks to a real external system — mirroring the general test-pyramid shape covered in the [Computer Science Fundamentals guide's testing question](../Computer%20Science%20Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md#28-whats-the-difference-between-unit-integration-and-end-to-end-tests)."

**Code:**

```text
Testing OrderService's DISCOUNT LOGIC — mock the dependency:
  -> fast, many cases, focused purely on OrderService's own branching logic
  MOCK the PaymentGateway and InventoryService — their real behavior isn't what's under test here

Testing that the ACTUAL SQL QUERY in OrderRepository works correctly against PostgreSQL:
  -> Testcontainers — a mock can't catch a real SQL dialect mismatch,
     since a mock only ever returns exactly what it was told to return
```

**Follow-up:**

I'd give the concrete anti-pattern worth naming directly: mocking a database repository entirely and only ever testing against that mock means a genuinely broken SQL query (a typo in a `@Query` JPQL string, a join that doesn't actually match the schema) can pass every unit test and only surface in production — this is exactly the gap a small number of real, Testcontainers-backed repository tests are meant to close, and it's why "we have 95% unit test coverage" isn't the same claim as "we've verified our actual database interactions work," a distinction worth making explicitly in a staff-level answer about test strategy.

**Source:** [Testcontainers — Official Documentation](https://testcontainers.com/)

---

### 23. How Would You Design a Test Strategy for a Legacy Codebase With No Existing Tests?

**Answer:**

"I wouldn't start by trying to retroactively write comprehensive tests for everything — that's an enormous, low-leverage effort against code whose actual behavior (bugs included) might be load-bearing for existing users, and it's easy to burn weeks without meaningfully reducing risk. Instead, I'd start with **characterization tests**: tests that capture the system's *actual current behavior*, bugs and all, as a safety net specifically for the next change, rather than tests that assert what the 'correct' behavior *should* be — the goal at this stage is 'don't let this next refactor silently change behavior,' not 'verify this code is right.'

Concretely, I'd prioritize coverage around whatever part of the codebase the *next planned change* actually touches — writing characterization tests for the specific methods/classes about to be modified, immediately before modifying them — rather than a top-down, comprehensive coverage effort across the entire codebase. This directly ties the testing investment to real, immediate risk reduction (this specific upcoming change is now safer) instead of an open-ended, hard-to-prioritize 'improve coverage generally' initiative that's difficult to justify against other work and easy to deprioritize indefinitely."

**Code:**

```java
// A characterization test — captures EXISTING behavior as-is, including anything
// questionable, specifically so an upcoming refactor doesn't silently change it
@Test
void calculateShipping_currentBehavior_forInternationalOrder() {
    // Written by RUNNING the existing code and recording what it actually returns —
    // not by reasoning about what the "correct" shipping cost formula should be
    BigDecimal result = legacyShippingCalculator.calculate(internationalOrder());
    assertEquals(new BigDecimal("47.50"), result); // whatever it ACTUALLY currently returns
    // If this number looks wrong on inspection, that's a separate, deliberate decision
    // to fix later — not something to silently "correct" while writing this safety net
}
```

**Follow-up:**

I'd bring up the "seam" concept (from Michael Feathers' *Working Effectively with Legacy Code*) as the practical technique for the hardest part of this problem — legacy code is often genuinely difficult to test because it's tightly coupled (a static call, a `new SomeDependency()` buried inside business logic, no dependency injection at all) — a 'seam' is a place in the code where behavior can be changed (typically, a dependency substituted) without editing that line of code itself, and finding/creating seams (introducing an interface, extracting a constructor parameter) incrementally, only where the next change actually needs one, is usually a far more tractable strategy than a wholesale upfront rewrite for testability.

**Source:** [Michael Feathers — *Working Effectively with Legacy Code*](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)

---

### 24. How Should Test Suites Be Structured and Run in CI to Avoid Becoming a Bottleneck?

**Answer:**

"I'd structure the suite in layered tiers, matching the test pyramid (covered in the [Computer Science Fundamentals guide](../Computer%20Science%20Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md#28-whats-the-difference-between-unit-integration-and-end-to-end-tests)) directly onto CI stages: a fast unit-test tier (seconds, runs on every single commit/PR, no external dependencies at all) gates quickly and cheaply; a slower integration tier (Testcontainers-backed, database/Kafka-dependent tests, covered throughout this guide) runs on every PR but is allowed to take longer; and a genuinely slow end-to-end tier runs less frequently (on merge to main, or on a schedule) rather than blocking every single PR, since E2E tests are both the slowest and, structurally, the most prone to flakiness of the three tiers.

Beyond tiering, **parallelization** is the other major lever — since independent tests (covered earlier in this guide) can safely run concurrently, splitting the suite across multiple CI workers/threads is usually the highest-leverage way to keep a growing suite's wall-clock time from creeping up linearly with the number of tests, as long as the independence discipline from earlier in this guide is actually maintained (parallelizing a suite with hidden shared-state dependencies just produces new, environment-dependent flakiness instead of speeding anything up safely)."

**Code:**

```text
CI pipeline, tiered:

  Stage 1: Unit tests           (seconds)    -> every commit, every PR — fast, cheap gate
  Stage 2: Integration tests    (minutes)    -> every PR — Testcontainers-backed, real dependencies
  Stage 3: E2E tests            (10s of min) -> on merge to main, or nightly — slowest, most flake-prone

# Parallelizing WITHIN a stage — splitting the suite across multiple workers:
./gradlew test --tests "*ServiceTest" &
./gradlew test --tests "*RepositoryTest" &
wait
```

**Follow-up:**

I'd bring up flaky-test quarantine as the practical policy worth having explicitly, tying directly back to the flaky-test question earlier in this guide: a known-flaky test should be tagged and *excluded* from the blocking gate (so it doesn't erode trust in CI by failing PRs for unrelated reasons) while remaining tracked and owned for an actual fix — the failure mode to avoid is either extreme: leaving a flaky test blocking merges (which trains people to ignore CI failures and re-run reflexively) or quietly deleting/disabling it forever with no tracking (which silently loses whatever real coverage it provided).

**Source:** [Google Testing Blog — Test Sizes (Small/Medium/Large as a tiering model)](https://testing.googleblog.com/2010/12/test-sizes.html)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| JUnit User Guide — Annotations | https://docs.junit.org/6.0.2/writing-tests/annotations.html |
| JUnit User Guide — Assertions | https://docs.junit.org/6.0.2/writing-tests/assertions.html |
| JUnit User Guide — Parameterized Tests | https://docs.junit.org/6.1.0/writing-tests/parameterized-classes-and-tests.html |
| JUnit User Guide — Test Execution Order | https://docs.junit.org/6.0.2/writing-tests/test-execution-order.html |
| Martin Fowler — GivenWhenThen | https://martinfowler.com/bliki/GivenWhenThen.html |
| Martin Fowler — Mocks Aren't Stubs | https://martinfowler.com/articles/mocksArentStubs.html |
| Martin Fowler — Testing Strategies in a Microservice Architecture | https://martinfowler.com/articles/microservice-testing/ |
| Mockito — Official Site | https://site.mockito.org/ |
| Mockito — `@InjectMocks` Javadoc | https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/InjectMocks.html |
| JaCoCo — Java Code Coverage Library | https://www.jacoco.org/jacoco/trunk/doc/ |
| Spring Boot Reference — Testing Spring Boot Applications | https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html |
| Spring Framework Reference — `MockMvc` | https://docs.spring.io/spring-framework/reference/testing/mockmvc.html |
| Spring Framework Reference — `@MockitoBean`/`@MockitoSpyBean` | https://docs.spring.io/spring-framework/reference/testing/annotations/integration-spring/annotation-mockitobean.html |
| Spring Framework Reference — Transaction Management in Tests | https://docs.spring.io/spring-framework/reference/testing/testcontext-framework/tx.html |
| Spring Framework Reference — Task Execution and Scheduling | https://docs.spring.io/spring-framework/reference/integration/scheduling.html |
| Spring for Apache Kafka — Testing | https://docs.spring.io/spring-kafka/reference/testing.html |
| Apache Kafka — `MockProducer` Javadoc | https://kafka.apache.org/40/javadoc/org/apache/kafka/clients/producer/MockProducer.html |
| Testcontainers — Official Documentation | https://testcontainers.com/ |
| Testcontainers — Spring Boot REST API Testing Guide | https://testcontainers.com/guides/testing-spring-boot-rest-api-using-testcontainers/ |
| Awaitility | https://github.com/awaitility/awaitility |
| `java.time.Clock` Javadoc, JDK 21 | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/Clock.html |
| Google Testing Blog — Flaky Tests at Google | https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html |
| Google Testing Blog — Test Sizes | https://testing.googleblog.com/2010/12/test-sizes.html |
| Michael Feathers — *Working Effectively with Legacy Code* | https://www.oreilly.com/library/view/working-effectively-with/0131177052/ |
