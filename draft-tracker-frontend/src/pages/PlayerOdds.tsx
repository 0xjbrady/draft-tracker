import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { getPlayerOddsHistory, getPlayerOddsChart } from '../services/api';
import OddsChart from '../components/OddsChart';
import ErrorAlert from '../components/common/ErrorAlert';
import PlayerOddsSkeleton from '../components/common/PlayerOddsSkeleton';
import { OddsMovementData, ChartData } from '../types';

interface PlayerData {
  history: OddsMovementData[];
  chart: ChartData;
}

export const PlayerOdds: React.FC = () => {
  const { name } = useParams<{ name: string }>();
  const [data, setData] = useState<PlayerData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    if (!name) return;

    try {
      setLoading(true);
      setError(null);
      const [historyResponse, chartResponse] = await Promise.all([
        getPlayerOddsHistory(name),
        getPlayerOddsChart(name),
      ]);
      setData({
        history: historyResponse,
        chart: chartResponse,
      });
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load player odds data'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [name]);

  if (!name) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" color="text.secondary" align="center">
          No player specified
        </Typography>
      </Box>
    );
  }

  if (loading) {
    return <PlayerOddsSkeleton />;
  }

  if (error) {
    return (
      <Box p={3}>
        <ErrorAlert 
          error={error} 
          severity="error"
          onRetry={() => {
            setError(null);
            setLoading(true);
            fetchData();
          }}
        />
      </Box>
    );
  }

  if (!data || !data.history || data.history.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" color="text.secondary" align="center">
          No odds data available for {name}. Please check back later when odds data has been collected.
        </Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        {name}
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Draft Position Odds History
      </Typography>
      
      <Box my={4}>
        <OddsChart data={data.chart} />
      </Box>

      <TableContainer component={Paper} sx={{ mt: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Sportsbook</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="right">Draft Position</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="right">Odds</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.history.map((entry, index) => (
              <TableRow key={index} hover>
                <TableCell>{new Date(entry.timestamp).toLocaleDateString()}</TableCell>
                <TableCell>{entry.sportsbook}</TableCell>
                <TableCell align="right">{entry.draft_position}</TableCell>
                <TableCell align="right">{entry.odds}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default PlayerOdds; 