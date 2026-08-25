# React — Interview Prep (Basic → Staff, with Code & Sources)

> **Target level:** Basic → Staff (graduated — see below) · **Baseline:** React 19 (current stable, released 2024-12-05; latest minor 19.2, released 2025-10-01) — function components and Hooks are treated as the default (class components covered only where a follow-up explicitly asks about legacy code); React Compiler is documented as a separate, independently-versioned project (stable v1.0 since 2025-10-07) rather than a built-in part of React itself · **Last verified:** 2026-08-24 · **Prerequisites:** core JavaScript, especially closures and array methods (see the [JavaScript guide](JavaScript_Interview_Prep.md)); no prior React experience assumed for the Basic section

How to use this: each question has a **Core answer** (100–180 words), a **Staff-level extension**, a concrete **Example**, **Follow-up questions**, and **Sources**. React's own core model (components, one-way data flow, hooks) has been stable for years, but the surrounding recommended practice has shifted meaningfully — Server Components, Actions, and the React Compiler are all relatively recent and change what "idiomatic React" looks like — so this guide is explicit about what's core-React-the-library versus what depends on a specific meta-framework (Next.js, and similar) or the separately-versioned Compiler.

<!-- toc -->
## Table of Contents

- [Basic](#basic)
  - [1. What Is React, and What Problem Does the Virtual DOM Solve?](#1-what-is-react-and-what-problem-does-the-virtual-dom-solve)
  - [2. What Is JSX, and How Does It Become Actual DOM Elements?](#2-what-is-jsx-and-how-does-it-become-actual-dom-elements)
  - [3. What Is a Component, and How Do Props Flow Through One?](#3-what-is-a-component-and-how-do-props-flow-through-one)
  - [4. How Does the `useState` Hook Work?](#4-how-does-the-usestate-hook-work)
  - [5. What's the Difference Between a Controlled and an Uncontrolled Input?](#5-whats-the-difference-between-a-controlled-and-an-uncontrolled-input)
  - [6. Why Does React Need a `key` Prop When Rendering a List?](#6-why-does-react-need-a-key-prop-when-rendering-a-list)
- [Intermediate](#intermediate)
  - [7. How Does `useEffect` Work, and What Is the Cleanup Function For?](#7-how-does-useeffect-work-and-what-is-the-cleanup-function-for)
  - [8. What Problem Does the Context API Solve?](#8-what-problem-does-the-context-api-solve)
  - [9. What's the Difference Between `useMemo` and `useCallback`?](#9-whats-the-difference-between-usememo-and-usecallback)
  - [10. What Is a Custom Hook, and When Would You Write One?](#10-what-is-a-custom-hook-and-when-would-you-write-one)
  - [11. What Are Refs For, and How Do They Differ From State?](#11-what-are-refs-for-and-how-do-they-differ-from-state)
  - [12. What's the Difference Between Lifting State Up and Prop Drilling?](#12-whats-the-difference-between-lifting-state-up-and-prop-drilling)
- [Staff Level](#staff-level)
  - [13. How Does React's Reconciliation Algorithm Actually Work?](#13-how-does-reacts-reconciliation-algorithm-actually-work)
  - [14. What Is Concurrent Rendering, and How Do `useTransition` and `Suspense` Use It?](#14-what-is-concurrent-rendering-and-how-do-usetransition-and-suspense-use-it)
  - [15. What Does the React Compiler Do, and How Does It Relate to `useMemo`/`useCallback`?](#15-what-does-the-react-compiler-do-and-how-does-it-relate-to-usememousecallback)
  - [16. What Are Server Components, and How Do They Differ From Client Components?](#16-what-are-server-components-and-how-do-they-differ-from-client-components)
  - [17. What Are Actions and `useActionState`, and What Problem Do They Solve?](#17-what-are-actions-and-useactionstate-and-what-problem-do-they-solve)
  - [18. How Would You Optimize the Performance of a Large React Application?](#18-how-would-you-optimize-the-performance-of-a-large-react-application)
  - [19. How Would You Approach State Management in a Large React Application?](#19-how-would-you-approach-state-management-in-a-large-react-application)
  - [20. How Do You Test a React Component?](#20-how-do-you-test-a-react-component)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## Basic

### 1. What Is React, and What Problem Does the Virtual DOM Solve?

**Core answer:**

"React is a JavaScript library, maintained by Meta, for building user interfaces out of composable components — it's explicitly scoped as a UI library, not a full application framework, which is why routing, data fetching conventions, and server rendering are typically provided by a separate meta-framework built on top of React rather than React itself. The virtual DOM is a lightweight in-memory representation of what the UI should look like — a tree of plain JavaScript objects describing elements, not real DOM nodes. When state changes, React builds a new virtual-DOM tree, compares it against the previous one (a process called reconciliation), and computes the minimal set of actual DOM mutations needed to make the real DOM match — rather than a developer manually figuring out which specific DOM nodes to update, or React naively tearing down and rebuilding the whole real DOM on every change, both of which would be slower and far more error-prone to write by hand."

**Staff-level extension:**

The precise reason this matters beyond "it's faster" is worth being able to state directly: real DOM operations (creating nodes, reflowing layout, repainting) are comparatively expensive, while diffing two in-memory JavaScript object trees is comparatively cheap — so React's model lets application code be written declaratively ("here's what the UI should look like given this state") without the developer having to reason imperatively about exactly which DOM nodes to touch, while still avoiding the cost of naive full-tree DOM rebuilds. It's also worth being precise that the virtual DOM isn't free — it's a deliberate trade: some diffing overhead in exchange for a dramatically simpler programming model and avoiding worse-than-necessary real DOM churn — which is exactly why React's own newer direction (the React Compiler, covered later in this guide) focuses on reducing unnecessary re-renders and re-computation even further, rather than the virtual DOM being the final word on performance.

**Example:**

```jsx
function Counter() {
  const [count, setCount] = React.useState(0);
  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  );
}
// On each click, React builds a new virtual-DOM tree for this component,
// diffs it against the previous one, and updates only the button's text node —
// it does not recreate the <button> element itself.
```

**Follow-up questions:**

- *"Is React a framework or a library, and why does that distinction matter here?"* — React itself only handles the UI-component layer; routing, data fetching conventions, and SSR are provided by separate libraries or a meta-framework (like Next.js) built on top of it — a genuinely different scope than an all-in-one framework, which affects how a team assembles a full application's tooling.
- *"Does the virtual DOM mean React is always faster than directly manipulating the real DOM?"* — No — hand-optimized, targeted direct DOM manipulation for a narrow, known use case can outperform React's general-purpose diffing; the virtual DOM's value is making a broadly-fast, declarative default achievable without that manual optimization work for the vast majority of UI code.

**Sources:** [React — Describing the UI](https://react.dev/learn/describing-the-ui), [React — Render and Commit](https://react.dev/learn/render-and-commit)

---

### 2. What Is JSX, and How Does It Become Actual DOM Elements?

**Core answer:**

"JSX is a syntax extension to JavaScript that lets UI structure be written in an HTML-like syntax directly inside JavaScript code, rather than calling `React.createElement()` by hand for every element. JSX isn't valid JavaScript on its own — a build tool (Babel, or the compiler built into a bundler like Vite) transforms it at build time into plain `React.createElement()` calls (or, with the newer JSX transform, calls to functions imported automatically from `react/jsx-runtime`), which in turn produce plain JavaScript objects describing the desired UI — the virtual-DOM elements covered in the previous question, not real DOM nodes yet. Because JSX compiles down to regular function calls and plain objects, it can embed arbitrary JavaScript expressions inside curly braces (`{count}`, `{items.map(...)}`), which is exactly what makes conditional rendering and list rendering in JSX just ordinary JavaScript, not a separate templating mini-language with its own rules to learn."

**Staff-level extension:**

The precise mechanical detail worth being able to state: `<div className="box">{title}</div>` compiles to something equivalent to `React.createElement('div', { className: 'box' }, title)` (or, under the modern automatic JSX runtime, `jsx('div', { className: 'box', children: title })`) — and that call doesn't touch the real DOM at all, it just returns a plain JavaScript object (a React element) describing what should eventually be rendered. This is exactly why conditional rendering in JSX is written with plain JavaScript operators (`condition && <Component />`, a ternary) rather than a special directive syntax — since the content inside `{}` is genuinely just a JavaScript expression being evaluated, the same as it would be anywhere else in the language, with no separate template-expression grammar to learn.

**Example:**

```jsx
// JSX as written:
const element = <h1 className="greeting">Hello, {user.name}!</h1>;

// Roughly what it compiles to (automatic JSX runtime, React 17+):
import { jsx } from 'react/jsx-runtime';
const element = jsx('h1', { className: 'greeting', children: `Hello, ${user.name}!` });

// Conditional/list rendering is just plain JavaScript expressions inside {}:
function ItemList({ items, showEmpty }) {
  return (
    <ul>
      {items.length === 0 && showEmpty && <li>No items</li>}
      {items.map(item => <li key={item.id}>{item.name}</li>)}
    </ul>
  );
}
```

**Follow-up questions:**

- *"Why doesn't the browser understand JSX directly?"* — JSX isn't part of the JavaScript language specification at all — it's a syntax extension that only build tooling (Babel, a bundler's built-in transform) understands, which is why a JSX file must always go through a build step before it can run in a browser.
- *"Why is `{condition && <Component />}` common in JSX instead of an `if` statement?"* — JSX expressions inside `{}` must be expressions, not statements — `if` is a statement and can't be embedded directly inside JSX curly braces, so a short-circuiting expression (`&&`, a ternary) is the idiomatic way to express a conditional inline within markup.

**Sources:** [React — Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx), [React — JavaScript in JSX with Curly Braces](https://react.dev/learn/javascript-in-jsx-with-curly-braces)

---

### 3. What Is a Component, and How Do Props Flow Through One?

**Core answer:**

"A component is a JavaScript function that accepts a single argument — conventionally destructured as named `props` — and returns JSX describing what should render. Props are how data flows from a parent component into a child: a parent passes them as JSX attributes (`<UserCard name="Alex" age={30} />`), and the child receives them as its function argument, read-only from the child's perspective — a child should never mutate the props object it receives, since that object may be the exact same reference the parent is also holding and rendering from. This one-directional flow — data only ever flows down, from parent to child, never the other way through props themselves — is a deliberate, foundational design choice in React, not an incidental limitation: a child that needs to affect a parent's state does so by calling a function the parent passed down as a prop, not by writing to its own props directly."

**Staff-level extension:**

The precise architectural reason one-way data flow matters at scale, worth stating beyond "it's the rule": in a UI where data could flow in both directions through the same channel, tracing where a given value's current state actually came from requires following both the down-the-tree prop passing and any up-the-tree mutation paths simultaneously, which becomes intractable in a large component tree; one-way flow means a value's origin is always traceable by walking up the tree exactly once, toward whichever ancestor owns that piece of state. This is also precisely why "lifting state up" (covered later in this guide) is React's answer to two sibling components needing to share or coordinate state — rather than one sibling reaching across to mutate the other's props or state directly, which the one-way model doesn't allow, the shared state moves up to their common parent, and both siblings receive it (and a callback to change it) as props.

**Example:**

```jsx
function UserCard({ name, age }) { // props received as a plain function argument, destructured
  return <p>{name}, age {age}</p>;
}

function App() {
  return <UserCard name="Alex" age={30} />; // data flows DOWN from App into UserCard via props
}

// A child affecting a parent: NOT by writing to props, but by calling a
// function the parent explicitly passed down.
function Parent() {
  const [count, setCount] = React.useState(0);
  return <Child onIncrement={() => setCount(count + 1)} />;
}
function Child({ onIncrement }) {
  return <button onClick={onIncrement}>Increment parent's count</button>;
}
```

**Follow-up questions:**

- *"What happens if a child component mutates a prop object directly, e.g. `props.user.name = 'new'`?"* — Since the prop is very likely the same object reference the parent is holding, this silently mutates the parent's data too, bypassing React's state-update mechanism entirely — the UI may not even re-render to reflect the change, since nothing told React a state update occurred.
- *"How does a deeply nested descendant get data from a distant ancestor without every intermediate component needing that prop?"* — Passing it down through every intermediate layer is called prop drilling, and Context (covered later) is React's built-in answer for the case where prop drilling becomes impractical.

**Sources:** [React — Passing Props to a Component](https://react.dev/learn/passing-props-to-a-component), [React — Your First Component](https://react.dev/learn/your-first-component)

---

### 4. How Does the `useState` Hook Work?

**Core answer:**

"`useState(initialValue)` gives a function component a piece of state that persists across re-renders — something a plain local variable inside the function body couldn't do, since the entire function body re-runs from scratch on every render, which would reset a plain variable back to its initial value every time. It returns an array of exactly two items: the current value, and a setter function to update it — calling the setter with a new value schedules a re-render, and on that next render, `useState` returns the new value instead of the old one. A critical, easy-to-miss detail: calling the setter does not mutate the existing state variable in place and does not immediately change the value available in the currently-executing function — the update is scheduled, and the new value is only visible starting from the next render, which is why reading the state variable again immediately after calling its setter, in the same function call, still shows the old value."

**Staff-level extension:**

The precise mechanism worth being able to explain, not just its symptom: React associates each `useState` call with a specific "slot" in that component instance's internal state, tracked by the *order* Hooks are called in during render — which is exactly why Hooks must be called unconditionally, at the top level of a component, never inside a conditional, loop, or nested function; calling a different number or order of Hooks between renders would misalign which stored value corresponds to which `useState` call. Functional updates (`setCount(prev => prev + 1)` instead of `setCount(count + 1)`) matter specifically when multiple updates to the same state might be scheduled before a re-render happens — passing a function guarantees each update operates on the actual latest pending value rather than a stale value captured in the closure from when the event handler was originally created.

**Example:**

```jsx
function Counter() {
  const [count, setCount] = React.useState(0);

  function handleTripleClick() {
    setCount(count + 1); // BUG: all three reference the same stale `count` from this render — ends at count + 1, not +3
    setCount(count + 1);
    setCount(count + 1);
  }

  function handleTripleClickCorrect() {
    setCount(prev => prev + 1); // each functional update sees the latest pending value — ends at count + 3
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
  }

  return <button onClick={handleTripleClickCorrect}>Count: {count}</button>;
}
```

**Follow-up questions:**

- *"Why does calling the setter three times in a row with `count + 1` not increment by 3?"* — All three calls in the same event handler close over the same `count` value from that render — none of them see each other's effect until the next render — so they all schedule the same "set to `count + 1`" update, not three sequential increments.
- *"Why must Hooks be called unconditionally, at the top level, never inside an `if`?"* — React tracks which `useState`/`useEffect` call corresponds to which internal state slot purely by the order they're called in during render — a conditional Hook call would change that order between renders and silently misalign every subsequent Hook's stored value.

**Sources:** [React — `useState`](https://react.dev/reference/react/useState), [React — Rules of Hooks](https://react.dev/warnings/invalid-hook-call-warning)

---

### 5. What's the Difference Between a Controlled and an Uncontrolled Input?

**Core answer:**

"A controlled input's value is driven entirely by React state — the input's `value` attribute is bound to a state variable, and an `onChange` handler updates that state on every keystroke, meaning React state is always the single source of truth for what the input displays, and the DOM input element itself has no independent memory of its own value. An uncontrolled input instead manages its own value internally, in the DOM, the way a plain HTML input normally would — React reads that value only when it needs it (typically via a `ref`, on form submission), rather than tracking every keystroke through state. Controlled inputs are generally preferred when the input's value needs to be validated, transformed, or reacted to as the user types, or when multiple UI elements need to stay in sync with it; uncontrolled inputs are simpler and have a lower per-keystroke re-render cost, which can matter for a very large form or a performance-sensitive input, at the cost of not having that value readily available in state until you explicitly go read it."

**Staff-level extension:**

The precise performance trade-off worth naming for a Staff-level answer: a controlled input triggers a React re-render on every single keystroke (since the `onChange` handler calls a state setter each time), which is entirely fine for the overwhelming majority of forms, but can become a genuine, measurable cost in a form with many controlled inputs re-rendering together, or an input feeding an expensive computation on every change — the mitigation isn't necessarily "switch to uncontrolled" but often debouncing the expensive downstream work (an API call, a heavy validation function) while keeping the input itself controlled for correctness and immediate visual feedback. React 19's Actions and form-related hooks (covered later in this guide) provide a third pattern specifically for form submission — reading a native `FormData` object from an uncontrolled-style form on submit — that avoids per-keystroke state entirely for cases where only the submitted values, not the live keystroke-by-keystroke value, actually matter.

**Example:**

```jsx
// Controlled — React state is the source of truth
function ControlledInput() {
  const [value, setValue] = React.useState('');
  return <input value={value} onChange={e => setValue(e.target.value)} />;
}

// Uncontrolled — the DOM manages its own value; React reads it via a ref only when needed
function UncontrolledInput() {
  const inputRef = React.useRef(null);
  function handleSubmit() {
    console.log(inputRef.current.value); // read only at submission time, not on every keystroke
  }
  return (
    <>
      <input ref={inputRef} defaultValue="" />
      <button onClick={handleSubmit}>Submit</button>
    </>
  );
}
```

**Follow-up questions:**

- *"What happens if you set an input's `value` prop without also providing an `onChange` handler?"* — React logs a console warning and the input becomes read-only from the user's perspective — since nothing updates the state backing `value`, every keystroke is immediately overwritten back to the unchanged state value on the next render.
- *"When would you deliberately choose an uncontrolled input?"* — A very large form where per-keystroke state updates and re-renders would be a measurable performance cost, or a simple form where only the final submitted values matter and no live validation/transformation is needed per keystroke.

**Sources:** [React — Reacting to Input with State](https://react.dev/learn/reacting-to-input-with-state), [React — Sharing State Between Components](https://react.dev/learn/sharing-state-between-components)

---

### 6. Why Does React Need a `key` Prop When Rendering a List?

**Core answer:**

"When React reconciles a list of rendered elements against its previous render, `key` is what lets it tell which item is which across renders — without a stable, unique `key`, React falls back to comparing elements by their position (index) in the list alone, which breaks down the moment the list is reordered, filtered, or has an item inserted/removed anywhere but the very end: React will incorrectly think the item now at a given position is the same 'item' that was previously at that position, potentially reusing the wrong DOM node's internal state (an input's typed text, a checkbox's checked state, a component's local `useState`) for what is actually a different logical item. A `key` should be a stable, unique identifier genuinely tied to the item's identity — typically an ID from a database or data source — not the array index, and not a randomly generated value created fresh on every render, both of which defeat the purpose `key` exists to serve."

**Staff-level extension:**

The precise, concrete failure mode worth being able to describe exactly, since "just use a real ID, not the index" undersells why it matters: if a list item contains its own local state (an uncontrolled input's value, an open/closed toggle, a component's internal `useState`) and the list is reordered or has an item removed from the middle while using array index as `key`, React will match the wrong DOM node (and its associated internal state) to the wrong logical item after the reorder — visually, a checkbox that was checked on "item C" can appear checked on "item B" after "item A" is deleted, because React saw "the element at index 0" persist and reused its state, never realizing the underlying data item at that position actually changed. Using array index as `key` is not always wrong — for a list that is genuinely static and never reordered, filtered, or has items inserted/removed from anywhere but the end, index and stable-ID keys behave identically — but relying on that assumption holding forever in code that will be maintained by other people is a fragile bet, which is why a stable ID is the default recommendation even when index would technically work today.

**Example:**

```jsx
// BROKEN: index as key — breaks if `todos` is ever reordered or filtered
function TodoListBroken({ todos }) {
  return (
    <ul>
      {todos.map((todo, index) => (
        <li key={index}>
          <input type="checkbox" defaultChecked={todo.done} /> {todo.text}
        </li>
      ))}
    </ul>
  );
}

// CORRECT: a stable identifier from the data itself
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <input type="checkbox" defaultChecked={todo.done} /> {todo.text}
        </li>
      ))}
    </ul>
  );
}
```

**Follow-up questions:**

- *"Is it ever acceptable to use the array index as `key`?"* — Yes, specifically for a list that is provably static — never reordered, filtered, or modified anywhere but appended to at the end — though a stable ID remains the safer default since that assumption is easy to accidentally violate later.
- *"Why not generate a new random key on every render instead of using the index?"* — That defeats `key`'s entire purpose from the opposite direction — if the key changes every render even for the same logical item, React treats it as an entirely new element every time, destroying and recreating its DOM node (and losing its state) on every single render, which is strictly worse than the index problem.

**Sources:** [React — Rendering Lists](https://react.dev/learn/rendering-lists), [React — Keeping List Items in Order with `key`](https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key)

---

## Intermediate

### 7. How Does `useEffect` Work, and What Is the Cleanup Function For?

**Core answer:**

"`useEffect(fn, dependencies)` lets a component run code that synchronizes with something outside React's own rendering — subscribing to an external data source, setting up a timer, manipulating the DOM directly, or making an API call — after React has committed the render to the DOM. The dependency array controls when the effect re-runs: React compares each dependency's value against its previous render's value, and only re-runs the effect if at least one has changed (an empty array `[]` means the effect runs once, after the first render only; omitting the array entirely means it runs after every render). If the effect function returns another function, React treats that returned function as cleanup — calling it right before the effect runs again (if its dependencies changed) and also when the component unmounts — which is exactly the place to reverse whatever the effect set up: unsubscribing, clearing a timer, removing an event listener, aborting an in-flight request, mirroring the `ngOnDestroy()` cleanup responsibility covered in the Angular guide."

**Staff-level extension:**

The precise, commonly-tested subtlety worth being able to state exactly: the cleanup function isn't only for unmount — it runs before *every* re-execution of the effect, not just the final one, which is exactly what makes `useEffect` safe for subscriptions whose target can change (a WebSocket connection to a room ID that can change, a timer whose interval prop can change) — each time the effect re-runs, the previous subscription is cleaned up first, then the new one is established, rather than accumulating multiple simultaneous subscriptions. React 18's Strict Mode deliberately mounts, unmounts, and remounts a component once extra in development specifically to surface effects whose cleanup is missing or incorrect — a component whose effect doesn't clean up properly will visibly misbehave (a duplicated subscription, a doubled counter) under Strict Mode in development even though it might appear to "work" without it, which is a deliberate design choice to catch this class of bug before it reaches production.

**Example:**

```jsx
function ChatRoom({ roomId }) {
  React.useEffect(() => {
    const connection = createConnection(roomId); // set up
    connection.connect();

    return () => {
      connection.disconnect(); // cleanup — runs before the next effect execution AND on unmount
    };
  }, [roomId]); // re-runs (cleanup old connection, establish new one) whenever roomId changes

  return <p>Connected to {roomId}</p>;
}
```

**Follow-up questions:**

- *"What happens if you forget the dependency array entirely, versus passing an empty array?"* — Omitting it entirely re-runs the effect after every single render, which for a subscription/timer-setup effect means creating a brand-new one on every render without ever cleaning up the prior one properly between them — an empty array runs the effect exactly once, after the initial render.
- *"Why does React's Strict Mode intentionally mount, unmount, and remount a component in development?"* — Specifically to surface effects with missing or buggy cleanup — a component whose effect properly cleans up behaves identically whether mounted once or mounted-unmounted-remounted, so any visible difference (like a duplicated subscription) is a real bug Strict Mode is designed to catch in development rather than production.

**Sources:** [React — `useEffect`](https://react.dev/reference/react/useEffect), [React — Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects), [React — Lifecycle of Reactive Effects](https://react.dev/learn/lifecycle-of-reactive-effects)

---

### 8. What Problem Does the Context API Solve?

**Core answer:**

"Context lets a value be made available to an entire subtree of components without passing it down manually as a prop through every intermediate component that doesn't itself need that value — the exact 'prop drilling' problem from the earlier props question, where a value needed by a deeply nested descendant would otherwise have to be threaded through every layer in between. A `Context` object is created with `createContext(defaultValue)`; a `<Context.Provider value={...}>` wraps the subtree that should have access to that value; and any descendant, no matter how deeply nested, reads it directly with `useContext(Context)`, skipping every intermediate layer entirely. Common real uses are things genuinely global to a large subtree or the whole app — the current authenticated user, a UI theme, the active locale for internationalization — where passing the value down explicitly through many layers of components that don't use it themselves would add real, pointless boilerplate to every one of those intermediate components."

**Staff-level extension:**

The precise trade-off worth naming for a Staff-level answer: Context is not a general-purpose state-management replacement for something like Redux or Zustand, and reaching for it as one has a real, specific cost — every component that calls `useContext(Context)` re-renders whenever the Provider's `value` changes, with no built-in way to subscribe to only part of that value, so a Context holding several unrelated pieces of state causes every consumer to re-render on any of them changing, even ones a given consumer doesn't actually read. The practical mitigations are splitting a large Context into several narrower ones scoped to logically-related state (so unrelated updates don't cause unrelated re-renders), and, for state that changes frequently or needs fine-grained subscriptions, reaching for a dedicated state-management library instead — Context is the right tool specifically for infrequently-changing, broadly-needed values, not high-frequency application state.

**Example:**

```jsx
const ThemeContext = React.createContext('light'); // default value, used if no Provider is above

function App() {
  const [theme, setTheme] = React.useState('dark');
  return (
    <ThemeContext.Provider value={theme}>
      <Toolbar /> {/* Toolbar itself never touches theme — no prop drilling needed */}
    </ThemeContext.Provider>
  );
}

function Toolbar() {
  return <ThemedButton />; // passes through without needing to know about theme at all
}

function ThemedButton() {
  const theme = React.useContext(ThemeContext); // reads directly, skipping Toolbar entirely
  return <button className={theme}>Click me</button>;
}
```

**Follow-up questions:**

- *"What re-renders when a Context's `value` changes?"* — Every component that calls `useContext` on that specific Context re-renders, regardless of which part of the value it actually reads — there's no built-in partial-subscription mechanism, which is the main reason Context isn't a drop-in replacement for a full state-management library.
- *"How would you avoid unnecessary re-renders if a Context holds multiple pieces of unrelated state?"* — Split it into multiple, narrower Context objects, each holding logically-related state, so a component only re-renders when the specific Context it actually consumes changes, not any of the others.

**Sources:** [React — Passing Data Deeply with Context](https://react.dev/learn/passing-data-deeply-with-context), [React — `useContext`](https://react.dev/reference/react/useContext)

---

### 9. What's the Difference Between `useMemo` and `useCallback`?

**Core answer:**

"Both exist to skip unnecessary recomputation across re-renders, and both take a dependency array with the same re-run semantics as `useEffect`'s — but they memoize different things. `useMemo(fn, deps)` caches the *return value* of calling `fn`, recomputing it only when a dependency changes — useful for an expensive calculation (filtering/sorting a large array, a heavy derived computation) that would otherwise re-run on every render even when its inputs haven't changed. `useCallback(fn, deps)` caches the *function reference itself*, returning the exact same function instance across renders as long as dependencies haven't changed, rather than a new function object being created on every render (which happens by default in JavaScript every time a function is defined inside a component body). `useCallback` matters specifically because a new function reference on every render can defeat `React.memo`'s reference-equality check on a child component that receives that function as a prop, causing the child to re-render even when nothing it actually cares about changed."

**Staff-level extension:**

The precise reason both hooks exist as *optimizations*, not correctness requirements, is worth stating directly for a Staff-level answer: skipping either one doesn't produce a wrong result — a non-memoized `useMemo` value or a non-memoized `useCallback` function are both just recomputed/recreated on every render, which is what happens anyway without the hook — the only cost of omitting them is potentially wasted work (an expensive recalculation, or a downstream `React.memo`'d child re-rendering unnecessarily), never incorrect behavior. This is exactly why reaching for `useMemo`/`useCallback` everywhere "just in case" is itself a real anti-pattern — each one has its own (small, but non-zero) bookkeeping cost, and applying them to a cheap computation or to a function passed to a component that isn't itself memoized provides no benefit at all while adding code complexity; the judgment call is measuring an actual, demonstrated cost (a slow render, a profiler-confirmed unnecessary child re-render) before reaching for either, not applying them reflexively. The React Compiler, covered later in this guide, exists specifically to automate this judgment call away in the common case.

**Example:**

```jsx
function ProductList({ products, onSelect }) {
  // useMemo: caches the computed VALUE — avoids re-sorting on every render
  const sorted = React.useMemo(
    () => [...products].sort((a, b) => a.price - b.price),
    [products]
  );

  // useCallback: caches the FUNCTION REFERENCE — lets React.memo below actually skip re-rendering
  const handleSelect = React.useCallback(
    (id) => onSelect(id),
    [onSelect]
  );

  return sorted.map(p => <ProductRow key={p.id} product={p} onSelect={handleSelect} />);
}

const ProductRow = React.memo(function ProductRow({ product, onSelect }) {
  // Without useCallback above, `onSelect` would be a NEW function reference every
  // ProductList render, defeating React.memo here — this component would re-render every time regardless.
  return <button onClick={() => onSelect(product.id)}>{product.name}</button>;
});
```

**Follow-up questions:**

- *"If you remove `useCallback` from the example above, does the app produce a wrong result?"* — No — `ProductRow` would just re-render more often than necessary, since `React.memo`'s reference-equality check on `onSelect` would fail every time; the behavior is still correct, just less efficient.
- *"When is `useMemo`/`useCallback` actually not worth using?"* — For a cheap computation, or a function passed to a component that isn't itself wrapped in `React.memo` — in both cases the memoization's own small overhead isn't offset by any actual savings, since there's nothing expensive being skipped.

**Sources:** [React — `useMemo`](https://react.dev/reference/react/useMemo), [React — `useCallback`](https://react.dev/reference/react/useCallback), [React — `memo`](https://react.dev/reference/react/memo)

---

### 10. What Is a Custom Hook, and When Would You Write One?

**Core answer:**

"A custom Hook is simply a JavaScript function whose name starts with `use` and that calls one or more of React's built-in Hooks internally — a mechanism for extracting and reusing *stateful logic* between components, as opposed to a regular utility function, which can share plain logic but can't itself hold state or use other Hooks outside a component or another Hook. A custom Hook doesn't share state between the components that use it — each call gets its own, entirely independent instance of whatever state it manages internally, the same as if that logic were written directly inline in each component; what's shared is the *logic*, not a single piece of state. Common real reasons to extract one: the same stateful pattern (a `useEffect`-plus-`useState` combination for tracking window size, fetching data with loading/error states, debouncing a value) is duplicated verbatim across multiple components, or a component's own logic has grown complex enough that separating a self-contained piece into a named Hook makes the component's body easier to read."

**Staff-level extension:**

The precise distinction worth being explicit about at Staff level: a custom Hook is not a lifecycle-independent singleton or a shared store — calling `useWindowSize()` in three different components creates three entirely separate `useState`/`useEffect` instances, each with its own independent state and its own independent subscription/cleanup, not one shared value magically available everywhere (that's what Context or a dedicated store solves instead, a genuinely different problem). The naming convention (`use` prefix) isn't cosmetic — it's what allows the linter (`eslint-plugin-react-hooks`) to enforce the Rules of Hooks specifically on that function, catching the same class of bugs (conditional Hook calls, calling Hooks outside a component or another Hook) it enforces on built-in Hooks — a function containing Hook calls that isn't named with a `use` prefix won't get that safety check applied, which is a real, easy-to-miss source of subtle Hook-order bugs.

**Example:**

```jsx
function useWindowSize() {
  const [size, setSize] = React.useState({ width: window.innerWidth, height: window.innerHeight });

  React.useEffect(() => {
    function handleResize() {
      setSize({ width: window.innerWidth, height: window.innerHeight });
    }
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize); // cleanup, per the useEffect question above
  }, []);

  return size;
}

// Each component using this Hook gets its OWN independent size state and listener:
function Header() {
  const { width } = useWindowSize();
  return <header>{width < 600 ? 'Mobile header' : 'Desktop header'}</header>;
}
```

**Follow-up questions:**

- *"If two components both call `useWindowSize()`, do they share the same `size` value?"* — No — each call creates its own completely independent `useState` and `useEffect` instance; they'll compute the same value since they're both reading `window.innerWidth`, but they're not sharing state, they're duplicating equivalent, independently-tracked state.
- *"Why must a custom Hook's name start with `use`?"* — It's the signal that lets the Rules-of-Hooks linter recognize the function as a Hook and apply the same static checks (no conditional calls, no calls outside a component/another Hook) it applies to React's own built-in Hooks — without the prefix, those checks silently don't apply.

**Sources:** [React — Reusing Logic with Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks), [React — Rules of Hooks](https://react.dev/warnings/invalid-hook-call-warning)

---

### 11. What Are Refs For, and How Do They Differ From State?

**Core answer:**

"A ref, created with `useRef(initialValue)`, holds a mutable value in an object with a single `.current` property that persists across re-renders — the same persistence guarantee `useState` provides — but changing a ref's `.current` does not trigger a re-render, and reading it does not need to go through any React re-render cycle at all. This makes refs the right tool for exactly two common cases: holding a mutable value that the component's rendered output doesn't actually depend on (a timer ID to clear later, a previous value for comparison, a mutable flag), and accessing an actual underlying DOM node directly (focusing an input, measuring an element's size, integrating a non-React library that needs a real DOM element) via `<div ref={myRef}>`, after which `myRef.current` is the actual DOM node. State should be used for anything the component's rendered UI needs to reflect; refs should be used for anything that needs to persist and be mutable but should not, by itself, cause the component to re-render when it changes."

**Staff-level extension:**

The precise reason using a ref for something that *should* affect the rendered output is a real, common bug worth being able to name exactly: since updating `.current` doesn't trigger a re-render, the DOM will keep showing stale content even after the ref's value has genuinely changed, until some *other* re-render happens to occur for an unrelated reason and the component happens to read the ref's now-current value during that render — which makes the bug appear intermittent and confusing rather than consistently broken, since it "works" whenever something else coincidentally triggers a re-render. As of React 19, `ref` can be passed as a plain prop directly to function components without `forwardRef` — a real, meaningful ergonomic change from React 18 and earlier, where a function component needed to be explicitly wrapped in `React.forwardRef()` to accept a ref from its parent at all.

**Example:**

```jsx
function Stopwatch() {
  const [running, setRunning] = React.useState(false);
  const intervalRef = React.useRef(null); // holds a timer ID — doesn't need to trigger re-renders itself

  function start() {
    setRunning(true);
    intervalRef.current = setInterval(() => console.log('tick'), 1000);
  }
  function stop() {
    setRunning(false);
    clearInterval(intervalRef.current); // read/cleared without causing any re-render
  }

  return <button onClick={running ? stop : start}>{running ? 'Stop' : 'Start'}</button>;
}

// React 19: ref as a plain prop, no forwardRef needed
function TextInput({ ref, placeholder }) {
  return <input ref={ref} placeholder={placeholder} />;
}
```

**Follow-up questions:**

- *"What happens if you use a ref to store a value your JSX actually displays?"* — The displayed value goes stale after the ref changes, since no re-render is triggered — it only updates the next time the component happens to re-render for some unrelated reason, producing a confusing, intermittent-looking bug.
- *"What changed about `ref` and function components in React 19 specifically?"* — Function components can now accept `ref` as a plain named prop directly, without wrapping the component in `React.forwardRef()` — `forwardRef` still works for backward compatibility but is no longer necessary for new code.

**Sources:** [React — `useRef`](https://react.dev/reference/react/useRef), [React — Manipulating the DOM with Refs](https://react.dev/learn/manipulating-the-dom-with-refs), [React — v19 Ref as a prop](https://react.dev/blog/2024/12/05/react-19)

---

### 12. What's the Difference Between Lifting State Up and Prop Drilling?

**Core answer:**

"Lifting state up means moving a piece of state from a child component to their closest common ancestor, so that ancestor can pass both the value and an updater function down to however many children need to read or change it — it's React's standard answer to two sibling components needing to share or stay synchronized on the same state, since siblings can't communicate directly with each other through props at all, only through a shared parent. Prop drilling is the separate, related problem of passing a value down through several layers of intermediate components that don't themselves use that value, purely so it can reach a deeply nested descendant that does — it's not wrong in principle, just increasingly inconvenient and noisy as the number of intermediate layers grows, and it's the specific problem Context (covered earlier) exists to solve for values that need to reach deeply without every layer in between needing to know about them."

**Staff-level extension:**

The precise decision boundary worth being able to state clearly at Staff level: lifting state up is about *where state should live* (moving its ownership to the right common ancestor), while Context is about *how a value gets from where it lives to where it's needed* without manually threading it through every intermediate layer — the two aren't alternatives to each other, they solve different parts of the same broader problem, and a real component tree commonly needs both: state lifted to an appropriate ancestor, then made available to distant descendants via Context rather than prop drilling through every layer in between. A genuinely common design mistake is lifting state further up the tree than it needs to go "just in case," which needlessly widens the set of components that re-render when it changes — the correct level to lift state to is the lowest common ancestor that actually needs it, not the application root by default.

**Example:**

```jsx
// Two siblings need synchronized state -> lift it to their common parent
function TemperatureConverter() {
  const [celsius, setCelsius] = React.useState(0); // lifted here — the common ancestor
  return (
    <>
      <CelsiusInput value={celsius} onChange={setCelsius} />
      <FahrenheitDisplay celsius={celsius} /> {/* sibling reads the SAME lifted state */}
    </>
  );
}

function CelsiusInput({ value, onChange }) {
  return <input type="number" value={value} onChange={e => onChange(Number(e.target.value))} />;
}
function FahrenheitDisplay({ celsius }) {
  return <p>{(celsius * 9) / 5 + 32}°F</p>;
}
```

**Follow-up questions:**

- *"Why can't two sibling components just pass state directly to each other?"* — Props only flow from parent to child, never sideways between siblings — the only path for two siblings to share state is through a common ancestor that owns it and passes it (or an updater) down to both.
- *"If lifting state up and Context solve different problems, when do you need both together?"* — When state needs to be owned by a specific ancestor (lifted appropriately, not too far up) but also needs to reach several deeply nested descendants scattered across the tree — the state lives at the lifted location, and Context is the delivery mechanism to the distant consumers, avoiding prop drilling through every layer in between.

**Sources:** [React — Sharing State Between Components](https://react.dev/learn/sharing-state-between-components), [React — Passing Data Deeply with Context](https://react.dev/learn/passing-data-deeply-with-context)

---

## Staff Level

### 13. How Does React's Reconciliation Algorithm Actually Work?

**Core answer:**

"React's diffing algorithm is a heuristic, not a general tree-diff — a fully general tree-diffing algorithm is computationally expensive (roughly O(n³) for n nodes in the naive case), so React instead uses two deliberate assumptions that make the common case fast: two elements of different types produce entirely different trees, so React tears down the old subtree and builds a new one from scratch rather than trying to diff their internals at all; and for a list of children, `key` (covered earlier) is what lets React match elements across renders efficiently, rather than falling back to a much more expensive general comparison. Internally, this all runs on top of Fiber, React's reconciliation engine (introduced in React 16) — a data structure representing the component tree as a linked list of 'fiber' nodes that can be processed incrementally, one unit of work at a time, rather than requiring a single, uninterruptible pass through the whole tree — which is precisely what makes concurrent rendering, covered in the next question, possible at all."

**Staff-level extension:**

The precise reason Fiber's incremental-unit-of-work model matters, worth being able to state exactly: before Fiber (in React 15 and earlier), reconciliation for a given update ran as one synchronous, uninterruptible pass over the entire affected tree — for a large enough tree, this could block the main thread long enough to visibly drop frames or delay input responsiveness, with no way for React to pause and let something more urgent (a keystroke, an animation frame) happen first. Fiber restructures that same work into small, individually resumable units, letting React's scheduler pause low-priority reconciliation work, yield to the browser to handle something more urgent, and resume where it left off — the tree-diffing heuristics (element-type identity, `key`-based list matching) determine *what* work needs to happen, and Fiber is *how* that work gets scheduled and executed without blocking the main thread for the whole duration.

**Example:**

```jsx
// Different element TYPES at the same position -> React discards the old subtree entirely,
// it does not try to diff <UserProfile>'s internals against <GuestBanner>'s.
function Header({ loggedIn }) {
  return loggedIn ? <UserProfile /> : <GuestBanner />;
  // Switching loggedIn unmounts whichever was rendered and mounts the other fresh —
  // any local state inside UserProfile/GuestBanner is lost on the switch, by design.
}

// SAME element type, different props -> React reuses the existing DOM node and updates only what changed.
function Header2({ title }) {
  return <h1>{title}</h1>; // changing `title` updates the existing <h1>'s text, doesn't recreate the element
}
```

**Follow-up questions:**

- *"What's the practical consequence of React tearing down a subtree when the element type changes, rather than diffing it?"* — Any local state inside that subtree (a form's typed values, a toggle's open/closed state) is lost, since the old component instance is unmounted and a genuinely new instance of the other component is mounted in its place, not updated in place.
- *"What specific capability does Fiber's incremental architecture unlock that the pre-Fiber reconciler couldn't do?"* — The ability to pause a render mid-way, let something more urgent run first (like responding to a keystroke), and resume — the foundation concurrent rendering and features like `useTransition`/`Suspense` are built on.

**Sources:** [React — Preserving and Resetting State](https://react.dev/learn/preserving-and-resetting-state), [React (GitHub) — Fiber Architecture](https://github.com/acdlite/react-fiber-architecture)

---

### 14. What Is Concurrent Rendering, and How Do `useTransition` and `Suspense` Use It?

**Core answer:**

"Concurrent rendering is the capability, built on Fiber, for React to work on an update in the background — interruptibly, without blocking the main thread — and pause, abandon, or restart that work if something more urgent comes in before it finishes, rather than every update being an uninterruptible, all-or-nothing block. `useTransition` lets a component mark a state update as low-priority ('a transition'): `startTransition(() => setSomeState(newValue))` tells React this update can be interrupted by something more urgent (the next keystroke in a search box), and the hook's `isPending` flag shows a pending indicator while that lower-priority work is still in progress. `Suspense` lets a component 'wait' for something — data, code, an image — to be ready before rendering, showing a fallback in the meantime, built on the same underlying mechanism: React can render other, unrelated parts of the tree while a Suspended part is still waiting, rather than blocking the whole render on one slow piece."

**Staff-level extension:**

The precise distinction worth being able to draw exactly at Staff level: concurrent rendering does not make any individual computation faster — it does not parallelize work across CPU cores, and it doesn't reduce the total amount of work React has to do — its value is entirely about *scheduling and interruptibility*: prioritizing urgent updates (a keystroke, a click) over less urgent ones (a large list re-filtering, a heavy derived computation) so the app *feels* more responsive, even though the total work done and total time to complete the low-priority update may be the same or slightly more. A concrete, common Staff-level scenario worth being able to walk through: a search input where every keystroke both updates the input's own displayed text immediately (a high-priority update) and triggers an expensive filter over a large list (wrapped in `startTransition`, a low-priority update) — without the transition, a fast typist's keystrokes would visibly lag behind the expensive re-filtering; with it, the input stays responsive immediately, and the filtered list updates as fast as it can in the background, interruptible by the very next keystroke.

**Example:**

```jsx
function SearchPage({ allItems }) {
  const [query, setQuery] = React.useState('');
  const [isPending, startTransition] = React.useTransition();
  const [results, setResults] = React.useState(allItems);

  function handleChange(e) {
    setQuery(e.target.value); // HIGH priority — input stays responsive immediately

    startTransition(() => {
      // LOW priority — can be interrupted by the next keystroke before it finishes
      setResults(allItems.filter(item => item.name.includes(e.target.value)));
    });
  }

  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending && <span>Updating results...</span>}
      <ResultsList results={results} />
    </>
  );
}
```

**Follow-up questions:**

- *"Does wrapping an update in `startTransition` make that update itself complete faster?"* — No — it doesn't reduce the work or speed up the computation itself; it only makes the update interruptible and lower-priority, so more urgent updates aren't blocked behind it, which improves perceived responsiveness, not raw throughput.
- *"Why can React render other parts of the tree while a `Suspense` boundary is still waiting?"* — Because Fiber's incremental, unit-of-work model (from the reconciliation question) lets React work on unrelated parts of the tree independently, rather than the whole render being one indivisible operation blocked entirely on the slowest piece.

**Sources:** [React — `useTransition`](https://react.dev/reference/react/useTransition), [React — `Suspense`](https://react.dev/reference/react/Suspense), [React — Concurrent Features](https://react.dev/blog/2022/03/29/react-v18)

---

### 15. What Does the React Compiler Do, and How Does It Relate to `useMemo`/`useCallback`?

**Core answer:**

"The React Compiler is a build-time tool — a genuinely separate, independently-versioned project from React itself, which reached stable v1.0 in October 2025 — that automatically inserts the equivalent of `useMemo`/`useCallback`/`React.memo`-style memoization into components during compilation, based on static analysis of the component's code, rather than a developer having to identify which values and functions are worth memoizing and wrap them by hand. In a codebase using the Compiler, most manual `useMemo`/`useCallback` calls become unnecessary — the Compiler achieves the same optimization automatically and more consistently, since it can apply the analysis uniformly across the whole codebase rather than depending on a developer remembering to do it, and correctly, in every place it would help. It supports React 17 and newer, ships by default in new Vite, Next.js, and Expo project templates as of its stable release, and is applied at build time via a Babel plugin (or the equivalent in a given build tool), meaning it changes how code compiles, not React's runtime behavior itself."

**Staff-level extension:**

The precise scope boundary worth being exact about at Staff level: the Compiler automates *memoization* specifically — skipping unnecessary recomputation and re-renders that plain component code would otherwise trigger — but it does not replace `useState`, `useEffect`, Context, or any other Hook, and it does not change the fundamental rules a component must follow (the Rules of Hooks still apply, and in fact the Compiler relies on code following them to safely analyze it). It's also worth being able to state precisely why manual `useMemo`/`useCallback` isn't simply obsolete even with the Compiler enabled: a codebase not yet fully migrated to the Compiler, a library meant to work standalone without assuming consumers use it, or a specific case the Compiler's static analysis can't safely optimize (some genuinely dynamic patterns) may still need manual memoization — the Compiler is described by the React team as reducing the *need* for manual memoization in the common case, not eliminating hand-written memoization as a valid tool entirely.

**Example:**

```jsx
// Without the Compiler: a developer must remember to memoize manually
function ProductList({ products }) {
  const sorted = React.useMemo(() => [...products].sort((a, b) => a.price - b.price), [products]);
  return sorted.map(p => <ProductRow key={p.id} product={p} />);
}

// With the React Compiler enabled: written the same simple way,
// the Compiler inserts equivalent memoization automatically at build time —
// no useMemo call needed in the source at all.
function ProductListCompiled({ products }) {
  const sorted = [...products].sort((a, b) => a.price - b.price); // Compiler memoizes this automatically
  return sorted.map(p => <ProductRow key={p.id} product={p} />);
}
```

**Follow-up questions:**

- *"Is the React Compiler part of React's core release, versioned alongside it?"* — No — it's an independently-versioned, separate project (reaching its own stable v1.0 in October 2025) that supports React 17 and newer; a team can adopt a new React Compiler version without that being tied to a specific React version release at all.
- *"Does adopting the Compiler mean deleting all existing `useMemo`/`useCallback` calls immediately?"* — Not necessarily as a first step — existing manual memoization is generally safe to leave in place alongside the Compiler (it becomes redundant, not harmful, in the common case), and the React team's own guidance is to migrate incrementally rather than treating it as a required, immediate cleanup.

**Sources:** [React Compiler — Introduction](https://react.dev/learn/react-compiler), [React — React Compiler v1.0 announcement](https://react.dev/blog/2025/10/07/react-compiler-1)

---

### 16. What Are Server Components, and How Do They Differ From Client Components?

**Core answer:**

"A Server Component renders entirely on the server — it can read directly from a database, the filesystem, or an internal API without shipping any of that access code (or the libraries it needs) to the browser at all, and it never re-renders on the client or carries any client-side interactivity (no `useState`, no event handlers, no effects). A Client Component is what 'traditional' React has always been — code that ships to and runs in the browser, can hold state, respond to events, and use browser APIs — and is opted into explicitly with a `'use client'` directive at the top of the file. The practical value: moving data-fetching and non-interactive rendering logic into Server Components reduces the amount of JavaScript actually shipped to the browser (since a Server Component's own code never needs to be sent at all), while Client Components remain exactly where interactivity is genuinely needed — the two compose together in the same tree, with a Server Component able to render a Client Component as a child, and pass it serializable props."

**Staff-level extension:**

The precise architectural boundary worth being exact about, since it's a common point of confusion: Server Components are not the same thing as traditional server-side rendering (SSR) — SSR (also fully supported, and often combined with Server Components) renders a Client Component's initial HTML on the server for faster first paint, but that component's *code* still ships to the browser afterward and re-renders there (hydration); a Server Component's code never ships to the client at all, under any circumstance — it's not "rendered first on the server, then again on the client," it exists exclusively on the server, full stop. It's also important to be precise that the underlying React Server Components (RSC) bundler/wire-format APIs that make this possible are not yet semver-stable on their own — using Server Components in practice, as of this guide's baseline, means going through a framework (most commonly Next.js's App Router) that has integrated those APIs, rather than assembling the RSC machinery directly from React's raw APIs in a custom setup.

**Example:**

```jsx
// ProductDetails.jsx — a Server Component (no 'use client' directive)
// Runs ONLY on the server — this database import and query never reach the browser bundle at all.
import { db } from './db';

async function ProductDetails({ id }) {
  const product = await db.products.findById(id); // direct DB access, server-only
  return (
    <div>
      <h1>{product.name}</h1>
      <AddToCartButton productId={product.id} /> {/* a Client Component, rendered as a child */}
    </div>
  );
}

// AddToCartButton.jsx — a Client Component (explicit opt-in)
'use client';
function AddToCartButton({ productId }) {
  const [added, setAdded] = React.useState(false); // state/interactivity — needs the client
  return <button onClick={() => setAdded(true)}>{added ? 'Added!' : 'Add to Cart'}</button>;
}
```

**Follow-up questions:**

- *"Can a Server Component use `useState` or an `onClick` handler?"* — No — those require running in the browser, which a Server Component never does; any component needing state, effects, or event handlers must be a Client Component.
- *"Is React Server Components the same feature as server-side rendering (SSR)?"* — No, and conflating them is a common mistake — SSR produces server-rendered HTML for a component whose code still ships to and re-executes in the browser afterward; a Server Component's code never ships to the browser at all, under any circumstance.

**Sources:** [React — Server Components](https://react.dev/reference/rsc/server-components), [React — `'use client'`](https://react.dev/reference/rsc/use-client), [React — React 19 announcement](https://react.dev/blog/2024/12/05/react-19)

---

### 17. What Are Actions and `useActionState`, and What Problem Do They Solve?

**Core answer:**

"Actions are React 19's built-in pattern for handling async operations that update state — most commonly form submissions — where a function passed to a `<form>`'s `action` prop (or a button's `formAction`) automatically gets the form's data, and React automatically manages the pending state and error handling around it, rather than a developer manually wiring up `event.preventDefault()`, reading form values, tracking a loading boolean, and catching errors by hand every time. `useActionState(actionFn, initialState)` (renamed from `useFormState` during React 19's stabilization) wraps such a function and returns the current state, a version of the action wired up for use as a form's `action`, and a pending flag — giving a component the current result/error state and a pending indicator without separate manual `useState` calls to track each of those independently. `useFormStatus` is a related hook, callable from a child of the `<form>`, that reports the enclosing form's pending status without that child needing the action function or state passed down to it as props at all."

**Staff-level extension:**

The precise problem this replaces, worth naming directly: before Actions, a form submission handler in React typically needed several separate, manually-coordinated pieces — a `useState` for the pending/loading flag, another for any error message, `event.preventDefault()`, manually reading each field's value (or constructing a `FormData` from the event), and manual `try`/`catch`/`finally` to set pending back to false and populate the error state — Actions consolidate that entire pattern into one function and one hook, since `useActionState` handles the pending tracking and result/error state automatically based on the action function's own resolution or thrown error. It's also worth being precise that Actions work with native browser form semantics — a form using an Action still functions (submits, at minimum) even before JavaScript has finished loading/hydrating on the client, in frameworks that support this via progressive enhancement, which a purely `onSubmit`-plus-`preventDefault()`-based handler cannot do at all.

**Example:**

```jsx
import { useActionState } from 'react';

async function updateName(previousState, formData) {
  const name = formData.get('name');
  if (!name) return { error: 'Name is required' };
  await saveNameToServer(name);
  return { error: null, success: true };
}

function NameForm() {
  const [state, formAction, isPending] = useActionState(updateName, { error: null });

  return (
    <form action={formAction}>
      <input name="name" />
      <button disabled={isPending}>{isPending ? 'Saving...' : 'Save'}</button>
      {state.error && <p>{state.error}</p>}
    </form>
  );
}
```

**Follow-up questions:**

- *"What did `useActionState` used to be called, and why does that matter for reading older code/tutorials?"* — It was named `useFormState` during React's experimental/canary period before React 19's stable release renamed it — material referencing `useFormState` predates the rename and refers to the same underlying hook.
- *"How does `useFormStatus` differ from reading the pending flag `useActionState` returns directly?"* — `useFormStatus` is callable from a *child* component nested inside the `<form>`, without that child needing the action function, state, or pending flag passed down to it as props at all — useful for a reusable submit-button component that needs to know its enclosing form's pending status without being tightly coupled to that specific form's action.

**Sources:** [React — `useActionState`](https://react.dev/reference/react/useActionState), [React — `useFormStatus`](https://react.dev/reference/react-dom/hooks/useFormStatus), [React — React 19 announcement](https://react.dev/blog/2024/12/05/react-19)

---

### 18. How Would You Optimize the Performance of a Large React Application?

**Core answer:**

"I'd work through this in layers, starting with the changes that need the least specialized tooling. First, avoiding unnecessary re-renders: `React.memo` on components that re-render often with unchanged props, paired with `useMemo`/`useCallback` (or the React Compiler handling this automatically, covered earlier) so memoized components' reference-equality checks actually hold. Second, code splitting: `React.lazy()` plus `Suspense` to split rarely-needed or route-specific code into separate bundles loaded on demand, rather than shipping the entire application's JavaScript up front. Third, for a very large list specifically, virtualization — rendering only the list items currently visible in the viewport (plus a small buffer), via a library like `react-window` or `TanStack Virtual`, rather than rendering every item in a list of thousands, which no amount of memoization alone fixes, since the cost there is DOM node count itself, not re-render frequency."

**Staff-level extension:**

The precise judgment worth demonstrating at Staff level is knowing which of these actually addresses a given bottleneck, since they solve genuinely different problems: memoization (`React.memo`/`useMemo`/`useCallback`/the Compiler) addresses *unnecessary re-computation and re-rendering* of components whose inputs haven't meaningfully changed; code splitting addresses *initial bundle size and load time*, not runtime rendering performance at all; and virtualization addresses *DOM node count* for very large lists, a problem no amount of memoization fixes since even a perfectly memoized component still costs something to keep mounted in the DOM if there are thousands of them simultaneously. The correct starting point, before applying any of these speculatively, is React DevTools' Profiler — recording an interaction and inspecting exactly which components rendered, how long each took, and why (a changed prop, a changed piece of context, a parent re-render) — since applying memoization or virtualization to a component that wasn't actually the bottleneck adds real complexity for no measured benefit.

**Example:**

```jsx
// Code splitting: this route's code loads only when navigated to
const ReportsPage = React.lazy(() => import('./ReportsPage'));

function App() {
  return (
    <React.Suspense fallback={<Spinner />}>
      <ReportsPage />
    </React.Suspense>
  );
}

// Virtualization: renders only the visible slice of a 10,000-item list,
// not all 10,000 DOM nodes at once
import { FixedSizeList } from 'react-window';

function BigList({ items }) {
  return (
    <FixedSizeList height={600} itemCount={items.length} itemSize={35} width="100%">
      {({ index, style }) => <div style={style}>{items[index].name}</div>}
    </FixedSizeList>
  );
}
```

**Follow-up questions:**

- *"Would memoizing every component in a large list fix a slow-scrolling performance problem?"* — Not by itself — if the underlying issue is thousands of simultaneously-mounted DOM nodes, memoization reduces unnecessary re-renders of those nodes but doesn't reduce how many exist in the DOM at once; virtualization addresses that specific cost directly.
- *"What's the risk of applying `React.memo`/`useMemo` speculatively, without profiling first?"* — Real added code complexity and a small per-use overhead with no measured benefit if the component wasn't actually re-rendering unnecessarily or wasn't expensive to begin with — profiling first avoids optimizing a part of the app that was never actually the bottleneck.

**Sources:** [React — `lazy`](https://react.dev/reference/react/lazy), [React — Render and Commit](https://react.dev/learn/render-and-commit), [React DevTools — Profiler](https://react.dev/learn/react-developer-tools)

---

### 19. How Would You Approach State Management in a Large React Application?

**Core answer:**

"I'd separate state into categories first, since they call for different tools, rather than reaching for one library to hold everything. Local UI state (a toggle, a form's in-progress values, a dropdown's open/closed state) belongs in `useState`/`useReducer` on the component that owns it. State shared across a few related components belongs lifted up to their common ancestor, delivered via props or, if it needs to reach distant descendants, via Context. Genuinely global client state used broadly across the app (the current user, app-wide UI preferences) can go through Context if it changes infrequently, or a dedicated lightweight store (Zustand, Redux, and similar) if it changes frequently enough that Context's re-render-everything-on-change behavior (covered in the Context question) becomes a real cost. Server state — data fetched from an API, which has its own caching, staleness, and refetching concerns that don't map cleanly onto client state tools at all — is generally best handled by a dedicated data-fetching library (TanStack Query, SWR, or a framework's built-in equivalent) rather than manually reimplemented with `useState`/`useEffect`."

**Staff-level extension:**

The precise distinction worth being explicit about at Staff level is that server state and client state are genuinely different problems, not the same problem at different scales — server state has its own concerns (cache invalidation, background refetching, deduplicating identical in-flight requests, handling staleness) that a generic client-state tool like Redux or a plain Context wasn't designed to solve, and manually reimplementing them with `useState`/`useEffect` (a loading flag, an error state, a manual `useEffect` fetch, no caching or deduplication across components requesting the same data) reproduces a worse, unmaintained version of what a dedicated data-fetching library already provides. The judgment worth demonstrating, mirroring the equivalent NgRx-vs-Signal-service trade-off from the Angular guide, is not defaulting to the most powerful/global tool available — Redux's strict unidirectional flow and time-travel debugging are genuinely valuable for a large team needing enforced consistency across many features touching shared state, but that overhead isn't worth paying for state a Context or even local `useState` would handle perfectly well.

**Example:**

```jsx
// Server state: a dedicated data-fetching library handles caching, refetching,
// and loading/error state automatically — not reimplemented by hand
import { useQuery } from '@tanstack/react-query';

function UserProfile({ userId }) {
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetch(`/api/users/${userId}`).then(r => r.json()),
  });

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <p>{user.name}</p>;
}
```

**Follow-up questions:**

- *"Why not just fetch server data with `useEffect` and `useState`, the way it's often first taught?"* — That approach lacks caching (refetches on every mount, even for data another component already fetched), request deduplication, background refetching, and standardized loading/error state — a dedicated library provides all of this without hand-rolling and re-testing it per feature.
- *"What would specifically justify introducing Redux over Context plus local state?"* — A concrete need Context/local state can't cleanly meet — enforced unidirectional update patterns across a large team, time-travel debugging, or genuinely complex cross-feature state interactions — not "Redux is the standard choice" as a reason by itself.

**Sources:** [React — Managing State](https://react.dev/learn/managing-state), [TanStack Query — Overview](https://tanstack.com/query/latest/docs/framework/react/overview)

---

### 20. How Do You Test a React Component?

**Core answer:**

"React Testing Library is the standard tool for component-level tests, and its guiding philosophy is deliberately different from testing a component's internal implementation details: it encourages querying and interacting with a rendered component the way an actual user would — finding elements by their visible text, label, or accessibility role, rather than by internal state, prop values, or CSS class names — and asserting on what's visible in the rendered output, not on a component's internal variables. `render()` renders a component into a virtual DOM for testing; `screen.getByRole()`/`getByText()` and similar queries find elements the way a user or assistive technology would locate them; and `fireEvent`/`userEvent` (the latter more accurately simulating real browser event sequences) simulates user interactions like clicks and typing. This approach means a test keeps passing through internal refactors (renaming a state variable, restructuring how a component is composed internally) as long as the component's actual user-facing behavior hasn't changed — and, conversely, a test written this way should fail if the user-facing behavior breaks, even if the internal implementation looks unchanged."

**Staff-level extension:**

The precise philosophical reason "query by role/text, not by implementation detail" matters at Staff level, worth being able to articulate directly rather than just following the convention: a test that reaches into a component's internal state or queries by a CSS class name/`data-testid` used only for testing is coupled to implementation details a refactor is likely to change even when user-facing behavior is unaffected — which produces the exact false-positive test failure this guide's Testing guide's mock/stub question warns about in a different form: a test failing for a reason that doesn't indicate an actual bug, costing real time to investigate and eroding trust in the test suite. `userEvent` over `fireEvent` is the more Staff-level-aware default specifically because `fireEvent` dispatches a single, synthetic DOM event directly, while `userEvent` simulates the fuller, more realistic sequence of events a real browser interaction actually produces (focus, keydown, keypress, input, keyup for typing a character, for instance) — catching bugs tied to that fuller event sequence that a single synthetic event would miss entirely.

**Example:**

```jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';

function LoginForm({ onSubmit }) {
  const [username, setUsername] = React.useState('');
  return (
    <form onSubmit={e => { e.preventDefault(); onSubmit(username); }}>
      <label htmlFor="username">Username</label>
      <input id="username" value={username} onChange={e => setUsername(e.target.value)} />
      <button type="submit">Log in</button>
    </form>
  );
}

describe('LoginForm', () => {
  it('calls onSubmit with the typed username', async () => {
    const handleSubmit = vi.fn();
    render(<LoginForm onSubmit={handleSubmit} />);

    // Queries by ACCESSIBLE role/label — not by internal state or a CSS class
    await userEvent.type(screen.getByLabelText('Username'), 'alex');
    await userEvent.click(screen.getByRole('button', { name: 'Log in' }));

    expect(handleSubmit).toHaveBeenCalledWith('alex'); // asserts on observable BEHAVIOR, not internal state
  });
});
```

**Follow-up questions:**

- *"Why does React Testing Library discourage querying by CSS class name or component internal state?"* — Both are implementation details a refactor can change without any actual user-facing behavior changing — a test coupled to them can fail for reasons unrelated to a real bug, which wastes investigation time and erodes confidence in what a test failure actually means.
- *"What's a concrete case where `userEvent` catches a bug that `fireEvent` would miss?"* — A component relying on a `focus` or intermediate `keydown` event (some custom keyboard-shortcut handling, an input mask reacting mid-keystroke) — `fireEvent` dispatching only a single synthetic event skips those intermediate events entirely, while `userEvent` fires the fuller, realistic sequence a real user's interaction produces.

**Sources:** [React Testing Library — Guiding Principles](https://testing-library.com/docs/guiding-principles/), [Testing Library — `user-event`](https://testing-library.com/docs/user-event/intro/)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| React — Describing the UI | https://react.dev/learn/describing-the-ui |
| React — Render and Commit | https://react.dev/learn/render-and-commit |
| React — Writing Markup with JSX | https://react.dev/learn/writing-markup-with-jsx |
| React — JavaScript in JSX with Curly Braces | https://react.dev/learn/javascript-in-jsx-with-curly-braces |
| React — Passing Props to a Component | https://react.dev/learn/passing-props-to-a-component |
| React — Your First Component | https://react.dev/learn/your-first-component |
| React — `useState` | https://react.dev/reference/react/useState |
| React — Rules of Hooks | https://react.dev/warnings/invalid-hook-call-warning |
| React — Reacting to Input with State | https://react.dev/learn/reacting-to-input-with-state |
| React — Sharing State Between Components | https://react.dev/learn/sharing-state-between-components |
| React — Rendering Lists | https://react.dev/learn/rendering-lists |
| React — `useEffect` | https://react.dev/reference/react/useEffect |
| React — Synchronizing with Effects | https://react.dev/learn/synchronizing-with-effects |
| React — Lifecycle of Reactive Effects | https://react.dev/learn/lifecycle-of-reactive-effects |
| React — Passing Data Deeply with Context | https://react.dev/learn/passing-data-deeply-with-context |
| React — `useContext` | https://react.dev/reference/react/useContext |
| React — `useMemo` | https://react.dev/reference/react/useMemo |
| React — `useCallback` | https://react.dev/reference/react/useCallback |
| React — `memo` | https://react.dev/reference/react/memo |
| React — Reusing Logic with Custom Hooks | https://react.dev/learn/reusing-logic-with-custom-hooks |
| React — `useRef` | https://react.dev/reference/react/useRef |
| React — Manipulating the DOM with Refs | https://react.dev/learn/manipulating-the-dom-with-refs |
| React — v19 Release Notes (ref as a prop, Actions, etc.) | https://react.dev/blog/2024/12/05/react-19 |
| React — Preserving and Resetting State | https://react.dev/learn/preserving-and-resetting-state |
| React (GitHub) — Fiber Architecture | https://github.com/acdlite/react-fiber-architecture |
| React — `useTransition` | https://react.dev/reference/react/useTransition |
| React — `Suspense` | https://react.dev/reference/react/Suspense |
| React — React 18 Concurrent Features | https://react.dev/blog/2022/03/29/react-v18 |
| React Compiler — Introduction | https://react.dev/learn/react-compiler |
| React — React Compiler v1.0 Announcement | https://react.dev/blog/2025/10/07/react-compiler-1 |
| React — Server Components | https://react.dev/reference/rsc/server-components |
| React — `'use client'` | https://react.dev/reference/rsc/use-client |
| React — `useActionState` | https://react.dev/reference/react/useActionState |
| React — `useFormStatus` | https://react.dev/reference/react-dom/hooks/useFormStatus |
| React — Managing State | https://react.dev/learn/managing-state |
| TanStack Query — Overview | https://tanstack.com/query/latest/docs/framework/react/overview |
| React Testing Library — Guiding Principles | https://testing-library.com/docs/guiding-principles/ |
| Testing Library — `user-event` | https://testing-library.com/docs/user-event/intro/ |
