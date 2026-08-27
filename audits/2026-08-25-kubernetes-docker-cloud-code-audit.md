# Kubernetes, Docker & Cloud — Code-Block Audit — 2026-08-25

Scope: twelfth guide in `ROADMAP.md`'s code-block validation rollout,
and the first with zero Java/application code — every block is
infrastructure configuration (YAML, Dockerfile, shell). No live cluster
or Docker daemon is available in this environment (confirmed:
`docker ps` fails to reach a daemon, no `kubectl` context configured),
so verification used offline, schema-aware tooling instead of live
execution: `kubectl` v1.34.1, `kubeconform` 0.8.0, and `hadolint` 2.15.1
(the latter two installed via Homebrew for this pass — standalone CLI
validators, not services), plus PyYAML in an isolated virtualenv for
baseline syntax checking.

## Classification summary (52 total code blocks)

- **15 `yaml`-tagged blocks.** All 15 parse as syntactically valid YAML
  (verified with PyYAML). Of the 13 that are complete manifests
  (`apiVersion`/`kind` present), 9 validated cleanly against the real
  Kubernetes API schema via `kubeconform` (Pod, Service, Ingress,
  ConfigMap, Secret, HorizontalPodAutoscaler, NetworkPolicy,
  ResourceQuota, Namespace, PodDisruptionBudget). 2 reference
  third-party CRDs (Kyverno's `ClusterPolicy`, the `VerticalPodAutoscaler`
  from the autoscaling SIG) that `kubeconform`'s default schema catalog
  doesn't include — reviewed manually for plausible, correctly-shaped
  field usage instead. 2 are deliberately **partial** manifest fragments
  (a bare `spec:` block illustrating a `preStop` hook; a `StatefulSet`
  showing only `serviceName`/`volumeClaimTemplates`) that fail full
  schema validation only because they omit fields irrelevant to the
  specific point being illustrated — correctly **partial illustrative
  snippet** per `CONTRIBUTING.md`, not a defect, since neither is
  presented as a complete, deployable manifest in its surrounding prose.
- **18 `bash`-tagged blocks** — `docker`/`kubectl`/`etcdctl` command
  sequences — reviewed for correct flag syntax and command names against
  current Docker/Kubernetes CLI documentation; not executed (no daemon/
  cluster available), but every flag and subcommand checked is real and
  correctly used.
- **12 `text`-tagged blocks** — architecture/isolation diagrams, timeline
  illustrations, checklists — correctly diagrams, not executable.
- **7 `dockerfile`-tagged blocks** — linted with `hadolint`. All findings
  were either stylistic best-practice suggestions (pin `apt`/`apk`
  package versions — a real but optional hardening suggestion, not a
  correctness defect) or expected structural notes on deliberately
  partial fragments that omit a `FROM` line because the point being
  illustrated (a `CMD`/`ENTRYPOINT` interaction, a layer-consolidation
  `RUN` chain) doesn't need one — no real bugs.

## Verification performed

- `kubeconform` against every complete YAML manifest — schema-validated
  9 resources against the real Kubernetes 1.28+ OpenAPI definitions.
- `hadolint` against all 7 Dockerfile blocks — no correctness errors,
  only optional best-practice suggestions already common in real-world
  Dockerfiles that don't pin every package version.
- Manual review of all 18 bash blocks' `docker`/`kubectl`/`etcdctl`
  flags and subcommands against current CLI documentation.

## Bugs found

None.

## Not done in this pass

- No live Kubernetes cluster or Docker daemon was used — this guide has
  no application code to compile/execute in the first place, so the
  verification ceiling here is schema/lint validation, not runtime
  behavior (there's no runtime behavior to observe for a YAML manifest
  or a Dockerfile in isolation).
- The two third-party-CRD YAML blocks (Kyverno `ClusterPolicy`, `VPA`)
  were reviewed manually rather than schema-validated, since
  `kubeconform`'s bundled schema catalog doesn't include every possible
  CRD in the ecosystem.
