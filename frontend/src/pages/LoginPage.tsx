import { FormEvent, useState } from "react";
import { BookOpenCheck, Loader2, LockKeyhole, UserRound } from "lucide-react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/authContext";

type LocationState = {
  from?: {
    pathname?: string;
  };
};

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, login, loginError } = useAuth();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = (location.state as LocationState | null)?.from?.pathname ?? "/";

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);

    try {
      await login({ username, password });
      navigate(from, { replace: true });
    } finally {
      setIsSubmitting(false);
    }
  }

  function applyDemoCredentials(nextUsername: string, nextPassword: string) {
    setUsername(nextUsername);
    setPassword(nextPassword);
  }

  return (
    <main className="login-page">
      <section className="login-panel" aria-labelledby="login-title">
        <div className="login-panel__intro">
          <div className="login-brand">
            <div className="login-brand__mark">ЭЖ</div>
            <div>
              <p>Электронный журнал</p>
              <span>рабочий доступ</span>
            </div>
          </div>
          <h1 id="login-title">Вход в систему</h1>
          <p>Используйте учетную запись администратора, преподавателя или студента.</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Логин</span>
            <div className="field__control">
              <UserRound aria-hidden="true" size={18} />
              <input
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
              />
            </div>
          </label>

          <label className="field">
            <span>Пароль</span>
            <div className="field__control">
              <LockKeyhole aria-hidden="true" size={18} />
              <input
                autoComplete="current-password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>
          </label>

          {loginError ? <div className="form-error">{loginError}</div> : null}

          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? <Loader2 aria-hidden="true" className="spin" size={18} /> : <BookOpenCheck aria-hidden="true" size={18} />}
            <span>{isSubmitting ? "Входим" : "Войти"}</span>
          </button>
        </form>

        <div className="demo-accounts">
          <span>Демо-доступ</span>
          <button type="button" onClick={() => applyDemoCredentials("admin", "admin123")}>
            admin / admin123
          </button>
          <button type="button" onClick={() => applyDemoCredentials("teacher", "teacher123")}>
            teacher / teacher123
          </button>
          <button type="button" onClick={() => applyDemoCredentials("student", "student123")}>
            student / student123
          </button>
        </div>
      </section>
    </main>
  );
}
