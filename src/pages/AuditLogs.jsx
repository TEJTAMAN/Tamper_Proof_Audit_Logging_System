import { useState, useEffect } from 'react';
import { getLogs } from '../services/api';

const shortenHash = (hash) => {
  if (!hash) return 'NULL';
  return `${hash.substring(0, 8)}...${hash.substring(hash.length - 8)}`;
};

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await getLogs();
        setLogs(data.logs);
      } catch (error) {
        console.error('Error fetching logs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, []);

  if (loading) return <div>Loading logs...</div>;

  return (
    <div>
      <h1>Audit Logs</h1>
      <p>Complete history of all transactions, secured by blockchain hashes.</p>
      
      <div className="table-container" style={{ marginTop: '2rem' }}>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Time</th>
              <th>User</th>
              <th>Action</th>
              <th>Record ID</th>
              <th>Current Hash</th>
              <th>Previous Hash</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.log_id}>
                <td>{log.log_id}</td>
                <td>{new Date(log.action_time).toLocaleString()}</td>
                <td>{log.username || `User ${log.user_id}`}</td>
                <td><span className="badge" style={{backgroundColor: '#e2e8f0'}}>{log.action_type}</span></td>
                <td>{log.record_id}</td>
                <td><span className="hash-text" title={log.current_hash}>{shortenHash(log.current_hash)}</span></td>
                <td><span className="hash-text" title={log.previous_hash}>{shortenHash(log.previous_hash)}</span></td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td colSpan="7" style={{textAlign: 'center'}}>No audit logs found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AuditLogs;
