import { useState, useEffect } from 'react';
import { getSummary } from '../services/api';

const Summary = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await getSummary();
        setSummary(data);
      } catch (error) {
        console.error('Error fetching summary:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) return <div>Loading summary...</div>;
  if (!summary) return <div>Failed to load summary.</div>;

  return (
    <div>
      <h1>System Summary Statistics</h1>
      <p>Aggregated data from the database using SQL GROUP BY clauses.</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '2rem' }}>
        
        <div className="card">
          <h2 style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
            Logs by Action
          </h2>
          <table style={{ width: '100%' }}>
            <thead>
              <tr>
                <th style={{ background: 'none' }}>Action Type</th>
                <th style={{ background: 'none', textAlign: 'right' }}>Count</th>
              </tr>
            </thead>
            <tbody>
              {summary.by_action.map((item, index) => (
                <tr key={index}>
                  <td><span className="badge" style={{backgroundColor: '#e2e8f0'}}>{item.action_type}</span></td>
                  <td style={{ textAlign: 'right', fontWeight: 'bold' }}>{item.count}</td>
                </tr>
              ))}
              {summary.by_action.length === 0 && (
                <tr><td colSpan="2" style={{ textAlign: 'center' }}>No data</td></tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h2 style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
            Logs by User
          </h2>
          <table style={{ width: '100%' }}>
            <thead>
              <tr>
                <th style={{ background: 'none' }}>Username</th>
                <th style={{ background: 'none', textAlign: 'right' }}>Count</th>
              </tr>
            </thead>
            <tbody>
              {summary.by_user.map((item, index) => (
                <tr key={index}>
                  <td>{item.username}</td>
                  <td style={{ textAlign: 'right', fontWeight: 'bold' }}>{item.count}</td>
                </tr>
              ))}
              {summary.by_user.length === 0 && (
                <tr><td colSpan="2" style={{ textAlign: 'center' }}>No data</td></tr>
              )}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
};

export default Summary;
