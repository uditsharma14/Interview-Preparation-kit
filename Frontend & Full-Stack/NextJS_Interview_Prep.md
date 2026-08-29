# Next.js — Interview Prep (Intermediate Level, with Code & Sources)

> **Target level:** Intermediate · **Baseline:** Next.js 15+, App Router (the current default; the older Pages Router is noted where it still matters) · **Last verified:** 2026-08-29 · **Prerequisites:** [React Interview Prep](React_Interview_Prep.md) — this guide assumes you already know components, hooks, and the virtual DOM, and focuses on what Next.js adds on top

How to use this: each question has an **Answer** you could actually say out loud in an interview, a **Code** example to back it up, a **Follow-up** covering what an interviewer typically asks next, and a **Source**. This is pitched at an intermediate level — enough to hold a real conversation about how Next.js apps are structured and deployed, not a deep dive into the framework's internals. A quick note on versions, since this area of Next.js changed recently: in Next.js 15, `params` and `searchParams` became `Promise`s you have to `await` — a lot of tutorials and existing code out there still show the older, synchronous version from Next.js 13/14. This guide uses the current, async style throughout.

<!-- toc -->
## Table of Contents

- [1. What Is Next.js, and What Does It Add on Top of React?](#1-what-is-nextjs-and-what-does-it-add-on-top-of-react)
- [2. How Does File-Based Routing Work in the App Router?](#2-how-does-file-based-routing-work-in-the-app-router)
- [3. What's the Difference Between the App Router and the Pages Router?](#3-whats-the-difference-between-the-app-router-and-the-pages-router)
- [4. How Do Dynamic Routes Work?](#4-how-do-dynamic-routes-work)
- [5. What Are Layouts, and How Do They Differ From Pages?](#5-what-are-layouts-and-how-do-they-differ-from-pages)
- [6. Compare Server-Side Rendering, Static Generation, and Incremental Static Regeneration](#6-compare-server-side-rendering-static-generation-and-incremental-static-regeneration)
- [7. What Are Server Components, and How Do They Differ From Client Components?](#7-what-are-server-components-and-how-do-they-differ-from-client-components)
- [8. When Do You Need "use client", and What Happens If You Forget It?](#8-when-do-you-need-use-client-and-what-happens-if-you-forget-it)
- [9. What Are Route Handlers, and How Do You Build One?](#9-what-are-route-handlers-and-how-do-you-build-one)
- [10. How Does Data Fetching and Caching Work in the App Router?](#10-how-does-data-fetching-and-caching-work-in-the-app-router)
- [11. What Is Middleware, and What's It Used For?](#11-what-is-middleware-and-whats-it-used-for)
- [12. How Would You Deploy a Next.js App?](#12-how-would-you-deploy-a-nextjs-app)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## 1. What Is Next.js, and What Does It Add on Top of React?

**Answer:**

"React on its own is a UI library — it renders components, but it doesn't tell you how to route between pages, how to fetch data, or how to actually ship the app. Next.js is a framework built on top of React that answers those questions with real, opinionated defaults: file-based routing, a choice between rendering on the server or the client per route, built-in code splitting and image/font optimization, and a production build pipeline.

The core value is that most of what a real app needs — routing, data fetching, bundling, deployment — comes preconfigured instead of being assembled from a dozen separate libraries. You can still drop down to plain React patterns where you need to, but you're not starting from a blank slate."

**Code:**

```bash
npx create-next-app@latest my-app
cd my-app
npm run dev   # starts the dev server, usually at localhost:3000
```

**Follow-up:**

I'd expect a follow-up like "why not just use React with React Router and Webpack yourself?" — the honest answer is you can, and plenty of teams do for apps that don't need server rendering at all. Next.js earns its place specifically when you want a mix of statically generated pages, server-rendered pages, and API endpoints in one project, with the routing and rendering strategy decided per-route instead of for the whole app.

**Source:** [Next.js — Introduction](https://nextjs.org/docs/app/getting-started/installation)

---

## 2. How Does File-Based Routing Work in the App Router?

**Answer:**

"Routes are defined by folders inside the `app` directory, not by a routing library you configure yourself. A folder maps to a URL segment, and a few special file names inside that folder give it behavior: `page.tsx` makes the segment a public, navigable route, and `layout.tsx` defines UI shared across that segment and everything nested under it. So `app/page.tsx` is your homepage (`/`), and `app/blog/page.tsx` is `/blog` — you don't register these routes anywhere, the folder structure is the routing table.

Layouts nest automatically. A layout at `app/layout.tsx` wraps everything in the app; a layout at `app/blog/layout.tsx` wraps only the blog section, inside the root layout. That nesting also means layouts don't re-render on navigation between pages that share them — only the page content underneath changes."

**Code:**

```text
app/
├── layout.tsx          -> root layout, wraps EVERYTHING
├── page.tsx             -> route: /
├── blog/
│   ├── layout.tsx        -> wraps only routes under /blog
│   ├── page.tsx           -> route: /blog
│   └── [slug]/
│       └── page.tsx        -> route: /blog/some-post-title
└── about/
    └── page.tsx          -> route: /about
```

```tsx
// app/blog/page.tsx
export default async function BlogPage() {
  const posts = await getPosts(); // runs on the server, no useEffect needed
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

**Follow-up:**

A common follow-up is "does every file in `app` become a route?" — no, only `page.tsx` files do. You can have plain component files, utility files, or a `components/` folder inside `app` without them turning into routes; Next.js only treats the specific reserved file names (`page`, `layout`, `route`, `loading`, `error`, and a handful of others) as special.

**Source:** [Next.js — Layouts and Pages](https://nextjs.org/docs/app/getting-started/layouts-and-pages)

---

## 3. What's the Difference Between the App Router and the Pages Router?

**Answer:**

"The Pages Router is the original Next.js routing system, based on a `pages` directory where each file is a route (`pages/blog/[slug].js` maps to `/blog/:slug`). Data fetching used exported functions like `getServerSideProps` or `getStaticProps`, and every component was a Client Component by default — rendered on the server for the initial load, then hydrated and treated like ordinary React on the client.

The App Router, introduced in Next.js 13 and the default since Next.js 13.4, replaced this with the `app` directory. It's built around React Server Components (question 7) instead of the old data-fetching functions — you fetch data directly inside an `async` component instead of exporting a special function next to it. It also adds nested layouts, streaming, and more granular control over caching per route. The Pages Router still works and is still supported, but new projects use the App Router, and that's what most interview questions and current tutorials assume."

**Code:**

```text
Pages Router (older):
  pages/blog/[slug].js
    export async function getServerSideProps({ params }) { ... }
    export default function Post({ post }) { ... }

App Router (current):
  app/blog/[slug]/page.tsx
    export default async function Post({ params }) {
      const { slug } = await params;
      const post = await getPost(slug); // fetched directly, no separate function
      return <article>{post.title}</article>;
    }
```

**Follow-up:**

If asked "would you migrate an existing Pages Router app," the honest answer is: not all at once. Next.js supports both routers side by side in the same project, so a real migration usually moves one route at a time, starting with pages that don't depend heavily on Pages-Router-specific APIs.

**Source:** [Next.js — App Router vs Pages Router](https://nextjs.org/docs/app/building-your-application/upgrading/app-router-migration)

---

## 4. How Do Dynamic Routes Work?

**Answer:**

"A folder name wrapped in square brackets creates a dynamic segment that matches any value at that position in the URL. `app/blog/[slug]/page.tsx` matches `/blog/hello-world`, `/blog/anything`, and so on, and the actual value is handed to the page as a `params` prop.

There are two variants worth knowing beyond the basic `[slug]`. A catch-all segment, `[...slug]`, matches one or more path segments and gives you an array — `/blog/2024/08/post` would give `slug: ['2024', '08', 'post']`. An optional catch-all, `[[...slug]]`, does the same thing but also matches the route with no extra segments at all, so `/blog` itself matches too, with an empty array."

**Code:**

```tsx
// app/blog/[slug]/page.tsx  -->  matches /blog/anything
export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params; // params is a Promise since Next.js 15
  return <h1>Post: {slug}</h1>;
}

// app/shop/[...slug]/page.tsx  -->  matches /shop/a/b/c
export default async function ShopPage({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}) {
  const { slug } = await params; // e.g. ['a', 'b', 'c']
  return <p>Category path: {slug.join(' / ')}</p>;
}
```

**Follow-up:**

A likely follow-up is how to pre-render specific dynamic routes at build time instead of generating them on every request — that's what `generateStaticParams` is for (question 6 covers the rendering-strategy side of this directly). It's an exported function next to the page that returns the list of param values Next.js should build pages for ahead of time.

**Source:** [Next.js — Dynamic Routes](https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes)

---

## 5. What Are Layouts, and How Do They Differ From Pages?

**Answer:**

"A page is the actual content for one specific route — a `page.tsx` file renders when someone navigates to that exact URL. A layout is UI shared across a page and everything nested below it — a nav bar, a sidebar, a footer — and it wraps its children through a `children` prop, the same way any React component would.

The important behavioral difference: layouts persist across navigation. If two routes share a layout, navigating between them doesn't remount or re-render that layout — only the page content inside it changes. That's genuinely useful for things like a sidebar that shouldn't flicker or lose its scroll position every time you click a link, and it also means a layout can't access the specific page's data directly; it only receives whatever `children` React gives it to render."

**Code:**

```tsx
// app/dashboard/layout.tsx — shared across every route under /dashboard
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      <Sidebar />
      <main>{children}</main>
    </div>
  );
}
```

**Follow-up:**

I'd expect a question like "can a layout re-fetch data on every navigation?" — no, not by default, and that's the point. If you need something to update on every navigation (a page title, a breadcrumb), that piece of UI usually belongs in the page itself, not the layout, precisely because the layout is deliberately not remounted.

**Source:** [Next.js — Layouts and Pages](https://nextjs.org/docs/app/getting-started/layouts-and-pages)

---

## 6. Compare Server-Side Rendering, Static Generation, and Incremental Static Regeneration

**Answer:**

"These are three different answers to 'when does the HTML for this page actually get generated.'

**Static Generation (SSG)** generates the HTML once, at build time. Every visitor gets the same pre-built page, served instantly from a CDN — great for content that doesn't change per request, like a marketing page or a blog post that isn't updated constantly.

**Server-Side Rendering (SSR)** generates the HTML on every request, on the server, using whatever's current at that exact moment — necessary for a page that has to reflect live, per-user, or frequently-changing data, at the cost of a server round trip on every visit instead of an instant cached response.

**Incremental Static Regeneration (ISR)** is the middle ground: the page is statically generated like SSG, but with a `revalidate` time attached. The first request after that time window serves the existing (now stale) cached page immediately, while Next.js regenerates a fresh version in the background — the next visitor after that gets the updated page. You get SSG's speed most of the time, without a full rebuild every time the underlying content changes."

**Code:**

```tsx
// SSG (default): no revalidate, no dynamic data source — built once at build time
export default async function AboutPage() {
  return <p>About us — this content is fixed at build time.</p>;
}

// ISR: revalidate every 60 seconds
export const revalidate = 60;

export default async function BlogPage() {
  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());
  return <PostList posts={posts} />;
}

// SSR: forcing dynamic rendering on every request
export const dynamic = 'force-dynamic';

export default async function DashboardPage() {
  const liveStats = await getLiveStats(); // needs to be fresh on every load
  return <Stats data={liveStats} />;
}
```

**Follow-up:**

A good follow-up is "how does Next.js decide which one to use if you don't specify anything?" — it infers it. If a route (or any `fetch` call inside it) doesn't touch anything request-specific — no cookies, no headers, no uncached `fetch` — Next.js renders it statically by default. The moment it detects something that requires a live request (reading `cookies()`, an uncached fetch, `searchParams` in some cases), it switches that route to dynamic rendering automatically.

**Source:** [Next.js — Incremental Static Regeneration](https://nextjs.org/docs/app/guides/incremental-static-regeneration)

---

## 7. What Are Server Components, and How Do They Differ From Client Components?

**Answer:**

"In the App Router, every component is a Server Component by default. A Server Component renders on the server, can directly `await` data (a database call, a `fetch`, a file read) with no `useEffect` or loading state needed, and never ships its own JavaScript to the browser — the client only receives the rendered output. That makes them a good default for content that doesn't need interactivity: a blog post, a product page, a dashboard's static layout.

A Client Component is what React has always given you — it can use `useState`, `useEffect`, event handlers, and browser-only APIs like `localStorage`, but it does ship JavaScript to the browser and has to be explicitly opted into with a `'use client'` directive (question 8). The two compose together: a Server Component can render a Client Component and pass it data as props, but a Server Component can't be imported *into* a Client Component's own module tree — only passed to it as `children` or a prop."

**Code:**

```tsx
// app/product/[id]/page.tsx — Server Component (default, no directive needed)
import AddToCartButton from './add-to-cart-button';

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const product = await getProduct(id); // direct await, runs on the server

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <AddToCartButton productId={product.id} /> {/* a Client Component */}
    </div>
  );
}
```

```tsx
// app/product/[id]/add-to-cart-button.tsx — Client Component
'use client';

import { useState } from 'react';

export default function AddToCartButton({ productId }: { productId: string }) {
  const [added, setAdded] = useState(false);
  return (
    <button onClick={() => setAdded(true)}>
      {added ? 'Added!' : 'Add to Cart'}
    </button>
  );
}
```

**Follow-up:**

I'd expect "why does this matter for performance?" — because JavaScript that never needed to reach the browser, doesn't. A page built almost entirely from Server Components, with a small interactive island (like the button above) as a Client Component, ships a much smaller JavaScript bundle than a page where the whole thing is a Client Component just because one button needed `onClick`.

**Source:** [Next.js — Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components)

---

## 8. When Do You Need "use client", and What Happens If You Forget It?

**Answer:**

"You need `'use client'` the moment a component uses something that only exists in the browser or only makes sense on the client: `useState`, `useEffect`, event handlers like `onClick`, or browser APIs like `window` or `localStorage`. The directive goes at the very top of the file, above the imports, and it marks a boundary — everything that file imports and directly renders becomes part of the client bundle too, not just that one component.

If you forget it and try to use `useState` in a component that's still a Server Component by default, you get a build-time error, not a silent bug — Next.js won't let a Server Component use client-only hooks, so this fails loudly and early rather than shipping broken code."

**Code:**

```tsx
// Missing 'use client' — this will fail to build
import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0); // ERROR: useState only works
  return <button onClick={() => setCount(count + 1)}>{count}</button>; // in Client Components
}
```

```tsx
// Fixed
'use client';

import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

**Follow-up:**

A common follow-up: "should you put `'use client'` at the top of your whole app to avoid thinking about this?" — no, and doing that defeats most of the benefit. The recommended pattern is to push `'use client'` as far down the component tree as possible — mark only the specific interactive piece (a button, a form, a dropdown) as a Client Component, and keep everything around it as Server Components by default.

**Source:** [Next.js — Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components)

---

## 9. What Are Route Handlers, and How Do You Build One?

**Answer:**

"Route Handlers are how you build API endpoints in the App Router — the App Router's replacement for the old `pages/api` routes. You create a `route.ts` file inside a folder under `app`, and export a function named after the HTTP method you want to handle: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`. They're built on the standard Web `Request`/`Response` APIs, not a Next.js-specific request object, so the code looks close to plain server-side JavaScript.

One structural rule worth knowing: a route segment can have a `page.tsx` (rendering UI) or a `route.ts` (handling API requests), but not both at the same segment — they'd conflict on what that URL is supposed to return."

**Code:**

```ts
// app/api/posts/route.ts
export async function GET() {
  const posts = await getPosts();
  return Response.json(posts);
}

export async function POST(request: Request) {
  const body = await request.json();
  const newPost = await createPost(body);
  return Response.json(newPost, { status: 201 });
}
```

```ts
// app/api/posts/[id]/route.ts — dynamic segment, same as pages
export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const post = await getPost(id);
  if (!post) return new Response('Not found', { status: 404 });
  return Response.json(post);
}
```

**Follow-up:**

If asked "how is this different from a Server Action," the distinction is: a Route Handler is a real HTTP endpoint, reachable from outside the app (a mobile client, a webhook from a third-party service, `curl`) — a Server Action is a function you call directly from a React component, and Next.js handles turning that into a request under the hood without you defining a separate route for it. Use Route Handlers when something external needs to call you; use Server Actions when the caller is your own UI.

**Source:** [Next.js — Route Handlers](https://nextjs.org/docs/app/api-reference/file-conventions/route)

---

## 10. How Does Data Fetching and Caching Work in the App Router?

**Answer:**

"Data fetching in the App Router is just `await` inside an `async` Server Component — no special hook, no `getServerSideProps`. What makes it more than plain `fetch`, though, is that Next.js extends the `fetch` API with its own caching behavior: by default, a `fetch` call's result can be cached and reused across requests, and you control that caching per call.

`fetch(url)` with no options caches indefinitely, until something explicitly invalidates it. `fetch(url, { next: { revalidate: 60 } })` caches it but revalidates after 60 seconds — the same idea as ISR (question 6), just scoped to one specific fetch instead of the whole page. `fetch(url, { cache: 'no-store' })` opts that specific call out of caching entirely, fetching fresh data every time. And you can invalidate cached data on demand — after a mutation, say — with `revalidatePath()` or `revalidateTag()` rather than waiting for a timer."

**Code:**

```tsx
// Cached indefinitely (default)
const staticData = await fetch('https://api.example.com/config');

// Revalidated every 60 seconds
const posts = await fetch('https://api.example.com/posts', {
  next: { revalidate: 60 },
});

// Never cached — always fresh
const liveScore = await fetch('https://api.example.com/live-score', {
  cache: 'no-store',
});
```

```ts
// app/actions.ts — invalidate on demand after a mutation, instead of waiting
'use server';

import { revalidatePath } from 'next/cache';

export async function createPost(data: FormData) {
  await savePost(data);
  revalidatePath('/blog'); // next visit to /blog gets fresh data immediately
}
```

**Follow-up:**

A good follow-up is "what if you're not using `fetch` at all — say, querying a database directly with an ORM?" — Next.js's extended caching only wraps `fetch`. For a database call, you'd wrap it yourself with `unstable_cache` (or just not cache it, if the data genuinely needs to be fresh on every request) to get equivalent time-based or tag-based revalidation.

**Source:** [Next.js — Caching and Revalidating](https://nextjs.org/docs/app/getting-started/caching)

---

## 11. What Is Middleware, and What's It Used For?

**Answer:**

"Middleware is code that runs before a request completes, ahead of any route's actual page or handler — defined in a single `middleware.ts` file at the root of the project (or inside `src/`). It gets the incoming request and can inspect it, redirect, rewrite the URL, modify headers, or let it continue on to the actual route unchanged.

The most common real uses: redirecting unauthenticated users away from protected routes before the page even starts rendering, A/B testing by rewriting some requests to a different route transparently, and geolocation-based redirects (sending a request to a locale-specific path based on the visitor's country). A `matcher` config lets you scope which routes middleware actually runs on, since running it on every single request — including static assets — would be wasteful."

**Code:**

```ts
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const isLoggedIn = request.cookies.has('session');

  if (!isLoggedIn && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next(); // let the request through unchanged
}

export const config = {
  matcher: ['/dashboard/:path*'], // only runs middleware for these routes
};
```

**Follow-up:**

I'd expect "can middleware read a database or call a slow API?" — you can, but it should be fast and lightweight, since it runs on every matched request before the actual page even starts. Middleware runs on the Edge Runtime by default, which is a deliberately restricted environment (no full Node.js API surface) built for exactly this kind of quick, low-latency check — not for heavy business logic.

**Source:** [Next.js — Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)

---

## 12. How Would You Deploy a Next.js App?

**Answer:**

"There are a few real options, and the right one depends on whether you need every Next.js feature or can live with a subset. A **Node.js server** — running `next build` then `next start` — supports every feature (SSR, ISR, Route Handlers, Middleware) and can be deployed to any host that runs Node, from a plain VM to a platform like Railway or Render. A **Docker container** gives you the same full feature support, packaged for any container-based infrastructure, including Kubernetes. A **static export** (`output: 'export'`) builds the app down to plain HTML/CSS/JS with no Node server at all, deployable to something as simple as S3 or GitHub Pages — but it gives up everything that needs a live server: SSR, ISR, Route Handlers, and Middleware all stop working, since there's no server left to run them.

**Vercel** (the company behind Next.js) is a managed platform built specifically around Next.js, and it's the path of least resistance — it deploys straight from a git push, supports every feature without configuration, and runs Middleware and some routes on its Edge Network automatically. It's not the only option, but it's worth knowing why it's the default recommendation: it's maintained by the same team building the framework, so new features tend to work there first."

**Code:**

```json
// package.json — required for a self-hosted Node.js deployment
{
  "scripts": {
    "build": "next build",
    "start": "next start"
  }
}
```

```js
// next.config.js — opting into a static export (drops SSR/ISR/Route Handlers)
module.exports = {
  output: 'export',
};
```

**Follow-up:**

If asked "when would you *not* use Vercel," the honest cases are: a company with a hard requirement to run everything on its own infrastructure (compliance, existing Kubernetes investment, cost at very large scale), or a team already standardized on a different cloud provider where a Docker-based deployment fits their existing pipeline more naturally than adopting a new platform.

**Source:** [Next.js — Deploying](https://nextjs.org/docs/app/getting-started/deploying)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Next.js — Installation | https://nextjs.org/docs/app/getting-started/installation |
| Next.js — Layouts and Pages | https://nextjs.org/docs/app/getting-started/layouts-and-pages |
| Next.js — App Router vs Pages Router Migration | https://nextjs.org/docs/app/building-your-application/upgrading/app-router-migration |
| Next.js — Dynamic Routes | https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes |
| Next.js — Incremental Static Regeneration | https://nextjs.org/docs/app/guides/incremental-static-regeneration |
| Next.js — Server and Client Components | https://nextjs.org/docs/app/getting-started/server-and-client-components |
| Next.js — Route Handlers | https://nextjs.org/docs/app/api-reference/file-conventions/route |
| Next.js — Caching and Revalidating | https://nextjs.org/docs/app/getting-started/caching |
| Next.js — Middleware | https://nextjs.org/docs/app/building-your-application/routing/middleware |
| Next.js — Deploying | https://nextjs.org/docs/app/getting-started/deploying |
