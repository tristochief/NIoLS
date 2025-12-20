import React, { useState } from 'react'
import { Status, SessionStatus, FSMState } from '../api'
import './LaserControl.css'

interface LaserControlProps {
  status: Status | null
  sessionStatus: SessionStatus | null
  onInitialize: () => Promise<void>
  onArm: () => Promise<void>
  onConfirmArm: () => Promise<void>
  onEmit: (
    patternType: string,
    message?: string,
    geometricType?: string,
    size?: number
  ) => Promise<void>
  onStop: () => Promise<void>
  onEmergencyStop: () => Promise<void>
  onSendPulse: (duration: number) => Promise<void>
  onSendPattern: (
    patternType: string,
    message?: string,
    geometricType?: string,
    size?: number
  ) => Promise<void>
}

const LaserControl: React.FC<LaserControlProps> = ({
  status,
  sessionStatus,
  onInitialize,
  onArm,
  onConfirmArm,
  onEmit,
  onStop,
  onEmergencyStop,
  onSendPulse,
  onSendPattern,
}) => {
  const [patternType, setPatternType] = useState('morse')
  const [message, setMessage] = useState('SOS')
  const [geometricType, setGeometricType] = useState('square')
  const [patternSize, setPatternSize] = useState(10)
  const [pulseDuration, setPulseDuration] = useState(0.1)

  const fsmState: FSMState = sessionStatus?.state || status?.state || 'SAFE'
  const budget = sessionStatus?.budget
  const laserState = status?.laser.state || 'off'
  const interlockSafe = status?.laser.interlock_safe

  // FSM state-based UI
  const renderFSMControls = () => {
    switch (fsmState) {
      case 'SAFE':
        return (
          <div className="fsm-controls">
            <button className="btn btn-primary" onClick={onInitialize}>
              Initialize System
            </button>
            <div className="state-info">System is in SAFE state. Initialize to begin.</div>
          </div>
        )
      
      case 'INITIALIZED':
        return (
          <div className="fsm-controls">
            <button className="btn btn-primary" onClick={onArm}>
              Arm System
            </button>
            <button className="btn btn-secondary" onClick={onStop}>
              Stop (Return to SAFE)
            </button>
            <div className="state-info">
              System initialized. Config and calibration hashes bound.
              {sessionStatus?.config_hash && (
                <div className="hash-info">Config: {sessionStatus.config_hash.substring(0, 16)}...</div>
              )}
            </div>
          </div>
        )
      
      case 'ARMED':
        return (
          <div className="fsm-controls">
            <button className="btn btn-primary" onClick={onConfirmArm}>
              Confirm Arm (Enter EMIT_READY)
            </button>
            <button className="btn btn-secondary" onClick={onStop}>
              Stop (Return to INITIALIZED)
            </button>
            <div className="state-info">
              System armed. Confirm within arming window to proceed.
            </div>
          </div>
        )
      
      case 'EMIT_READY':
        return (
          <div className="fsm-controls">
            <button className="btn btn-secondary" onClick={onStop}>
              Stop (Return to ARMED)
            </button>
            {budget && (
              <div className="budget-info">
                <h4>Emission Budget</h4>
                <div>Remaining time: {(budget.remaining_emit_ms / 1000).toFixed(1)} s</div>
                <div>Remaining duty: {budget.remaining_duty_percent.toFixed(1)}%</div>
                <div>Cooldown: {(budget.cooldown_remaining_ms / 1000).toFixed(1)} s</div>
              </div>
            )}
            <div className="state-info">System ready for emission. Use pattern controls below.</div>
          </div>
        )
      
      case 'EMITTING':
        return (
          <div className="fsm-controls">
            <div className="state-info warning">⚠️ Emission in progress...</div>
            <button className="btn btn-secondary" onClick={onStop}>
              Stop Emission
            </button>
          </div>
        )
      
      case 'FAULT':
        return (
          <div className="fsm-controls">
            <div className="state-info error">❌ FAULT STATE</div>
            <button className="btn btn-danger" onClick={onStop}>
              Reset (Return to SAFE)
            </button>
            <div className="error">System in fault state. Reset required.</div>
          </div>
        )
      
      default:
        return null
    }
  }

  if (!status?.laser.initialized && fsmState === 'SAFE') {
    return (
      <div className="laser-control">
        <h2>Laser Control</h2>
        <div className="fsm-state-display">
          <strong>FSM State:</strong> {fsmState}
        </div>
        {renderFSMControls()}
      </div>
    )
  }

  if (interlockSafe === false && fsmState !== 'SAFE') {
    return (
      <div className="laser-control">
        <h2>Laser Control</h2>
        <div className="fsm-state-display">
          <strong>FSM State:</strong> {fsmState}
        </div>
        <div className="error">⚠️ Safety interlock is not engaged!</div>
        {renderFSMControls()}
      </div>
    )
  }

  return (
    <div className="laser-control">
      <h2>Laser Control</h2>

      <div className="fsm-state-display">
        <strong>FSM State:</strong> {fsmState}
      </div>

      {renderFSMControls()}

      <div className="laser-divider"></div>

      <div className="laser-state">
        <strong>Laser Hardware State:</strong> {laserState.toUpperCase()}
      </div>

      <button
        className="btn btn-danger"
        onClick={onEmergencyStop}
        style={{ width: '100%', marginBottom: '1.5rem' }}
      >
        Emergency Stop
      </button>

      <div className="laser-divider"></div>

      <div className="pattern-section">
        <h3>Send Pattern</h3>

        <div className="form-group">
          <label>Pattern Type</label>
          <select
            value={patternType}
            onChange={(e) => setPatternType(e.target.value)}
          >
            <option value="morse">Morse</option>
            <option value="binary">Binary</option>
            <option value="geometric">Geometric</option>
          </select>
        </div>

        {patternType === 'geometric' ? (
          <>
            <div className="form-group">
              <label>Geometric Pattern</label>
              <select
                value={geometricType}
                onChange={(e) => setGeometricType(e.target.value)}
              >
                <option value="square">Square</option>
                <option value="circle">Circle</option>
                <option value="triangle">Triangle</option>
                <option value="spiral">Spiral</option>
              </select>
            </div>
            <div className="form-group">
              <label>Pattern Size: {patternSize}</label>
              <input
                type="range"
                min="5"
                max="50"
                value={patternSize}
                onChange={(e) => setPatternSize(parseInt(e.target.value))}
              />
            </div>
            <button
              className="btn btn-primary"
              onClick={() =>
                fsmState === 'EMIT_READY' 
                  ? onEmit(patternType, undefined, geometricType, patternSize)
                  : onSendPattern(patternType, undefined, geometricType, patternSize)
              }
              disabled={fsmState !== 'EMIT_READY'}
            >
              Send Geometric Pattern
            </button>
          </>
        ) : (
          <>
            <div className="form-group">
              <label>Message</label>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Enter message"
              />
            </div>
            <button
              className="btn btn-primary"
              onClick={() =>
                fsmState === 'EMIT_READY'
                  ? onEmit(patternType, message)
                  : onSendPattern(patternType, message)
              }
              disabled={fsmState !== 'EMIT_READY'}
            >
              Send Message
            </button>
          </>
        )}
      </div>

      <div className="laser-divider"></div>

      <div className="pulse-section">
        <h3>Single Pulse</h3>
        <div className="form-group">
          <label>Pulse Duration (s): {pulseDuration.toFixed(3)}</label>
          <input
            type="range"
            min="0.001"
            max="1.0"
            step="0.001"
            value={pulseDuration}
            onChange={(e) => setPulseDuration(parseFloat(e.target.value))}
          />
        </div>
        <button
          className="btn btn-primary"
          onClick={() => onSendPulse(pulseDuration)}
        >
          Send Pulse
        </button>
      </div>
    </div>
  )
}

export default LaserControl

