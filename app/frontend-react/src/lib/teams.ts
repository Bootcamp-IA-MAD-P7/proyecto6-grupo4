// Catálogo de equipos: se pide a GET /api/v1/teams (deriva del calendario del
// backend). Este arreglo es solo el fallback mientras esa llamada resuelve,
// para que los selects no aparezcan vacíos en el primer render.
import type { Team } from "./types";

export const FALLBACK_TEAMS: Team[] = [
  { label: "Real Madrid", value: "Real Madrid" },
  { label: "FC Barcelona", value: "Barcelona" },
  { label: "Atlético de Madrid", value: "Ath Madrid" },
  { label: "Sevilla FC", value: "Sevilla" },
  { label: "Real Betis", value: "Betis" },
  { label: "Real Sociedad", value: "Sociedad" },
  { label: "Athletic Club", value: "Ath Bilbao" },
  { label: "Villarreal CF", value: "Villarreal" },
  { label: "Valencia CF", value: "Valencia" },
  { label: "RC Celta", value: "Celta" },
  { label: "Getafe CF", value: "Getafe" },
  { label: "CA Osasuna", value: "Osasuna" },
  { label: "Rayo Vallecano", value: "Vallecano" },
  { label: "Deportivo Alavés", value: "Alaves" },
  { label: "RCD Espanyol", value: "Espanol" },
  { label: "Elche CF", value: "Elche" },
  { label: "Levante UD", value: "Levante" },
  { label: "RC Deportivo", value: "Deportivo" },
  { label: "Málaga CF", value: "Malaga" },
  { label: "Racing de Santander", value: "Racing Santander" },
];
