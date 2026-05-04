import { useState, useEffect } from 'react';
import { getAlerts } from '../services/api';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const data = await getAlerts();
        setAlerts(data.alerts);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
  }, []);

  if (loading) return <div>Loading alerts...</div>;

  return (
    <div>
      <h1>Security Alerts</h1>
      <p>System generated alerts for suspicious activity or chain breaks.</p>
      
      <div className="table-container" style={{ marginTop: '2rem' }}>
        <table>
          <thead>
            <tr>
              <th>Alert ID</th>
              <th>Time</th>
              <th>Log ID Reference</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((alert) => (
              <tr key={alert.alert_id}>
                <td>{alert.alert_id}</td>
                <td>{new Date(alert.created_at).toLocaleString()}</td>
                <td>{alert.log_id || 'N/A'}</td>
                <td><span style={{ color: 'var(--danger)', fontWeight: 500 }}>{alert.alert_message}</span></td>
              </tr>
            ))}
            {alerts.length === 0 && (
              <tr>
                <td colSpan="4" style={{textAlign: 'center', padding: '2rem'}}>
                  <span className="badge success">No security alerts triggered.</span>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Alerts;
