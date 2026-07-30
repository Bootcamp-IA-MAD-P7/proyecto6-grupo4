import { useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { ApiRequestError } from "../lib/api";

interface AuthModalProps {
  mode: "login" | "register";
  onClose: () => void;
  onSwitchMode: (mode: "login" | "register") => void;
}

export function AuthModal({ mode, onClose, onSwitchMode }: AuthModalProps) {
  const { login, register } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [phone, setPhone] = useState("");
  const [acceptsTerms, setAcceptsTerms] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        if (!acceptsTerms) {
          setError("Debes confirmar que eres mayor de 18 años y que los datos son correctos.");
          setLoading(false);
          return;
        }
        await register({
          first_name: firstName,
          last_name: lastName,
          birth_date: birthDate,
          phone,
          email,
          password,
          accepts_terms: acceptsTerms,
        });
      }
      onClose();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Ocurrió un error inesperado.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="modal auth-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-modal-title"
      >
        <button type="button" className="modal__close" onClick={onClose} aria-label="Cerrar">
          ×
        </button>

        <div className="auth-modal__tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={mode === "login"}
            className={`auth-modal__tab ${mode === "login" ? "auth-modal__tab--active" : ""}`}
            onClick={() => onSwitchMode("login")}
          >
            Iniciar sesión
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === "register"}
            className={`auth-modal__tab ${mode === "register" ? "auth-modal__tab--active" : ""}`}
            onClick={() => onSwitchMode("register")}
          >
            Registrarse
          </button>
        </div>

        <h2 id="auth-modal-title" className="auth-modal__title">
          {mode === "login" ? "Bienvenido de nuevo" : "Crea tu cuenta"}
        </h2>

        <form className="auth-modal__form" onSubmit={handleSubmit}>
          {mode === "register" && (
            <>
              <div className="field-row">
                <div className="field">
                  <label htmlFor="first-name">Nombre</label>
                  <input id="first-name" required value={firstName} onChange={(e) => setFirstName(e.target.value)} />
                </div>
                <div className="field">
                  <label htmlFor="last-name">Apellido</label>
                  <input id="last-name" required value={lastName} onChange={(e) => setLastName(e.target.value)} />
                </div>
              </div>
              <div className="field-row">
                <div className="field">
                  <label htmlFor="birth-date">Fecha de nacimiento</label>
                  <input
                    id="birth-date"
                    type="date"
                    required
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                  />
                </div>
                <div className="field">
                  <label htmlFor="phone">Teléfono</label>
                  <input
                    id="phone"
                    type="tel"
                    required
                    placeholder="+34 600 123 456"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                  />
                </div>
              </div>
            </>
          )}

          <div className="field">
            <label htmlFor="email">Correo electrónico</label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="field">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {mode === "register" && <small className="field__hint">Mínimo 8 caracteres.</small>}
          </div>

          {mode === "register" && (
            <label className="checkbox-field">
              <input
                type="checkbox"
                checked={acceptsTerms}
                onChange={(e) => setAcceptsTerms(e.target.checked)}
                required
              />
              <span>
                Confirmo que soy <strong>mayor de 18 años</strong> y que los datos ingresados son
                correctos y verídicos.
              </span>
            </label>
          )}

          {error && <p className="auth-modal__error">{error}</p>}

          <button type="submit" className="btn btn--primary" disabled={loading}>
            {loading ? "Procesando…" : mode === "login" ? "Entrar" : "Crear cuenta y entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
