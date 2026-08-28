# Spring Security & OAuth2 — Interview Prep, Basic to Staff Level (with Code & Sources)

> **Target level:** Basic → Staff (graduated — see below) · **Baseline:** Spring Security 6.x (`SecurityFilterChain` bean-based configuration), Spring Boot 3.x, OAuth 2.0 / OpenID Connect · **Last verified:** 2026-08-23 · **Prerequisites:** [Spring Boot Internals](Spring_Boot_Internals_Interview_Prep.md) for the Basic section; the Intermediate section onward assumes the Basic section's authentication/authorization fundamentals

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **code snippet** you could sketch on a whiteboard or IDE to back it up, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar is explaining the actual security model and its failure modes, not naming annotations. Questions are grouped by level (Basic → Intermediate → Staff) so you can calibrate depth to the interview you're prepping for; the later sections assume the earlier ones as background and don't re-explain them.

<!-- toc -->
## Table of Contents

- [Basic](#basic)
  - [1. What Is Spring Security, and What Does `@EnableWebSecurity` Actually Do?](#1-what-is-spring-security-and-what-does-enablewebsecurity-actually-do)
  - [2. What Is a `UserDetailsService`, and How Does Spring Security Use It?](#2-what-is-a-userdetailsservice-and-how-does-spring-security-use-it)
  - [3. What's the Difference Between Basic Authentication and Form-Based Login?](#3-whats-the-difference-between-basic-authentication-and-form-based-login)
  - [4. Why Does Spring Security Hash Passwords, and What Is `BCryptPasswordEncoder`?](#4-why-does-spring-security-hash-passwords-and-what-is-bcryptpasswordencoder)
  - [5. What's the Difference Between a Cookie and a Session, Mechanically?](#5-whats-the-difference-between-a-cookie-and-a-session-mechanically)
  - [6. What Is HTTPS/TLS, and Why Does It Matter for Authentication?](#6-what-is-httpstls-and-why-does-it-matter-for-authentication)
  - [7. What Is Role-Based Access Control, and How Do You Express It With `@PreAuthorize`/`hasRole()`?](#7-what-is-role-based-access-control-and-how-do-you-express-it-with-preauthorizehasrole)
- [Intermediate](#intermediate)
  - [8. What's the Difference Between `hasRole()` and `hasAuthority()`?](#8-whats-the-difference-between-hasrole-and-hasauthority)
  - [9. What Is a JWT, Structurally?](#9-what-is-a-jwt-structurally)
  - [10. What Do `permitAll()`, `authenticated()`, and `denyAll()` Mean in a `SecurityFilterChain`?](#10-what-do-permitall-authenticated-and-denyall-mean-in-a-securityfilterchain)
  - [11. What Is CSRF, at a Basic Level?](#11-what-is-csrf-at-a-basic-level)
  - [12. What Does an `AuthenticationEntryPoint` Do When a Request Is Unauthenticated?](#12-what-does-an-authenticationentrypoint-do-when-a-request-is-unauthenticated)
- [Staff Level](#staff-level)
  - [13. Explain the Spring Security Filter Chain From Request Entry to Authorization](#13-explain-the-spring-security-filter-chain-from-request-entry-to-authorization)
  - [14. How Are Authentication and Authorization Different?](#14-how-are-authentication-and-authorization-different)
  - [15. Explain `SecurityContext`, `Authentication`, `GrantedAuthority`, and `AuthenticationProvider`](#15-explain-securitycontext-authentication-grantedauthority-and-authenticationprovider)
  - [16. How Does Spring Choose Among Multiple `SecurityFilterChain` Beans?](#16-how-does-spring-choose-among-multiple-securityfilterchain-beans)
  - [17. What Is the Difference Between Request-Level and Method-Level Authorization?](#17-what-is-the-difference-between-request-level-and-method-level-authorization)
  - [18. Why Does Method-Security Self-Invocation Cause Problems?](#18-why-does-method-security-self-invocation-cause-problems)
  - [19. When Should CSRF Protection Be Enabled or Disabled?](#19-when-should-csrf-protection-be-enabled-or-disabled)
  - [20. Compare CORS and CSRF. Why Does Configuring One Not Solve the Other?](#20-compare-cors-and-csrf-why-does-configuring-one-not-solve-the-other)
  - [21. Compare Session-Based Authentication and Bearer-Token Authentication](#21-compare-session-based-authentication-and-bearer-token-authentication)
  - [22. Explain OAuth 2.0 Authorization-Code Flow With PKCE](#22-explain-oauth-20-authorization-code-flow-with-pkce)
  - [23. Why Is the Resource-Owner Password Flow Deprecated?](#23-why-is-the-resource-owner-password-flow-deprecated)
  - [24. What Are the Roles of the Resource Owner, Client, Authorization Server, and Resource Server?](#24-what-are-the-roles-of-the-resource-owner-client-authorization-server-and-resource-server)
  - [25. Compare Access Tokens, Refresh Tokens, and ID Tokens](#25-compare-access-tokens-refresh-tokens-and-id-tokens)
  - [26. What Is the Difference Between OAuth 2.0 and OpenID Connect?](#26-what-is-the-difference-between-oauth-20-and-openid-connect)
  - [27. Compare Opaque Tokens and JWT Access Tokens](#27-compare-opaque-tokens-and-jwt-access-tokens)
  - [28. How Does a Resource Server Validate a JWT?](#28-how-does-a-resource-server-validate-a-jwt)
  - [29. How Should Services Handle Signing-Key Rotation?](#29-how-should-services-handle-signing-key-rotation)
  - [30. What Are `iss`, `aud`, `exp`, `nbf`, `jti`, and `kid` Used For?](#30-what-are-iss-aud-exp-nbf-jti-and-kid-used-for)
  - [31. Why Is Revoking a JWT Difficult? What Strategies Are Available?](#31-why-is-revoking-a-jwt-difficult-what-strategies-are-available)
  - [32. Where Should Tokens Be Stored in a Browser Application?](#32-where-should-tokens-be-stored-in-a-browser-application)
  - [33. How Do Refresh-Token Rotation and Reuse Detection Work?](#33-how-do-refresh-token-rotation-and-reuse-detection-work)
  - [34. How Would You Secure Service-to-Service Communication?](#34-how-would-you-secure-service-to-service-communication)
  - [35. How Would You Model Scopes, Roles, Permissions, and Tenant Boundaries?](#35-how-would-you-model-scopes-roles-permissions-and-tenant-boundaries)
  - [36. How Do You Prevent Broken Object-Level Authorization?](#36-how-do-you-prevent-broken-object-level-authorization)
  - [37. How Should Authentication Context Propagate Through Asynchronous Processing?](#37-how-should-authentication-context-propagate-through-asynchronous-processing)
  - [38. How Would You Design Authorization for Kafka Consumers Where There Is No HTTP Request?](#38-how-would-you-design-authorization-for-kafka-consumers-where-there-is-no-http-request)
  - [39. How Do You Prevent Confused-Deputy Problems in Downstream Service Calls?](#39-how-do-you-prevent-confused-deputy-problems-in-downstream-service-calls)
  - [40. What Security Information Is Safe to Log?](#40-what-security-information-is-safe-to-log)
  - [41. How Would You Investigate Intermittent `401` Versus `403` Responses?](#41-how-would-you-investigate-intermittent-401-versus-403-responses)
  - [42. Design an Authentication and Authorization Architecture for a Multi-Tenant Platform](#42-design-an-authentication-and-authorization-architecture-for-a-multi-tenant-platform)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## Basic

### 1. What Is Spring Security, and What Does `@EnableWebSecurity` Actually Do?

**Answer:**

"Spring Security handles authentication (confirming who a caller is) and authorization (deciding what they're allowed to do). Under the hood it's a chain of servlet filters that intercept every incoming HTTP request before it reaches your application code — more on that later in this guide. In modern Spring Boot, just adding the `spring-boot-starter-security` dependency already turns Spring Security on with sensible defaults: every endpoint requires authentication, you get a generated login form, and a random default password gets logged at startup. So `@EnableWebSecurity` isn't actually required to turn security on. Its real job is signaling that you're providing **custom** security configuration — your own `SecurityFilterChain` bean — instead of accepting the defaults, and it wires up Spring MVC integration hooks like resolving `Authentication` as a controller method argument.

The actual security rules — which endpoints need authentication, what login mechanism to use — get configured via a `SecurityFilterChain` bean, which we'll get to next. Not via `@EnableWebSecurity` itself."

**Code:**

```java
// Spring Boot 3.x — @EnableWebSecurity is often implicit via auto-configuration once
// spring-boot-starter-security is on the classpath, but explicit custom config looks like this:
@Configuration
@EnableWebSecurity // signals: custom security config follows, don't just use the defaults
class SecurityConfig {
    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .anyRequest().authenticated());
        return http.build();
    }
}
```

**Follow-up:**

Adding the security starter with zero configuration is a fine way to quickly confirm Spring Security is active — every endpoint immediately requires authentication, so you know the filter chain is running. But it's never a real production setup. Real applications need a custom `SecurityFilterChain` to say which endpoints are actually public, which authentication mechanism to use, and how authorization should work — which is what the rest of this guide covers.

**Source:** [Spring Security Reference — Getting Started](https://docs.spring.io/spring-security/reference/servlet/getting-started.html)

---

### 2. What Is a `UserDetailsService`, and How Does Spring Security Use It?

**Answer:**

"`UserDetailsService` is the interface Spring Security uses to load a user's credentials and authorities given a username. It's a single method, `loadUserByUsername(String username)`, that returns a `UserDetails` object with the username, the hashed password, and the user's granted authorities/roles. During username/password authentication, `DaoAuthenticationProvider` calls this method to fetch the stored user record, then hashes the submitted password and compares it against the stored hash. `UserDetailsService` itself doesn't do that comparison — it's just responsible for retrieving the user's data from wherever it lives, whether that's a database, an LDAP directory, or an in-memory list for testing.

In a real application you write your own implementation backed by your actual user store, typically a Spring Data repository querying a `users` table. Spring Security ships basic in-memory and JDBC-based implementations too, but those are mainly for prototyping and testing, not a production user base."

**Code:**

```java
@Component
class DatabaseUserDetailsService implements UserDetailsService {
    private final UserRepository userRepository;

    DatabaseUserDetailsService(UserRepository userRepository) { this.userRepository = userRepository; }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException("No user: " + username));
        return org.springframework.security.core.userdetails.User
            .withUsername(user.getUsername())
            .password(user.getHashedPassword()) // already hashed — never store or return plaintext
            .authorities(user.getRoles())
            .build();
    }
}
```

**Follow-up:**

One thing worth flagging: `UserDetailsService` is tied specifically to the username/password flow. It plays no role at all in OAuth2/JWT authentication, where the resource server validates a token issued by a separate authorization server instead of looking up credentials locally. Expecting `UserDetailsService` to somehow be involved in JWT validation is a common early confusion — they're genuinely separate mechanisms, covered in different parts of this guide.

**Source:** [Spring Security Reference — `UserDetailsService`](https://docs.spring.io/spring-security/reference/servlet/authentication/passwords/user-details-service.html)

---

### 3. What's the Difference Between Basic Authentication and Form-Based Login?

**Answer:**

"**HTTP Basic authentication** sends credentials on every single request, base64-encoded in the `Authorization: Basic <credentials>` header. Base64 isn't encryption — it's trivially reversible — so this absolutely requires HTTPS. The browser's built-in credential prompt handles collecting the credentials, with no custom login page involved. It's stateless and simple, which makes it a reasonable fit for machine-to-machine or API-client scenarios, but a poor fit for an end-user-facing web app: there's no real logout (the browser just keeps resending cached credentials), and the built-in prompt isn't customizable at all.

**Form-based login** presents a proper HTML login form. On successful submission, the server creates a session (or issues a token) and typically sets a session cookie, so subsequent requests carry that identifier instead of resending raw credentials every time. This is the standard pattern for browser-based apps — it supports a real logout, a customizable UI, and doesn't require re-sending the password on every request."

**Code:**

```java
// Basic Auth — credentials on EVERY request, base64-encoded (NOT encrypted)
http.httpBasic(Customizer.withDefaults());
// curl -u username:password https://api.example.com/orders
// -> Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=  (trivially decodable — HTTPS is mandatory)

// Form login — credentials submitted ONCE, then a session cookie carries subsequent requests
http.formLogin(form -> form.loginPage("/login").permitAll());
```

**Follow-up:**

Both of these are increasingly the "legacy" pattern beyond a simple internal tool or a quick API-client integration. Modern applications — especially anything with a separate frontend/mobile client or third-party integrations — lean toward OAuth2/OpenID Connect and bearer tokens instead, covered later in this guide. Token-based auth decouples the authentication mechanism from the resource server and supports delegated access (a third-party app acting on a user's behalf) in a way neither Basic Auth nor session-based form login was designed for.

**Source:** [Spring Security Reference — Basic Authentication](https://docs.spring.io/spring-security/reference/servlet/authentication/passwords/basic.html), [Spring Security Reference — Form Login](https://docs.spring.io/spring-security/reference/servlet/authentication/passwords/form.html)

---

### 4. Why Does Spring Security Hash Passwords, and What Is `BCryptPasswordEncoder`?

**Answer:**

"If a password is stored in plaintext, anyone with database access — an attacker who breaches it, a rogue insider, a misconfigured backup — has every user's actual password immediately. And since people reuse passwords across services, one breach compromises accounts on completely unrelated systems too. Hashing turns the password into a one-way-derived value: you can't feasibly recover the original from the hash, but you can verify a later login attempt by hashing the submitted password the same way and comparing.

`BCryptPasswordEncoder` is Spring Security's standard implementation of bcrypt, a deliberately slow, salted hashing algorithm. "Slow" is the actual point, not a flaw. A fast hash like plain SHA-256 lets an attacker who steals the hash database try billions of password guesses per second on cheap hardware. Bcrypt's deliberate computational cost — tunable via its work-factor parameter — makes brute-forcing dramatically more expensive, without meaningfully slowing down the one legitimate hash-and-compare a real login does. It also automatically generates and embeds a random salt per password, so two users with the identical password get completely different stored hashes, which defeats precomputed rainbow-table attacks."

**Code:**

```java
@Bean
PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(); // default strength (work factor) of 10
}

// Registering a new user — HASH before storing, never store the raw password:
String hashed = passwordEncoder.encode(rawPassword);
userRepository.save(new User(username, hashed));

// Verifying a login attempt — compare, don't decrypt (bcrypt hashes can't be reversed):
boolean matches = passwordEncoder.matches(submittedPassword, storedHash);
```

**Follow-up:**

A fast general-purpose hash function like MD5 or plain SHA-256 is the wrong tool for passwords, even though it's a perfectly good hash for other things like checksums or content-addressing. Those are deliberately optimized to be fast, which is exactly what makes brute-forcing cheap once an attacker has the hash database. Bcrypt, and similar purpose-built algorithms like Argon2 or PBKDF2, are deliberately slow and tunable to counter that — which is the whole reason password-hashing exists as its own category, separate from general-purpose hashing.

**Source:** [`BCryptPasswordEncoder` Javadoc](https://docs.spring.io/spring-security/site/docs/current/api/org/springframework/security/crypto/bcrypt/BCryptPasswordEncoder.html), [Spring Security Reference — Password Storage](https://docs.spring.io/spring-security/reference/features/authentication/password-storage.html)

---

### 5. What's the Difference Between a Cookie and a Session, Mechanically?

**Answer:**

"A **cookie** is just a small piece of data the server asks the browser to store, via a `Set-Cookie` response header, and automatically send back on every later request to that domain, via a `Cookie` request header. The browser handles storage and resending mechanically — the cookie's content can be literally anything the server puts in it. A **session** is a server-side concept: a chunk of state the server keeps for a particular client, most commonly an `HttpSession` object holding whatever the application stored (logged-in user info, cart contents). The two are connected by convention, not by any inherent requirement. The standard pattern: the server generates a random, unguessable session identifier, sends it to the browser as a cookie (`JSESSIONID` in a typical Java web app), and on each later request uses that cookie's value to look up the corresponding server-side state.

By default the cookie itself carries only the opaque session ID, not the actual session data. So losing or tampering with the cookie value just means the server can't find the session — it doesn't mean any real user data was exposed in the cookie itself."

**Code:**

```http
# Server creates a session, sends the ID back as a cookie
Set-Cookie: JSESSIONID=A1B2C3D4E5F6; HttpOnly; Secure; SameSite=Lax

# Browser automatically resends it on every subsequent request to this domain
GET /orders HTTP/1.1
Cookie: JSESSIONID=A1B2C3D4E5F6
# Server looks up session A1B2C3D4E5F6 server-side to find "who is this, are they logged in"
```

**Follow-up:**

This "ID in a cookie, data server-side" split has a real operational cost at scale. Server-side sessions have to live somewhere accessible to whichever server instance handles the next request, which means either sticky sessions — routing a user's requests consistently to the same instance — or a shared session store, Redis being the common choice. That's exactly the trade-off that motivates stateless, token-based authentication for horizontally-scaled services, covered later in this guide: a self-contained token needs no server-side session lookup at all.

**Source:** [MDN — HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies), [`HttpSession` Javadoc](https://jakarta.ee/specifications/servlet/6.0/apidocs/jakarta.servlet/jakarta/servlet/http/httpsession)

---

### 6. What Is HTTPS/TLS, and Why Does It Matter for Authentication?

**Answer:**

"TLS (the modern successor to SSL) encrypts data traveling between client and server, and HTTPS is just HTTP running over a TLS connection instead of a plain, unencrypted one. Without it, everything sent in a request — an `Authorization` header, a session cookie, form-submitted credentials — travels as plaintext, readable by anyone positioned to intercept the traffic: a compromised network device, someone on the same public Wi-Fi, an ISP.

That's why every authentication mechanism in this guide — Basic Auth, form login, bearer tokens — treats HTTPS as a hard requirement, not an optional hardening step. Encoding or hashing credentials doesn't protect them in transit the way encryption does. Even a bearer token, which looks random, is fully usable by anyone who intercepts it in plaintext — no cracking required."

**Code:**

```text
Without TLS: GET /login HTTP/1.1
             Authorization: Basic dXNlcjpwYXNzd29yZA==
             -- travels as PLAINTEXT bytes on the wire, trivially readable by an interceptor --

With TLS:    the entire request (headers, body, URL path) is encrypted before leaving the client;
             an interceptor sees only opaque encrypted bytes, not the actual header/credential content
```

**Follow-up:**

Worth knowing here: the `Secure` and `HttpOnly` cookie flags. `Secure` tells the browser to only ever send that cookie over HTTPS, closing off a downgrade-style leak even if some part of the app accidentally serves an HTTP endpoint. `HttpOnly` is a separate, complementary flag that prevents JavaScript from reading the cookie at all — that's about XSS protection, not transport security. They address different threats, and both are worth setting on any sensitive cookie. We'll come back to this in the token-storage question later.

**Source:** [MDN — Transport Layer Security](https://developer.mozilla.org/en-US/docs/Web/Security/Transport_Layer_Security)

---

### 7. What Is Role-Based Access Control, and How Do You Express It With `@PreAuthorize`/`hasRole()`?

**Answer:**

"Role-Based Access Control (RBAC) grants permissions based on a user's assigned **role** — `ADMIN`, `USER`, `MANAGER` — rather than checking permissions for each user one by one. A role is a named bundle of permissions, and a user gets access to whatever their role allows, which scales far better than per-user permission management as the user base and feature set grow. In Spring Security, roles are a specific kind of `GrantedAuthority`, prefixed by convention with `ROLE_` (`ROLE_ADMIN`), and you can check them declaratively at the method level via `@PreAuthorize(\"hasRole('ADMIN')\")`. That check runs before the method executes and throws `AccessDeniedException` if the user doesn't have the role — the method body never runs at all for an unauthorized caller.

Method-level authorization like this needs `@EnableMethodSecurity` active, and it works via a Spring AOP proxy wrapping the bean — the same mechanism `@Transactional` uses, which is why it has the same self-invocation limitation. More on that later in this guide."

**Code:**

```java
@Service
class AdminService {
    @PreAuthorize("hasRole('ADMIN')") // checks for the ROLE_ADMIN authority BEFORE the method runs
    void deleteUser(Long userId) {
        // this body never executes at all for a caller without ROLE_ADMIN —
        // AccessDeniedException is thrown before the method is entered
        userRepository.deleteById(userId);
    }
}
```

**Follow-up:**

RBAC is a good default, but it has a real limitation: it works well when permissions cluster into a handful of coarse roles, but it breaks down for fine-grained, resource-specific authorization — "can this user edit this specific order, but not someone else's?" That's a different problem, object-level authorization, covered directly in the BOLA-prevention question later. RBAC alone isn't enough for it.

**Source:** [Spring Security Reference — Authorization Architecture](https://docs.spring.io/spring-security/reference/servlet/authorization/architecture.html)

---

## Intermediate

### 8. What's the Difference Between `hasRole()` and `hasAuthority()`?

**Answer:**

"Both check whether the current user has a specific `GrantedAuthority`, but `hasRole('ADMIN')` is a convenience shortcut that automatically prepends `ROLE_` — it actually checks for `ROLE_ADMIN`, not `ADMIN`. `hasAuthority('ROLE_ADMIN')` checks for the exact string you pass, with no prefixing at all, so you have to spell out `ROLE_` yourself.

That means `hasRole('ADMIN')` and `hasAuthority('ROLE_ADMIN')` are functionally identical when your authorities follow the standard `ROLE_` convention. But `hasAuthority()` is the right tool for a non-role-shaped permission — a fine-grained authority like `orders:write` or `reports:export` isn't really a role, and shouldn't be forced through the `ROLE_` prefix just to use `hasRole()`."

**Code:**

```java
// User has authority "ROLE_ADMIN" (the standard role-naming convention)
@PreAuthorize("hasRole('ADMIN')")        // checks for "ROLE_ADMIN" — the prefix is added automatically
void adminOnlyMethod() { /* ... */ }

@PreAuthorize("hasAuthority('ROLE_ADMIN')") // functionally IDENTICAL — you spelled out ROLE_ yourself
void sameCheckDifferentSyntax() { /* ... */ }

// A fine-grained, non-role-shaped permission — hasAuthority() is the correct, direct tool here
@PreAuthorize("hasAuthority('orders:write')") // NOT a "role" conceptually — hasRole() is the wrong fit
void updateOrder() { /* ... */ }
```

**Follow-up:**

Here's the mistake this distinction guards against: calling `hasRole('orders:write')` actually checks for `ROLE_orders:write`. The automatic prefixing silently produces a check that will never match the real `orders:write` authority — a quiet bug where the check just always fails, and it's easy to miss unless you already know `hasRole()` prefixes things.

**Source:** [Spring Security Reference — Authorization Expressions](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html)

---

### 9. What Is a JWT, Structurally?

**Answer:**

"A JWT is three base64url-encoded segments joined by dots: `header.payload.signature`. The **header** identifies the signing algorithm and token type (`{\"alg\":\"RS256\",\"typ\":\"JWT\"}`). The **payload**, also called claims, is a JSON object holding the actual data: who the token represents (`sub`), when it expires (`exp`), who issued it (`iss`), and any application-specific claims like roles or a tenant ID — more on that later. The **signature** is computed over the header and payload using the issuer's private key, and it's what a recipient checks to confirm the token really came from the claimed issuer and hasn't been tampered with.

Here's the detail that trips people up constantly: base64url encoding is not encryption. Anyone can decode a JWT's header and payload with no key at all — paste one into jwt.io and read it directly. So a JWT's contents are fully readable by anyone who has the token, even though its authenticity is cryptographically protected by the signature. Never put an actual secret — a raw password, a credit card number — directly in a JWT's claims. Signed means tamper-evident, not confidential."

**Code:**

```text
JWT structure:  header.payload.signature

eyJhbGciOiJSUzI1NiJ9  .  eyJzdWIiOiJhbGljZSIsImV4cCI6MTc...  .  MEUCIQD...
     ^header (base64url)      ^payload/claims (base64url)         ^signature

# Decoding the header/payload requires NO key at all — just base64url decoding:
echo "eyJhbGciOiJSUzI1NiJ9" | base64 -d
# {"alg":"RS256"}   <- readable by anyone with the token, no secret required

# But COMPUTING a valid signature requires the issuer's private/secret key —
# that's the part that actually can't be forged without it
```

**Follow-up:**

The practical consequence: because the payload is fully readable without a key, a JWT should never be logged in full without redaction, and should never hold anything a user isn't meant to see about their own token. The resource-server-validation and claims questions coming up both build on this "signed but not encrypted" understanding.

**Source:** [RFC 7519 — JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)

---

### 10. What Do `permitAll()`, `authenticated()`, and `denyAll()` Mean in a `SecurityFilterChain`?

**Answer:**

"These are authorization rules applied to URL patterns inside `authorizeHttpRequests()`, evaluated in the order they're declared — first match wins, which is why ordering matters and a catch-all rule almost always goes last. `permitAll()` lets the request through with no authentication check at all — the right rule for genuinely public endpoints like a health check, a login page, or static assets. `authenticated()` just requires a successfully authenticated principal, with no specific role or authority check — any logged-in user passes. `denyAll()` rejects every matching request unconditionally, regardless of authentication state — useful for explicitly blocking a path, like a deprecated internal endpoint, instead of leaving it to fall through to a more permissive default rule later.

A typical configuration lists specific rules first — `permitAll()` on `/public/**`, role checks on admin paths — and ends with a catch-all `anyRequest().authenticated()`. That way, anything not explicitly matched still requires at least authentication by default. Secure by default, rather than accidentally leaving something public."

**Code:**

```java
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/public/**", "/login").permitAll()      // no auth check at all
    .requestMatchers("/internal/debug/**").denyAll()            // blocked unconditionally, always
    .requestMatchers("/admin/**").hasRole("ADMIN")               // specific role required
    .anyRequest().authenticated()                                 // catch-all: must be LOGGED IN, any role
);
// Order matters: rules are evaluated top-to-bottom, first match wins
```

**Follow-up:**

The mistake this question is really testing for: put `anyRequest().authenticated()` before a more specific `permitAll()` rule for a public path, and the catch-all matches first — the endpoint that was supposed to be public now incorrectly requires authentication. Spring Security doesn't automatically prefer the more specific rule the way some routing frameworks do. It's strictly first-match-wins in declaration order, so specific rules have to come before general ones.

**Source:** [Spring Security Reference — Authorize HTTP Requests](https://docs.spring.io/spring-security/reference/servlet/authorization/authorize-http-requests.html)

---

### 11. What Is CSRF, at a Basic Level?

**Answer:**

"CSRF exploits the fact that a browser automatically attaches a site's cookies — including a session cookie — to any request sent to that site, even a request triggered by a completely different, malicious site the victim happens to have open in another tab. Say a user is logged into `bank.com` and then visits `evil.com`, which has a hidden form or script that submits a request to `bank.com/transfer-funds`. The browser dutifully attaches the victim's real `bank.com` session cookie to that request. From the bank's server's perspective it looks like a completely legitimate, authenticated request, because the cookie genuinely is theirs — even though the user never intended to make it.

The core defense is a CSRF token: the server includes a random, unpredictable token in the legitimate forms/pages it serves, and requires that exact token on any state-changing request. `evil.com` has no way to read or predict it, since the same-origin policy blocks it from reading the legitimate page's content. So it can trigger a request with the victim's cookie attached, but it can't supply the matching token, and the server rejects the forged request."

**Code:**

```html
<!-- A legitimate form served by bank.com includes a CSRF token the server can verify -->
<form action="/transfer-funds" method="post">
    <input type="hidden" name="_csrf" value="a1b2c3d4-random-unpredictable-token"/>
    <!-- ... -->
</form>
<!-- evil.com CANNOT read this token (same-origin policy blocks it from reading bank.com's
     page content), so a forged request from evil.com is missing it and gets rejected -->
```

**Follow-up:**

CSRF is at its root a cookie-based-session problem — it exploits the browser's automatic cookie-attachment behavior. That's exactly why a pure bearer-token API, where the client explicitly attaches the token in an `Authorization` header via its own JavaScript, is far less exposed: there's no automatic browser behavior for an attacker to piggyback on. Keep that in mind for the enable/disable decision and the CORS-vs-CSRF comparison coming up next.

**Source:** [OWASP — Cross-Site Request Forgery](https://owasp.org/www-community/attacks/csrf), [Spring Security Reference — CSRF](https://docs.spring.io/spring-security/reference/features/exploits/csrf.html)

---

### 12. What Does an `AuthenticationEntryPoint` Do When a Request Is Unauthenticated?

**Answer:**

"`AuthenticationEntryPoint` is what Spring Security invokes when an unauthenticated request tries to access a resource that requires authentication — it decides how to respond, since the right answer genuinely differs by application type. For a traditional server-rendered app, the default entry point typically redirects to the login page (`302` to `/login`), since the natural next step for a browser is to show a form. For a REST API, redirecting to an HTML login page makes no sense to a JSON client at all — the right entry point instead returns `401 Unauthorized` with a JSON error body, letting the client handle the failure programmatically instead of following a redirect meant for a browser.

This is a separate concept from `AccessDeniedHandler`, which handles the different case of an authenticated user attempting something they don't have permission for (`403 Forbidden`). Mixing the two up is a common way to end up returning the wrong status code — exactly the distinction the intermittent-401-vs-403 investigation question later in this guide walks through."

**Code:**

```java
@Bean
SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http.exceptionHandling(exceptions -> exceptions
        // Unauthenticated request to a protected resource -> 401 with a JSON body, not an HTML redirect
        .authenticationEntryPoint((request, response, authException) -> {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.setContentType("application/json");
            response.getWriter().write("{\"error\":\"authentication required\"}");
        })
        // Authenticated but lacking permission -> 403, a SEPARATE handler entirely
        .accessDeniedHandler((request, response, accessDeniedException) -> {
            response.setStatus(HttpServletResponse.SC_FORBIDDEN);
        })
    );
    return http.build();
}
```

**Follow-up:**

This ties back to the Basic-Auth-vs-form-login question: Spring Security's default entry point behavior actually depends on which authentication mechanisms are configured. Enabling `httpBasic()` alongside form login can produce a `WWW-Authenticate: Basic` challenge header instead of the redirect you expected — a common source of "why is my API returning a browser login prompt instead of a clean 401" in a REST API that left `httpBasic()`/form-login defaults active instead of configuring an explicit, API-appropriate entry point.

**Source:** [`AuthenticationEntryPoint` Javadoc](https://docs.spring.io/spring-security/site/docs/current/api/org/springframework/security/web/AuthenticationEntryPoint.html)

---

## Staff Level

### 13. Explain the Spring Security Filter Chain From Request Entry to Authorization

**Answer:**

"Every request to a Spring Security-protected app passes through a chain of servlet filters before it ever reaches your controller. It's wired in via a single `DelegatingFilterProxy` registered with the servlet container, which delegates to Spring's own `FilterChainProxy` — the actual entry point into Spring Security. `FilterChainProxy` picks the matching `SecurityFilterChain` for the request (question 16) and runs its ordered list of filters.

Here are the important ones, roughly in the order they run. `SecurityContextHolderFilter` restores the `SecurityContext` from the session at the start of the chain (or leaves it empty for stateless setups) and clears it at the end. Then authentication-mechanism-specific filters run: `UsernamePasswordAuthenticationFilter` for form login, `BearerTokenAuthenticationFilter` for OAuth2 bearer tokens, `BasicAuthenticationFilter` for HTTP Basic. Whichever mechanism is configured tries to authenticate the request and, on success, populates the `SecurityContext` with an `Authentication` object. Later, `ExceptionTranslationFilter` catches any `AuthenticationException`/`AccessDeniedException` thrown further down and translates it into the right response — a redirect, or a 401/403. Finally, `AuthorizationFilter` (formerly `FilterSecurityInterceptor`) does the actual authorization check, deciding based on the now-populated `SecurityContext` and the configured rules whether this request can proceed to the controller at all."

**Code:**

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .build();
        // this ONE call assembles the whole ordered filter chain under the hood —
        // SecurityContextHolderFilter, BearerTokenAuthenticationFilter,
        // ExceptionTranslationFilter, AuthorizationFilter, all wired for you
    }
}
```

**Follow-up:**

Worth calling out `DelegatingFilterProxy` explicitly — it's the bridge between the plain servlet container, which knows nothing about Spring beans, and Spring's own `FilterChainProxy`, a Spring-managed bean. That indirection is why Spring Security filters can be reconfigured, reordered, or replaced entirely through Spring configuration, without touching servlet-container registration directly. Filter order also isn't incidental: adding a custom filter — say, a header-based auth mechanism — requires saying explicitly where it runs relative to Spring's built-in filters, via `addFilterBefore`/`addFilterAfter`. Getting that wrong is a common, hard-to-diagnose source of "my custom filter runs, but the request still gets rejected" bugs, since a misplaced filter sets up context too late for the checks further down the chain to see it.

**Source:** [Spring Security Reference — Architecture](https://docs.spring.io/spring-security/reference/servlet/architecture.html)

---

### 14. How Are Authentication and Authorization Different?

**Answer:**

"Authentication answers 'who are you' — verifying an identity claim, typically producing a principal (a user, a service account) the system now trusts, backed by some proof like a password, a valid signed token, or a client certificate. Authorization answers a completely different question, asked after authentication already succeeded: 'is this now-known identity allowed to do this specific thing' — access a resource, call an endpoint, perform an action.

Beyond definitions, this matters practically because the two fail differently and should be reported differently. A failed authentication — bad credentials, an expired token — should produce a `401 Unauthorized`: I don't know who you are, or I don't believe your claimed identity. A failed authorization, where the identity is known and valid but just isn't permitted to do this thing, should produce a `403 Forbidden`: I know exactly who you are, and the answer is still no. Conflating the two in error handling is a common real bug, and it matters for security too — leaking which one failed for a resource a user has no business knowing exists can itself be an information disclosure. Sometimes the deliberate choice is to return `404` instead of `403`, specifically to avoid confirming the resource exists at all to someone unauthorized to see it."

**Code:**

```java
@RestController
class AccountController {
    @GetMapping("/accounts/{id}")
    Account getAccount(@PathVariable String id, Authentication authentication) {
        // AUTHENTICATION already happened by the time this method runs —
        // `authentication` here is a trusted, verified principal, not a raw claim
        Account account = accountService.find(id);

        // AUTHORIZATION — a separate, subsequent check: is THIS authenticated
        // principal allowed to view THIS specific account?
        if (!account.getOwnerId().equals(authentication.getName())) {
            throw new AccessDeniedException("not the account owner"); // -> 403, correctly
            // distinct from an AuthenticationException, which would -> 401
        }
        return account;
    }
}
```

**Follow-up:**

The 403-vs-404 information-disclosure trade-off should be a deliberate, per-resource-type decision, not whatever a framework defaults to. In a multi-tenant system, 403 for "this exists but isn't yours" versus 404 for "as far as you're concerned, this doesn't exist" has real security implications — a 403 confirms the resource's existence to an attacker probing IDs, a 404 doesn't. Getting this right also matters for diagnostics: question 41's investigation of intermittent 401s vs 403s gets a lot harder if the two are conflated in logs and monitoring.

**Source:** [Spring Security Reference — Authentication vs Authorization](https://docs.spring.io/spring-security/reference/features/authentication/index.html)

---

### 15. Explain `SecurityContext`, `Authentication`, `GrantedAuthority`, and `AuthenticationProvider`

**Answer:**

"These four types are the core object model Spring Security's authentication mechanism is built on.

`SecurityContext` holds the currently-authenticated principal's information for the duration of a request or thread, depending on strategy. You access it via `SecurityContextHolder.getContext()`, which by default uses a `ThreadLocal` under the hood — that ties back to the concurrency file's context-propagation concerns, since it needs explicit handling across thread/executor boundaries.

`Authentication` is the object living inside the `SecurityContext`. It represents both the principal (who) and their granted authorities (what they can do), and before authentication completes it can also represent an unauthenticated attempt carrying just raw credentials — a username/password pair submitted for verification — distinguished by its `isAuthenticated()` flag.

`GrantedAuthority` is a single permission or role granted to the authenticated principal, typically a role like `ROLE_ADMIN` or a fine-grained permission like `orders:write`. It's a simple string-backed interface, and an `Authentication` carries a whole collection of them.

`AuthenticationProvider` is the pluggable strategy that actually does the verification. Given an unauthenticated `Authentication`, it either returns a fully populated, authenticated one — identity confirmed, authorities attached — or throws an `AuthenticationException`. Spring Security supports multiple providers via `AuthenticationManager`, usually a `ProviderManager` that tries each configured provider in turn. That's how one application can support several authentication mechanisms at once — a DAO-based username/password provider, an LDAP provider, and a JWT-decoding provider, all simultaneously."

**Code:**

```java
// A custom AuthenticationProvider — the pluggable "how do we actually verify this" strategy
@Component
class ApiKeyAuthenticationProvider implements AuthenticationProvider {

    @Override
    public Authentication authenticate(Authentication authentication) {
        String apiKey = (String) authentication.getCredentials();
        ApiKeyRecord record = apiKeyRepository.findByKey(apiKey)
            .orElseThrow(() -> new BadCredentialsException("invalid API key"));

        List<GrantedAuthority> authorities = record.getScopes().stream()
            .map(SimpleGrantedAuthority::new)
            .collect(Collectors.toList());

        // returns a FULLY AUTHENTICATED Authentication — isAuthenticated() == true,
        // carrying the resolved principal and its granted authorities
        return new ApiKeyAuthenticationToken(record.getOwnerId(), apiKey, authorities);
    }

    @Override
    public boolean supports(Class<?> authentication) {
        return ApiKeyAuthenticationToken.class.isAssignableFrom(authentication);
    }
}

// Reading the current authenticated principal and its authorities anywhere downstream
Authentication auth = SecurityContextHolder.getContext().getAuthentication();
String principalName = auth.getName();
boolean isAdmin = auth.getAuthorities().stream()
    .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
```

**Follow-up:**

The `ThreadLocal`-backed `SecurityContextHolder` is a direct callback to the concurrency file's context-propagation question. The authenticated principal doesn't automatically follow work handed off to another thread — an `@Async` method, a manually-submitted executor task — and forgetting to explicitly propagate it, via a `TaskDecorator` or Spring Security's own `DelegatingSecurityContextExecutor`, is a very common cause of "authorization mysteriously fails only for async-processed requests" bugs. The actual configurable mechanism behind this is `SecurityContextHolderStrategy`: `MODE_THREADLOCAL` (default, per-thread), `MODE_INHERITABLETHREADLOCAL` (propagates to child threads spawned via `new Thread()`, but not to pooled-executor tasks, which don't create new threads), and `MODE_GLOBAL` (rare, mostly for standalone-application contexts).

**Source:** [Spring Security Reference — Authentication](https://docs.spring.io/spring-security/reference/servlet/authentication/index.html), [`SecurityContextHolder` Javadoc](https://docs.spring.io/spring-security/site/docs/current/api/org/springframework/security/core/context/SecurityContextHolder.html)

---

### 16. How Does Spring Choose Among Multiple `SecurityFilterChain` Beans?

**Answer:**

"When more than one `SecurityFilterChain` bean is registered, Spring Security evaluates them in order against each request's `RequestMatcher` and uses the first one whose matcher matches. It doesn't merge chains — exactly one applies per request. Order matters a lot here: chains are evaluated by their `@Order` value, or registration order if unspecified, which is fragile and not something to rely on. A broadly-matching chain with a lower order value than a more specific one will "steal" requests meant for the specific configuration, and that chain's rules simply never run.

This is the standard way to give different parts of a URL space genuinely different security behavior — a public API secured with OAuth2 bearer tokens under `/api/**`, and a traditional session-based form-login flow for an admin UI under `/admin/**`. Each gets its own `SecurityFilterChain`, matched by its own `securityMatcher`, with an independent set of filters and rules."

**Code:**

```java
@Configuration
@EnableWebSecurity
public class MultiChainSecurityConfig {

    @Bean
    @Order(1) // evaluated FIRST — more specific matcher, must come before broader ones
    public SecurityFilterChain apiFilterChain(HttpSecurity http) throws Exception {
        http.securityMatcher("/api/**")
            .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS));
        return http.build();
    }

    @Bean
    @Order(2) // evaluated SECOND — catches everything the first chain's matcher didn't
    public SecurityFilterChain webFilterChain(HttpSecurity http) throws Exception {
        http.securityMatcher("/**")
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/login", "/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(Customizer.withDefaults());
        return http.build();
    }
    // a request to /api/orders matches chain 1's securityMatcher and uses ONLY
    // chain 1's rules and filters — chain 2 never even evaluates for this request
}
```

**Follow-up:**

The "exactly one chain applies, no fallthrough" behavior is what most commonly surprises people coming from a single-chain setup. If a broad `/**` matcher chain accidentally gets a lower `@Order` than a more specific one, every request gets swallowed by the broad chain and the specific chain's rules — maybe stricter checks for a sensitive subpath — silently never run. This same pattern is exactly how one application can serve both a stateless bearer-token API and a stateful session-based UI at once without the two mechanisms interfering — a common real-world need for services with both a machine-facing API and a human-facing admin console.

**Source:** [Spring Security Reference — Multiple SecurityFilterChain](https://docs.spring.io/spring-security/reference/servlet/architecture.html#servlet-securityfilterchain)

---

### 17. What Is the Difference Between Request-Level and Method-Level Authorization?

**Answer:**

"Request-level authorization is enforced in the filter chain itself, via `authorizeHttpRequests` matched against URL patterns and HTTP methods. It runs before the request ever reaches a controller method, based purely on path and method, with no visibility into the actual business objects involved.

Method-level authorization — `@PreAuthorize`, `@PostAuthorize`, `@Secured`, `@RolesAllowed` — is enforced via AOP proxies, the same mechanism from the Spring Boot Internals file, around individual bean methods. Critically, it has access to the actual method arguments and, for `@PostAuthorize`, the return value — which lets it express rules that depend on the specific data involved, not just the URL shape. A request-level rule can say "any authenticated user may call `GET /orders/{id}`." Only a method-level rule can say "this specific user may retrieve this order only if they own it," since checking ownership means actually loading and inspecting the order.

In practice I use both together: request-level rules for coarse, URL-shape gating (public vs. authenticated-only paths, role-gated admin sections), and method-level rules for the fine-grained, data-dependent checks that request-level matching structurally can't express."

**Code:**

```java
// Request-level — coarse, URL-shape-based, no visibility into actual data
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/orders/**").authenticated() // any authenticated user can call this URL
    .requestMatchers("/admin/**").hasRole("ADMIN")
);

// Method-level — fine-grained, data-dependent, has access to actual arguments/return value
@Service
class OrderService {

    @PreAuthorize("hasRole('ADMIN') or #id == authentication.name") // evaluated BEFORE
    public Order getOrder(String id) { return orderRepository.findById(id); } // the method runs

    @PostAuthorize("returnObject.ownerId == authentication.name") // evaluated AFTER the
    public Order getOrderByReference(String reference) { // method runs, checking the
        return orderRepository.findByReference(reference); // ACTUAL returned object
    }
}
```

**Follow-up:**

`@PostAuthorize` needs careful judgment. Because it evaluates after the method body has already run, using it on anything with side effects means the side effect already happened by the time the check fails and throws — almost always the wrong behavior for a mutating operation. The practical rule: `@PostAuthorize` is fine for read-only methods where checking the loaded object's ownership is the only way to express the rule, but a method with side effects should use `@PreAuthorize` against the arguments instead, or an explicit ownership check before the mutation, so an unauthorized side effect never executes even momentarily. And enabling method security needs `@EnableMethodSecurity`, and is subject to the same proxy-based self-invocation limitation as `@Transactional`/`@Cacheable`/`@Async` from the Spring Boot Internals file.

**Source:** [Spring Security Reference — Method Security](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html)

---

### 18. Why Does Method-Security Self-Invocation Cause Problems?

**Answer:**

"This is the exact same proxy mechanism and the exact same failure mode as `@Transactional`/`@Cacheable`/`@Async` self-invocation from the Spring Boot Internals file. `@PreAuthorize`/`@PostAuthorize`/`@Secured` are all implemented via the same AOP proxy interception, and a bean calling one of its own annotated methods via `this.method()` — or an implicit bare call, which is the same thing — bypasses the proxy entirely. The security check never runs. What makes this specifically dangerous for security annotations, versus caching or transactions, is the failure mode: it's not slightly-wrong behavior, it's a silent authorization bypass. A method meant to require `ROLE_ADMIN` runs with zero enforcement when reached via self-invocation, and nothing throws, logs, or signals that the check was skipped."

**Code:**

```java
@Service
class AccountService {

    public void transferFunds(String fromAccount, String toAccount, BigDecimal amount) {
        validateTransfer(fromAccount, toAccount, amount);
        executeTransfer(fromAccount, toAccount, amount); // SELF-INVOCATION —
    }                                                       // bypasses the proxy entirely

    @PreAuthorize("hasRole('TREASURY_ADMIN')") // NEVER actually enforced when called
    public void executeTransfer(String fromAccount, String toAccount, BigDecimal amount) {
        // this runs with ZERO authorization checking when reached via transferFunds()
        // above — a genuine, silent security bypass, not just a minor bug
        ledgerRepository.transfer(fromAccount, toAccount, amount);
    }
}

// FIX — split into a separate bean, so the call crosses a real proxy boundary
@Service
class AccountServiceFixed {
    private final TreasuryOperations treasuryOperations; // separate bean

    public void transferFunds(String fromAccount, String toAccount, BigDecimal amount) {
        validateTransfer(fromAccount, toAccount, amount);
        treasuryOperations.executeTransfer(fromAccount, toAccount, amount); // cross-bean
    }                                                                         // call — proxy
}                                                                              // correctly applies

@Service
class TreasuryOperations {
    @PreAuthorize("hasRole('TREASURY_ADMIN')")
    public void executeTransfer(String fromAccount, String toAccount, BigDecimal amount) {
        ledgerRepository.transfer(fromAccount, toAccount, amount); // NOW genuinely enforced
    }
}
```

**Follow-up:**

This is severe enough to warrant an actual automated safeguard, not just code review. A static-analysis rule — ArchUnit is a common choice — that flags any `@PreAuthorize`/`@Secured`/`@RolesAllowed` method called from within the same class is cheap, valuable platform tooling, precisely because the bug is silent and security-critical, unlike a `@Cacheable` self-invocation miss which is just a performance regression. AspectJ weaving, compile-time or load-time rather than Spring's default runtime proxying, does correctly intercept self-invocation since it rewrites bytecode directly instead of wrapping an external proxy — a legitimate, if heavier, fix for a codebase where this keeps recurring despite review and tooling.

**Source:** [Spring Security Reference — Method Security, proxying limitations](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html)

---

### 19. When Should CSRF Protection Be Enabled or Disabled?

**Answer:**

"CSRF protection defends against a specific attack: a malicious site tricks a victim's browser into submitting a request to your application, and because the browser automatically attaches the victim's session cookie to it, your server sees what looks like a legitimate, authenticated request the victim never intended to make. CSRF tokens defeat this by requiring a secret value the attacker's page can't know or predict, alongside the cookie, on any state-changing request.

The key insight for when to enable or disable it: CSRF is fundamentally a cookie-based session problem — the attack only works because the browser automatically attaches credentials regardless of which site initiated the request. If your API instead authenticates via a bearer token the client must explicitly attach to a header, a forged cross-site request has no way to include that header — the browser won't add it on the attacker's behalf the way it does with cookies. So the attack vector doesn't exist for that mechanism at all, and disabling CSRF protection for a stateless, bearer-token API is standard, correct practice, not a shortcut.

Conversely, any endpoint that authenticates via a cookie — a traditional session-based web app, but also an API that stores its token in a cookie for browser convenience rather than requiring an explicit header — absolutely needs CSRF protection, since it has the exact automatic-credential-attachment property CSRF exploits."

**Code:**

```java
// Stateless, header-based bearer-token API — CSRF protection correctly disabled,
// because the attack vector (automatic credential attachment) doesn't exist here
@Bean
public SecurityFilterChain apiFilterChain(HttpSecurity http) throws Exception {
    return http
        .securityMatcher("/api/**")
        .csrf(AbstractHttpConfigurer::disable) // correct — bearer tokens aren't
        .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults())) // auto-attached
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .build();
}

// Session/cookie-based web app — CSRF protection MUST stay enabled
@Bean
public SecurityFilterChain webFilterChain(HttpSecurity http) throws Exception {
    return http
        .securityMatcher("/app/**")
        .csrf(Customizer.withDefaults()) // enabled — session cookies ARE
        .formLogin(Customizer.withDefaults()) // automatically attached by the browser,
        .build();                                // exactly the property CSRF exploits
}
```

**Follow-up:**

There's a dangerous middle-ground configuration worth naming, since it's a real, recurring mistake: an API that stores its auth token in a cookie for browser convenience, but disables CSRF protection because "it's an API, not a web app." That combination has the exact vulnerable property — automatic credential attachment — and no defense against it. A genuinely exploitable setup. The deciding factor for CSRF is never "is this an API vs. a web app," it's whether the authentication mechanism gets automatically attached to requests by the browser regardless of origin. Cookie-based auth always needs CSRF protection (or `SameSite=Strict`/`Lax` as a complementary, browser-native defense); explicit-header-based auth generally doesn't.

**Source:** [Spring Security Reference — CSRF](https://docs.spring.io/spring-security/reference/features/exploits/csrf.html)

---

### 20. Compare CORS and CSRF. Why Does Configuring One Not Solve the Other?

**Answer:**

"These get confused constantly because they both involve a request from a different origin, but they solve completely different problems, and neither one's protection substitutes for the other.

**CORS** is a browser-enforced relaxation mechanism. By default, browsers block a page on origin A from reading the response of a request it made to origin B — the same-origin policy. CORS is the server-controlled mechanism, `Access-Control-Allow-Origin` and related headers, that explicitly permits specific other origins to make that cross-origin request and read the response. It exists to protect your users' data on other sites from being read by your site's JavaScript without permission — it's about controlling who can read the response.

**CSRF** exists to protect your site from a forged request being submitted using a victim's ambient credentials, regardless of whether the attacker ever reads the response. The attacker often doesn't even need to read it for the attack to work — a forged "transfer money" or "change email" request causes damage purely by being submitted.

Configuring CORS permissively does nothing to prevent CSRF, because CORS's browser-enforced read-blocking has no bearing on whether a request can be submitted in the first place. A plain HTML form submission, or an `img`/`script` tag triggering a GET, isn't subject to CORS preflight rules for many request shapes at all. And even for requests that are subject to CORS, the request often still reaches the server and executes its side effects before the browser blocks the response from being read. That's exactly why the two need separate, independent defenses."

**Code:**

```java
// CORS configuration — controls who can READ cross-origin responses via a browser.
// This is NOT a CSRF defense — it doesn't stop the request from being SUBMITTED,
// it (partially) controls whether the response can be read back by the calling page
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://trusted-frontend.example.com"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
    config.setAllowCredentials(true); // allows cookies to be sent cross-origin —
    // this specific combination (credentials + permissive origins) is exactly
    // the configuration that needs CSRF protection to remain fully sound
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}

// A CSRF attack that CORS does NOTHING to stop — a plain HTML form on an
// attacker's site, no JavaScript, no CORS involved at all:
// <form action="https://victim-bank.example.com/transfer" method="POST">
//   <input type="hidden" name="toAccount" value="attacker-account">
//   <input type="hidden" name="amount" value="10000">
// </form>
// <script>document.forms[0].submit()</script>
// The browser happily submits this cross-site POST WITH the victim's session
// cookie attached — CORS is irrelevant here since the attacker's page never
// tries to READ the response, it just needs the side effect to happen
```

**Follow-up:**

The mental model that resolves this confusion for good: CORS is about response confidentiality across origins — can this other origin's script read what came back. CSRF is about request authenticity — was this request genuinely intended by the user, or forged by another site exploiting their ambient credentials. Completely orthogonal concerns, and a system needs both defenses independently, never treating one as covering for the other. `SameSite=Strict`/`Lax` cookie attributes have become a standard complementary, browser-native CSRF defense alongside explicit tokens, but it's a defense-in-depth layer, not a full replacement — older browsers and certain cross-site navigation patterns can still leave gaps.

**Source:** [Spring Security Reference — CORS](https://docs.spring.io/spring-security/reference/servlet/integrations/cors.html), [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

### 21. Compare Session-Based Authentication and Bearer-Token Authentication

**Answer:**

"Session-based authentication issues an opaque session identifier, typically via a cookie, after login, and the server maintains the actual state — who's logged in, what authorities they have — in server-side storage, whether in-memory or a shared store like Redis for a multi-instance deployment. Every later request presents just the session ID, and the server looks up the state. It's simple to reason about and easy to revoke instantly — delete the server-side session and the ID is immediately worthless — but it needs either sticky sessions or a shared session store to work across multiple server instances, and it doesn't naturally extend to service-to-service or mobile/native-client scenarios the way a self-contained token does.

Bearer-token authentication, most commonly JWT these days, has the client present a token in an `Authorization: Bearer <token>` header on every request. The token is often self-contained, carrying the claims needed to establish identity and authorities directly, cryptographically signed by an authorization server. The server can validate the signature and read the claims with no server-side session state or lookup at all — which is exactly what lets it scale cleanly across stateless server instances with zero shared session infrastructure, and what makes it a natural fit for service-to-service and cross-domain scenarios that cookies handle awkwardly. The trade-off, covered in depth in question 31, is that this same no-lookup-required property makes revocation fundamentally harder — there's no server-side record to delete, since avoiding server-side lookups was the whole point."

**Code:**

```java
// Session-based — server holds the actual state, client just holds a reference to it
@Bean
public SecurityFilterChain sessionFilterChain(HttpSecurity http) throws Exception {
    return http
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED))
        .formLogin(Customizer.withDefaults())
        .build();
    // session state lives server-side (in-memory or Redis-backed via Spring Session);
    // the client only ever holds an opaque cookie value referencing it
}

// Bearer-token/JWT — server validates a self-contained token, no server-side
// session lookup required at all for a normal request
@Bean
public SecurityFilterChain jwtFilterChain(HttpSecurity http) throws Exception {
    return http
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
        .build();
    // identity + authorities are read directly out of the token's claims after
    // signature verification — no shared session store needed across instances
}
```

**Follow-up:**

The actual decision comes down to deployment topology and revocation needs, not "modern vs. old-fashioned." A small number of instances behind a load balancer with sticky sessions, or a shared Redis-backed session store (Spring Session makes this straightforward), makes session-based auth entirely viable at moderate scale, with the real advantage of trivially instant, precise revocation. Bearer tokens win decisively for genuinely distributed, multi-service, cross-domain, or mobile-client scenarios where a shared session store becomes an availability and latency liability — but that scalability comes at the direct cost of a harder revocation story. The staff-level answer names this trade-off explicitly and picks based on the system's real topology and revocation needs, rather than defaulting to JWT because it's the more commonly discussed pattern.

**Source:** [Spring Security Reference — Session Management](https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html), [Spring Security Reference — OAuth2 Resource Server](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/index.html)

---

### 22. Explain OAuth 2.0 Authorization-Code Flow With PKCE

**Answer:**

"Authorization-code flow is the standard OAuth2 flow for anything with a redirect-capable user agent — a browser, or a mobile app's system browser/webview. It's designed so the actual access token is never exposed to the user agent or transmitted through a redirect URL; only a short-lived, single-use authorization code is.

Here's the sequence. The client redirects the user's browser to the authorization server's `/authorize` endpoint, including the client ID, requested scopes, a redirect URI, and, with PKCE, a `code_challenge` — a hash of a locally-generated, client-held secret called the `code_verifier`. The user authenticates with the authorization server, not the client — that's the whole point, the client never sees the user's actual credentials — and approves the requested scopes. The authorization server redirects back to the client with a short-lived authorization code. The client then makes a direct, back-channel POST (not through the browser) to the token endpoint, presenting the code plus the original `code_verifier`. The authorization server hashes the presented verifier, checks it matches the earlier `code_challenge`, and only then exchanges the code for an actual access token and typically a refresh token.

PKCE exists specifically to close a vulnerability in public clients — mobile apps, single-page apps — that have no way to keep a client secret confidential. Without PKCE, an attacker who intercepts the authorization code (a real risk on mobile, via a malicious app registering the same custom URI scheme) could exchange it for a token themselves. With PKCE they'd also need the `code_verifier`, which never left the legitimate client and was never transmitted anywhere until the final back-channel exchange."

**Code:**

```text
1. Client generates a random code_verifier, computes
   code_challenge = BASE64URL(SHA256(code_verifier))

2. Client redirects the user's browser to:
   GET https://auth.example.com/authorize?
       response_type=code
       &client_id=my-client
       &redirect_uri=https://app.example.com/callback
       &scope=orders:read
       &code_challenge=<code_challenge>
       &code_challenge_method=S256
       &state=<random-csrf-protection-value>

3. User authenticates + consents AT THE AUTHORIZATION SERVER (never at the client)

4. Authorization server redirects back:
   GET https://app.example.com/callback?code=<auth-code>&state=<same-state>

5. Client makes a DIRECT (non-browser, back-channel) POST to the token endpoint:
   POST https://auth.example.com/token
   grant_type=authorization_code
   &code=<auth-code>
   &redirect_uri=https://app.example.com/callback
   &code_verifier=<original-code_verifier>   <-- proves this IS the client that
                                                   started the flow in step 1

6. Authorization server verifies SHA256(code_verifier) == code_challenge from
   step 1, and only then returns an access_token (and refresh_token)
```

```java
@Bean
public SecurityFilterChain oauth2LoginFilterChain(HttpSecurity http) throws Exception {
    return http
        .oauth2Login(Customizer.withDefaults()) // Spring Security handles the full
        .build();                                  // authorization-code + PKCE flow for you
    // configured via spring.security.oauth2.client.registration.* properties
}
```

**Follow-up:**

PKCE is now recommended for all clients, not just public ones without a secret — the current OAuth 2.1 draft mandates it universally, since it's a strict security improvement with no real downside even for confidential clients. The `state` parameter serves a separate purpose from `code_challenge`/`code_verifier`: it defends against CSRF on the redirect callback itself, making sure the authorization response actually corresponds to a flow this browser session initiated. That's a different threat than the code-interception threat PKCE addresses. Both are needed, and omitting `state` because "we already have PKCE" is a real, if subtle, gap.

**Source:** [RFC 7636, PKCE](https://datatracker.ietf.org/doc/html/rfc7636), [Spring Security Reference — OAuth2 Login](https://docs.spring.io/spring-security/reference/servlet/oauth2/login/index.html)

---

### 23. Why Is the Resource-Owner Password Flow Deprecated?

**Answer:**

"The resource-owner password credentials (ROPC) flow has the client application collect the user's actual username and password directly and send them straight to the authorization server's token endpoint in exchange for a token — no redirect to the authorization server at all, no separate authentication surface. This directly violates the core security principle the entire rest of OAuth2 is built around: the client application should **never see the user's actual credentials**.

Concretely, this means: the client application (which might be a third-party app, or simply a codebase with a larger attack surface than the authorization server itself) now has to be trusted with raw passwords, defeating the entire purpose of using an authorization server as a separate, hardened, single point of credential handling. It also structurally can't support anything beyond a simple username/password check — no multi-factor authentication step, no passkeys/WebAuthn, no 'this login looks suspicious, show a CAPTCHA or step-up challenge' — because the flow is just 'hand over a password, get a token back,' with the authorization server never actually getting a chance to interactively drive the authentication experience. OAuth 2.1 (the informal successor spec cleaning up 2.0's accumulated flows) removes ROPC entirely, and it should be treated as fully deprecated in any new system design."

**Code:**

```text
# ROPC — the client itself collects and forwards the raw password. AVOID.
POST https://auth.example.com/token
grant_type=password
&username=alice
&password=hunter2          <-- the CLIENT APPLICATION now holds/transmits
&client_id=my-app             this raw credential directly — exactly what
                                the rest of OAuth2 is designed to avoid

# The correct alternative for the same underlying need (a trusted, first-party
# client) — authorization code flow, where the authorization server itself
# collects the password on ITS OWN login page, never the client's:
GET https://auth.example.com/authorize?response_type=code&client_id=my-app&...
# user enters credentials directly into auth.example.com's own page, not the
# client app's UI at all
```

**Follow-up:**

I'd mention the historical context for why ROPC existed at all — it was meant as a migration path for legacy applications that already had a username/password login form and needed a stepping stone toward OAuth2 without an immediate UI rewrite, but that migration-convenience justification never outweighed the structural security cost, which is exactly why it's now formally deprecated rather than merely discouraged. I'd also flag that for genuinely trusted first-party native/mobile clients (a company's own mobile app, not a third party) where redirecting to a system browser feels like worse UX than an in-app password field, the correct modern answer is still authorization-code-with-PKCE using an in-app browser tab (Custom Tabs on Android, `ASWebAuthenticationSession` on iOS) rather than a custom in-app login form — these platform-provided mechanisms let the authorization server's own page render inside a browser context the client app can't inspect or intercept, preserving the "client never sees the password" property even in a native app.

**Source:** [RFC 6749 §4.3 — Resource Owner Password Credentials Grant](https://datatracker.ietf.org/doc/html/rfc6749#section-4.3), [OAuth 2.1 draft — removed grant types](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1)

---

### 24. What Are the Roles of the Resource Owner, Client, Authorization Server, and Resource Server?

**Answer:**

"These four roles are the core vocabulary of the entire OAuth2 spec, and keeping them straight is what makes the rest of the flows make sense.

The **resource owner** is the entity — usually an end user — who owns the protected data and can grant or deny access to it. The **client** is the application requesting access to that data *on the resource owner's behalf* — critically, the client is not the same as the resource owner, and OAuth2's whole design is built around the client never needing to directly hold the resource owner's actual credentials. The **authorization server** is the trusted party that authenticates the resource owner, collects their consent, and issues tokens representing that granted access — this is the system that owns the login page and the token-issuance logic. The **resource server** is the API that actually holds the protected data and enforces access based on a presented, validated token — it trusts tokens issued by the authorization server (having validated them, question 28) without needing to re-authenticate the user itself.

A concrete mapping makes this click: a user (resource owner) uses a third-party photo-printing app (client) that wants to access their Google Photos (resource server), and Google's own login/consent system (authorization server) is what actually authenticates the user and issues the printing app a scoped token — the printing app never sees the user's Google password, and Google Photos (the resource server) only ever sees a token, never re-verifying the user's identity itself for each API call."

**Code:**

```text
Resource Owner  --(1. authenticates + consents)-->  Authorization Server
                                                            |
                                                    (2. issues access token)
                                                            |
      Client  <-----------------------------------------  /
        |
        | (3. presents access token)
        v
Resource Server -- validates token (question 28) -- serves the protected data

# In a microservices context, these roles are often ALL within one organization:
#   Resource Owner = the end user
#   Client = the frontend / BFF service
#   Authorization Server = the org's own identity provider (Okta, Keycloak, Auth0,
#                            or a self-hosted Spring Authorization Server)
#   Resource Server = each individual backend microservice validating the token
```

**Follow-up:**

I'd bring up that in a large internal microservices architecture, a single service frequently plays **both** the resource-server role (validating incoming tokens from external callers) **and** the client role (acting as a client itself when calling further downstream services, question 34) — recognizing which role a given piece of code is playing at any moment clarifies exactly which OAuth2 concern applies: token *validation* logic belongs to the resource-server role, token *acquisition/attachment* logic belongs to the client role, and conflating the two in a design discussion is a common source of confused, circular architecture conversations. I'd also mention that the same physical service can even be a client to *itself* in a service-mesh context — worth flagging so the vocabulary stays precise rather than devolving into "the service" meaning three different roles in the same sentence.

**Source:** [RFC 6749 §1.1 — Roles](https://datatracker.ietf.org/doc/html/rfc6749#section-1.1)

---

### 25. Compare Access Tokens, Refresh Tokens, and ID Tokens

**Answer:**

"**Access tokens** are what a client presents to a resource server to actually access protected data — they're deliberately short-lived (commonly minutes to an hour) to limit the blast radius if one leaks, and they carry the granted scopes/authorities the resource server checks against.

**Refresh tokens** are long-lived credentials the client holds *privately* (never sent to a resource server, only ever presented back to the authorization server's token endpoint) specifically to obtain a *new* access token once the current one expires, without forcing the user to re-authenticate interactively every time a short-lived access token expires. Because they're long-lived and powerful (effectively 'get me a fresh access token, indefinitely'), they need to be stored and transmitted with real care, and refresh-token rotation (question 33) exists specifically to limit the damage if one is ever compromised.

**ID tokens** are a distinctly different thing, and this is a common source of confusion: they belong to OpenID Connect (OIDC), not core OAuth2, and they exist purely to convey *authentication* information (who the user is, when they authenticated, via which method) to the **client** itself — they're meant to be consumed by the client application, not presented to a resource server as an access credential. An ID token is always a JWT with a specific, standardized claim set; an access token, by contrast, is *not required* by the OAuth2 spec to be any particular format at all (it can be opaque or a JWT), and conflating 'my access token happens to be a JWT' with 'therefore it's the same thing as an ID token' is a genuinely common mistake."

**Code:**

```json
// ID Token (OIDC) — describes the AUTHENTICATION EVENT, meant for the CLIENT
{
  "iss": "https://auth.example.com",
  "sub": "user-12345",
  "aud": "my-client-app",
  "exp": 1735689600,
  "iat": 1735686000,
  "auth_time": 1735685990,
  "name": "Alice Example",     // OIDC standard claims about the user
  "email": "alice@example.com"
}

// Access Token (JWT-formatted example) — describes AUTHORIZATION, meant for
// the RESOURCE SERVER, NOT necessarily meaningful to the client application itself
{
  "iss": "https://auth.example.com",
  "sub": "user-12345",
  "aud": "orders-api",           // note: different audience — THIS resource server
  "exp": 1735689900,             // typically much shorter-lived than the ID token
  "scope": "orders:read orders:write"
}
```

**Follow-up:**

I'd call out the "never send the access token as if it were proof of identity to your own frontend, and never send the ID token to a resource server as if it were an access credential" rule explicitly, since mixing these up is a real, recurring implementation mistake — an ID token's `aud` claim is the client, not a resource server, so a resource server that's misconfigured to accept ID tokens as access tokens is validating a token that was never intended to authorize API access at all, and might not even carry the scope information a resource server needs to make an authorization decision. I'd also mention token lifetime tuning as a genuine security/UX trade-off: shorter access-token lifetimes reduce the blast radius of a leaked token but increase the frequency of refresh-token-exchange calls (more load on the authorization server, and a slightly larger window where a delayed revocation propagation, per question 31, matters); this is a real tuning knob, not a "shorter is always strictly better" decision.

**Source:** [RFC 6749 §1.4 — Access Token](https://datatracker.ietf.org/doc/html/rfc6749#section-1.4), [OpenID Connect Core — ID Token](https://openid.net/specs/openid-connect-core-1_0.html#IDToken)

---

### 26. What Is the Difference Between OAuth 2.0 and OpenID Connect?

**Answer:**

"OAuth2 is fundamentally an **authorization** framework — it's about a client obtaining scoped, delegated access to a resource on a user's behalf. It was never actually designed to answer 'who is this user' in a standardized way — plenty of early, ad-hoc 'social login' implementations built on top of bare OAuth2 by treating 'the client successfully got an access token' as a proxy for 'the user is authenticated,' which is a real category error (a client getting an access token proves it was granted some access, not necessarily that it has any standardized way to verify who the user actually is).

**OpenID Connect (OIDC)** is a thin, standardized identity layer built directly on top of OAuth2 specifically to close that gap — it adds the ID token (question 25), a standardized `/userinfo` endpoint for fetching profile claims, and a standardized discovery document (`/.well-known/openid-configuration`) describing an authorization server's exact endpoints and capabilities. The practical rule: if you need to know *who the user is* (their identity, for your own application's use — displaying their name, tying data to their user ID), you need OIDC, not bare OAuth2. If you only need your client to be granted scoped *access to a resource*, without needing to establish or display identity information yourself, plain OAuth2 suffices — though in practice, the overwhelming majority of modern 'login with X' integrations are OIDC, since almost every real system needs to know who's logged in, not just that access was granted."

**Code:**

```text
# OIDC discovery document — the standardized way clients find an authorization
# server's capabilities, NOT part of bare OAuth2 at all:
GET https://auth.example.com/.well-known/openid-configuration

{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "userinfo_endpoint": "https://auth.example.com/userinfo",   // OIDC-specific
  "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
  "id_token_signing_alg_values_supported": ["RS256"]
}
```

```properties
# Spring Security config difference is small but meaningful — requesting
# the "openid" scope is what turns a plain OAuth2 authorization request into
# an OIDC one, triggering ID token issuance alongside the access token:
spring.security.oauth2.client.registration.myprovider.scope=openid,profile,email
```

**Follow-up:**

I'd bring up the practical, historical reason OIDC exists at all as useful context: before OIDC standardized this, every identity provider had its own bespoke way of exposing "who is this user" (a proprietary userinfo endpoint shape, non-standard claims), which meant every client integration was custom, provider-specific glue code — OIDC's real contribution was standardizing that layer so a client library can work against *any* OIDC-compliant provider with the same code, the same way OAuth2 itself standardized the authorization mechanics. I'd also flag the discovery document specifically as a genuinely underused piece of pragmatic engineering — pointing a client at just the issuer URL and letting it fetch `/.well-known/openid-configuration` to learn all the other endpoints dynamically is both more robust to a provider's internal endpoint changes and less configuration for the client to hardcode and maintain.

**Source:** [OpenID Connect Core specification](https://openid.net/specs/openid-connect-core-1_0.html), [RFC 8414 — OAuth 2.0 Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414)

---

### 27. Compare Opaque Tokens and JWT Access Tokens

**Answer:**

"An **opaque token** is a random, meaningless-on-its-own string — it carries no information by itself, and a resource server can only validate it by making a call back to the authorization server (typically its token-introspection endpoint, RFC 7662) to ask 'is this still valid, and if so, what does it represent.' A **JWT access token** is self-contained — it's a signed (and optionally encrypted) structure carrying the claims (subject, scopes, expiry) directly, so a resource server can validate it entirely locally, by checking the signature against a known public key, with **no network call to the authorization server needed at all** for a normal validation.

The trade-off is close to a mirror image of each other. Opaque tokens: every single validation costs a network round-trip to the authorization server (added latency, and the authorization server becomes a hard dependency for every resource server's every request), but revocation is instant and precise — the authorization server can simply mark the token invalid in its own store, and the very next introspection call reflects that immediately. JWTs: validation is fast and fully decoupled from the authorization server being available or reachable at request time (a real resilience win — a resource server can keep validating already-issued tokens even if the authorization server is briefly down), but revocation is fundamentally hard (question 31) — a resource server has no way to know a JWT was revoked before its natural expiry unless some additional, out-of-band mechanism is layered on top, which reintroduces some of the same 'ask someone else if this is still good' cost JWTs were meant to avoid."

**Code:**

```java
// JWT — local, signature-based validation, no network call to the auth server needed
@Bean
public SecurityFilterChain jwtResourceServer(HttpSecurity http) throws Exception {
    return http.oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults())).build();
    // configured with just the issuer's public JWKS endpoint — validation happens
    // ENTIRELY LOCALLY afterward, using cached public keys, no per-request call out
}

// Opaque token — EVERY validation requires an introspection call to the auth server
@Bean
public SecurityFilterChain opaqueResourceServer(HttpSecurity http) throws Exception {
    return http.oauth2ResourceServer(oauth2 -> oauth2
        .opaqueToken(opaque -> opaque
            .introspectionUri("https://auth.example.com/introspect")
            .introspectionClientCredentials("resource-server-client-id", "secret")
        )
    ).build();
    // EVERY incoming request triggers a network call to the auth server to check
    // validity — genuinely more expensive per-request, but instantly revocable
}
```

**Follow-up:**

I'd frame the actual decision around the real operational trade-off: JWTs are the right default for high-throughput, latency-sensitive resource servers where an extra network round-trip per request is a genuine cost, and where the (short) window between revocation and natural expiry is an acceptable risk given short-lived access tokens; opaque tokens (or a hybrid — JWT access tokens with short lifetimes, combined with an introspection-checked, longer-lived session concept for high-sensitivity operations) are the right choice when instant, precise revocation genuinely matters more than raw per-request latency — financial transaction authorization, or any system where "this access must be revocable within seconds, not minutes" is a hard requirement. I'd also mention that some architectures split the difference deliberately: a short-lived JWT access token (minutes) minimizes the real-world impact of the "can't revoke early" problem simply by making "early" a very short window, which is often a perfectly sufficient practical answer without needing opaque tokens' introspection overhead at all.

**Source:** [RFC 7662 — OAuth 2.0 Token Introspection](https://datatracker.ietf.org/doc/html/rfc7662), [Spring Security Reference — Opaque Token](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/opaque-token.html)

---

### 28. How Does a Resource Server Validate a JWT?

**Answer:**

"Validation has two distinct parts, and both matter — a lot of insecure implementations get the second part wrong even when the first is correct.

First, **cryptographic signature verification**: the resource server fetches the authorization server's public signing keys (typically from its JWKS endpoint, `/.well-known/jwks.json`, identified by a `kid` — key ID — in the JWT header matching a specific key in that set) and verifies the JWT's signature was genuinely produced by the authorization server's private key, proving the token wasn't forged or tampered with. This is necessary but **not sufficient** on its own.

Second, **claim validation** — even a token with a perfectly valid signature needs its claims checked: `exp` (has it expired), `nbf` (is it being used before it's valid), and critically `iss`/`aud` (was this token actually issued *by the authorization server this resource server trusts*, and was it actually *intended for this specific resource server*, not just any resource server that happens to trust the same issuer). Skipping the `aud` check specifically is a genuinely common, dangerous mistake: without it, a valid token issued for a *completely different* resource server (in a multi-service environment sharing one authorization server) would still pass signature verification, since it's a legitimately signed token — it's just not meant for *this* API, and accepting it anyway is a confused-deputy-style vulnerability (question 39)."

**Code:**

```java
@Bean
public JwtDecoder jwtDecoder() {
    NimbusJwtDecoder decoder = NimbusJwtDecoder
        .withJwkSetUri("https://auth.example.com/.well-known/jwks.json")
        .build(); // handles signature verification + kid-based key selection automatically

    // Claim validation MUST be added explicitly — signature verification alone
    // is NOT sufficient, this is the part that's commonly forgotten:
    OAuth2TokenValidator<Jwt> audienceValidator = jwt -> {
        if (jwt.getAudience().contains("orders-api")) { // THIS specific resource server
            return OAuth2TokenValidatorResult.success();
        }
        return OAuth2TokenValidatorResult.failure(new OAuth2Error(
            "invalid_token", "required audience 'orders-api' is missing", null));
    };

    OAuth2TokenValidator<Jwt> validator = new DelegatingOAuth2TokenValidator<>(
        JwtValidators.createDefaultWithIssuer("https://auth.example.com"), // exp, nbf, iss
        audienceValidator                                                   // aud — NOT
    );                                                                        // included by default!
    decoder.setJwtValidator(validator);
    return decoder;
}
```

**Follow-up:**

I'd emphasize the `aud` validation gap as specifically the thing worth bringing up unprompted, since Spring Security's default JWT validation (`JwtValidators.createDefaultWithIssuer`) checks `exp`/`nbf`/`iss` but explicitly does **not** check `aud` by default — a resource server that doesn't add this check itself will happily accept a token minted for an entirely different downstream API, as long as both share the same trusted issuer, which is a genuinely exploitable gap in a multi-service architecture with a shared identity provider. I'd also mention JWKS key rotation handling (question 29) as directly tied to this validation flow — the decoder needs to handle a `kid` it hasn't cached yet gracefully (re-fetching the JWKS document), which most libraries do correctly out of the box, but it's worth confirming rather than assuming for any custom validation code.

**Source:** [Spring Security Reference — JWT Validation](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html#oauth2resourceserver-jwt-validation), [RFC 7519 — JWT §4.1 Registered Claims](https://datatracker.ietf.org/doc/html/rfc7519#section-4.1)

---

### 29. How Should Services Handle Signing-Key Rotation?

**Answer:**

"The standard mechanism is JWKS (JSON Web Key Set) — the authorization server publishes its current public signing key(s) at a well-known endpoint, and every JWT it issues includes a `kid` (key ID) header identifying *which* key in that set signed it. Resource servers fetch and cache the JWKS document (rather than re-fetching it on every single request, which would defeat the whole point of self-contained JWT validation), and when validating a token, look up the specific key matching that token's `kid`.

Rotation works by the authorization server publishing a **new** key in the JWKS document *before* it starts actually signing new tokens with it — so resource servers have a window to pick up the new key via their normal (periodic, or on-demand-on-cache-miss) JWKS refresh before any token signed with it actually arrives. The authorization server then switches to signing with the new key, while **keeping the old key published in the JWKS set** for as long as tokens signed with it might still be in circulation (i.e., at least as long as the maximum token lifetime) — only removing the old key from the published set once you're certain no valid, unexpired token signed with it can possibly still exist. Removing an old key too early breaks validation for any still-valid token signed with it; this is a real, avoidable outage if rotation isn't sequenced correctly."

**Code:**

```json
// JWKS document DURING a rotation window — BOTH keys published simultaneously
{
  "keys": [
    { "kid": "2024-key", "kty": "RSA", "use": "sig", "n": "...", "e": "..." }, // OLD —
    { "kid": "2025-key", "kty": "RSA", "use": "sig", "n": "...", "e": "..." }  // still
  ]                                                                              // valid
}                                                                        // for existing tokens
// The authorization server signs NEW tokens with "2025-key" going forward, but
// keeps "2024-key" published until every token signed with it has expired —
// only THEN is "2024-key" safely removed from the published set
```

```java
// Resource-server-side, most libraries handle re-fetch-on-unknown-kid automatically —
// but caching behavior is worth confirming explicitly, not assumed:
@Bean
public JwtDecoder jwtDecoder() {
    return NimbusJwtDecoder.withJwkSetUri("https://auth.example.com/.well-known/jwks.json")
        .cache(Duration.ofMinutes(5)) // periodic refresh — most libraries ALSO
        .build();                       // re-fetch immediately on an unrecognized
}                                          // kid, rather than waiting for the next
                                            // scheduled refresh, but confirm this
                                            // for whatever library is actually in use
```

**Follow-up:**

I'd bring up this exact scenario as a direct link to the cross-stack design question about a rotated signing key causing valid requests to be rejected (question 10 in the design-scenarios category) — the real, common root cause is exactly the sequencing mistake above: the old key gets removed from the JWKS document before every token it signed has actually expired, or a resource server's JWKS cache doesn't get refreshed quickly enough to pick up the new key before tokens signed with it start arriving. The correct operational practice is to always overlap key validity periods for at least the maximum token lifetime, monitor JWKS fetch success/failure and cache-refresh timing explicitly, and treat key rotation as a genuine deployment/rollout process with its own runbook — not a one-off "swap the key" operation performed without regard for tokens already in flight.

**Source:** [RFC 7517 — JSON Web Key (JWK)](https://datatracker.ietf.org/doc/html/rfc7517), [Spring Security Reference — JWKS-based JWT Decoding](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)

---

### 30. What Are `iss`, `aud`, `exp`, `nbf`, `jti`, and `kid` Used For?

**Answer:**

"These are the standardized JWT claims (and one header field) that carry the metadata needed to validate and reason about a token correctly, rather than just trusting its payload blindly.

`iss` (issuer) — identifies *who issued* this token, allowing a resource server to confirm it trusts this specific issuer, not just that the signature happens to verify against *some* key it has cached.

`aud` (audience) — identifies *who the token is intended for*; a resource server must check its own identifier appears here, or it risks accepting a token that was legitimately issued but meant for a different service entirely (question 28's confused-deputy risk).

`exp` (expiration time) — a Unix timestamp after which the token must be rejected regardless of signature validity; this is what bounds the blast radius of a leaked token.

`nbf` (not before) — the mirror of `exp`; a timestamp before which the token must **not yet** be considered valid, used for tokens deliberately issued ahead of their intended validity window.

`jti` (JWT ID) — a unique identifier for this specific token instance, used to support scenarios that need to track or deny *this exact token* individually (e.g., a targeted single-token revocation via a denylist, or replay-detection for a one-time-use token) — something that's otherwise hard to do with a purely self-contained, stateless JWT.

`kid` (key ID) — a JWT **header** field, not a payload claim, identifying which key in the issuer's JWKS set was used to sign this specific token, letting a resource server pick the right public key for verification without needing to try every published key."

**Code:**

```json
{
  "header": {
    "alg": "RS256",
    "kid": "2025-key"                 // WHICH key signed this — header, not a claim
  },
  "payload": {
    "iss": "https://auth.example.com", // WHO issued it
    "aud": "orders-api",                // WHO it's meant for
    "sub": "user-12345",
    "exp": 1735689900,                  // valid UNTIL this timestamp
    "nbf": 1735686300,                  // valid STARTING this timestamp
    "jti": "8f14e45f-ceea-467e-b1a0",   // THIS specific token instance's unique ID
    "scope": "orders:read orders:write"
  }
}
```

**Follow-up:**

I'd bring up `jti` as the specific, standardized mechanism for building a targeted revocation denylist without needing to revoke every token from a user — a resource server (or the authorization server itself, at introspection time) can maintain a small, short-lived store of "revoked jti values still within their natural expiry window," and check incoming tokens' `jti` against it; since the denylist only needs to retain entries until the token's own `exp` would have removed it naturally anyway, this store stays bounded and cheap, unlike trying to denylist every unexpired token a user has ever been issued. I'd also flag that none of these claims are enforced by the JWT format itself — they're conventions defined by RFC 7519 and OAuth2/OIDC profiles on top of it, and it's entirely the validating service's responsibility to actually check them; a JWT library validating only the signature and ignoring `exp`/`aud`/`nbf` is a real, exploitable gap, not a hypothetical one.

**Source:** [RFC 7519 — JSON Web Token, §4 Registered Claims](https://datatracker.ietf.org/doc/html/rfc7519#section-4)

---

### 31. Why Is Revoking a JWT Difficult? What Strategies Are Available?

**Answer:**

"The entire value proposition of a JWT is that a resource server can validate it **without calling back to the authorization server** — that's what makes it fast and decouples resource servers from the authorization server's availability. Revocation fundamentally requires the *opposite*: some way for a resource server to learn 'this specific, otherwise-still-cryptographically-valid token should now be rejected' — which either means giving up the no-callback property entirely, or accepting that revocation can only take effect once the token naturally expires.

The available strategies, in order of how much they compromise the stateless benefit: **do nothing and rely on short expiry** — accept that revocation effectively means 'wait for the token to expire naturally,' which is why access-token lifetimes are kept short (minutes), making this an acceptable trade for most cases. **A revocation denylist keyed by `jti`** — the authorization server (or a shared store resource servers check) tracks explicitly revoked token IDs, and resource servers check incoming tokens against it; this reintroduces exactly one lookup per request (though it can be a much cheaper, more cacheable lookup than a full introspection call, and can use a fast in-memory/Redis-backed structure). **Hybrid opaque-reference tokens** — the client-facing 'access token' is actually an opaque reference the resource server exchanges (with caching) for the real claims, giving instant revocability at the cost of reintroducing a lookup. **Short-lived access tokens plus revocable refresh tokens** — the most common real-world compromise: keep access tokens short and effectively un-revocable (accept the small window), but make the refresh token (which the client needs to get a *new* access token) fully revocable via a server-side check, so revoking a user's session prevents them from getting *any new* access token, even though their current one has a few more minutes to naturally expire."

**Code:**

```java
// jti-based denylist check, added to JWT validation — reintroduces ONE lookup,
// but a cheap, cacheable one (not a full introspection round-trip)
OAuth2TokenValidator<Jwt> notRevokedValidator = jwt -> {
    String jti = jwt.getId();
    if (revocationStore.isRevoked(jti)) { // fast Redis SISMEMBER-style check
        return OAuth2TokenValidatorResult.failure(
            new OAuth2Error("invalid_token", "token has been revoked", null));
    }
    return OAuth2TokenValidatorResult.success();
};

// Revoking a user's session in practice — revoke the REFRESH token (fully
// controllable server-side state), accept the short window on any already-
// issued access token until it naturally expires:
void revokeUserSession(String userId) {
    refreshTokenRepository.revokeAllForUser(userId); // blocks any FUTURE access
    // token issuance for this user immediately — the current access token(s)
}                                                        // remain valid for at most
                                                           // their own short remaining lifetime
```

**Follow-up:**

I'd name the actual trade-off explicitly as a spectrum, not a binary choice: pure stateless JWTs give maximum performance/availability decoupling but effectively zero instant revocability; adding any revocation mechanism moves along that spectrum toward session-based auth's instant-revocability property, at a proportional cost to the stateless benefit — there's no free option that gets both. For most systems, "short-lived access tokens + fully revocable refresh tokens" is the pragmatic sweet spot, accepting a small, bounded, and known exposure window rather than paying a lookup cost on every single request. For genuinely high-sensitivity scenarios (an admin account compromise, a detected security incident requiring *immediate* full lockout), I'd say the right answer is having a documented emergency mechanism — a global "reject all tokens issued before timestamp X" check, which is cheap to implement (compare `iat` against a stored cutoff) and gives a true instant kill-switch for the rare case where waiting even a few minutes for natural expiry is unacceptable.

**Source:** [RFC 7009 — OAuth 2.0 Token Revocation](https://datatracker.ietf.org/doc/html/rfc7009), [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html)

---

### 32. Where Should Tokens Be Stored in a Browser Application?

**Answer:**

"This is a genuinely contested area with real trade-offs on every option, so I'd walk through them rather than claim one universally correct answer.

**`localStorage`/`sessionStorage`**: accessible to any JavaScript running on the page, which means it's fully exposed to **XSS** — if an attacker manages to inject a script (via any XSS vulnerability anywhere on the page, including in a third-party dependency), they can read the token directly and exfiltrate it. This is the option I'd actively avoid for anything beyond a low-sensitivity token, despite it being the most common pattern in tutorials and many real SPAs.

**A cookie with `HttpOnly`, `Secure`, and `SameSite=Strict`/`Lax`**: `HttpOnly` means JavaScript literally cannot read the cookie's value at all, closing off the XSS-exfiltration vector entirely — a real, meaningful security improvement over `localStorage`. But this reintroduces CSRF exposure (question 19/20) since the browser now auto-attaches the cookie to requests, so CSRF protection becomes mandatory again, and it requires the token to be issued as a cookie by a same-site (or carefully configured cross-site) backend rather than handled directly by frontend JavaScript.

**In-memory only (a JavaScript variable, never persisted to any storage)**: the most XSS-resistant option, since there's nothing sitting in storage for a script to read even if XSS occurs — but the token is lost on every page refresh, requiring a silent re-authentication flow (commonly, a same-site `HttpOnly` refresh-token cookie combined with a short-lived, in-memory-only access token) to restore it without forcing the user to log in again on every reload — this hybrid, 'refresh token in an `HttpOnly` cookie, access token in memory only,' is generally the pattern I'd actually recommend for a security-conscious SPA."

**Code:**

```javascript
// AVOID for anything sensitive — fully readable by any injected script (XSS)
localStorage.setItem('access_token', token);

// BETTER — HttpOnly cookie, JS literally cannot read this value at all
// (set by the SERVER in a Set-Cookie response header, not by frontend JS):
// Set-Cookie: refresh_token=xyz; HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh

// RECOMMENDED HYBRID — access token held ONLY in memory (a module-level
// variable), never persisted; refresh token in an HttpOnly cookie handles
// silently restoring a session across page reloads
let accessToken = null; // lives only in JS memory for this page's lifetime

async function silentlyRestoreSession() {
    const response = await fetch('/auth/refresh', {
        method: 'POST',
        credentials: 'include' // sends the HttpOnly refresh-token cookie automatically;
    });                          // JS never touches its actual value at any point
    const { access_token } = await response.json();
    accessToken = access_token; // held in memory only, lost (intentionally) on reload
}
```

**Follow-up:**

I'd bring up that this decision needs to be paired with a broader XSS-prevention posture, not treated as a substitute for one — a strict Content Security Policy (CSP), consistent output encoding, and a locked-down dependency supply chain all reduce the *likelihood* of the XSS that would make `localStorage` dangerous in the first place, but I wouldn't rely on "we have good XSS hygiene" as the sole justification for `localStorage` token storage, since a single missed encoding bug or a compromised third-party script anywhere on the page is enough to defeat it entirely — defense in depth (assume XSS will eventually happen somewhere, and design token storage so that alone doesn't lead to full account takeover) is the more defensible engineering posture. I'd also mention that mobile-app equivalents of this question (Keychain on iOS, Keystore-backed encrypted storage on Android) are generally much safer defaults than either browser storage option, since they're OS-level secure storage rather than something an in-app script (or in a WebView context, similarly-scoped JS) can read directly.

**Source:** [OWASP — JWT Storage on Client Side](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html), [OWASP Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

---

### 33. How Do Refresh-Token Rotation and Reuse Detection Work?

**Answer:**

"Without rotation, a single refresh token stays valid for its entire long lifetime — if it's ever leaked (intercepted, extracted from insecure storage), an attacker can silently mint fresh access tokens indefinitely, and there's no signal to anyone that this happened, since the legitimate client is still using the same token successfully too.

**Refresh-token rotation** changes this: every time a refresh token is used to obtain a new access token, the authorization server also issues a **brand-new refresh token** and immediately invalidates the one just used — a refresh token becomes single-use. **Reuse detection** is the security payoff this enables: if the *same, already-used-and-invalidated* refresh token is ever presented again, that's a strong, unambiguous signal something is wrong — either the client and an attacker both have a copy of the same original token and are racing to use it, or a stolen token is being replayed after the legitimate client already rotated past it. The authorization server's correct response to a detected reuse isn't just to reject that one request — it should treat the entire *token family* (every refresh token descended from that original one, however many rotations have occurred since) as compromised and revoke all of them, forcing full re-authentication, since at that point you genuinely cannot tell which of the two token-holders is the legitimate one."

**Code:**

```java
// Conceptual server-side logic for rotation + reuse detection
class RefreshTokenService {

    TokenPair rotateRefreshToken(String presentedToken) {
        RefreshTokenRecord record = refreshTokenRepository.find(presentedToken)
            .orElseThrow(() -> new InvalidTokenException("unknown refresh token"));

        if (record.isAlreadyUsed()) {
            // REUSE DETECTED — this exact token was already rotated away once before.
            // Don't just reject this one request: revoke the ENTIRE token family,
            // since we can no longer tell legitimate client from attacker
            refreshTokenRepository.revokeEntireFamily(record.getFamilyId());
            securityAlerting.flag("refresh token reuse detected", record.getUserId());
            throw new TokenReuseDetectedException("session revoked, re-authentication required");
        }

        record.markUsed(); // this exact token can NEVER be used again, even if
                              // this is the legitimate request

        RefreshTokenRecord newToken = new RefreshTokenRecord(
            generateToken(), record.getFamilyId(), record.getUserId()); // SAME family,
        refreshTokenRepository.save(newToken);                            // new token
        AccessToken accessToken = issueNewAccessToken(record.getUserId());
        return new TokenPair(accessToken, newToken.getValue());
    }
}
```

**Follow-up:**

I'd walk through exactly why "revoke the whole family, not just reject this request" is the correct response, since it's the subtle part: if an attacker stole a refresh token and used it *before* the legitimate client did, the legitimate client's *next* attempt to use what it thinks is still its valid token would actually be the reuse-detected event (since the attacker already rotated it away) — meaning the *legitimate* user, not the attacker, might be the one who triggers detection. This is exactly why the response has to be "force full re-authentication for this token family," rather than trying to guess which of the two callers is legitimate — there's genuinely no reliable way to tell from the server's side, and the safe, conservative response is to treat the whole family as burned. I'd also mention this pattern is exactly what's implemented by major identity providers (Auth0's refresh token rotation, for instance) and is worth adopting via a managed provider rather than hand-rolling, given how easy it is to get the family-revocation semantics subtly wrong.

**Source:** [RFC 6749 §10.4 — Refresh Token Security](https://datatracker.ietf.org/doc/html/rfc6749#section-10.4), [Auth0 — Refresh Token Rotation](https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation)

---

### 34. How Would You Secure Service-to-Service Communication?

**Answer:**

"For service-to-service (machine-to-machine, no human resource owner involved), the standard OAuth2 answer is the **client credentials grant** — a service authenticates directly to the authorization server using its own client ID and secret (or, better, a signed client assertion/mTLS certificate rather than a shared secret), and receives an access token representing *the service itself*, not any particular end user, scoped to whatever that service-to-service call is permitted to do.

Beyond the token-acquisition mechanism itself, I'd think about this in layers: **transport security** (mTLS between services, especially within a service mesh, providing both encryption and mutual authentication at the network layer, independent of the application-layer token); **token scoping** (each service-to-service credential should carry the narrowest scope that specific caller-to-callee relationship actually needs — a service shouldn't hold a token that would let it call every other service in the fleet with full privileges, just because it's technically 'internal'); and **credential lifecycle** (service credentials need the same rotation discipline as any other secret — stored in a proper secrets manager, rotated regularly, never hardcoded or committed).

For propagating a specific end-user's identity *through* a chain of internal service calls (not just service-to-service with no user context), I'd reach for a **token exchange** pattern (RFC 8693) or a signed, constrained 'on-behalf-of' token, rather than either forwarding the original user-facing token unchanged to every downstream service (over-broad — every downstream service that's ever called ends up trusted with the full original token) or having each service just trust an unsigned internal header claiming a user identity (no verification at all, trivially forgeable by anything on the internal network)."

**Code:**

```java
// Client credentials grant — service-to-service, no end user involved
@Bean
public OAuth2AuthorizedClientManager authorizedClientManager(
        ClientRegistrationRepository clients, OAuth2AuthorizedClientRepository authorizedClients) {
    OAuth2AuthorizedClientProvider provider = OAuth2AuthorizedClientProviderBuilder.builder()
        .clientCredentials() // this service authenticates AS ITSELF, not on behalf of a user
        .build();
    var manager = new DefaultOAuth2AuthorizedClientManager(clients, authorizedClients);
    manager.setAuthorizedClientProvider(provider);
    return manager;
}
```

```text
# Token exchange (RFC 8693) — propagating a constrained, re-scoped identity
# through a service chain, rather than forwarding the original user token verbatim
POST https://auth.example.com/token
grant_type=urn:ietf:params:oauth:grant-type:token-exchange
&subject_token=<original-user-access-token>
&subject_token_type=urn:ietf:params:oauth:token-type:access_token
&audience=inventory-service          <-- explicitly scoped to THIS specific
&scope=inventory:read                     downstream service and narrower scope,
                                            not a blanket forward of the original token
```

**Follow-up:**

I'd bring up the "don't just forward the original bearer token to every downstream call" principle explicitly, since it's the thing that separates a naive implementation from a properly-designed one: forwarding an unmodified, broadly-scoped user token to every service in a call chain means every one of those services is now a place where that token's full privileges could be misused or leaked, dramatically widening the blast radius of any single compromised service — token exchange, or at minimum re-issuing narrower, audience-restricted tokens per downstream hop, keeps each service's actual trust/privilege footprint minimal. I'd also mention mTLS and OAuth2 tokens as complementary, not competing, layers — mTLS proves *which service* is calling (network-layer identity), while the token proves *what it's authorized to do, and on whose behalf* (application-layer authorization) — a mature service-mesh security posture uses both together rather than relying on either alone.

**Source:** [RFC 6749 §4.4 — Client Credentials Grant](https://datatracker.ietf.org/doc/html/rfc6749#section-4.4), [RFC 8693 — OAuth 2.0 Token Exchange](https://datatracker.ietf.org/doc/html/rfc8693)

---

### 35. How Would You Model Scopes, Roles, Permissions, and Tenant Boundaries?

**Answer:**

"I'd keep these four concepts deliberately distinct, since conflating them is a common source of both security gaps and confusing authorization code.

**Scopes** are OAuth2-level — they describe what a *client application* (not necessarily the end user) has been granted permission to do on the resource owner's behalf, typically coarse-grained (`orders:read`, `orders:write`) and negotiated once, at token-issuance time, as part of the OAuth2 flow itself.

**Roles** are a coarse-grained grouping of a *user's* permissions within your own application's domain model (`ADMIN`, `SUPPORT_AGENT`, `CUSTOMER`) — a convenient shorthand for 'this set of permissions, bundled together,' but a blunt instrument if used as the *only* authorization mechanism, since real authorization needs often don't map cleanly onto a small, fixed set of roles.

**Permissions** are fine-grained, specific capabilities (`orders:cancel`, `orders:refund:approve`) — the actual atomic unit authorization decisions should usually be checked against, with roles acting as a convenient way to *assign* a bundle of permissions to a user rather than the check itself.

**Tenant boundaries**, in a multi-tenant system, are an entirely orthogonal dimension layered on top of all three — a role or permission is meaningless without also confirming the action is scoped to the correct tenant; `ADMIN` doesn't mean 'admin of everything,' it means 'admin *within their own tenant*,' and every single authorization check needs to include the tenant-scoping condition, not just the role/permission check, or you get exactly the kind of broken object-level authorization covered in question 36."

**Code:**

```java
// Scope check — OAuth2-level, what the CLIENT is permitted to do
@PreAuthorize("hasAuthority('SCOPE_orders:write')")
public void createOrder(OrderRequest request) { /* ... */ }

// Role-based shorthand for a bundle of permissions — convenient, but coarse
@PreAuthorize("hasRole('SUPPORT_AGENT')")
public void viewCustomerOrders(String customerId) { /* ... */ }

// Fine-grained permission check — the actual atomic capability being exercised
@PreAuthorize("hasAuthority('orders:refund:approve')")
public void approveRefund(String orderId) { /* ... */ }

// TENANT boundary — must be checked on EVERY authorization decision, independent
// of role/permission/scope, or a correct-looking role check still leaks across tenants
@PreAuthorize("hasAuthority('orders:refund:approve') and @tenantGuard.sameTenant(#orderId, authentication)")
public void approveRefundScoped(String orderId) {
    // @tenantGuard.sameTenant() explicitly verifies the order's tenant matches
    // the authenticated principal's tenant — a role/permission check ALONE,
    // without this, would let a support agent from Tenant A approve refunds
    // for Tenant B's orders, as long as they hold the right role/permission
}
```

**Follow-up:**

I'd bring up the practical failure mode this distinction guards against: teams that model authorization purely via roles, without a separate tenant dimension explicitly enforced at the data-access layer, are extremely prone to cross-tenant data leaks — a role check passing (`hasRole('ADMIN')`) says nothing about *which tenant's* data the admin should be restricted to, and it's very easy to write a query that's correctly permission-checked but forgets the tenant filter entirely. My general recommendation for a genuinely multi-tenant system: enforce tenant scoping as close to the data-access layer as possible (a Hibernate filter, a repository base class that always injects a tenant-ID predicate) rather than relying on every individual authorization check to remember to include it — that way tenant isolation is structurally hard to bypass by accident, rather than a rule every new endpoint has to remember to apply correctly.

**Source:** [Spring Security Reference — Authorization Architecture](https://docs.spring.io/spring-security/reference/servlet/authorization/architecture.html)

---

### 36. How Do You Prevent Broken Object-Level Authorization?

**Answer:**

"Broken Object-Level Authorization (BOLA, OWASP API Security's #1 risk) is the pattern where an API correctly checks 'is this user authenticated, and do they generally have permission to call this endpoint' but fails to check 'does this specific user actually own/have access to *this specific object identified in the request*' — the classic shape is `GET /orders/{id}` where any authenticated user can substitute any `id` and retrieve *someone else's* order, because the endpoint checks authentication and maybe a coarse role, but never checks ownership of the specific object being requested.

The structural fix is to make the ownership/access check an unavoidable, built-in part of every single data-access path, rather than something each endpoint has to remember to add individually — every query that fetches an object by ID should be scoped by the authenticated principal (or their tenant) at the query level, not fetched unconditionally and checked afterward (checking afterward at least works, but fetching pre-scoped is more defensible against a check being accidentally omitted, and it's also more efficient). I'd treat this as squarely a data-access-layer design responsibility, not something to leave to individual controller-method vigilance — a repository method signature that takes only an ID, with no principal/tenant parameter at all, is an API design smell that invites exactly this bug."

**Code:**

```java
// VULNERABLE — checks authentication, but not ownership of THIS specific object
@GetMapping("/orders/{id}")
Order getOrder(@PathVariable String id) {
    return orderRepository.findById(id); // ANY authenticated user can read ANY order
}                                           // by guessing/enumerating IDs — classic BOLA

// FIXED — ownership is baked into the query itself, not checked as an afterthought
@GetMapping("/orders/{id}")
Order getOrder(@PathVariable String id, Authentication authentication) {
    return orderRepository.findByIdAndOwnerId(id, authentication.getName())
        .orElseThrow(() -> new ResourceNotFoundException("order not found")); // 404, not 403 —
}                                                                                // per question 14,
                                                                                   // deliberately not
                                                                                   // confirming the
                                                                                   // order even exists

// A repository BASE CLASS that structurally prevents forgetting this check —
// every finder method requires a principal/tenant parameter by construction
interface TenantScopedRepository<T, ID> {
    Optional<T> findByIdAndTenantId(ID id, String tenantId); // there is no
    // findById(ID id) at all on this interface — the unscoped, dangerous
    // method literally doesn't exist as an option to accidentally call
}
```

**Follow-up:**

I'd bring up this exact vulnerability class as consistently ranking #1 in OWASP's API Security Top 10 for good reason — it's simultaneously extremely common (any team under time pressure will eventually write an ID-based lookup without the ownership check) and extremely severe (it directly leaks or lets attackers modify other users' data, often trivially discoverable via simple ID enumeration). The staff-level mitigation isn't "review every endpoint carefully" — that doesn't scale and inevitably misses something — it's structural: repository/DAO method signatures that make the unscoped, dangerous query impossible to write by accident (as in the base-class example), automated tests that specifically attempt cross-user/cross-tenant access against every object-returning endpoint, and treating a new endpoint's data-access pattern as a required code-review checklist item specifically calling out "is this query scoped to the authenticated principal or tenant."

**Source:** [OWASP API Security Top 10 — API1:2023 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)

---

### 37. How Should Authentication Context Propagate Through Asynchronous Processing?

**Answer:**

"This is exactly the concurrency-file question about propagating context across thread boundaries, applied specifically to security. `SecurityContextHolder` is `ThreadLocal`-backed by default, so an `@Async` method, a manually-submitted executor task, or any work handed off to a different thread starts with a completely empty `SecurityContext` unless something explicitly copies it across — and code that assumes `SecurityContextHolder.getContext().getAuthentication()` will 'just work' inside async code is a common, real bug.

Spring Security provides `DelegatingSecurityContextExecutor`/`DelegatingSecurityContextExecutorService` wrappers specifically for this — they wrap a plain `Executor`, capturing the calling thread's `SecurityContext` at submission time and restoring it on the executing thread for the duration of the task, then clearing it afterward (the same 'copy in, clear in finally' idiom from the concurrency file's `ThreadLocal`-leak discussion, since a pooled executor thread will be reused for a completely unrelated task next). For genuinely asynchronous, non-request-driven work — a Kafka consumer processing a message, a scheduled batch job — there's no 'calling thread's security context' to propagate at all, since there was never an HTTP request establishing one in the first place; that's a different problem, covered specifically in question 38."

**Code:**

```java
@Configuration
@EnableAsync
class AsyncSecurityConfig {
    @Bean
    Executor taskExecutor() {
        // Spring Security's own wrapper — captures the caller's SecurityContext
        // at submission time and restores it on the executing thread automatically
        return new DelegatingSecurityContextExecutor(Executors.newVirtualThreadPerTaskExecutor());
    }
}

@Service
class OrderService {
    @Async
    void sendConfirmationAsync(Order order) {
        // WITHOUT the wrapper above, this line would see an EMPTY SecurityContext —
        // no authenticated principal at all, even though the original HTTP request
        // that triggered this @Async call was fully authenticated
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        auditLog.record(auth.getName(), "sent order confirmation", order.getId());
    }
}
```

**Follow-up:**

I'd flag that `SecurityContextHolder.setStrategyName(SecurityContextHolder.MODE_INHERITABLETHREADLOCAL)` is a tempting-looking global fix that only solves half the problem — it propagates context to threads created via `new Thread()`, but does **nothing** for pooled-executor tasks (which reuse existing threads rather than creating new ones), which is the far more common real-world pattern (`@Async`, `ExecutorService`, reactive schedulers) — so relying on it as a blanket solution gives a false sense of correctness. I'd also mention that this exact propagation gap is one of the most common causes of "authorization works fine synchronously but silently fails/misbehaves for background-processed requests" bugs in real systems, and that the fix needs to be applied consistently at every executor boundary in an application, not just the first one someone happens to test.

**Source:** [Spring Security Reference — Concurrency Support](https://docs.spring.io/spring-security/reference/servlet/integrations/concurrency.html)

---

### 38. How Would You Design Authorization for Kafka Consumers Where There Is No HTTP Request?

**Answer:**

"The core problem is that all the mechanisms discussed so far — the filter chain, `SecurityContextHolder`, bearer tokens on a request — are fundamentally built around 'there's an incoming HTTP request carrying credentials.' A Kafka consumer processing a message has no such thing: there's no per-message 'Authorization header,' and the concept of 'the currently authenticated user' doesn't map cleanly onto an asynchronous, potentially-much-later-processed event.

My approach splits into two different concerns. First, **consumer-level authorization** — does *this consumer/service* have legitimate access to *this topic* at all — is handled at the messaging-infrastructure layer, not the application layer: Kafka ACLs (or an equivalent authorization layer in a managed service like Confluent/MSK) control which service principals can read/write which topics, enforced by the broker itself, independent of anything in application code. Second, **acting-on-behalf-of-a-user authorization** — if a message represents an action originally initiated by a specific end user (e.g., 'user X requested a refund,' now being processed asynchronously) — requires the *event itself* to carry enough identity/authorization context for the consumer to make a correct decision, since there's no live request to derive it from. This usually means embedding a validated identity claim (the user ID, and ideally a short-lived, narrowly-scoped token or a pre-validated claim, not raw unvalidated data) directly in the event payload or headers at *publish* time — when the original authenticated request context was still available — so the consumer can re-derive and re-check authorization using that embedded context, rather than trying to reconstruct 'who was this for' after the fact."

**Code:**

```java
// AT PUBLISH TIME — while the original authenticated HTTP request context still
// exists — embed the necessary identity/authorization context INTO the event itself
@PostMapping("/orders/{id}/refund")
void requestRefund(@PathVariable String id, Authentication authentication) {
    RefundRequestedEvent event = RefundRequestedEvent.builder()
        .orderId(id)
        .requestedByUserId(authentication.getName()) // captured HERE, while
        .requestedByTenantId(getTenantId(authentication)) // the real auth context
        .build();                                            // is actually available
    kafkaTemplate.send("refund-requests", event);
}

// AT CONSUME TIME — no HTTP request, no SecurityContext — re-derive authorization
// from the context embedded in the event itself, validated against current state
@KafkaListener(topics = "refund-requests")
void handleRefundRequest(RefundRequestedEvent event) {
    Order order = orderRepository.findById(event.getOrderId())
        .orElseThrow();
    // explicit re-validation against CURRENT state — the user's permissions
    // may have changed since the event was originally published
    if (!authorizationService.canApproveRefund(event.getRequestedByUserId(), order)) {
        deadLetterQueue.send(event, "authorization no longer valid at processing time");
        return;
    }
    refundService.process(order);
}
```

**Follow-up:**

I'd bring up the specific staleness risk this design has to account for explicitly: by the time an asynchronously-processed event is actually consumed, the user's permissions might have legitimately changed (role revoked, account suspended, tenant access removed) since the event was originally published — so "authorization was valid at publish time" is not the same guarantee as "authorization is valid now," and a consumer handling anything sensitive should re-validate against *current* authorization state at consume time, not just trust the embedded claim blindly as if it were still current truth. I'd also mention Kafka ACLs and application-level authorization as genuinely separate, complementary layers — broker-level ACLs answer "can this service read this topic at all" (infrastructure-level, coarse), while the embedded-claim-plus-revalidation pattern answers "is this specific action, on behalf of this specific user, still authorized right now" (application-level, fine-grained) — conflating the two, or assuming broker-level ACLs are sufficient application authorization, is a real gap.

**Source:** [Apache Kafka Documentation — Authorization and ACLs](https://kafka.apache.org/documentation/#security_authz), [OWASP API Security — Broken Function Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa5-broken-function-level-authorization/)

---

### 39. How Do You Prevent Confused-Deputy Problems in Downstream Service Calls?

**Answer:**

"A confused-deputy vulnerability is when a service — trusted with some elevated privilege to do its job — can be tricked by a caller into misusing that privilege on the caller's behalf, beyond what the caller itself should actually be authorized to do. The classic shape in a service-to-service context: Service A has broad access to Service B (because Service A legitimately needs *some* access to B for its own normal function), and if Service A blindly forwards *whatever a client asked it to do* directly to Service B using its own elevated service-to-service credential, without checking whether the *original calling user* was actually authorized for that specific action, the client has effectively borrowed Service A's greater privilege to do something it couldn't do directly.

The core defenses: never let a service's own broad service-to-service credential substitute for checking the *original caller's* actual authorization — every hop needs its own authorization check against the actual originating principal's permissions, not just 'am I, the calling service, generally trusted to talk to this downstream service.' This is exactly what audience-restricted tokens and token exchange (question 34) are for — ensuring a downstream service call carries a token that's scoped to what the *original* caller is actually permitted, rather than the intermediate service's own broader privilege being transparently exercised on the caller's behalf without re-verification."

**Code:**

```java
// VULNERABLE — Service A forwards the request to Service B using its OWN
// broad service-to-service credential, without checking if the ORIGINAL caller
// was actually authorized for this specific action
@PostMapping("/proxy/inventory/{sku}/adjust")
void adjustInventory(@PathVariable String sku, @RequestBody AdjustmentRequest request) {
    // Service A's OWN client-credentials token has broad inventory-write access —
    // used here regardless of what the ORIGINAL caller (whoever called Service A)
    // was actually permitted to do
    inventoryServiceClient.adjust(sku, request, serviceAOwnCredential);
}

// FIXED — explicitly check the ORIGINAL caller's actual authorization BEFORE
// exercising Service A's own broader downstream privilege on their behalf
@PostMapping("/proxy/inventory/{sku}/adjust")
void adjustInventoryFixed(@PathVariable String sku, @RequestBody AdjustmentRequest request,
                            Authentication originalCaller) {
    if (!authorizationService.canAdjustInventory(originalCaller, sku)) {
        throw new AccessDeniedException("caller not authorized for this specific adjustment");
    }
    // only AFTER confirming the ORIGINAL caller was genuinely authorized do we
    // exercise Service A's own (broader) downstream privilege on their behalf
    inventoryServiceClient.adjust(sku, request, serviceAOwnCredential);
}
```

**Follow-up:**

I'd bring up the classic, canonical confused-deputy example for context — the original 1988 case involved a compiler service with legitimate write access to a shared billing log file, which a user could trick into overwriting an *arbitrary* file by supplying a crafted output filename, since the compiler used its *own* elevated file-write privilege without checking whether the requesting user actually had permission to write to that specific target file. The modern microservices version is structurally identical: any service holding a broader downstream privilege than an individual caller should have is a potential confused deputy the moment it forwards caller-controlled input into that privileged downstream call without its own independent authorization check. I'd frame the general defense as: **never let a service's own credential silently substitute for verifying the original requester's actual, specific authorization** — every privilege-bearing hop needs its own check against the real originating principal, and object-capability-style design (only ever holding references/tokens scoped to exactly what's needed, never a broad ambient credential) is the deeper architectural principle this specific fix is an instance of.

**Source:** [OWASP — Confused Deputy](https://en.wikipedia.org/wiki/Confused_deputy_problem), [RFC 8693 — OAuth 2.0 Token Exchange](https://datatracker.ietf.org/doc/html/rfc8693)

---

### 40. What Security Information Is Safe to Log?

**Answer:**

"The general rule: log enough to investigate and audit *what happened and by whom*, without logging anything that itself becomes a credential or a privacy liability if the logs are ever read by someone who shouldn't see it — and logs get read by a surprisingly wide audience over their lifetime (on-call engineers, log-aggregation platforms, sometimes third-party log-shipping vendors), so 'only trusted people will see this' is a weak assumption to build on.

**Safe/expected to log**: user IDs (not necessarily emails/PII, depending on your privacy posture), request IDs/trace IDs, the *type* of authentication event (login success/failure, token refresh, permission denied), timestamps, source IP (with appropriate retention/privacy handling), and the specific resource/action involved in an authorization decision.

**Never log**: raw passwords (obviously, but this includes accidentally logging an entire request body that happens to contain one), full access/refresh/ID tokens (a leaked log line containing a valid bearer token is functionally equivalent to a credential leak — treat log exposure as seriously as you'd treat exposing the token itself), API keys/client secrets, and full credit card numbers or other regulated PII beyond what's explicitly required and appropriately protected. A specific, easy-to-miss trap: logging an entire incoming request or an entire outgoing response object for debugging purposes, without realizing the object happens to contain an `Authorization` header or a token field somewhere inside it — generic request/response logging middleware is a very common accidental source of token leaks into logs."

**Code:**

```java
// DANGEROUS — logs the FULL Authorization header, which IS the bearer token itself
log.info("incoming request: {} {}", request.getMethod(), request.getHeader("Authorization"));

// DANGEROUS — a generic "log everything for debugging" filter that doesn't
// know or care that the request body contains a password field
log.debug("request body: {}", requestBody); // requestBody might be a LoginRequest
                                              // containing a raw password field

// SAFE — logs what's needed for investigation, explicitly redacts anything sensitive
log.info("authentication event: user={} outcome={} requestId={} sourceIp={}",
    maskUserId(username), outcome, requestId, sourceIp); // NO token, NO password,
                                                            // NO full request body

// A redacting log filter, applied globally, as a structural safeguard rather
// than trusting every individual log statement to remember not to log secrets
public class SensitiveFieldRedactingFilter extends OncePerRequestFilter {
    private static final Set<String> SENSITIVE_HEADERS = Set.of("authorization", "cookie", "x-api-key");

    // ... wraps logging so these headers are ALWAYS masked, regardless of
    // whether an individual log statement remembered to do so itself
}
```

**Follow-up:**

I'd bring up that this is exactly the kind of thing that shouldn't rely on every developer remembering the rule correctly at every single log statement — a structural safeguard (a logging filter/interceptor that automatically redacts known-sensitive header names and field patterns before anything reaches the actual log sink, applied globally rather than trusted to individual call sites) is far more reliable than a coding-standard document saying "don't log tokens." I'd also mention that log *retention* and *access control* are part of the same overall concern, not a separate problem: even correctly-redacted logs containing user IDs and behavioral data still need appropriate retention limits and access restrictions under most privacy regulations (GDPR, CCPA), so "we redacted the actual secrets" doesn't fully close out the security/privacy review for a logging pipeline — it's a necessary but not sufficient step.

**Source:** [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

---

### 41. How Would You Investigate Intermittent `401` Versus `403` Responses?

**Answer:**

"First, per question 14, I'd confirm the two are being reported correctly and distinctly in whatever logging/monitoring is available — if they're conflated into one generic 'auth error' metric, I'd fix that first, since the two point at completely different root-cause categories.

For **intermittent 401s** specifically — since a *consistent* 401 usually just means bad credentials, but *intermittent* implies something is failing only sometimes — my prime suspects are: clock skew between the resource server and the token issuer causing `exp`/`nbf` checks to fail right at the edges of a token's validity window (a token that should be valid gets rejected as expired, or not-yet-valid, purely due to clock drift); a JWKS key-rotation issue where a resource server hasn't yet picked up a newly-rotated key and rejects tokens signed with it (tying directly to question 29); or a load-balanced fleet where only *some* instances have a stale JWKS cache or misconfiguration, so the same request succeeds or fails depending purely on which instance happens to handle it — a classic 'works when I retry' symptom.

For **intermittent 403s**, I'd suspect: a cache (permissions/roles cached with a TTL) serving stale authorization data that hasn't caught up with a recent, legitimate permission change; a race condition where an authorization check runs against data that's being concurrently modified (a role being granted in one transaction while a request checking that exact role runs concurrently against not-yet-committed data); or, in a multi-tenant/multi-region system, a request being routed to a region/instance that hasn't yet received a recent authorization-data replication update."

**Code:**

```bash
# Correlate the SPECIFIC response code against instance/pod identity — a classic
# "some instances behave differently" pattern points at inconsistent config/cache
# state across a fleet, not a genuine, consistent authorization decision
grep "status=401\|status=403" access.log | awk '{print $INSTANCE_ID_FIELD, $STATUS}' | sort | uniq -c

# Check for clock skew directly — a surprisingly common, easy-to-overlook root
# cause for intermittent, edge-of-validity-window 401s
date -u  # on the resource server
# compare against the issuer's own reported time (many issue a Date header,
# or expose server time via a status endpoint) — even a few seconds of drift
# can flip a token from "valid" to "expired" right at its exp boundary
```

```java
// Adding explicit, structured logging around JWT validation failures specifically —
// distinguishing WHICH validator failed (signature vs exp vs aud vs jti-revoked)
// turns "intermittent 401s" from a mystery into a specific, actionable signal
OAuth2TokenValidator<Jwt> loggingValidator = jwt -> {
    OAuth2TokenValidatorResult result = defaultValidator.validate(jwt);
    if (!result.hasErrors()) return result;
    log.warn("JWT validation failed: kid={} errors={} exp={} now={}",
        jwt.getHeaders().get("kid"), result.getErrors(), jwt.getExpiresAt(), Instant.now());
    return result;
};
```

**Follow-up:**

I'd emphasize that the single highest-leverage diagnostic step is almost always adding structured, specific logging *at the point of the actual authorization/authentication decision* — logging not just "401" or "403" but *which specific check failed and why* (expired vs bad signature vs missing audience vs role check failed vs stale cache) — since without that granularity, "investigate intermittent 401s" devolves into speculative guessing across a huge space of possible causes. I'd also mention that intermittent-by-instance patterns (some pods failing, others not, for the identical request) are worth checking first specifically because they're both common (config drift, cache staleness across a fleet) and cheap to rule in or out via a simple correlation query, before investing time in deeper token-validation-logic hypotheses.

**Source:** [Spring Security Reference — Troubleshooting](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html), [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

---

### 42. Design an Authentication and Authorization Architecture for a Multi-Tenant Platform

**Answer:**

"I'd structure this around a few explicit layers, each addressing a distinct concern, rather than one monolithic 'auth system.'

**Identity layer**: a central identity provider (either a managed service — Okta, Auth0, Cognito — or a self-hosted OIDC-compliant authorization server like Keycloak or Spring Authorization Server) handling authentication for all tenants, issuing OIDC ID tokens for user identity and OAuth2 access tokens for API authorization. Tenant identification needs to be established *at* authentication time, embedded as a claim in the issued token (a `tenant_id` claim) — not derived later from something client-suppliable like a header or a request parameter, which would let a malicious client simply claim to be a different tenant.

**Authorization layer**: fine-grained permission checks (question 35's roles/permissions model) always evaluated *together with* the tenant claim from the token — every single data-access path scoped by tenant at the query/repository level as a structural default (question 36's BOLA prevention, applied specifically to tenant boundaries here), not as an optional check individual endpoints might forget.

**Tenant isolation strategy**: a genuine architectural decision with real trade-offs — separate databases per tenant (strongest isolation, most operational overhead), a shared database with a tenant-ID column and row-level security/mandatory query filtering (moderate isolation, much less operational overhead, but correctness now depends on every query correctly applying the filter), or a hybrid (shared infrastructure for most tenants, dedicated infrastructure for specific high-sensitivity or high-scale tenants) — and I'd pick based on the platform's actual sensitivity/scale/compliance requirements rather than defaulting to whichever is easiest to build first.

**Cross-cutting concerns**: propagating tenant + user identity consistently through async processing (question 37/38) and service-to-service calls (question 34), auditing every authorization decision with enough detail to investigate a suspected cross-tenant leak after the fact, and a deliberate incident-response plan specifically for 'a cross-tenant data leak was discovered' — since for a multi-tenant platform, that's one of the most severe possible incident categories and deserves its own tested runbook, not an improvised response."

**Code:**

```java
// tenant_id embedded in the token AT AUTHENTICATION TIME by the identity
// provider — never derived from a client-suppliable header/parameter
{
  "iss": "https://auth.platform.example.com",
  "sub": "user-12345",
  "tenant_id": "tenant-acme-corp",   // established by the IdP during login,
  "aud": "platform-api",              // NOT something the client can set itself
  "scope": "orders:read orders:write"
}
```

```java
// Structural tenant enforcement at the data-access layer — every repository
// method requires the tenant explicitly, making the unscoped query impossible
@Repository
interface OrderRepository extends JpaRepository<Order, String> {
    Optional<Order> findByIdAndTenantId(String id, String tenantId); // the ONLY
    // way to look up an order by ID — there is no findById(id) exposed at all
}

@Service
class OrderService {
    Order getOrder(String id, Jwt jwt) {
        String tenantId = jwt.getClaimAsString("tenant_id"); // from the VALIDATED
        return orderRepository.findByIdAndTenantId(id, tenantId) // token, not a
            .orElseThrow(() -> new ResourceNotFoundException("order not found")); // header
    }
}
```

**Follow-up:**

I'd bring up Hibernate/JPA's `@Filter` mechanism (or an equivalent row-level-security feature at the database level, e.g. PostgreSQL RLS) as a genuinely stronger structural defense than relying on every repository method to remember the tenant parameter — a database-enforced row-level-security policy that automatically restricts every query to the current session's tenant, set once per connection/transaction, means even a query written by a developer who *forgot* to add tenant scoping still can't leak across tenants, because the database itself refuses to return rows outside the current tenant regardless of what the application-level query asked for. This is the kind of defense-in-depth I'd specifically push for in a Staff-level design review for a multi-tenant platform — not relying on a single layer (application code discipline) to be the only thing standing between "correct" and "catastrophic cross-tenant data leak," given how severe and reputation-damaging that specific failure category is compared to most other bug classes.

**Source:** [PostgreSQL — Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html), [Hibernate — Filters](https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html#pc-filters), [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Spring Security Reference — Architecture | https://docs.spring.io/spring-security/reference/servlet/architecture.html |
| Spring Security Reference — Authentication | https://docs.spring.io/spring-security/reference/servlet/authentication/index.html |
| `SecurityContextHolder` Javadoc | https://docs.spring.io/spring-security/site/docs/current/api/org/springframework/security/core/context/SecurityContextHolder.html |
| Spring Security Reference — Method Security | https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html |
| Spring Security Reference — CSRF | https://docs.spring.io/spring-security/reference/features/exploits/csrf.html |
| Spring Security Reference — CORS | https://docs.spring.io/spring-security/reference/servlet/integrations/cors.html |
| OWASP CSRF Prevention Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html |
| Spring Security Reference — Session Management | https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html |
| Spring Security Reference — OAuth2 Resource Server | https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/index.html |
| RFC 7636 — PKCE | https://datatracker.ietf.org/doc/html/rfc7636 |
| Spring Security Reference — OAuth2 Login | https://docs.spring.io/spring-security/reference/servlet/oauth2/login/index.html |
| RFC 6749 — OAuth 2.0 | https://datatracker.ietf.org/doc/html/rfc6749 |
| OAuth 2.1 draft | https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1 |
| RFC 8414 — Authorization Server Metadata | https://datatracker.ietf.org/doc/html/rfc8414 |
| OpenID Connect Core | https://openid.net/specs/openid-connect-core-1_0.html |
| RFC 7662 — Token Introspection | https://datatracker.ietf.org/doc/html/rfc7662 |
| Spring Security Reference — Opaque Token | https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/opaque-token.html |
| Spring Security Reference — JWT | https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html |
| RFC 7519 — JSON Web Token | https://datatracker.ietf.org/doc/html/rfc7519 |
| RFC 7517 — JSON Web Key | https://datatracker.ietf.org/doc/html/rfc7517 |
| RFC 7009 — OAuth 2.0 Token Revocation | https://datatracker.ietf.org/doc/html/rfc7009 |
| OWASP JWT Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html |
| OWASP Cross Site Scripting Prevention Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html |
| Auth0 — Refresh Token Rotation | https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation |
| RFC 8693 — OAuth 2.0 Token Exchange | https://datatracker.ietf.org/doc/html/rfc8693 |
| OWASP API Security Top 10 | https://owasp.org/API-Security/editions/2023/en/0x11-t10/ |
| OWASP — Confused Deputy | https://en.wikipedia.org/wiki/Confused_deputy_problem |
| OWASP Logging Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html |
| PostgreSQL — Row Security Policies | https://www.postgresql.org/docs/current/ddl-rowsecurity.html |
| Hibernate — Filters | https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html#pc-filters |
| Apache Kafka — Authorization and ACLs | https://kafka.apache.org/documentation/#security_authz |
