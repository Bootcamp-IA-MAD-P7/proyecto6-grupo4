export interface Team {
  value: string;
  label: string;
}

export interface Fixture {
  date: string;
  time: string;
  home_team: string;
  home_label: string;
  away_team: string;
  away_label: string;
  venue: string;
  city: string;
  has_history: boolean;
}

export type Outcome = "H" | "D" | "A";

export interface Probabilities {
  H: number;
  D: number;
  A: number;
}

export interface PredictionResult {
  request_id: string;
  prediction: Outcome;
  probabilities: Probabilities;
  model_version: string;
  data_version: string;
  latency_ms: number;
  message: string;
}

export interface HistoryItem {
  request_id: string;
  home_team: string;
  away_team: string;
  match_date: string;
  prediction: Outcome;
  probabilities: Probabilities;
  model_version: string;
  data_version: string;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface ApiError {
  status: "error";
  error: string;
  message: string;
  details: { field: string | null; reason: string }[];
}
