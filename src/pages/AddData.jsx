import { useState } from 'react';
import { addData } from '../services/api';

const AddData = () => {
  const [dataContent, setDataContent] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!dataContent.trim()) {
      setStatus({ type: 'danger', message: 'Data content cannot be empty' });
      return;
    }

    setLoading(true);
    try {
      await addData(dataContent);
      setStatus({ type: 'success', message: 'Record added! Audit log automatically created.' });
      setDataContent('');
    } catch (error) {
      setStatus({ 
        type: 'danger', 
        message: error.response?.data?.error || 'Failed to add data' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Add Data Record</h1>
      <p>Inserting a record here will trigger the MySQL database to automatically create a blockchain-hashed audit log.</p>
      
      <div className="card" style={{ maxWidth: '600px', marginTop: '2rem' }}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="dataContent">Data Content</label>
            <input
              type="text"
              id="dataContent"
              className="form-control"
              value={dataContent}
              onChange={(e) => setDataContent(e.target.value)}
              placeholder="Enter some sensitive data to log..."
              disabled={loading}
            />
          </div>
          
          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Adding...' : 'Add Record'}
          </button>
        </form>

        {status.message && (
          <div className={`badge ${status.type}`} style={{ marginTop: '1rem', display: 'block', padding: '1rem' }}>
            {status.message}
          </div>
        )}
      </div>
    </div>
  );
};

export default AddData;
