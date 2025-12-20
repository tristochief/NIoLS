/**
 * API client for backend communication
 */

const API_BASE = '/api';

// FSM State types
export type FSMState = 'SAFE' | 'INITIALIZED' | 'ARMED' | 'EMIT_READY' | 'EMITTING' | 'FAULT';

// Envelope types
export interface WavelengthEnvelope {
  min_nm: number;
  max_nm: number;
  confidence?: number;
  valid_until?: number;
}

export interface VoltageEnvelope {
  min_v: number;
  max_v: number;
  rms_noise?: number;
}

export interface MeasurementQuality {
  snr_estimate?: number;
  saturation_flag: boolean;
  clipping_flag: boolean;
}

export interface MeasurementEnvelope {
  wavelength_envelope_nm?: WavelengthEnvelope;
  voltage_envelope_v?: VoltageEnvelope;
  measurement_quality?: MeasurementQuality;
}

export interface BudgetEnvelope {
  remaining_emit_ms: number;
  remaining_duty_percent: number;
  cooldown_remaining_ms: number;
}

export interface SessionStatus {
  state: FSMState;
  budget: BudgetEnvelope;
  config_hash?: string;
  cal_hash?: string;
  constraints?: Record<string, any>;
}

// Legacy status interface for backward compatibility
export interface Status {
  photodiode: {
    initialized: boolean;
    connected: boolean;
    mode: string;
  };
  laser: {
    initialized: boolean;
    connected: boolean;
    mode: string;
    state: string | null;
    interlock_safe: boolean | null;
  };
  measurement: {
    running: boolean;
    last_measurement: {
      wavelength: number | null;
      voltage: number;
    };
  };
  state?: FSMState;
  budget?: BudgetEnvelope;
}

export interface HealthCheck {
  name: string;
  status: string;
  message: string;
  details?: any;
}

export interface HealthStatus {
  overall_status: string;
  overall_message: string;
  checks: HealthCheck[];
}

export interface MeasurementHistory {
  wavelengths: number[];
  voltages: number[];
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export const api = {
  // FSM-based endpoints
  async initialize(): Promise<{ 
    status: string; 
    message: string; 
    state: FSMState;
    config_hash: string;
    cal_hash: string;
    session_id: string;
  }> {
    return fetchAPI('/initialize', { method: 'POST' });
  },

  async arm(): Promise<{ status: string; message: string; state: FSMState }> {
    return fetchAPI('/arm', { method: 'POST' });
  },

  async confirmArm(): Promise<{ status: string; message: string; state: FSMState }> {
    return fetchAPI('/arm/confirm', { method: 'POST' });
  },

  async stop(): Promise<{ status: string; message: string; state: FSMState }> {
    return fetchAPI('/stop', { method: 'POST' });
  },

  async emit(
    patternType: string,
    message?: string,
    geometricType?: string,
    size?: number
  ): Promise<{ 
    status: string; 
    message: string; 
    emit_envelope: {
      power_mw_max: number;
      duty_cycle_max: number;
      duration_ms: number;
    };
    trace_seq?: number;
  }> {
    return fetchAPI('/emit', {
      method: 'POST',
      body: JSON.stringify({
        pattern_type: patternType,
        message,
        geometric_type: geometricType,
        size,
      }),
    });
  },

  async getStatus(): Promise<SessionStatus> {
    return fetchAPI('/status');
  },

  async startMeasurement(): Promise<{ status: string }> {
    return fetchAPI('/measurement/start', { method: 'POST' });
  },

  async stopMeasurement(): Promise<{ status: string }> {
    return fetchAPI('/measurement/stop', { method: 'POST' });
  },

  async calibrateDark(): Promise<{ status: string; dark_voltage: number }> {
    return fetchAPI('/measurement/calibrate-dark', { method: 'POST' });
  },

  async getCurrentMeasurement(): Promise<MeasurementEnvelope> {
    return fetchAPI('/measurement/current');
  },

  async getMeasurementHistory(): Promise<MeasurementHistory> {
    return fetchAPI('/measurement/history');
  },

  async enableLaser(): Promise<{ status: string; message: string }> {
    return fetchAPI('/laser/enable', { method: 'POST' });
  },

  async disableLaser(): Promise<{ status: string; message: string }> {
    return fetchAPI('/laser/disable', { method: 'POST' });
  },

  async emergencyStop(): Promise<{ status: string; message: string }> {
    return fetchAPI('/laser/emergency-stop', { method: 'POST' });
  },

  async sendPulse(duration: number): Promise<{ status: string; message: string }> {
    return fetchAPI('/laser/pulse', {
      method: 'POST',
      body: JSON.stringify({ duration }),
    });
  },

  async sendPattern(
    patternType: string,
    message?: string,
    geometricType?: string,
    size?: number
  ): Promise<{ status: string; message: string }> {
    return fetchAPI('/laser/pattern', {
      method: 'POST',
      body: JSON.stringify({
        pattern_type: patternType,
        message,
        geometric_type: geometricType,
        size,
      }),
    });
  },

  async runHealthCheck(): Promise<HealthStatus> {
    return fetchAPI('/health/check', { method: 'POST' });
  },

  async getHealthStatus(): Promise<HealthStatus> {
    return fetchAPI('/health/status');
  },

  async getSessionBundle(): Promise<{ session_id: string; session_dir: string }> {
    return fetchAPI('/session/bundle');
  },

  // Legacy endpoints (for backward compatibility)
  async sendPattern(
    patternType: string,
    message?: string,
    geometricType?: string,
    size?: number
  ): Promise<{ status: string; message: string }> {
    // Redirect to emit endpoint
    return this.emit(patternType, message, geometricType, size);
  },
};

