export interface Player {
  id: number;
  name: string;
  position: string;
  college: string;
}

export interface OddsEntry {
  id: number;
  player_id: number;
  odds: string;
  draft_position: number;
  sportsbook: string;
  market_type: string;
  timestamp: string;
  player: Player;
}

export interface ConsensusRanking {
  consensus_position: number;
  standard_deviation: number;
  number_of_markets: number;
}

export interface DraftBoardData {
  player_name: string;
  consensus_position: number;
  standard_deviation: number;
}

export interface OddsMovementData {
  timestamp: string;
  odds: string;
  draft_position: number;
  sportsbook: string;
  market_type: string;
}

export interface ChartData {
  data: {
    timestamp: string;
    value: number;
    label?: string;
  }[];
  xAxisLabel: string;
  yAxisLabel: string;
  title: string;
} 