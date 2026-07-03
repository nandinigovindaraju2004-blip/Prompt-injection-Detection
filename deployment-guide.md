# Deployment Guide

## 1. MongoDB Atlas (database)
1. Create a free cluster at https://www.mongodb.com/atlas
2. Create a database user + allow-list your deploy platform's IP (or `0.0.0.0/0` for demo).
3. Copy the connection string into `MONGO_URI`.

## 2. Backend on Render
1. Push `server/` to a GitHub repo (or the whole monorepo, setting Render's root directory to
   `server`).
2. New Web Service → connect repo → Build command `npm install` → Start command `npm start`.
3. Add environment variables from `server/.env.example`: `MONGO_URI`, `JWT_SECRET`,
   `OPENAI_API_KEY`, `OPENAI_MODEL`.
4. **Python runtime**: Render's Node environment doesn't include Python by default. Either:
   - Use a Render "Native Environment" with a `render-build.sh` that also runs
     `pip install -r server/ml/requirements.txt`, or
   - (Recommended for production) extract `server/ml` into its own small Flask service
     deployed separately (e.g. Render Python service) and change `mlEngine.js` to call it
     over HTTP instead of spawning a subprocess.
5. Note the deployed URL, e.g. `https://prompt-guard-api.onrender.com`.

## 3. Frontend on Vercel
1. Import the repo into Vercel, set root directory to `client`.
2. Add environment variable `NEXT_PUBLIC_API_URL=https://prompt-guard-api.onrender.com/api`.
3. Deploy.

## 4. Post-deploy checklist
- [ ] Rotate `JWT_SECRET` to a long random value (never reuse the `.env.example` placeholder).
- [ ] Set a real `OPENAI_API_KEY` (or leave unset — the app degrades gracefully and returns a
      placeholder AI response).
- [ ] Confirm CORS: `app.js` currently allows all origins (`cors()`); restrict to your Vercel
      domain in production via `cors({ origin: "https://yourapp.vercel.app" })`.
- [ ] Confirm the rate limiter (`express-rate-limit`) values suit expected traffic.
- [ ] Create an admin user manually in MongoDB (set `role: "admin"`) to unlock the aggregate
      (all-users) dashboard view.
