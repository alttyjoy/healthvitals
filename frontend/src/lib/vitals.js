export const VITAL_TYPES = [
  { key: 'blood_glucose', name: 'Blood Glucose', unit: 'mg/dL', icon: 'Drop', color: '#2D4A3E', min: 20, max: 600, normalMin: 70, normalMax: 140, chartType: 'line' },
  { key: 'blood_oxygen', name: 'Blood Oxygen', unit: '%', icon: 'Wind', color: '#D96C4E', min: 70, max: 100, normalMin: 95, normalMax: 100, chartType: 'area' },
  { key: 'blood_pressure', name: 'Blood Pressure', unit: 'mmHg', icon: 'Heartbeat', color: '#8CB369', min: 60, max: 250, normalMin: 90, normalMax: 140, chartType: 'dual_line', hasDualValue: true, value2Label: 'Diastolic', value2Min: 40, value2Max: 150 },
  { key: 'bmi', name: 'BMI', unit: 'kg/m2', icon: 'User', color: '#E9C46A', min: 10, max: 60, normalMin: 18.5, normalMax: 24.9, chartType: 'line' },
  { key: 'body_temperature', name: 'Body Temperature', unit: 'F', icon: 'Thermometer', color: '#F4A261', min: 90, max: 110, normalMin: 97, normalMax: 99.5, chartType: 'line' },
  { key: 'heart_rate', name: 'Heart Rate', unit: 'bpm', icon: 'Heartbeat', color: '#A3B18A', min: 30, max: 250, normalMin: 60, normalMax: 100, chartType: 'line' },
  { key: 'respiratory_rate', name: 'Respiratory Rate', unit: 'breaths/min', icon: 'Wind', color: '#588157', min: 5, max: 60, normalMin: 12, normalMax: 20, chartType: 'line' },
  { key: 'sleep_duration', name: 'Sleep Duration', unit: 'hours', icon: 'Moon', color: '#3A5A40', min: 0, max: 24, normalMin: 7, normalMax: 9, chartType: 'bar' },
  { key: 'physical_activity', name: 'Physical Activity', unit: 'minutes', icon: 'PersonSimpleRun', color: '#2D4A3E', min: 0, max: 1440, normalMin: 30, normalMax: 120, chartType: 'bar' },
  { key: 'waist_circumference', name: 'Waist Circumference', unit: 'cm', icon: 'Ruler', color: '#D96C4E', min: 40, max: 200, normalMin: 60, normalMax: 102, chartType: 'line' },
  { key: 'weight', name: 'Weight', unit: 'kg', icon: 'Scales', color: '#8CB369', min: 20, max: 300, normalMin: 50, normalMax: 100, chartType: 'line' },
  { key: 'hydration', name: 'Hydration Level', unit: 'glasses', icon: 'Drop', color: '#E9C46A', min: 0, max: 30, normalMin: 8, normalMax: 15, chartType: 'bar' },
];

export const VITAL_MAP = Object.fromEntries(VITAL_TYPES.map(v => [v.key, v]));

export function getVitalStatus(key, value) {
  const vital = VITAL_MAP[key];
  if (!vital || value == null) return 'none';
  if (value >= vital.normalMin && value <= vital.normalMax) return 'normal';
  if (value < vital.min || value > vital.max) return 'critical';
  return 'warning';
}

export function getStatusColor(status) {
  switch (status) {
    case 'normal': return '#588157';
    case 'warning': return '#E9C46A';
    case 'critical': return '#D96C4E';
    default: return '#6E6E6A';
  }
}
