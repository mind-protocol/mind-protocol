# Linting Standards

This document outlines the linting standards and rules for the Mind Protocol project. Adherence to these standards ensures code quality, maintainability, and consistency across the codebase.

## Pragma Discipline

Pragmas are **exceptions**, not defaults. They should be used sparingly and only when absolutely necessary, with clear justification.

### Denylist

The following categories of pragmas are **not allowed** and will result in a build failure (R-213):

*   **R-102 CITIZEN_ARRAY**: Suppressing hardcoded citizen arrays. Citizen lists must be resolved dynamically from environment variables or the organization graph.
*   **R-301 SILENT_FALLBACK**: Suppressing silent fallbacks. All error paths must either re-raise, return a typed `Err`, or emit a `failure` event.

### Override Process

To use a pragma for an allowed rule, the following criteria must be met:

*   **Owner**: The pragma must include an `owner:` tag specifying the responsible person or citizen (R-215).
*   **Reason**: A clear and concise `reason=` must be provided, explaining why the pragma is necessary. This reason should include a ticket number (e.g., `#123`) or an ISO date (R-210).
*   **Expiry**: The pragma should have an `expires_at` date (or a date in the reason) in the future. Pragmas with expired dates will cause a build failure (R-212).
*   **No Delta**: A pragma added in a hunk that only changes comments/whitespace or replaces a TODO with the pragma will cause a build failure (R-211).
*   **Budget**: Files or the repository exceeding a defined number of active pragmas will trigger a soft failure (R-214) until an override is granted.

## Fail Loudly in Code Paths (R-400/401)

All code paths must explicitly handle errors.

*   **R-400 FAIL_LOUD_REQUIRED**: Any broad `except` block must re-raise the exception, return a typed `Err` object, or log the error at a `warn` or `error` level.
*   **R-401 FAILURE_EVENT_MISSING**: If a non-raising fallback path exists, a `failure.emit()` call is required within the same block to ensure the failure is visible and traceable.
