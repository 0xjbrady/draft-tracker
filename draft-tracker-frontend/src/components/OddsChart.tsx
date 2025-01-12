import { Box, Typography } from '@mui/material';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { ChartData } from '../types';

interface OddsChartProps {
  data: ChartData;
}

export default function OddsChart({ data }: OddsChartProps) {
  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <Typography variant="h6" align="center" gutterBottom>
        {data.title}
      </Typography>
      <ResponsiveContainer width="100%" height="90%">
        <LineChart data={data.data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            label={{ value: data.xAxisLabel, position: 'insideBottom', offset: -10 }}
            tickFormatter={(value) => new Date(value).toLocaleDateString()}
          />
          <YAxis label={{ value: data.yAxisLabel, angle: -90, position: 'insideLeft' }} />
          <Tooltip
            labelFormatter={(value) => new Date(value).toLocaleString()}
            formatter={(value: number) => [value.toFixed(2), data.yAxisLabel]}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            name={data.yAxisLabel}
            stroke="#8884d8"
            activeDot={{ r: 8 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
} 