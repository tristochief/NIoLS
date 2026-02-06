import React, { useState } from 'react'
import { NHIDetectionEnvelope as NHIDetectionType, SessionStatus } from '../api'
import './NHIDetectionPanel.css'

interface NHIDetectionPanelProps {
  detection: NHIDetectionType | null
  sessionStatus: SessionStatus | null
  onSendResponse: () => Promise<void>
  loading?: boolean
}

const NHIDetectionPanel: React.FC<NHIDetectionPanelProps> = ({
  detection,
  sessionStatus,
  onSendResponse,
  loading = false,
}) => {
  const [responseError, setResponseError] = useState<string | null>(null)
  const state = sessionStatus?.state ?? null
  const canSendResponse =
    detection?.envelope_satisfied === true && state === 'EMIT_READY' && !loading

  const handleSendResponse = async () => {
    if (!canSendResponse) return
    setResponseError(null)
    try {
      await onSendResponse()
    } catch (err) {
      setResponseError(err instanceof Error ? err.message : 'Send response failed')
    }
  }

  if (!detection) {
    return (
      <div className="nhi-detection-panel">
        <h3>NHI Detection Envelope</h3>
        <p className="nhi-disclaimer">No measurement yet. Start measurement to evaluate detection envelope.</p>
      </div>
    )
  }

  const satisfied = detection.envelope_satisfied
  const wEnv = detection.wavelength_envelope_nm
  const vEnv = detection.voltage_envelope_v
  const ts = detection.timestamp ? new Date(detection.timestamp * 1000).toISOString() : '—'

  return (
    <div className="nhi-detection-panel">
      <h3>NHI Detection Envelope</h3>
      <div className={`nhi-status ${satisfied ? 'satisfied' : 'not-satisfied'}`}>
        <span className="nhi-status-label">Envelope:</span>
        <span className="nhi-status-value">{satisfied ? 'Satisfied' : 'Not satisfied'}</span>
      </div>
      <div className="nhi-metrics">
        {wEnv && (
          <div className="nhi-metric">
            <div className="nhi-metric-label">Wavelength envelope</div>
            <div className="nhi-metric-value">
              {wEnv.min_nm.toFixed(1)} – {wEnv.max_nm.toFixed(1)} nm
            </div>
          </div>
        )}
        {vEnv && (
          <div className="nhi-metric">
            <div className="nhi-metric-label">Voltage envelope</div>
            <div className="nhi-metric-value">
              {vEnv.min_v.toFixed(4)} – {vEnv.max_v.toFixed(4)} V
            </div>
          </div>
        )}
        <div className="nhi-timestamp">Last evaluated: {ts}</div>
      </div>
      <div className="nhi-response-section">
        <p className="nhi-doctrine">
          Detection envelope satisfied = optical signal in band above baseline. No identification claimed.
        </p>
        <p className="nhi-response-copy">
          When envelope is satisfied and system is EMIT_READY, send response (uplink) to complete the two-way optical link.
        </p>
        <button
          type="button"
          className="nhi-send-response-btn"
          disabled={!canSendResponse}
          onClick={handleSendResponse}
          title={
            !satisfied
              ? 'Detection envelope not satisfied'
              : state !== 'EMIT_READY'
                ? `System must be EMIT_READY (current: ${state})`
                : 'Emit configured response pattern'
          }
        >
          {loading ? 'Sending…' : 'Send response (uplink)'}
        </button>
        {responseError && <p className="nhi-response-error">{responseError}</p>}
      </div>
      <p className="nhi-disclaimer">{detection.note}</p>
    </div>
  )
}

export default NHIDetectionPanel
