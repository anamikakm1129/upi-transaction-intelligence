import React, { useState, useRef } from 'react';
import { api, formatNumber } from '../services/api';

export function UploadModal({ isOpen, onClose, onUploadSuccess, showToast }) {
  const [file, setFile] = useState(null);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      setErrorMsg('Please select a valid CSV file (.csv).');
      return;
    }

    setFile(selectedFile);
    setErrorMsg('');
    setValidating(true);
    setValidationResult(null);

    try {
      const res = await api.validateCsv(selectedFile);
      setValidationResult(res);
    } catch (err) {
      console.error('Validation error:', err);
      setErrorMsg(err.message || 'Failed to inspect CSV schema.');
    } finally {
      setValidating(false);
    }
  };

  const handleConfirmProcessing = async () => {
    if (!file) return;
    setProcessing(true);
    setErrorMsg('');
    try {
      const res = await api.uploadCsv(file);
      if (showToast) {
        showToast(`Successfully processed ${formatNumber(res.cleaned_records_count)} transaction records!`, 'success');
      }
      onUploadSuccess(res);
      handleClose();
    } catch (err) {
      console.error('Processing error:', err);
      setErrorMsg(err.message || 'Failed to process dataset.');
    } finally {
      setProcessing(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setValidating(false);
    setValidationResult(null);
    setProcessing(false);
    setErrorMsg('');
    onClose();
  };

  return (
    <div className="drawer-backdrop" onClick={handleClose}>
      <div
        className="drawer-panel"
        style={{ maxWidth: 640 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="drawer-header">
          <div>
            <h3 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-main)' }}>
              Upload Transaction CSV
            </h3>
            <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>
              Inspect and ingest real UPI transaction records into analytics engine
            </p>
          </div>
          <button
            onClick={handleClose}
            style={{
              width: 36,
              height: 36,
              borderRadius: '50%',
              backgroundColor: 'var(--surface-hover)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 18,
              color: 'var(--text-muted)'
            }}
          >
            ✕
          </button>
        </div>

        <div className="drawer-body">
          {/* File Picker Zone */}
          <div
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: '2px dashed var(--border-focus)',
              borderRadius: 14,
              padding: '28px 20px',
              textAlign: 'center',
              backgroundColor: '#FAF8FC',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept=".csv"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            <div style={{ fontSize: 36, marginBottom: 10 }}>📤</div>
            <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-main)' }}>
              {file ? file.name : 'Choose a CSV file or drag & drop'}
            </div>
            <div style={{ fontSize: 13.5, color: 'var(--text-muted)', marginTop: 6 }}>
              Standard CSV (.csv) up to 25 MB with UTF-8 encoding
            </div>
          </div>

          {/* Error Banner */}
          {errorMsg && (
            <div style={{ padding: '14px 18px', borderRadius: 10, backgroundColor: 'var(--status-failed-bg)', border: '1px solid var(--status-failed)', color: 'var(--status-failed)', fontSize: 14, lineHeight: 1.5 }}>
              <strong>Error:</strong> {errorMsg}
            </div>
          )}

          {/* Validating Spinner */}
          {validating && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, padding: 24 }}>
              <div className="spinner" />
              <span style={{ fontSize: 14.5, color: 'var(--text-muted)' }}>Validating schema and inspecting data quality...</span>
            </div>
          )}

          {/* Validation Review State */}
          {validationResult && !validating && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {/* Validation Status Card */}
              <div
                style={{
                  padding: '16px 20px',
                  borderRadius: 10,
                  backgroundColor: validationResult.is_valid_schema ? '#ECFDF5' : '#FEF2F2',
                  border: `1px solid ${validationResult.is_valid_schema ? '#10B981' : '#EF4444'}`
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: 700, fontSize: 14.5, color: validationResult.is_valid_schema ? '#047857' : '#B91C1C' }}>
                    {validationResult.is_valid_schema ? '✓ Schema Validation Passed' : '⚠️ Missing Required Columns'}
                  </span>
                  <span className="mono" style={{ fontSize: 13.5, fontWeight: 600 }}>
                    {formatNumber(validationResult.total_records)} rows found
                  </span>
                </div>

                {validationResult.missing_columns && validationResult.missing_columns.length > 0 && (
                  <div style={{ marginTop: 8, fontSize: 13.5, color: '#B91C1C' }}>
                    Missing columns: <strong>{validationResult.missing_columns.join(', ')}</strong>
                  </div>
                )}
              </div>

              {/* Preliminary Quality Summary */}
              {validationResult.data_quality_preview && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
                  <div style={{ padding: 14, borderRadius: 8, background: '#FAF6F2', border: '1px solid var(--border-main)', textAlign: 'center' }}>
                    <div style={{ fontSize: 12.5, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>TOTAL ROWS</div>
                    <div className="mono" style={{ fontSize: 18, fontWeight: 700, marginTop: 4 }}>
                      {formatNumber(validationResult.total_records)}
                    </div>
                  </div>
                  <div style={{ padding: 14, borderRadius: 8, background: '#FAF6F2', border: '1px solid var(--border-main)', textAlign: 'center' }}>
                    <div style={{ fontSize: 12.5, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>DUPLICATE IDs</div>
                    <div className="mono" style={{ fontSize: 18, fontWeight: 700, marginTop: 4, color: validationResult.data_quality_preview.duplicate_records > 0 ? '#EF4444' : 'inherit' }}>
                      {formatNumber(validationResult.data_quality_preview.duplicate_records)}
                    </div>
                  </div>
                  <div style={{ padding: 14, borderRadius: 8, background: '#FAF6F2', border: '1px solid var(--border-main)', textAlign: 'center' }}>
                    <div style={{ fontSize: 12.5, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>INVALID ROWS</div>
                    <div className="mono" style={{ fontSize: 18, fontWeight: 700, marginTop: 4, color: validationResult.data_quality_preview.invalid_records > 0 ? '#F59E0B' : 'inherit' }}>
                      {formatNumber(validationResult.data_quality_preview.invalid_records)}
                    </div>
                  </div>
                </div>
              )}

              {/* Data Preview */}
              {validationResult.preview_rows && validationResult.preview_rows.length > 0 && (
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Data Preview (First {validationResult.preview_rows.length} Rows)
                  </div>
                  <div style={{ overflowX: 'auto', border: '1px solid var(--border-main)', borderRadius: 8 }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13.5, textAlign: 'left' }}>
                      <thead>
                        <tr style={{ background: '#FAF8F6', borderBottom: '1px solid var(--border-main)' }}>
                          <th style={{ padding: '8px 12px', fontWeight: 600 }}>transaction_id</th>
                          <th style={{ padding: '8px 12px', fontWeight: 600 }}>customer_id</th>
                          <th style={{ padding: '8px 12px', fontWeight: 600 }}>merchant_id</th>
                          <th style={{ padding: '8px 12px', fontWeight: 600 }}>amount</th>
                          <th style={{ padding: '8px 12px', fontWeight: 600 }}>category</th>
                        </tr>
                      </thead>
                      <tbody>
                        {validationResult.preview_rows.map((row, idx) => (
                          <tr key={idx} style={{ borderBottom: '1px solid #ECE8E5' }}>
                            <td className="mono" style={{ padding: '8px 12px' }}>{row.transaction_id || '—'}</td>
                            <td className="mono" style={{ padding: '8px 12px' }}>{row.customer_id || '—'}</td>
                            <td className="mono" style={{ padding: '8px 12px' }}>{row.merchant_id || '—'}</td>
                            <td className="mono" style={{ padding: '8px 12px', fontWeight: 600 }}>{row.amount ? `₹${row.amount}` : '—'}</td>
                            <td style={{ padding: '8px 12px' }}>{row.category || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Column requirements hint */}
          <div style={{ padding: 14, borderRadius: 10, background: '#FAF6F2', border: '1px solid var(--border-main)', fontSize: 13.5, color: 'var(--text-muted)', lineHeight: 1.5 }}>
            <div style={{ fontWeight: 700, color: 'var(--text-main)', marginBottom: 4 }}>Required Column Schema:</div>
            <code>transaction_id, timestamp, customer_id, merchant_id, amount, category, status</code>
            <div style={{ marginTop: 6, fontSize: 12.5 }}>
              Optional: <code>payment_method, bank_reference_number, device_type</code>
            </div>
          </div>
        </div>

        <div className="drawer-footer">
          <button className="btn btn-secondary" onClick={handleClose} disabled={processing}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={handleConfirmProcessing}
            disabled={!file || !validationResult?.is_valid_schema || processing}
          >
            {processing ? 'Processing & Ingesting...' : 'Confirm & Process Dataset'}
          </button>
        </div>
      </div>
    </div>
  );
}

