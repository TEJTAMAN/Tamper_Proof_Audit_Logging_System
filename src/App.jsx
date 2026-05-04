import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import AddData from './pages/AddData';
import AuditLogs from './pages/AuditLogs';
import VerifyIntegrity from './pages/VerifyIntegrity';
import Alerts from './pages/Alerts';
import Summary from './pages/Summary';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/add-data" element={<AddData />} />
            <Route path="/logs" element={<AuditLogs />} />
            <Route path="/verify" element={<VerifyIntegrity />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/summary" element={<Summary />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
