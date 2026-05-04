import { useState, useEffect } from 'react';
import { getLogsCount, verifyChain, getDataRecords } from '../services/api';

const Dashboard = () => {
  const [logsCount, setLogsCount] = useState(0);
  const [recordsCount, setRecordsCount] = useState(0);
  const [chainStatus, setChainStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [logsRes, verifyRes, dataRes] = await Promise.all([
          getLogsCount(),
          verifyChain(),
          getDataRecords()
        ]);
        
        setLogsCount(logsRes.count);
        setChainStatus(verifyRes);
        setRecordsCount(dataRes.count);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) return <div>Loading dashboard...</div>;

  return (
    <div>
      <h1>Dashboard</h1>
      
      <div className="card-grid">
        <div className="card">
          <h3>Total Audit Logs</h3>
          <div className="value">{logsCount}</div>
        </div>
        
        <div className="card">
          <h3>Total Data Records</h3>
          <div className="value">{recordsCount}</div>
        </div>

        <div className="card">
          <h3>Blockchain Status</h3>
          <div className="value">
            {chainStatus?.is_valid ? (
              <span className="badge success">Valid & Secure</span>
            ) : (
              <span className="badge danger">Broken!</span>
            )}
          </div>
          <p style={{marginTop: '0.5rem', fontSize: '0.875rem'}}>
            {chainStatus?.message}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
