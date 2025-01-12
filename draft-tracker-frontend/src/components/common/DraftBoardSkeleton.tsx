import React from 'react';
import { Box, Skeleton, Grid } from '@mui/material';

export const DraftBoardSkeleton: React.FC = () => {
  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Chart Area Skeleton */}
      <Skeleton 
        variant="rectangular" 
        width="100%" 
        height={400} 
        sx={{ mb: 4 }}
      />

      {/* Player List Skeleton */}
      <Grid container spacing={2}>
        {[...Array(10)].map((_, index) => (
          <Grid item xs={12} key={index}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Skeleton variant="circular" width={40} height={40} />
              <Box sx={{ flex: 1 }}>
                <Skeleton variant="text" width="60%" height={24} />
                <Skeleton variant="text" width="40%" height={20} />
              </Box>
              <Skeleton variant="rectangular" width={80} height={32} />
            </Box>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default DraftBoardSkeleton; 