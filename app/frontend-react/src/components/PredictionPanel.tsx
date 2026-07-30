import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch, ApiRequestError } from "../lib/api";
import { OUTCOME_LABEL } from "../lib/constants";
import type { Fixture, PredictionResult } from "../lib/types";

interface PredictionPanelProps {
  fixture: Fixture | null;
  onRequireAuth: () => void;
  onPredicted: () => void;
}



function ConfidenceRing({ value }: { value: number }) {
  const radius = 54;
  const stroke = 10;
  const normalizedRadius = radius - stroke / 2;
  const circumference = 2 * Math.PI * normalizedRadius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="confidence-ring">
      <svg width={radius * 2} height={radius * 2} viewBox={`0 0 ${radius * 2} ${radius * 2}`}>
        <circle
          className="confidence-ring__track"
          cx={radius}
          cy={radius}
          r={normalizedRadius}
          fill="none"
          stroke="var(--border)"
          strokeWidth={stroke}
        />
        <circle
          className="confidence-ring__fill"
          cx={radius}
          cy={radius}
          r={normalizedRadius}
          fill="none"
          stroke="var(--spain-yellow)"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${radius} ${radius})`}
        />
      </svg>
      <div className="confidence-ring__label">
        <span className="confidence-ring__value">{value}%</span>
        <span className="confidence-ring__text">CONFIANZA</span>
      </div>
    </div>
  );
}

export function PredictionPanel({ fixture, onRequireAuth, onPredicted }: PredictionPanelProps) {
  const { isAuthenticated } = useAuth();
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setResult(null);
    setError(null);
    if (!fixture) return;
    if (!isAuthenticated) return;

    let cancelled = false;
    setLoading(true);
    apiFetch<PredictionResult>("/api/v1/predictions", {
      method: "POST",
      body: JSON.stringify({ home_team: fixture.home_team, away_team: fixture.away_team, match_date: fixture.date }),
    })
      .then((payload) => {
        if (cancelled) return;
        setResult(payload);
        onPredicted();
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof ApiRequestError ? err.message : "No se pudo calcular la predicción.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fixture, isAuthenticated]);

  if (!fixture) {
    return (
      <section className="panel prediction-panel prediction-panel--empty">
        <p>Selecciona un partido de la lista para ver su predicción.</p>
      </section>
    );
  }

  return (
    <section className="panel prediction-panel" aria-live="polite">
      <div className="prediction-panel__header">
        <span className="prediction-panel__team prediction-panel__team--home">{fixture.home_label}</span>
        <span className="prediction-panel__vs">VS</span>
        <span className="prediction-panel__team prediction-panel__team--away">{fixture.away_label}</span>
      </div>
      <p className="prediction-panel__meta">
        {fixture.date.split("-").reverse().join("/")} {"\u00B7"} {fixture.time} {"\u00B7"} {"\u{1F4CD}"} {fixture.venue}, {fixture.city}
      </p>

      {!isAuthenticated && (
        <div className="prediction-panel__locked">
          <p>Inicia sesión para ver la predicción de este partido.</p>
          <button type="button" className="btn btn--primary" onClick={onRequireAuth}>
            Iniciar sesión
          </button>
        </div>
      )}

      {isAuthenticated && loading && <p className="upcoming__hint">Calculando predicción…</p>}
      {isAuthenticated && error && <p className="prediction-panel__error">{error}</p>}

      {isAuthenticated && result && (
        <div className="prediction-panel__result">
          {result.no_history && (
            <div className="prediction-panel__no-history">
              <p><strong>Sin histórico disponible.</strong> Este equipo fue recién ascendido a Primera División y aún no posee datos suficientes para generar una predicción fiable. Se muestran probabilidades por defecto.</p>
            </div>
          )}
          <div className="prediction-panel__badge">{OUTCOME_LABEL[result.prediction]}</div>

          <div className="prediction-panel__content">
            <ConfidenceRing value={Math.min(100, Math.round(Math.max(result.probabilities.H, result.probabilities.D, result.probabilities.A) * 100))} />

            <div className="prediction-panel__probabilities">
              <h3 className="prediction-panel__prob-title">Probabilidades</h3>
              <div className="bars">
                <div className="bar">
                  <span className="bar__label">Local</span>
                  <div className="bar__track">
                    <div className="bar__fill bar__fill--home" style={{ width: `${result.probabilities.H * 100}%` }} />
                  </div>
                  <span className="bar__value">{Math.round(result.probabilities.H * 100)}%</span>
                </div>
                <div className="bar">
                  <span className="bar__label">Empate</span>
                  <div className="bar__track">
                    <div className="bar__fill bar__fill--draw" style={{ width: `${result.probabilities.D * 100}%` }} />
                  </div>
                  <span className="bar__value">{Math.round(result.probabilities.D * 100)}%</span>
                </div>
                <div className="bar">
                  <span className="bar__label">Visitante</span>
                  <div className="bar__track">
                    <div className="bar__fill bar__fill--away" style={{ width: `${result.probabilities.A * 100}%` }} />
                  </div>
                  <span className="bar__value">{Math.round(result.probabilities.A * 100)}%</span>
                </div>
              </div>
            </div>
          </div>

          <p className="prediction-panel__disclaimer">Estimación probabilística basada únicamente en resultados históricos del desempeño de ambos contrincantes.</p>
        </div>
      )}
    </section>
  );
}
