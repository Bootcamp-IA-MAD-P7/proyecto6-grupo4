import { useEffect, useState } from "react";

interface ModelMetrics {
  name: string;
  algorithm: string;
  valMacroF1: number;
  valAccuracy: number;
  valBalancedAcc: number;
  valLogLoss: number;
  overfitGap: number;
  trainTime: string;
  inferenceMs: string;
  champion?: boolean;
}

const MODELS: ModelMetrics[] = [
  { name: "Candidate A", algorithm: "Logistic Regression (Multinomial)", valMacroF1: 0.4646, valAccuracy: 0.5013, valBalancedAcc: 0.4787, valLogLoss: 1.0207, overfitGap: 0.0, trainTime: "0.54s", inferenceMs: "0.081" },
  { name: "Candidate B", algorithm: "HistGradientBoosting", valMacroF1: 0.4721, valAccuracy: 0.4812, valBalancedAcc: 0.4734, valLogLoss: 1.0286, overfitGap: 0.0499, trainTime: "45.35s", inferenceMs: "0.731" },
  { name: "Candidate C", algorithm: "Random Forest", valMacroF1: 0.4788, valAccuracy: 0.5021, valBalancedAcc: 0.4853, valLogLoss: 1.0219, overfitGap: 0.0, trainTime: "3.02s", inferenceMs: "0.408" },
  { name: "Candidate D", algorithm: "SVC RBF + CalibratedCV", valMacroF1: 0.4829, valAccuracy: 0.4954, valBalancedAcc: 0.4882, valLogLoss: 1.0517, overfitGap: 0.0101, trainTime: "81.29s", inferenceMs: "2.488" },
  { name: "ENSEMBLE ABCD", algorithm: "Soft Voting (A+B+C+D)", valMacroF1: 0.4853, valAccuracy: 0.4996, valBalancedAcc: 0.4901, valLogLoss: 1.0206, overfitGap: 0.0054, trainTime: "186.94s", inferenceMs: "2.488", champion: true },
];

const TOP_FEATURES = [
  { feature: "elo_difference_home", importance: 0.0326 },
  { feature: "away_elo_pre_match", importance: 0.0275 },
  { feature: "away_matches_played", importance: 0.0174 },
  { feature: "away_points_per_match_5", importance: 0.0162 },
  { feature: "away_team", importance: 0.0124 },
  { feature: "away_goals_for_per_match_5", importance: 0.0123 },
  { feature: "home_win_rate_5", importance: 0.0118 },
];

export function InfoPanel() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open]);

  return (
    <>
      <button
        type="button"
        className="info-fab"
        onClick={() => setOpen(true)}
        aria-label="Información del modelo"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
      </button>

      {open && (
        <div className="info-overlay" onClick={() => setOpen(false)}>
          <div className="info-modal" onClick={(e) => e.stopPropagation()}>
            <button type="button" className="info-modal__close" onClick={() => setOpen(false)} aria-label="Cerrar">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>

            <div className="info-modal__content">
              <h2 className="info-modal__title">Modelos entrenados</h2>
              <p className="info-modal__subtitle">
                Comparativa de todos los candidatos evaluados en el conjunto de validación.
              </p>

              <div className="info-table-wrapper">
                <table className="info-table">
                  <thead>
                    <tr>
                      <th>Modelo</th>
                      <th>Algoritmo</th>
                      <th>Macro F1</th>
                      <th>Accuracy</th>
                      <th>Bal. Accuracy</th>
                      <th>Log Loss</th>
                      <th>Gap</th>
                      <th>Inferencia</th>
                    </tr>
                  </thead>
                  <tbody>
                    {MODELS.map((m) => (
                      <tr key={m.name} className={m.champion ? "info-table__row--champion" : ""}>
                        <td>
                          <span className="info-table__name">
                            {m.name}
                            {m.champion && <span className="info-table__badge">Champion</span>}
                          </span>
                        </td>
                        <td>{m.algorithm}</td>
                        <td>{m.valMacroF1.toFixed(4)}</td>
                        <td>{m.valAccuracy.toFixed(4)}</td>
                        <td>{m.valBalancedAcc.toFixed(4)}</td>
                        <td>{m.valLogLoss.toFixed(4)}</td>
                        <td>{m.overfitGap.toFixed(4)}</td>
                        <td>{m.inferenceMs} ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="info-section">
                <h3 className="info-section__title">Métricas en test (frozen)</h3>
                <div className="info-test-metrics">
                  <div className="info-test-metric">
                    <span className="info-test-metric__value">0.4796</span>
                    <span className="info-test-metric__label">Macro F1</span>
                  </div>
                  <div className="info-test-metric">
                    <span className="info-test-metric__value">0.5061</span>
                    <span className="info-test-metric__label">Accuracy</span>
                  </div>
                  <div className="info-test-metric">
                    <span className="info-test-metric__value">0.4859</span>
                    <span className="info-test-metric__label">Bal. Accuracy</span>
                  </div>
                  <div className="info-test-metric">
                    <span className="info-test-metric__value">1.0104</span>
                    <span className="info-test-metric__label">Log Loss</span>
                  </div>
                </div>
              </div>

              <div className="info-section">
                <h3 className="info-section__title">Variables más importantes (Permutation Importance)</h3>
                <div className="info-features">
                  {TOP_FEATURES.map((f, i) => (
                    <div key={f.feature} className="info-feature">
                      <span className="info-feature__rank">{i + 1}</span>
                      <span className="info-feature__name">{f.feature}</span>
                      <div className="info-feature__bar-track">
                        <div className="info-feature__bar-fill" style={{ width: `${(f.importance / 0.035) * 100}%` }} />
                      </div>
                      <span className="info-feature__value">{f.importance.toFixed(4)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="info-section">
                <h3 className="info-section__title">¿Por qué se eligió este modelo?</h3>
                <div className="info-explanation">
                  <p>
                    El modelo final (<strong>ENSEMBLE ABCD</strong>) es un <em>VotingClassifier</em> con votación suave que
                    combina cuatro modelos individuales: Regresión Logística, HistGradientBoosting, Random Forest y
                    SVC calibrado con temperatura.
                  </p>
                  <p>
                    <strong>Criterio de selección:</strong> Se filtraron los candidatos con sobreajuste excesivo
                    (gap de macro-F1 entre train y validación {"<"} 0.05). Entre los elegibles, se seleccionó el de
                    <strong> mayor macro-F1 en validación</strong>. En caso de empate, se usó la menor latencia de inferencia.
                  </p>
                  <p>
                    <strong>¿Por qué el ensamble?</strong> El ensamble de los 4 modelos alcanzó un macro-F1 de validación
                    de <strong>0.4853</strong>, superando al mejor modelo individual (Candidate D con 0.4829). Además,
                    tiene el menor gap de sobreajuste (0.0054), lo que indica la mejor generalización. La combinación de
                    modelos con arquitecturas diferentes (lineal, árboles, kernel) captura patrones complementarios
                    del histórico de LaLiga.
                  </p>
                  <p>
                    <strong>Features clave:</strong> La diferencia de Elo entre equipos (<code>elo_difference_home</code>)
                    es la variable más predictiva, seguida del Elo del visitante y su rendimiento reciente
                    (puntos por partido, partidos jugados en los últimos 5 encuentros).
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
