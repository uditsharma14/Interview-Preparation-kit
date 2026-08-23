# Software Testing — Interview Prep for SDET & QA Roles, Basic to Staff Level (with Code & Sources)

> **Target level:** Basic → Staff (graduated — see below) · **Baseline:** ISTQB Certified Tester Foundation Level (CTFL) v4.0.1 terminology for testing fundamentals · JUnit 6.x (Jupiter programming model — unchanged from JUnit 5, but JUnit 6 requires Java 17+ and is the current major version) · Mockito 5.x · Spring Framework 6.x/Spring Boot 3.4+ testing support (`@MockitoBean`, the current annotation — the older `@MockBean` was deprecated in Spring Boot 3.4) · Testcontainers · Selenium 4.x WebDriver · REST Assured · Cucumber/Gherkin · Apache JMeter/Gatling · **Last verified:** 2026-08-23 · **Prerequisites:** none for the testing-fundamentals and types-of-testing questions at the start of the Basic section; [Java Collections](../Language/Java_Collections_Interview_Prep.md) becomes relevant once the guide moves into JUnit/Mockito, [Spring Boot Internals](../Frameworks/Spring_Boot_Internals_Interview_Prep.md) helpful from the Intermediate section onward, [JPA & Hibernate](../Frameworks/JPA_Hibernate_Interview_Prep.md) helpful for the `@DataJpaTest`/Testcontainers questions

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **code snippet** you could sketch on a whiteboard or IDE to back it up, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar isn't naming annotations or tools, it's explaining testing terminology precisely, choosing the right test type/tool for the job, and reasoning through something genuinely hard to test (an external dependency, async code, a flaky UI suite, a performance target) and why. The guide starts with QA/SDET testing fundamentals and types of testing (no code required), moves into Java/Spring-specific testing mechanics (JUnit, Mockito, Spring Boot test slices), then SDET automation tooling (Selenium, API testing, BDD/Cucumber, the test pyramid), and finishes with Staff-level scenario-based questions. The later sections assume the earlier ones as background and don't re-explain them.

<!-- toc -->
## Table of Contents

- [Basic](#basic)
  - [1. What Is Software Testing, and What's the Difference Between Verification and Validation?](#1-what-is-software-testing-and-whats-the-difference-between-verification-and-validation)
  - [2. What Is the Software Testing Life Cycle (STLC)?](#2-what-is-the-software-testing-life-cycle-stlc)
  - [3. What's the Difference Between a Test Plan, a Test Strategy, and a Test Case?](#3-whats-the-difference-between-a-test-plan-a-test-strategy-and-a-test-case)
  - [4. What's the Difference Between Functional and Non-Functional Testing?](#4-whats-the-difference-between-functional-and-non-functional-testing)
  - [5. What's the Difference Between Black-Box, White-Box, and Gray-Box Testing?](#5-whats-the-difference-between-black-box-white-box-and-gray-box-testing)
  - [6. What's the Difference Between Smoke Testing, Sanity Testing, and Regression Testing?](#6-whats-the-difference-between-smoke-testing-sanity-testing-and-regression-testing)
  - [7. What's the Difference Between Manual Testing and Test Automation, and When Would You Automate a Test?](#7-whats-the-difference-between-manual-testing-and-test-automation-and-when-would-you-automate-a-test)
  - [8. What Is the Defect Life Cycle, and What's the Difference Between Severity and Priority?](#8-what-is-the-defect-life-cycle-and-whats-the-difference-between-severity-and-priority)
  - [9. What Is JUnit, and What Do `@Test`, `@BeforeEach`, and `@AfterEach` Do?](#9-what-is-junit-and-what-do-test-beforeeach-and-aftereach-do)
  - [10. What's the Difference Between an Assertion Failure and an Exception in a Test?](#10-whats-the-difference-between-an-assertion-failure-and-an-exception-in-a-test)
  - [11. What Is the AAA (Arrange-Act-Assert) Pattern?](#11-what-is-the-aaa-arrange-act-assert-pattern)
  - [12. What's the Difference Between a Mock, a Stub, and a Spy?](#12-whats-the-difference-between-a-mock-a-stub-and-a-spy)
  - [13. What Is Mockito, and How Do You Create and Use a Basic Mock?](#13-what-is-mockito-and-how-do-you-create-and-use-a-basic-mock)
  - [14. What's the Difference Between `@Mock` and `@InjectMocks`?](#14-whats-the-difference-between-mock-and-injectmocks)
  - [15. What Makes a Good Test Name, and Why Does It Matter?](#15-what-makes-a-good-test-name-and-why-does-it-matter)
  - [16. What Is Test Coverage, and Why Isn't 100% Coverage the Goal?](#16-what-is-test-coverage-and-why-isnt-100-coverage-the-goal)
- [Intermediate](#intermediate)
  - [17. What Are `@ParameterizedTest`, `@ValueSource`, and `@CsvSource`, and When Would You Use Them?](#17-what-are-parameterizedtest-valuesource-and-csvsource-and-when-would-you-use-them)
  - [18. How Do You Test That a Method Throws the Expected Exception?](#18-how-do-you-test-that-a-method-throws-the-expected-exception)
  - [19. What's the Difference Between `@SpringBootTest`, `@WebMvcTest`, and `@DataJpaTest`?](#19-whats-the-difference-between-springboottest-webmvctest-and-datajpatest)
  - [20. What Is `MockMvc`, and How Do You Use It to Test a REST Controller?](#20-what-is-mockmvc-and-how-do-you-use-it-to-test-a-rest-controller)
  - [21. What's the Difference Between `@Mock` and `@MockitoBean`?](#21-whats-the-difference-between-mock-and-mockitobean)
  - [22. Why Should Tests Be Independent of Each Other, and What Breaks That Independence?](#22-why-should-tests-be-independent-of-each-other-and-what-breaks-that-independence)
  - [23. What Is Testcontainers, and What Problem Does It Solve?](#23-what-is-testcontainers-and-what-problem-does-it-solve)
  - [24. What Is API Testing, and What Does a Typical REST API Test Verify?](#24-what-is-api-testing-and-what-does-a-typical-rest-api-test-verify)
  - [25. What Is Selenium WebDriver, and How Does It Locate and Interact with Elements?](#25-what-is-selenium-webdriver-and-how-does-it-locate-and-interact-with-elements)
  - [26. What Is the Page Object Model (POM), and Why Is It Used in UI Automation?](#26-what-is-the-page-object-model-pom-and-why-is-it-used-in-ui-automation)
  - [27. What Is BDD, and What Role Does Gherkin/Cucumber Play in It?](#27-what-is-bdd-and-what-role-does-gherkincucumber-play-in-it)
  - [28. What's the Difference Between Data-Driven Testing and Keyword-Driven Testing?](#28-whats-the-difference-between-data-driven-testing-and-keyword-driven-testing)
  - [29. What Is the Test Automation Pyramid, and Why Does It Recommend Fewer UI Tests Than Unit Tests?](#29-what-is-the-test-automation-pyramid-and-why-does-it-recommend-fewer-ui-tests-than-unit-tests)
- [Staff Level — Scenario-Based Testing](#staff-level--scenario-based-testing)
  - [30. How Would You Test a Service That Calls an External Payment Gateway?](#30-how-would-you-test-a-service-that-calls-an-external-payment-gateway)
  - [31. How Would You Test an `@Async` Method or a Scheduled Task?](#31-how-would-you-test-an-async-method-or-a-scheduled-task)
  - [32. How Would You Test a Kafka Producer/Consumer?](#32-how-would-you-test-a-kafka-producerconsumer)
  - [33. How Would You Diagnose and Fix a Flaky Test?](#33-how-would-you-diagnose-and-fix-a-flaky-test)
  - [34. How Would You Test Code That Depends on the Current Time?](#34-how-would-you-test-code-that-depends-on-the-current-time)
  - [35. How Would You Manage Test Data for Integration Tests Against a Real Database?](#35-how-would-you-manage-test-data-for-integration-tests-against-a-real-database)
  - [36. How Would You Decide Between Mocking a Dependency and Using Testcontainers for It?](#36-how-would-you-decide-between-mocking-a-dependency-and-using-testcontainers-for-it)
  - [37. How Would You Design a Test Strategy for a Legacy Codebase With No Existing Tests?](#37-how-would-you-design-a-test-strategy-for-a-legacy-codebase-with-no-existing-tests)
  - [38. How Should Test Suites Be Structured and Run in CI to Avoid Becoming a Bottleneck?](#38-how-should-test-suites-be-structured-and-run-in-ci-to-avoid-becoming-a-bottleneck)
  - [39. How Would You Design a Test Automation Framework from Scratch for a New Product?](#39-how-would-you-design-a-test-automation-framework-from-scratch-for-a-new-product)
  - [40. How Would You Diagnose a Flaky UI/Selenium Test, as Opposed to a Flaky Unit Test?](#40-how-would-you-diagnose-a-flaky-uiselenium-test-as-opposed-to-a-flaky-unit-test)
  - [41. How Would You Approach Performance/Load Testing for a New API?](#41-how-would-you-approach-performanceload-testing-for-a-new-api)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## Basic

### 1. What Is Software Testing, and What's the Difference Between Verification and Validation?

**Answer:**

"Software testing is the process of evaluating a system or its components to find out whether it satisfies specified requirements, and to identify defects before the software reaches production — it's simultaneously an information-gathering activity (how good or bad is this build) and a risk-reduction activity (catch this bug before a customer does). Two closely related but genuinely distinct concepts sit underneath that definition: **verification** asks 'are we building the product right?' — confirming, through review, inspection, or testing, that a work product (a design doc, a piece of code, a build) meets its specified requirements at each stage of development. **Validation** asks 'are we building the right product?' — confirming that the finished system actually meets the real-world needs of its stakeholders, which a work product can satisfy on paper (verified against a spec) while still being validated as wrong, because the spec itself didn't capture what users actually needed.

A concrete way to keep them apart: a code review confirming a login form matches its design spec is verification; a user testing that same login form and finding it genuinely confusing to use, even though it matches the spec exactly, is a validation failure — the software does what was specified, but not what was actually needed."

**Code:**

```text
VERIFICATION — "Are we building the product right?"
  - Code review against a design document
  - Unit tests checking a function against its specification
  - Static analysis confirming coding standards are followed

VALIDATION — "Are we building the right product?"
  - User acceptance testing (UAT) with real stakeholders
  - Beta testing with actual end users
  - A demo where a product owner confirms the feature solves the real problem
```

**Follow-up:**

I'd bring up why this distinction matters in practice beyond terminology: a project can pass every verification check (100% of specified requirements implemented and tested correctly) and still fail in the market, because the specification itself was validated too late or not at all — this is exactly the failure mode agile practices (short iterations, frequent stakeholder demos) are designed to catch early, by folding validation into every sprint rather than deferring it to a single UAT phase at the very end of a waterfall-style project.

**Source:** [ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)

---

### 2. What Is the Software Testing Life Cycle (STLC)?

**Answer:**

"STLC is the structured sequence of phases a testing effort moves through for a given release or feature — commonly broken into: **requirement analysis** (understanding what needs to be tested, from a testability standpoint), **test planning** (defining scope, approach, resources, schedule — producing the test plan), **test case development** (writing the actual test cases and test data), **test environment setup** (provisioning the environment the tests will run against), **test execution** (running the tests and logging results/defects), and **test cycle closure** (evaluating exit criteria, summarizing results, capturing lessons learned). ISTQB's own foundation syllabus describes this same sequence somewhat more granularly as the 'test process' — test planning, monitoring and control, analysis, design, implementation, execution, and completion — the underlying activities are the same regardless of which exact label a given company or textbook uses.

In practice, these phases are rarely a strict, one-way waterfall even inside an agile project — test analysis and design often start well before a feature is code-complete (test cases can be written directly from acceptance criteria during sprint planning), and test execution happens continuously as code lands rather than as one big phase at the end."

**Code:**

```text
STLC phases (ISTQB's "test process" activities in parentheses):

1. Requirement Analysis         (-> Test Analysis)
2. Test Planning                (-> Test Planning)
3. Test Case Development        (-> Test Design + Test Implementation)
4. Test Environment Setup       (-> Test Implementation)
5. Test Execution               (-> Test Execution)
6. Test Cycle Closure           (-> Test Completion)

Running throughout: Test Monitoring and Control (tracking progress against the plan)
```

**Follow-up:**

I'd mention entry and exit criteria as the practical mechanism that makes this more than a checklist — each phase, most importantly test execution, should have explicit, agreed-upon entry criteria (is the build actually stable enough to start testing) and exit criteria (what defect-severity or coverage threshold has to be met before calling testing "done" for this cycle) — without those, "testing is complete" becomes a subjective, argued-about judgment call rather than something the team agreed on in advance.

**Source:** [ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)

---

### 3. What's the Difference Between a Test Plan, a Test Strategy, and a Test Case?

**Answer:**

"These three sit at different altitudes. A **test strategy** is the highest-level, most durable of the three — an organization- or program-level document describing the general approach to testing across multiple projects (which test levels will be used, what the default automation approach is, how risk is generally assessed) — it changes rarely and isn't tied to any one release. A **test plan** is project- or release-specific — a document describing the scope, approach, resources, and schedule of testing for *this* specific effort: what's in scope, what test design techniques will be used, who's doing what, what the test environment looks like, and the entry/exit criteria for this particular cycle. A **test case** is the most granular of the three — a single, concrete set of preconditions, input values, execution steps, and expected results, written to exercise one specific behavior or requirement.

The relationship is roughly hierarchical: the test strategy sets the ground rules an organization's test plans generally follow; each test plan then scopes and schedules the testing for one specific release; and the actual test cases are what get written and executed within that plan."

**Code:**

```text
Test Strategy   (organization-wide, long-lived)
  -> "We target 70% unit / 20% integration / 10% E2E automated coverage across all projects.
      Manual exploratory testing runs before every major release."

  Test Plan     (this release, this project)
    -> "For the v2.4 checkout release: in scope is the new payment flow;
        out of scope is the existing shipping calculator (unchanged).
        Entry criteria: staging deploy green. Exit criteria: 0 open Critical/High defects."

    Test Case   (one specific, executable check)
      -> "Given a cart with 1 item and a valid coupon code,
          when the user applies the coupon,
          then the discounted total should be shown before checkout."
```

**Follow-up:**

I'd flag the practical failure mode this distinction helps avoid: teams that never write an explicit test strategy end up re-deciding the same foundational questions (how much should we automate, what's our default regression scope) on every single project, inconsistently — a lightweight, living test strategy is what lets each individual test plan stay short and mostly just fill in the project-specific details rather than re-litigating strategy from scratch every time.

**Source:** [ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)

---

### 4. What's the Difference Between Functional and Non-Functional Testing?

**Answer:**

"**Functional testing** verifies *what* the system does — does it correctly implement the behavior described in its requirements, specifications, or use cases (does clicking 'submit' actually place the order, does an invalid coupon code get correctly rejected). It's fundamentally about correctness of behavior, and it's most naturally evaluated as a black-box technique (covered next in this guide) — testing what goes in and what comes out, without needing to know how the system does it internally. **Non-functional testing** verifies *how well* the system does it — attributes of the system that aren't about any single specific behavior, like performance (how fast, under what load), security (can it be compromised), usability (how easy is it to use correctly), reliability (does it stay up), and portability (does it work across environments).

A system can pass every functional test — every feature does exactly what it's supposed to — and still be genuinely unusable in production if it fails on the non-functional side: correct behavior that takes 30 seconds to respond, or correct behavior that's trivially exploitable, isn't actually shippable, which is exactly why both categories need deliberate test coverage rather than treating 'does the feature work' as the only bar."

**Code:**

```text
FUNCTIONAL — "does it do the right thing?"
  - Does the login form correctly reject a wrong password?
  - Does the checkout flow correctly apply a valid discount code?

NON-FUNCTIONAL — "does it do it well enough?"
  - Performance: does the search endpoint respond in under 200ms at p99?
  - Security: can an authenticated user access another user's order by guessing an ID?
  - Usability: can a first-time user complete checkout without external help?
  - Reliability: does the service recover cleanly from a dependency timing out?
```

**Follow-up:**

I'd tie this to how it shapes test planning practically: functional test cases tend to map fairly directly onto individual requirements or acceptance criteria and are the natural target for automation early on, while non-functional testing (load testing, security testing, usability testing) often needs dedicated tooling and specialized skill, sometimes a separate specialist (a performance engineer, a security tester) — a team that only ever measures "percentage of requirements covered by tests" is implicitly measuring functional coverage alone, and can miss a system that's functionally correct but operationally unfit to ship.

**Source:** [ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)

---

### 5. What's the Difference Between Black-Box, White-Box, and Gray-Box Testing?

**Answer:**

"These describe how much internal knowledge of the system the person designing the test has, and how that knowledge is (or isn't) used. **Black-box testing** derives test cases purely from external specification — requirements, specs, user-facing behavior — with zero reference to the system's internal code structure; the tester treats the system as a closed box, only caring about inputs and outputs. **White-box testing** goes the opposite direction: test cases are derived from the system's actual internal structure — its code paths, branches, conditions — with the explicit goal of exercising specific lines, branches, or paths a black-box approach might never happen to hit (this is where structural, coverage-guided test design, covered from the coverage-metric angle earlier in this guide, actually comes from). **Gray-box testing** sits between the two: the tester has *some* internal knowledge (the database schema, the API's internal architecture, how two services communicate) and uses it to design smarter black-box-style tests, without going as far as testing individual code branches directly.

In practice, most SDET/QA test-case design leans black-box (testing against requirements and API contracts, independent of implementation), while developers writing unit tests are naturally doing white-box testing (they know exactly which branches their own code has), and integration testing across service boundaries is often genuinely gray-box (knowing the API contract and rough architecture, without needing to read every line of the other service's code)."

**Code:**

```text
BLACK-BOX  — tester knows: the spec/requirements only
  -> "Given these inputs, the spec says I should get this output" — test written with zero code access

WHITE-BOX  — tester knows: the actual source code
  -> "This method has an if/else — I need one test case per branch to get full branch coverage"

GRAY-BOX   — tester knows: some internals (schema, API contract, architecture) but not full source
  -> "I know this endpoint writes to two tables — I'll verify both got updated, without reading the handler code"
```

**Follow-up:**

I'd mention that this isn't a strict either/or in practice — a mature test suite deliberately uses all three at different layers: white-box unit tests (owned by developers, exercising every branch), black-box API/functional tests (owned by SDETs, exercising the contract), and gray-box integration tests bridging services — and being able to name which category a given test in a suite actually falls into is a genuinely useful diagnostic when a test suite feels like it has redundant or misplaced coverage.

**Source:** [ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)

---

### 6. What's the Difference Between Smoke Testing, Sanity Testing, and Regression Testing?

**Answer:**

"All three run *after* some change, but at different scope and depth. **Smoke testing** is a broad, shallow check run against a brand-new build — a small set of tests covering the system's most critical, must-work functionality (can a user log in, does the homepage load, does checkout complete at all) — its only job is to answer 'is this build stable enough to bother testing further,' not to find subtle bugs. **Sanity testing** is narrower and deeper than smoke testing, but scoped specifically to a *recent, specific change* — after a bug fix or a small feature change, sanity testing verifies that the specific area affected now works as expected, without re-running the full regression suite. **Regression testing** is the broadest of the three — re-running previously-passing tests, ideally the automated suite, after a change, specifically to catch unintended side effects the change may have introduced in *unrelated* areas of the system that nobody was deliberately trying to change.

A useful way to keep the three straight: smoke asks 'is this build even worth testing,' sanity asks 'did this specific fix actually work,' and regression asks 'did fixing that break something else.'"

**Code:**

```text
SMOKE      — new build, broad + shallow: "is this build stable enough to test further at all?"
  -> login works, homepage loads, checkout completes end-to-end (once, happy path only)

SANITY     — after a specific fix, narrow + deep: "did THIS fix actually work?"
  -> the exact bug that was reported is now verified fixed, plus its immediate surrounding behavior

REGRESSION — after any change, broad: "did this change break something UNRELATED?"
  -> re-run the full previously-passing suite (or a representative subset) across the whole system
```

**Follow-up:**

I'd bring up automation as the practical lever that makes this distinction operational rather than theoretical: smoke and regression suites are the natural candidates for full automation, run on every build or every PR, since they're meant to be run constantly and cheaply, while sanity checks are often still done manually in the moments right after a fix, since they're one-off and narrowly scoped to something that just changed — a team's CI pipeline structure, covered from the Java/Spring testing angle later in this guide, usually mirrors this exact split.

**Source:** [ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)

---

### 7. What's the Difference Between Manual Testing and Test Automation, and When Would You Automate a Test?

**Answer:**

"Manual testing is a human executing test steps and judging the result directly, without a script running the check; test automation is a script or tool executing those same steps and asserting the result programmatically, without a human needed for each run. Automation's advantage is repeatability and speed at scale — an automated regression suite can re-run thousands of checks in minutes, every single build, at essentially zero marginal human cost per run — but it comes with real upfront cost (writing and maintaining the automation) and a real blind spot: automation only ever checks exactly what it was told to check, so it's structurally bad at catching the kind of surprising, unanticipated issue a human actually *notices* while using the product.

The practical decision rule I'd use: automate a test when it's going to be run repeatedly — regression, smoke, anything re-run on every build — and its expected result is stable and well-defined; keep it manual, or more precisely, use **exploratory testing** (a test approach where a skilled tester simultaneously designs and executes tests based on their own judgment and what they learn as they go, rather than following a pre-written script) — for one-off checks, genuinely subjective usability judgment, and specifically for finding the kind of bug nobody thought to write an automated check for in the first place."

**Code:**

```text
GOOD candidate for automation:
  - Regression suite run on every PR (same checks, run hundreds of times)
  - Smoke tests run after every deploy
  - Data-heavy boundary-value test cases (many input/output pairs, stable expected results)

GOOD candidate for manual / exploratory testing:
  - A brand-new feature nobody has used yet — no established "expected result" to automate against
  - Subjective usability judgment ("does this actually feel confusing to a first-time user?")
  - A one-off investigation of a specific bug report, before a fix even exists to write a regression test against
```

**Follow-up:**

I'd mention the common mistake this framing helps avoid: treating "100% automated" as an inherently good target — a team that automates a test that only ever runs once, or automates a check whose expected result changes constantly (making the automation itself high-maintenance), often spends more effort maintaining that automation than the manual check would ever have cost; the right question isn't "can this be automated" but "will this be run often enough, with a stable enough expected result, that automating it actually pays back the upfront cost."

**Source:** [ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)

---

### 8. What Is the Defect Life Cycle, and What's the Difference Between Severity and Priority?

**Answer:**

"The defect (bug) life cycle is the sequence of states a reported defect moves through from discovery to resolution — typically: **New** (just logged), **Assigned** (a developer is on it), **Open/In Progress** (being actively worked), **Fixed** (a fix has been implemented), **Retest** (QA verifies the fix), then either **Closed** (verified fixed) or **Reopened** (the fix didn't actually resolve it, cycling back). Some teams also have a **Rejected**/**Duplicate**/**Deferred** branch for defects that turn out not to be bugs, are already tracked elsewhere, or are consciously postponed.

**Severity** and **priority** are the two dimensions used to triage a defect within that life cycle, and they answer genuinely different questions. **Severity** measures *technical impact* — how badly does this defect affect the system's functionality, does it crash the whole app or is it a cosmetic misalignment — and is typically assessed by whoever finds or verifies the defect (QA). **Priority** measures *business urgency* — how soon does this need to be fixed, relative to everything else in the backlog — and is typically set by product or business stakeholders. The two don't always move together: a typo in a rarely-seen legal disclaimer is low severity but can be high priority (a legal/compliance deadline); a crash in a rarely-used admin-only debug feature can be high severity but low priority, since barely anyone hits it."

**Code:**

```text
Defect life cycle:
  New -> Assigned -> Open/In Progress -> Fixed -> Retest -> Closed
                                                          -> Reopened (back to Open/In Progress)
  (also: Rejected / Duplicate / Deferred, branching off "New")

Severity vs. Priority — genuinely independent axes:

                    HIGH PRIORITY              LOW PRIORITY
  HIGH SEVERITY   "Checkout is down"        "Crash in an unused
                   (fix now)                  admin-only tool"
                                              (fix eventually)

  LOW SEVERITY    "Wrong year in the        "Button is 2px
                   footer copyright"          misaligned on
                   (fix now — legal ask)      a rarely-used page"
                                              (low priority, low severity)
```

**Follow-up:**

I'd bring up why keeping these genuinely separate matters practically: a bug tracker that conflates severity and priority into one field pressures whoever's triaging to guess at business urgency while also judging technical impact, and the two disagreements get silently merged into one number — keeping them as two explicit fields lets QA report severity honestly, based purely on what the defect does to the system, while product or business independently decides priority, based on what's actually urgent right now, and the disagreement between the two — a high-severity, low-priority bug sitting in the backlog — becomes a visible, deliberate decision rather than a hidden one.

**Source:** [ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)

---

### 9. What Is JUnit, and What Do `@Test`, `@BeforeEach`, and `@AfterEach` Do?

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

### 10. What's the Difference Between an Assertion Failure and an Exception in a Test?

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

### 11. What Is the AAA (Arrange-Act-Assert) Pattern?

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

### 12. What's the Difference Between a Mock, a Stub, and a Spy?

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

### 13. What Is Mockito, and How Do You Create and Use a Basic Mock?

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

### 14. What's the Difference Between `@Mock` and `@InjectMocks`?

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

### 15. What Makes a Good Test Name, and Why Does It Matter?

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

### 16. What Is Test Coverage, and Why Isn't 100% Coverage the Goal?

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

### 17. What Are `@ParameterizedTest`, `@ValueSource`, and `@CsvSource`, and When Would You Use Them?

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

### 18. How Do You Test That a Method Throws the Expected Exception?

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

### 19. What's the Difference Between `@SpringBootTest`, `@WebMvcTest`, and `@DataJpaTest`?

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

### 20. What Is `MockMvc`, and How Do You Use It to Test a REST Controller?

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

### 21. What's the Difference Between `@Mock` and `@MockitoBean`?

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

### 22. Why Should Tests Be Independent of Each Other, and What Breaks That Independence?

**Answer:**

"Test independence means any single test's outcome (pass or fail) doesn't depend on whether some *other* test ran before it, or in what order tests happen to execute — each test should be runnable completely on its own and produce the same result regardless of what ran before it. This matters for two concrete, practical reasons: test frameworks don't guarantee a specific execution order by default (and even when they do, relying on it is fragile), and independence is exactly what makes **parallel test execution** possible at all — tests that secretly depend on shared, mutated state can't be safely run concurrently, since one test's mutation can race with or corrupt another's expectations.

The most common ways independence breaks: a shared, mutable `static` field that one test modifies and a later test implicitly depends on; a shared database row/table that one test's data setup or cleanup affects; or a test relying on file-system state left behind by a previous test. `@BeforeEach` resetting state to a known baseline (covered in the JUnit annotations question earlier in this guide) is the standard defense against the first category; careful, per-test data setup/teardown is the defense against the other two."

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

### 23. What Is Testcontainers, and What Problem Does It Solve?

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

### 24. What Is API Testing, and What Does a Typical REST API Test Verify?

**Answer:**

"API testing verifies a service's behavior directly at the API layer — sending real (or realistically simulated) HTTP requests and asserting on the response — without going through a UI at all. It sits below UI-driven end-to-end testing and above pure unit testing in the test pyramid (covered later in this guide): faster and more stable than driving a browser, but still exercising the real, deployed contract a client actually depends on, not just an internal method call. A typical REST API test verifies several things at once: the **status code** (200 for success, 404 for not found, 400 for a bad request), the **response body's shape and values** (does the JSON contain the right fields, with the right values and types), **response headers** (content type, caching headers, rate-limit headers), and, for state-changing requests, that the **side effect actually happened** (a subsequent GET reflects the change the POST or PUT made).

Tools like REST Assured (Java, a fluent given/when/then syntax purpose-built for HTTP assertions) or Postman (a GUI-first tool, also scriptable and CI-runnable via Newman) are the standard way to write these tests outside of Spring's own `MockMvc` (covered earlier in this guide) — the key difference from `MockMvc` being that a REST Assured or Postman test typically hits a *real, running* service over the network, verifying the full stack including the actual HTTP server, not just Spring's in-process request-dispatch machinery."

**Code:**

```java
import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;

@Test
void getOrder_existingId_returns200WithCorrectBody() {
    given()
        .baseUri("https://api.example.com")
        .header("Authorization", "Bearer " + testToken)
    .when()
        .get("/orders/123")
    .then()
        .statusCode(200)
        .body("sku", equalTo("SKU-1"))
        .body("quantity", equalTo(2))
        .header("Content-Type", equalTo("application/json"));
}

@Test
void createOrder_validPayload_persistsAndIsRetrievable() {
    String orderId =
        given().contentType("application/json").body(newOrderJson)
        .when().post("/orders")
        .then().statusCode(201).extract().path("id");

    // verify the side effect actually happened, not just that POST returned 201
    given().when().get("/orders/" + orderId)
           .then().statusCode(200).body("sku", equalTo("SKU-1"));
}
```

**Follow-up:**

I'd mention API testing's specific value for an SDET role beyond just being faster than UI tests: since it tests directly against the contract a mobile app, a web frontend, and any third-party integration all independently depend on, a broken API test catches a breaking change *before* any of those consumers do — which is exactly why API test suites are often the highest-leverage layer of automation for a service with multiple client types, catching contract breakage a UI-only test suite covering just one client would miss entirely.

**Source:** [REST Assured — Official Documentation](https://rest-assured.io/)

---

### 25. What Is Selenium WebDriver, and How Does It Locate and Interact with Elements?

**Answer:**

"Selenium WebDriver is the core browser-automation API within the Selenium project — it lets a test drive a real browser programmatically (clicking, typing, navigating, reading page content) by talking to the browser's own native automation interface, via each browser's WebDriver implementation like ChromeDriver, rather than simulating input at the OS level. The fundamental workflow is: **locate** an element on the page, then **interact** with it. Locating is done via a `By` strategy — `By.id`, `By.cssSelector`, `By.xpath`, `By.className`, and others — each trading off robustness (does this locator still work after a minor UI change) against specificity (can it uniquely identify the one element you actually want). Once located, WebDriver exposes interaction methods on the returned `WebElement` — `.click()`, `.sendKeys()`, `.getText()`, `.isDisplayed()` — that drive the browser exactly as a real user's mouse and keyboard would.

The general locator-strategy guidance: prefer `id` when the application provides stable ones, since it's fastest and least brittle; fall back to CSS selectors for anything without a stable ID; and treat XPath as a last resort for cases CSS genuinely can't express, like selecting an element by its visible text, since XPath expressions tend to be the most brittle against markup changes and the slowest to evaluate."

**Code:**

```java
WebDriver driver = new ChromeDriver();
driver.get("https://example.com/login");

// LOCATE, then INTERACT — the fundamental WebDriver pattern
WebElement usernameField = driver.findElement(By.id("username"));
WebElement passwordField = driver.findElement(By.cssSelector("input[name='password']"));
WebElement loginButton  = driver.findElement(By.xpath("//button[text()='Log In']"));

usernameField.sendKeys("test-user");
passwordField.sendKeys("test-password");
loginButton.click();

WebElement welcomeBanner = driver.findElement(By.className("welcome-banner"));
assertTrue(welcomeBanner.isDisplayed());
assertEquals("Welcome, test-user", welcomeBanner.getText());

driver.quit(); // always release the browser session, even on failure (typically in @AfterEach)
```

**Follow-up:**

I'd flag explicit waits as the thing that separates a reliable Selenium suite from a flaky one: a page's elements often aren't present the instant `driver.get()` returns, since JavaScript may still be rendering or an API call may still be in flight, so calling `findElement` immediately can throw `NoSuchElementException` intermittently — `WebDriverWait` combined with `ExpectedConditions.visibilityOfElementLocated(...)` polls for the element to actually be ready instead of guessing at a fixed delay, the same underlying anti-pattern — a hard-coded sleep versus polling for a real condition — covered from the flaky-test angle later in this guide.

**Source:** [Selenium — Official Documentation, WebDriver Locators](https://www.selenium.dev/documentation/webdriver/elements/locators/)

---

### 26. What Is the Page Object Model (POM), and Why Is It Used in UI Automation?

**Answer:**

"The Page Object Model is a design pattern for UI test automation where each page, or significant component, of the application under test gets its own class — a 'page object' — encapsulating that page's locators and the actions a test can perform on it, behind a clean method-level API. Instead of a test directly calling `driver.findElement(By.id("username")).sendKeys(...)`, it calls a method like `loginPage.loginAs(username, password)`, with the page object internally owning the locator details.

The value is almost entirely about maintainability: a UI's markup changes far more often than its actual user-facing behavior does — a CSS class gets renamed during a redesign, an element gets wrapped in a new container — without POM, that single markup change means hunting down and fixing every test that happens to reference that locator directly; with POM, it means updating the locator in exactly one place, the page object, and every test that uses that page object is automatically fixed. It also makes tests themselves read more like a description of user intent, 'log in, then verify the order confirmation shows,' rather than a sequence of low-level driver calls, which is a real readability win independent of the maintenance benefit."

**Code:**

```java
// Page Object — owns locators and actions for ONE page
class LoginPage {
    private final WebDriver driver;
    private final By usernameField = By.id("username");
    private final By passwordField = By.cssSelector("input[name='password']");
    private final By loginButton = By.xpath("//button[text()='Log In']");

    LoginPage(WebDriver driver) { this.driver = driver; }

    HomePage loginAs(String username, String password) {
        driver.findElement(usernameField).sendKeys(username);
        driver.findElement(passwordField).sendKeys(password);
        driver.findElement(loginButton).click();
        return new HomePage(driver); // returns the NEXT page — models real navigation
    }
}

// The test itself reads like user intent, with ZERO locator details in it
@Test
void login_validCredentials_showsWelcomeBanner() {
    LoginPage loginPage = new LoginPage(driver);
    HomePage homePage = loginPage.loginAs("test-user", "test-password");

    assertTrue(homePage.isWelcomeBannerDisplayed());
    // if the username field's locator ever changes, ONLY LoginPage needs updating — not this test
}
```

**Follow-up:**

I'd bring up the natural extension of this pattern worth mentioning at a Staff/SDET level: a shared **base page** class or interface for behavior common to every page (waiting for the page to finish loading, checking for a global error banner) avoids duplicating that logic across every individual page object, and chaining page-object methods that return the *next* page object, as `loginAs()` does above by returning `HomePage`, keeps a multi-step user flow readable as a single fluent chain in the test, rather than a flat sequence of unrelated driver calls.

**Source:** [Selenium — Official Documentation, Page Object Models](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/)

---

### 27. What Is BDD, and What Role Does Gherkin/Cucumber Play in It?

**Answer:**

"Behavior-Driven Development (BDD) is a practice where a feature's expected behavior is described collaboratively, up front, in a structured, plain-language format that both technical and non-technical stakeholders — product, QA, engineering — can read and agree on. The goal is closing the gap between what the business actually wants and what gets built and tested, by making the shared specification itself executable as a test, rather than letting requirements and tests drift apart as separate artifacts. Gherkin is the specific structured language BDD scenarios are written in, using the `Given`/`When`/`Then` keywords — the same Arrange-Act-Assert idea covered earlier in this guide, just phrased for a business audience rather than a developer one — to describe a precondition, an action, and an expected outcome. Cucumber is the tool that makes a Gherkin scenario *executable*: it parses the `.feature` file and matches each line to a 'step definition,' actual code that performs the real action or assertion, so the same plain-language scenario a product manager reads is literally what runs as the automated test.

This matters specifically for an SDET role because it shifts test-case authorship left and makes it collaborative — a well-run BDD process has acceptance criteria written as Gherkin scenarios *before* a feature is built, agreed on by product, QA, and engineering together, which then become the actual automated regression tests once step definitions are wired up — rather than QA reverse-engineering test cases from a finished feature after the fact."

**Code:**

```gherkin
# login.feature — written in plain language, readable by product/QA/engineering alike
Feature: User login

  Scenario: Successful login with valid credentials
    Given a registered user with username "test-user" and password "test-password"
    When the user submits the login form with those credentials
    Then the user should see the welcome banner
    And the user should be redirected to the home page
```

```java
// Step definitions — the ACTUAL code Cucumber runs for each Gherkin line above
public class LoginSteps {
    private final WebDriver driver;
    private LoginPage loginPage;
    private HomePage homePage;

    @Given("a registered user with username {string} and password {string}")
    public void aRegisteredUser(String username, String password) {
        testDataSetup.createUser(username, password);
        loginPage = new LoginPage(driver); // reuses the Page Object Model from earlier in this guide
    }

    @When("the user submits the login form with those credentials")
    public void submitsLoginForm() {
        homePage = loginPage.loginAs(username, password);
    }

    @Then("the user should see the welcome banner")
    public void seesWelcomeBanner() {
        assertTrue(homePage.isWelcomeBannerDisplayed());
    }
}
```

**Follow-up:**

I'd mention the common failure mode worth naming directly: BDD's value comes specifically from the *collaboration* around writing scenarios together, not from the Gherkin syntax itself — a team that has engineers write Gherkin scenarios alone, after the feature is already built, purely as a syntax wrapper around what would've been a normal automated test anyway, gets all of Gherkin's verbosity with none of BDD's actual benefit, which is shared, agreed-upon acceptance criteria written before the code; that's a real, common critique of BDD adoptions worth being able to speak to directly in an interview.

**Source:** [Cucumber — Official Gherkin Reference](https://cucumber.io/docs/gherkin/)

---

### 28. What's the Difference Between Data-Driven Testing and Keyword-Driven Testing?

**Answer:**

"Both are automation techniques for separating *what varies between test runs* from the automation script itself, but they separate different things. **Data-driven testing** separates the *test data* from a fixed control script — the same script runs repeatedly, once per row in a table, spreadsheet, or CSV of inputs and expected results (this is the same underlying idea as `@CsvSource`/`@ParameterizedTest`, covered earlier in this guide, just applied at a larger, often non-code-based scale — a QA-maintained spreadsheet rather than a hard-coded annotation). **Keyword-driven testing** goes a step further and separates the *test logic itself*, not just the data, into a data file: each row specifies a keyword, such as `Login`, `ClickButton`, or `VerifyText`, representing a reusable action, and a supporting 'keyword interpreter' script maps each keyword to actual automation code, letting someone build entire test cases by combining keywords in a spreadsheet, without writing code for each new test case at all.

The practical trade-off: data-driven testing is simpler to build and maintain but still requires someone who can write or modify the control script for genuinely new test *logic*, not just new data; keyword-driven testing has a steeper upfront framework-building cost, since someone has to build and maintain the keyword interpreter and its full keyword library, but it pays that back by letting non-programmers — manual QA, business analysts — author new test cases directly, entirely within the keyword vocabulary, once the framework exists."

**Code:**

```text
DATA-DRIVEN — same fixed script, varying data:

  username,   password,   expectedResult
  test-user,  correct-pw, success
  test-user,  wrong-pw,   failure
  ,           correct-pw, failure   <- missing username

  (ONE control script: "attempt login with this row's data, assert this row's expected result")

KEYWORD-DRIVEN — varying data AND varying logic, expressed as keywords:

  Keyword           | Target               | Value
  OpenBrowser        | https://example.com  |
  EnterText          | usernameField         | test-user
  EnterText          | passwordField          | correct-pw
  ClickElement         | loginButton            |
  VerifyTextVisible     | welcomeBanner           | Welcome, test-user

  (an interpreter script maps EACH keyword — OpenBrowser, EnterText, ClickElement, VerifyTextVisible —
   to real WebDriver code; a new test case is just a new sequence of existing keywords)
```

**Follow-up:**

I'd tie this to a practical staff-level framework-design decision: building a keyword-driven layer is a real, deliberate investment that only pays off when a team genuinely has non-programmers who need to author test cases independently and at real volume — for a team of SDETs who are all comfortable writing code directly, a well-organized data-driven approach, or just well-factored code with the Page Object Model covered earlier in this guide, usually delivers most of the same reuse benefit with far less framework-maintenance overhead than a full keyword-driven interpreter layer.

**Source:** [ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)

---

### 29. What Is the Test Automation Pyramid, and Why Does It Recommend Fewer UI Tests Than Unit Tests?

**Answer:**

"The test pyramid is a model, popularized by Mike Cohn and widely cited via Martin Fowler's write-up of it, for how a healthy automated test suite's *proportions* should look across layers: many fast, cheap, focused unit tests at the base; a smaller number of integration and API tests, covered earlier in this guide, in the middle; and a small number of slow, broad, UI-driven end-to-end tests at the top. The shape isn't arbitrary — it directly reflects each layer's actual cost, speed, and stability trade-off: a unit test runs in milliseconds, needs no external dependencies, and fails with a precise, easy-to-diagnose signal pointing at exactly the broken code; a UI test drives a real browser through a real, or near-real, full stack, which is inherently slower, more expensive to run at scale, and structurally more prone to flakiness — timing, rendering, environment differences — and when a UI test fails, it's often much harder to tell *which* layer of the stack actually broke.

The practical implication for an SDET/QA automation strategy: push as much coverage as reasonably possible down to the unit and API layers, where it's fast and stable, and reserve UI automation specifically for the things that can only genuinely be verified by actually driving the UI, a handful of true end-to-end critical-path journeys — an 'inverted pyramid,' or 'ice cream cone,' anti-pattern, where a team has mostly UI tests and few unit tests, is a well-known, common failure mode that produces a slow, flaky, expensive-to-maintain suite for the amount of actual confidence it provides."

**Code:**

```text
                    /\
                   /  \      UI / End-to-End tests  — FEW, slow, broad, most flake-prone
                  /----\
                 /      \    Integration / API tests — SOME, covered earlier in this guide
                /--------\
               /          \  Unit tests             — MANY, fast, cheap, precise failure signal
              /____________\

Anti-pattern — the "ice cream cone" (inverted pyramid):
              ______________
              \            /  MANY slow, flaky UI tests
               \----------/
                \        /    some integration tests
                 \------/
                  \    /      FEW unit tests
                   \  /
                    \/
```

**Follow-up:**

I'd mention that the pyramid is a *shape guideline*, not a rigid ratio to enforce mechanically — the right proportions genuinely differ by system, since a UI-heavy consumer product legitimately needs more UI coverage than a pure backend API, but the underlying principle, push a check down to the cheapest, fastest, most stable layer that can actually verify it, holds regardless of the exact ratio, and it's the same underlying reasoning covered from the mocking-vs-Testcontainers angle later in this guide.

**Source:** [Martin Fowler — TestPyramid](https://martinfowler.com/bliki/TestPyramid.html)

---

## Staff Level — Scenario-Based Testing

### 30. How Would You Test a Service That Calls an External Payment Gateway?

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

### 31. How Would You Test an `@Async` Method or a Scheduled Task?

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

### 32. How Would You Test a Kafka Producer/Consumer?

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

### 33. How Would You Diagnose and Fix a Flaky Test?

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

### 34. How Would You Test Code That Depends on the Current Time?

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

### 35. How Would You Manage Test Data for Integration Tests Against a Real Database?

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

### 36. How Would You Decide Between Mocking a Dependency and Using Testcontainers for It?

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

### 37. How Would You Design a Test Strategy for a Legacy Codebase With No Existing Tests?

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

### 38. How Should Test Suites Be Structured and Run in CI to Avoid Becoming a Bottleneck?

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

### 39. How Would You Design a Test Automation Framework from Scratch for a New Product?

**Answer:**

"I'd start from the test pyramid, covered earlier in this guide, as the shape I'm designing toward, then work through the concrete decisions layer by layer rather than starting with tooling choices. First, **structure and layering**: separate the framework into distinct, independently-runnable layers — unit, API, UI — each with its own execution-speed expectations and its own place in CI, covered from the Java/Spring angle later in this guide. Second, **the core abstractions**: a Page Object Model layer for UI, covered earlier in this guide, so locators live in one place, a dedicated API client layer wrapping REST Assured/HTTP calls so endpoint details aren't duplicated across every test, and shared test-data builders so tests aren't hand-constructing complex objects field by field. Third, **environment and data management**: how does a test get a clean, known environment and known data to run against — Testcontainers, covered from the Java/Spring angle earlier in this guide, for backing services, and a deliberate test-data strategy, seeded fixtures or an API-driven setup step, rather than relying on whatever happens to already be in a shared environment.

I'd deliberately *not* try to build the full framework upfront before writing any real tests — I'd build the thinnest possible version of each layer against the first few real test cases, then extend the framework as genuinely new needs show up, the same incremental-seam-finding discipline covered in the legacy-codebase test strategy question later in this guide, just applied to greenfield framework design instead of retrofitting one onto existing code."

**Code:**

```text
Framework structure, by layer:

  /tests
    /unit           — fast, no external deps, run on every commit
    /api             — REST Assured-based, run against a deployed test environment
    /ui               — Selenium + Page Object Model, run last, smallest count

  /framework
    /pages            — Page Object Model classes (one per UI page/component)
    /api-clients       — one client class per API resource, wrapping REST Assured calls
    /test-data          — builder classes with sensible defaults (anOrder().withSku("SKU-1").build())
    /config              — environment configuration (base URLs, credentials, per-environment overrides)

  Decision checklist, in order:
    1. What are the FIRST 5-10 real test cases we actually need? Build only what THEY need.
    2. How do tests get a clean environment/data? (Testcontainers for services, builders for data)
    3. How do these layers plug into CI? (tiered stages, covered later in this guide)
    4. What's the reporting/triage story when something fails? (screenshots on UI failure, structured logs)
```

**Follow-up:**

I'd bring up reporting and triage-ability as the thing that's easy to underinvest in early and expensive to retrofit later: a UI test failure with no screenshot, no page source dump, and no clear failure message forces whoever's triaging to reproduce the failure locally just to understand what broke — building in automatic failure artifacts, a screenshot, the browser console log, a clear assertion message naming what was expected versus actual, from the very first test, rather than after the suite is already large, is a cheap decision early and a genuinely expensive one to add retroactively across hundreds of existing tests.

**Source:** [Selenium — Official Documentation, Test Practices](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/)

---

### 40. How Would You Diagnose a Flaky UI/Selenium Test, as Opposed to a Flaky Unit Test?

**Answer:**

"The general flaky-test diagnostic discipline covered earlier in this guide still applies — reproduce reliably, look for a timing, shared-state, or order-dependence cause — but UI automation has its own specific, additional failure modes worth checking first, since they're disproportionately common there compared to unit-test flakiness. The most common by far: **synchronization** — the test interacted with, or asserted on, an element before the page actually finished rendering or loading it, which is exactly what explicit waits, covered from the Selenium-basics angle earlier in this guide, exist to prevent; a suite still using fixed `Thread.sleep()` calls instead of `WebDriverWait`/`ExpectedConditions` is almost always going to be flaky under any real load or CI-runner slowness. Second: **environment or state pollution** — a previous test left the browser in an unexpected state, a modal still open, a cookie or session not cleared, which is the UI-specific version of the shared-state-independence problem covered earlier in this guide, just manifesting through browser/session state instead of application/database state. Third: **environment differences** — a test that passes locally but fails in CI, or vice versa, because of a different browser version, screen resolution, or headless-versus-headed rendering difference, which unit tests essentially never have to deal with at all.

For genuinely hard-to-reproduce cases, I'd lean on the failure artifacts mentioned in the framework-design question earlier in this guide, a screenshot and page source captured automatically at the moment of failure, rather than trying to reproduce a UI-specific race condition purely by re-running the test locally, since local runs are often on a different machine, browser, or network profile than the CI environment where the flakiness actually showed up."

**Code:**

```java
// The anti-pattern — a fixed sleep, guessing at "long enough":
driver.findElement(By.id("submit")).click();
Thread.sleep(2000); // flaky — sometimes not enough time, always wastes time when it IS enough
WebElement confirmation = driver.findElement(By.className("confirmation"));

// The fix — explicit wait, polling for the actual condition:
driver.findElement(By.id("submit")).click();
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement confirmation = wait.until(
    ExpectedConditions.visibilityOfElementLocated(By.className("confirmation"))
);

// Capturing failure artifacts automatically — invaluable for diagnosing failures
// that only reproduce in CI, not locally:
@AfterEach
void captureArtifactsOnFailure(TestInfo testInfo) {
    if (testFailed) {
        File screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
        // save alongside test report, named after testInfo.getDisplayName()
    }
}
```

**Follow-up:**

I'd mention headless-versus-headed rendering differences specifically as a subtle, easy-to-miss category worth naming: a test suite run headless in CI can genuinely behave differently from the same suite run headed locally — element visibility calculations, viewport size defaults, some CSS/JS behavior tied to actual rendering — so when a test only fails in CI and never locally, checking whether the local reproduction is actually running in the same headless mode as CI is a fast, easy check to rule out before assuming the flakiness is something more subtle like a genuine race condition.

**Source:** [Google Testing Blog — Flaky Tests at Google and How We Mitigate Them](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)

---

### 41. How Would You Approach Performance/Load Testing for a New API?

**Answer:**

"I'd start by getting explicit, quantified requirements before writing a single load test — 'is it fast enough' isn't answerable without knowing the target throughput in requests per second, acceptable latency, often expressed as p50/p95/p99 rather than just an average, since averages hide the tail latency users actually notice, and the expected concurrent-user scale — since without those numbers, a load test has no actual pass/fail criteria. With targets defined, I'd distinguish the different test types deliberately rather than running one generic 'load test': **load testing** verifies behavior at expected, realistic peak traffic; **stress testing** pushes well beyond that peak specifically to find the system's actual breaking point and how it fails, gracefully with backpressure and clear errors, or catastrophically; **soak testing** runs a sustained, moderate load over a long duration specifically to catch slow degradation, such as a memory leak or a connection pool slowly exhausting, that a short test wouldn't surface.

Tool-wise, Apache JMeter, GUI-driven or scriptable and broadly language-agnostic since it works at the HTTP-protocol level, and Gatling, Scala-based and code-first, often preferred when load tests need to live alongside the codebase in version control, are the two most common choices for this — either works; the tool matters far less than having quantified targets and testing all three of load, stress, and soak, not just one 'happy path at expected traffic' scenario."

**Code:**

```text
Performance testing types, each answering a different question:

  LOAD TEST   — "Does it meet its SLA at EXPECTED peak traffic?"
    -> ramp to target RPS, hold for a representative duration, verify p95/p99 latency stays within SLA

  STRESS TEST — "Where does it actually BREAK, and how gracefully?"
    -> ramp well past expected peak until errors/latency spike; verify it degrades gracefully
       (clear 503s with backpressure) rather than catastrophically (cascading failure, data corruption)

  SOAK TEST   — "Does it degrade over TIME under sustained load?"
    -> moderate, realistic load held for hours, watching for memory growth, connection pool exhaustion,
       or slowly increasing latency that a short test would never catch
```

```groovy
// Gatling — a load-test scenario, code-first
class OrderApiSimulation extends Simulation {
  val httpProtocol = http.baseUrl("https://api.example.com")

  val scn = scenario("Get Order")
    .exec(http("get_order").get("/orders/123").check(status.is(200)))

  setUp(
    scn.inject(rampUsersPerSec(10) to 200 during (2 minutes)) // ramp to target load
  ).protocols(httpProtocol)
   .assertions(global.responseTime.percentile3.lt(300)) // p95 under 300ms — the actual SLA target
}
```

**Follow-up:**

I'd bring up test-environment fidelity as the caveat worth stating explicitly in a staff-level answer: a load test run against an undersized staging environment — fewer instances, a smaller database, no CDN in front — can produce numbers that don't actually predict production behavior at all, either falsely reassuring, since staging happens to handle the load fine because traffic is artificially low elsewhere, or falsely alarming, since staging chokes at a load production's larger fleet would handle easily — for genuinely high-stakes launches, running load tests against a production-like environment, or carefully against a controlled slice of real production traffic, is worth the extra setup cost specifically to avoid that gap between what was tested and what actually ships.

**Source:** [Apache JMeter — Official Documentation](https://jmeter.apache.org/)

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
| ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1 | https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf |
| REST Assured — Official Documentation | https://rest-assured.io/ |
| Selenium — Official Documentation, WebDriver Locators | https://www.selenium.dev/documentation/webdriver/elements/locators/ |
| Selenium — Official Documentation, Page Object Models | https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/ |
| Cucumber — Official Gherkin Reference | https://cucumber.io/docs/gherkin/ |
| Martin Fowler — TestPyramid | https://martinfowler.com/bliki/TestPyramid.html |
| Apache JMeter — Official Documentation | https://jmeter.apache.org/ |
