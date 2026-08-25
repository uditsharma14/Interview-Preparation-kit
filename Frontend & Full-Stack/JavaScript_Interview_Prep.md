# JavaScript — Interview Prep (Basic → Staff, with Code & Sources)

> **Target level:** Basic → Staff (graduated — see below) · **Baseline:** ECMAScript 2026 (ES2026, current finalized edition) per the TC39 ECMA-262 specification; V8 (Chrome/Node.js) referenced for engine-specific behavior (GC, JIT) since it's the most commonly discussed engine in interviews · **Last verified:** 2026-08-24 · **Prerequisites:** none for the Basic section; comfort with functions and objects helpful from the Intermediate section onward

How to use this: each question has a **Core answer** (100–180 words, the version you'd actually say out loud in an interview), a **Staff-level extension** covering the deeper judgment and trade-offs the core answer leaves out, a concrete **Example**, **Follow-up questions** an interviewer might ask next, and **Sources**. The guide starts with core language semantics (Basic), moves into the mechanics that show up in almost every real codebase — closures, the event loop, prototypes (Intermediate) — and finishes with the engine-internals and scenario-based questions a Staff-level loop actually presses on.

<!-- toc -->
## Table of Contents

- [Basic](#basic)
  - [1. What's the Difference Between `var`, `let`, and `const`?](#1-whats-the-difference-between-var-let-and-const)
  - [2. What Is Hoisting?](#2-what-is-hoisting)
  - [3. What's the Difference Between `==` and `===`?](#3-whats-the-difference-between--and-)
  - [4. What's the Difference Between a Primitive and a Reference Type?](#4-whats-the-difference-between-a-primitive-and-a-reference-type)
  - [5. What's the Difference Between `null` and `undefined`?](#5-whats-the-difference-between-null-and-undefined)
  - [6. How Does `this` Differ Between a Regular Function and an Arrow Function?](#6-how-does-this-differ-between-a-regular-function-and-an-arrow-function)
- [Intermediate](#intermediate)
  - [7. What Is a Closure, and What Is It Actually Used For?](#7-what-is-a-closure-and-what-is-it-actually-used-for)
  - [8. How Does the Event Loop Work, at a Basic Level?](#8-how-does-the-event-loop-work-at-a-basic-level)
  - [9. How Do Promises and `async`/`await` Relate to Each Other?](#9-how-do-promises-and-asyncawait-relate-to-each-other)
  - [10. How Does Prototypal Inheritance Work?](#10-how-does-prototypal-inheritance-work)
  - [11. What Do `call()`, `apply()`, and `bind()` Actually Do?](#11-what-do-call-apply-and-bind-actually-do)
  - [12. What Are `map()`, `filter()`, and `reduce()`, and Why Prefer Them Over a Loop?](#12-what-are-map-filter-and-reduce-and-why-prefer-them-over-a-loop)
- [Staff Level](#staff-level)
  - [13. Within the Event Loop, What's the Difference Between a Microtask and a Macrotask?](#13-within-the-event-loop-whats-the-difference-between-a-microtask-and-a-macrotask)
  - [14. How Do Closures Cause Memory Leaks in Long-Running Applications?](#14-how-do-closures-cause-memory-leaks-in-long-running-applications)
  - [15. What's the Difference Between Debounce and Throttle, and How Would You Implement Each?](#15-whats-the-difference-between-debounce-and-throttle-and-how-would-you-implement-each)
  - [16. What's the Difference Between CommonJS and ES Modules?](#16-whats-the-difference-between-commonjs-and-es-modules)
  - [17. How Does V8's Garbage Collector Actually Work?](#17-how-does-v8s-garbage-collector-actually-work)
  - [18. How Would You Defend a Web Application Against XSS?](#18-how-would-you-defend-a-web-application-against-xss)
  - [19. Why Does Event Delegation Improve Performance, and When Would You Reach for It?](#19-why-does-event-delegation-improve-performance-and-when-would-you-reach-for-it)
  - [20. How Would You Implement a Simplified Version of `Promise.all()`?](#20-how-would-you-implement-a-simplified-version-of-promiseall)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## Basic

### 1. What's the Difference Between `var`, `let`, and `const`?

**Core answer:**

"`var` is function-scoped (or global-scoped if declared outside a function) and is hoisted with its value initialized to `undefined`, which is exactly why you can reference a `var` before its declaration line without an error — you just get `undefined` instead of the real value. `let` and `const` are block-scoped instead — confined to the nearest `{}`, including a bare block, an `if`, or a `for` loop — and while they're also hoisted, they sit in a 'temporal dead zone' until their declaration actually runs, so accessing one before that line throws a `ReferenceError` instead of silently giving `undefined`. `const` additionally prevents reassignment of the binding itself — the variable can't be pointed at a new value — but that says nothing about the value's own mutability: a `const` array or object can still have its contents changed freely."

**Staff-level extension:**

The practical default worth stating explicitly: reach for `const` first, `let` only when a binding genuinely needs reassignment, and treat `var` as legacy syntax with essentially no reason to write it in new code. The function-scoping vs. block-scoping distinction is what actually causes the classic "loop variable captured by closure" bug: a `var` in a `for` loop is one shared binding across every iteration, so callbacks registered inside the loop all close over the same final value; a `let` creates a fresh binding per iteration, which is why switching `var` to `let` is often the entire fix for that bug, not a stylistic preference.

**Example:**

```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log("var:", i), 0); // prints 3, 3, 3 — one shared binding
}

for (let j = 0; j < 3; j++) {
  setTimeout(() => console.log("let:", j), 0); // prints 0, 1, 2 — a fresh binding per iteration
}

const arr = [1, 2, 3];
arr.push(4);       // fine — mutating the array's contents, not reassigning the binding
console.log(arr);  // [1, 2, 3, 4]
// arr = [5, 6];   // TypeError: Assignment to constant variable.
```

**Follow-up questions:**

- *"Is a `const` object actually immutable?"* — No — `const` only freezes the binding, not the value. Use `Object.freeze()` (shallow) if the object's own properties genuinely shouldn't change.
- *"What is the temporal dead zone, precisely?"* — The span between entering a block and a `let`/`const` declaration's line actually executing, during which the binding exists but accessing it throws.

**Sources:** [MDN — `let`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let), [MDN — `var`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/var), [MDN — `const`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/const)

---

### 2. What Is Hoisting?

**Core answer:**

"Hoisting is the JavaScript engine's behavior of processing variable and function declarations during a compile pass before any code actually runs, so a declaration is 'known' to the engine even if the code that reads it appears earlier in the file than the declaration itself. It behaves differently depending on what's declared: a function declaration is hoisted completely, body included, so it can be called before its line in the source. A `var` declaration is hoisted but only its declaration, not its assignment, so it's `undefined` until the assignment line actually executes. `let` and `const` are hoisted too, technically, but land in the temporal dead zone rather than being usable early, which is why they behave, in practice, as if they weren't hoisted at all."

**Staff-level extension:**

The detail worth being precise about in a Staff-level answer: hoisting isn't literally moving code to the top of the file — it's that the engine builds the scope's variable/function bindings during a compilation phase before execution, so the *effect* looks like the declaration moved, without anything actually being rearranged in source order. Function expressions and arrow functions assigned to a `var`/`let`/`const` are not hoisted the way function declarations are — only the variable binding is hoisted, following that binding's own hoisting rules, while the function value itself is only assigned when that line executes.

**Example:**

```javascript
console.log(hoistedVar);      // undefined — declaration hoisted, assignment isn't
var hoistedVar = "value";

sayHi();                      // "hi" — function declarations are hoisted whole
function sayHi() { console.log("hi"); }

sayBye();                     // TypeError: sayBye is not a function
var sayBye = function () { console.log("bye"); };
```

**Follow-up questions:**

- *"Why does calling `sayBye()` above throw a `TypeError` rather than `ReferenceError`?"* — The `var sayBye` binding is hoisted as `undefined`; calling `undefined` as a function is a `TypeError`, distinct from referencing an undeclared identifier.
- *"Does hoisting apply inside a function body the same way it applies at the top level?"* — Yes — each function creates its own scope, and hoisting happens per-scope, not just once globally.

**Sources:** [MDN — Hoisting](https://developer.mozilla.org/en-US/docs/Glossary/Hoisting), [MDN — `let`, Temporal Dead Zone](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let#temporal_dead_zone_tdz)

---

### 3. What's the Difference Between `==` and `===`?

**Core answer:**

"`===` is strict equality: it compares both value and type, with no conversion — `5 === "5"` is `false`, since one's a number and the other's a string. `==` is loose equality: if the two operands are different types, it applies a documented set of coercion rules before comparing — `5 == "5"` is `true`, because the string gets coerced to a number first. The coercion rules for `==` are genuinely specified and consistent, not random, but they're specific enough (how `null`/`undefined`/booleans/objects each coerce) that most style guides, and the language's own idiomatic advice, recommend defaulting to `===` and only reaching for `==` in the couple of narrow cases where the coercion is exactly what you want."

**Staff-level extension:**

The one broadly-accepted exception worth naming explicitly: `value == null` is a common, deliberate idiom for checking "is this `null` or `undefined`" in one comparison, since `null == undefined` is `true` under `==`'s coercion rules, while `null === undefined` is `false`. Outside that specific idiom, unexplained `==` in a code review is worth asking about, since the coercion table has enough surprising entries (`"" == 0` is `true`, `[] == false` is `true`) that relying on it correctly, rather than accidentally, is a real skill most people don't have memorized.

**Example:**

```javascript
5 === "5";        // false — different types, no coercion
5 == "5";         // true — "5" coerced to 5 first

null === undefined; // false — strict equality, different types
null == undefined;  // true — the one common, deliberate use of ==

"" == 0;    // true  — a classic coercion surprise
[] == false; // true — another one
```

**Follow-up questions:**

- *"What does `Object.is()` add that `===` doesn't cover?"* — It treats `NaN` as equal to itself (`===` says `NaN === NaN` is `false`) and distinguishes `+0`/`-0`, which `===` treats as equal.
- *"Why do most style guides ban `==` outright rather than trusting developers to use it correctly?"* — Because the coercion table has enough non-obvious entries that a reviewer can't tell, from the code alone, whether a given `==` was deliberate or a mistake.

**Sources:** [MDN — Equality comparisons and sameness](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Equality_comparisons_and_sameness), [MDN — Strict equality (`===`)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Strict_equality)

---

### 4. What's the Difference Between a Primitive and a Reference Type?

**Core answer:**

"JavaScript has seven primitive types — `string`, `number`, `bigint`, `boolean`, `undefined`, `symbol`, and `null` — and everything else, objects (including arrays and functions), is a reference type. Primitives are immutable and compared by value: two variables holding the string `"cat"` are equal, and no operation can change a string in place, only produce a new one. Objects are compared by reference: two separately-created objects with identical contents are not `===` equal, since the comparison checks whether both variables point to the same location in memory, not whether their contents match. This is also why passing a primitive into a function can't let that function mutate the caller's variable, while passing an object lets the function mutate the object's own properties, even though the object *reference* itself is still passed by value."

**Staff-level extension:**

That last point is worth stating precisely, since "pass by reference" is the wrong way to describe it and trips people up: JavaScript is always pass-by-value, including for objects — what's passed is a copy of the reference (the memory address), not the object itself. That's why reassigning the parameter inside a function (`param = {}`) never affects the caller's variable, but mutating a property on it (`param.x = 1`) does, since both the caller's variable and the parameter still point at the same underlying object.

**Example:**

```javascript
function tryToChangePrimitive(val) { val = 99; }
let num = 1;
tryToChangePrimitive(num);
console.log(num); // 1 — primitives are copied, the function only changed its own local copy

function mutateObject(obj) { obj.value = 99; }
const ref = { value: 1 };
mutateObject(ref);
console.log(ref.value); // 99 — same underlying object, mutated through the copied reference

function reassignObject(obj) { obj = { value: 100 }; }
reassignObject(ref);
console.log(ref.value); // still 99 — reassigning the parameter doesn't touch the caller's variable
```

**Follow-up questions:**

- *"Is a `string` really immutable, given you can do `str += "x"`?"* — Yes — that expression creates a brand-new string and reassigns the variable to it; it never modifies the original string in place.
- *"How would you deep-copy an object to avoid the shared-reference problem?"* — `structuredClone()` for most cases; `JSON.parse(JSON.stringify(obj))` as an older workaround that silently drops functions, `undefined`, and loses `Date`/`Map`/`Set` fidelity.

**Sources:** [MDN — JavaScript data types and data structures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Data_structures), [MDN — `structuredClone()`](https://developer.mozilla.org/en-US/docs/Web/API/Window/structuredClone)

---

### 5. What's the Difference Between `null` and `undefined`?

**Core answer:**

"`undefined` means a variable has been declared but never assigned a value, or a function parameter wasn't supplied, or a property doesn't exist on an object at all — it's the language's own default for 'nothing was ever put here.' `null` is different in kind: it's a value a developer assigns deliberately to represent 'no value, on purpose' — an intentional absence, not an accidental one. `typeof undefined` is `"undefined"`, while `typeof null` is, famously, `"object"` — a long-standing bug in the language dating back to its earliest implementation that's kept for backward compatibility rather than fixed, since fixing it would break existing code that depends on it."

**Staff-level extension:**

The practical convention worth stating in an interview: use `undefined` for "this was never set" (the language's own default, and the value you get back from an unset object property or a missing function argument) and reserve `null` for "this was explicitly cleared or is intentionally absent" in your own code and APIs — e.g., a `user` variable set to `null` after logout, as opposed to `undefined` before it was ever fetched. Consistently drawing that line makes `=== null` and `=== undefined` checks in a codebase actually mean something, rather than being used interchangeably by convention drift.

**Example:**

```javascript
let a;
console.log(a);          // undefined — declared, never assigned
console.log(typeof a);   // "undefined"

let b = null;
console.log(typeof b);   // "object" — the famous historical quirk

const obj = { x: 1 };
console.log(obj.y);      // undefined — property doesn't exist at all

function greet(name) { console.log(name); }
greet();                 // undefined — no argument supplied
```

**Follow-up questions:**

- *"How does optional chaining (`?.`) relate to this distinction?"* — `obj?.prop` short-circuits to `undefined`, without throwing, if `obj` is `null` or `undefined` — it treats both the same way, since either means "there's nothing here to read a property from."
- *"What does the nullish coalescing operator (`??`) do differently from `||`?"* — `??` only falls back on `null`/`undefined`, while `||` falls back on any falsy value (`0`, `""`, `false` included) — a real behavioral difference when `0` or `""` is a legitimate value you don't want replaced.

**Sources:** [MDN — `undefined`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/undefined), [MDN — `null`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/null), [MDN — Nullish coalescing operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)

---

### 6. How Does `this` Differ Between a Regular Function and an Arrow Function?

**Core answer:**

"A regular function's `this` is determined dynamically, by *how* it's called — call it as a method (`obj.method()`) and `this` is `obj`; call the same function detached from any object and `this` is `undefined` in strict mode (or the global object in non-strict mode). An arrow function doesn't have its own `this` at all — it captures `this` lexically from the enclosing scope at the point it's defined, the same way it captures any other variable via closure, and that binding never changes no matter how the arrow function is later called or invoked. That's exactly why arrow functions are the natural choice for callbacks that need to preserve the surrounding `this` — a `setTimeout` callback or an array method's callback inside a class method — without needing `.bind(this)` or a `const self = this` workaround."

**Staff-level extension:**

This is precisely why arrow functions are the wrong choice for object methods and class fields that need dynamic `this`: a `{ value: 1, getValue: () => this.value }` object's `getValue` doesn't bind `this` to the object at all — it inherits `this` from whatever scope the object literal itself was written in, which is almost never what's intended. The rule of thumb worth stating directly: use a regular function (or method shorthand) when `this` should depend on the call site, and an arrow function specifically when you want `this` to stay fixed to the surrounding context regardless of how the function gets invoked later.

**Example:**

```javascript
const obj = {
  value: 42,
  regularMethod() {
    console.log(this.value); // 42 — `this` is `obj`, since it was called as obj.regularMethod()
  },
  arrowMethod: () => {
    console.log(this.value); // undefined — `this` is whatever enclosing scope defined it, not `obj`
  },
  delayedRegular() {
    setTimeout(function () { console.log(this.value); }, 0);   // undefined — plain function, `this` lost
  },
  delayedArrow() {
    setTimeout(() => { console.log(this.value); }, 0);          // 42 — arrow captures `this` from delayedArrow
  },
};
```

**Follow-up questions:**

- *"Can you change an arrow function's `this` with `.call()` or `.bind()`?"* — No — arrow functions ignore the first argument to `call`/`apply`/`bind` entirely, since they have no `this` binding of their own to override.
- *"Why does `delayedRegular` above lose `this`?"* — The plain function passed to `setTimeout` is invoked as a bare function call by the timer, not as a method on `obj`, so its dynamic `this` resolves to `undefined` (strict mode) rather than `obj`.

**Sources:** [MDN — `this`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this), [MDN — Arrow function expressions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions)

---

## Intermediate

### 7. What Is a Closure, and What Is It Actually Used For?

**Core answer:**

"A closure is a function bundled together with references to the variables from its enclosing scope, such that the function keeps access to those variables even after the outer function that created them has already returned. In JavaScript this happens automatically, every time — any function defined inside another function closes over its parent's variables by default, not as an opt-in feature. The practical uses are genuinely common: private state (a counter whose internal value can't be touched except through the functions returned alongside it), function factories (a function that returns a customized function, like `makeMultiplier(3)` returning a function that always multiplies by 3), and memoization or caching, where a closure holds onto a cache object across calls."

**Staff-level extension:**

The precise mechanism worth being able to explain, not just the definition: a closure doesn't copy the outer variables at the time the inner function is created — it keeps a live reference to the actual variable binding, so if the outer variable changes after the closure is created, the closure sees the updated value, not a snapshot. This is exactly the mechanism behind the classic `var`-in-a-loop bug from the `let`/`var` question earlier in this guide: every closure created in that loop shares the same live `i` binding, so they all eventually see its final value, not the value at the time each closure was created.

**Example:**

```javascript
function makeCounter() {
  let count = 0; // private — inaccessible from outside except through the returned functions
  return {
    increment: () => ++count,
    getValue: () => count,
  };
}

const counter = makeCounter();
counter.increment();
counter.increment();
console.log(counter.getValue()); // 2
console.log(counter.count);      // undefined — genuinely private, not just a naming convention

function makeMultiplier(factor) {
  return (n) => n * factor; // closes over `factor`
}
const triple = makeMultiplier(3);
console.log(triple(7)); // 21
```

**Follow-up questions:**

- *"Does every function in JavaScript create a closure?"* — Every function that references a variable from an enclosing scope is a closure over that scope, even if it's never described that way explicitly — it's the language's default behavior, not a special case.
- *"What's a realistic case where closures cause a bug rather than a feature?"* — Holding a closure alive longer than intended keeps its entire enclosing scope alive too, even variables the closure never actually uses — covered in the memory-leak question later in this guide.

**Sources:** [MDN — Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures)

---

### 8. How Does the Event Loop Work, at a Basic Level?

**Core answer:**

"JavaScript runs on a single thread, so it can only execute one piece of code at a time — there's no true parallelism within one JS context. The event loop is the mechanism that makes asynchronous behavior possible anyway: synchronous code runs on the call stack immediately, while asynchronous work — a `setTimeout` callback, a network response, a DOM event — gets registered with the browser or Node's runtime and, once it's ready, gets placed into a queue rather than run immediately. The event loop's whole job is simple: continuously check whether the call stack is empty, and if it is, take the next callback off the queue and push it onto the stack to run. That's why a `setTimeout(fn, 0)` doesn't run immediately — it still has to wait for the current call stack to fully empty first, no matter how short the delay."

**Staff-level extension:**

The detail that separates a surface-level answer from a precise one: there isn't just one queue. The distinction between the microtask queue (Promises, `queueMicrotask`) and the macrotask/task queue (`setTimeout`, DOM events, I/O callbacks) — and the fact that the *entire* microtask queue drains completely before the event loop picks even one macrotask — is covered in depth in the next Staff-level question in this guide, since it's exactly the kind of ordering detail that separates knowing the event loop exists from being able to predict real output.

**Example:**

```javascript
console.log("1: synchronous");

setTimeout(() => console.log("3: macrotask, runs after sync code"), 0);

console.log("2: synchronous");

// Output order: 1, 2, 3 — the setTimeout callback can't run until the
// call stack is empty, even with a 0ms delay.
```

**Follow-up questions:**

- *"Is JavaScript single-threaded even with Web Workers?"* — Each Web Worker runs on its own genuinely separate thread with its own event loop and call stack; they communicate via message passing, not shared memory, so the single-threaded model still holds within any one context.
- *"Why doesn't a long synchronous loop let the event loop process anything?"* — Because the call stack is never empty while that loop runs — the event loop only ever picks up the next task once the stack empties, so a long synchronous block blocks all queued callbacks, including UI updates, for its entire duration.

**Sources:** [MDN — Concurrency model and the event loop](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model)

---

### 9. How Do Promises and `async`/`await` Relate to Each Other?

**Core answer:**

"A Promise represents a value that isn't available yet but will be, eventually — it's in one of three states: pending, fulfilled (with a value), or rejected (with a reason), and once it settles into fulfilled or rejected it stays that way permanently. `.then()`/`.catch()` are how you register callbacks to run once it settles. `async`/`await` is syntax built directly on top of Promises, not a separate mechanism — an `async` function always returns a Promise, and `await` inside it pauses that function's execution until the awaited Promise settles, then either returns the resolved value or throws the rejection as a catchable exception. It's genuinely just syntactic sugar: anything written with `await` can be rewritten with `.then()` chains, but `async`/`await` reads like synchronous code, which is exactly why it displaced `.then()` chains as the default style for anything beyond a single async step."

**Staff-level extension:**

The precise mechanical point worth stating: `await` doesn't block the thread — it suspends the `async` function's own execution and yields control back to the event loop, letting other code run while the awaited Promise is still pending, and resumes the function, via the microtask queue, once it settles. A common real mistake worth naming: awaiting Promises sequentially in a loop when they're actually independent (`for (const url of urls) { await fetch(url); }`) serializes work that could run concurrently — `Promise.all(urls.map(url => fetch(url)))` starts every request at once and is the fix when the requests genuinely don't depend on each other's results.

**Example:**

```javascript
// Equivalent behavior, two styles:
function getUserThen(id) {
  return fetchUser(id).then(user => fetchPosts(user.id)).then(posts => posts.length);
}

async function getUserAwait(id) {
  const user = await fetchUser(id);
  const posts = await fetchPosts(user.id);
  return posts.length;
}

// Sequential (slow) vs. concurrent (fast) when requests are independent:
async function sequential(ids) {
  const results = [];
  for (const id of ids) results.push(await fetchUser(id)); // waits for each before starting the next
  return results;
}

async function concurrent(ids) {
  return Promise.all(ids.map(id => fetchUser(id))); // all requests start immediately
}
```

**Follow-up questions:**

- *"How do you handle an error from an `await`ed call?"* — A regular `try`/`catch` around the `await` — a rejected Promise surfaces as a thrown exception at the `await` line, catchable exactly like a synchronous throw.
- *"What does `Promise.allSettled()` do differently from `Promise.all()`?"* — `Promise.all()` rejects immediately if any input Promise rejects; `Promise.allSettled()` always waits for every Promise and returns each one's outcome, fulfilled or rejected, without short-circuiting.

**Sources:** [MDN — Using Promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises), [MDN — `async function`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function), [MDN — `Promise.allSettled()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/allSettled)

---

### 10. How Does Prototypal Inheritance Work?

**Core answer:**

"Every JavaScript object has an internal link to another object, its prototype, and when you access a property that doesn't exist directly on the object, the engine automatically walks up that prototype link — the 'prototype chain' — checking each linked object in turn until it finds the property or reaches the end of the chain, `null`. This is fundamentally different from classical (class-based) inheritance: there's no blueprint being copied — objects delegate to other actual objects at lookup time. `class` syntax, introduced to make this more approachable, doesn't change the underlying mechanism at all — a `class` is syntactic sugar over exactly this same prototype-chain delegation; `class Dog extends Animal` just sets up `Dog.prototype`'s internal link to point at `Animal.prototype`, the same link you could wire up manually with `Object.create()` or `Object.setPrototypeOf()`."

**Staff-level extension:**

The thing worth stating precisely to show real understanding, not just familiarity with the `class` keyword: methods defined in a `class` body live on the prototype, shared by every instance, while properties assigned in the constructor (or as class fields) live on the instance itself — which is why `instance.hasOwnProperty('method')` is `false` but `instance.method()` still works, resolved via the prototype chain. This also explains a genuinely common performance/behavior distinction: adding a method to `Array.prototype` affects every array in the entire program, since they all share that one prototype object through the chain — which is exactly why extending built-in prototypes is broadly discouraged, despite technically working.

**Example:**

```javascript
function Animal(name) { this.name = name; }
Animal.prototype.speak = function () { return `${this.name} makes a sound.`; };

function Dog(name) { Animal.call(this, name); }
Dog.prototype = Object.create(Animal.prototype); // wire up the prototype chain manually
Dog.prototype.speak = function () { return `${this.name} barks.`; };

const rex = new Dog("Rex");
console.log(rex.speak());              // "Rex barks." — found directly on Dog.prototype
console.log(rex.hasOwnProperty("name")); // true — set in the constructor, lives on the instance
console.log(rex.hasOwnProperty("speak")); // false — lives on the prototype, found via the chain

// class syntax — identical mechanism underneath:
class AnimalClass {
  constructor(name) { this.name = name; }
  speak() { return `${this.name} makes a sound.`; }
}
class DogClass extends AnimalClass {
  speak() { return `${this.name} barks.`; }
}
```

**Follow-up questions:**

- *"What does `Object.create(null)` give you that a plain `{}` doesn't?"* — An object with no prototype at all — no inherited `toString`, `hasOwnProperty`, etc. — useful as a genuinely clean dictionary/map when inherited properties could collide with real data keys.
- *"Why is modifying a built-in prototype like `Array.prototype` risky?"* — It affects every array in the entire program, including ones from third-party libraries that may not expect the new property, and a future spec-added method with the same name would silently override yours.

**Sources:** [MDN — Inheritance and the prototype chain](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Inheritance_and_the_prototype_chain)

---

### 11. What Do `call()`, `apply()`, and `bind()` Actually Do?

**Core answer:**

"All three exist to explicitly control what `this` a function runs with, overriding whatever `this` the function's call site would otherwise produce. `call(thisArg, arg1, arg2, ...)` invokes the function immediately, with `this` set to `thisArg` and the remaining arguments passed individually. `apply(thisArg, [argsArray])` does exactly the same thing, except the arguments are passed as a single array instead of individually — useful when the argument list is already a collection you have, rather than something you'd type out by hand. `bind(thisArg, ...)` is different in kind from the other two: it doesn't invoke the function at all — it returns a brand-new function with `this` (and optionally some leading arguments) permanently locked to what you passed, ready to be called, or passed around and called later, with that binding guaranteed regardless of how it's eventually invoked."

**Staff-level extension:**

The precise distinction worth stating explicitly in a Staff-level answer: `call`/`apply` are for a one-off invocation with a borrowed `this` — a classic use is invoking `Array.prototype.slice.call(arrayLikeObject)` to convert an array-like object (like the old `arguments` object) into a real array — while `bind` is for producing a reusable, pre-configured function, commonly to preserve `this` for a callback that will be invoked later by something else (an event handler, a `setTimeout`), the same problem arrow functions solve lexically instead. Once a function's `this` has been `bind`-locked, calling `.call()` or `.apply()` on the resulting bound function to try to override `this` again has no effect — the binding, once set via `bind`, cannot be overridden a second time.

**Example:**

```javascript
function introduce(greeting) { return `${greeting}, I'm ${this.name}`; }
const person = { name: "Alex" };

introduce.call(person, "Hi");     // "Hi, I'm Alex" — args passed individually
introduce.apply(person, ["Hi"]);  // "Hi, I'm Alex" — args passed as an array

const boundIntroduce = introduce.bind(person);
boundIntroduce("Hello");          // "Hello, I'm Alex" — `this` locked, ready to call any time later

const other = { name: "Sam" };
boundIntroduce.call(other, "Hey"); // still "Hey, I'm Alex" — bind's `this` can't be overridden
```

**Follow-up questions:**

- *"What's the array-like-to-array conversion idiom, and is it still needed?"* — `Array.prototype.slice.call(arguments)` was the classic pre-ES2015 idiom; modern code uses `Array.from(arguments)` or, better, a rest parameter (`function f(...args)`) that's already a real array.
- *"Can you partially apply a function with `bind`?"* — Yes — arguments passed to `bind` after `thisArg` are prepended to every future call, so `add.bind(null, 5)` returns a function that always adds 5 to whatever's passed to it.

**Sources:** [MDN — `Function.prototype.call()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/call), [MDN — `Function.prototype.apply()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/apply), [MDN — `Function.prototype.bind()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/bind)

---

### 12. What Are `map()`, `filter()`, and `reduce()`, and Why Prefer Them Over a Loop?

**Core answer:**

"All three are `Array` methods that take a callback and iterate the array without mutating it, each producing a different shape of output. `map()` transforms every element and returns a new array of the same length — one output per input. `filter()` tests every element with a predicate and returns a new array containing only the elements that passed — potentially shorter, never longer. `reduce()` is the most general: it folds the entire array down into a single accumulated value, of whatever shape you want, by calling the callback with an accumulator and the current element on every step. All three are non-mutating: they read the original array and return a new array (or value), leaving the source untouched, which is exactly the property that makes them compose cleanly and makes reasoning about the code easier than tracking an index and a mutated array by hand."

**Staff-level extension:**

`reduce()` is worth understanding as the genuinely general-purpose tool underneath the other two — `map()` and `filter()` can each be implemented in terms of `reduce()`, since folding into an accumulator is expressive enough to build up any output shape, including another array. That said, reaching for `reduce()` when a simpler `map()` or `filter()` would express the same intent more directly is a real, common readability regression — the practical guidance is to use the most specific method that expresses what's actually happening, and reserve `reduce()` for genuinely aggregate operations (a sum, a grouped object, a single combined value) rather than using it as a universal hammer.

**Example:**

```javascript
const nums = [1, 2, 3, 4, 5];

const doubled = nums.map(n => n * 2);          // [2, 4, 6, 8, 10]
const evens = nums.filter(n => n % 2 === 0);   // [2, 4]
const sum = nums.reduce((acc, n) => acc + n, 0); // 15

// map() implemented via reduce(), to show reduce()'s generality:
const doubledViaReduce = nums.reduce((acc, n) => { acc.push(n * 2); return acc; }, []);

// A genuinely aggregate use reduce() is well-suited for, that map/filter can't express directly:
const grouped = nums.reduce((acc, n) => {
  const key = n % 2 === 0 ? "even" : "odd";
  (acc[key] ??= []).push(n);
  return acc;
}, {}); // { odd: [1, 3, 5], even: [2, 4] }
```

**Follow-up questions:**

- *"Do `map`/`filter`/`reduce` mutate the original array?"* — No — all three read the original and return a new array or value; the source array is untouched (though the callback itself could mutate elements if they're objects, which is a separate concern from the method itself).
- *"When would a plain `for` loop still be the better choice?"* — When you need to break out early (`map`/`filter`/`reduce` always run to completion) or when the performance-critical hot path genuinely benefits from avoiding the per-call callback overhead — both real but comparatively rare in typical application code.

**Sources:** [MDN — `Array.prototype.map()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map), [MDN — `Array.prototype.filter()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/filter), [MDN — `Array.prototype.reduce()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce)

---

## Staff Level

### 13. Within the Event Loop, What's the Difference Between a Microtask and a Macrotask?

**Core answer:**

"Both are queues of callbacks waiting for the call stack to be empty, but they're not treated equally. Macrotasks (also just called 'tasks') are things like `setTimeout`/`setInterval` callbacks, DOM events, and I/O callbacks — the event loop processes exactly one macrotask per pass through the loop. Microtasks are Promise callbacks (`.then`/`.catch`/`.finally`) and `queueMicrotask()` — and critically, the event loop drains the *entire* microtask queue, including any new microtasks that get added while draining it, before it's allowed to move on to the next macrotask or render anything to the screen. That's exactly why a Promise's `.then()` callback reliably runs before a `setTimeout(fn, 0)` callback, even though both were scheduled at essentially the same instant: microtasks always get fully flushed first, on every single pass through the loop, not just occasionally."

**Staff-level extension:**

This ordering is a genuine, common source of subtle bugs when code assumes `setTimeout(fn, 0)` and a resolved Promise's `.then()` are interchangeable ways to "defer to the next tick" — they are not interchangeable, since a chain of Promise callbacks that keeps scheduling more microtasks can starve macrotasks (including rendering) indefinitely, a real, documented pathological case. The practical mental model worth stating explicitly: after every single macrotask, the engine drains microtasks completely before doing anything else, including a rendering pass — which is also why a burst of synchronous-looking Promise chaining can visibly block the UI even though no individual operation looks like a long-running loop.

**Example:**

```javascript
console.log("1: sync");

setTimeout(() => console.log("4: macrotask"), 0);

Promise.resolve().then(() => console.log("3: microtask"));

console.log("2: sync");

// Output: 1, 2, 3, 4
// Synchronous code always runs first; the microtask (Promise .then) always
// runs before the next macrotask (setTimeout), no matter the declared delay.
```

**Follow-up questions:**

- *"Where does rendering fit relative to microtasks and macrotasks?"* — The browser generally renders between macrotasks, after the microtask queue has been fully drained — which is exactly why unbounded microtask chaining can visibly delay a frame from painting.
- *"What's a realistic bug this ordering causes?"* — Code that assumes a `setTimeout(fn, 0)` scheduled just after a `.then()` callback will run in the order they were written, when in fact all pending microtasks resolve first regardless of when the macrotask was scheduled.

**Sources:** [MDN — Microtasks](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide), [MDN — `queueMicrotask()`](https://developer.mozilla.org/en-US/docs/Web/API/Window/queueMicrotask)

---

### 14. How Do Closures Cause Memory Leaks in Long-Running Applications?

**Core answer:**

"A closure keeps its entire enclosing scope alive for as long as the closure itself is reachable — not just the specific variables it actually uses, but the whole scope object, in most engine implementations. If a closure that captures a large object is attached somewhere long-lived — a global event listener, a module-level cache, a timer that's never cleared — that large object can never be garbage collected, even if nothing else in the program still needs it, because the closure is still holding a live reference to it. In a single-page application specifically, the classic version of this bug is a component that adds an event listener or a `setInterval` in its setup and never removes it in cleanup — every time the component mounts again, another closure gets attached, each one keeping its own version of that component's data alive indefinitely, and the leak compounds every time the user navigates back to that view."

**Staff-level extension:**

The genuinely subtle version of this worth naming for a Staff-level answer: a closure that only uses one small variable from its enclosing scope can still, in some engine implementations, keep the *entire* enclosing scope's variables alive, not just the one it references, since the scope is captured as a whole. Detached DOM nodes are the other classic instance of the same underlying pattern — a JavaScript reference (often via a closure) held onto a DOM element that's since been removed from the document keeps that entire node, and everything it once referenced, from being collected, which is exactly why "detached DOM tree" is one of the most common leak categories a heap snapshot in browser DevTools surfaces in practice.

**Example:**

```javascript
function setupLeakyListener() {
  const hugeData = new Array(1_000_000).fill("leaked"); // large, should be temporary

  document.addEventListener("click", function handler() {
    console.log(hugeData.length); // closure keeps hugeData alive for as long as this listener exists
  });
  // If this listener is never removed, hugeData can never be garbage collected —
  // even long after whatever needed it is gone.
}

// The fix: keep a reference to the handler and remove it during cleanup
function setupCleanListener() {
  const hugeData = new Array(1_000_000).fill("temporary");
  function handler() { console.log(hugeData.length); }
  document.addEventListener("click", handler);
  return () => document.removeEventListener("click", handler); // caller invokes this on teardown
}
```

**Follow-up questions:**

- *"How would you actually find a leak like this in production?"* — Chrome DevTools' Memory panel: take two heap snapshots across a suspected leaking action repeated several times, and compare — objects whose count grows every repetition without ever dropping are the leak candidates.
- *"Why does a `setInterval` that's never cleared count as a leak even if its callback does nothing harmful?"* — The interval itself, plus its callback's entire closure scope, stays alive and keeps running for the life of the page, unless `clearInterval()` is called — a common source of the "many mount/unmount cycles, ever-growing memory" pattern in SPAs.

**Sources:** [MDN — Memory management](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Memory_management), [Chrome DevTools — Fix memory problems](https://developer.chrome.com/docs/devtools/memory-problems/)

---

### 15. What's the Difference Between Debounce and Throttle, and How Would You Implement Each?

**Core answer:**

"Both limit how often a function runs in response to a rapidly-firing event — a scroll handler, a resize listener, a search-input keystroke handler — but they trade off differently. Debounce delays execution until the event has stopped firing for a specified quiet period, resetting that timer on every new event — so a debounced search-suggestions handler only actually fires once the user pauses typing, not on every keystroke. Throttle instead guarantees the function runs at most once per specified time interval, regardless of how many events fire during that interval — so a throttled scroll handler updates a UI element at a steady, bounded rate throughout continuous scrolling, rather than waiting for scrolling to stop entirely. The practical choice: debounce for 'only care about the final state after activity settles' (search-as-you-type, form validation), throttle for 'need periodic updates throughout continuous activity' (scroll position, drag tracking)."

**Staff-level extension:**

A genuinely common implementation mistake worth naming: a debounce or throttle implementation that doesn't correctly preserve `this` and the original arguments when invoking the wrapped function breaks any code that relied on either — the fix is invoking the wrapped function via `.apply(this, args)` (or spreading arguments) inside the returned wrapper, not just calling the original function with no arguments. It's also worth being able to state precisely that neither technique is free: debounce's delay means the UI update is deliberately deferred, which is the wrong trade-off for something that must feel instantaneous (a button's own visual press state, say), and throttle's periodic-but-not-immediate updates can still feel laggy if the interval is set too generously for the interaction it's gating.

**Example:**

```javascript
function debounce(fn, delay) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId); // cancel any pending call — resets the quiet-period timer
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

function throttle(fn, interval) {
  let lastCallTime = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastCallTime >= interval) {
      lastCallTime = now;
      fn.apply(this, args); // runs immediately, then blocks further calls until the interval elapses
    }
  };
}

const debouncedSearch = debounce((query) => console.log("searching:", query), 300);
const throttledScroll = throttle(() => console.log("scroll position updated"), 200);
```

**Follow-up questions:**

- *"What happens if `delay` in the debounce example above is set to 0?"* — It still defers to a macrotask via `setTimeout`, so it's not synchronous, but with no meaningful "quiet period" — effectively collapsing multiple synchronous calls in the same tick into one, rather than genuinely waiting for user activity to pause.
- *"Would you ever combine debounce and throttle for the same handler?"* — Yes — a search box that throttles for periodic 'still typing' feedback while also debouncing the actual expensive search request until typing stops is a real, common pattern, though it's genuinely more complexity than most cases need.

**Sources:** [MDN — `setTimeout()`](https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout), [MDN — Debouncing and throttling explained through examples (css-tricks, referenced widely as the canonical explanation)](https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout#throttling_and_debouncing)

---

### 16. What's the Difference Between CommonJS and ES Modules?

**Core answer:**

"CommonJS (`require()`/`module.exports`) is Node.js's original module system, and it's synchronous and dynamic: `require()` can be called conditionally, inside an `if` block or a function, and modules are resolved and loaded at the moment `require()` actually executes, not ahead of time. ES Modules (`import`/`export`), standardized as part of the language itself, are statically analyzable instead: `import` statements must appear at the top level of a file, can't be conditional, and the entire module graph is resolved before any module's code actually runs, which is exactly what enables 'tree shaking' — a bundler statically determining which exports are genuinely used and excluding the rest from the final bundle, something CommonJS's dynamic `require()` calls fundamentally can't support, since the bundler can't always know in advance which module will be requested."

**Staff-level extension:**

The practical interop detail worth knowing precisely, since it's a genuinely common source of confusing bugs: Node.js supports both systems, but they don't mix seamlessly — a CommonJS module `require()`-ing an ES Module gets back a Promise (since ESM loading is inherently asynchronous, even for a single file), not the module's exports directly, while an ES Module `import`-ing a CommonJS module generally gets the whole `module.exports` object as the default export, which can produce surprising results with named-export syntax if the CommonJS module wasn't authored with ESM interop in mind. Package.json's `"type": "module"` field (or a `.mjs`/`.cjs` extension) is how a project declares which system a given file uses, and getting this wrong is the single most common cause of "works locally, breaks in this other environment" module errors in real Node projects.

**Example:**

```javascript
// CommonJS — math.cjs
function add(a, b) { return a + b; }
module.exports = { add };
// Elsewhere:
const { add } = require("./math.cjs"); // synchronous, dynamic — can be called conditionally

// ES Modules — math.mjs
export function add(a, b) { return a + b; }
// Elsewhere:
import { add } from "./math.mjs"; // static, must be top-level, resolved ahead of execution

// Static analyzability is what enables tree shaking:
import { add } from "./math.mjs"; // a bundler can statically see ONLY `add` is used
// ...and exclude any other exports math.mjs defines from the final bundle.
```

**Follow-up questions:**

- *"Why can't `import` be used conditionally inside an `if` block the way `require()` can?"* — Because the ES Module spec requires the entire dependency graph to be statically resolvable before execution — that's precisely the property that enables tree shaking and static analysis; dynamic `import()` (a function, not the statement) exists as the deliberate escape hatch when conditional loading is genuinely needed, and it returns a Promise.
- *"What does top-level `await` require?"* — It's only valid inside an ES Module (not CommonJS), since ESM's module graph is already resolved asynchronously; using it pauses that module's own evaluation, and anything importing it, until the awaited Promise settles.

**Sources:** [Node.js Documentation — Modules: ECMAScript modules](https://nodejs.org/api/esm.html), [Node.js Documentation — Modules: CommonJS modules](https://nodejs.org/api/modules.html), [MDN — JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)

---

### 17. How Does V8's Garbage Collector Actually Work?

**Core answer:**

"V8 splits the heap by object age, on the observation — the 'generational hypothesis' — that most objects die young, so it's worth optimizing specifically for that case. New objects are allocated in a small 'young generation' (further split into a 'nursery' and an 'intermediate' space), collected frequently by a fast, parallel algorithm called Scavenger, since scanning a small region often is cheap. Objects that survive a couple of Scavenger cycles get promoted into the 'old generation,' a much larger space collected far less frequently, since scanning it is expensive, using a mark-and-sweep-and-compact algorithm (Major GC) that runs mostly concurrently and incrementally with the main thread specifically to avoid the long 'stop-the-world' pauses that would otherwise be visible as dropped frames or UI jank."

**Staff-level extension:**

The practical, application-facing consequence worth stating: an object that's short-lived is essentially free from a GC-pressure standpoint, since Scavenger handles the young generation cheaply and quickly, but an application pattern that accidentally keeps large numbers of objects alive just long enough to get promoted into the old generation — a subtle closure leak, or a cache with no eviction — creates real, comparatively expensive Major GC pressure over time, exactly the class of problem the memory-leak question earlier in this guide is describing from the application-code side rather than the engine-internals side. Worth naming that this is genuinely engine-specific, not part of the ECMAScript specification at all — the spec says nothing about how memory is managed, only about observable language semantics, so a different engine (JavaScriptCore in Safari, SpiderMonkey in Firefox) can and does implement different GC strategies while remaining fully spec-compliant.

**Example:**

```text
V8 heap, conceptually:

  Young Generation (small, collected often — Scavenger, a parallel/fast algorithm)
    - Most objects die here almost immediately — the common case, optimized for.
    - Survivors of a couple of collection cycles get PROMOTED to:

  Old Generation (large, collected rarely — Major GC, mark-sweep-compact)
    - Objects expected to live a long time; collection here is comparatively
      expensive, so V8 runs it incrementally/concurrently to avoid long,
      visible "stop the world" pauses on the main thread.
```

**Follow-up questions:**

- *"Is this generational GC behavior something the JavaScript spec requires?"* — No — the ECMAScript spec doesn't mandate any particular memory-management strategy at all, only the language's observable behavior; generational, incremental GC is a V8 implementation choice other spec-compliant engines aren't required to share.
- *"How would you actually observe old-generation GC pressure in a running application?"* — Chrome DevTools' Performance panel shows GC events on the main thread timeline; a pattern of frequent, longer "Major GC" entries correlating with UI jank is the practical signal, distinct from the much more frequent, cheap "Minor GC" (Scavenger) entries.

**Sources:** [V8 Blog — Trash talk: the Orinoco garbage collector](https://v8.dev/blog/trash-talk), [MDN — Memory management](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Memory_management)

---

### 18. How Would You Defend a Web Application Against XSS?

**Core answer:**

"Cross-Site Scripting (XSS) is an attack where an attacker gets their own JavaScript to execute in another user's browser, in the context of your site — most commonly by injecting a `<script>` tag or an event-handler attribute into content that later gets rendered as HTML without being escaped, letting the injected script read cookies, make authenticated requests, or manipulate the page as if it were the real site's own code. The core defense is output encoding: never insert untrusted user input directly into the DOM as raw HTML — use `textContent` rather than `innerHTML` when inserting plain text, and if HTML genuinely needs to be rendered from user input, sanitize it first with a dedicated library rather than a hand-rolled regex, since HTML/JS injection has enough edge cases that ad hoc escaping reliably misses some. Modern frameworks (React, Angular — covered in their own guides) escape interpolated content by default, which closes off the most common injection path automatically, but that protection has real, specific bypasses worth knowing precisely, not just trusting blindly."

**Staff-level extension:**

A Content Security Policy (CSP) response header is the layered, defense-in-depth complement to output encoding, not a substitute for it: a strict CSP (disallowing inline scripts, restricting script sources to an explicit allowlist) means that even if an XSS injection somehow gets past encoding, the browser itself refuses to execute the injected script, since it doesn't match the policy — a real, independent second line of defense. The specific framework bypasses worth naming precisely: React's `dangerouslySetInnerHTML` and Angular's `[innerHTML]` binding (or explicit `bypassSecurityTrustHtml()` calls) exist specifically to opt back *out* of the framework's default escaping, and using either on genuinely untrusted input reintroduces the exact vulnerability the framework was otherwise preventing — the name `dangerouslySetInnerHTML` is a deliberate, literal warning, not decoration.

**Example:**

```javascript
// VULNERABLE — untrusted input inserted as raw HTML
const comment = getUserComment(); // e.g., "<img src=x onerror=alert('XSS')>"
element.innerHTML = comment; // the onerror handler executes immediately

// SAFE — inserted as plain text, never parsed as HTML
element.textContent = comment; // renders literally as visible text, no execution

// If HTML rendering is genuinely required, sanitize with a real library first:
import DOMPurify from "dompurify";
element.innerHTML = DOMPurify.sanitize(comment); // strips dangerous tags/attributes, keeps safe HTML
```

```http
# A CSP header as a defense-in-depth layer, disallowing inline scripts:
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.example.com
```

**Follow-up questions:**

- *"What's the difference between stored, reflected, and DOM-based XSS?"* — Stored: the malicious payload is saved server-side (a comment, a profile field) and served to every subsequent viewer. Reflected: the payload comes from the current request itself (a query parameter echoed back into the page) and only affects whoever clicks the crafted link. DOM-based: the vulnerability is entirely client-side — untrusted data flows into a dangerous DOM sink via client-side JavaScript, with no server involvement in the injection step at all.
- *"Does using React or Angular mean you don't need to think about XSS at all?"* — No — both escape interpolated content by default, which closes the most common path, but `dangerouslySetInnerHTML`/`[innerHTML]` bindings, URL/attribute injection in specific contexts, and third-party dependencies rendering unsanitized content are all real, framework-independent ways XSS still gets through.

**Sources:** [OWASP — Cross Site Scripting (XSS)](https://owasp.org/www-community/attacks/xss/), [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html), [MDN — Content-Security-Policy header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy)

---

### 19. Why Does Event Delegation Improve Performance, and When Would You Reach for It?

**Core answer:**

"Event delegation means attaching a single event listener to a common ancestor element instead of attaching a separate listener to every individual child element, relying on event bubbling — the fact that most DOM events fire on the target element and then propagate upward through each of its ancestors — to let that one listener handle events from any current or future child, since the event handler can inspect `event.target` to determine which specific child actually triggered it. This matters for performance directly when there are many similar children (a list with thousands of rows, each needing a click handler) — one listener instead of thousands is cheaper to set up and consumes less memory — but the more common, practical reason to reach for it is correctness with dynamic content: children added to the DOM after the initial listeners were attached automatically work with a delegated listener on their parent, with zero extra wiring, while individually-attached listeners would need to be re-attached to every newly-added element by hand."

**Staff-level extension:**

The precise mechanical detail worth being able to state: delegation relies specifically on the bubbling phase of the DOM event model, so it doesn't work at all for the handful of events that don't bubble by default (`focus`, `blur`, and a few others) unless the code explicitly uses the capturing phase or listens for a bubbling equivalent (`focusin`/`focusout` bubble, while `focus`/`blur` don't) — a real, specific gotcha worth knowing rather than assuming delegation is universally applicable to any event type. Framework code (React's synthetic event system, in particular) already implements a form of delegation internally, attaching a small number of listeners at the root and dispatching synthetically from there — which is worth mentioning as evidence this isn't just a vanilla-JS micro-optimization, it's a pattern serious frameworks build in as a foundational design choice.

**Example:**

```javascript
// WITHOUT delegation — one listener per row, and new rows need new listeners manually attached
document.querySelectorAll(".list-item").forEach(item => {
  item.addEventListener("click", () => console.log("clicked:", item.textContent));
});

// WITH delegation — ONE listener on the parent, works for current AND future children
document.querySelector(".list").addEventListener("click", (event) => {
  const item = event.target.closest(".list-item"); // find the actual clicked row, if any
  if (item) console.log("clicked:", item.textContent);
});
// Adding a new .list-item to .list later requires NO additional listener setup at all.
```

**Follow-up questions:**

- *"Why doesn't delegation work for a `focus` event handler without extra care?"* — `focus` and `blur` don't bubble by default; `focusin`/`focusout` are the bubbling equivalents specifically designed to support delegation for that category of event.
- *"What's `event.target` versus `event.currentTarget` in a delegated handler?"* — `event.target` is the actual element the event originated on (the specific child clicked); `event.currentTarget` is the element the listener is attached to (the parent) — delegation depends on reading `event.target`, since `event.currentTarget` is always just the parent regardless of which child was clicked.

**Sources:** [MDN — Event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling), [MDN — `Element: closest()`](https://developer.mozilla.org/en-US/docs/Web/API/Element/closest)

---

### 20. How Would You Implement a Simplified Version of `Promise.all()`?

**Core answer:**

"`Promise.all()` takes an array of Promises and returns a single Promise that resolves with an array of all their resolved values, in the same order as the input, once every input Promise has resolved — or rejects immediately, with that Promise's reason, the moment any single input Promise rejects, without waiting for the others. Implementing a simplified version tests whether you actually understand Promise mechanics rather than just calling the built-in: you need your own `new Promise()` wrapping the whole operation, a counter tracking how many of the input Promises have resolved so far, a results array pre-sized to preserve input order regardless of which Promise happens to settle first, and a rejection path that immediately calls the outer Promise's `reject` the moment any input rejects, short-circuiting the rest."

**Staff-level extension:**

The detail that's easy to get wrong and worth calling out explicitly while implementing this live: results must be written into the pre-allocated results array by *index*, not pushed in resolution order, since Promises can resolve in a different order than they appear in the input array — a genuinely common bug in a naive first attempt is treating "the third resolution to happen" as "goes at index 2," which silently scrambles the output order whenever the Promises don't happen to resolve in their original sequence. It's also worth handling the edge case of an empty input array explicitly (should resolve immediately with `[]`, never hang waiting for zero completions) and non-Promise values in the input array (`Promise.all()` treats them as already-resolved values, via an implicit `Promise.resolve()` wrap) — both are easy to miss and are exactly the kind of edge case a Staff-level interviewer will probe for after the happy path works.

**Example:**

```javascript
function myPromiseAll(promises) {
  return new Promise((resolve, reject) => {
    const results = new Array(promises.length); // pre-sized to preserve input ORDER
    let completedCount = 0;

    if (promises.length === 0) {
      resolve([]); // edge case: nothing to wait for
      return;
    }

    promises.forEach((maybePromise, index) => {
      Promise.resolve(maybePromise) // handles non-Promise values transparently, like the real API
        .then((value) => {
          results[index] = value; // write by INDEX, not push — resolution order isn't input order
          completedCount++;
          if (completedCount === promises.length) resolve(results);
        })
        .catch(reject); // short-circuits immediately on the FIRST rejection, like the real API
    });
  });
}

myPromiseAll([
  new Promise(res => setTimeout(() => res("slow"), 100)),
  Promise.resolve("fast"),
  42, // a plain value — treated as already resolved
]).then(console.log); // ["slow", "fast", 42] — original order preserved, despite different resolve times
```

**Follow-up questions:**

- *"How would `myPromiseAllSettled` differ from this implementation?"* — Instead of calling `reject` on the first failure, it would catch each rejection individually, record `{ status: "rejected", reason }` (or `{ status: "fulfilled", value }`) at that index, and always resolve once every Promise has settled one way or the other — never short-circuiting.
- *"What would you change to implement `Promise.race()` instead?"* — Drop the results array and completion counter entirely — just call the outer `resolve`/`reject` directly from the first Promise (success or failure) to settle at all, and let the rest resolve or reject with no effect, since the outer Promise is already settled by then.

**Sources:** [MDN — `Promise.all()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all), [MDN — `Promise.allSettled()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/allSettled), [MDN — `Promise.race()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/race)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| MDN — `let` | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let |
| MDN — `var` | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/var |
| MDN — `const` | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/const |
| MDN — Hoisting | https://developer.mozilla.org/en-US/docs/Glossary/Hoisting |
| MDN — Equality comparisons and sameness | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Equality_comparisons_and_sameness |
| MDN — JavaScript data types and data structures | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Data_structures |
| MDN — `structuredClone()` | https://developer.mozilla.org/en-US/docs/Web/API/Window/structuredClone |
| MDN — `undefined` | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/undefined |
| MDN — `null` | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/null |
| MDN — Nullish coalescing operator | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing |
| MDN — `this` | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this |
| MDN — Arrow function expressions | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions |
| MDN — Closures | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures |
| MDN — Concurrency model and the event loop | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model |
| MDN — Using Promises | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises |
| MDN — `async function` | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function |
| MDN — Inheritance and the prototype chain | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Inheritance_and_the_prototype_chain |
| MDN — `Function.prototype.bind()` | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/bind |
| MDN — `Array.prototype.reduce()` | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce |
| MDN — Microtasks | https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide |
| MDN — Memory management | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Memory_management |
| Chrome DevTools — Fix memory problems | https://developer.chrome.com/docs/devtools/memory-problems/ |
| Node.js Documentation — ECMAScript modules | https://nodejs.org/api/esm.html |
| Node.js Documentation — CommonJS modules | https://nodejs.org/api/modules.html |
| V8 Blog — Trash talk: the Orinoco garbage collector | https://v8.dev/blog/trash-talk |
| OWASP — Cross Site Scripting (XSS) | https://owasp.org/www-community/attacks/xss/ |
| OWASP XSS Prevention Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html |
| MDN — Event bubbling | https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling |
| MDN — `Promise.all()` | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all |
| TC39 — ECMA-262 Specification | https://tc39.es/ecma262/ |
