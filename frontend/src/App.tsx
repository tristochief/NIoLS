import React, { useState, useEffect, useCallback } from 'react'
import { api, Status, HealthStatus, MeasurementHistory, SessionStatus, MeasurementEnvelope, NHIDetectionEnvelope } from './api'
import Sidebar from './components/Sidebar'
import WavelengthMeasurement from './components/WavelengthMeasurement'
import LaserControl from './components/LaserControl'
import NHIDetectionPanel from './components/NHIDetectionPanel'
import './App.css'

function App() {
  const [status, setStatus] = useState<Status | null>(null)
  const [sessionStatus, setSessionStatus] = useState<SessionStatus | null>(null)
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null)
  const [measurementHistory, setMeasurementHistory] = useState<MeasurementHistory>({ wavelengths: [], voltages: [] })
  const [measurementEnvelope, setMeasurementEnvelope] = useState<MeasurementEnvelope | null>(null)
  const [nhiDetection, setNHIDetection] = useState<NHIDetectionEnvelope | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const loadStatus = useCallback(async () => {
    try {
      const newStatus = await api.getStatus()
      // Check if it's SessionStatus (has state and budget) or legacy Status
      if ('state' in newStatus && 'budget' in newStatus) {
        setSessionStatus(newStatus as SessionStatus)
        // Also set as status for backward compatibility
        setStatus({ ...newStatus } as Status)
      } else {
        setStatus(newStatus as Status)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load status')
    }
  }, [])

  const loadMeasurementEnvelope = useCallback(async () => {
    try {
      const envelope = await api.getCurrentMeasurement()
      setMeasurementEnvelope(envelope)
    } catch (err) {
      // Ignore errors for measurement envelope
    }
  }, [])

  const loadHealthStatus = useCallback(async () => {
    try {
      const health = await api.getHealthStatus()
      setHealthStatus(health)
    } catch (err) {
      // Health check might not have been run yet
    }
  }, [])

  const loadMeasurementHistory = useCallback(async () => {
    try {
      const history = await api.getMeasurementHistory()
      setMeasurementHistory(history)
    } catch (err) {
      // Ignore errors for history
    }
  }, [])

  const loadNHIDetection = useCallback(async () => {
    try {
      const detection = await api.getNHIDetection()
      setNHIDetection(detection)
    } catch (err) {
      // Ignore errors for NHI detection
    }
  }, [])

  useEffect(() => {
    loadStatus()
    loadHealthStatus()
    loadMeasurementHistory()
    loadMeasurementEnvelope()
    loadNHIDetection()

    // Poll for status updates
    const interval = setInterval(() => {
      loadStatus()
      loadMeasurementHistory()
      loadMeasurementEnvelope()
      loadNHIDetection()
    }, 1000)

    return () => clearInterval(interval)
  }, [loadStatus, loadHealthStatus, loadMeasurementHistory, loadMeasurementEnvelope, loadNHIDetection])

  const handleInitialize = async () => {
    setLoading(true)
    setError(null)
    try {
      await api.initialize()
      await loadStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize hardware')
    } finally {
      setLoading(false)
    }
  }

  const handleArm = async () => {
    setLoading(true)
    setError(null)
    try {
      await api.arm()
      await loadStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to arm system')
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmArm = async () => {
    setLoading(true)
    setError(null)
    try {
      await api.confirmArm()
      await loadStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to confirm arm')
    } finally {
      setLoading(false)
    }
  }

  const handleEmit = async (patternType: string, message?: string, geometricType?: string, size?: number) => {
    setLoading(true)
    setError(null)
    try {
      await api.emit(patternType, message, geometricType, size)
      await loadStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to emit pattern')
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    setLoading(true)
    setError(null)
    try {
      await api.stop()
      await loadStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop system')
    } finally {
      setLoading(false)
    }
  }

  const handleHealthCheck = async () => {
    setLoading(true)
    setError(null)
    try {
      const health = await api.runHealthCheck()
      setHealthStatus(health)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run health check')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔭 EUV Detection & Laser Communication Device</h1>
      </header>

      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="app-content">
        <Sidebar
          status={status}
          healthStatus={healthStatus}
          onInitialize={handleInitialize}
          onHealthCheck={handleHealthCheck}
          loading={loading}
        />

        <main className="main-content">
          <div className="content-grid">
            <div className="content-left">
              <WavelengthMeasurement
                status={status}
                measurementHistory={measurementHistory}
                measurementEnvelope={measurementEnvelope}
                onStart={() => api.startMeasurement()}
                onStop={() => api.stopMeasurement()}
                onCalibrateDark={async () => {
                  try {
                    await api.calibrateDark()
                  } catch (err) {
                    setError(err instanceof Error ? err.message : 'Failed to calibrate dark voltage')
                  }
                }}
              />
              <NHIDetectionPanel
                detection={nhiDetection}
                sessionStatus={sessionStatus}
                onSendResponse={async () => {
                  setLoading(true)
                  setError(null)
                  try {
                    await api.sendNHIResponse()
                    await loadStatus()
                  } catch (err) {
                    setError(err instanceof Error ? err.message : 'Send response failed')
                  } finally {
                    setLoading(false)
                  }
                }}
                loading={loading}
              />
            </div>

            <div className="content-right">
              <LaserControl
                status={status}
                sessionStatus={sessionStatus}
                onInitialize={handleInitialize}
                onArm={handleArm}
                onConfirmArm={handleConfirmArm}
                onEmit={handleEmit}
                onStop={handleStop}
                onEmergencyStop={async () => {
                  try {
                    await api.emergencyStop()
                    await loadStatus()
                  } catch (err) {
                    setError(err instanceof Error ? err.message : 'Failed to emergency stop')
                  }
                }}
                onSendPulse={async (duration) => {
                  try {
                    await api.sendPulse(duration)
                    await loadStatus()
                  } catch (err) {
                    setError(err instanceof Error ? err.message : 'Failed to send pulse')
                  }
                }}
                onSendPattern={async (patternType, message, geometricType, size) => {
                  try {
                    await api.sendPattern(patternType, message, geometricType, size)
                    await loadStatus()
                  } catch (err) {
                    setError(err instanceof Error ? err.message : 'Failed to send pattern')
                  }
                }}
              />
            </div>
          </div>
        </main>
      </div>

      <footer className="app-footer">
        <p>EUV Detection & Laser Communication Device v1.0 | Class 1M Laser | Australian Compliant</p>
      </footer>
    </div>
  )
}

export default App

