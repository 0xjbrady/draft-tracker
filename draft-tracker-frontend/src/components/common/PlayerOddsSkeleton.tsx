import React from 'react';
import { Box, Skeleton, TableContainer, Table, TableHead, TableRow, TableCell, TableBody, Paper } from '@mui/material';

export const PlayerOddsSkeleton: React.FC = () => {
  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      {/* Player Name and Subtitle */}
      <Skeleton variant="text" width={300} height={48} sx={{ mb: 1 }} />
      <Skeleton variant="text" width={400} height={24} sx={{ mb: 4 }} />
      
      {/* Chart Area Skeleton */}
      <Box sx={{ mt: 4, height: 400 }}>
        <Skeleton variant="rectangular" width="100%" height="100%" />
      </Box>

      {/* Table Skeleton */}
      <Box sx={{ mt: 4 }}>
        <Skeleton variant="text" width={200} height={32} sx={{ mb: 2 }} />
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><Skeleton variant="text" width={100} /></TableCell>
                <TableCell align="right"><Skeleton variant="text" width={80} /></TableCell>
                <TableCell align="right"><Skeleton variant="text" width={80} /></TableCell>
                <TableCell><Skeleton variant="text" width={100} /></TableCell>
                <TableCell><Skeleton variant="text" width={120} /></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {[...Array(5)].map((_, index) => (
                <TableRow key={index}>
                  <TableCell><Skeleton variant="text" width={100} /></TableCell>
                  <TableCell align="right"><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell align="right"><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell><Skeleton variant="text" width={140} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Paper>
  );
};

export default PlayerOddsSkeleton; 