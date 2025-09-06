import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Security,
  BugReport,
  Speed,
  Assessment,
  Warning,
  CheckCircle,
  Error,
  Refresh,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { api } from '../services/api';

interface MetricCard {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  color: string;
  severity?: 'success' | 'warning' | 'error' | 'info';
}

interface VulnerabilityData {
  name: string;
  value: number;
  severity: string;
}

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricCard[]>([]);
  const [vulnerabilities, setVulnerabilities] = useState<VulnerabilityData[]>([]);
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [testStatus, setTestStatus] = useState<any>({});

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [metricsRes, vulnRes, timeSeriesRes, statusRes] = await Promise.all([
        api.get('/api/metrics'),
        api.get('/api/vulnerabilities/summary'),
        api.get('/api/metrics/timeseries'),
        api.get('/api/test/status'),
      ]);

      setMetrics([
        {
          title: 'Total Tests Run',
          value: metricsRes.data.total_tests || 0,
          icon: <Assessment />,
          color: '#2196f3',
          change: 12,
        },
        {
          title: 'Vulnerabilities Found',
          value: metricsRes.data.vulnerabilities_found || 0,
          icon: <BugReport />,
          color: '#ff1744',
          severity: 'error',
          change: -5,
        },
        {
          title: 'Success Rate',
          value: `${metricsRes.data.success_rate || 0}%`,
          icon: <CheckCircle />,
          color: '#00ff41',
          severity: 'success',
        },
        {
          title: 'Avg Response Time',
          value: `${metricsRes.data.avg_response_time || 0}ms`,
          icon: <Speed />,
          color: '#ff9800',
          change: -15,
        },
      ]);

      setVulnerabilities(vulnRes.data || []);
      setTimeSeriesData(timeSeriesRes.data || []);
      setTestStatus(statusRes.data || {});
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#ff1744', '#ff9800', '#ffeb3b', '#4caf50'];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h3" sx={{ fontWeight: 700 }}>
          Security Dashboard
        </Typography>
        <Tooltip title="Refresh Data">
          <IconButton onClick={fetchDashboardData} color="primary">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Metric Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                background: `linear-gradient(135deg, ${metric.color}20 0%, ${metric.color}10 100%)`,
                border: `1px solid ${metric.color}40`,
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 2,
                      backgroundColor: `${metric.color}20`,
                      display: 'flex',
                      mr: 2,
                    }}
                  >
                    {metric.icon}
                  </Box>
                  <Typography variant="h6" component="div">
                    {metric.title}
                  </Typography>
                </Box>
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
                  {metric.value}
                </Typography>
                {metric.change && (
                  <Typography
                    variant="body2"
                    sx={{
                      color: metric.change > 0 ? '#00ff41' : '#ff1744',
                      display: 'flex',
                      alignItems: 'center',
                    }}
                  >
                    {metric.change > 0 ? '↑' : '↓'} {Math.abs(metric.change)}% from last run
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Vulnerability Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Vulnerability Distribution
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={vulnerabilities}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {vulnerabilities.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <ChartTooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Attack Success Rate Over Time */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Attack Success Rate Trend
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <LineChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <ChartTooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="successRate"
                  stroke="#00ff41"
                  strokeWidth={2}
                  name="Success Rate"
                />
                <Line
                  type="monotone"
                  dataKey="blockRate"
                  stroke="#ff1744"
                  strokeWidth={2}
                  name="Block Rate"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Test Status */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Current Test Status
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {Object.entries(testStatus).map(([key, value]: [string, any]) => (
                <Box key={key} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography sx={{ minWidth: 150 }}>{key}:</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={value.progress || 0}
                    sx={{ flexGrow: 1, height: 10, borderRadius: 5 }}
                  />
                  <Chip
                    label={value.status}
                    color={value.status === 'running' ? 'warning' : 'success'}
                    size="small"
                  />
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
