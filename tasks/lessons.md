# Lessons

- When a frontend dev server and backend API run on different ports, do not rely on a root `.env` variable being present in the frontend process for basic API routing. Add an explicit dev proxy or a safe development default so auth and CRUD calls do not silently hit the frontend server and return 404.
- If the frontend calls the backend directly across origins in development, add explicit CORS middleware with credentials support. `curl` succeeding does not mean browser login will work.
