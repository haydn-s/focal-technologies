# Focal Family — React UI preview

A Gemini / Google AI Studio-generated React UI candidate contributed by Qingyi Hu, imported from `focal-family-2026-11-5-00-59-27.zip` on November 5, 2026. This is a separate prototype; the existing Streamlit implementation in `../focal-family/` remains the current independent demo.

The brand-blue theme refresh was imported from `untitled-2026-11-5-14-32-13.zip` on November 5, 2026. App source and the independent HTML snapshot were updated; packaging fixes and Focal page metadata were retained.

## Run the React app

Use Node.js 22.12+ (validated with Node.js 24.20.0).

```sh
cd prototypes/focal-family-ui
npm ci
npm run dev
```

Open the local URL printed by Vite (normally http://localhost:3000). No Gemini API key or backend is required. The entry point is `index.html`, with application code in `src/`. Google Fonts are requested by the React entry page; system-font fallbacks are provided.

## Checks and build

```sh
npm run lint
npm test
npm run build
npm run preview
```

`npm run lint` runs TypeScript checking. `npm test` runs the six supplied logic tests. Build output goes to `dist/`, which is intentionally excluded from Git. Deploying this static build requires separate hosting; merging this directory does not update the Streamlit app.

## Standalone HTML preview

Open `public/focal-family-preview.html` directly for a build-free preview. It is a separately implemented snapshot, not an automatically generated export of the React app; later React changes will not update it. The React app is the preferred implementation for further development.

## Scope and provenance

Includes the welcome, guided setup, directional-letter activity, completion, parent-note, and history screens, plus the DMV concept modal and session drawer. The official team logo is rendered inline; the supplied SVG original is retained in `public/assets/aistudio/` for reference.

The contributor supplied the AI Studio design and implementation. Codex packaged it into this isolated directory, removed unused template dependencies and AI Studio metadata, added reproducible install/test scripts, and checked build/types/supplied tests. These checks do not establish clinical validity, measurement accuracy, accessibility compliance, or complete browser coverage.

The activity is a student interaction prototype, not a diagnosis or validated vision screening. Fictional examples must remain clearly labeled. Session records are held in React memory rather than a backend. The independent HTML preview is preserved as supplied.

AI Studio temporary screenshots, generation plans, unused reference HTML, and template environment/API-capability metadata are omitted. No secret or `.env` file is required or included. The original ZIP remains unchanged outside this repository.
