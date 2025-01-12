import axios, { AxiosError } from 'axios';
import { OddsEntry, ConsensusRanking, DraftBoardData, OddsMovementData, ChartData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000, // 5 second timeout
});

const handleApiError = (error: unknown) => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail: string }>;
    if (axiosError.code === 'ECONNABORTED') {
      throw new Error('Request timed out. Please try again.');
    }
    if (axiosError.code === 'ERR_NETWORK') {
      throw new Error('Network error. Please check your connection and try again.');
    }
    if (axiosError.response?.data?.detail) {
      throw new Error(axiosError.response.data.detail);
    }
    if (axiosError.response?.status === 404) {
      throw new Error('Resource not found. Please try again later.');
    }
    if (axiosError.response?.status === 500) {
      throw new Error('Server error. Please try again later.');
    }
  }
  throw new Error('An unexpected error occurred. Please try again.');
};

export const getPlayerOddsHistory = async (playerName: string): Promise<OddsMovementData[]> => {
  try {
    const response = await api.get(`/odds/player/${encodeURIComponent(playerName)}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getPlayerOddsChart = async (playerName: string): Promise<ChartData> => {
  try {
    const response = await api.get(`/odds/player/${encodeURIComponent(playerName)}/chart`);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getConsensusRankings = async (): Promise<Record<string, ConsensusRanking>> => {
  try {
    const response = await api.get('/odds/rankings');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getDraftBoard = async (): Promise<DraftBoardData[]> => {
  try {
    const response = await api.get('/odds/draft-board');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getLatestOdds = async (): Promise<OddsEntry[]> => {
  try {
    const response = await api.get('/odds/latest');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
}; 