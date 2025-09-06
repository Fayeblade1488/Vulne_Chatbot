import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

// Pages
import Dashboard from './pages/Dashboard';
import ChatInterface from './pages/ChatInterface';
import BenchmarkRunner from './pages/BenchmarkRunner';
import VulnerabilityReport from './pages/VulnerabilityReport';
import Settings from './pages/Settings';

// Components
import Navigation from './components/Navigation';
import { NotificationProvider } from './components/NotificationProvider';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00ff41',
    },
    secondary: {
      main: '#ff1744',
    },
    background: {
      default: '#0a0e1a',
      paper: '#0f1823',
    },
    error: {
      main: '#ff1744',
    },
    warning: {
      main: '#ff9800',
    },
    info: {
      main: '#2196f3',
    },
    success: {
      main: '#00ff41',
    },
  },
  typography: {
    fontFamily: '"JetBrains Mono", "Roboto Mono", monospace',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          borderRadius: 12,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <NotificationProvider>
        <Router>
          <Box sx={{ display: 'flex', height: '100vh' }}>
            <Navigation />
            <Box
              component="main"
              sx={{
                flexGrow: 1,
                p: 3,
                overflow: 'auto',
                backgroundColor: 'background.default',
              }}
            >
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/chat" element={<ChatInterface />} />
                <Route path="/benchmark" element={<BenchmarkRunner />} />
                <Route path="/reports" element={<VulnerabilityReport />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Box>
          </Box>
        </Router>
      </NotificationProvider>
    </ThemeProvider>
  );
}

export default App;
