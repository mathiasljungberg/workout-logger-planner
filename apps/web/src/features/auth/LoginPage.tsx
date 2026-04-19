import { FormEvent, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { api } from "../../lib/api/client";
import { queryKeys } from "../../lib/api/queries";

type LoginPageProps = {
  authenticated: boolean;
  onLogin: () => Promise<void>;
};

export function LoginPage({ authenticated, onLogin }: LoginPageProps) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const login = useMutation({
    mutationFn: (credentials: { username: string; password: string }) =>
      api.post("/auth/login", credentials),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.me });
      await onLogin();
      navigate("/calendar");
    },
  });

  if (authenticated) {
    return <Navigate to="/calendar" replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await login.mutateAsync({ username, password });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Login failed");
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
        <button type="submit" disabled={login.isPending}>
          {login.isPending ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </div>
  );
}
