import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import AppShell from './layout/AppShell';
import DrugTrialPage from './pages/DrugTrialPage';
import DrugDiscoveryPage from './pages/DrugDiscoveryPage';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppShell>
          <Routes>
            <Route path="/" element={<Navigate to="/trials" replace />} />
            <Route path="/trials" element={<DrugTrialPage />} />
            <Route path="/discovery" element={<DrugDiscoveryPage />} />
          </Routes>
        </AppShell>
      </Router>
    </ThemeProvider>
  );
}

export default App;
