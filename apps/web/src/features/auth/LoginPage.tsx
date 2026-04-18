import { FormEvent, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { api } from "../../lib/api/client";

type LoginPageProps = {
  authenticated: boolean;
  onLogin: () => Promise<void>;
};

export function LoginPage({ authenticated, onLogin }: LoginPageProps) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  if (authenticated) {
    return <Navigate to="/calendar" replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.post("/auth/login", { username, password });
      await onLogin();
      navigate("/calendar");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login">
      <form className="card login__card" onSubmit={handleSubmit}>
        <p className="eyebrow">Single-user access</p>
        <h1>Workout Tracker</h1>
        <p className="page__description">Log in with the seeded admin account to start planning and logging.</p>
        <label>
          Username
          <input value={username} onChange={(event) => setUsername(event.target.value)} />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error ? <p className="error">{error}</p> : null}
        <button type="submit" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </div>
  );
}

