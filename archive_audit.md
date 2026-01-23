# Archive Safety Audit Report

**Status**: ❌ **UNSAFE** - Critical issues found

**Date**: 2026-01-22  
**Auditor**: Antigravity AI

---

## 1. Archive Inventory Table

| Path | Original Purpose | Referenced? | Reference Location | Safe to Archive? |
|------|------------------|-------------|-------------------|------------------|
| `archive/camera/` | Video capture + face analysis | **NO** | None in active code | ✅ SUPERSEDED |
| `archive/audio/` | Audio capture + VAD | **NO** | None in active code | ✅ SUPERSEDED |
| `archive/storage/` | Session + JSON writer | **YES** ⚠️ | `face_logger.py:12`, `voice_activity.py:9` | ❌ **BROKEN DEPENDENCY** |
| `archive/api/` | FastAPI server + session | **NO** | None in active code | ✅ SUPERSEDED |
| `archive/ui/` | CLI overlay rendering | **NO** | None in active code | ✅ SUPERSEDED |
| `archive/doc/` | Documentation | **NO** | None | ✅ LEGACY |
| `archive/main.py` | CLI entry point | **NO** | None | ✅ SUPERSEDED |
| `archive/requirements.txt` | Dependencies | **NO** | None | ✅ LEGACY |
| `archive/stitch_demo_landing_screen/` | Design mockups | **NO** | None | ✅ EXPERIMENTAL |

---

## 2. Dependency Scan Results

### ❌ CRITICAL: Broken Imports Found

| Active File | Line | Import Statement | Status |
|-------------|------|------------------|--------|
| `backend/app/capture/camera/face_logger.py` | 12 | `from storage.json_writer import JsonWriter` | **BROKEN** |
| `backend/app/capture/audio/voice_activity.py` | 9 | `from storage.json_writer import JsonWriter` | **BROKEN** |

**Root Cause**: When files were copied from the original location to `backend/app/`, the internal imports inside `face_logger.py` and `voice_activity.py` were NOT updated. They still reference the old flat `storage.` path.

**Expected Import**: `from app.session.json_writer import JsonWriter`

**Impact**: The backend will **FAIL** at runtime when these modules are loaded.

### ✅ No Other Dependencies Found

- `app/main.py` - Uses `app.api.session` ✓
- `app/api/session.py` - Uses `app.session.*`, `app.capture.*` ✓
- `app/cli.py` - Uses `app.*` paths ✓
- Frontend JS files - No Python imports (not applicable)

---

## 3. Naming Collision Risk Assessment

| Archived Folder | Risk Level | Recommendation |
|-----------------|------------|----------------|
| `archive/camera/` | ⚠️ MEDIUM | Could confuse IDE auto-import |
| `archive/audio/` | ⚠️ MEDIUM | Could confuse IDE auto-import |
| `archive/api/` | ⚠️ MEDIUM | Could confuse IDE auto-import |
| `archive/storage/` | 🔴 HIGH | **Currently being imported by mistake** |
| `archive/ui/` | 🟡 LOW | Less common import target |

**Recommendation**: Rename `archive/` to `_archive_legacy_20260122/` to:
- Prevent IDE from suggesting these as import targets
- Make the obsolete status visually obvious
- Include timestamp for audit trail

---

## 4. Archive Classification

| Item | Classification | Notes |
|------|---------------|-------|
| `archive/camera/` | SUPERSEDED_BY_NEW_MODULE | Replaced by `backend/app/capture/camera/` |
| `archive/audio/` | SUPERSEDED_BY_NEW_MODULE | Replaced by `backend/app/capture/audio/` |
| `archive/storage/` | SUPERSEDED_BY_NEW_MODULE | Replaced by `backend/app/session/` |
| `archive/api/` | SUPERSEDED_BY_NEW_MODULE | Replaced by `backend/app/api/` + `main.py` |
| `archive/ui/` | SUPERSEDED_BY_NEW_MODULE | Replaced by `backend/app/ui/` |
| `archive/main.py` | SUPERSEDED_BY_NEW_MODULE | Replaced by `backend/app/cli.py` |
| `archive/requirements.txt` | LEGACY_IMPLEMENTATION | Copy exists in backend |
| `archive/doc/` | EXPERIMENTAL_UNUSED | Documentation assets |
| `archive/stitch_demo_landing_screen/` | EXPERIMENTAL_UNUSED | Design mockups only |

---

## 5. Final Verdict

### ❌ UNSAFE

The archive is **NOT SAFE** in its current state due to:

1. **Broken imports** in active code referencing old `storage.` path
2. **Naming collision risk** with IDE auto-imports
3. **Missing import path updates** in copied capture modules

### Required Fixes Before Archive is Safe

| Priority | Action | Files |
|----------|--------|-------|
| 🔴 P0 | Fix broken imports | `face_logger.py:12`, `voice_activity.py:9` |
| 🟡 P1 | Rename archive folder | `archive/` → `_archive_legacy_20260122/` |
| 🟢 P2 | Verify backend starts | Run `uvicorn app.main:app` |

---

## Evidence Summary

```
$ grep -r "from storage\." backend/
backend/app/capture/camera/face_logger.py:from storage.json_writer import JsonWriter
backend/app/capture/audio/voice_activity.py:from storage.json_writer import JsonWriter
```

These imports will fail because `storage/` was moved to `archive/storage/` and is no longer in the Python path.

---

— **END OF ARCHIVE SAFETY AUDIT** —
