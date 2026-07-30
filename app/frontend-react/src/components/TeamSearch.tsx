import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { FALLBACK_TEAMS } from "../lib/teams";
import type { Fixture, Team } from "../lib/types";
import { MatchCard } from "./MatchCard";

interface TeamSearchProps {
  selectedFixture: Fixture | null;
  onSelectFixture: (fixture: Fixture) => void;
}

export function TeamSearch({ selectedFixture, onSelectFixture }: TeamSearchProps) {
  const [teams, setTeams] = useState<Team[]>(FALLBACK_TEAMS);
  const [team, setTeam] = useState("");
  const [results, setResults] = useState<Fixture[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    apiFetch<{ items: Team[] }>("/api/v1/teams", { signal: controller.signal })
      .then((payload) => {
        if (!controller.signal.aborted && payload.items.length) setTeams(payload.items);
      })
      .catch(() => {
        /* se mantiene el catálogo de respaldo */
      });
    return () => controller.abort();
  }, []);

  async function handleSearch() {
    if (!team) return;
    setLoading(true);
    setError(null);
    try {
      const payload = await apiFetch<{ items: Fixture[] }>(`/api/v1/fixtures?team=${encodeURIComponent(team)}`);
      setResults(payload.items);
    } catch {
      setError("No se pudieron cargar los partidos de este equipo.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="sidebar-block" aria-labelledby="search-title">
      <h2 id="search-title" className="panel__title">
        Buscar por equipo
      </h2>
      <div className="team-search__controls">
        <select value={team} onChange={(e) => setTeam(e.target.value)} aria-label="Selecciona un equipo">
          <option value="" disabled>
            Selecciona un equipo
          </option>
          {teams.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
        <button type="button" className="btn btn--primary btn--block" onClick={handleSearch} disabled={!team || loading}>
          {loading ? "Buscando…" : "Buscar Próximos Partidos"}
        </button>
      </div>

      {error && <p className="prediction-panel__error">{error}</p>}

      {results && (
        <div className="team-search__results">
          {results.length === 0 && <p className="upcoming__hint">Este equipo no tiene más partidos esta temporada.</p>}
          {results.map((fixture) => (
            <MatchCard
              key={`${fixture.date}-${fixture.home_team}-${fixture.away_team}`}
              fixture={fixture}
              selected={
                selectedFixture?.date === fixture.date &&
                selectedFixture?.home_team === fixture.home_team &&
                selectedFixture?.away_team === fixture.away_team
              }
              onSelect={onSelectFixture}
            />
          ))}
        </div>
      )}
    </section>
  );
}
