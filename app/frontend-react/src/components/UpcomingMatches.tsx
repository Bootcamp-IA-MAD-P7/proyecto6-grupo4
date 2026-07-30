import type { Fixture } from "../lib/types";
import { MatchCard } from "./MatchCard";

interface UpcomingMatchesProps {
  fixtures: Fixture[];
  loading: boolean;
  selected: Fixture | null;
  onSelect: (fixture: Fixture) => void;
}

export function UpcomingMatches({ fixtures, loading, selected, onSelect }: UpcomingMatchesProps) {
  return (
    <section className="upcoming" aria-labelledby="upcoming-title">
      <h2 id="upcoming-title" className="panel__title">
        Próximos partidos (30 días)
      </h2>
      {loading && <p className="upcoming__hint">Cargando calendario…</p>}
      {!loading && fixtures.length === 0 && <p className="upcoming__hint">No hay partidos programados en este rango.</p>}
      <div className="upcoming__scroller">
        {fixtures.map((fixture) => (
          <MatchCard
            key={`${fixture.date}-${fixture.home_team}-${fixture.away_team}`}
            fixture={fixture}
            selected={
              selected?.date === fixture.date &&
              selected?.home_team === fixture.home_team &&
              selected?.away_team === fixture.away_team
            }
            onSelect={onSelect}
          />
        ))}
      </div>
    </section>
  );
}
