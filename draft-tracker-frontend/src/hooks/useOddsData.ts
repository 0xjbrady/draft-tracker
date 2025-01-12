import { useQuery } from '@tanstack/react-query';
import * as api from '../services/api';
import { OddsEntry, ConsensusRanking, DraftBoardData, OddsMovementData } from '../types';

export const usePlayerOddsHistory = (playerName: string) => {
  return useQuery<OddsMovementData[]>({
    queryKey: ['playerOdds', playerName],
    queryFn: () => api.getPlayerOddsHistory(playerName),
    enabled: !!playerName,
  });
};

export const usePlayerOddsChart = (playerName: string) => {
  return useQuery({
    queryKey: ['playerOddsChart', playerName],
    queryFn: () => api.getPlayerOddsChart(playerName),
    enabled: !!playerName,
  });
};

export const useConsensusRankings = () => {
  return useQuery<Record<string, ConsensusRanking>>({
    queryKey: ['consensusRankings'],
    queryFn: api.getConsensusRankings,
    refetchInterval: 300000, // Refetch every 5 minutes
  });
};

export const useDraftBoard = () => {
  return useQuery<DraftBoardData[]>({
    queryKey: ['draftBoard'],
    queryFn: api.getDraftBoard,
    refetchInterval: 300000, // Refetch every 5 minutes
  });
};

export const useLatestOdds = () => {
  return useQuery<OddsEntry[]>({
    queryKey: ['latestOdds'],
    queryFn: api.getLatestOdds,
    refetchInterval: 300000, // Refetch every 5 minutes
  });
}; 