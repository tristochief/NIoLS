import React, { useEffect, useRef } from 'react'
import Plot from 'react-plotly.js'
import { Status, MeasurementHistory, MeasurementEnvelope } from '../api'
import './WavelengthMeasurement.css'

interface WavelengthMeasurementProps {
  status: Status | null
  measurementHistory: MeasurementHistory
  measurementEnvelope: MeasurementEnvelope | null
  onStart: () => Promise<void>
  onStop: () => Promise<void>
  onCalibrateDark: () => Promise<void>
}

const WavelengthMeasurement: React.FC<WavelengthMeasurementProps> = ({
  status,
  measurementHistory,
  measurementEnvelope,
  onStart,
  onStop,
  onCalibrateDark,
}) => {
  const wavelengthPlotRef = useRef<HTMLDivElement>(null)
  const voltagePlotRef = useRef<HTMLDivElement>(null)

  const isRunning = status?.measurement.running || false
  
  // Display envelope bounds instead of point values
  const wavelengthEnv = measurementEnvelope?.wavelength_envelope_nm
  const voltageEnv = measurementEnvelope?.voltage_envelope_v
  const quality = measurementEnvelope?.measurement_quality

  const wavelengthLayout = {
    title: 'Wavelength History',
    xaxis: { title: 'Measurement' },
    yaxis: { title: 'Wavelength (nm)' },
    height: 300,
    margin: { l: 60, r: 20, t: 40, b: 40 },
  }

  const voltageLayout = {
    title: 'Voltage History',
    xaxis: { title: 'Measurement' },
    yaxis: { title: 'Voltage (V)' },
    height: 300,
    margin: { l: 60, r: 20, t: 40, b: 40 },
  }

  return (
    <div className="wavelength-measurement">
      <h2>Wavelength Measurement</h2>

      <div className="measurement-controls">
        <button
          className="btn btn-primary"
          onClick={onStart}
          disabled={isRunning || !status?.photodiode.initialized}
        >
          Start Measurement
        </button>
        <button
          className="btn btn-secondary"
          onClick={onStop}
          disabled={!isRunning}
        >
          Stop Measurement
        </button>
        <button
          className="btn btn-secondary"
          onClick={onCalibrateDark}
          disabled={!status?.photodiode.initialized}
        >
          Calibrate Dark
        </button>
      </div>

      <div className="measurement-metrics">
        <div className="metric">
          <div className="metric-label">Wavelength Envelope</div>
          <div className="metric-value">
            {wavelengthEnv
              ? `${wavelengthEnv.min_nm.toFixed(1)} - ${wavelengthEnv.max_nm.toFixed(1)} nm`
              : 'N/A'}
          </div>
          {wavelengthEnv && wavelengthEnv.confidence && (
            <div className="metric-confidence">
              ({Math.round(wavelengthEnv.confidence * 100)}% confidence)
            </div>
          )}
        </div>
        <div className="metric">
          <div className="metric-label">Voltage Envelope</div>
          <div className="metric-value">
            {voltageEnv
              ? `${voltageEnv.min_v.toFixed(4)} - ${voltageEnv.max_v.toFixed(4)} V`
              : 'N/A'}
          </div>
          {voltageEnv && voltageEnv.rms_noise && (
            <div className="metric-noise">
              (RMS noise: {voltageEnv.rms_noise.toFixed(6)} V)
            </div>
          )}
        </div>
        {quality && (
          <div className="metric-quality">
            {quality.snr_estimate && (
              <div>SNR: {quality.snr_estimate.toFixed(1)}</div>
            )}
            {quality.saturation_flag && (
              <div className="warning">⚠️ Saturation detected</div>
            )}
            {quality.clipping_flag && (
              <div className="warning">⚠️ Clipping detected</div>
            )}
          </div>
        )}
      </div>

      {measurementHistory.wavelengths.length > 0 && (
        <div className="plot-container" ref={wavelengthPlotRef}>
          <Plot
            data={[
              {
                y: measurementHistory.wavelengths,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Wavelength (nm)',
                line: { color: 'blue' },
              },
            ]}
            layout={wavelengthLayout}
            style={{ width: '100%', height: '100%' }}
            config={{ responsive: true }}
          />
        </div>
      )}

      {measurementHistory.voltages.length > 0 && (
        <div className="plot-container" ref={voltagePlotRef}>
          <Plot
            data={[
              {
                y: measurementHistory.voltages,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Voltage (V)',
                line: { color: 'green' },
              },
            ]}
            layout={voltageLayout}
            style={{ width: '100%', height: '100%' }}
            config={{ responsive: true }}
          />
        </div>
      )}
    </div>
  )
}

export default WavelengthMeasurement

