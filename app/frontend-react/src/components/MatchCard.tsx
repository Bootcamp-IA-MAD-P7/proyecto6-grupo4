import type { Fixture } from "../lib/types";

interface MatchCardProps {
  fixture: Fixture;
  selected?: boolean;
  onSelect: (fixture: Fixture) => void;
}

function formatDate(iso: string): string {
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}

export function MatchCard({ fixture, selected, onSelect }: MatchCardProps) {
  return (
    <button
      type="button"
      className={`match-card ${selected ? "match-card--selected" : ""}`}
      onClick={() => onSelect(fixture)}
      aria-pressed={selected}
      aria-label={`${fixture.home_label} vs ${fixture.away_label}, ${formatDate(fixture.date)} ${fixture.time}`}
    >
      <div className="match-card__meta">
        <span>{formatDate(fixture.date)}</span>
        <span>{fixture.time}</span>
      </div>
      <div className="match-card__teams">
        <span className="match-card__team">
          <small>Local</small>
          {fixture.home_label}
        </span>
        <span className="match-card__vs">vs</span>
        <span className="match-card__team match-card__team--away">
          <small>Visitante</small>
          {fixture.away_label}
        </span>
      </div>
      <div className="match-card__venue">
        📍 {fixture.venue} · {fixture.city}
      </div>
      {!fixture.has_history && <div className="match-card__badge">Equipo ascendido · sin histórico</div>}
    </button>
  );
}
