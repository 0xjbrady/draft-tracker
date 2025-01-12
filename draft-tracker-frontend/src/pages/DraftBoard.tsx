import React, { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Typography, Paper, Link } from '@mui/material';
import { getDraftBoard } from '../services/api';
import DraftBoardChart from '../components/DraftBoardChart';
import ErrorAlert from '../components/common/ErrorAlert';
import DraftBoardSkeleton from '../components/common/DraftBoardSkeleton';
import { DraftBoardData } from '../types';

export const DraftBoard: React.FC = () => {
  const [data, setData] = useState<DraftBoardData[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getDraftBoard();
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load draft board data'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <DraftBoardSkeleton />;
  }

  if (error) {
    return (
      <ErrorAlert 
        error={error}
        onRetry={fetchData}
      />
    );
  }

  if (!data || data.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" color="text.secondary" align="center">
          No draft board data available. Please check back later when odds data has been collected.
        </Typography>
      </Box>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        NFL Draft Board
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Based on consensus odds from multiple sportsbooks
      </Typography>
      
      <Box sx={{ mt: 4, height: 400 }}>
        <DraftBoardChart data={data} />
      </Box>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Top Prospects
        </Typography>
        {data.slice(0, 10).map((player: DraftBoardData, index: number) => (
          <Box
            key={player.player_name}
            sx={{
              display: 'flex',
              alignItems: 'center',
              p: 2,
              borderBottom: '1px solid',
              borderColor: 'divider',
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <Typography variant="h6" sx={{ width: 40 }}>
              {index + 1}
            </Typography>
            <Box sx={{ ml: 2, flex: 1 }}>
              <Link
                component={RouterLink}
                to={`/player/${encodeURIComponent(player.player_name)}`}
                color="primary"
                sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
              >
                <Typography variant="subtitle1">
                  {player.player_name}
                </Typography>
              </Link>
              <Typography variant="body2" color="text.secondary">
                Std Dev: {player.standard_deviation.toFixed(2)}
              </Typography>
            </Box>
            <Typography variant="body1" color="primary">
              {player.consensus_position.toFixed(1)}
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
};

export default DraftBoard; 