import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          padding: "2rem",
          textAlign: "center",
          background: "#0d1411",
          color: "#eef3ef",
          fontFamily: "Inter, system-ui, sans-serif",
        }}>
          <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>Algo salió mal</h1>
          <p style={{ color: "#9db2a8", marginBottom: "1.5rem", maxWidth: "400px" }}>
            Ha ocurrido un error inesperado. Por favor, recarga la página.
          </p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            style={{
              padding: "0.6rem 1.5rem",
              borderRadius: "999px",
              border: "none",
              background: "#1b7a3d",
              color: "#fff",
              fontWeight: 600,
              cursor: "pointer",
              fontSize: "0.9rem",
            }}
          >
            Recargar página
          </button>
          {this.state.error && (
            <pre style={{
              marginTop: "1.5rem",
              padding: "1rem",
              background: "#131c17",
              borderRadius: "8px",
              fontSize: "0.75rem",
              color: "#9db2a8",
              maxWidth: "100%",
              overflow: "auto",
            }}>
              {this.state.error.message}
            </pre>
          )}
        </div>
      );
    }
    return this.props.children;
  }
}
