// Datos generados a partir del dataset real del proyecto (data/processed/laliga_matches_clean.csv)
// y de un fixture ilustrativo para la temporada 2026/27 (aun no jugada).

const LALIGA_TEAMS = [
  "Alaves",
  "Ath Bilbao",
  "Ath Madrid",
  "Barcelona",
  "Betis",
  "Celta",
  "Elche",
  "Espanol",
  "Getafe",
  "Girona",
  "Levante",
  "Mallorca",
  "Osasuna",
  "Oviedo",
  "Real Madrid",
  "Sevilla",
  "Sociedad",
  "Valencia",
  "Vallecano",
  "Villarreal"
];

const FIXTURES_2026_27 = [
  {
    "jornada": 1,
    "date": "2026-08-15",
    "home": "Valencia",
    "away": "Levante"
  },
  {
    "jornada": 1,
    "date": "2026-08-16",
    "home": "Betis",
    "away": "Sevilla"
  },
  {
    "jornada": 1,
    "date": "2026-08-17",
    "home": "Mallorca",
    "away": "Osasuna"
  },
  {
    "jornada": 1,
    "date": "2026-08-15",
    "home": "Ath Bilbao",
    "away": "Vallecano"
  },
  {
    "jornada": 1,
    "date": "2026-08-16",
    "home": "Espanol",
    "away": "Ath Madrid"
  },
  {
    "jornada": 1,
    "date": "2026-08-17",
    "home": "Oviedo",
    "away": "Elche"
  },
  {
    "jornada": 1,
    "date": "2026-08-15",
    "home": "Villarreal",
    "away": "Getafe"
  },
  {
    "jornada": 1,
    "date": "2026-08-16",
    "home": "Sociedad",
    "away": "Barcelona"
  },
  {
    "jornada": 1,
    "date": "2026-08-17",
    "home": "Real Madrid",
    "away": "Celta"
  },
  {
    "jornada": 1,
    "date": "2026-08-15",
    "home": "Girona",
    "away": "Alaves"
  },
  {
    "jornada": 2,
    "date": "2026-08-22",
    "home": "Betis",
    "away": "Valencia"
  },
  {
    "jornada": 2,
    "date": "2026-08-23",
    "home": "Levante",
    "away": "Osasuna"
  },
  {
    "jornada": 2,
    "date": "2026-08-24",
    "home": "Ath Bilbao",
    "away": "Sevilla"
  },
  {
    "jornada": 2,
    "date": "2026-08-22",
    "home": "Mallorca",
    "away": "Ath Madrid"
  },
  {
    "jornada": 2,
    "date": "2026-08-23",
    "home": "Oviedo",
    "away": "Vallecano"
  },
  {
    "jornada": 2,
    "date": "2026-08-24",
    "home": "Espanol",
    "away": "Getafe"
  },
  {
    "jornada": 2,
    "date": "2026-08-22",
    "home": "Sociedad",
    "away": "Elche"
  },
  {
    "jornada": 2,
    "date": "2026-08-23",
    "home": "Villarreal",
    "away": "Celta"
  },
  {
    "jornada": 2,
    "date": "2026-08-24",
    "home": "Girona",
    "away": "Barcelona"
  },
  {
    "jornada": 2,
    "date": "2026-08-22",
    "home": "Real Madrid",
    "away": "Alaves"
  },
  {
    "jornada": 3,
    "date": "2026-08-29",
    "home": "Valencia",
    "away": "Osasuna"
  },
  {
    "jornada": 3,
    "date": "2026-08-30",
    "home": "Ath Bilbao",
    "away": "Betis"
  },
  {
    "jornada": 3,
    "date": "2026-08-31",
    "home": "Levante",
    "away": "Ath Madrid"
  },
  {
    "jornada": 3,
    "date": "2026-08-29",
    "home": "Oviedo",
    "away": "Sevilla"
  },
  {
    "jornada": 3,
    "date": "2026-08-30",
    "home": "Mallorca",
    "away": "Getafe"
  },
  {
    "jornada": 3,
    "date": "2026-08-31",
    "home": "Sociedad",
    "away": "Vallecano"
  },
  {
    "jornada": 3,
    "date": "2026-08-29",
    "home": "Espanol",
    "away": "Celta"
  },
  {
    "jornada": 3,
    "date": "2026-08-30",
    "home": "Girona",
    "away": "Elche"
  },
  {
    "jornada": 3,
    "date": "2026-08-31",
    "home": "Villarreal",
    "away": "Alaves"
  },
  {
    "jornada": 3,
    "date": "2026-08-29",
    "home": "Real Madrid",
    "away": "Barcelona"
  }
];

const HISTORICAL_RESULTS = {
  "Alaves": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Alaves",
      "away": "Vallecano",
      "home_goals": 1,
      "away_goals": 2
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Oviedo",
      "away": "Alaves",
      "home_goals": 0,
      "away_goals": 1
    },
    {
      "date": "2026-05-13",
      "season": "2025-26",
      "home": "Alaves",
      "away": "Barcelona",
      "home_goals": 1,
      "away_goals": 0
    },
    {
      "date": "2026-05-09",
      "season": "2025-26",
      "home": "Elche",
      "away": "Alaves",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-02",
      "season": "2025-26",
      "home": "Alaves",
      "away": "Ath Bilbao",
      "home_goals": 2,
      "away_goals": 4
    }
  ],
  "Ath Bilbao": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Real Madrid",
      "away": "Ath Bilbao",
      "home_goals": 4,
      "away_goals": 2
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Ath Bilbao",
      "away": "Celta",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-13",
      "season": "2025-26",
      "home": "Espanol",
      "away": "Ath Bilbao",
      "home_goals": 2,
      "away_goals": 0
    },
    {
      "date": "2026-05-10",
      "season": "2025-26",
      "home": "Ath Bilbao",
      "away": "Valencia",
      "home_goals": 0,
      "away_goals": 1
    },
    {
      "date": "2026-05-02",
      "season": "2025-26",
      "home": "Alaves",
      "away": "Ath Bilbao",
      "home_goals": 2,
      "away_goals": 4
    }
  ],
  "Ath Madrid": [
    {
      "date": "2026-05-24",
      "season": "2025-26",
      "home": "Villarreal",
      "away": "Ath Madrid",
      "home_goals": 5,
      "away_goals": 1
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Ath Madrid",
      "away": "Girona",
      "home_goals": 1,
      "away_goals": 0
    },
    {
      "date": "2026-05-12",
      "season": "2025-26",
      "home": "Osasuna",
      "away": "Ath Madrid",
      "home_goals": 1,
      "away_goals": 2
    },
    {
      "date": "2026-05-09",
      "season": "2025-26",
      "home": "Ath Madrid",
      "away": "Celta",
      "home_goals": 0,
      "away_goals": 1
    },
    {
      "date": "2026-05-02",
      "season": "2025-26",
      "home": "Valencia",
      "away": "Ath Madrid",
      "home_goals": 0,
      "away_goals": 2
    }
  ],
  "Barcelona": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Valencia",
      "away": "Barcelona",
      "home_goals": 3,
      "away_goals": 1
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Barcelona",
      "away": "Betis",
      "home_goals": 3,
      "away_goals": 1
    },
    {
      "date": "2026-05-13",
      "season": "2025-26",
      "home": "Alaves",
      "away": "Barcelona",
      "home_goals": 1,
      "away_goals": 0
    },
    {
      "date": "2026-05-10",
      "season": "2025-26",
      "home": "Barcelona",
      "away": "Real Madrid",
      "home_goals": 2,
      "away_goals": 0
    },
    {
      "date": "2026-05-02",
      "season": "2025-26",
      "home": "Osasuna",
      "away": "Barcelona",
      "home_goals": 1,
      "away_goals": 2
    }
  ],
  "Betis": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Betis",
      "away": "Levante",
      "home_goals": 2,
      "away_goals": 1
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Barcelona",
      "away": "Betis",
      "home_goals": 3,
      "away_goals": 1
    },
    {
      "date": "2026-05-12",
      "season": "2025-26",
      "home": "Betis",
      "away": "Elche",
      "home_goals": 2,
      "away_goals": 1
    },
    {
      "date": "2026-05-09",
      "season": "2025-26",
      "home": "Sociedad",
      "away": "Betis",
      "home_goals": 2,
      "away_goals": 2
    },
    {
      "date": "2026-05-03",
      "season": "2025-26",
      "home": "Betis",
      "away": "Oviedo",
      "home_goals": 3,
      "away_goals": 0
    }
  ],
  "Celta": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Celta",
      "away": "Sevilla",
      "home_goals": 1,
      "away_goals": 0
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Ath Bilbao",
      "away": "Celta",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-12",
      "season": "2025-26",
      "home": "Celta",
      "away": "Levante",
      "home_goals": 2,
      "away_goals": 3
    },
    {
      "date": "2026-05-09",
      "season": "2025-26",
      "home": "Ath Madrid",
      "away": "Celta",
      "home_goals": 0,
      "away_goals": 1
    },
    {
      "date": "2026-05-03",
      "season": "2025-26",
      "home": "Celta",
      "away": "Elche",
      "home_goals": 3,
      "away_goals": 1
    }
  ],
  "Elche": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Girona",
      "away": "Elche",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Elche",
      "away": "Getafe",
      "home_goals": 1,
      "away_goals": 0
    },
    {
      "date": "2026-05-12",
      "season": "2025-26",
      "home": "Betis",
      "away": "Elche",
      "home_goals": 2,
      "away_goals": 1
    },
    {
      "date": "2026-05-09",
      "season": "2025-26",
      "home": "Elche",
      "away": "Alaves",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-03",
      "season": "2025-26",
      "home": "Celta",
      "away": "Elche",
      "home_goals": 3,
      "away_goals": 1
    }
  ],
  "Espanol": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Espanol",
      "away": "Sociedad",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Osasuna",
      "away": "Espanol",
      "home_goals": 1,
      "away_goals": 2
    },
    {
      "date": "2026-05-13",
      "season": "2025-26",
      "home": "Espanol",
      "away": "Ath Bilbao",
      "home_goals": 2,
      "away_goals": 0
    },
    {
      "date": "2026-05-09",
      "season": "2025-26",
      "home": "Sevilla",
      "away": "Espanol",
      "home_goals": 2,
      "away_goals": 1
    },
    {
      "date": "2026-05-03",
      "season": "2025-26",
      "home": "Espanol",
      "away": "Real Madrid",
      "home_goals": 0,
      "away_goals": 2
    }
  ],
  "Getafe": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Getafe",
      "away": "Osasuna",
      "home_goals": 1,
      "away_goals": 0
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Elche",
      "away": "Getafe",
      "home_goals": 1,
      "away_goals": 0
    },
    {
      "date": "2026-05-13",
      "season": "2025-26",
      "home": "Getafe",
      "away": "Mallorca",
      "home_goals": 3,
      "away_goals": 1
    },
    {
      "date": "2026-05-10",
      "season": "2025-26",
      "home": "Oviedo",
      "away": "Getafe",
      "home_goals": 0,
      "away_goals": 0
    },
    {
      "date": "2026-05-03",
      "season": "2025-26",
      "home": "Getafe",
      "away": "Vallecano",
      "home_goals": 0,
      "away_goals": 2
    }
  ],
  "Girona": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Girona",
      "away": "Elche",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Ath Madrid",
      "away": "Girona",
      "home_goals": 1,
      "away_goals": 0
    },
    {
      "date": "2026-05-14",
      "season": "2025-26",
      "home": "Girona",
      "away": "Sociedad",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-11",
      "season": "2025-26",
      "home": "Vallecano",
      "away": "Girona",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-01",
      "season": "2025-26",
      "home": "Girona",
      "away": "Mallorca",
      "home_goals": 0,
      "away_goals": 1
    }
  ],
  "Levante": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Betis",
      "away": "Levante",
      "home_goals": 2,
      "away_goals": 1
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Levante",
      "away": "Mallorca",
      "home_goals": 2,
      "away_goals": 0
    },
    {
      "date": "2026-05-12",
      "season": "2025-26",
      "home": "Celta",
      "away": "Levante",
      "home_goals": 2,
      "away_goals": 3
    },
    {
      "date": "2026-05-08",
      "season": "2025-26",
      "home": "Levante",
      "away": "Osasuna",
      "home_goals": 3,
      "away_goals": 2
    },
    {
      "date": "2026-05-02",
      "season": "2025-26",
      "home": "Villarreal",
      "away": "Levante",
      "home_goals": 5,
      "away_goals": 1
    }
  ],
  "Mallorca": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Mallorca",
      "away": "Oviedo",
      "home_goals": 3,
      "away_goals": 0
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Levante",
      "away": "Mallorca",
      "home_goals": 2,
      "away_goals": 0
    },
    {
      "date": "2026-05-13",
      "season": "2025-26",
      "home": "Getafe",
      "away": "Mallorca",
      "home_goals": 3,
      "away_goals": 1
    },
    {
      "date": "2026-05-10",
      "season": "2025-26",
      "home": "Mallorca",
      "away": "Villarreal",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-01",
      "season": "2025-26",
      "home": "Girona",
      "away": "Mallorca",
      "home_goals": 0,
      "away_goals": 1
    }
  ],
  "Osasuna": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Getafe",
      "away": "Osasuna",
      "home_goals": 1,
      "away_goals": 0
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Osasuna",
      "away": "Espanol",
      "home_goals": 1,
      "away_goals": 2
    },
    {
      "date": "2026-05-12",
      "season": "2025-26",
      "home": "Osasuna",
      "away": "Ath Madrid",
      "home_goals": 1,
      "away_goals": 2
    },
    {
      "date": "2026-05-08",
      "season": "2025-26",
      "home": "Levante",
      "away": "Osasuna",
      "home_goals": 3,
      "away_goals": 2
    },
    {
      "date": "2026-05-02",
      "season": "2025-26",
      "home": "Osasuna",
      "away": "Barcelona",
      "home_goals": 1,
      "away_goals": 2
    }
  ],
  "Oviedo": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Mallorca",
      "away": "Oviedo",
      "home_goals": 3,
      "away_goals": 0
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Oviedo",
      "away": "Alaves",
      "home_goals": 0,
      "away_goals": 1
    },
    {
      "date": "2026-05-14",
      "season": "2025-26",
      "home": "Real Madrid",
      "away": "Oviedo",
      "home_goals": 2,
      "away_goals": 0
    },
    {
      "date": "2026-05-10",
      "season": "2025-26",
      "home": "Oviedo",
      "away": "Getafe",
      "home_goals": 0,
      "away_goals": 0
    },
    {
      "date": "2026-05-03",
      "season": "2025-26",
      "home": "Betis",
      "away": "Oviedo",
      "home_goals": 3,
      "away_goals": 0
    }
  ],
  "Real Madrid": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Real Madrid",
      "away": "Ath Bilbao",
      "home_goals": 4,
      "away_goals": 2
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Sevilla",
      "away": "Real Madrid",
      "home_goals": 0,
      "away_goals": 1
    },
    {
      "date": "2026-05-14",
      "season": "2025-26",
      "home": "Real Madrid",
      "away": "Oviedo",
      "home_goals": 2,
      "away_goals": 0
    },
    {
      "date": "2026-05-10",
      "season": "2025-26",
      "home": "Barcelona",
      "away": "Real Madrid",
      "home_goals": 2,
      "away_goals": 0
    },
    {
      "date": "2026-05-03",
      "season": "2025-26",
      "home": "Espanol",
      "away": "Real Madrid",
      "home_goals": 0,
      "away_goals": 2
    }
  ],
  "Sevilla": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Celta",
      "away": "Sevilla",
      "home_goals": 1,
      "away_goals": 0
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Sevilla",
      "away": "Real Madrid",
      "home_goals": 0,
      "away_goals": 1
    },
    {
      "date": "2026-05-13",
      "season": "2025-26",
      "home": "Villarreal",
      "away": "Sevilla",
      "home_goals": 2,
      "away_goals": 3
    },
    {
      "date": "2026-05-09",
      "season": "2025-26",
      "home": "Sevilla",
      "away": "Espanol",
      "home_goals": 2,
      "away_goals": 1
    },
    {
      "date": "2026-05-04",
      "season": "2025-26",
      "home": "Sevilla",
      "away": "Sociedad",
      "home_goals": 1,
      "away_goals": 0
    }
  ],
  "Sociedad": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Espanol",
      "away": "Sociedad",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Sociedad",
      "away": "Valencia",
      "home_goals": 3,
      "away_goals": 4
    },
    {
      "date": "2026-05-14",
      "season": "2025-26",
      "home": "Girona",
      "away": "Sociedad",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-09",
      "season": "2025-26",
      "home": "Sociedad",
      "away": "Betis",
      "home_goals": 2,
      "away_goals": 2
    },
    {
      "date": "2026-05-04",
      "season": "2025-26",
      "home": "Sevilla",
      "away": "Sociedad",
      "home_goals": 1,
      "away_goals": 0
    }
  ],
  "Valencia": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Valencia",
      "away": "Barcelona",
      "home_goals": 3,
      "away_goals": 1
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Sociedad",
      "away": "Valencia",
      "home_goals": 3,
      "away_goals": 4
    },
    {
      "date": "2026-05-14",
      "season": "2025-26",
      "home": "Valencia",
      "away": "Vallecano",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-10",
      "season": "2025-26",
      "home": "Ath Bilbao",
      "away": "Valencia",
      "home_goals": 0,
      "away_goals": 1
    },
    {
      "date": "2026-05-02",
      "season": "2025-26",
      "home": "Valencia",
      "away": "Ath Madrid",
      "home_goals": 0,
      "away_goals": 2
    }
  ],
  "Vallecano": [
    {
      "date": "2026-05-23",
      "season": "2025-26",
      "home": "Alaves",
      "away": "Vallecano",
      "home_goals": 1,
      "away_goals": 2
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Vallecano",
      "away": "Villarreal",
      "home_goals": 2,
      "away_goals": 0
    },
    {
      "date": "2026-05-14",
      "season": "2025-26",
      "home": "Valencia",
      "away": "Vallecano",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-11",
      "season": "2025-26",
      "home": "Vallecano",
      "away": "Girona",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-03",
      "season": "2025-26",
      "home": "Getafe",
      "away": "Vallecano",
      "home_goals": 0,
      "away_goals": 2
    }
  ],
  "Villarreal": [
    {
      "date": "2026-05-24",
      "season": "2025-26",
      "home": "Villarreal",
      "away": "Ath Madrid",
      "home_goals": 5,
      "away_goals": 1
    },
    {
      "date": "2026-05-17",
      "season": "2025-26",
      "home": "Vallecano",
      "away": "Villarreal",
      "home_goals": 2,
      "away_goals": 0
    },
    {
      "date": "2026-05-13",
      "season": "2025-26",
      "home": "Villarreal",
      "away": "Sevilla",
      "home_goals": 2,
      "away_goals": 3
    },
    {
      "date": "2026-05-10",
      "season": "2025-26",
      "home": "Mallorca",
      "away": "Villarreal",
      "home_goals": 1,
      "away_goals": 1
    },
    {
      "date": "2026-05-02",
      "season": "2025-26",
      "home": "Villarreal",
      "away": "Levante",
      "home_goals": 5,
      "away_goals": 1
    }
  ]
};

// Datos reales de los 4 candidatos, verificados en reports/experiments/*.json
const MODEL_CANDIDATES = [
  { id: "A", algorithm: "Regresión logística multinomial", member: "Arnaldo (I1)", trainF1: 0.465, valF1: 0.465, gap: 0.000, status: "aprobado" },
  { id: "B", algorithm: "HistGradientBoostingClassifier", member: "Johans (I2)", trainF1: 0.754, valF1: 0.404, gap: 0.351, status: "descartado" },
  { id: "C", algorithm: "RandomForestClassifier", member: "César (I3)", trainF1: 0.468, valF1: 0.474, gap: 0.000, status: "aprobado" },
  { id: "D", algorithm: "SVC (kernel RBF)", member: "Fernanda (I4)", trainF1: 0.493, valF1: 0.484, gap: 0.009, status: "champion" },
];

const CHAMPION = {
  candidateId: "D",
  algorithm: "SVC(kernel=\"rbf\", probability=True)",
  modelVersion: "candidate_d_svc_rbf_v1",
  hyperparameters: { C: 0.5, kernel: "rbf", gamma: "scale", class_weight: "balanced", probability: true, random_state: 42 },
  trainRows: 9607,
  validationRows: 1197,
  finalFitRows: 10804,
  testRows: 1140,
  valMacroF1: 0.4837,
  gap: 0.009166,
  testMacroF1: 0.470529,
  selectionRule: "Mayor macro-F1 de validación entre candidatos con gap < 0.05; empate por menor latencia.",
  selectedOn: "2026-07-26",
};

const TRAINING_LOG = [
  { date: "2026-07-24", event: "Gate Data Ready verificado — checklist de 2_spec.md completa", actor: "Equipo (coordina I2)" },
  { date: "2026-07-26", event: "4 pipelines candidatos (A-D) entrenados y evaluados bajo protocolo común", actor: "I1, I2, I3, I4" },
  { date: "2026-07-26", event: "Modelo B descartado por overfitting severo (gap 0.351)", actor: "Johans (I2)" },
  { date: "2026-07-26", event: "Modelo C descartado en primer intento (gap 0.262)", actor: "César (I3)" },
  { date: "2026-07-26", event: "Champion seleccionado: Modelo D, evaluado una única vez sobre test", actor: "Equipo (coordina I2)" },
  { date: "2026-07-26", event: "Champion integrado en backend (POST /api/v1/predictions)", actor: "Fernanda (I4)" },
  { date: "2026-07-27", event: "Modelo C regularizado y reentrenado — gap baja a 0.000, val. sube a 0.474", actor: "César (I3)" },
];

const DATASET_INFO = {
  totalMatches: 11944,
  seasons: "1995/96 – 2025/26",
  targetDistribution: { H: 0.474, D: 0.256, A: 0.271 },
  imbalanceRatio: 1.85,
  metric: "macro-F1",
  gapLimit: 0.05,
};
