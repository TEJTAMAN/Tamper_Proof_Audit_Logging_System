import { useState, useEffect } from 'react';
import { verifyChain } from '../services/api';

const VerifyIntegrity = () => {
  const [verification, setVerification] = useState(null);
  const [loading, setLoading] = useState(false);

  const runVerification = async () => {
    setLoading(true);
    try {
      const data = await verifyChain();
      setVerification(data);
    } catch (error) {
      console.error('Error verifying chain:', error);
      setVerification({ is_valid: false, message: 'Failed to connect to verification server.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runVerification();
  }, []);

  return (
    <div>
      <h1>Blockchain Integrity Check</h1>
      <p>Verifies that no historical logs have been tampered with by re-calculating the hash chain.</p>
      
      <div className="card" style={{ marginTop: '2rem', textAlign: 'center', padding: '3rem 2rem' }}>
        {loading ? (
          <h2>Verifying blocks...</h2>
        ) : verification ? (
          <>
            <div style={{ marginBottom: '2rem' }}>
              {verification.is_valid ? (
                <div style={{ color: 'var(--success)' }}>
                  <svg style={{ width: '80px', height: '80px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h2 style={{ fontSize: '2rem', marginTop: '1rem', color: 'var(--success)' }}>Chain is Valid</h2>
                </div>
              ) : (
                <div style={{ color: 'var(--danger)' }}>
                  <svg style={{ width: '80px', height: '80px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h2 style={{ fontSize: '2rem', marginTop: '1rem', color: 'var(--danger)' }}>Tampering Detected!</h2>
                </div>
              )}
            </div>
            
            <p style={{ fontSize: '1.2rem', marginBottom: '1rem', color: 'var(--text-dark)' }}>
              {verification.message}
            </p>
            {verification.checked !== undefined && (
              <p>Checked {verification.checked} cryptographically linked blocks.</p>
            )}
            
          </>
        ) : null}

        <button 
          className="btn" 
          onClick={runVerification} 
          disabled={loading}
          style={{ marginTop: '2rem' }}
        >
          {loading ? 'Running Scan...' : 'Re-run Verification'}
        </button>
      </div>
    </div>
  );
};

export default VerifyIntegrity;
