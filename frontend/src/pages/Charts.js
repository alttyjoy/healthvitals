import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '@/lib/api';
import { VITAL_TYPES, VITAL_MAP } from '@/lib/vitals';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Legend
} from 'recharts';
import { ChartLine, TrendUp, TrendDown, Minus } from '@phosphor-icons/react';

const CHART_COLORS = ['#2D4A3E', '#D96C4E', '#8CB369', '#E9C46A', '#F4A261', '#A3B18A'];

const DATE_RANGES = [
  { label: '7 Days', days: 7 },
  { label: '14 Days', days: 14 },
  { label: '30 Days', days: 30 },
  { label: '90 Days', days: 90 },
];

export default function Charts() {
  const { vitalKey: paramKey } = useParams();
  const [selectedVital, setSelectedVital] = useState(paramKey || '');
  const [enabledVitals, setEnabledVitals] = useState([]);
  const [chartData, setChartData] = useState(null);
  const [dateRange, setDateRange] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/vitals/enabled').then(res => {
      const ev = res.data.enabled_vitals || [];
      setEnabledVitals(ev);
      if (!selectedVital && ev.length > 0) setSelectedVital(ev[0]);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedVital) return;
    const end = new Date().toISOString().split('T')[0];
    const start = new Date(Date.now() - dateRange * 86400000).toISOString().split('T')[0];
    setLoading(true);
    api.get(`/charts/${selectedVital}?start_date=${start}&end_date=${end}`)
      .then(res => setChartData(res.data))
      .catch(() => setChartData(null))
      .finally(() => setLoading(false));
  }, [selectedVital, dateRange]);

  const vital = VITAL_MAP[selectedVital];
  const stats = chartData?.stats || {};

  const renderChart = () => {
    if (!chartData || !chartData.entries?.length) {
      return (
        <div className="flex flex-col items-center justify-center py-20 text-[#6E6E6A]">
          <ChartLine weight="duotone" className="w-12 h-12 mb-3 opacity-50" />
          <p className="text-sm">No data for this period. Start tracking!</p>
        </div>
      );
    }
    const data = chartData.entries.map(e => ({
      date: new Date(e.date + 'T00:00:00').toLocaleDateString('en', { month: 'short', day: 'numeric' }),
      value: e.value,
      value2: e.value2,
    }));
    const normalMin = vital?.normalMin;
    const normalMax = vital?.normalMax;
    const chartType = vital?.chartType || 'line';
    const commonProps = {
      data, margin: { top: 10, right: 10, left: -10, bottom: 0 },
    };

    if (chartType === 'bar') {
      return (
        <ResponsiveContainer width="100%" height={350}>
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#EAE7E1" />
            <XAxis dataKey="date" fontSize={11} tick={{ fill: '#6E6E6A' }} />
            <YAxis fontSize={11} tick={{ fill: '#6E6E6A' }} />
            <Tooltip contentStyle={{ background: 'rgba(255,255,255,0.95)', border: '1px solid #EAE7E1', borderRadius: 12, boxShadow: '0 8px 32px rgba(0,0,0,0.08)' }} />
            {normalMin != null && <ReferenceLine y={normalMin} stroke="#588157" strokeDasharray="4 4" label={{ value: 'Min', fill: '#588157', fontSize: 10 }} />}
            {normalMax != null && <ReferenceLine y={normalMax} stroke="#D96C4E" strokeDasharray="4 4" label={{ value: 'Max', fill: '#D96C4E', fontSize: 10 }} />}
            <Bar dataKey="value" fill={vital?.color || CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      );
    }
    if (chartType === 'area') {
      return (
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#EAE7E1" />
            <XAxis dataKey="date" fontSize={11} tick={{ fill: '#6E6E6A' }} />
            <YAxis fontSize={11} tick={{ fill: '#6E6E6A' }} />
            <Tooltip contentStyle={{ background: 'rgba(255,255,255,0.95)', border: '1px solid #EAE7E1', borderRadius: 12 }} />
            {normalMin != null && <ReferenceLine y={normalMin} stroke="#588157" strokeDasharray="4 4" />}
            <Area type="monotone" dataKey="value" stroke={vital?.color || CHART_COLORS[0]} fill={`${vital?.color || CHART_COLORS[0]}20`} strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      );
    }
    if (chartType === 'dual_line') {
      return (
        <ResponsiveContainer width="100%" height={350}>
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#EAE7E1" />
            <XAxis dataKey="date" fontSize={11} tick={{ fill: '#6E6E6A' }} />
            <YAxis fontSize={11} tick={{ fill: '#6E6E6A' }} />
            <Tooltip contentStyle={{ background: 'rgba(255,255,255,0.95)', border: '1px solid #EAE7E1', borderRadius: 12 }} />
            <Legend />
            <Line type="monotone" dataKey="value" name="Systolic" stroke={CHART_COLORS[0]} strokeWidth={2} dot={{ r: 3 }} />
            <Line type="monotone" dataKey="value2" name="Diastolic" stroke={CHART_COLORS[1]} strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      );
    }
    // Default line chart
    return (
      <ResponsiveContainer width="100%" height={350}>
        <LineChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" stroke="#EAE7E1" />
          <XAxis dataKey="date" fontSize={11} tick={{ fill: '#6E6E6A' }} />
          <YAxis fontSize={11} tick={{ fill: '#6E6E6A' }} />
          <Tooltip contentStyle={{ background: 'rgba(255,255,255,0.95)', border: '1px solid #EAE7E1', borderRadius: 12 }} />
          {normalMin != null && <ReferenceLine y={normalMin} stroke="#588157" strokeDasharray="4 4" label={{ value: 'Normal Min', fill: '#588157', fontSize: 10, position: 'left' }} />}
          {normalMax != null && <ReferenceLine y={normalMax} stroke="#D96C4E" strokeDasharray="4 4" label={{ value: 'Normal Max', fill: '#D96C4E', fontSize: 10, position: 'left' }} />}
          <Line type="monotone" dataKey="value" stroke={vital?.color || CHART_COLORS[0]} strokeWidth={2.5} dot={{ r: 3, fill: vital?.color || CHART_COLORS[0] }} activeDot={{ r: 5 }} />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in-up" data-testid="charts-page">
      <div>
        <h1 className="text-2xl font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>Charts & Trends</h1>
        <p className="text-sm text-[#6E6E6A]">Visualize your health data over time</p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-3 items-center">
        <Select value={selectedVital} onValueChange={setSelectedVital}>
          <SelectTrigger className="w-[220px] rounded-xl border-[#EAE7E1] bg-white" data-testid="chart-vital-select">
            <SelectValue placeholder="Select vital" />
          </SelectTrigger>
          <SelectContent>
            {enabledVitals.map(vk => (
              <SelectItem key={vk} value={vk}>{VITAL_MAP[vk]?.name || vk}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="flex gap-1 bg-white border border-[#EAE7E1] rounded-xl p-1">
          {DATE_RANGES.map(r => (
            <Button
              key={r.days}
              variant={dateRange === r.days ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setDateRange(r.days)}
              data-testid={`chart-range-${r.days}`}
              className={`rounded-lg text-xs px-3 ${dateRange === r.days ? 'bg-[#2D4A3E] text-white' : 'text-[#6E6E6A]'}`}
            >
              {r.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white border border-[#EAE7E1] rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.02)]">
        {vital && (
          <div className="flex items-center gap-3 mb-4">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: vital.color }} />
            <h2 className="text-lg font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>{vital.name}</h2>
            <Badge className="bg-[#FAFAF9] text-[#6E6E6A] border border-[#EAE7E1] text-xs">{vital.unit}</Badge>
          </div>
        )}
        {loading ? (
          <div className="h-[350px] flex items-center justify-center"><div className="animate-pulse w-full h-full bg-[#FAFAF9] rounded-xl" /></div>
        ) : renderChart()}
      </div>

      {/* Stats */}
      {stats.count > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatBox label="Average" value={stats.avg} unit={vital?.unit} />
          <StatBox label="Minimum" value={stats.min} unit={vital?.unit} />
          <StatBox label="Maximum" value={stats.max} unit={vital?.unit} />
          <StatBox label="Readings" value={stats.count} unit="entries" />
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-xs text-[#6E6E6A] text-center mt-4">
        Charts are for informational tracking only. Consult your healthcare provider for medical advice.
      </p>
    </div>
  );
}

function StatBox({ label, value, unit }) {
  return (
    <div className="bg-white border border-[#EAE7E1] rounded-2xl p-4">
      <p className="text-xs text-[#6E6E6A] uppercase tracking-wide">{label}</p>
      <p className="text-xl font-semibold text-[#2C2C2A] mt-1" style={{ fontFamily: 'Outfit' }}>
        {value} <span className="text-xs font-normal text-[#6E6E6A]">{unit}</span>
      </p>
    </div>
  );
}
