# Angular — Interview Prep (Basic → Staff, with Code & Sources)

> **Target level:** Basic → Staff (graduated — see below) · **Baseline:** Angular 22 (current stable, released 2026-06-03) — standalone components (default since v19), Signals (`signal()`/`computed()`/`effect()`, stable since v20), and zoneless change detection (stable since v20.2, default for new apps since v21) are all treated as the current recommended defaults; NgModule-based and RxJS/zone.js-based patterns are covered explicitly as the still-common, still-supported style most real production codebases are built on · **Last verified:** 2026-08-24 · **Prerequisites:** core JavaScript (see the [JavaScript guide](JavaScript_Interview_Prep.md)) for the Basic section; TypeScript familiarity helpful from the Intermediate section onward

How to use this: each question has a **Core answer** (100–180 words), a **Staff-level extension**, a concrete **Example**, **Follow-up questions**, and **Sources**. Angular has gone through several genuinely significant default-changing releases in a short span — standalone components, Signals, and zoneless change detection all shipped as the recommended path within the last two years — so this guide is explicit about what changed, when, and why the older pattern (NgModules, zone.js, RxJS-only state) still shows up constantly in real codebases and real interviews.

<!-- toc -->
## Table of Contents

- [Basic](#basic)
  - [1. What Is Angular, and How Does It Differ From AngularJS?](#1-what-is-angular-and-how-does-it-differ-from-angularjs)
  - [2. What Is a Component, and What Role Does a Template Play?](#2-what-is-a-component-and-what-role-does-a-template-play)
  - [3. What Are the Different Types of Data Binding in Angular?](#3-what-are-the-different-types-of-data-binding-in-angular)
  - [4. What's the Difference Between a Structural Directive and an Attribute Directive?](#4-whats-the-difference-between-a-structural-directive-and-an-attribute-directive)
  - [5. What Is Dependency Injection in Angular, and How Do You Provide a Service?](#5-what-is-dependency-injection-in-angular-and-how-do-you-provide-a-service)
  - [6. What Are Angular's Component Lifecycle Hooks?](#6-what-are-angulars-component-lifecycle-hooks)
- [Intermediate](#intermediate)
  - [7. What's the Difference Between a Standalone Component and an NgModule-Based Component?](#7-whats-the-difference-between-a-standalone-component-and-an-ngmodule-based-component)
  - [8. What Is an Observable, and How Does the `async` Pipe Use It?](#8-what-is-an-observable-and-how-does-the-async-pipe-use-it)
  - [9. What's the Difference Between Default and `OnPush` Change Detection?](#9-whats-the-difference-between-default-and-onpush-change-detection)
  - [10. What Are Signals, and How Do `signal()`, `computed()`, and `effect()` Work Together?](#10-what-are-signals-and-how-do-signal-computed-and-effect-work-together)
  - [11. What's the Difference Between Template-Driven and Reactive Forms?](#11-whats-the-difference-between-template-driven-and-reactive-forms)
  - [12. What Does `HttpClient` Provide, and How Do Interceptors Work?](#12-what-does-httpclient-provide-and-how-do-interceptors-work)
- [Staff Level](#staff-level)
  - [13. How Does Angular's Change Detection Actually Work, and What Does Zoneless Angular Change?](#13-how-does-angulars-change-detection-actually-work-and-what-does-zoneless-angular-change)
  - [14. Signals vs. RxJS — When Would You Use Each, and How Do They Interoperate?](#14-signals-vs-rxjs--when-would-you-use-each-and-how-do-they-interoperate)
  - [15. How Would You Optimize the Performance of a Large Angular Application?](#15-how-would-you-optimize-the-performance-of-a-large-angular-application)
  - [16. How Does Angular's Dependency Injection Hierarchy Work?](#16-how-does-angulars-dependency-injection-hierarchy-work)
  - [17. How Would You Approach State Management in a Large Angular Application?](#17-how-would-you-approach-state-management-in-a-large-angular-application)
  - [18. What Is Server-Side Rendering in Angular, and How Does Hydration Work?](#18-what-is-server-side-rendering-in-angular-and-how-does-hydration-work)
  - [19. How Do You Test an Angular Component?](#19-how-do-you-test-an-angular-component)
  - [20. What Are Signal-Based Inputs and Outputs, and How Do They Compare to `@Input()`/`@Output()`?](#20-what-are-signal-based-inputs-and-outputs-and-how-do-they-compare-to-inputoutput)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## Basic

### 1. What Is Angular, and How Does It Differ From AngularJS?

**Core answer:**

"Angular is a TypeScript-based framework for building web applications, maintained by Google, providing a full, opinionated toolkit out of the box — components, dependency injection, routing, forms, and an HTTP client — rather than requiring a team to assemble these from separate libraries. AngularJS (versions 1.x) was Angular's predecessor, an entirely different codebase built on JavaScript with two-way `$scope`-based data binding and no real concept of components as the primary building block; Angular (versions 2 and up) was a ground-up rewrite, not an upgrade path, built around components and TypeScript from the start. AngularJS reached end of life in January 2022 and receives no further updates, so any team still running it is maintaining genuinely unsupported software — a real, common consulting/migration scenario worth knowing exists."

**Staff-level extension:**

The naming is a real, common point of confusion worth clarifying directly: "Angular" (no "JS" suffix, versions 2+) and "AngularJS" (versions 1.x) are different frameworks that happen to share a name and a maintaining organization, not sequential versions of the same codebase — there is no automated upgrade path from one to the other, only a full rewrite or Google's own `@angular/upgrade` compatibility layer for incremental migration. Angular itself follows a predictable, deliberately fast release cadence — a new major version roughly every six months, each with 12 months of active support followed by 12 months of long-term support — which is worth knowing precisely, since it means "which Angular version" is a genuinely load-bearing question for any real codebase, not a formality.

**Example:**

```typescript
// Angular (2+) — component-based, TypeScript, standalone by default since v19
import { Component } from '@angular/core';

@Component({
  selector: 'app-hello',
  template: `<h1>Hello, {{ name }}!</h1>`,
})
export class HelloComponent {
  name = 'Angular';
}
```

**Follow-up questions:**

- *"If AngularJS reached end of life, why does it still come up in interviews?"* — A meaningful number of large, older enterprise codebases are still running it, unsupported, and "how would you plan a migration off AngularJS" is a real, common Staff-level scenario question.
- *"What does Angular's six-month major release cadence mean in practice for a team?"* — A given major version's active support window is genuinely short, so a team on an old major that's fallen out of both active and LTS support is running an unsupported version, similar in spirit to running an end-of-life AngularJS app, just with a shorter timeline.

**Sources:** [Angular — Overview](https://angular.dev/overview), [Angular — Version Compatibility and Releases](https://angular.dev/reference/releases)

---

### 2. What Is a Component, and What Role Does a Template Play?

**Core answer:**

"A component is Angular's fundamental building block — a TypeScript class decorated with `@Component`, pairing application logic with a view. The decorator's metadata specifies a `selector` (the custom HTML tag used to place the component), a `template` (or `templateUrl`, pointing at a separate HTML file), and optional styles. The template is HTML extended with Angular-specific syntax — interpolation (`{{ }}`), bindings, and control-flow blocks — that Angular compiles into actual DOM-manipulation instructions ahead of time; the template isn't interpreted at runtime the way a hand-written string might be, it's compiled, which is part of what makes Angular's rendering fast. As of Angular 19, components are standalone by default, meaning they declare their own dependencies (other components, directives, pipes) directly via an `imports` array, with no separate `NgModule` required to wire them together — the older NgModule-based approach still exists and still works, covered later in this guide."

**Staff-level extension:**

The precise mental model worth stating: a component's template isn't parsed as generic HTML string interpolation at runtime — Angular's compiler (`ngc`, via the Ivy rendering engine) processes the template ahead of time into JavaScript instructions that directly create and update DOM nodes, which is why Angular can catch many template errors (a typo'd property binding, a type mismatch) at build time rather than only at runtime, given a component's inputs are typed. This build-time compilation is also the mechanism that makes tree-shaking and dead-code elimination effective for standalone components specifically — since a component explicitly lists exactly what it imports, a bundler can determine unused dependencies far more precisely than it could reliably infer from an NgModule's more implicit dependency graph.

**Example:**

```typescript
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; // needed for @if/@for in older syntax; not required for the new control-flow blocks

@Component({
  selector: 'app-greeting',
  imports: [], // standalone — explicit dependencies, no NgModule needed
  template: `
    <h2>{{ title }}</h2>
    <p>Rendered by a standalone Angular component.</p>
  `,
})
export class GreetingComponent {
  title = 'Welcome';
}
```

**Follow-up questions:**

- *"What's the difference between `template` and `templateUrl`?"* — `template` is an inline string in the decorator, convenient for small components; `templateUrl` points at a separate `.html` file, the more common choice once a template grows beyond a few lines.
- *"Why does Angular compile templates ahead of time instead of interpreting them at runtime?"* — Ahead-of-time compilation catches template errors at build time, produces smaller and faster runtime code (no template parser shipped to the browser), and enables more effective tree-shaking.

**Sources:** [Angular — Anatomy of a Component](https://angular.dev/guide/components), [Angular — Component Selectors](https://angular.dev/guide/components/selectors)

---

### 3. What Are the Different Types of Data Binding in Angular?

**Core answer:**

"Angular has four binding types, each with distinct syntax. Interpolation (`{{ expression }}`) inserts a component property's value as text into the template — one-way, from the component to the view. Property binding (`[property]="expression"`) sets a DOM property or a component/directive input directly, also one-way, component to view, but for actual DOM properties or inputs rather than text content. Event binding (`(event)="handler()"`) listens for a DOM event or a component/directive output and runs a method in response — one-way in the opposite direction, view to component. Two-way binding (`[(ngModel)]="property"`) combines property and event binding into one syntax specifically for form inputs, keeping the component property and the input's displayed value in sync in both directions — under the hood it's genuinely just property binding plus event binding, written with a combined syntax as a convenience, not a fundamentally different mechanism."

**Staff-level extension:**

Worth being precise about, since it comes up directly: `[(ngModel)]` requires importing `FormsModule` (or, in a standalone component, adding it to the `imports` array) — it's not a core template feature Angular ships by default, unlike interpolation and plain property/event binding, which need no extra import at all. The two-way binding syntax itself, `[(x)]`, is also a general Angular convention, not exclusive to `ngModel` — any component can support it for its own custom property by defining a paired `x` input and an `xChange` output, which Angular's compiler recognizes and automatically expands into the combined `[(x)]` sugar.

**Example:**

```typescript
@Component({
  selector: 'app-binding-demo',
  imports: [FormsModule], // required for [(ngModel)] specifically
  template: `
    <p>{{ message }}</p>                          <!-- interpolation -->
    <img [src]="imageUrl">                         <!-- property binding -->
    <button (click)="onClick()">Click me</button>  <!-- event binding -->
    <input [(ngModel)]="name">                      <!-- two-way binding -->
    <p>Hello, {{ name }}</p>
  `,
})
export class BindingDemoComponent {
  message = 'Data binding demo';
  imageUrl = '/logo.png';
  name = '';
  onClick() { console.log('clicked'); }
}
```

**Follow-up questions:**

- *"Can you build your own custom two-way binding, the way `[(ngModel)]` works?"* — Yes — define an `input()` (or `@Input()`) named `x` and an `output()` (or `@Output()`) named exactly `xChange`; Angular's template compiler recognizes that pairing and allows `[(x)]` syntax automatically.
- *"Why does `[(ngModel)]` need `FormsModule` while `[src]` and `(click)` don't?"* — `[src]`/`(click)` bind to native DOM properties/events, which Angular's core template engine handles directly; `ngModel` is itself a directive shipped in `FormsModule`, an optional module, not part of the compiler's built-in template syntax.

**Sources:** [Angular — Property Binding](https://angular.dev/guide/templates/property-binding), [Angular — Event Binding](https://angular.dev/guide/templates/event-listeners), [Angular — Two-way Binding](https://angular.dev/guide/templates/two-way-binding)

---

### 4. What's the Difference Between a Structural Directive and an Attribute Directive?

**Core answer:**

"A structural directive changes the DOM's actual structure — adding, removing, or repeating entire elements — while an attribute directive changes the appearance or behavior of an element that's already there, without adding or removing anything from the DOM tree. Since Angular 17, the recommended way to express conditional rendering and loops is the built-in control-flow syntax — `@if`, `@for`, `@switch` — directly in the template, which replaced the older `*ngIf`/`*ngFor`/`*ngSwitch` structural directives as the default going forward, though the older syntax still works and appears constantly in existing codebases. `NgClass` and `NgStyle` are the classic examples of attribute directives — they change an existing element's classes or inline styles without touching how many elements exist in the DOM."

**Staff-level extension:**

The precise reason the new `@if`/`@for` control-flow syntax replaced `*ngIf`/`*ngFor` as the default is worth being able to state, not just that it exists: the new syntax is built directly into the template compiler rather than being implemented as directives at all, which removes the need to import `CommonModule` just for conditionals and loops in a standalone component, and it produces measurably better runtime performance, particularly for `@for`, which requires an explicit `track` expression (the new syntax's equivalent of `*ngFor`'s optional `trackBy`) — making list-identity tracking a required, not optional, part of writing a loop, which is a deliberate design choice to prevent a common, easy-to-miss performance mistake.

**Example:**

```html
<!-- New control-flow syntax (Angular 17+, the current recommended default) -->
@if (user) {
  <p>Welcome, {{ user.name }}</p>
} @else {
  <p>Please log in.</p>
}

@for (item of items; track item.id) {
  <li>{{ item.name }}</li>
} @empty {
  <li>No items.</li>
}

<!-- Older structural-directive syntax (*ngIf/*ngFor) — still valid, common in existing code -->
<p *ngIf="user; else loggedOut">Welcome, {{ user.name }}</p>
<ng-template #loggedOut><p>Please log in.</p></ng-template>
<li *ngFor="let item of items; trackBy: trackById">{{ item.name }}</li>

<!-- Attribute directive — changes an EXISTING element, doesn't add/remove from the DOM -->
<div [ngClass]="{ active: isActive, disabled: isDisabled }">Status indicator</div>
```

**Follow-up questions:**

- *"Why does `@for` require a `track` expression while `*ngFor`'s `trackBy` was optional?"* — Making it required forces every loop to have an explicit identity strategy, preventing the common performance mistake of Angular destroying and recreating every DOM node in a list on every change because it couldn't tell which items were actually the same across re-renders.
- *"Is `*ngIf`/`*ngFor` deprecated?"* — Not formally deprecated as of this guide's baseline — both syntaxes are supported, but `@if`/`@for` is the documented, recommended default for new code, and Angular provides an automated schematic to migrate an existing codebase from the old syntax to the new one.

**Sources:** [Angular — Control Flow](https://angular.dev/guide/templates/control-flow), [Angular — Attribute Directives](https://angular.dev/guide/directives/attribute-directives), [Angular — Structural Directives](https://angular.dev/guide/directives/structural-directives)

---

### 5. What Is Dependency Injection in Angular, and How Do You Provide a Service?

**Core answer:**

"Dependency Injection (DI) is a design pattern where a class declares what it needs — its dependencies — as constructor parameters (or, more recently, via the `inject()` function), rather than constructing those dependencies itself, and a framework-managed injector supplies the actual instances at runtime. Angular's DI system is built in and pervasive — services, and even components themselves, are typically requested this way rather than instantiated with `new`. A service is just a TypeScript class, conventionally decorated with `@Injectable()`; the most common way to make it available is `@Injectable({ providedIn: 'root' })`, which registers it as a singleton available application-wide without needing to list it in any component's or module's `providers` array explicitly — the injector creates it lazily, the first time something actually asks for it, and reuses that same instance for every subsequent request."

**Staff-level extension:**

The practical value DI provides, worth stating beyond the mechanism itself: a component that receives its dependencies via injection rather than constructing them directly can have those dependencies swapped out — most commonly for a test double in a unit test — without changing the component's own code at all, which is exactly the same "program to the interface, not the implementation" benefit other frameworks' DI systems provide. `inject()`, the newer function-based injection API, is now generally preferred over constructor-parameter injection for its own reasons: it works in contexts a constructor can't easily reach (a field initializer, a plain function used inside a component), and it reads more directly at the point of use, though constructor injection remains fully supported and extremely common in real code.

**Example:**

```typescript
import { Injectable, inject, Component } from '@angular/core';

@Injectable({ providedIn: 'root' }) // singleton, app-wide, created lazily on first use
export class LoggerService {
  log(message: string) { console.log(`[LOG]: ${message}`); }
}

// Constructor injection — the traditional style
@Component({ selector: 'app-a', template: '' })
export class ComponentA {
  constructor(private logger: LoggerService) {
    this.logger.log('ComponentA created');
  }
}

// inject() — the newer, function-based style, equivalent behavior
@Component({ selector: 'app-b', template: '' })
export class ComponentB {
  private logger = inject(LoggerService);
  constructor() { this.logger.log('ComponentB created'); }
}
```

**Follow-up questions:**

- *"What does `providedIn: 'root'` actually control?"* — Where the service is registered in Angular's injector hierarchy — `'root'` means the application-wide root injector, giving a single shared instance across the entire app, as opposed to registering it in a specific component's `providers` array for a narrower, per-component-subtree instance.
- *"Why might you choose `inject()` over constructor injection?"* — It works in places a constructor parameter can't (a class field initializer, a plain injectable function, a route guard written as a function), and it avoids long constructor parameter lists when a class has many dependencies.

**Sources:** [Angular — Dependency Injection in Angular](https://angular.dev/guide/di), [Angular — `inject()` function](https://angular.dev/guide/di/dependency-injection#injecting-services)

---

### 6. What Are Angular's Component Lifecycle Hooks?

**Core answer:**

"Lifecycle hooks are methods Angular calls automatically at specific points in a component's lifetime, letting code run exactly when something relevant happens rather than guessing at timing. `ngOnInit()` runs once, after Angular has set the component's initial inputs — the standard place to fetch initial data or set up state that depends on those inputs, rather than doing that work in the constructor, which runs before inputs are available. `ngOnChanges()` runs whenever an input property's value changes, receiving the previous and current values. `ngOnDestroy()` runs once, right before Angular removes the component, and is the standard place to clean up anything that would otherwise leak — unsubscribing from an Observable, clearing a timer, removing an event listener attached manually. Several other hooks exist for more specific timing (`ngAfterViewInit`, `ngAfterContentInit`, and their `Checked` counterparts), each tied to a specific point in change detection rather than the component's own creation or destruction."

**Staff-level extension:**

The precise reason `ngOnInit()` exists as a separate hook from the constructor, rather than just doing setup work in the constructor directly, is worth being able to state: a component's `@Input()`-bound properties are not yet set when the constructor runs — Angular creates the component instance first, then sets its inputs, then calls `ngOnInit()` — so any logic that depends on an input's actual value has to live in `ngOnInit()` or later, not the constructor, or it will silently operate on the input's default/undefined value instead of what was actually passed in. `ngOnDestroy()`'s cleanup role is not optional housekeeping — failing to unsubscribe from a long-lived Observable (an interval, a WebSocket stream, a store subscription) in `ngOnDestroy()` is one of the most common sources of memory leaks and duplicate-work bugs in real Angular applications, directly analogous to the closure/event-listener leak pattern covered in the JavaScript guide.

**Example:**

```typescript
import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { interval, Subscription } from 'rxjs';

@Component({ selector: 'app-timer', template: `<p>Tick: {{ tickCount }}</p>` })
export class TimerComponent implements OnInit, OnDestroy {
  @Input() intervalMs = 1000;
  tickCount = 0;
  private subscription?: Subscription;

  constructor() {
    // this.intervalMs is still the DEFAULT here (1000) — @Input() hasn't been set yet
  }

  ngOnInit() {
    // this.intervalMs now reflects whatever the parent actually bound to it
    this.subscription = interval(this.intervalMs).subscribe(() => this.tickCount++);
  }

  ngOnDestroy() {
    this.subscription?.unsubscribe(); // without this, the interval keeps running after the component is gone
  }
}
```

**Follow-up questions:**

- *"Why is `intervalMs` still 1000 inside the constructor above, even if a parent passes a different value?"* — Angular sets `@Input()`-bound properties after constructing the instance but before calling `ngOnInit()`, so the constructor always sees only the property's default value, never the actual bound input.
- *"What happens if you forget `ngOnDestroy()`'s unsubscribe in the example above?"* — The `interval` subscription keeps running indefinitely, even after the component is removed from the DOM, continuing to increment a `tickCount` nothing displays anymore and holding the component instance itself alive in memory since the subscription's callback still references `this`.

**Sources:** [Angular — Component Lifecycle](https://angular.dev/guide/components/lifecycle)

---

## Intermediate

### 7. What's the Difference Between a Standalone Component and an NgModule-Based Component?

**Core answer:**

"An NgModule-based component declares its dependencies indirectly: the component itself lists nothing, and a separate `@NgModule` class declares which components belong to it and which other modules (`CommonModule`, `FormsModule`, feature modules) it imports, making everything declared or imported in that module available to every component inside it. A standalone component, the default since Angular 19, declares its own dependencies directly, in its own `@Component` decorator's `imports` array — no `NgModule` required at all, for the component or for the application as a whole. Standalone was introduced as a genuinely separate opt-in feature in Angular 14, became the officially recommended default for new applications in Angular 17, and became the actual compiler default (so a component is standalone unless explicitly marked `standalone: false`) in Angular 19 — NgModules are not deprecated and continue to work, but new applications and new components should default to standalone unless there's a specific reason to use an NgModule."

**Staff-level extension:**

The practical reason standalone became the default, beyond simplicity, is worth stating precisely: an NgModule's `imports`/`declarations` create an implicit, module-wide dependency graph that a bundler has to reason about indirectly, while a standalone component's explicit, per-component `imports` array gives a bundler a direct, local list of exactly what that one component needs — which produces measurably better tree-shaking and makes lazy-loading a single component (rather than an entire feature module) straightforward, since there's no module boundary a component needs to be pulled out of. Migrating an existing NgModule-based codebase to standalone is not an all-or-nothing decision — Angular ships an official schematic (`ng generate @angular/core:standalone`) specifically to automate this incrementally, and standalone components can be used inside an NgModule-based application during a gradual migration, which is the realistic path for any codebase with real production history rather than a greenfield rewrite.

**Example:**

```typescript
// NgModule-based (the traditional style — still fully supported)
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({ selector: 'app-legacy', standalone: false, template: `<p *ngIf="show">Legacy</p>` })
export class LegacyComponent { show = true; }

@NgModule({
  declarations: [LegacyComponent],
  imports: [CommonModule], // needed here so LegacyComponent's *ngIf works
  exports: [LegacyComponent],
})
export class LegacyModule {}

// Standalone (the default since v19 — no NgModule involved at all)
@Component({
  selector: 'app-modern',
  imports: [], // @if is built into the compiler — no CommonModule import needed for it
  template: `@if (show) { <p>Modern</p> }`,
})
export class ModernComponent { show = true; }
```

**Follow-up questions:**

- *"Can a standalone component be used inside an NgModule-based application?"* — Yes — standalone components can be imported directly into an `NgModule`'s `imports` array, which is exactly what makes incremental migration practical rather than requiring a full rewrite.
- *"What's `bootstrapApplication()`, and how does it relate to standalone?"* — It's the standalone equivalent of the older `platformBrowserDynamic().bootstrapModule(AppModule)` call — it bootstraps an application directly from a root standalone component, with no root `AppModule` required at all.

**Sources:** [Angular — Standalone Components](https://angular.dev/guide/components/importing), [Angular — Roadmap](https://angular.dev/roadmap)

---

### 8. What Is an Observable, and How Does the `async` Pipe Use It?

**Core answer:**

"An Observable, from the RxJS library, represents a stream of values that can arrive over time — zero, one, or many — as opposed to a Promise, which represents exactly one eventual value. Angular uses Observables extensively in its own APIs: `HttpClient` returns an Observable per request, the `Router`'s events and route parameters are Observables, and reactive forms expose value changes as Observables. The `async` pipe (`| async`) is a template feature that subscribes to an Observable (or a Promise) directly in the template, automatically unwraps its emitted value for display, and — critically — automatically unsubscribes when the component is destroyed, which is exactly the manual cleanup work the lifecycle-hooks question earlier in this guide showed being done by hand in `ngOnDestroy()`. That automatic cleanup is the main reason the `async` pipe is the generally recommended way to display Observable data in a template, over manually subscribing in the component class."

**Staff-level extension:**

The precise trade-off worth naming: manually subscribing in the component class (typically in `ngOnInit()`) gives you a plain, already-unwrapped value to use anywhere in the component's logic, not just the template, but it makes you personally responsible for unsubscribing in `ngOnDestroy()` — miss that, and it's the exact `ngOnDestroy()`-cleanup leak pattern covered earlier in this guide. The `async` pipe avoids that responsibility entirely for anything only needed in the template, but each `| async` usage on the *same* Observable in a template creates its *own* separate subscription by default, which can trigger duplicate underlying work (a duplicate HTTP request, for instance) unless the Observable is explicitly shared — the fix is either assigning the piped result to a local template variable with `@if (data$ | async; as data)` and reusing that variable, or applying an RxJS `shareReplay()` operator to the source Observable itself.

**Example:**

```typescript
@Component({
  selector: 'app-user-profile',
  template: `
    @if (user$ | async; as user) {
      <p>{{ user.name }}</p>
      <p>{{ user.email }}</p>  <!-- reuses the SAME subscription via the "as user" alias -->
    } @else {
      <p>Loading...</p>
    }
  `,
})
export class UserProfileComponent {
  user$ = this.http.get<User>('/api/user'); // an Observable, not yet subscribed to
  constructor(private http: HttpClient) {}
  // No ngOnInit() subscribe() call, and no ngOnDestroy() unsubscribe() call needed —
  // the async pipe handles both automatically.
}
```

**Follow-up questions:**

- *"What happens if you use `| async` twice on the same Observable without the `as` alias?"* — Two separate subscriptions get created, which for an HTTP-backed Observable means two separate HTTP requests — a real, easy-to-miss performance bug.
- *"Does the `async` pipe work with Signals directly?"* — No — Signals aren't Observables; interop goes through `toObservable()` (wrapping a signal as an Observable) or, more directly for template display, simply reading the signal's value in the template without any pipe at all, since Angular's change detection already reacts to signal reads.

**Sources:** [Angular — `AsyncPipe`](https://angular.dev/api/common/AsyncPipe), [RxJS — Observable](https://rxjs.dev/guide/observable)

---

### 9. What's the Difference Between Default and `OnPush` Change Detection?

**Core answer:**

"With the Default change-detection strategy, Angular checks every component in the tree on every change-detection cycle — triggered by essentially any async event it's aware of (a click, an HTTP response, a timer) — regardless of whether that component's data could plausibly have changed. `OnPush` narrows this: a component marked `OnPush` is only re-checked when one of its `@Input()`-bound (or signal-based `input()`) properties receives a genuinely new reference, an event originates from within it, an `Observable` it's subscribed to via the `async` pipe emits, or a Signal it reads changes — Angular skips it, and its entire subtree, otherwise. This is a safe, common optimization for most components, since their output usually only depends on their own inputs — but it has one sharp edge: 'a new reference' is checked by identity for objects and arrays, so mutating one in place (`user.name = 'new'`) rather than replacing it (`user = { ...user, name: 'new' }`) doesn't count as a change and won't trigger a re-check."

**Staff-level extension:**

That reference-identity requirement is exactly why `OnPush` pairs naturally with an immutable-update discipline — always replacing an object/array rather than mutating its contents in place — and it's also exactly why Signals fit `OnPush` so well without that discipline being manually enforced: a `signal()`'s own change-notification mechanism is built around exactly this "did the value actually change" question, so code using signals for state gets `OnPush`-compatible behavior by construction, without a developer having to remember the immutable-update rule at every mutation site the way plain object/array state under `OnPush` requires. This is part of why Angular's default change-detection strategy for newly generated applications, starting with signals and zoneless as the default path, is effectively `OnPush`-equivalent behavior everywhere, rather than `OnPush` being an opt-in optimization a team has to remember to apply component by component.

**Example:**

```typescript
@Component({
  selector: 'app-user-card',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<p>{{ user.name }}</p>`,
})
export class UserCardComponent {
  @Input() user!: { name: string };
}

// In the parent:
// updateUserBroken() {
//   this.user.name = 'New Name'; // MUTATION — same object reference — OnPush child won't re-render
// }
// updateUserCorrect() {
//   this.user = { ...this.user, name: 'New Name' }; // NEW reference — OnPush child DOES re-render
// }
```

**Follow-up questions:**

- *"Does `OnPush` skip change detection for the component's children too, or just itself?"* — The entire subtree rooted at that component is skipped when the component itself isn't re-checked, which is exactly why the performance benefit compounds — one `OnPush` component near the root of a large, mostly-static subtree can save checking that whole subtree.
- *"How do Signals avoid the immutable-update discipline `OnPush` normally requires for plain objects?"* — A signal's setter (`mySignal.set(...)`/`.update(...)`) is itself the change-notification mechanism — Angular knows exactly when a signal's value changed because the signal API is how that value is ever changed at all, unlike a plain object property, which can be mutated through any reference with no notification.

**Sources:** [Angular — Skipping Component Subtrees](https://angular.dev/best-practices/skipping-subtrees), [Angular — Change Detection](https://angular.dev/guide/change-detection)

---

### 10. What Are Signals, and How Do `signal()`, `computed()`, and `effect()` Work Together?

**Core answer:**

"A Signal is a reactive value container — `signal(initialValue)` creates one, `.set(newValue)` or `.update(fn)` changes it, and reading it (calling it like a function, `mySignal()`) both returns the current value and, if read inside a reactive context like a template or another Signal, registers that context as a dependent that should be notified when the value changes. `computed(() => ...)` derives a new, read-only Signal from one or more other Signals — it recalculates automatically, and only, when a Signal it actually reads inside its function changes, and its result is cached between those recalculations rather than rerun on every read. `effect(() => ...)` runs a side effect — logging, a manual DOM update, syncing to `localStorage` — automatically whenever a Signal it reads changes, similar in spirit to `computed()` but for side effects rather than producing a new reactive value. All three fundamental Signal primitives, along with signal-based `input()`, graduated from developer preview to stable in Angular v20."

**Staff-level extension:**

The precise mechanism that makes this genuinely different from a plain variable plus manual change-tracking, worth stating explicitly: Signals use automatic, fine-grained dependency tracking — a `computed()` or `effect()` doesn't need to be told which Signals it depends on; it discovers them automatically by observing which Signals actually get *read* during its own function's execution, and only re-runs when one of those specific dependencies changes, not on some broader "anything changed" trigger. This is exactly what makes Signals compatible with `OnPush`-equivalent change detection everywhere without manual immutability discipline, and it's also why `effect()` should be reached for sparingly and specifically for genuine side effects — using `effect()` to derive a new piece of state from existing Signals, rather than `computed()`, is a common misuse that reintroduces manual, imperative state-syncing exactly where the reactive model was supposed to eliminate it.

**Example:**

```typescript
import { signal, computed, effect } from '@angular/core';

const count = signal(0);
const doubled = computed(() => count() * 2); // recalculates ONLY when count() changes, cached otherwise

effect(() => {
  console.log(`count is now ${count()}, doubled is ${doubled()}`); // re-runs automatically when either changes
});

count.set(5);          // logs: "count is now 5, doubled is 10" — effect re-ran automatically
count.update(n => n + 1); // logs: "count is now 6, doubled is 12"
```

**Follow-up questions:**

- *"Why is using `effect()` to derive state, instead of `computed()`, discouraged?"* — It reintroduces manual, imperative synchronization (setting one signal in response to another changing) exactly where `computed()` already provides automatic, cached, pure derivation — `effect()` is meant for genuine side effects outside the reactive graph, not for producing new reactive values.
- *"Do Signals replace `@Input()`?"* — Not exactly — Angular added signal-based `input()` as a distinct, stable-since-v19 API alongside decorator-based `@Input()`, covered later in this guide, letting a component's inputs themselves be Signals rather than plain properties.

**Sources:** [Angular — Signals](https://angular.dev/guide/signals), [Angular — Roadmap](https://angular.dev/roadmap)

---

### 11. What's the Difference Between Template-Driven and Reactive Forms?

**Core answer:**

"Template-driven forms build the form's structure and validation mostly in the template, using directives like `ngModel` and `ngForm`, with Angular inferring a form model behind the scenes automatically — this reads simply for small forms but pushes logic into the template, where it's harder to unit test directly. Reactive forms build the form model explicitly in the component class instead, using `FormGroup`, `FormControl`, and `FormArray`, with the template binding to that already-constructed model via `formGroup`/`formControlName` — this is more verbose for a trivial form but keeps all validation logic, dynamic field behavior, and the form's actual shape in TypeScript, where it's directly unit-testable and far more manageable as a form's complexity grows (conditional fields, cross-field validation, dynamically added rows)."

**Staff-level extension:**

The practical decision rule worth stating directly: reactive forms are the generally recommended default for anything beyond a genuinely trivial form, specifically because the form model living in the component class, as plain TypeScript objects, makes it directly testable without rendering the template at all, and makes complex validation logic (a validator that depends on two fields' combined state, a dynamically-added set of fields) tractable in a way that's awkward to express through template directives alone. Template-driven forms still have a real, legitimate niche — simple forms where minimizing component-class boilerplate matters more than testability or complex validation — but a Staff-level answer should be able to state precisely *why* reactive forms scale better, not just that they're "the modern one."

**Example:**

```typescript
// Reactive forms — model built explicitly in the class
import { FormGroup, FormControl, Validators, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-signup',
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="signupForm" (ngSubmit)="onSubmit()">
      <input formControlName="email">
      <button [disabled]="signupForm.invalid">Sign up</button>
    </form>
  `,
})
export class SignupComponent {
  signupForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
  });
  onSubmit() { console.log(this.signupForm.value); } // { email: "..." } — a plain, testable object
}
```

**Follow-up questions:**

- *"Why are reactive forms considered easier to unit test?"* — The form's model is a plain `FormGroup`/`FormControl` object constructed directly in the component class, so a test can create it, set values, and assert on validity/state without rendering any template at all.
- *"Can you mix reactive and template-driven forms in the same application?"* — Technically yes, but not recommended within the *same form* — the two approaches use different underlying mechanisms for tracking form state, and mixing them for one form leads to genuinely confusing, hard-to-debug state synchronization issues.

**Sources:** [Angular — Reactive Forms](https://angular.dev/guide/forms/reactive-forms), [Angular — Building a Template-Driven Form](https://angular.dev/guide/forms/template-driven-forms)

---

### 12. What Does `HttpClient` Provide, and How Do Interceptors Work?

**Core answer:**

"`HttpClient` is Angular's built-in service for making HTTP requests, returning an Observable per request rather than a Promise, so requests integrate naturally with the rest of Angular's RxJS-based APIs — cancellable via unsubscription, composable with RxJS operators for retry logic, debouncing, or combining multiple requests. An interceptor is a function (or, in the older API, a class implementing `HttpInterceptor`) that sits in the middle of every outgoing request and incoming response, letting you apply cross-cutting behavior in exactly one place instead of repeating it at every individual call site — attaching an auth token to every request's headers, logging every request/response, centrally catching and transforming error responses, or retrying a failed request automatically. Interceptors are registered once, application-wide (or per-injector, for more targeted scoping), and then apply transparently to every request made through `HttpClient` from that point on."

**Staff-level extension:**

The version-scoped detail worth being precise about: Angular introduced a functional interceptor API (`HttpInterceptorFn`, a plain function rather than an injectable class) alongside the class-based `HttpInterceptor` interface, and the functional style is now the generally recommended default, registered via `provideHttpClient(withInterceptors([...]))` rather than the older `HTTP_INTERCEPTORS` multi-provider token — both styles are still supported, but new code should default to the functional API for the same reason standalone components are now the default: less boilerplate, and no class/DI ceremony required just to intercept a request. A subtle but real interceptor-ordering detail worth knowing: interceptors run in the order they're provided for the outgoing request, and in *reverse* order for the incoming response — the first interceptor to touch the request is the last to see the response, since each one wraps the next like layers of an onion.

**Example:**

```typescript
import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('token');
  const authReq = token
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;
  return next(authReq); // pass the (possibly modified) request to the next interceptor/the actual HTTP call
};

// Registration — application-wide, functional style
import { provideHttpClient, withInterceptors } from '@angular/common/http';

bootstrapApplication(AppComponent, {
  providers: [provideHttpClient(withInterceptors([authInterceptor]))],
});
```

**Follow-up questions:**

- *"Why does `HttpClient` return an Observable instead of a Promise?"* — An Observable can be cancelled by unsubscribing (a Promise can't be cancelled once created), and it composes naturally with RxJS operators for retry, timeout, and combining multiple requests — capabilities a raw Promise-based API doesn't provide without extra wrapping.
- *"What's the practical effect of interceptor ordering being reversed on the response path?"* — An auth interceptor added first sees the outgoing request first (attaching the token before anything else runs) but sees the incoming response last (after every other interceptor has already processed it) — worth accounting for if a later interceptor's error handling depends on headers an earlier one set.

**Sources:** [Angular — `HttpClient`](https://angular.dev/guide/http), [Angular — Intercepting Requests and Responses](https://angular.dev/guide/http/interceptors)

---

## Staff Level

### 13. How Does Angular's Change Detection Actually Work, and What Does Zoneless Angular Change?

**Core answer:**

"Historically, Angular relied on Zone.js, a library that monkey-patches essentially every async browser API — `setTimeout`, DOM event listeners, Promise callbacks, `fetch` — so that Angular can be notified any time any of them fires, and trigger a change-detection pass across the whole component tree in response, without the application code needing to explicitly tell Angular anything changed. This works, but it's a genuinely broad, somewhat blunt instrument: it patches globally, adds real overhead to every async operation in the app, and triggers a full tree walk on events that often have nothing to do with what actually changed. Zoneless Angular removes Zone.js entirely and instead relies on Signals' own precise, automatic dependency tracking (and explicit notifications from `markForCheck()`/`ChangeDetectorRef` for non-signal cases) to know exactly which components could plausibly need re-checking — reaching stable status in Angular 20.2 and becoming the default for newly generated applications in Angular 21."

**Staff-level extension:**

The precise trade-off worth naming: Zone.js's blunt "anything happened, check everything" model is *correct* by construction — it can't miss a change, since it's triggered by literally every async API — but it's imprecise and adds real per-operation overhead system-wide, even for code paths that have nothing to do with the UI. Zoneless Angular is precise and has essentially zero equivalent async-patching overhead, but it depends on the application actually using Signals (or other explicit change-notification mechanisms) correctly everywhere state changes — a zoneless app that still mutates plain object state without going through a Signal, an `OnPush`-compatible `@Input()` change, or an explicit `markForCheck()` call, genuinely won't re-render, since nothing tells Angular a check is needed. This is exactly why the zoneless migration path matters as much as the feature itself: it's not a drop-in performance toggle for an existing large Zone.js-based codebase, it requires that codebase's state updates to already be (or become) Signal-driven or otherwise explicit.

**Example:**

```typescript
// Zone.js-based (the historical default): Angular is notified automatically
// after ANY patched async API fires, and checks the WHOLE component tree.
setTimeout(() => { this.count++; }, 1000);
// Zone.js's monkey-patched setTimeout tells Angular "something happened, check everything" —
// this works even though `count` is a plain property, no signal involved.

// Zoneless (Angular 20.2+ stable, default for new apps since v21):
// no global patching at all — Angular only knows to re-check because
// a Signal's own setter is what's changing the value:
count = signal(0);
setTimeout(() => { this.count.update(n => n + 1); }, 1000);
// The signal.update() call itself is the notification mechanism — Zone.js
// isn't involved, and isn't even loaded into the bundle at all.
```

**Follow-up questions:**

- *"What happens if a zoneless application mutates a plain (non-signal) property?"* — Nothing automatically triggers a re-check — the change simply won't be reflected in the view until something else (an unrelated signal change, a manual `markForCheck()` call) happens to trigger one, which is a real, common source of "why isn't my UI updating" bugs during a zoneless migration.
- *"Is going zoneless purely a performance win, or does it change application behavior?"* — Both — it removes real per-operation overhead, but it also means change detection becomes precise rather than blanket, so any part of an application relying on Zone.js's "checks everything, always" behavior without an explicit Signal or notification mechanism needs to be identified and fixed as part of the migration, not just flipped on.

**Sources:** [Angular — Zoneless Change Detection](https://angular.dev/guide/experimental/zoneless), [Angular — Change Detection](https://angular.dev/guide/change-detection), [Angular — Roadmap](https://angular.dev/roadmap)

---

### 14. Signals vs. RxJS — When Would You Use Each, and How Do They Interoperate?

**Core answer:**

"Signals and RxJS Observables solve genuinely overlapping but distinct problems. A Signal represents a single, current value that changes over time — synchronous by nature, with automatic, fine-grained dependency tracking built in, and no concept of 'events' independent of value changes. An Observable represents a stream of events or values over time, which can be asynchronous, can represent zero-to-many discrete emissions rather than one current value, and comes with a large, composable operator library (`debounceTime`, `switchMap`, `retry`, `combineLatest`) for genuinely complex async event orchestration that Signals don't attempt to replace. The practical guidance: reach for Signals for component and application state — the current value of something, derived values, UI-driven reactivity — and reach for RxJS for complex asynchronous event streams and orchestration — debounced search input, WebSocket message streams, combining multiple async sources with specific timing/cancellation semantics."

**Staff-level extension:**

`toSignal()` and `toObservable()` are the official interop bridge, and knowing precisely what each direction gives you (and costs you) is a real Staff-level distinction: `toSignal(observable$)` converts an Observable into a Signal, subscribing automatically and unwrapping each emission into the Signal's current value, which is genuinely convenient for using `HttpClient`'s Observable-returning APIs in template code without an `async` pipe — but it collapses the stream down to "the current value," discarding the ability to see or react to distinct emissions as events, the way an Observable naturally does. `toObservable(signal)` goes the other way, emitting a new value on the Observable every time the Signal changes, which is useful specifically when a Signal's value needs to feed into an existing RxJS operator chain (debouncing a signal-driven search term before it hits an HTTP call, for instance) that has no direct Signal equivalent. Neither direction is "the modern replacement" for the other — the practical skill is recognizing which shape a given piece of state or logic actually has and reaching for the matching tool, rather than defaulting to one everywhere out of habit.

**Example:**

```typescript
import { signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { debounceTime, switchMap } from 'rxjs';

// Signal -> Observable, to use an RxJS operator (debounceTime) that has no Signal equivalent:
const searchTerm = signal('');
const searchTerm$ = toObservable(searchTerm);
const results$ = searchTerm$.pipe(
  debounceTime(300),
  switchMap(term => this.http.get<Result[]>(`/api/search?q=${term}`))
);

// Observable -> Signal, to use an Observable-returning API directly as a value in the template:
const results = toSignal(results$, { initialValue: [] as Result[] });
// results() can now be read directly in the template, no `| async` pipe needed
```

**Follow-up questions:**

- *"What does `toSignal()`'s `initialValue` option handle?"* — Since an Observable might not emit synchronously on subscription, `toSignal()` needs some value to return before the first real emission arrives — `initialValue` supplies that, avoiding an `undefined`-typed signal that would otherwise need null-checking everywhere it's read.
- *"Would you ever use both Signals and RxJS in the same feature?"* — Yes, routinely — a common real pattern is RxJS for the async orchestration (debounced search, request cancellation via `switchMap`) feeding its result into a Signal via `toSignal()`, so the rest of the component and its template interact with a plain, synchronous current value rather than the stream directly.

**Sources:** [Angular — RxJS Interop](https://angular.dev/ecosystem/rxjs-interop), [Angular — Signals](https://angular.dev/guide/signals)

---

### 15. How Would You Optimize the Performance of a Large Angular Application?

**Core answer:**

"I'd work through this in layers, starting with the cheapest, highest-leverage changes. First, change detection: `OnPush` (or, more comprehensively, a signals-and-zoneless-driven app where this is closer to automatic) so components aren't re-checked on every unrelated event across the app. Second, list rendering: every `@for` loop needs a correct `track` expression (or `*ngFor`'s `trackBy`) so Angular can tell which items are genuinely new, moved, or removed, rather than destroying and recreating the entire list's DOM on every change — a routinely underestimated cost in a large list. Third, route-level and component-level code splitting: lazy-loaded routes so a user's initial bundle only includes what the first screen needs, and Angular's `@defer` blocks (introduced alongside the new control-flow syntax) for deferring an expensive, below-the-fold, or conditionally-shown component's loading until it's actually needed, triggered by viewport visibility, interaction, or a timer."

**Staff-level extension:**

`@defer` is worth naming specifically as a genuinely newer, less commonly known tool than lazy-loaded routes, and it operates at a finer grain: where route-level lazy loading splits a bundle by page, `@defer` splits it by component, letting a heavy, rarely-immediately-needed piece of a single page (a comment section below the fold, a modal's contents, a chart library) ship in its own separate chunk loaded only when its trigger condition fires — `on viewport`, `on interaction`, `on idle`, `on timer(ms)`, or a combination. Beyond bundle size and change detection, the other genuinely high-leverage lever in a large real application is the DI/data-fetching pattern itself: duplicate, uncoordinated HTTP requests for the same resource across sibling components (each independently calling `HttpClient` for data another sibling already fetched) is a common, easy-to-miss source of real performance cost that no template-level optimization fixes — the fix is a shared service holding the request behind a `shareReplay()`'d Observable or a Signal-backed cache, not a per-component optimization at all.

**Example:**

```html
<!-- Component-level code splitting: this chunk loads only when it enters the viewport -->
@defer (on viewport) {
  <app-heavy-chart [data]="chartData"></app-heavy-chart>
} @placeholder {
  <div class="chart-placeholder">Chart loading...</div>
} @loading (minimum 200ms) {
  <app-spinner></app-spinner>
}
```

```typescript
// Route-level code splitting — this route's component and its dependencies
// are in a separate chunk, only fetched when the user actually navigates here
export const routes: Routes = [
  { path: 'reports', loadComponent: () => import('./reports/reports.component').then(m => m.ReportsComponent) },
];
```

**Follow-up questions:**

- *"What triggers does `@defer` support besides `on viewport`?"* — `on idle` (when the browser is idle), `on interaction` (a click/keydown on the placeholder), `on hover`, `on timer(ms)`, and `on immediate` (defer to the next macrotask, mainly to deprioritize below other work) — usable individually or combined with `;`.
- *"How would you diagnose which part of a slow Angular app is actually the bottleneck, rather than guessing?"* — Angular DevTools' Profiler records a change-detection timeline showing exactly which components were checked and how long each took per cycle — the practical starting point before applying any of the optimizations above speculatively.

**Sources:** [Angular — Deferred Loading with `@defer`](https://angular.dev/guide/defer), [Angular — Lazy-loading Feature Modules and Routes](https://angular.dev/guide/ngmodules/lazy-loading), [Angular — Skipping Component Subtrees](https://angular.dev/best-practices/skipping-subtrees)

---

### 16. How Does Angular's Dependency Injection Hierarchy Work?

**Core answer:**

"Angular's injectors form a tree that mirrors the component tree, plus a distinct 'environment injector' hierarchy above it — the root (application-wide) injector, then a platform injector above that, and individual component injectors below, each component potentially adding its own `providers`. When a class asks for a dependency, Angular walks *up* the injector tree starting from where the request originated, using the nearest provider it finds — which means a service registered in a specific component's `providers` array creates a separate instance scoped to that component and its children, shadowing (not replacing globally) whatever the same token resolves to further up the tree for anything outside that subtree. `providedIn: 'root'` is the common case — one singleton, the root injector, visible everywhere — but component-level `providers` is the deliberate tool for genuinely per-component-subtree state, most commonly one distinct instance per usage of a reusable component that needs its own isolated state rather than sharing the application-wide singleton."

**Staff-level extension:**

Injection tokens are the mechanism worth being able to explain precisely for anything that isn't a class — Angular's DI naturally resolves by class reference for services, but configuration values, primitives, or interfaces (which don't exist at runtime in TypeScript, so can't be used as an injection key) need an explicit `InjectionToken`, created once and used both when providing a value and when injecting it, giving DI-based configuration the same swappability (for testing, for environment-specific config) that class-based services get for free. The precise resolution rule worth stating exactly for a Staff-level answer: Angular doesn't search the *entire* tree and pick the "best" match — it walks up from the requesting injector and stops at the *first* injector that has a provider for that token, which is exactly why a component-level provider "hides" a `providedIn: 'root'` registration for that component and everything nested inside it, without needing to explicitly override or know about the root registration at all.

**Example:**

```typescript
import { InjectionToken, Component } from '@angular/core';

// A non-class value needs an InjectionToken, since there's no class reference to inject by
export const API_URL = new InjectionToken<string>('API_URL');

// Root-level: one shared instance/value for the whole app
@Injectable({ providedIn: 'root' })
export class CartService { items: string[] = []; }

// Component-level provider: a NEW, isolated CartService instance for just this component subtree
@Component({
  selector: 'app-product-widget',
  providers: [CartService], // shadows the root CartService for this component and its children
  template: `...`,
})
export class ProductWidgetComponent {
  constructor(private cart: CartService) {} // gets the LOCAL instance, not the app-wide singleton
}
```

**Follow-up questions:**

- *"Why can't you just use a plain interface as an injection token?"* — TypeScript interfaces are a compile-time-only construct — they don't exist in the compiled JavaScript, so there's nothing at runtime for Angular's injector to look up by; an `InjectionToken` is a real, runtime object that serves as the lookup key instead.
- *"What's a realistic reason to use a component-level provider instead of `providedIn: 'root'`?"* — A reusable widget component (a tabbed panel, a wizard) that needs its own independent piece of state per usage on the page — if the service were a root-level singleton, every instance of that widget on the same page would incorrectly share one state.

**Sources:** [Angular — Hierarchical Injectors](https://angular.dev/guide/di/hierarchical-dependency-injection), [Angular — Dependency Injection in Angular](https://angular.dev/guide/di)

---

### 17. How Would You Approach State Management in a Large Angular Application?

**Core answer:**

"I'd think about this in tiers rather than picking one universal tool. For state that's genuinely local to one component (a form's in-progress values, a toggle's open/closed state), a plain Signal on the component itself is enough — no shared store needed at all. For state shared across a feature but not the whole app (a shopping cart's contents, a wizard's multi-step progress), a Signal-based service — an injectable class holding `signal()`s and `computed()`s, provided at the appropriate level in the DI hierarchy — is generally sufficient and keeps the mental model simple: state lives in a service, components read and update it through injected methods. For genuinely large, cross-cutting application state with many features reading and writing the same data, with a real need for time-travel debugging, strict unidirectional data flow, and a large team needing a consistent, enforced pattern, NgRx (now with `signalStore`, its Signals-based API) remains the team-endorsed option for that specific scale of problem."

**Staff-level extension:**

The judgment worth demonstrating explicitly in a Staff-level answer is *not* reaching for the most powerful tool by default — NgRx's actual value (strict unidirectional flow, time-travel debugging, a single normalized source of truth, enforced patterns across a large team) comes with real, genuine overhead (boilerplate, a steeper learning curve, more indirection for a simple read/write) that isn't worth paying for a feature or app that a Signal-based service would handle perfectly well. The practical decision framework: default to component-local Signals, escalate to a Signal-based service the moment two or more components genuinely need to share the same state, and only reach for NgRx once the application has grown enough that "share state via one shared service" itself starts breaking down — many features touching overlapping data, a team large enough that an enforced, consistent state-update pattern is worth its overhead, or genuine cross-cutting concerns (undo/redo, state persistence, DevTools time-travel) that a hand-rolled service would have to reimplement anyway.

**Example:**

```typescript
// Tier 2: a Signal-based service — shared state, no framework needed
@Injectable({ providedIn: 'root' })
export class CartStore {
  private itemsSignal = signal<CartItem[]>([]);
  readonly items = this.itemsSignal.asReadonly(); // exposed read-only — consumers can't call .set() directly
  readonly total = computed(() =>
    this.itemsSignal().reduce((sum, item) => sum + item.price, 0)
  );

  addItem(item: CartItem) {
    this.itemsSignal.update(items => [...items, item]); // new array reference — OnPush/zoneless-friendly
  }
}

// Any component injecting CartStore reads `cart.items()` / `cart.total()` reactively,
// and calls `cart.addItem(...)` to mutate — no separate store library needed at this scale.
```

**Follow-up questions:**

- *"What does exposing `.asReadonly()` on a Signal actually protect against?"* — It prevents consumers outside the service from calling `.set()`/`.update()` directly on the exposed Signal, forcing all mutations to go through the service's own explicit methods (like `addItem` above) — a deliberate encapsulation boundary, not just a naming convention.
- *"What would specifically justify introducing NgRx over the Signal-service pattern shown here?"* — A concrete, current pain point the service pattern can't cleanly solve — genuinely tangled cross-feature state dependencies, a team-wide need for enforced update patterns, or a real requirement for time-travel debugging/state persistence — not "NgRx is the more standard/powerful choice" as a reason on its own.

**Sources:** [Angular — Signals](https://angular.dev/guide/signals), [NgRx — SignalStore](https://ngrx.io/guide/signals/signal-store)

---

### 18. What Is Server-Side Rendering in Angular, and How Does Hydration Work?

**Core answer:**

"Server-side rendering (SSR) means running the Angular application on the server for an initial request, producing fully-rendered HTML that's sent to the browser immediately, rather than sending an empty shell and waiting for JavaScript to download, parse, and render the page client-side. This improves perceived load time (the user sees real content immediately) and is often essential for SEO, since crawlers can index the actual rendered content without executing JavaScript. Angular's SSR support is built directly into the framework via `@angular/ssr` (the historical Angular Universal project is now integrated into core Angular tooling). Hydration is the step after the server-rendered HTML arrives in the browser: rather than discarding that HTML and re-rendering everything from scratch client-side — the older, wasteful approach — Angular's hydration mechanism reuses the existing DOM nodes the server already produced, attaching event listeners and reactivity to them in place, so the user-visible page never flickers or gets torn down and rebuilt."

**Staff-level extension:**

The precise distinction worth naming for a Staff-level answer: full (non-hydrated) SSR without hydration still has to destroy and recreate the entire DOM client-side to make the page interactive, which produces a visible flash/layout shift and does real, wasted rendering work, since the server already built correct DOM the client then throws away; hydration's whole value is skipping that destroy-and-rebuild step by matching the client-side render against the server's existing DOM node-by-node and attaching behavior to what's already there. A genuinely common hydration bug worth knowing about explicitly: a "hydration mismatch," where the server-rendered HTML and what the client would have rendered don't actually match — often caused by code that behaves differently in a server environment versus a browser (checking `window`/`document` directly instead of using Angular's platform-detection APIs, or rendering something time-dependent that produces a different value between the server's render time and the client's hydration time) — Angular detects and logs these mismatches, but the fix is application code, not a framework setting.

**Example:**

```typescript
// Enabling hydration — provided once at the application root
import { provideClientHydration } from '@angular/platform-browser';

bootstrapApplication(AppComponent, {
  providers: [provideClientHydration()],
});

// A common hydration-mismatch source: code that behaves differently server vs. client
@Component({ selector: 'app-clock', template: `<p>{{ now }}</p>` })
export class ClockComponent {
  // BROKEN under SSR+hydration: the server renders one timestamp,
  // the client hydrates against a DIFFERENT timestamp moments later — a mismatch.
  now = new Date().toLocaleTimeString();
}
```

**Follow-up questions:**

- *"Why does a hydration mismatch matter if the page still ends up working?"* — Angular has to discard and re-render the mismatched portion of the DOM client-side after all, losing exactly the flicker-free benefit hydration exists to provide for that section — it degrades gracefully, but it silently defeats the optimization for whatever part mismatched.
- *"What's the practical SEO argument for SSR, given modern crawlers can execute JavaScript?"* — Even crawlers that can execute JavaScript generally allocate a limited rendering budget and can time out or deprioritize a page that requires significant client-side work before content appears — server-rendered content removes that dependency entirely, a more robust guarantee than "the crawler probably renders it."

**Sources:** [Angular — Server-side and Hybrid Rendering](https://angular.dev/guide/ssr), [Angular — Hydration](https://angular.dev/guide/hydration)

---

### 19. How Do You Test an Angular Component?

**Core answer:**

"Angular's testing utilities center on `TestBed`, which configures a small, isolated Angular testing module — declaring the component under test, providing mock versions of its dependencies, and compiling it — specifically so a component can be instantiated and rendered in a test without needing the entire real application's DI graph. `TestBed.createComponent()` returns a `ComponentFixture`, which wraps the component instance (`fixture.componentInstance`) alongside its rendered DOM (`fixture.nativeElement` or `fixture.debugElement`), letting a test both drive the component's TypeScript API directly and assert on what actually rendered. `fixture.detectChanges()` has to be called explicitly to trigger Angular's change detection in a test — it doesn't happen automatically the way it does in a running application — which is a common early stumbling block: a test that sets a property and immediately asserts on the rendered DOM without calling `detectChanges()` first will see stale, pre-update content."

**Staff-level extension:**

The precise reason to mock dependencies rather than using their real implementations in a component unit test is the same reason covered in depth in the Testing guide's mock/stub/spy question — isolating the component under test from its dependencies' actual behavior and external calls, so the test is fast, deterministic, and actually pinpoints the component's own logic when it fails. Angular-specific testing utilities worth knowing precisely: `HttpClientTestingModule` (or the newer `provideHttpClientTesting()`) intercepts `HttpClient` calls in a test and lets you assert exactly what request was made and supply a controlled fake response, rather than hitting a real backend or hand-mocking `HttpClient` generically; and Angular CDK's Component Test Harnesses provide a stable, implementation-detail-independent API for interacting with a Material or custom component in tests, so a test doesn't break every time an internal template structure changes, only when the component's actual public behavior changes.

**Example:**

```typescript
import { TestBed } from '@angular/core/testing';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

describe('UserProfileComponent', () => {
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [UserProfileComponent], // standalone components import directly, no declarations array
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    httpTesting = TestBed.inject(HttpTestingController);
  });

  it('renders the fetched user name', () => {
    const fixture = TestBed.createComponent(UserProfileComponent);
    fixture.detectChanges(); // triggers ngOnInit and the initial render — required explicitly

    const req = httpTesting.expectOne('/api/user'); // asserts the exact request was made
    req.flush({ name: 'Alex', email: 'alex@example.com' }); // supplies a controlled fake response

    fixture.detectChanges(); // re-render now that the (fake) HTTP response has resolved
    expect(fixture.nativeElement.textContent).toContain('Alex');
  });
});
```

**Follow-up questions:**

- *"Why does `fixture.detectChanges()` need to be called explicitly instead of happening automatically?"* — A test needs deterministic control over exactly when rendering happens, to assert on a known, stable state rather than a state that might still be mid-update depending on timing — automatic change detection would make test assertions racy.
- *"What's the value of a Component Test Harness over querying the DOM directly with `fixture.nativeElement.querySelector(...)`?"* — A harness exposes the component's behavior through a stable API (`harness.click()`, `harness.getValue()`) that survives internal template/CSS-class refactors, while a raw DOM selector query breaks the moment an internal implementation detail (a class name, a nesting structure) changes, even if the component's actual behavior hasn't.

**Sources:** [Angular — Testing](https://angular.dev/guide/testing), [Angular — Component Test Harnesses Overview](https://material.angular.dev/cdk/test-harnesses/overview)

---

### 20. What Are Signal-Based Inputs and Outputs, and How Do They Compare to `@Input()`/`@Output()`?

**Core answer:**

"Signal-based `input()` and `output()`, stable since Angular 19, are functions used as class field initializers instead of the `@Input()`/`@Output()` decorators — `name = input<string>()` declares an input as a genuine, read-only Signal (read as `this.name()`), and `changed = output<string>()` declares an output whose `.emit(value)` method works the same as the decorator-based `@Output()`'s `EventEmitter`. The practical difference from decorator-based `@Input()`: a signal input is automatically read-only from inside the component and participates directly in Signal-based reactivity — a `computed()` that reads `this.name()` recalculates automatically when a new value arrives, with none of the manual `ngOnChanges()` handling the decorator-based approach would need to react to an input change. `input.required<T>()` additionally makes an input's requiredness a compile-time-checked property, rather than something enforced only by convention or a runtime check, which decorator-based `@Input()` has no equivalent for."

**Staff-level extension:**

The subtle behavioral difference worth knowing precisely for a Staff-level answer: decorator-based `@Input()` properties are, in principle, freely reassignable from inside the component itself (nothing stops `this.myInput = newValue` at the language level, even though doing so is bad practice, since it fights the "data flows down from the parent" model), while a signal-based `input()` is read-only from the component's own perspective by construction — there's no `.set()` method exposed on it, only the reading call syntax, which makes the "inputs are driven by the parent" contract enforced by the type system rather than convention. `model()` is the signal-based equivalent of a component supporting `[(x)]` two-way binding — it produces a Signal the component can both read and write internally, with writes automatically flowing back up to update the parent's bound property, replacing the older paired-`@Input()`-plus-`@Output()`-named-`xChange`-convention with one single, purpose-built primitive.

**Example:**

```typescript
import { Component, input, output, model, computed } from '@angular/core';

@Component({
  selector: 'app-quantity-picker',
  template: `
    <button (click)="decrement()">-</button>
    <span>{{ quantity() }}</span>
    <button (click)="increment()">+</button>
    <p>{{ label() }}: {{ total() }}</p>
  `,
})
export class QuantityPickerComponent {
  label = input.required<string>();          // signal-based required input — compile-time checked
  pricePerUnit = input<number>(1);            // signal-based input with a default value
  quantity = model(1);                        // two-way bindable — parent can [(quantity)]="parentValue"
  changed = output<number>();                 // signal-based output, same .emit() API as @Output()

  total = computed(() => this.quantity() * this.pricePerUnit()); // reacts automatically to either changing

  increment() { this.quantity.update(q => q + 1); this.changed.emit(this.quantity()); }
  decrement() { this.quantity.update(q => q - 1); this.changed.emit(this.quantity()); }
}
```

**Follow-up questions:**

- *"Can `@Input()` and signal-based `input()` be mixed within the same component?"* — Yes — they can coexist during a gradual migration, though a single given input should use one style or the other, not both, for that same property.
- *"What replaces `ngOnChanges()` for reacting to a signal-based input changing?"* — An `effect()` that reads the input signal, or, more idiomatically, a `computed()` deriving a new value directly from it — since the signal's own reactivity already provides exactly the "notify me when this changes" behavior `ngOnChanges()` existed to approximate for decorator-based inputs.

**Sources:** [Angular — Signal Inputs](https://angular.dev/guide/signals/inputs), [Angular — Model Inputs (Two-way Binding with Signals)](https://angular.dev/guide/signals/model), [Angular — Signals](https://angular.dev/guide/signals)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Angular — Overview | https://angular.dev/overview |
| Angular — Version Compatibility and Releases | https://angular.dev/reference/releases |
| Angular — Anatomy of a Component | https://angular.dev/guide/components |
| Angular — Component Selectors | https://angular.dev/guide/components/selectors |
| Angular — Property Binding | https://angular.dev/guide/templates/property-binding |
| Angular — Event Binding | https://angular.dev/guide/templates/event-listeners |
| Angular — Two-way Binding | https://angular.dev/guide/templates/two-way-binding |
| Angular — Control Flow | https://angular.dev/guide/templates/control-flow |
| Angular — Attribute Directives | https://angular.dev/guide/directives/attribute-directives |
| Angular — Structural Directives | https://angular.dev/guide/directives/structural-directives |
| Angular — Dependency Injection in Angular | https://angular.dev/guide/di |
| Angular — Hierarchical Injectors | https://angular.dev/guide/di/hierarchical-dependency-injection |
| Angular — Component Lifecycle | https://angular.dev/guide/components/lifecycle |
| Angular — Standalone Components | https://angular.dev/guide/components/importing |
| Angular — Roadmap | https://angular.dev/roadmap |
| Angular — `AsyncPipe` | https://angular.dev/api/common/AsyncPipe |
| RxJS — Observable | https://rxjs.dev/guide/observable |
| Angular — Skipping Component Subtrees | https://angular.dev/best-practices/skipping-subtrees |
| Angular — Change Detection | https://angular.dev/guide/change-detection |
| Angular — Signals | https://angular.dev/guide/signals |
| Angular — Signal Inputs | https://angular.dev/guide/signals/inputs |
| Angular — Model Inputs | https://angular.dev/guide/signals/model |
| Angular — Reactive Forms | https://angular.dev/guide/forms/reactive-forms |
| Angular — Template-Driven Forms | https://angular.dev/guide/forms/template-driven-forms |
| Angular — `HttpClient` | https://angular.dev/guide/http |
| Angular — Interceptors | https://angular.dev/guide/http/interceptors |
| Angular — Zoneless Change Detection | https://angular.dev/guide/experimental/zoneless |
| Angular — RxJS Interop | https://angular.dev/ecosystem/rxjs-interop |
| Angular — Deferred Loading with `@defer` | https://angular.dev/guide/defer |
| Angular — Lazy-loading Feature Modules and Routes | https://angular.dev/guide/ngmodules/lazy-loading |
| NgRx — SignalStore | https://ngrx.io/guide/signals/signal-store |
| Angular — Server-side and Hybrid Rendering | https://angular.dev/guide/ssr |
| Angular — Hydration | https://angular.dev/guide/hydration |
| Angular — Testing | https://angular.dev/guide/testing |
| Angular — Component Test Harnesses Overview | https://material.angular.dev/cdk/test-harnesses/overview |
