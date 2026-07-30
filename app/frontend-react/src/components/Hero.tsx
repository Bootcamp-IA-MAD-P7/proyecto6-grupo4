import heroStadium from "../assets/hero-stadium.webp";

export function Hero() {
  return (
    <section
      className="hero"
      aria-label="Presentación"
      style={{ backgroundImage: `url(${heroStadium})` }}
    >
      <div className="hero__overlay" aria-hidden="true" />

      <div className="hero__content">
        <span className="hero__badge">LaLiga EA Sports · Temporada 2026/27</span>
        <h1 className="hero__title">Predicción de Resultados de la Liga de Fútbol Español</h1>
        <p className="hero__subtitle">
          Análisis, probabilidades y factores clave para cada enfrentamiento.
        </p>
      </div>
    </section>
  );
}
