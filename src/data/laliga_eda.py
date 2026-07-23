"""EDA reproducible del dataset canónico de LaLiga."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import chi2_contingency
from sklearn.metrics import confusion_matrix, log_loss

from src.data.laliga_loader import (
    DETAILED_FILENAME,
    HISTORICAL_FILENAME,
    SOURCE_PROVENANCE,
    TARGET_COLUMN,
    audit_dataset,
)


RESULT_ORDER = ["H", "D", "A"]
RESULT_LABELS = {"H": "Victoria local", "D": "Empate", "A": "Victoria visitante"}
RESULT_COLORS = {"H": "#2E8B57", "D": "#D4A72C", "A": "#C44E52"}

POST_EVENT_LEAKAGE = {
    "home_goals_ft", "away_goals_ft", "home_goals_ht", "away_goals_ht", "result_ht",
    "total_goals", "goal_diff_home", "both_teams_scored", "over_2_5",
    "clean_sheet_home", "clean_sheet_away", "home_points", "away_points",
    "shots_home", "shots_away", "shots_on_target_home", "shots_on_target_away",
    "fouls_home", "fouls_away", "corners_home", "corners_away",
    "yellow_cards_home", "yellow_cards_away", "red_cards_home", "red_cards_away",
}
IDENTIFIERS = {"match_id"}
METADATA = {"source_coverage", "has_detailed_stats", "league_code"}
CLOSING_MARKET = {
    "odds_avg_home_close", "odds_avg_draw_close", "odds_avg_away_close",
    "odds_avg_over_2_5_close", "odds_avg_under_2_5_close", "asian_handicap_line_close",
    "odds_avg_asian_home_close", "odds_avg_asian_away_close",
}


def _configure_style() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 10,
            "font.family": "DejaVu Sans",
        }
    )


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _cramers_v(left: pd.Series, right: pd.Series) -> float:
    table = pd.crosstab(left, right)
    if min(table.shape) < 2:
        return 0.0
    chi2 = chi2_contingency(table, correction=False)[0]
    n = table.to_numpy().sum()
    phi2 = chi2 / n
    rows, cols = table.shape
    correction = ((cols - 1) * (rows - 1)) / (n - 1)
    phi2_corr = max(0.0, phi2 - correction)
    rows_corr = rows - ((rows - 1) ** 2) / (n - 1)
    cols_corr = cols - ((cols - 1) ** 2) / (n - 1)
    denominator = min(cols_corr - 1, rows_corr - 1)
    return float(np.sqrt(phi2_corr / denominator)) if denominator > 0 else 0.0


def _iqr_outliers(series: pd.Series) -> dict[str, float | int | None]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return {"count": 0, "pct": 0.0, "lower": None, "upper": None}
    q1, q3 = clean.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    count = int(((clean < lower) | (clean > upper)).sum())
    return {
        "count": count,
        "pct": float(count / len(clean)),
        "lower": float(lower),
        "upper": float(upper),
    }


def build_data_dictionary(frame: pd.DataFrame) -> pd.DataFrame:
    """Contrato provisional por variable, incluyendo disponibilidad y leakage."""

    descriptions = {
        "match_id": "Identificador único fecha-local-visitante.",
        "season": "Temporada normalizada YYYY-YY.",
        "match_date": "Fecha del encuentro.",
        "match_time": "Hora publicada del encuentro; solo disponible en la fuente detallada.",
        "match_year": "Año natural derivado de la fecha.",
        "match_month": "Mes natural derivado de la fecha.",
        "iso_weekday": "Día ISO de la semana (1=lunes, 7=domingo).",
        "home_team": "Equipo local.",
        "away_team": "Equipo visitante.",
        "result_ft": "Target provisional: H local, D empate, A visitante.",
        "source_coverage": "Cobertura de la fila en las fuentes raw.",
        "has_detailed_stats": "Indica disponibilidad del bloque detallado 2025-26.",
        "league_code": "Código de competición de la fuente.",
    }
    rows: list[dict[str, Any]] = []
    for column in frame.columns:
        if column == TARGET_COLUMN:
            role = "target"
            availability = "after_match"
            leakage = "target"
            null_treatment = "reject_row_if_missing"
        elif column in IDENTIFIERS:
            role = "identifier"
            availability = "pre_match"
            leakage = "none_but_no_predictive_role"
            null_treatment = "reject_row_if_missing"
        elif column in POST_EVENT_LEAKAGE:
            role = "excluded"
            availability = "after_match"
            leakage = "critical_post_event"
            null_treatment = "do_not_impute_for_pre_match_model"
        elif column in METADATA:
            role = "excluded"
            availability = "pipeline_metadata"
            leakage = "source_or_coverage_proxy"
            null_treatment = "not_applicable"
        elif column in CLOSING_MARKET:
            role = "conditional_feature"
            availability = "near_kickoff_only"
            leakage = "timing_risk"
            null_treatment = "pipeline_decision_pending"
        else:
            role = "candidate_feature"
            availability = "pre_match"
            leakage = "none_identified"
            null_treatment = "pipeline_decision_pending"

        series = frame[column]
        if pd.api.types.is_datetime64_any_dtype(series):
            allowed = f"{series.min():%Y-%m-%d} .. {series.max():%Y-%m-%d}"
            data_type = "datetime"
        elif pd.api.types.is_numeric_dtype(series):
            clean = pd.to_numeric(series, errors="coerce").dropna()
            allowed = f"{clean.min():g} .. {clean.max():g}" if not clean.empty else "sin valores"
            data_type = str(series.dtype)
        else:
            unique = series.dropna().astype(str).unique()
            allowed = " | ".join(sorted(unique)[:12]) + (" | …" if len(unique) > 12 else "")
            data_type = str(series.dtype)

        if column.startswith("odds_"):
            description = "Cuota media decimal del mercado indicado en el nombre de la variable."
        elif column.startswith("asian_handicap"):
            description = "Línea de hándicap asiático media del mercado indicado."
        elif column in descriptions:
            description = descriptions[column]
        else:
            description = column.replace("_", " ").capitalize() + "."

        rows.append(
            {
                "column": column,
                "description": description,
                "dtype": data_type,
                "role": role,
                "allowed_values_or_range": allowed,
                "missing_count": int(series.isna().sum()),
                "missing_pct": float(series.isna().mean()),
                "null_treatment": null_treatment,
                "available_at_inference": availability,
                "leakage_risk": leakage,
            }
        )
    return pd.DataFrame(rows)


def calculate_eda_metrics(frame: pd.DataFrame) -> dict[str, Any]:
    target_counts = frame[TARGET_COLUMN].value_counts().reindex(RESULT_ORDER, fill_value=0)
    target_shares = (target_counts / len(frame)).reindex(RESULT_ORDER)
    majority_class = str(target_counts.idxmax())
    majority_predictions = np.full(len(frame), majority_class)
    majority_confusion = confusion_matrix(
        frame[TARGET_COLUMN],
        majority_predictions,
        labels=RESULT_ORDER,
    )
    missingness = frame.isna().mean().sort_values(ascending=False)
    season_result = pd.crosstab(frame["season"], frame[TARGET_COLUMN], normalize="index").reindex(
        columns=RESULT_ORDER, fill_value=0
    )
    season_summary = frame.groupby("season", observed=True).agg(
        matches=("match_id", "size"),
        home_win_rate=("result_ft", lambda s: float(s.eq("H").mean())),
        draw_rate=("result_ft", lambda s: float(s.eq("D").mean())),
        away_win_rate=("result_ft", lambda s: float(s.eq("A").mean())),
        avg_total_goals=("total_goals", "mean"),
        avg_home_goal_diff=("goal_diff_home", "mean"),
    )

    detailed = frame.loc[frame["has_detailed_stats"].fillna(False)].copy()
    odds = detailed.dropna(
        subset=["odds_avg_home_open", "odds_avg_draw_open", "odds_avg_away_open", TARGET_COLUMN]
    ).copy()
    market: dict[str, Any] = {"rows_with_complete_opening_odds": int(len(odds))}
    market_confusion = np.zeros((3, 3), dtype=int)
    if not odds.empty:
        raw_probs = 1 / odds[["odds_avg_home_open", "odds_avg_draw_open", "odds_avg_away_open"]].to_numpy()
        probs = raw_probs / raw_probs.sum(axis=1, keepdims=True)
        picks = np.array(RESULT_ORDER)[np.argmax(probs, axis=1)]
        y_true = odds[TARGET_COLUMN].to_numpy()
        market_confusion = confusion_matrix(y_true, picks, labels=RESULT_ORDER)
        market.update(
            {
                "favorite_accuracy": float(np.mean(picks == y_true)),
                "multiclass_log_loss": float(
                    log_loss(y_true, probs[:, [2, 1, 0]], labels=["A", "D", "H"])
                ),
                "mean_overround": float(raw_probs.sum(axis=1).mean() - 1),
                "confusion_matrix": market_confusion.tolist(),
            }
        )

    outlier_columns = [
        "home_goals_ft", "away_goals_ft", "total_goals", "shots_home", "shots_away",
        "shots_on_target_home", "shots_on_target_away", "fouls_home", "fouls_away",
        "yellow_cards_home", "yellow_cards_away", "red_cards_home", "red_cards_away",
    ]
    outliers = {column: _iqr_outliers(frame[column]) for column in outlier_columns}
    return {
        "quality": audit_dataset(frame),
        "target": {
            "counts": {key: int(value) for key, value in target_counts.items()},
            "shares": {key: float(value) for key, value in target_shares.items()},
            "majority_class": majority_class,
            "majority_baseline_accuracy": float(target_shares.max()),
            "majority_confusion_matrix": majority_confusion.tolist(),
            "max_to_min_ratio": (
                float(target_counts.max() / target_counts[target_counts.gt(0)].min())
                if target_counts.gt(0).any()
                else 0.0
            ),
        },
        "missingness": {
            "columns_with_missing": int((missingness > 0).sum()),
            "columns_over_90_pct_missing": int((missingness > 0.9).sum()),
            "top": {key: float(value) for key, value in missingness.head(20).items()},
        },
        "temporal": {
            "season_summary": season_summary.reset_index().to_dict(orient="records"),
            "result_share_by_season": season_result.reset_index().to_dict(orient="records"),
        },
        "goals": {
            "mean_total": float(frame["total_goals"].mean()),
            "median_total": float(frame["total_goals"].median()),
            "pct_over_2_5": float(frame["over_2_5"].mean()),
            "pct_both_teams_scored": float(frame["both_teams_scored"].mean()),
            "mean_home": float(frame["home_goals_ft"].mean()),
            "mean_away": float(frame["away_goals_ft"].mean()),
        },
        "associations": {
            "season_vs_target_cramers_v": _cramers_v(frame["season"], frame[TARGET_COLUMN]),
            "home_team_vs_target_cramers_v": _cramers_v(frame["home_team"], frame[TARGET_COLUMN]),
            "away_team_vs_target_cramers_v": _cramers_v(frame["away_team"], frame[TARGET_COLUMN]),
        },
        "cardinality": {
            "match_id_unique_pct": float(frame["match_id"].nunique() / len(frame)),
            "home_teams": int(frame["home_team"].nunique()),
            "away_teams": int(frame["away_team"].nunique()),
            "seasons": int(frame["season"].nunique()),
        },
        "detailed_subset": {
            "rows": int(len(detailed)),
            "share_of_total": float(len(detailed) / len(frame)),
            "opening_odds_coverage_within_subset": float(
                detailed[["odds_avg_home_open", "odds_avg_draw_open", "odds_avg_away_open"]]
                .notna().all(axis=1).mean()
            ),
        },
        "market_baseline": market,
        "outliers_iqr": outliers,
        "leakage": {
            "post_event_columns": sorted(POST_EVENT_LEAKAGE),
            "identifier_columns": sorted(IDENTIFIERS),
            "metadata_columns": sorted(METADATA),
            "closing_market_timing_risk": sorted(CLOSING_MARKET),
        },
    }


def _plot_target(frame: pd.DataFrame, figures_dir: Path) -> None:
    counts = frame[TARGET_COLUMN].value_counts().reindex(RESULT_ORDER, fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        [RESULT_LABELS[key] for key in RESULT_ORDER], counts.values,
        color=[RESULT_COLORS[key] for key in RESULT_ORDER], width=0.68,
    )
    ax.bar_label(bars, labels=[f"{value:,}\n({value / len(frame):.1%})" for value in counts], padding=5)
    ax.set(title="El target está moderadamente desbalanceado hacia la victoria local", ylabel="Partidos", xlabel="")
    ax.set_ylim(0, counts.max() * 1.2)
    sns.despine(ax=ax)
    _save(fig, figures_dir / "01_target_distribution.png")


def _plot_season_trend(frame: pd.DataFrame, figures_dir: Path) -> None:
    share = pd.crosstab(frame["season"], frame[TARGET_COLUMN], normalize="index").reindex(
        columns=RESULT_ORDER, fill_value=0
    )
    fig, ax = plt.subplots(figsize=(13, 6))
    for key in RESULT_ORDER:
        ax.plot(share.index, share[key], marker="o", markersize=3, linewidth=2, label=RESULT_LABELS[key], color=RESULT_COLORS[key])
    ax.set(title="La ventaja local persiste, pero varía por temporada", ylabel="Proporción de partidos", xlabel="Temporada")
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.tick_params(axis="x", rotation=70, labelsize=8)
    ax.legend(ncol=3, frameon=False, loc="upper center")
    sns.despine(ax=ax)
    _save(fig, figures_dir / "02_target_by_season.png")


def _plot_goals(frame: pd.DataFrame, figures_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.histplot(frame, x="total_goals", discrete=True, color="#2F75B5", ax=axes[0])
    axes[0].axvline(frame["total_goals"].mean(), color="#C44E52", linestyle="--", label=f"Media {frame['total_goals'].mean():.2f}")
    axes[0].set(title="Distribución de goles totales", xlabel="Goles por partido", ylabel="Partidos")
    axes[0].legend(frameon=False)
    sns.boxplot(
        data=frame, x="result_ft", y="total_goals", order=RESULT_ORDER,
        hue="result_ft", palette=RESULT_COLORS, legend=False, ax=axes[1], showfliers=True,
    )
    axes[1].set(title="Goles por resultado (descriptivo, no predictivo)", xlabel="Resultado", ylabel="Goles totales")
    axes[1].set_xticks(range(len(RESULT_ORDER)), [RESULT_LABELS[key] for key in RESULT_ORDER])
    sns.despine(fig=fig)
    _save(fig, figures_dir / "03_goals_distribution.png")


def _plot_home_advantage(frame: pd.DataFrame, figures_dir: Path) -> None:
    summary = frame.groupby("season", observed=True).agg(
        home_win_rate=("result_ft", lambda value: value.eq("H").mean()),
        avg_goal_diff=("goal_diff_home", "mean"),
    )
    fig, ax1 = plt.subplots(figsize=(13, 5.5))
    ax1.plot(summary.index, summary["home_win_rate"], color=RESULT_COLORS["H"], marker="o", label="% victorias locales")
    ax1.set(ylabel="Victorias locales", xlabel="Temporada", title="La ventaja de jugar en casa es estable pero no constante")
    ax1.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax2 = ax1.twinx()
    ax2.plot(summary.index, summary["avg_goal_diff"], color="#17365D", marker="s", alpha=0.75, label="Diferencia media de goles")
    ax2.axhline(0, color="#999999", linewidth=1)
    ax2.set_ylabel("Goles local − visitante")
    ax1.tick_params(axis="x", rotation=70, labelsize=8)
    lines = ax1.get_lines() + ax2.get_lines()[:1]
    ax1.legend(lines, [line.get_label() for line in lines], ncol=2, frameon=False, loc="upper center")
    sns.despine(ax=ax1, right=False)
    _save(fig, figures_dir / "04_home_advantage_trend.png")


def _team_table(frame: pd.DataFrame) -> pd.DataFrame:
    home = frame[["home_team", "home_points", "home_goals_ft", "away_goals_ft"]].rename(
        columns={"home_team": "team", "home_points": "points", "home_goals_ft": "goals_for", "away_goals_ft": "goals_against"}
    )
    away = frame[["away_team", "away_points", "away_goals_ft", "home_goals_ft"]].rename(
        columns={"away_team": "team", "away_points": "points", "away_goals_ft": "goals_for", "home_goals_ft": "goals_against"}
    )
    return pd.concat([home, away], ignore_index=True).groupby("team").agg(
        matches=("points", "size"), points=("points", "sum"), goals_for=("goals_for", "sum"), goals_against=("goals_against", "sum")
    ).assign(points_per_match=lambda value: value["points"] / value["matches"])


def _plot_team_performance(frame: pd.DataFrame, figures_dir: Path) -> None:
    all_teams = _team_table(frame)
    minimum_matches = 100 if all_teams["matches"].ge(100).any() else 1
    teams = all_teams.query("matches >= @minimum_matches").nlargest(15, "points_per_match").sort_values("points_per_match")
    fig, ax = plt.subplots(figsize=(9, 7))
    bars = ax.barh(teams.index, teams["points_per_match"], color="#2F75B5")
    ax.bar_label(bars, labels=[f"{value:.2f}" for value in teams["points_per_match"]], padding=4)
    ax.set(title=f"Rendimiento histórico: puntos por partido (mínimo {minimum_matches} partidos)", xlabel="Puntos por partido", ylabel="")
    ax.set_xlim(0, max(2.4, teams["points_per_match"].max() * 1.14))
    sns.despine(ax=ax)
    _save(fig, figures_dir / "05_team_performance.png")


def _plot_missingness(frame: pd.DataFrame, figures_dir: Path) -> None:
    missing = frame.isna().mean().sort_values(ascending=False)
    missing = missing[missing > 0].head(25).sort_values()
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = np.where(missing > 0.9, "#C44E52", "#D4A72C")
    bars = ax.barh(missing.index, missing.values, color=colors)
    ax.bar_label(bars, labels=[f"{value:.1%}" for value in missing], padding=3, fontsize=8)
    ax.set(title="La ausencia del bloque detallado es estructural, no aleatoria", xlabel="Valores ausentes", ylabel="")
    ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.set_xlim(0, 1.08)
    sns.despine(ax=ax)
    _save(fig, figures_dir / "06_missingness_profile.png")


def _plot_correlations(frame: pd.DataFrame, figures_dir: Path) -> None:
    detailed = frame.loc[frame["has_detailed_stats"].fillna(False)].copy()
    columns = [
        "home_goals_ft", "away_goals_ft", "shots_home", "shots_away", "shots_on_target_home",
        "shots_on_target_away", "fouls_home", "fouls_away", "corners_home", "corners_away",
        "yellow_cards_home", "yellow_cards_away", "odds_avg_home_open", "odds_avg_draw_open", "odds_avg_away_open",
    ]
    corr = detailed[columns].astype(float).corr().fillna(0.0)
    corr_values = corr.to_numpy(copy=True)
    np.fill_diagonal(corr_values, 1.0)
    corr = pd.DataFrame(corr_values, index=corr.index, columns=corr.columns)
    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, mask=mask, cmap="vlag", center=0, vmin=-1, vmax=1, square=True, linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.75})
    ax.set_title("Correlaciones en 2025-26 (incluye variables postpartido)")
    ax.tick_params(axis="x", rotation=65, labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    _save(fig, figures_dir / "07_detailed_correlation_heatmap.png")


def _market_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    columns = ["odds_avg_home_open", "odds_avg_draw_open", "odds_avg_away_open"]
    odds = frame.loc[frame["has_detailed_stats"].fillna(False)].dropna(subset=columns + [TARGET_COLUMN]).copy()
    raw_probs = 1 / odds[columns].to_numpy()
    probs = raw_probs / raw_probs.sum(axis=1, keepdims=True)
    picks = np.array(RESULT_ORDER)[np.argmax(probs, axis=1)]
    return odds, probs, picks


def _plot_detailed_relationships(frame: pd.DataFrame, figures_dir: Path) -> None:
    detailed = frame.loc[frame["has_detailed_stats"].fillna(False)].copy()
    detailed["shot_on_target_diff"] = detailed["shots_on_target_home"] - detailed["shots_on_target_away"]
    odds, probs, _ = _market_data(frame)
    probability = pd.DataFrame(probs, columns=RESULT_ORDER, index=odds.index)
    odds["market_prob_observed"] = [probability.loc[index, result] for index, result in odds[TARGET_COLUMN].items()]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.boxplot(data=detailed, x=TARGET_COLUMN, y="shot_on_target_diff", order=RESULT_ORDER, hue=TARGET_COLUMN, palette=RESULT_COLORS, legend=False, ax=axes[0])
    axes[0].axhline(0, color="#999999", linewidth=1)
    axes[0].set(title="Diferencia de tiros a puerta y resultado", xlabel="Resultado", ylabel="Tiros a puerta local − visitante")
    axes[0].set_xticks(range(len(RESULT_ORDER)), [RESULT_LABELS[key] for key in RESULT_ORDER])
    sns.boxplot(data=odds, x=TARGET_COLUMN, y="market_prob_observed", order=RESULT_ORDER, hue=TARGET_COLUMN, palette=RESULT_COLORS, legend=False, ax=axes[1])
    axes[1].set(title="Probabilidad de mercado de la clase observada", xlabel="Resultado", ylabel="Probabilidad implícita normalizada")
    axes[1].set_xticks(range(len(RESULT_ORDER)), [RESULT_LABELS[key] for key in RESULT_ORDER])
    axes[1].yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    sns.despine(fig=fig)
    _save(fig, figures_dir / "08_relationships_with_target.png")


def _plot_market_confusion(frame: pd.DataFrame, figures_dir: Path) -> None:
    odds, _, picks = _market_data(frame)
    matrix = confusion_matrix(odds[TARGET_COLUMN], picks, labels=RESULT_ORDER, normalize="true")
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(matrix, annot=True, fmt=".1%", cmap="Blues", vmin=0, vmax=1, cbar=False, ax=ax)
    ax.set(
        title="Baseline de mercado: clase favorita frente al resultado real",
        xlabel="Favorito según cuotas de apertura",
        ylabel="Resultado real",
    )
    labels = [RESULT_LABELS[key] for key in RESULT_ORDER]
    ax.set_xticklabels(labels, rotation=20)
    ax.set_yticklabels(labels, rotation=0)
    _save(fig, figures_dir / "09_market_baseline_confusion.png")


def _plot_majority_confusion(frame: pd.DataFrame, figures_dir: Path) -> None:
    majority_class = frame[TARGET_COLUMN].value_counts().idxmax()
    predictions = np.full(len(frame), majority_class)
    matrix = confusion_matrix(
        frame[TARGET_COLUMN],
        predictions,
        labels=RESULT_ORDER,
        normalize="true",
    )
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(
        matrix,
        annot=True,
        fmt=".1%",
        cmap="Blues",
        vmin=0,
        vmax=1,
        cbar=False,
        ax=ax,
    )
    ax.set(
        title="Baseline descriptivo: predecir siempre la clase mayoritaria",
        xlabel=f"Predicción de la regla fija ({RESULT_LABELS[majority_class]})",
        ylabel="Resultado real",
    )
    labels = [RESULT_LABELS[key] for key in RESULT_ORDER]
    ax.set_xticklabels(labels, rotation=20)
    ax.set_yticklabels(labels, rotation=0)
    _save(fig, figures_dir / "10_majority_baseline_confusion.png")


def _plot_outlier_profile(frame: pd.DataFrame, figures_dir: Path) -> None:
    columns = [
        "home_goals_ft",
        "away_goals_ft",
        "total_goals",
        "shots_home",
        "shots_away",
        "shots_on_target_home",
        "shots_on_target_away",
        "fouls_home",
        "fouls_away",
        "yellow_cards_home",
        "yellow_cards_away",
        "red_cards_home",
        "red_cards_away",
    ]
    profile = pd.DataFrame(
        [
            {
                "column": column,
                **_iqr_outliers(frame[column]),
            }
            for column in columns
        ]
    ).sort_values("pct")
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = [
        "#2F75B5" if "goals" in column else "#D4A72C"
        for column in profile["column"]
    ]
    bars = ax.barh(profile["column"], profile["pct"], color=colors)
    ax.bar_label(
        bars,
        labels=[
            f"{percentage:.1%} ({count})"
            for percentage, count in zip(profile["pct"], profile["count"], strict=True)
        ],
        padding=4,
        fontsize=8,
    )
    ax.set(
        title="Valores extremos detectados por la regla IQR (1,5 × IQR)",
        xlabel="Porcentaje sobre valores disponibles",
        ylabel="",
    )
    ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.set_xlim(0, max(0.05, float(profile["pct"].max()) * 1.35))
    sns.despine(ax=ax)
    _save(fig, figures_dir / "11_outlier_profile.png")


def generate_figures(frame: pd.DataFrame, figures_dir: str | Path) -> list[Path]:
    _configure_style()
    output = Path(figures_dir)
    plotters = [
        _plot_target, _plot_season_trend, _plot_goals, _plot_home_advantage,
        _plot_team_performance, _plot_missingness, _plot_correlations,
        _plot_detailed_relationships, _plot_market_confusion,
        _plot_majority_confusion, _plot_outlier_profile,
    ]
    for plotter in plotters:
        plotter(frame, output)
    return sorted(output.glob("*.png"))


def _pct(value: float) -> str:
    return f"{value:.1%}"


def render_markdown_report(metrics: dict[str, Any], report_path: str | Path) -> Path:
    quality = metrics["quality"]
    target = metrics["target"]
    goals = metrics["goals"]
    detailed = metrics["detailed_subset"]
    market = metrics["market_baseline"]
    associations = metrics["associations"]
    output = Path(report_path)
    preprocessing_file = output.parent / "metrics" / "preprocessing_summary.json"
    preprocessing = (
        json.loads(preprocessing_file.read_text(encoding="utf-8"))
        if preprocessing_file.exists()
        else {}
    )
    join = preprocessing.get("join", {})
    source_cleaning = preprocessing.get("source_cleaning", {})
    historical_cleaning = source_cleaning.get(HISTORICAL_FILENAME, {})
    detailed_cleaning = source_cleaning.get(DETAILED_FILENAME, {})
    column_summary = preprocessing.get("column_policy_summary", {})
    processed_output = preprocessing.get("output", {})
    outlier_rows = "\n".join(
        f"| `{column}` | {values['lower'] if values['lower'] is not None else 'N/A':} | "
        f"{values['upper'] if values['upper'] is not None else 'N/A':} | "
        f"{values['count']} | {_pct(values['pct'])} |"
        for column, values in sorted(
            metrics["outliers_iqr"].items(),
            key=lambda item: item[1]["pct"],
            reverse=True,
        )
    )
    source_rows = "\n".join(
        (
            f"| `{filename}` | {metadata['source_name']} | "
            f"{metadata['source_page_url']} | {metadata['acquisition']} | "
            f"{metadata['license']} |"
        )
        for filename, metadata in SOURCE_PROVENANCE.items()
    )
    majority_matrix = target["majority_confusion_matrix"]
    market_matrix = market.get("confusion_matrix", [[0, 0, 0] for _ in RESULT_ORDER])
    report = f"""# EDA completo — Partidos de LaLiga

## Estado del análisis

Este informe cubre el preprocesamiento T-1.4 y el EDA T-1.3 del dataset canónico provisional de LaLiga. El target propuesto es `result_ft`: **H** (victoria local), **D** (empate) y **A** (victoria visitante). El flujo es reproducible, pero **no cierra `Data Ready`**: la licencia, el protocolo de evaluación y la aprobación cruzada siguen pendientes.

## Resumen ejecutivo

- Se analizaron **{quality['rows']:,} partidos**, **{quality['columns']} variables** y **{quality['season_count']} temporadas**, entre {quality['date_min']} y {quality['date_max']}.
- La unión prioriza la fuente detallada en **{join.get('overlap_rows', quality['source_coverage'].get('both_sources', 0))} partidos solapados** y termina con **{quality['duplicate_match_ids']} IDs duplicados**, **{quality['missing_target']} targets ausentes** y **{quality['full_time_result_inconsistencies']} incoherencias.
- El target está moderadamente desbalanceado: H={target['counts']['H']:,} ({_pct(target['shares']['H'])}), D={target['counts']['D']:,} ({_pct(target['shares']['D'])}) y A={target['counts']['A']:,} ({_pct(target['shares']['A'])}). La baseline mayoritaria es {_pct(target['majority_baseline_accuracy'])}.
- La media es **{goals['mean_total']:.2f} goles/partido**; {_pct(goals['pct_over_2_5'])} supera 2,5 goles y {_pct(goals['pct_both_teams_scored'])} registra goles de ambos equipos.
- Solo **{detailed['rows']} partidos** ({_pct(detailed['share_of_total'])}) contienen tiros, faltas, tarjetas y cuotas. Esta ausencia es estructural por temporada y no debe imputarse sobre el histórico.
- En las filas con cuotas completas, escoger el favorito de apertura acierta {_pct(market.get('favorite_accuracy', 0.0))}; es una referencia descriptiva, no un modelo entrenado.

![Distribución del target](figures/01_target_distribution.png)

## 1. Fuentes y trazabilidad

Los CSV originales se conservan sin modificación en `data/raw/` y sus SHA-256 están en `reports/metrics/dataset_manifest.json`.

| Archivo raw | Fuente identificada | URL | Obtención | Licencia/uso |
|---|---|---|---|---|
{source_rows}

La procedencia está documentada; la aprobación de uso/licencia sigue abierta. El CSV detallado local es una instantánea anterior a la versión actualmente servida por Football-Data: coincide en temporada, 380 filas y 131 columnas, pero no byte a byte porque las cuotas se actualizan.

## 2. Pipeline de combinación y política de columnas

- Histórico: **{historical_cleaning.get('input', {}).get('rows', 11664):,} filas y {historical_cleaning.get('input', {}).get('columns', 10)} columnas**. Se conservan fecha, equipos, goles y resultados; `Season` solo valida y luego se deriva desde la fecha.
- Detallado: **{detailed_cleaning.get('input', {}).get('rows', 380):,} filas y {detailed_cleaning.get('input', {}).get('columns', 131)} columnas**. Se conservan **{column_summary.get('detailed_columns_kept', 39)}** y se eliminan **{column_summary.get('detailed_columns_dropped', 92)}** cuotas específicas/máximas redundantes y con cobertura irregular.
- La política completa, columna por columna, está en `reports/metrics/source_column_policy.csv`.
- Clave de solapamiento: **fecha normalizada + equipo local recortado + equipo visitante recortado**.
- Estrategia: unión vertical, descartando del histórico la clave repetida y conservando la fila detallada. Se usa porque ambas fuentes describen partidos, no entidades diferentes, y la fila detallada contiene el bloque mínimo más estadísticas y promedios de mercado.

## 3. Limpieza y calidad final

Reglas deterministas:

1. Recortar texto y normalizar resultados a H/D/A.
2. Convertir fechas y goles; retirar filas con clave, marcador o target crítico inválido.
3. Eliminar duplicados exactos y duplicados de clave dentro de cada fuente.
4. Resolver los {join.get('overlap_rows', 100)} solapamientos priorizando la fila detallada.
5. Conservar los dos nulos de descanso porque son opcionales, posteriores al evento y no se usarán como feature prepartido.
6. No imputar el bloque detallado ausente del histórico: el nulo es estructural.

| Control de limpieza | Histórico | Detallado |
|---|---:|---:|
| Duplicados exactos eliminados | {historical_cleaning.get('exact_duplicate_rows_removed', 0)} | {detailed_cleaning.get('exact_duplicate_rows_removed', 0)} |
| Filas críticas inválidas eliminadas | {historical_cleaning.get('invalid_rows_removed', 0)} | {detailed_cleaning.get('invalid_rows_removed', 0)} |
| Claves duplicadas internas eliminadas | {historical_cleaning.get('duplicate_match_keys_removed', 0)} | {detailed_cleaning.get('duplicate_match_keys_removed', 0)} |
| Filas tras limpieza de fuente | {historical_cleaning.get('rows_after_source_cleaning', 11664):,} | {detailed_cleaning.get('rows_after_source_cleaning', 380):,} |

| Control | Resultado |
|---|---:|
| Filas finales | {quality['rows']:,} |
| Columnas finales | {quality['columns']} |
| Filas duplicadas completas | {quality['duplicate_rows']} |
| IDs de partido duplicados | {quality['duplicate_match_ids']} |
| Target ausente | {quality['missing_target']} |
| Filas con descanso incompleto | {quality['missing_half_time_rows']} |
| Resultados incoherentes con goles | {quality['full_time_result_inconsistencies']} |
| Equipos local y visitante iguales | {quality['same_team_rows']} |
| Goles negativos | {quality['negative_goal_rows']} |

Salida reproducible: `{processed_output.get('path', 'data/processed/laliga_matches_clean.csv')}`; SHA-256 `{processed_output.get('sha256', 'generado por el pipeline')}`.

![Perfil de valores ausentes](figures/06_missingness_profile.png)

## 4. Distribución y balance del target

La clase H domina, seguida de A y D. El ratio entre clase mayoritaria y minoritaria es **{target['max_to_min_ratio']:.2f}**: existe desbalance moderado, no extremo. Accuracy por sí sola no será suficiente; el protocolo de evaluación debería considerar balanced accuracy y macro-F1, sujeto a T-0.4.

La mezcla de resultados cambia por temporada. La asociación temporada-target es baja (V de Cramér={associations['season_vs_target_cramers_v']:.3f}), pero el orden temporal sigue siendo crítico para evitar evaluar con información futura.

![Target por temporada](figures/02_target_by_season.png)

## 5. Distribuciones, evolución temporal y outliers

Los goles son variables discretas con cola derecha. Los valores extremos identificados por IQR representan goleadas reales plausibles y no errores automáticos; deben validarse, no truncarse por defecto.

La tasa de victoria local y la diferencia media de goles fluctúan a lo largo de las temporadas. Esto indica posible cambio temporal de distribución y recomienda particiones cronológicas y features de forma calculadas únicamente con partidos anteriores.

![Distribución de goles](figures/03_goals_distribution.png)

![Ventaja local](figures/04_home_advantage_trend.png)

| Variable | Límite inferior IQR | Límite superior IQR | Outliers | Porcentaje |
|---|---:|---:|---:|---:|
{outlier_rows}

![Perfil de outliers](figures/11_outlier_profile.png)

Conclusión: los extremos de goles, tiros y tarjetas son observaciones deportivas plausibles. No se eliminan automáticamente; la limpieza retira errores lógicos, no partidos raros pero válidos.

## 6. Equipos y cardinalidad

Hay {metrics['cardinality']['home_teams']} equipos distintos en el rol local. `match_id` es único al {_pct(metrics['cardinality']['match_id_unique_pct'])} y debe tratarse exclusivamente como identificador. Los nombres de equipo sí pueden aportar señal, pero requieren una estrategia capaz de manejar ascensos, descensos y categorías no vistas. Una alternativa más robusta es derivar forma, Elo o promedios móviles usando solo el pasado.

La asociación bruta del equipo local con el target es V={associations['home_team_vs_target_cramers_v']:.3f} y la del visitante V={associations['away_team_vs_target_cramers_v']:.3f}; no implican causalidad.

![Rendimiento histórico de equipos](figures/05_team_performance.png)

## 7. Relaciones entre variables y target

En 2025-26, tiros y tiros a puerta se relacionan con goles y resultado, como cabe esperar. Esa relación es **descriptiva y posterior al evento**: usarla para predecir el mismo partido produciría leakage crítico.

Las cuotas de apertura sí existen antes del partido y muestran señal predictiva. Su uso es viable si la aplicación garantiza la misma fuente y momento de captura. Las cuotas de cierre tienen riesgo temporal porque pueden no estar disponibles cuando se solicita la predicción.

![Correlaciones detalladas](figures/07_detailed_correlation_heatmap.png)

![Relaciones con el target](figures/08_relationships_with_target.png)

## 8. Matrices de confusión descriptivas

No se entrena ningún candidato porque `.specify` mantiene bloqueados splits y modelos. Se incluyen dos reglas de referencia:

1. **Clase mayoritaria** sobre todo el dataset: siempre predice H y alcanza {_pct(target['majority_baseline_accuracy'])}. Evidencia que accuracy puede ocultar un fallo total en D y A.

| Real \\ Predicha | H | D | A |
|---|---:|---:|---:|
| H | {majority_matrix[0][0]} | {majority_matrix[0][1]} | {majority_matrix[0][2]} |
| D | {majority_matrix[1][0]} | {majority_matrix[1][1]} | {majority_matrix[1][2]} |
| A | {majority_matrix[2][0]} | {majority_matrix[2][1]} | {majority_matrix[2][2]} |

![Baseline mayoritaria](figures/10_majority_baseline_confusion.png)

2. **Favorito de cuotas de apertura** sobre {market.get('rows_with_complete_opening_odds', 0)} partidos 2025-26: elige la mayor probabilidad implícita y acierta {_pct(market.get('favorite_accuracy', 0.0))}. No es un modelo entrenado ni una evaluación final.

| Real \\ Favorito | H | D | A |
|---|---:|---:|---:|
| H | {market_matrix[0][0]} | {market_matrix[0][1]} | {market_matrix[0][2]} |
| D | {market_matrix[1][0]} | {market_matrix[1][1]} | {market_matrix[1][2]} |
| A | {market_matrix[2][0]} | {market_matrix[2][1]} | {market_matrix[2][2]} |

![Baseline de mercado](figures/09_market_baseline_confusion.png)

## 9. Riesgo de leakage

Se deben excluir del entrenamiento prepartido del mismo encuentro:

- Marcador final y al descanso, resultado al descanso y todas sus derivadas.
- Tiros, tiros a puerta, faltas, córners y tarjetas.
- `total_goals`, diferencias, clean sheets, puntos, over 2,5 y ambos marcan.
- Metadatos de fuente/cobertura, que revelan la temporada y el mecanismo de captura.
- `match_id`, que no tiene valor predictivo generalizable.

La fecha, temporada y equipos son inputs disponibles, pero no deben transformarse usando datos futuros. Las cuotas de cierre quedan condicionadas a definir la ventana de inferencia.

## 10. Viabilidad para una aplicación

Inputs directamente solicitables: equipo local, visitante, fecha/hora y, si existe una integración externa aprobada, cuotas prepartido. Para ofrecer valor sin depender de casas de apuestas, el pipeline debería generar forma reciente, fuerza ofensiva/defensiva y rating histórico a partir de partidos anteriores.

No son inputs aceptables: goles, tiros, tarjetas o cualquier estadística ocurrida durante/después del partido que se intenta predecir.

## 11. Reglas comunes propuestas

1. Mantener ambos CSV raw inmutables y verificar sus SHA-256.
2. Deduplicar por fecha + local + visitante y priorizar la fila detallada.
3. Normalizar fechas, temporada y tipos con el loader común.
4. No imputar el bloque detallado sobre 1995-96–2024-25: es ausencia estructural.
5. Excluir leakage y metadatos antes de modelar.
6. Construir features históricas con `shift`/ventanas cerradas al pasado.
7. Usar un split temporal; no congelarlo hasta aprobar T-0.4.
8. Proteger el test final y ajustar transformaciones solo con train.

## 12. Limitaciones y decisiones pendientes

- Las URL y la trazabilidad ya están documentadas; falta que el equipo apruebe las condiciones de uso/licencia.
- El target, el usuario y la ventana de predicción son propuestas que requieren aprobación del equipo.
- El bloque detallado representa una única temporada y no permite asumir estabilidad histórica.
- Las primeras temporadas contienen más partidos por cambios de tamaño de la liga; comparar conteos brutos sin normalizar puede inducir a error.
- Las matrices mostradas son reglas descriptivas; no se han creado splits ni entrenado candidatos.

## Reproducibilidad

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements-eda.txt
.\\.venv\\Scripts\\python.exe scripts\\run_laliga_preprocessing.py
.\\.venv\\Scripts\\python.exe scripts\\run_laliga_eda.py
.\\.venv\\Scripts\\python.exe scripts\\create_preprocessing_notebook.py
.\\.venv\\Scripts\\python.exe scripts\\create_eda_notebook.py
.\\.venv\\Scripts\\python.exe scripts\\execute_eda_notebook.py
.\\.venv\\Scripts\\python.exe -m pytest
```

Los artefactos métricos se guardan en `reports/metrics/`, las figuras en `reports/figures/` y el dataset limpio versionable en `data/processed/laliga_matches_clean.csv`.
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return output


def run_full_eda(frame: pd.DataFrame, reports_dir: str | Path) -> dict[str, Any]:
    """Genera métricas, contrato, figuras e informe Markdown."""

    reports = Path(reports_dir)
    figures = reports / "figures"
    metrics_dir = reports / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics = calculate_eda_metrics(frame)
    (metrics_dir / "eda_summary.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    missing = pd.DataFrame(
        {
            "column": frame.columns,
            "missing_count": frame.isna().sum().to_numpy(),
            "missing_pct": frame.isna().mean().to_numpy(),
            "non_null_count": frame.notna().sum().to_numpy(),
        }
    ).sort_values("missing_pct", ascending=False)
    missing.to_csv(metrics_dir / "missingness.csv", index=False, encoding="utf-8")
    build_data_dictionary(frame).to_csv(
        metrics_dir / "data_dictionary.csv", index=False, encoding="utf-8"
    )
    pd.DataFrame(metrics["temporal"]["season_summary"]).to_csv(
        metrics_dir / "season_summary.csv", index=False, encoding="utf-8"
    )
    generate_figures(frame, figures)
    render_markdown_report(metrics, reports / "laliga_eda.md")
    return metrics
