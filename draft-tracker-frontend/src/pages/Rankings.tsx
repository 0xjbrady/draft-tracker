import React, { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Link } from '@mui/material';
import { getConsensusRankings } from '../services/api';
import { ConsensusRanking } from '../types';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { PlayerOddsSkeleton } from '../components/common/PlayerOddsSkeleton';

interface RankingsData {
  [key: string]: ConsensusRanking;
}

export const Rankings: React.FC = () => {
  const [data, setData] = useState<RankingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchRankings = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getConsensusRankings();
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch rankings'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRankings();
  }, []);

  if (loading) {
    return <PlayerOddsSkeleton />;
  }

  if (error) {
    return (
      <Box p={3}>
        <ErrorAlert 
          error={error} 
          onRetry={fetchRankings} 
          severity="error"
        />
      </Box>
    );
  }

  if (!data || Object.keys(data).length === 0) {
    return (
      <Box p={3}>
        <Typography variant="h6">No rankings data available</Typography>
      </Box>
    );
  }

  const rankingsArray = Object.entries(data)
    .map(([name, ranking]) => ({
      name,
      ...ranking
    }))
    .sort((a, b) => a.consensus_position - b.consensus_position);

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        NFL Draft Consensus Rankings
      </Typography>
      <Typography variant="subtitle1" gutterBottom color="text.secondary">
        Based on aggregated odds from multiple sportsbooks
      </Typography>
      <TableContainer component={Paper} sx={{ mt: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Rank</strong></TableCell>
              <TableCell><strong>Player</strong></TableCell>
              <TableCell align="right"><strong>Consensus Position</strong></TableCell>
              <TableCell align="right"><strong>Standard Deviation</strong></TableCell>
              <TableCell align="right"><strong>Markets</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rankingsArray.map((player, index) => (
              <TableRow 
                key={player.name}
                sx={{ '&:hover': { backgroundColor: 'action.hover' } }}
              >
                <TableCell>{index + 1}</TableCell>
                <TableCell>
                  <Link
                    component={RouterLink}
                    to={`/player/${encodeURIComponent(player.name)}`}
                    color="primary"
                    sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
                  >
                    {player.name}
                  </Link>
                </TableCell>
                <TableCell align="right">{player.consensus_position.toFixed(1)}</TableCell>
                <TableCell align="right">{player.standard_deviation.toFixed(2)}</TableCell>
                <TableCell align="right">{player.number_of_markets}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Rankings; 