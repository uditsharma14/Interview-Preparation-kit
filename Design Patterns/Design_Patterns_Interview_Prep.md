# Design Patterns — Interview Prep (Gang-of-Four Patterns, with Code & Sources)

> **Target level:** Basic → Staff — organized by Gang-of-Four category (Creational → Structural → Behavioral), not by difficulty, since real interviews jump between these freely; the Staff-level extension in each question is where the deeper judgment (including when a pattern is the wrong tool) lives · **Baseline:** the canonical Gang-of-Four definitions (Gamma, Helm, Johnson, Vlissides — *Design Patterns: Elements of Reusable Object-Oriented Software*, 1994); code examples in Java 21, noting the real JDK/Spring class that already implements each pattern where one exists · **Last verified:** 2026-08-24 · **Prerequisites:** core Java OOP — interfaces, inheritance versus composition, abstract classes

How to use this: each pattern has a **Core answer** (100–180 words — roughly what you'd actually say out loud in 40–70 seconds), a **Staff-level extension** covering the pattern's most common real-world JDK/Spring instance and, just as important, when reaching for the pattern is overkill for what a simpler design would do just as well, a self-contained, compilable **Example**, **Follow-up questions**, and **Sources**. Fifteen of the Gang of Four's original twenty-three patterns are covered here — the ones that come up constantly in real interviews — grouped the traditional way: **Creational** (patterns concerned with how objects get created), **Structural** (patterns concerned with how objects and classes compose into larger structures), and **Behavioral** (patterns concerned with how objects communicate and distribute responsibility). A named pattern is a tool, not a badge of sophistication — the Staff-level judgment throughout is knowing when a pattern earns its indirection and when it's solving a problem the code doesn't actually have.

<!-- toc -->
## Table of Contents

- [Creational Patterns](#creational-patterns)
  - [1. Singleton](#1-singleton)
  - [2. Factory Method](#2-factory-method)
  - [3. Builder](#3-builder)
- [Structural Patterns](#structural-patterns)
  - [4. Adapter](#4-adapter)
  - [5. Decorator](#5-decorator)
  - [6. Facade](#6-facade)
  - [7. Proxy](#7-proxy)
  - [8. Composite](#8-composite)
- [Behavioral Patterns](#behavioral-patterns)
  - [9. Observer](#9-observer)
  - [10. Strategy](#10-strategy)
  - [11. Command](#11-command)
  - [12. Iterator](#12-iterator)
  - [13. State](#13-state)
  - [14. Template Method](#14-template-method)
  - [15. Chain of Responsibility](#15-chain-of-responsibility)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## Creational Patterns

### 1. Singleton

**Core answer:**

"Singleton ensures a class has exactly one instance and provides a single, global access point to it. The classic motivation is coordinating access to a genuinely shared resource — a configuration object, a connection pool, a logging facility — where more than one instance would cause real bugs (inconsistent state, duplicated resource allocation). The modern, safest Java implementation is the **enum singleton**: `enum ConfigurationManager { INSTANCE; ... }` — the JVM guarantees enum instance initialization is thread-safe and happens exactly once, it's automatically serialization-safe with no extra code needed, and it's immune to the reflection-based attack that can call `setAccessible(true)` on a private constructor and instantiate a 'singleton' class more than once anyway. The older idiom — a private constructor, a static instance field, and a static accessor — requires careful handling (double-checked locking with a `volatile` field) to be both lazily initialized and thread-safe without the enum trick."

**Staff-level extension:**

Push back on Singleton as frequently overused — it's often really "global mutable state in a trenchcoat," and its biggest real cost is making unit testing hard: a hidden global dependency is difficult to substitute with a test double, since a test can't easily construct a different instance for isolation. In a Spring context specifically, an ordinary `@Component`/`@Service` bean is *already* a singleton by default (Spring's default bean scope) without any hand-rolled Singleton-pattern boilerplate — the DI container manages the one instance and its lifecycle, and, critically, a different implementation can be substituted for a test via a different bean definition, which a hardcoded static singleton can't do at all. If a framework already manages object lifecycles, hand-writing the GoF Singleton pattern on top of it is almost always unnecessary.

**Example:**

```java
import java.util.HashMap;
import java.util.Map;

public class SingletonDemo {
    enum ConfigurationManager {
        INSTANCE;

        private final Map<String, String> settings = new HashMap<>();

        void set(String key, String value) { settings.put(key, value); }
        String get(String key) { return settings.get(key); }
    }

    public static void main(String[] args) {
        ConfigurationManager.INSTANCE.set("env", "production"); // no "new" possible at all
        System.out.println(ConfigurationManager.INSTANCE.get("env")); // production
    }
}
```

**Follow-up questions:**

- *"Why is the enum-based singleton preferred over the classic private-constructor approach?"* — Enum instance initialization is inherently thread-safe (guaranteed by the JVM), immune to reflection-based re-instantiation the way a private constructor isn't automatically, and automatically serialization-safe with no `readResolve()` override needed.
- *"Why does a Spring singleton-scoped bean make the hand-written GoF pattern unnecessary?"* — Spring's container already guarantees one instance per bean definition and manages its lifecycle, and — unlike a hardcoded static singleton — a different implementation can be substituted for testing via a different bean.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Singleton](https://refactoring.guru/design-patterns/singleton)

---

### 2. Factory Method

**Core answer:**

"Factory Method defines an interface for creating an object, but lets subclasses decide which concrete class to instantiate. Instead of a base class calling `new ConcreteType()` directly — which would hardcode exactly one concrete type and make the base class unable to work with any other — it calls an abstract 'factory method' that each subclass overrides to produce the specific type that subclass needs. The caller working with the base class never names a concrete class at all; it just calls the base class's other methods, which internally rely on the factory method to get the object they need to work with. This decouples the code that *uses* an object from the code that *decides which concrete type* to create, which matters specifically when a class hierarchy needs to be extended with new types later without modifying the existing base class's logic — new subclasses just override the factory method with their own concrete type."

**Staff-level extension:**

Factory Method is easy to over-apply to a case that doesn't actually need it — if there's only ever going to be one concrete type, or if the concrete type is known and fixed at the call site anyway, introducing an abstract creator class and a subclass hierarchy just to produce that one type is pure indirection with no real payoff. It earns its complexity specifically when the *set* of concrete types genuinely needs to grow over time, independently of the code that consumes them — Spring's `BeanFactory` is a real-world instance of this: the container decides which concrete bean implementation to hand back for a given type, and calling code depends only on the abstraction, never a `new` call to a specific class.

**Example:**

```java
public class FactoryMethodDemo {
    interface Notification {
        String send(String message);
    }

    static class EmailNotification implements Notification {
        public String send(String message) { return "Email: " + message; }
    }

    static class SmsNotification implements Notification {
        public String send(String message) { return "SMS: " + message; }
    }

    abstract static class NotificationCreator {
        abstract Notification createNotification(); // the "factory method" — subclasses decide the concrete type

        String notify(String message) {
            Notification notification = createNotification(); // never names a concrete class here
            return notification.send(message);
        }
    }

    static class EmailNotificationCreator extends NotificationCreator {
        Notification createNotification() { return new EmailNotification(); }
    }

    public static void main(String[] args) {
        NotificationCreator creator = new EmailNotificationCreator();
        System.out.println(creator.notify("Hello")); // Email: Hello
    }
}
```

**Follow-up questions:**

- *"When is Factory Method pure overkill?"* — When there's only ever one concrete type, or the concrete type is already known at the call site — the abstract creator hierarchy adds indirection with no corresponding flexibility payoff.
- *"How does Spring's `BeanFactory` relate to this pattern?"* — It's a real-world Factory Method instance — the container decides which concrete bean implementation to return for a requested type, and calling code depends only on the abstraction, never a direct `new` call.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Factory Method](https://refactoring.guru/design-patterns/factory-method)

---

### 3. Builder

**Core answer:**

"Builder separates the construction of a complex object from its final representation, so the same step-by-step construction process can produce different configurations of the result. It's the standard answer to the 'telescoping constructor' problem — a class with many optional fields that would otherwise need a large number of overloaded constructors (or one constructor with a long, error-prone, position-dependent parameter list) to cover every combination of fields a caller might want set. A Builder instead exposes one method per settable field, each returning the builder itself so calls can be chained fluently, plus a final `build()` method that validates and produces the finished, often immutable, object. This makes optional parameters read clearly at the call site by name (`.cheese(true).pepperoni(true)`) instead of as an ambiguous sequence of positional constructor arguments, and it lets the target class stay genuinely immutable — nothing about the object can be mutated after `build()` returns."

**Staff-level extension:**

Builder is worth reaching for specifically once a class has several optional fields or the construction itself needs validation logic that doesn't belong inside a plain constructor — for a class with two or three always-required fields and nothing optional, a Builder is unnecessary ceremony over a plain constructor. Lombok's `@Builder` annotation generates this exact boilerplate automatically in real Java codebases, which is worth naming directly: knowing when to reach for the generated version instead of hand-writing it is itself a practical, real-world judgment call, not just knowing the pattern exists.

**Example:**

```java
public class BuilderDemo {
    static final class Pizza {
        private final String size;
        private final boolean cheese;
        private final boolean pepperoni;

        private Pizza(Builder builder) {
            this.size = builder.size;
            this.cheese = builder.cheese;
            this.pepperoni = builder.pepperoni;
        }

        static class Builder {
            private final String size; // required
            private boolean cheese = false; // optional, sensible default
            private boolean pepperoni = false;

            Builder(String size) { this.size = size; }
            Builder cheese(boolean value) { this.cheese = value; return this; }
            Builder pepperoni(boolean value) { this.pepperoni = value; return this; }
            Pizza build() { return new Pizza(this); }
        }

        public String toString() {
            return size + " pizza" + (cheese ? " with cheese" : "") + (pepperoni ? " with pepperoni" : "");
        }
    }

    public static void main(String[] args) {
        Pizza pizza = new Pizza.Builder("Large").cheese(true).pepperoni(true).build();
        System.out.println(pizza); // Large pizza with cheese with pepperoni
    }
}
```

**Follow-up questions:**

- *"When is a Builder unnecessary?"* — When a class has only a couple of always-required fields and nothing optional — a plain constructor already reads clearly, and a Builder just adds ceremony with no readability or flexibility payoff.
- *"How does Lombok's `@Builder` relate to hand-writing this pattern?"* — It generates the exact same boilerplate (a static nested Builder class, chained setter-style methods, a `build()` method) automatically from annotations — real codebases commonly reach for the generated version rather than hand-writing it.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Builder](https://refactoring.guru/design-patterns/builder)

---

## Structural Patterns

### 4. Adapter

**Core answer:**

"Adapter converts the interface of one class into another interface a client expects, letting classes work together that couldn't otherwise, because their interfaces are incompatible. It's the object-oriented equivalent of a physical power adapter — it doesn't change either side's internal implementation, it just translates calls at the boundary between them. This comes up constantly when integrating a legacy system, a third-party library, or any external component whose API shape doesn't match what the rest of the codebase expects: rather than changing the legacy component (often impossible) or scattering translation logic throughout every call site that touches it, an Adapter class wraps the incompatible component and implements the interface the rest of the code actually expects, translating each call internally, once, in one place. Callers depend only on the target interface and never need to know the adapter is wrapping something with a completely different shape underneath."

**Staff-level extension:**

Adapter and the Anti-Corruption Layer pattern from architecture-level design (covered in the Microservices & Architecture Patterns guide) are the same underlying idea applied at different scales — a class-level interface translation versus a service-boundary-level domain-model translation — and recognizing that connection is worth stating explicitly in an interview, rather than treating them as unrelated. Worth distinguishing precisely from Facade: Adapter makes an *existing, incompatible* interface usable by translating it to match one a client already expects; Facade simplifies access to a *complex but otherwise compatible* subsystem by introducing a new, simpler interface on top of it — Adapter is about compatibility, Facade is about simplicity.

**Example:**

```java
public class AdapterDemo {
    interface ModernPaymentProcessor {
        void pay(double amountInDollars);
    }

    static class LegacyPaymentGateway { // incompatible interface — expects cents, different method name
        void makePayment(long amountInCents) {
            System.out.println("Legacy gateway charged " + amountInCents + " cents");
        }
    }

    static class PaymentGatewayAdapter implements ModernPaymentProcessor {
        private final LegacyPaymentGateway legacyGateway;
        PaymentGatewayAdapter(LegacyPaymentGateway legacyGateway) { this.legacyGateway = legacyGateway; }

        public void pay(double amountInDollars) {
            long cents = Math.round(amountInDollars * 100);
            legacyGateway.makePayment(cents); // translates the call, once, in one place
        }
    }

    public static void main(String[] args) {
        ModernPaymentProcessor processor = new PaymentGatewayAdapter(new LegacyPaymentGateway());
        processor.pay(19.99); // Legacy gateway charged 1999 cents
    }
}
```

**Follow-up questions:**

- *"What's the difference between Adapter and Facade?"* — Adapter makes an existing, incompatible interface usable by translating it to one a client already expects; Facade introduces a new, simpler interface over a complex but otherwise compatible subsystem — one is about compatibility, the other about simplicity.
- *"How does this relate to an anti-corruption layer at the architecture level?"* — Same underlying idea at a bigger scale — Adapter translates at a class interface boundary, an anti-corruption layer translates at a service/domain-model boundary, both isolating one side from the other's incompatible shape.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Adapter](https://refactoring.guru/design-patterns/adapter)

---

### 5. Decorator

**Core answer:**

"Decorator attaches additional responsibilities to an object dynamically, providing a flexible alternative to subclassing for extending behavior. A decorator implements the same interface as the object it wraps, holds a reference to the wrapped object, and adds its own behavior before or after delegating the call to the wrapped object — and because it implements the same interface, decorators can be stacked, each one adding another layer of behavior on top of the last, all interchangeable with the original undecorated object from the caller's point of view. This avoids the combinatorial explosion a pure-subclassing approach would need to cover every combination of optional behaviors (a `MilkAndSugarCoffee` subclass, a `SugarOnlyCoffee` subclass, and so on for every combination) — instead, each behavior is its own small decorator class, composed together at runtime in whatever combination is actually needed. `java.io`'s stream classes (`BufferedReader` wrapping a `Reader`) are the canonical real JDK example of this exact pattern."

**Staff-level extension:**

The precise reason Decorator scales better than subclassing for combinable behaviors is worth being able to state directly: `N` independent, combinable behaviors need only `N` decorator classes, each stacked in any combination at runtime, versus up to `2^N` subclasses to cover every combination if done through inheritance alone. The real cost worth naming honestly: a deeply stacked chain of decorators can become genuinely hard to debug, since the actual behavior is spread across however many layers are currently wrapped, and stepping through a stack trace means stepping through every decorator in the chain, not one class with the combined logic visible in one place.

**Example:**

```java
public class DecoratorDemo {
    interface Coffee {
        double cost();
        String description();
    }

    static class SimpleCoffee implements Coffee {
        public double cost() { return 2.0; }
        public String description() { return "Coffee"; }
    }

    abstract static class CoffeeDecorator implements Coffee {
        protected final Coffee decorated;
        CoffeeDecorator(Coffee decorated) { this.decorated = decorated; }
    }

    static class MilkDecorator extends CoffeeDecorator {
        MilkDecorator(Coffee decorated) { super(decorated); }
        public double cost() { return decorated.cost() + 0.5; }
        public String description() { return decorated.description() + " + Milk"; }
    }

    static class SugarDecorator extends CoffeeDecorator {
        SugarDecorator(Coffee decorated) { super(decorated); }
        public double cost() { return decorated.cost() + 0.25; }
        public String description() { return decorated.description() + " + Sugar"; }
    }

    public static void main(String[] args) {
        Coffee order = new SugarDecorator(new MilkDecorator(new SimpleCoffee()));
        System.out.println(order.description() + " = $" + order.cost()); // Coffee + Milk + Sugar = $2.75
    }
}
```

**Follow-up questions:**

- *"Why does Decorator scale better than subclassing for combinable behaviors?"* — `N` independent behaviors need only `N` decorator classes, stacked in any combination at runtime, versus up to `2^N` subclasses to cover every combination if handled through inheritance alone.
- *"What's the real cost of a deeply stacked decorator chain?"* — Debugging gets harder, since the actual behavior is spread across however many layers are wrapped — a stack trace has to be walked through every decorator in the chain rather than one class showing the combined logic in one place.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Decorator](https://refactoring.guru/design-patterns/decorator), [`InputStream` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/InputStream.html)

---

### 6. Facade

**Core answer:**

"Facade provides a single, unified, simplified interface to a set of interfaces in a more complex subsystem, making that subsystem easier to use for the common cases without hiding or removing access to its individual parts for callers that genuinely need finer control. A subsystem with several classes that must be used together in a specific sequence — initialize this, then configure that, then call these three methods in order — forces every caller to know and correctly repeat that sequence; a Facade class encapsulates that sequence once, behind one or a few simple methods, so most callers only ever need to call the Facade, not understand or correctly coordinate the subsystem's internals themselves. This doesn't reduce the subsystem's actual complexity — it just concentrates the knowledge of how to use it correctly in one place, rather than requiring every caller to rediscover and correctly replicate that same coordination logic independently."

**Staff-level extension:**

A Facade should be additive, not a wall — it's a mistake to make the Facade the *only* way to reach the subsystem if some callers genuinely need lower-level access the simplified interface doesn't expose; the subsystem's original interfaces should generally remain available for the cases that need them. Spring's `JdbcTemplate` is a well-known real-world Facade: it hides the considerable boilerplate of manually acquiring a `Connection`, creating a `PreparedStatement`, handling `SQLException`, and closing resources in a `finally` block, exposing a handful of simple methods for the common cases, while lower-level JDBC access remains available for anything the template's simplified surface doesn't cover.

**Example:**

```java
public class FacadeDemo {
    static class CPU { void freeze() {} void jump(long pos) {} void execute() {} }
    static class Memory { void load(long pos, byte[] data) {} }
    static class HardDrive { byte[] read(long lba, int size) { return new byte[size]; } }

    static class ComputerFacade {
        private final CPU cpu = new CPU();
        private final Memory memory = new Memory();
        private final HardDrive hardDrive = new HardDrive();

        void start() { // ONE simple method hides the subsystem's real coordination complexity
            cpu.freeze();
            memory.load(0, hardDrive.read(0, 1024));
            cpu.jump(0);
            cpu.execute();
            System.out.println("Computer started");
        }
    }

    public static void main(String[] args) {
        new ComputerFacade().start(); // caller never touches CPU/Memory/HardDrive directly
    }
}
```

**Follow-up questions:**

- *"Does introducing a Facade reduce the subsystem's actual complexity?"* — No — it concentrates the knowledge of how to correctly use the subsystem in one place, rather than removing that complexity; the subsystem's own classes still do the same amount of work underneath.
- *"Is `JdbcTemplate` a real-world Facade example?"* — Yes — it hides the boilerplate of manually managing a `Connection`, `PreparedStatement`, exception handling, and resource cleanup behind a few simple methods, while raw JDBC access is still available for cases the template doesn't cover.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Facade](https://refactoring.guru/design-patterns/facade)

---

### 7. Proxy

**Core answer:**

"Proxy provides a surrogate or placeholder object that controls access to another object, standing in for it and adding behavior — lazy initialization, access control, logging, or remote-call marshaling — around the calls it forwards to the real object. A common variant is the **virtual proxy**, used for lazy loading: the proxy implements the same interface as an expensive-to-create real object, but defers actually constructing that real object until it's genuinely needed for the first time, rather than paying the construction cost up front regardless of whether it's ever used. Other classic variants include a **protection proxy** (checking permissions before forwarding a call) and a **remote proxy** (representing an object that actually lives in a different process or machine, hiding the network call behind a normal-looking method call). Every variant shares the same shape: same interface as the real object, a held reference to it, and additional logic wrapped around forwarding the call."

**Staff-level extension:**

`java.lang.reflect.Proxy` and Spring AOP proxies are the concrete, unavoidable real-world instance of this pattern in any Spring codebase: a `@Transactional` or `@Cacheable` method isn't called directly at all — Spring generates a runtime proxy that wraps the real bean, and the proxy is what intercepts the call to add the transaction/cache behavior before and after delegating to the actual method. This is also the source of a genuinely common, confusing bug worth being able to explain precisely: a `@Transactional`-annotated method called from *another method in the same class* bypasses the proxy entirely, since that's a direct internal `this.method()` call, not a call through the proxy — the annotation silently does nothing in that specific case, which trips up developers who don't understand that the proxy, not the annotation itself, is what actually implements the behavior.

**Example:**

```java
public class ProxyDemo {
    interface Image {
        void display();
    }

    static class RealImage implements Image {
        private final String filename;
        RealImage(String filename) {
            this.filename = filename;
            loadFromDisk(); // expensive — happens at CONSTRUCTION time
        }
        private void loadFromDisk() { System.out.println("Loading " + filename); }
        public void display() { System.out.println("Displaying " + filename); }
    }

    static class ProxyImage implements Image {
        private final String filename;
        private RealImage realImage; // NOT created until actually needed

        ProxyImage(String filename) { this.filename = filename; }

        public void display() {
            if (realImage == null) {
                realImage = new RealImage(filename); // lazy — only loads on first actual use
            }
            realImage.display();
        }
    }

    public static void main(String[] args) {
        Image image = new ProxyImage("photo.png"); // no loading yet
        image.display(); // loads NOW, then displays
        image.display(); // already loaded — just displays
    }
}
```

**Follow-up questions:**

- *"Why does a `@Transactional` method silently not work when called from another method in the same class?"* — Spring's transaction behavior is implemented by a runtime proxy wrapping the bean; a same-class internal call goes directly to the real method (`this.method()`), bypassing the proxy entirely, so the transaction logic the proxy would have added never runs.
- *"What's the difference between a virtual proxy and a protection proxy?"* — A virtual proxy defers expensive construction until first real use (lazy loading); a protection proxy checks permissions before forwarding a call — both share the same wrap-and-forward shape, just for different reasons.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Proxy](https://refactoring.guru/design-patterns/proxy), [`java.lang.reflect.Proxy` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/reflect/Proxy.html)

---

### 8. Composite

**Core answer:**

"Composite composes objects into tree structures to represent part-whole hierarchies, and lets client code treat an individual object (a 'leaf') and a composition of objects (a 'composite,' containing more leaves or composites) through the exact same interface, uniformly. The canonical example is a file system: a `File` and a `Directory` (which can itself contain `File`s and other `Directory`s) both implement the same interface — asking either one for its size, for instance, works identically from the caller's perspective, even though a `File` just returns a stored value and a `Directory` has to recursively sum its children's sizes first. This means client code that operates on the tree doesn't need to distinguish between 'a single item' and 'a group of items' at all — it just calls the shared interface's methods, and the object itself (leaf or composite) handles what that operation actually means for its own type, including recursing into children when it's a composite."

**Staff-level extension:**

The main design tension worth naming explicitly: making leaves and composites share one interface sometimes means the interface has to include operations that only make sense for one of the two (an `add(child)` method that a leaf can't meaningfully support) — the classic trade-off is either giving the leaf a no-op or throwing-exception implementation of operations it doesn't support (favoring transparency — one uniform interface, at the cost of a leaf technically exposing methods that don't apply to it), or splitting the interface so only composites expose child-management operations (favoring safety — no meaningless methods on a leaf, at the cost of client code needing to type-check or downcast to add a child at all). Real-world component trees — a UI widget hierarchy, a `java.nio.file.Path` structure — routinely make this same call, and being able to name which trade-off a given design chose is a genuine Staff-level distinction, not just recognizing the pattern's shape.

**Example:**

```java
import java.util.ArrayList;
import java.util.List;

public class CompositeDemo {
    interface FileSystemNode {
        long size();
    }

    static class FileNode implements FileSystemNode {
        private final long sizeInBytes;
        FileNode(long sizeInBytes) { this.sizeInBytes = sizeInBytes; }
        public long size() { return sizeInBytes; }
    }

    static class Directory implements FileSystemNode {
        private final List<FileSystemNode> children = new ArrayList<>();
        void add(FileSystemNode node) { children.add(node); }
        public long size() { // treats a FileNode and a Directory THE SAME WAY
            long total = 0;
            for (FileSystemNode child : children) total += child.size();
            return total;
        }
    }

    public static void main(String[] args) {
        Directory root = new Directory();
        root.add(new FileNode(100));
        Directory subDir = new Directory();
        subDir.add(new FileNode(200));
        root.add(subDir);
        System.out.println(root.size()); // 300 — root doesn't care that subDir is itself a composite
    }
}
```

**Follow-up questions:**

- *"What's the core design tension in Composite?"* — Whether to give leaves a no-op/throwing implementation of composite-only operations like `add(child)` (uniform interface, transparency) or split the interface so only composites expose them (safety, at the cost of needing type-checks to manage children).
- *"Why does `root.size()` in the example work correctly without root needing to know `subDir` is itself a Directory?"* — Because `Directory` and `FileNode` both implement the same `size()` method — the caller just invokes it uniformly, and each type's own implementation handles what "size" means for it, including recursing for a composite.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Composite](https://refactoring.guru/design-patterns/composite)

---

## Behavioral Patterns

### 9. Observer

**Core answer:**

"Observer defines a one-to-many dependency between objects so that when one object — the 'subject' — changes state, all of its registered dependents — the 'observers' — are notified and updated automatically, without the subject needing to know anything concrete about what each observer actually does with that notification. The subject exposes a way to subscribe and unsubscribe observers, holds a collection of currently-subscribed observers, and calls each one's update method whenever its own relevant state changes. This decouples the subject from its observers almost completely: the subject only depends on a generic observer interface, not any concrete observer class, so new kinds of observers can be added later without changing the subject at all, and the number of observers can change freely at runtime. This is the foundational pattern behind most event-driven and reactive systems — a UI element's registered event listeners, a message broker's subscribers, and Spring's `ApplicationEventPublisher` are all real instances of this same underlying shape."

**Staff-level extension:**

The classic `java.util.Observer`/`Observable` classes that shipped with early Java were deprecated as of Java 9, specifically because they had real design flaws worth knowing precisely: `Observable` was a class, not an interface, so a class that needed to extend something else couldn't also extend `Observable`; it wasn't thread-safe; and its notification order and semantics were underspecified. Modern Java code implements this pattern with a custom interface (as in the example here), `java.beans.PropertyChangeListener`, or reactive-streams-based APIs instead — worth being able to name specifically *why* the built-in version fell out of favor, not just that it did, since it demonstrates understanding of the pattern's actual failure modes, not just its shape.

**Example:**

```java
import java.util.ArrayList;
import java.util.List;

public class ObserverDemo {
    interface Observer {
        void update(double temperature);
    }

    static class WeatherStation {
        private final List<Observer> observers = new ArrayList<>();

        void subscribe(Observer observer) { observers.add(observer); }

        void setTemperature(double temperature) {
            for (Observer observer : observers) observer.update(temperature); // notify ALL, automatically
        }
    }

    static class PhoneDisplay implements Observer {
        public void update(double temperature) {
            System.out.println("Phone: temperature is now " + temperature);
        }
    }

    public static void main(String[] args) {
        WeatherStation station = new WeatherStation();
        station.subscribe(new PhoneDisplay());
        station.setTemperature(25.5); // Phone: temperature is now 25.5
    }
}
```

**Follow-up questions:**

- *"Why were `java.util.Observer`/`Observable` deprecated?"* — `Observable` was a class rather than an interface (blocking a subclass that needed to extend something else), wasn't thread-safe, and its notification semantics were underspecified — real code today uses a custom interface or `PropertyChangeListener` instead.
- *"What real Spring API implements this pattern?"* — `ApplicationEventPublisher` combined with `@EventListener`-annotated methods — publishing an event notifies every registered listener automatically, the same one-to-many, decoupled-subject-and-observers shape.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Observer](https://refactoring.guru/design-patterns/observer)

---

### 10. Strategy

**Core answer:**

"Strategy defines a family of interchangeable algorithms, encapsulates each one behind a common interface, and lets the algorithm used by a client vary independently of the client itself. Rather than a class implementing several variants of a behavior internally with conditional branching (`if (discountType == PERCENTAGE) ... else if (discountType == FLAT) ...`), each variant becomes its own small class implementing a shared strategy interface, and the client holds a reference to whichever concrete strategy it's currently configured with, calling it through the interface without knowing or caring which specific implementation is plugged in. This makes adding a new algorithm variant a matter of adding a new class implementing the interface, with zero changes to the client class itself, and it makes the algorithm swappable at runtime, even dynamically, by simply handing the client a different strategy instance. `java.util.Comparator`, passed into `Collections.sort()` or `List.sort()`, is the exact real-world instance of this pattern built into the JDK."

**Staff-level extension:**

Strategy and State (covered next) share an almost identical structural shape — both involve a context object holding a reference to an interchangeable implementation object — but differ in *intent* and *who controls the swap*: a Strategy is chosen by an external client, deliberately, based on what behavior is currently wanted, and doesn't change itself; a State transitions itself internally, in response to its own logic, as part of representing an object's own internal lifecycle. Being able to state this distinction precisely, rather than only reciting each pattern's individual definition, is exactly the kind of connection a Staff-level interviewer is listening for — recognizing that two patterns share a shape but differ in intent is a stronger signal of understanding than knowing either pattern in isolation.

**Example:**

```java
public class StrategyDemo {
    interface DiscountStrategy {
        double applyDiscount(double price);
    }

    static class NoDiscount implements DiscountStrategy {
        public double applyDiscount(double price) { return price; }
    }

    static class PercentageDiscount implements DiscountStrategy {
        private final double percent;
        PercentageDiscount(double percent) { this.percent = percent; }
        public double applyDiscount(double price) { return price * (1 - percent / 100); }
    }

    static class Checkout {
        private final DiscountStrategy strategy; // the algorithm is INJECTED, swappable
        Checkout(DiscountStrategy strategy) { this.strategy = strategy; }
        double total(double price) { return strategy.applyDiscount(price); }
    }

    public static void main(String[] args) {
        Checkout regular = new Checkout(new NoDiscount());
        Checkout sale = new Checkout(new PercentageDiscount(20));
        System.out.println(regular.total(100)); // 100.0
        System.out.println(sale.total(100));    // 80.0
    }
}
```

**Follow-up questions:**

- *"How is Strategy different from State, given they look almost identical structurally?"* — Strategy's implementation is chosen externally by a client and doesn't change itself; State transitions itself internally as part of representing an object's own lifecycle — same shape, different intent and different controller of the swap.
- *"How is `Comparator` a real-world Strategy example?"* — It's an interchangeable algorithm (the comparison logic) passed into a generic sorting method, which calls it without knowing or caring which specific comparison is plugged in — exactly Strategy's shape.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Strategy](https://refactoring.guru/design-patterns/strategy), [`Comparator` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Comparator.html)

---

### 11. Command

**Core answer:**

"Command encapsulates a request as a standalone object, containing everything needed to perform an action or trigger it later — letting you parameterize other objects with different requests, queue or log requests, and support undoable operations. Instead of a caller invoking a method directly, it creates a Command object representing that specific request (which method to call, on which receiver, with which arguments) and hands the Command object to an invoker, which calls the Command's own `execute()` method whenever it's time to actually run it. Because the request is now a real object rather than a direct method call, it can be stored in a history list for undo support, placed in a queue for later or asynchronous execution, or logged for auditing — none of which is possible with a plain, immediate method call, since a method call leaves no artifact behind once it returns. `Runnable` is the JDK's minimal, execute-only version of this pattern; a full Command implementation typically also exposes an `undo()` method the minimal `Runnable` interface doesn't have."

**Staff-level extension:**

The undo capability is where Command earns real complexity, and it's worth being precise about what it actually requires: a Command implementing `undo()` correctly needs to either capture enough state before `execute()` runs to reverse the exact change it made (not just perform the logically-opposite action, which can silently diverge if other state changed in between), or express the inverse operation directly when one exists cleanly (turning a light off is a clean inverse of turning it on; a more complex mutation might not have one). A command history stack (as in the example) is the natural data structure for supporting multiple levels of undo, and recognizing that a command needs to store its own "how to undo me" state, not just "how to run me," is the detail that separates a working undo feature from one that quietly corrupts state on the second or third undo.

**Example:**

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class CommandDemo {
    interface Command {
        void execute();
        void undo();
    }

    static class Light {
        void turnOn() { System.out.println("Light ON"); }
        void turnOff() { System.out.println("Light OFF"); }
    }

    static class TurnOnCommand implements Command {
        private final Light light;
        TurnOnCommand(Light light) { this.light = light; }
        public void execute() { light.turnOn(); }
        public void undo() { light.turnOff(); }
    }

    static class RemoteControl {
        private final Deque<Command> history = new ArrayDeque<>();
        void press(Command command) {
            command.execute();
            history.push(command); // stored as an OBJECT — enables undo, logging, queuing
        }
        void pressUndo() {
            if (!history.isEmpty()) history.pop().undo();
        }
    }

    public static void main(String[] args) {
        Light light = new Light();
        RemoteControl remote = new RemoteControl();
        remote.press(new TurnOnCommand(light)); // Light ON
        remote.pressUndo();                      // Light OFF
    }
}
```

**Follow-up questions:**

- *"Why can't a plain method call support undo the way a Command object can?"* — A method call leaves no artifact behind once it returns — there's nothing stored to reverse; a Command object persists as a real object, so it can be kept in a history and later asked to undo itself.
- *"What does a Command's `undo()` actually need to work correctly?"* — Either state captured before `execute()` ran (to precisely reverse that specific change) or a clean logical inverse operation — just performing "the opposite action" without captured state can silently diverge if other state changed in between.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Command](https://refactoring.guru/design-patterns/command)

---

### 12. Iterator

**Core answer:**

"Iterator provides a way to access the elements of a collection sequentially without exposing the collection's underlying representation — the code consuming the collection doesn't need to know whether it's backed by an array, a linked list, or a tree; it just calls `hasNext()` and `next()` repeatedly. This decouples traversal logic from the collection's internal structure, and it also means multiple independent iterators over the same collection can exist simultaneously, each tracking its own position, without interfering with each other. This isn't a pattern you typically need to hand-implement in modern Java for your own everyday collections — it's built directly into the language: `java.util.Iterator` is the interface, and implementing `Iterable` on a custom type (as the example here does) is what makes a for-each loop work on it at all, since the enhanced for loop is purely syntactic sugar over calling `iterator()` once and then `hasNext()`/`next()` in a loop underneath."

**Staff-level extension:**

Worth being precise about `Iterator`'s **fail-fast** behavior, since it's a frequently-tested detail: most JDK collection iterators throw a `ConcurrentModificationException` if the underlying collection is structurally modified (an element added or removed through a route other than the iterator's own `remove()` method) while iteration is in progress — this is a deliberate, best-effort safety check to surface a likely bug early, not a strict guarantee, and it's exactly why removing an element from a `List` mid-iteration has to go through `Iterator.remove()` specifically, not `list.remove(item)` called directly inside the loop body, which is a genuinely common early-career bug this pattern's own contract exists to catch, loudly, rather than silently corrupting iteration state.

**Example:**

```java
import java.util.Iterator;
import java.util.NoSuchElementException;

public class IteratorDemo {
    static class NameCollection implements Iterable<String> {
        private final String[] names;
        NameCollection(String[] names) { this.names = names; }

        public Iterator<String> iterator() {
            return new Iterator<>() {
                private int index = 0;
                public boolean hasNext() { return index < names.length; }
                public String next() {
                    if (!hasNext()) throw new NoSuchElementException();
                    return names[index++];
                }
            };
        }
    }

    public static void main(String[] args) {
        NameCollection names = new NameCollection(new String[]{"Alex", "Sam", "Jordan"});
        for (String name : names) { // sugar over calling iterator(), then next()/hasNext()
            System.out.println(name);
        }
    }
}
```

**Follow-up questions:**

- *"What does a for-each loop actually compile down to?"* — A call to `iterator()` once, followed by a loop calling `hasNext()`/`next()` — the enhanced for loop is purely syntactic sugar over the Iterator pattern, nothing more.
- *"Why does removing an element from a `List` mid-iteration require `Iterator.remove()` specifically?"* — Most JDK iterators are fail-fast — modifying the collection through any other route while iterating throws `ConcurrentModificationException` as a best-effort check; `Iterator.remove()` is the one mutation method the iterator itself tracks safely.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Iterator](https://refactoring.guru/design-patterns/iterator), [`Iterator` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Iterator.html)

---

### 13. State

**Core answer:**

"State allows an object to alter its behavior when its internal state changes, making the object appear as if it changed its class entirely. Rather than a class holding a status field and branching on it throughout its methods (`if (status == PENDING) ... else if (status == SHIPPED) ...`, repeated in every method that cares about status), each possible state becomes its own class implementing a shared state interface, and the context object holds a reference to its *current* state object, delegating behavior to it. Crucially, a state object can transition the context to a *different* state object as part of handling a request — which is what actually changes the context's future behavior, since the next call is delegated to whatever the *new* current state object is. This eliminates scattered conditional branching on a status field throughout a class and makes each state's specific behavior, and its own allowed transitions, live together in one focused class instead of spread across the whole context class."

**Staff-level extension:**

The mechanical detail that makes State actually work, worth being able to state precisely: a state object needs a way to change the *context's* current-state reference to a different state object — typically by receiving the context itself as a parameter to its transition method, as in the example here — which is exactly what allows the state object handling the current request to determine what the *next* state should be, rather than the context class itself needing to know every valid transition from every state. This is the same intent-versus-shape distinction covered in the Strategy question worth restating from the other side: State's swapping is driven internally, by the state object's own transition logic reacting to the current request, not by an external client choosing an implementation up front.

**Example:**

```java
public class StateDemo {
    interface OrderState {
        void next(Order order);
        String name();
    }

    static class PendingState implements OrderState {
        public void next(Order order) { order.setState(new ShippedState()); }
        public String name() { return "PENDING"; }
    }

    static class ShippedState implements OrderState {
        public void next(Order order) { order.setState(new DeliveredState()); }
        public String name() { return "SHIPPED"; }
    }

    static class DeliveredState implements OrderState {
        public void next(Order order) { /* terminal — no further transition */ }
        public String name() { return "DELIVERED"; }
    }

    static class Order {
        private OrderState state = new PendingState();
        void setState(OrderState state) { this.state = state; }
        void advance() { state.next(this); } // behavior of "advance" DEPENDS ENTIRELY on current state
        String status() { return state.name(); }
    }

    public static void main(String[] args) {
        Order order = new Order();
        System.out.println(order.status()); // PENDING
        order.advance();
        System.out.println(order.status()); // SHIPPED
        order.advance();
        System.out.println(order.status()); // DELIVERED
    }
}
```

**Follow-up questions:**

- *"How does a state object actually change the context's current state?"* — By receiving the context itself as a parameter to its transition method and calling the context's own state-setter — the state object handling the current request decides what the next state should be, not the context class.
- *"What problem does State solve compared to a status field with conditional branching?"* — It stops each state's specific behavior and allowed transitions from being scattered across every method of the context class that checks the status field — each state's logic lives together in its own focused class instead.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — State](https://refactoring.guru/design-patterns/state)

---

### 14. Template Method

**Core answer:**

"Template Method defines the skeleton of an algorithm in a method in a base class, with some of the algorithm's individual steps deferred to subclasses — letting subclasses redefine specific steps of the algorithm without changing its overall structure or the order those steps run in. The base class's template method is typically declared `final` specifically so subclasses can override individual step methods but can't rearrange or skip the algorithm's overall sequence; some steps are `abstract` (a subclass *must* provide an implementation) while others are concrete methods with a sensible default behavior a subclass can optionally override — these optional, overridable-but-not-required steps are often called 'hooks.' This is the inverse of Strategy's composition-based approach to varying behavior: Template Method varies behavior through inheritance (a subclass overriding specific steps), while Strategy varies behavior through composition (a client holding and swapping a separate strategy object) — both let a specific behavior vary, but through structurally different mechanisms."

**Staff-level extension:**

Spring's `JdbcTemplate` (despite the "Template" in its name overlapping in common parlance with this pattern's name, and it also legitimately being the Facade discussed earlier) and `AbstractList`'s implementation of several `List` methods purely in terms of a subclass's `get(int)` and `size()` are real instances of this exact pattern in everyday Java code — a subclass supplies a small number of specific steps, and the base class provides the surrounding algorithm for free. The general trade-off worth naming: Template Method's inheritance-based extension point is more rigid than Strategy's composition-based one, since a class can only extend one base class, while a Strategy-based design can swap in any number of independent behaviors freely — "favor composition over inheritance" is a real, applicable design principle here, not just a slogan, and it's exactly why many modern APIs prefer accepting a functional-interface-typed parameter (an effective Strategy) over requiring a subclass to override a template step.

**Example:**

```java
public class TemplateMethodDemo {
    abstract static class DataProcessor {
        final void process() { // the TEMPLATE — fixed sequence, final so subclasses can't reorder it
            readData();
            processData();
            writeData();
        }
        abstract void readData();
        abstract void processData();
        void writeData() { System.out.println("Writing to standard output (default)"); } // an optional "hook"
    }

    static class CsvDataProcessor extends DataProcessor {
        void readData() { System.out.println("Reading CSV"); }
        void processData() { System.out.println("Parsing CSV rows"); }
    }

    public static void main(String[] args) {
        new CsvDataProcessor().process();
        // Reading CSV
        // Parsing CSV rows
        // Writing to standard output (default)
    }
}
```

**Follow-up questions:**

- *"Why is the template method itself typically declared `final`?"* — To prevent subclasses from overriding the algorithm's overall sequence — subclasses may only customize individual steps, not reorder or skip parts of the algorithm the base class defines.
- *"How does Template Method differ from Strategy in how it lets behavior vary?"* — Template Method varies behavior through inheritance — a subclass overrides specific steps of a fixed algorithm; Strategy varies behavior through composition — a client holds and swaps an entirely separate object implementing the behavior.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Template Method](https://refactoring.guru/design-patterns/template-method)

---

### 15. Chain of Responsibility

**Core answer:**

"Chain of Responsibility avoids coupling the sender of a request to one specific receiver by giving more than one object a chance to handle it — the potential handlers are linked into a chain, and a request travels along the chain until some handler actually handles it (or the chain ends with the request unhandled). Each handler in the chain decides independently whether it can handle a given request; if it can, it does, and typically stops the chain there; if it can't, it passes the request along to the next handler in the chain, which repeats the same decision. The sender only ever talks to the first handler in the chain and has no idea which specific handler, if any, will actually end up processing the request, or how many handlers the request passes through before one does — this keeps the sender fully decoupled from the concrete set of handlers and their ordering, which can change independently of the sending code."

**Staff-level extension:**

Servlet filter chains and Spring Security's filter chain are real, unavoidable everyday instances of this exact pattern: an HTTP request passes through a configured sequence of filters, each deciding whether to handle it (authenticate, authorize, log, reject) and whether to pass it further down the chain by calling the next filter, or short-circuit it there. The genuinely easy mistake to make with this pattern, worth naming directly: forgetting to explicitly handle the case where *no* handler in the chain actually processes the request — a chain with no terminal "nobody handled this" fallback either silently drops the request or throws a confusing `NullPointerException` when code downstream assumes a chain always produces some result, rather than failing clearly and immediately at the point the gap actually is.

**Example:**

```java
public class ChainOfResponsibilityDemo {
    abstract static class SupportHandler {
        protected SupportHandler next;
        SupportHandler setNext(SupportHandler next) { this.next = next; return next; }

        void handle(int severity) {
            if (canHandle(severity)) {
                resolve(severity);
            } else if (next != null) {
                next.handle(severity); // pass along the chain
            } else {
                System.out.println("No handler could resolve severity " + severity);
            }
        }
        abstract boolean canHandle(int severity);
        abstract void resolve(int severity);
    }

    static class Tier1Support extends SupportHandler {
        boolean canHandle(int severity) { return severity <= 1; }
        void resolve(int severity) { System.out.println("Tier 1 resolved severity " + severity); }
    }

    static class Tier2Support extends SupportHandler {
        boolean canHandle(int severity) { return severity <= 3; }
        void resolve(int severity) { System.out.println("Tier 2 resolved severity " + severity); }
    }

    public static void main(String[] args) {
        SupportHandler chain = new Tier1Support();
        chain.setNext(new Tier2Support());
        chain.handle(2); // Tier 1 can't handle -> passes to Tier2 -> "Tier 2 resolved severity 2"
    }
}
```

**Follow-up questions:**

- *"What's a real, everyday instance of Chain of Responsibility?"* — Servlet filter chains and Spring Security's filter chain — an HTTP request passes through a sequence of filters, each deciding whether to handle/reject it or pass it along to the next one.
- *"What's the easy mistake to make when implementing this pattern?"* — Forgetting an explicit fallback for the case where no handler in the chain processes the request — without one, the request either silently disappears or causes a confusing failure downstream instead of failing clearly at the actual gap.

**Sources:** [Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia)](https://en.wikipedia.org/wiki/Design_Patterns), [refactoring.guru — Chain of Responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Gamma, Helm, Johnson, Vlissides — Design Patterns (Wikipedia) | https://en.wikipedia.org/wiki/Design_Patterns |
| refactoring.guru — Singleton | https://refactoring.guru/design-patterns/singleton |
| refactoring.guru — Factory Method | https://refactoring.guru/design-patterns/factory-method |
| refactoring.guru — Builder | https://refactoring.guru/design-patterns/builder |
| refactoring.guru — Adapter | https://refactoring.guru/design-patterns/adapter |
| refactoring.guru — Decorator | https://refactoring.guru/design-patterns/decorator |
| `InputStream` Javadoc, JDK 21 | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/InputStream.html |
| refactoring.guru — Facade | https://refactoring.guru/design-patterns/facade |
| refactoring.guru — Proxy | https://refactoring.guru/design-patterns/proxy |
| `java.lang.reflect.Proxy` Javadoc, JDK 21 | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/reflect/Proxy.html |
| refactoring.guru — Composite | https://refactoring.guru/design-patterns/composite |
| refactoring.guru — Observer | https://refactoring.guru/design-patterns/observer |
| refactoring.guru — Strategy | https://refactoring.guru/design-patterns/strategy |
| `Comparator` Javadoc, JDK 21 | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Comparator.html |
| refactoring.guru — Command | https://refactoring.guru/design-patterns/command |
| refactoring.guru — Iterator | https://refactoring.guru/design-patterns/iterator |
| `Iterator` Javadoc, JDK 21 | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Iterator.html |
| refactoring.guru — State | https://refactoring.guru/design-patterns/state |
| refactoring.guru — Template Method | https://refactoring.guru/design-patterns/template-method |
| refactoring.guru — Chain of Responsibility | https://refactoring.guru/design-patterns/chain-of-responsibility |
