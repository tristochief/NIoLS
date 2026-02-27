PAGE 1 — PURPOSE, SCOPE, NON-NEGOTIABLES
1.1 Purpose

Build a local orchestration system that enables:

multi-agent workflows executed in ChatGPT UI (in multiple tabs if desired)

grounded decision-making by providing the UI with accurate local state

deterministic application of UI outputs (patches/commands)

robust verification loops (tests/lint/build)

full replayability and audit trails

1.2 Non-Negotiables (properties of the produced code)

The produced code MUST:

Never call LLM APIs (no OpenAI/Anthropic API usage).

Never include “semantic decision logic” that substitutes for UI reasoning.

Be excellent at:

context packaging

patch ingestion & application

command execution

verification

artifact/state management

Make it easy to:

run “parallel agents” (human opens multiple UI tabs)

feed all agents the same grounded bundle

collect & apply whichever output you pick

1.3 Cursor’s authority

Cursor can design anything. But Cursor must ensure the runtime system obeys the constraints above.

PAGE 2 — CORE ARCHITECTURE (UI Brain / Local Bus)
2.1 The Architecture Contract

The system is a two-part cognitive machine:

UI Brain (ChatGPT UI): planning, reasoning, synthesis, critique, decisions, writing patches

Local Grounding Bus (repo + CLI): sensing local truth, packaging it, applying UI directives, verifying outcomes

2.2 Data flow (round-trip loop)

Local CLI generates a Grounding Bundle (truth snapshot)

Human pastes bundle into ChatGPT UI (one agent tab or many)

UI returns one of: PATCH / COMMANDS / QUESTIONS

Local CLI ingests, applies, executes, verifies

CLI generates next Grounding Bundle

Repeat until done

2.3 System goal

Minimize:

UI hallucinations by maximizing grounding

“lost context” by consistent bundle structure

“bad patches” by strict patch contracts + verification

PAGE 3 — WHAT THE CODE IS ALLOWED TO DO (AND NOT DO)
3.1 Code Allowed Capabilities (strong)

The produced code is allowed to be “smart” in mechanical ways:

Parse stack traces to extract file paths + line numbers

Collect diffs, file lists, repo trees

Tail logs, capture stdout/stderr

Run build/test/lint commands

Enforce schemas and formatting

Apply patches atomically with rollback

Maintain state machine of steps defined by manifests

Provide user-friendly CLI UX

3.2 Code Forbidden Capabilities (semantic)

The produced code MUST NOT:

Decide “what to do next” based on meaning

Synthesize multiple agent outputs into one

Score/rank/grade outputs

Summarize research or infer conclusions

Perform semantic routing (“send this to research agent” automatically)

Implement “critic” logic beyond mechanical checks (e.g., missing required sections)

Rule of thumb: if it resembles a judgment a human would make reading text, it belongs in the UI.

PAGE 4 — DELIVERABLES: REPO, CLI, FILE LAYOUT
4.1 Repo layout (required)
/orchestrator
  /bundles/                # generated grounding bundles per run
  /runs/
    /RUN_<timestamp>_<slug>/
      run.yaml
      state.yaml
      /inputs/
      /outputs/
      /patches/
      /logs/
      /reports/
  /workflows/              # human-authored or UI-authored, then saved here
  /prompts/                # agent prompts and step prompts (templates)
  /schemas/                # JSON schema for outputs
  /src/orch/               # python package (or node package)
  orch                     # CLI entry
  README.md
4.2 Required CLI commands

orch init

orch new-run --workflow <id> --objective "<text>"

orch bundle [--focus ...] [--max-bytes ...]

orch ingest --patch <file>|--commands <file>|--ui-output <file>

orch apply

orch exec --preset test|lint|build|custom

orch verify (runs configured checks, stores outputs)

orch status

orch checkpoint --message "<text>"

orch rollback

orch export (create a single zip/dir you can paste/share)

4.3 Git integration (required)

auto-create branch per run

checkpoint commits optional but strongly supported

clean rollback path

PAGE 5 — WORKFLOWS & “MULTI-AGENT” WITHOUT APIs
5.1 Workflows are explicit manifests

A workflow is YAML that defines steps, inputs, outputs, and verification gates.

Example:

workflow_id: debug_fix_verify_v1
steps:
  - id: bundle_failures
    action: bundle
    focus: failing
  - id: ui_patch
    action: ui_step
    prompt_ref: prompts/steps/implementer_patch.md
    expected_output: PATCH
  - id: apply_patch
    action: apply
  - id: verify
    action: verify
    presets: [test, lint]
  - id: ui_iterate
    action: ui_step
    prompt_ref: prompts/steps/verifier_next.md
    expected_output: PATCH|COMMANDS|QUESTIONS
5.2 Multi-agent is a UI practice, supported by tooling

The system supports multi-agent by:

generating the same bundle for multiple UI tabs

providing agent prompt templates to paste

letting you store multiple candidate patches under /runs/.../patches/

allowing you to choose which to apply

The code must not merge. It must store, diff, and apply.

PAGE 6 — GROUNDING BUNDLE SPEC (THE HEART)
6.1 Bundle format (strict markdown)

Every bundle must be deterministic and structured:

# Grounding Bundle
Run: RUN_...
Time: ...
Branch: ...
Commit: ...
Dirty: yes/no

## Objective
...

## Constraints
...

## Current Status
- last step:
- failing checks:
- last applied patch:

## Repo Snapshot
(tree summary, focused)

## Diffs
(unified diff or list + excerpts)

## Failing Outputs
(raw logs; no summarization)

## Relevant File Excerpts
(file path + exact line ranges)

## Commands Available
(list of safe presets)

## Required UI Output Contract
You must output EXACTLY one:
- PATCH (unified diff)
- COMMANDS (shell commands)
- QUESTIONS (blocking questions only)
6.2 Focus selectors

orch bundle must support focus modes like:

--focus failing

--focus diff

--focus file:src/x.py

--focus test:test_name

--focus trace

--focus recent --since 2h

6.3 Size control

Bundles must be bounded:

--max-bytes

--max-files

--max-excerpts-per-file

with deterministic truncation rules (and “truncated” markers)

PAGE 7 — UI OUTPUT CONTRACTS (PATCH / COMMANDS / QUESTIONS)
7.1 PATCH format

unified diff only

no prose

correct paths

can add files (explicit)

deterministic line endings

The tool must:

validate patch format

apply with 3-way merge optional, but default to strict

on failure: produce a “patch failed” bundle with exact errors

7.2 COMMANDS format

shell commands only

one per line

working directory explicit if needed

no commentary

The tool must:

run commands in a controlled shell

capture outputs verbatim

store logs and include them in next bundle

7.3 QUESTIONS format

allowed only if blocked

must be minimal and specific
Tooling treats QUESTIONS as a “pause state”.

PAGE 8 — SAFETY, CHECKPOINTING, REPLAY
8.1 Safety mechanisms (required)

Dry run: orch apply --dry-run

Patch sandbox: apply to working tree or to temp checkout

Rollback: revert working tree changes or git reset

Immutable artifacts: bundles/logs/patches are never overwritten

8.2 Replay (required)

A run must be replayable by:

reloading run.yaml and state.yaml

re-emitting the last bundle

re-running verify commands

re-applying selected patches (optionally)

8.3 Redaction (recommended)

Provide optional config to redact:

secrets

tokens

private keys
from bundles/logs via regex-based redaction (mechanical).

PAGE 9 — “INTELLIGENCE EXTERNALIZATION” GUARANTEES
9.1 How the system forces UI cognition

The system must make the UI the obvious place to decide by:

Always providing “Required UI Output Contract” in bundles

Never providing “recommended fixes” from the tool

Presenting raw evidence (diffs/logs/excerpts) rather than summaries

Making step progression depend on either:

an explicit workflow step; or

explicit human command

9.2 Preventing hidden tool reasoning creep

Implement a hard “capabilities firewall”:

No dependencies that are LLM toolkits

No embeddings

No semantic search

No vector DB

No ranking models

No “auto planner” modules

If Cursor wants semantic search, it must be UI-driven (“ask UI to tell you what file to open”), then the tool can extract that file excerpt.

PAGE 10 — ACCEPTANCE TESTS & DEFINITION OF DONE
10.1 Done means

I can run orch new-run, generate a bundle, paste into ChatGPT UI, ingest a patch, apply, verify, and iterate—end-to-end.

The tool never calls external AI services.

The tool never decides solutions.

The UI always has enough grounded context to act with low hallucination.

Parallel UI agents are supported by storing multiple candidate patches and letting me choose.

10.2 Test cases (must ship)

Patch apply success

Patch apply failure → produces a failure bundle

Verify failure → produces failing bundle with logs

Bundle size limits work deterministically

Replay run works from state.yaml

Multiple candidate patches stored and diffable

Redaction rules applied to bundles (if enabled)

10.3 Required documentation

“How to run multi-agent in multiple UI tabs”

“How to paste bundles and enforce PATCH output”

“How to ingest/apply/verify”

“Recovery and rollback”

“How to author workflows”