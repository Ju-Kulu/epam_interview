# Task 10 - Frontend Chat UI

## Task name / goal
Implement a React chat interface that sends natural-language questions to the existing backend `/chat` endpoint and displays answers and source references.

## Prompt summary
Add a small typed frontend chat flow with question entry, loading and error states, answer/source rendering, and no duplicate backend logic or new UI framework. Do not modify backend or Docker files.

## Implementation / result
- Replaced the frontend placeholder with a responsive chat interface, conversation turns, an example question placeholder, loading feedback, readable request errors, and source references.
- Added TypeScript request/response/source types and runtime validation of the response payload.
- Requests use `/chat`; the Vite development proxy defaults to `http://localhost:8000` and can be configured with `VITE_API_PROXY_TARGET`, using `http://backend:8000` in Docker Compose.

## Files changed
- `frontend/src/App.tsx`
- `frontend/src/styles.css`
- `frontend/vite.config.ts`
- `ai-conversations/copilot-task-10.md`

## Tests / result
No frontend unit-test framework exists in the project. `npm run build` completed successfully (TypeScript and Vite production build). The Vite dev server started at `http://localhost:5173/`.

## Important decisions / assumptions
Used the existing Vite dev server as a same-origin proxy for `/chat`, avoiding backend CORS or source changes. Installed only dependencies already listed in `package.json`, with lockfile generation disabled.

## Corrections / limitations
The first build attempt could not find `tsc` because frontend dependencies were not installed; after installing declared dependencies, the build exposed one extra closing CSS brace, which was removed. The clean build passed. `npm install` reported two dependency audit findings (one moderate, one high); no audit fix or dependency upgrade was applied because dependency changes were outside scope.
