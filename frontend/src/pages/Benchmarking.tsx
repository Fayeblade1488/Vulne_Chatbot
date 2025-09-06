import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Tooltip,
  FormControlLabel,
  Checkbox,
  Switch,
  Slider,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Settings,
  Save,
  Upload,
  Download,
  ExpandMore,
  Security,
  BugReport,
  Code,
  Timer,
  Memory,
} from '@mui/icons-material';
import { api } from '../services/api';
import { useNotification } from '../contexts/NotificationContext';

interface TestConfig {
  name: string;
  type: 'garak' | 'nemo' | 'guardrailsai' | 'custom';
  enabled: boolean;
  probes: string[];
  models: string[];
  timeout: number;
  parallel: boolean;
  maxWorkers: number;
  outputFormat: string;
}

interface ProbeDefinition {
  id: string;
  name: string;
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  tags: string[];
}

const Benchmarking: React.FC = () => {
  const { showNotification } = useNotification();
  const [activeStep, setActiveStep] = useState(0);
  const [testConfigs, setTestConfigs] = useState<TestConfig[]>([]);
  const [availableProbes, setAvailableProbes] = useState<ProbeDefinition[]>([]);
  const [selectedProbes, setSelectedProbes] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<any>(null);

  const [config, setConfig] = useState({
    targetUrl: 'http://localhost:7000/chat',
    outputDir: './results',
    parallel: true,
    maxWorkers: 4,
    timeout: 300,
    retryCount: 3,
    verbose: true,
    saveResponses: true,
    generateReport: true,
  });

  useEffect(() => {
    loadAvailableProbes();
    loadSavedConfigs();
  }, []);

  const loadAvailableProbes = async () => {
    try {
      const response = await api.get('/api/probes/available');
      setAvailableProbes(response.data);
    } catch (error) {
      console.error('Failed to load probes:', error);
    }
  };

  const loadSavedConfigs = async () => {
    try {
      const response = await api.get('/api/benchmarks/configs');
      setTestConfigs(response.data);
    } catch (error) {
      console.error('Failed to load configs:', error);
    }
  };

  const handleRunBenchmark = async () => {
    setRunning(true);
    setProgress(0);
    
    try {
      const benchmarkConfig = {
        ...config,
        probes: selectedProbes,
        models: selectedModels,
        timestamp: new Date().toISOString(),
      };

      const response = await api.post('/api/benchmarks/run', benchmarkConfig);
      const taskId = response.data.task_id;

      // Poll for progress
      const pollInterval = setInterval(async () => {
        const statusRes = await api.get(`/api/benchmarks/status/${taskId}`);
        setProgress(statusRes.data.progress);
        
        if (statusRes.data.status === 'completed') {
          clearInterval(pollInterval);
          setResults(statusRes.data.results);
          setRunning(false);
          showNotification('Benchmark completed successfully!', 'success');
        } else if (statusRes.data.status === 'failed') {
          clearInterval(pollInterval);
          setRunning(false);
          showNotification('Benchmark failed. Check logs for details.', 'error');
        }
      }, 1000);
    } catch (error) {
      setRunning(false);
      showNotification('Failed to start benchmark', 'error');
      console.error('Benchmark error:', error);
    }
  };

  const handleStopBenchmark = async () => {
    try {
      await api.post('/api/benchmarks/stop');
      setRunning(false);
      showNotification('Benchmark stopped', 'info');
    } catch (error) {
      console.error('Failed to stop benchmark:', error);
    }
  };

  const handleSaveConfig = async () => {
    try {
      const configToSave = {
        name: `Config_${new Date().toISOString()}`,
        ...config,
        probes: selectedProbes,
        models: selectedModels,
      };
      
      await api.post('/api/benchmarks/configs', configToSave);
      showNotification('Configuration saved', 'success');
      loadSavedConfigs();
    } catch (error) {
      showNotification('Failed to save configuration', 'error');
    }
  };

  const probeCategories = [...new Set(availableProbes.map(p => p.category))];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h3" sx={{ mb: 3, fontWeight: 700 }}>
        Benchmarking Suite
      </Typography>

      <Grid container spacing={3}>
        {/* Configuration Panel */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" sx={{ mb: 3 }}>
              Test Configuration
            </Typography>

            <Stepper activeStep={activeStep} orientation="vertical">
              <Step>
                <StepLabel>Target Configuration</StepLabel>
                <StepContent>
                  <Box sx={{ mb: 2 }}>
                    <TextField
                      fullWidth
                      label="Target URL"
                      value={config.targetUrl}
                      onChange={(e) => setConfig({ ...config, targetUrl: e.target.value })}
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      label="Output Directory"
                      value={config.outputDir}
                      onChange={(e) => setConfig({ ...config, outputDir: e.target.value })}
                      sx={{ mb: 2 }}
                    />
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Button variant="contained" onClick={() => setActiveStep(1)}>
                        Continue
                      </Button>
                    </Box>
                  </Box>
                </StepContent>
              </Step>

              <Step>
                <StepLabel>Select Probes</StepLabel>
                <StepContent>
                  {probeCategories.map((category) => (
                    <Accordion key={category}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography>{category}</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {availableProbes
                            .filter((p) => p.category === category)
                            .map((probe) => (
                              <Chip
                                key={probe.id}
                                label={probe.name}
                                onClick={() => {
                                  setSelectedProbes((prev) =>
                                    prev.includes(probe.id)
                                      ? prev.filter((id) => id !== probe.id)
                                      : [...prev, probe.id]
                                  );
                                }}
                                color={selectedProbes.includes(probe.id) ? 'primary' : 'default'}
                                variant={selectedProbes.includes(probe.id) ? 'filled' : 'outlined'}
                              />
                            ))}
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                  <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                    <Button onClick={() => setActiveStep(0)}>Back</Button>
                    <Button variant="contained" onClick={() => setActiveStep(2)}>
                      Continue
                    </Button>
                  </Box>
                </StepContent>
              </Step>

              <Step>
                <StepLabel>Model Selection</StepLabel>
                <StepContent>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Models</InputLabel>
                    <Select
                      multiple
                      value={selectedModels}
                      onChange={(e) => setSelectedModels(e.target.value as string[])}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {(selected as string[]).map((value) => (
                            <Chip key={value} label={value} size="small" />
                          ))}
                        </Box>
                      )}
                    >
                      <MenuItem value="mistral:latest">Mistral Latest</MenuItem>
                      <MenuItem value="llama2:latest">Llama 2</MenuItem>
                      <MenuItem value="oci:cohere.command-r-plus">Cohere Command R+</MenuItem>
                      <MenuItem value="openai:gpt-4">GPT-4</MenuItem>
                    </Select>
                  </FormControl>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button onClick={() => setActiveStep(1)}>Back</Button>
                    <Button variant="contained" onClick={() => setActiveStep(3)}>
                      Continue
                    </Button>
                  </Box>
                </StepContent>
              </Step>

              <Step>
                <StepLabel>Advanced Settings</StepLabel>
                <StepContent>
                  <Box sx={{ mb: 3 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.parallel}
                          onChange={(e) => setConfig({ ...config, parallel: e.target.checked })}
                        />
                      }
                      label="Parallel Execution"
                    />
                    
                    {config.parallel && (
                      <Box sx={{ mt: 2 }}>
                        <Typography gutterBottom>Max Workers: {config.maxWorkers}</Typography>
                        <Slider
                          value={config.maxWorkers}
                          onChange={(e, value) => setConfig({ ...config, maxWorkers: value as number })}
                          min={1}
                          max={16}
                          marks
                          valueLabelDisplay="auto"
                        />
                      </Box>
                    )}

                    <Box sx={{ mt: 2 }}>
                      <Typography gutterBottom>Timeout (seconds): {config.timeout}</Typography>
                      <Slider
                        value={config.timeout}
                        onChange={(e, value) => setConfig({ ...config, timeout: value as number })}
                        min={30}
                        max={600}
                        step={30}
                        marks
                        valueLabelDisplay="auto"
                      />
                    </Box>

                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={config.verbose}
                          onChange={(e) => setConfig({ ...config, verbose: e.target.checked })}
                        />
                      }
                      label="Verbose Output"
                    />
                    
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={config.saveResponses}
                          onChange={(e) => setConfig({ ...config, saveResponses: e.target.checked })}
                        />
                      }
                      label="Save All Responses"
                    />
                    
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={config.generateReport}
                          onChange={(e) => setConfig({ ...config, generateReport: e.target.checked })}
                        />
                      }
                      label="Generate Report"
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button onClick={() => setActiveStep(2)}>Back</Button>
                    <Button variant="contained" color="success" onClick={handleRunBenchmark}>
                      Start Benchmark
                    </Button>
                  </Box>
                </StepContent>
              </Step>
            </Stepper>
          </Paper>
        </Grid>

        {/* Status Panel */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Execution Status
            </Typography>
            
            {running ? (
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CircularProgress size={40} sx={{ mr: 2 }} />
                  <Typography>Running benchmarks...</Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Progress: {progress}%
                  </Typography>
                  <LinearProgress variant="determinate" value={progress} />
                </Box>
                <Button
                  variant="contained"
                  color="error"
                  onClick={handleStopBenchmark}
                  startIcon={<Stop />}
                  fullWidth
                >
                  Stop Benchmark
                </Button>
              </Box>
            ) : (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  No benchmark running
                </Alert>
                <Button
                  variant="contained"
                  onClick={handleRunBenchmark}
                  startIcon={<PlayArrow />}
                  disabled={selectedProbes.length === 0 || selectedModels.length === 0}
                  fullWidth
                >
                  Start Benchmark
                </Button>
              </Box>
            )}
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<Save />}
                onClick={handleSaveConfig}
                fullWidth
              >
                Save Configuration
              </Button>
              <Button variant="outlined" startIcon={<Upload />} fullWidth>
                Load Configuration
              </Button>
              <Button variant="outlined" startIcon={<Download />} fullWidth>
                Export Results
              </Button>
            </Box>
          </Paper>

          {/* Summary Stats */}
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Configuration Summary
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2">
                <strong>Selected Probes:</strong> {selectedProbes.length}
              </Typography>
              <Typography variant="body2">
                <strong>Selected Models:</strong> {selectedModels.length}
              </Typography>
              <Typography variant="body2">
                <strong>Execution Mode:</strong> {config.parallel ? 'Parallel' : 'Sequential'}
              </Typography>
              <Typography variant="body2">
                <strong>Timeout:</strong> {config.timeout}s
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Results Section */}
      {results && (
        <Grid container spacing={3} sx={{ mt: 3 }}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" sx={{ mb: 2 }}>
                Benchmark Results
              </Typography>
              <pre>{JSON.stringify(results, null, 2)}</pre>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default Benchmarking;
