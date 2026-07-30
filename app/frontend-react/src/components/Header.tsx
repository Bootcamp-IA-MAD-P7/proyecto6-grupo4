import { useAuth } from "../context/AuthContext";

interface HeaderProps {
  onOpenAuth: (mode: "login" | "register") => void;
}

export function Header({ onOpenAuth }: HeaderProps) {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="topbar">
      <video
        className="topbar__video"
        aria-hidden="true"
        autoPlay
        loop
        muted
        playsInline
        poster="/goal-header-poster.jpg"
      >
        <source src="/goal-header.webm" type="video/webm" />
        <source src="/goal-header.mp4" type="video/mp4" />
      </video>
      <div className="topbar__video-overlay" aria-hidden="true" />

      <span className="sr-only">LaLiga Predictor</span>

      <div className="topbar__actions">
        {isAuthenticated ? (
          <>
            <span className="topbar__user">
              Hola, {user?.first_name} 👋
            </span>
            <button type="button" className="btn btn--ghost" onClick={logout}>
              Cerrar sesión
            </button>
          </>
        ) : (
          <>
            <button type="button" className="btn btn--ghost" onClick={() => onOpenAuth("login")}>
              Iniciar sesión
            </button>
            <button type="button" className="btn btn--primary" onClick={() => onOpenAuth("register")}>
              Registrarse
            </button>
          </>
        )}
      </div>
    </header>
  );
}
