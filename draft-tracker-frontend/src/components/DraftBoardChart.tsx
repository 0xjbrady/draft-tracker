import { Box, Typography } from '@mui/material';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ErrorBar,
} from 'recharts';
import { DraftBoardData } from '../types';

interface DraftBoardChartProps {
  data: DraftBoardData[];
}

export default function DraftBoardChart({ data }: DraftBoardChartProps) {
  const chartData = data.map((item) => ({
    name: item.player_name,
    x: item.consensus_position,
    y: data.length - data.findIndex((d) => d.player_name === item.player_name), // Reverse Y-axis for visual ranking
    errorX: item.standard_deviation,
  }));

  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <Typography variant="h6" align="center" gutterBottom>
        NFL Draft Consensus Board
      </Typography>
      <ResponsiveContainer width="100%" height="90%">
        <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 60 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="x"
            name="Draft Position"
            label={{ value: 'Draft Position', position: 'bottom' }}
            domain={[0, 'auto']}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="Player"
            tickFormatter={(value) => {
              const player = chartData.find((d) => d.y === value);
              return player ? player.name : '';
            }}
          />
          <Tooltip
            formatter={(value: number, name: string) => {
              if (name === 'x') return [`Position: ${value.toFixed(1)}`, 'Consensus Position'];
              return [value, name];
            }}
          />
          <Scatter name="Players" data={chartData} fill="#8884d8">
            <ErrorBar dataKey="errorX" width={4} strokeWidth={2} stroke="#8884d8" direction="x" />
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </Box>
  );
} 