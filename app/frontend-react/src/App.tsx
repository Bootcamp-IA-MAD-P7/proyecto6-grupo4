import { useEffect, useState } from "react";
import { AuthModal } from "./components/AuthModal";
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
  const { isAuthenticated } = useAuth();
  const [authModal, setAuthModal] = useState<"login" | "register" | null>(null);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [loadingFixtures, setLoadingFixtures] = useState(true);
  const [selectedFixture, setSelectedFixture] = useState<Fixture | null>(null);
  const [historyRefreshToken, setHistoryRefreshToken] = useState(0);

  useEffect(() => {
    apiFetch<{ items: Fixture[] }>("/api/v1/fixtures?days=30")
      .then((payload) => setFixtures(payload.items))
      .catch(() => setFixtures([]))
      .finally(() => setLoadingFixtures(false));
  }, []);

  function handleSelectFixture(fixture: Fixture) {
    setSelectedFixture(fixture);
    if (!isAuthenticated) setAuthModal("login");
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

      {authModal && <AuthModal mode={authModal} onClose={() => setAuthModal(null)} onSwitchMode={setAuthModal} />}
      <InfoPanel />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}

export default App;
