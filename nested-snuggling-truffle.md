# Modernisation Plan: aws2tf

## Context

aws2tf is a functional, production-quality Python tool with significant accumulated technical debt. The codebase has grown organically — security fixes were retrofitted, the handler system was recently optimised (Dec 2024), but foundational patterns were never modernised. This plan addresses structural issues that make the code hard to test, reason about, and extend, while preserving the working logic. The goal is incremental improvement rather than a rewrite.

---

## Phase 1: Fix Active Bugs (Do First)

**Priority: bugs that cause incorrect behaviour**

### 1.1 Bug in `fixtf.py` — invalid file mode `"e"` (line 770)
`open(tf2 + ".saved", "e")` — `"e"` is not a valid Python file mode. Code is unreachable today (only triggered for `aws_lb` with disabled access/connection logs) but will raise `ValueError` when hit.
- Fix: change to `"r"`

### 1.2 Bug in `fixtf.py` — `type` builtin shadowed (line 766)
`if type == "aws_lb":` — `type` is a Python builtin and not in scope as a local variable here. Should be `ttft`.

### 1.3 Bug in `context.py` — `exit_aws2tf` logic always-true condition (line 140)
`if mess is not None or mess != "":` — `or` means this is always `True`. Should be `and`.

### 1.4 Bug in `context.py` — both branches of `exit_aws2tf` are identical (lines 143–146)
Both `if context.fast` and `else` call `sys.exit(1)`. The `fast`-mode branch is dead code.

---

## Phase 2: Remove Dead Code and Clutter

**Goal: reduce noise so the real logic is visible**

### 2.1 Remove the no-op `remove_block()` in `fixtf.py` (line 820)
Empty function that just returns. Remove it.

### 2.2 Delete commented-out code blocks
Key locations:
- `fixtf.py` lines 446–451 (optimisation comment with dead `cp`/`mv` logic)
- `common.py` lines 2178, 2263, 2359, 2437–2460 (commented print/debug blocks)
- `aws2tf.py` line 60 (commented import)

### 2.3 Remove unused imports in `aws2tf.py`
- `concurrent.futures` is imported redundantly (ThreadPoolExecutor already imported separately)
- `io` appears unused

---

## Phase 3: Replace 220-Line Import Block in `fixtf.py` with `importlib`

**File: `code/fixtf.py` lines 17–435**

Currently: 220 explicit `from fixtf_aws_resources import fixtf_X` statements followed by a 200-entry `FIXTF_MODULES` dict that re-maps the same modules by string key.

This is redundant: the registry key is always `"fixtf_" + clfn`, which is exactly the module name. Replace with dynamic loading:

```python
import importlib

def _get_fixtf_module(callfn: str):
    try:
        return importlib.import_module(f"fixtf_aws_resources.{callfn}")
    except ModuleNotFoundError:
        return None
```

The `FIXTF_MODULES` dict and all 220 explicit imports can be deleted. Module lookup at call time (with optional LRU cache) is equivalent — modules are cached by Python's import system after first load.

**Files modified:** `code/fixtf.py`
**Lines removed:** ~420 (the import block + registry dict)

---

## Phase 4: Replace Global Module State (`context.py`) with a Dataclass

**File: `code/context.py`**

Currently 100+ module-level mutable variables used as a global singleton. This makes code impossible to unit test (state leaks between tests) and creates hidden dependencies.

**Approach:**
- Convert to a `@dataclass` (or use `SimpleNamespace` as a lightweight first step)
- Instantiate once in `aws2tf.py::main_new()` and pass to top-level functions
- Inner functions (handlers, get_aws_resource) that need context can continue reading from the module for now — the key win is making the top-level flow testable

```python
# context.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AppContext:
    region: str = ""
    acc: str = ""
    fast: bool = False
    debug: bool = False
    merge: bool = False
    rproc: dict = field(default_factory=dict)
    rdep: dict = field(default_factory=dict)
    vpclist: dict = field(default_factory=dict)
    # ... etc
```

The module-level singleton pattern can be preserved during transition by keeping a module-level `_ctx: AppContext` instance, accessed via `context.ctx.region` etc., allowing incremental migration without changing all 108 service files at once.

**Files modified:** `code/context.py`, `aws2tf.py` (initialisation)

---

## Phase 5: Add Type Hints to Core Public APIs

**Priority order (highest impact first):**

1. `code/context.py` — the dataclass migration (Phase 4) adds these automatically
2. `aws2tf.py` — the 10 phase functions (`parse_and_validate_arguments`, `setup_environment_and_context`, etc.)
3. `code/common.py` — public functions: `write_import()`, `add_dependancy()`, `rc()`, `call_resource()`
4. `code/build_lists.py` — `build_lists()`, `build_secondary_lists()`
5. `code/fixtf.py` — `fixtf()`

Do **not** attempt to add hints to all 108 get_aws_resources files or 259 handler files in one pass — focus on the orchestration layer first. Handler signature can be captured with a `TypeAlias`:

```python
from typing import TypeAlias
HandlerResult: TypeAlias = tuple[int, str, bool, str]
HandlerFn: TypeAlias = Callable[[str, str, str, bool, str], HandlerResult]
```

---

## Phase 6: Fix Exception Handling

**Replace bare `except:` with specific exceptions**

9 instances in `code/common.py`, plus several in `code/fixtf.py`.

Pattern:
```python
# Before
except:
    pass

# After — choose the right exception
except KeyError:
    pass
except (ValueError, IndexError):
    tt2 = ""
```

The `fixtf.py` prescan blocks (`lines 507, 517, 527, 540, 546, 556, 567, 587, 687, 688`) all catch exceptions from `t1.split("=")[1]` — these should all be `except IndexError`.

---

## Phase 7: Consolidate Pre-scan Loops in `fixtf.py`

**File: `code/fixtf.py` lines 492–615**

Currently: 7 separate `for t1 in Lines:` loops, each scanning the full file for a specific resource type. Only one can match per call (since `ttft` is fixed), but all 7 loops execute sequentially.

Replace with a single dispatch:

```python
PRESCAN_HANDLERS = {
    "aws_s3_bucket_replication_configuration": _prescan_s3_replication,
    "aws_elasticache_cluster": _prescan_elasticache_cluster,
    # ...
}

if handler := PRESCAN_HANDLERS.get(ttft):
    handler(Lines)
```

Each `_prescan_X` function is a small extracted function. This is an O(1) dispatch instead of O(7) sequential checks.

---

## Phase 8: Remove `print()` Statements from `common.py`

9 `print()` calls mixed with structured logging (lines 1286, 1359–1365, 2439, 2443, 2447, 2455). Replace with `log.info()` / `log.debug()` equivalents. The formatted error box (lines 1359–1365) can use a multi-line `log.error()`.

---

## Phase 9: Project Packaging — Replace `sys.path.insert` Hack

**File: `aws2tf.py` line 18: `sys.path.insert(0, "./code")`**

This makes the tool CWD-dependent. Replace with proper packaging:

- Add `pyproject.toml` (replaces `requirements.txt`, enables `pip install -e .`)
- Use `src/` layout or keep flat layout with package declaration
- Makes imports work regardless of where the tool is invoked from

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "aws2tf"
requires-python = ">=3.12"
dependencies = ["boto3>=1.42.16", "requests>=2.32.5", "tqdm>=4.66.0"]

[project.scripts]
aws2tf = "aws2tf:main_new"
```

---

## Phase 10: Consolidate String Formatting

Low-friction cleanup: replace string concatenation in log calls with f-strings or lazy `%` formatting.

Examples:
- `log.info("./aws2tf.py  -t " + line + "     \t\t\t" + str(line3))` → `log.info("./aws2tf.py  -t %s\t\t\t%s", line, line3)`
- `log.error("ERROR: clfn is None with type=" + ttft)` → `log.error("ERROR: clfn is None with type=%s", ttft)`

Use `%`-style for log calls (lazy evaluation), f-strings for everything else.

---

## Files Modified (Summary)

| File | Phases |
|------|--------|
| `code/fixtf.py` | 1.1, 1.2, 2.1, 2.2, 3, 6, 7 |
| `code/context.py` | 1.3, 1.4, 4 |
| `aws2tf.py` | 2.2, 2.3, 5, 9, 10 |
| `code/common.py` | 2.2, 5, 6, 8, 10 |
| `code/build_lists.py` | 5 |
| `pyproject.toml` | 9 (new file) |

---

## Verification

For each phase:

1. **Bugs (Phase 1):** Run `pytest` before and after — zero regressions. Manually trigger the `aws_lb` code path with disabled access logs to confirm the file mode fix works.
2. **importlib refactor (Phase 3):** Run `pytest` + smoke test `./aws2tf.py -t vpc` against a real (or mocked) AWS account. All 1,612 resource types should still resolve.
3. **Context dataclass (Phase 4):** Existing tests pass; write 2–3 new unit tests that instantiate `AppContext` directly without needing module-level state.
4. **Type hints (Phase 5):** Run `mypy code/aws2tf.py code/common.py code/context.py` — no errors.
5. **Exception handling (Phase 6):** `ruff check .` — no bare `except` warnings.
6. **Packaging (Phase 9):** `pip install -e . && aws2tf -h` from a different working directory.

---

## What This Plan Deliberately Excludes

- Rewriting the 108 `get_aws_resources/` files or 259 handler files (too large, low ROI vs. risk)
- Adding locks/synchronisation to `build_lists.py` threading (the GIL protects dict updates; current pattern is documented and safe for the current usage)
- Large-scale test coverage expansion (the existing 267 tests provide a safety net; new tests should follow naturally from the dataclass refactor)
- Architectural changes to the 10-phase flow (it works and is documented)
