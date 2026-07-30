import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../lib/api";
import { OUTCOME_LABEL } from "../lib/constants";
import type { HistoryItem } from "../lib/types";

interface HistoryProps {
  refreshToken: number;
}

export function History({ refreshToken }: HistoryProps) {
  const { isAuthenticated } = useAuth();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      setItems([]);
      return;
    }
    const controller = new AbortController();
    setLoading(true);
    apiFetch<{ items: HistoryItem[] }>("/api/v1/history")
      .then((payload) => {
        if (!controller.signal.aborted) setItems(payload.items);
      })
      .catch(() => {
        if (!controller.signal.aborted) setItems([]);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [isAuthenticated, refreshToken]);

  return (
    <section className="sidebar-block" aria-labelledby="history-title">
      <h2 id="history-title" className="panel__title">
        Tu historial
      </h2>
      {!isAuthenticated && <p className="upcoming__hint">Inicia sesión para ver tu historial de consultas.</p>}
      {isAuthenticated && loading && <p className="upcoming__hint">Cargando…</p>}
      {isAuthenticated && !loading && items.length === 0 && (
        <p className="upcoming__hint">Aún no hay predicciones. Empieza seleccionando un partido.</p>
      )}
      <ul className="history-list" aria-label="Historial de predicciones">
        {items.map((item) => (
          <li key={item.request_id} className="history-list__item">
            <div>
              <strong>{item.home_team}</strong> vs <strong>{item.away_team}</strong>
              <br />
              <small>
                {item.match_date.split("-").reverse().join("/")} · {OUTCOME_LABEL[item.prediction as keyof typeof OUTCOME_LABEL]}
              </small>
            </div>
            <span className="bar__value">
              {Math.round(Math.max(item.probabilities.H, item.probabilities.D, item.probabilities.A) * 100)}%
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
