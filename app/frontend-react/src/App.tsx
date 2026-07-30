import { useEffect, useState } from "react";
import { AuthModal } from "./components/AuthModal";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { InfoPanel } from "./components/InfoPanel";
import { PredictionPanel } from "./components/PredictionPanel";
import { Sidebar } from "./components/Sidebar";
import { UpcomingMatches } from "./components/UpcomingMatches";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { apiFetch } from "./lib/api";
import type { Fixture } from "./lib/types";

function AppShell() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [authModal, setAuthModal] = useState<"login" | "register" | null>(null);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [loadingFixtures, setLoadingFixtures] = useState(true);
  const [selectedFixture, setSelectedFixture] = useState<Fixture | null>(null);
  const [historyRefreshToken, setHistoryRefreshToken] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    apiFetch<{ items: Fixture[] }>("/api/v1/fixtures?days=30", { signal: controller.signal })
      .then((payload) => {
        if (!controller.signal.aborted) setFixtures(payload.items);
      })
      .catch(() => {
        if (!controller.signal.aborted) setFixtures([]);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoadingFixtures(false);
      });
    return () => controller.abort();
  }, []);

  function handleSelectFixture(fixture: Fixture) {
    setSelectedFixture(fixture);
    if (!isAuthenticated) setAuthModal("login");
  }

  if (authLoading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", background: "#0d1411", color: "#9db2a8" }}>
        Cargando…
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Header onOpenAuth={setAuthModal} />

      <div className="app-body">
        <Sidebar
          selectedFixture={selectedFixture}
          onSelectFixture={handleSelectFixture}
          historyRefreshToken={historyRefreshToken}
        />

        <main className="app-main">
          <Hero />
          <UpcomingMatches
            fixtures={fixtures}
            loading={loadingFixtures}
            selected={selectedFixture}
            onSelect={handleSelectFixture}
          />
          <PredictionPanel
            fixture={selectedFixture}
            onRequireAuth={() => setAuthModal("login")}
            onPredicted={() => setHistoryRefreshToken((n) => n + 1)}
          />
        </main>
      </div>

      <footer className="footer">
        <p>Predicción de Resultados de la Liga de Fútbol Español · Estimaciones basadas en histórico real</p>
      </footer>

      {authModal && <AuthModal key={authModal} mode={authModal} onClose={() => setAuthModal(null)} onSwitchMode={setAuthModal} />}
      <InfoPanel />
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppShell />
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
