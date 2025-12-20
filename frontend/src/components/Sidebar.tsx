import React, { useState } from 'react'
import { Status, HealthStatus } from '../api'
import './Sidebar.css'

interface SidebarProps {
  status: Status | null
  healthStatus: HealthStatus | null
  onInitialize: () => void
  onHealthCheck: () => void
  loading: boolean
}

const Sidebar: React.FC<SidebarProps> = ({
  status,
  healthStatus,
  onInitialize,
  onHealthCheck,
  loading,
}) => {
  const [expandedChecks, setExpandedChecks] = useState(false)

  const getStatusIcon = (mode: string) => {
    if (mode === 'connected') return '✅'
    if (mode === 'simulation') return '⚠️'
    return '❌'
  }

  const getHealthIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return '✓'
      case 'warning':
        return '⚠'
      case 'error':
        return '✗'
      case 'critical':
        return '🚨'
      default:
        return '?'
    }
  }

  const getHealthClass = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'health-healthy'
      case 'warning':
        return 'health-warning'
      case 'error':
        return 'health-error'
      case 'critical':
        return 'health-critical'
      default:
        return ''
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <h2>System Status</h2>

        <button
          className="btn btn-primary"
          onClick={onInitialize}
          disabled={loading}
        >
          Initialize Hardware
        </button>

        <div className="status-list">
          <div className="status-item">
            <strong>Photodiode:</strong>{' '}
            {status
              ? `${getStatusIcon(status.photodiode.mode)} ${
                  status.photodiode.mode === 'connected'
                    ? 'Connected'
                    : status.photodiode.mode === 'simulation'
                    ? 'Simulation Mode'
                    : 'Not Initialized'
                }`
              : '❌ Not Initialized'}
          </div>

          <div className="status-item">
            <strong>Laser:</strong>{' '}
            {status
              ? `${getStatusIcon(status.laser.mode)} ${
                  status.laser.mode === 'connected'
                    ? 'Connected'
                    : status.laser.mode === 'simulation'
                    ? 'Simulation Mode'
                    : 'Not Initialized'
                }`
              : '❌ Not Initialized'}
          </div>

          {status?.laser.interlock_safe !== null && (
            <div className="status-item">
              {status.laser.interlock_safe ? (
                <span className="interlock-safe">🔒 Interlock: SAFE</span>
              ) : (
                <span className="interlock-unsafe">🔓 Interlock: UNSAFE</span>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="sidebar-divider"></div>

      <div className="sidebar-section">
        <h3>System Health</h3>

        <button
          className="btn btn-secondary"
          onClick={onHealthCheck}
          disabled={loading}
        >
          Run Health Check
        </button>

        {healthStatus && (
          <div className="health-status">
            <div className={`health-overall ${getHealthClass(healthStatus.overall_status)}`}>
              {getHealthIcon(healthStatus.overall_status)}{' '}
              {healthStatus.overall_status === 'critical' && 'CRITICAL: '}
              {healthStatus.overall_message}
            </div>

            <details className="health-details">
              <summary onClick={() => setExpandedChecks(!expandedChecks)}>
                Detailed Health Checks
              </summary>
              <div className="health-checks">
                {healthStatus.checks.map((check, idx) => (
                  <div key={idx} className="health-check-item">
                    <span className={`health-icon ${getHealthClass(check.status)}`}>
                      {getHealthIcon(check.status)}
                    </span>
                    <div>
                      <strong>{check.name}</strong>: {check.message}
                      {check.details && (
                        <pre className="health-details-json">
                          {JSON.stringify(check.details, null, 2)}
                        </pre>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </details>
          </div>
        )}
      </div>

      <div className="sidebar-divider"></div>

      <div className="sidebar-section">
        <div className="safety-warning">
          <strong>⚠️ Safety Reminders:</strong>
          <ul>
            <li>Never point laser at people or aircraft</li>
            <li>Ensure interlock is engaged before operation</li>
            <li>Class 1M laser: ≤1 mW output</li>
            <li>Follow all safety protocols</li>
          </ul>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar

