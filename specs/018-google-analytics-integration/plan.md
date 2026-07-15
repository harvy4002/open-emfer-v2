# Implementation Plan: Google Analytics Integration

**Branch**: `018-google-analytics-integration` | **Date**: Wednesday, July 15, 2026 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/018-google-analytics-integration/spec.md`

## Summary

This feature designs and implements Google Analytics 4 (GA4) integration into the public dashboard (`web/index.html`).

The configuration key is completely segregated inside a dedicated static script file `web/js/config.js` to ensure zero hardcoded keys. The dashboard controller (`web/js/app.js`) evaluates the configuration on load and dynamically injects the Google site tag manager script into the `<head>` of `index.html` at runtime.

---

## Technical Context

**Language/Version**: Vanilla browser ECMAScript 6 JavaScript & HTML5

**Primary Dependencies**: None (Standard browser W3C DOM manipulation and Google Tag Manager external script), maintaining a completely static, lightweight front-end footprint

**Storage**: External configuration file (`web/js/config.js`), requiring **zero** server-side database tables

**Testing**: Browser console logs, DOM element inspections, and network call checks

**Target Platform**: Any modern HTML5/W3C compliant web browser

**Project Type**: Standalone Static Frontend Integration

**Performance Goals**: Dynamic tag script injected and compiled under 30ms on load

**Constraints**: Absolute $0 runtime server hosting costs, matching Principle VII; graceful bypass with zero exceptions when GA measurement key is unconfigured or blank

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Contract-First)**: **PASS**. Fully specified in `spec.md` and caching variables configured in `data-model.md`.
- **Principle II (Serverless Simplicity)**: **PASS**. Introduces zero serverless Python dependencies, Lambda cold starts, or additional AWS services.
- **Principle IV (Database Modeling)**: **PASS**. Operates 100% client-side, requiring zero database modifications.
- **Principle VII (Cost-Optimized Static Frontend)**: **PASS**. Designed strictly as standard browser Fetch/API interactions with $0 runtime hosting costs.
- **Principle VIII (Fast Feedback Loop)**: **PASS**. Instantly runnable and testable locally on port 3000 using the python simulation server.

---

## Project Structure

### Documentation (this feature)

```text
specs/018-google-analytics-integration/
├── spec.md              # Functional specification and user scenarios
├── plan.md              # Implementation plan (this file)
├── research.md          # Architectural decision record
├── data-model.md        # Extended client-side storage blueprints
├── quickstart.md        # Step-by-step validation guide
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code (repository root)

```text
web/
├── index.html           # Add script import for config.js before app.js
└── js/
    ├── config.js        # Create a new centralized configuration file
    └── app.js           # Add dynamic script injection loop on page load
```

**Structure Decision**: Web application option.

---

## Complexity Tracking

*No Constitution Check violations or complexity deviations are identified. The design is completely clean, serverless, and lightweight.*
