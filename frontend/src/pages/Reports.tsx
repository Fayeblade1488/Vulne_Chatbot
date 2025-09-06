import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Button,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Tabs,
  Tab,
  LinearProgress,
} from '@mui/material';
import {
  Download,
  Search,
  FilterList,
  Assessment,
  BugReport,
  Security,
  TrendingUp,
  TrendingDown,
  ExpandMore,
  ExpandLess,
  GetApp,
  Share,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { api } from '../services/api';

interface Report {
  id: string;
  timestamp: string;
  testName: string;
  model: string;
  probe: string;
  status: 'passed' | 'failed' | 'blocked';
  vulnerability?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  response?: string;
  details?: any;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [filteredReports, setFilteredReports] = useState<Report[]>([]);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchReports();
  }, [timeRange]);

  useEffect(() => {
    applyFilters();
  }, [reports, searchTerm, filterSeverity, filterStatus]);

  const fetchReports = async () => {
    try {
      const response = await api.get(`/api/reports?timeRange=${timeRange}`);
      setReports(response.data);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    }
  };

  const applyFilters = () => {
    let filtered = [...reports];

    if (searchTerm) {
      filtered = filtered.filter(
        (r) =>
          r.testName.toLowerCase().includes(searchTerm.toLowerCase()) ||
          r.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
          r.probe.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterSeverity !== 'all') {
      filtered = filtered.filter((r) => r.severity === filterSeverity);
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter((r) => r.status === filterStatus);
    }

    setFilteredReports(filtered);
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'success';
      case 'failed':
        return 'error';
      case 'blocked':
        return 'warning';
      default:
        return 'default';
    }
  };

  const handleExportReport = async (format: 'json' | 'csv' | 'pdf') => {
    try {
      const response = await api.get(`/api/reports/export`, {
        params: { format, timeRange },
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${new Date().toISOString()}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export report:', error);
    }
  };

  // Calculate statistics
  const stats = {
    total: filteredReports.length,
    passed: filteredReports.filter((r) => r.status === 'passed').length,
    failed: filteredReports.filter((r) => r.status === 'failed').length,
    blocked: filteredReports.filter((r) => r.status === 'blocked').length,
    critical: filteredReports.filter((r) => r.severity === 'critical').length,
    high: filteredReports.filter((r) => r.severity === 'high').length,
  };

  // Prepare chart data
  const severityData = [
    { name: 'Critical', value: stats.critical, color: '#ff1744' },
    { name: 'High', value: stats.high, color: '#ff9800' },
    { name: 'Medium', value: filteredReports.filter((r) => r.severity === 'medium').length, color: '#2196f3' },
    { name: 'Low', value: filteredReports.filter((r) => r.severity === 'low').length, color: '#4caf50' },
  ];

  const modelPerformance = Object.entries(
    filteredReports.reduce((acc: any, report) => {
      if (!acc[report.model]) {
        acc[report.model] = { passed: 0, failed: 0, blocked: 0 };
      }
      acc[report.model][report.status]++;
      return acc;
    }, {})
  ).map(([model, stats]: [string, any]) => ({
    model,
    successRate: (stats.passed / (stats.passed + stats.failed + stats.blocked)) * 100,
    ...stats,
  }));

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h3" sx={{ fontWeight: 700 }}>
          Security Reports
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={() => handleExportReport('pdf')}
          >
            Export PDF
          </Button>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={() => handleExportReport('csv')}
          >
            Export CSV
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Tests
              </Typography>
              <Typography variant="h4">{stats.total}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ borderLeft: '4px solid #4caf50' }}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Passed
              </Typography>
              <Typography variant="h4" sx={{ color: '#4caf50' }}>
                {stats.passed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ borderLeft: '4px solid #ff1744' }}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Failed
              </Typography>
              <Typography variant="h4" sx={{ color: '#ff1744' }}>
                {stats.failed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ borderLeft: '4px solid #ff9800' }}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Blocked
              </Typography>
              <Typography variant="h4" sx={{ color: '#ff9800' }}>
                {stats.blocked}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ borderLeft: '4px solid #ff1744' }}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Critical
              </Typography>
              <Typography variant="h4" sx={{ color: '#ff1744' }}>
                {stats.critical}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ borderLeft: '4px solid #ff9800' }}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                High Severity
              </Typography>
              <Typography variant="h4" sx={{ color: '#ff9800' }}>
                {stats.high}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
          <Tab label="Test Results" />
          <Tab label="Vulnerability Analysis" />
          <Tab label="Model Performance" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {/* Filters */}
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <TextField
              placeholder="Search tests..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ flexGrow: 1 }}
            />
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Severity</InputLabel>
              <Select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                label="Severity"
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                label="Status"
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="passed">Passed</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
                <MenuItem value="blocked">Blocked</MenuItem>
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Time Range</InputLabel>
              <Select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                label="Time Range"
              >
                <MenuItem value="1h">Last Hour</MenuItem>
                <MenuItem value="24h">Last 24 Hours</MenuItem>
                <MenuItem value="7d">Last 7 Days</MenuItem>
                <MenuItem value="30d">Last 30 Days</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Results Table */}
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Test Name</TableCell>
                  <TableCell>Model</TableCell>
                  <TableCell>Probe</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Severity</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredReports
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((report) => (
                    <TableRow key={report.id}>
                      <TableCell>
                        {new Date(report.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell>{report.testName}</TableCell>
                      <TableCell>{report.model}</TableCell>
                      <TableCell>{report.probe}</TableCell>
                      <TableCell>
                        <Chip
                          label={report.status}
                          color={getStatusColor(report.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {report.severity && (
                          <Chip
                            label={report.severity}
                            color={getSeverityColor(report.severity) as any}
                            size="small"
                          />
                        )}
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => setSelectedReport(report)}
                          >
                            <ExpandMore />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={filteredReports.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Vulnerability Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={severityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <ChartTooltip />
                  <Bar dataKey="value">
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Attack Success Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={modelPerformance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="model" />
                  <YAxis />
                  <ChartTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="successRate" stroke="#00ff41" name="Success Rate %" />
                </LineChart>
              </ResponsiveContainer>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Model Performance Comparison
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={modelPerformance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model" />
              <YAxis />
              <ChartTooltip />
              <Legend />
              <Bar dataKey="passed" stackId="a" fill="#4caf50" />
              <Bar dataKey="failed" stackId="a" fill="#ff1744" />
              <Bar dataKey="blocked" stackId="a" fill="#ff9800" />
            </BarChart>
          </ResponsiveContainer>
        </TabPanel>
      </Paper>

      {/* Report Details Modal */}
      {selectedReport && (
        <Paper
          sx={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            width: 400,
            maxHeight: 500,
            overflow: 'auto',
            p: 3,
            boxShadow: 3,
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Report Details</Typography>
            <IconButton size="small" onClick={() => setSelectedReport(null)}>
              <ExpandLess />
            </IconButton>
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Typography variant="body2">
              <strong>ID:</strong> {selectedReport.id}
            </Typography>
            <Typography variant="body2">
              <strong>Test:</strong> {selectedReport.testName}
            </Typography>
            <Typography variant="body2">
              <strong>Model:</strong> {selectedReport.model}
            </Typography>
            <Typography variant="body2">
              <strong>Probe:</strong> {selectedReport.probe}
            </Typography>
            {selectedReport.vulnerability && (
              <Typography variant="body2">
                <strong>Vulnerability:</strong> {selectedReport.vulnerability}
              </Typography>
            )}
            {selectedReport.response && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  Response:
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    mt: 1,
                    p: 1,
                    bgcolor: 'grey.100',
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.85rem',
                  }}
                >
                  {selectedReport.response}
                </Typography>
              </Box>
            )}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default Reports;
