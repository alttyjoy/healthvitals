import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '@/lib/api';
import { VITAL_MAP } from '@/lib/vitals';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Legend
} from 'recharts';
import { ChartLine, TrendUp, TrendDown, Minus, ArrowUp, ArrowDown } from '@phosphor-icons/react';

const CHART_COLORS = ['#0EA5E9', '#EF4444', '#8CB369', '#E9C46A', '#F4A261', '#A3B18A'];

const DATE_RANGES = [
  { label: '7 Days', days: 7 },
  { label: '14 Days', days: 14 },
  { label: '30 Days', days: 30 },
  { label: '90 Days', days: 90 },
];

function TrendIndicator({ trend, changePercent }) {
  if (!trend || trend === 'stable') {
    return (
      <div className="flex items-center gap-1 text-[#64748B]">
        <Minus weight="bold" className="w-4 h-4" />
        <span className="text-xs font-medium">Stable</span>
      </div>
    );
  }
  const isUp = trend === 'rising';
  const color = isUp ? '#EF4444' : '#10B981';
  const Icon = isUp ? ArrowUp : ArrowDown;
  return (
    <div className="flex items-center gap-1" style={{ color }}>
      <Icon weight="bold" className="w-4 h-4" />
      <span className="text-xs font-semibold">
        {changePercent != null ? `${Math.abs(changePercent)}%` : (isUp ? 'Rising' : 'Falling')}
      </span>
    </div>
  );
}

export default function Charts() {
  const { vitalKey: paramKey } = useParams();
  const [selectedVital, setSelectedVital] = useState(paramKey || '');
  const [enabledVitals, setEnabledVitals] = useState([]);
  const [chartData, setChartData] = useState(null);
  const [dateRange, setDateRange] = useState(30);
  const [loading, setLoading] = useState(true);
  const [showCompare, setShowCompare] = useState(false);

  useEffect(() => {
    api.get('/vitals/enabled').then(res => {
      const ev = res.data.enabled_vitals || [];
      setEnabledVitals(ev);
      if (!selectedVital && ev.length > 0) setSelectedVital(ev[0]);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!selectedVital) return;
    const end = new Date().toISOString().split('T')[0];
    const start = new Date(Date.now() - dateRange * 86400000).toISOString().split('T')[0];
    setLoading(true);
    api.get(`/charts/${selectedVital}?start_date=${start}&end_date=${end}&compare=${showCompare}`)
      .then(res => setChartData(res.data))
      .catch(() => setChartData(null))
      .finally(() => setLoading(false));
  }, [selectedVital, dateRange, showCompare]);

  const vital = VITAL_MAP[selectedVital];
  const stats = chartData?.stats || {};
  const prevStats = chartData?.previous_stats || {};
  const changePercent = chartData?.change_percent;
  const trend = chartData?.trend;

  const renderChart = () => {
    if (!chartData || !chartData.entries?.length) {
      return (
        <div className="flex flex-col items-center justify-center py-20 text-[#64748B]">
          <ChartLine weight="duotone" className="w-12 h-12 mb-3 opacity-50" />
          <p className="text-sm">No data for this period. Start tracking!</p>
        </div>
      );
    }
    // Merge current and previous period data for comparison
    const currentEntries = chartData.entries.map(e => ({
      date: new Date(e.date + 'T00:00:00').toLocaleDateString('en', { month: 'short', day: 'numeric' }),
      rawDate: e.date,
      value: e.value,
      value2: e.value2,
    }));

    let data = currentEntries;
    if (showCompare && chartData.previous_entries?.length > 0) {
      // Align previous entries by index (day offset) for overlay
      const prevMap = {};
      chartData.previous_entries.forEach((e, i) => {
        prevMap[i] = e.value;
      });
      data = currentEntries.map((entry, i) => ({
        ...entry,
        prev: prevMap[i] ?? null,
      }));
    }

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
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="date" fontSize={11} tick={{ fill: '#64748B' }} />
            <YAxis fontSize={11} tick={{ fill: '#64748B' }} />
            <Tooltip contentStyle={{ background: 'rgba(255,255,255,0.95)', border: '1px solid #E2E8F0', borderRadius: 12, boxShadow: '0 8px 32px rgba(0,0,0,0.08)' }} />
            <Legend />
            {normalMin != null && <ReferenceLine y={normalMin} stroke="#10B981" strokeDasharray="4 4" label={{ value: 'Min', fill: '#10B981', fontSize: 10 }} />}
            {normalMax != null && <ReferenceLine y={normalMax} stroke="#EF4444" strokeDasharray="4 4" label={{ value: 'Max', fill: '#EF4444', fontSize: 10 }} />}
            <Bar dataKey="value" name="Current" fill={vital?.color || CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
            {showCompare && <Bar dataKey="prev" name="Previous" fill="#CBD5E1" radius={[4, 4, 0, 0]} opacity={0.5} />}
          </BarChart>
        </ResponsiveContainer>
      );
    }
    if (chartType === 'area') {
      return (
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="date" fontSize={11} tick={{ fill: '#64748B' }} />
            <YAxis fontSize={11} tick={{ fill: '#64748B' }} />
            <Tooltip contentStyle={{ background: 'rgba(255,255,255,0.95)', border: '1px solid #E2E8F0', borderRadius: 12 }} />
            <Legend />
            {normalMin != null && <ReferenceLine y={normalMin} stroke="#10B981" strokeDasharray="4 4" />}
            <Area type="monotone" dataKey="value" name="Current" stroke={vital?.color || CHART_COLORS[0]} fill={`${vital?.color || CHART_COLORS[0]}20`} strokeWidth={2} />
            {showCompare && <Area type="monotone" dataKey="prev" name="Previous" stroke="#94A3B8" fill="#94A3B810" strokeWidth={1.5} strokeDasharray="4 4" />}
          </AreaChart>
        </ResponsiveContainer>
      );
    }
    if (chartType === 'dual_line') {
      return (
        <ResponsiveContainer width="100%" height={350}>
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="date" fontSize={11} tick={{ fill: '#64748B' }} />
            <YAxis fontSize={11} tick={{ fill: '#64748B' }} />
            <Tooltip contentStyle={{ background: 'rgba(255,255,255,0.95)', border: '1px solid #E2E8F0', borderRadius: 12 }} />
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
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
          <XAxis dataKey="date" fontSize={11} tick={{ fill: '#64748B' }} />
          <YAxis fontSize={11} tick={{ fill: '#64748B' }} />
          <Tooltip contentStyle={{ background: 'rgba(255,255,255,0.95)', border: '1px solid #E2E8F0', borderRadius: 12 }} />
          <Legend />
          {normalMin != null && <ReferenceLine y={normalMin} stroke="#10B981" strokeDasharray="4 4" label={{ value: 'Normal Min', fill: '#10B981', fontSize: 10, position: 'left' }} />}
          {normalMax != null && <ReferenceLine y={normalMax} stroke="#EF4444" strokeDasharray="4 4" label={{ value: 'Normal Max', fill: '#EF4444', fontSize: 10, position: 'left' }} />}
          <Line type="monotone" dataKey="value" name="Current" stroke={vital?.color || CHART_COLORS[0]} strokeWidth={2.5} dot={{ r: 3, fill: vital?.color || CHART_COLORS[0] }} activeDot={{ r: 5 }} />
          {showCompare && <Line type="monotone" dataKey="prev" name="Previous Period" stroke="#94A3B8" strokeWidth={1.5} strokeDasharray="5 5" dot={{ r: 2, fill: '#94A3B8' }} />}
        </LineChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in-up" data-testid="charts-page">
      <div>
        <h1 className="text-2xl font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Charts & Trends</h1>
        <p className="text-sm text-[#64748B]">Visualize your health data over time</p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-3 items-center">
        <Select value={selectedVital} onValueChange={setSelectedVital}>
          <SelectTrigger className="w-[220px] rounded-xl border-[#E2E8F0] bg-white" data-testid="chart-vital-select">
            <SelectValue placeholder="Select vital" />
          </SelectTrigger>
          <SelectContent>
            {enabledVitals.map(vk => (
              <SelectItem key={vk} value={vk}>{VITAL_MAP[vk]?.name || vk}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="flex gap-1 bg-white border border-[#E2E8F0] rounded-xl p-1">
          {DATE_RANGES.map(r => (
            <Button
              key={r.days}
              variant={dateRange === r.days ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setDateRange(r.days)}
              data-testid={`chart-range-${r.days}`}
              className={`rounded-lg text-xs px-3 ${dateRange === r.days ? 'bg-[#0EA5E9] text-white' : 'text-[#64748B]'}`}
            >
              {r.label}
            </Button>
          ))}
        </div>
        <div className="flex items-center gap-2 ml-auto bg-white border border-[#E2E8F0] rounded-xl px-3 py-1.5">
          <Switch checked={showCompare} onCheckedChange={setShowCompare} data-testid="compare-toggle" />
          <Label className="text-xs text-[#64748B] cursor-pointer" onClick={() => setShowCompare(!showCompare)}>Compare</Label>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
        {vital && (
          <div className="flex items-center gap-3 mb-4">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: vital.color }} />
            <h2 className="text-lg font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>{vital.name}</h2>
            <Badge className="bg-[#F8FAFC] text-[#64748B] border border-[#E2E8F0] text-xs">{vital.unit}</Badge>
            {trend && <TrendIndicator trend={trend} changePercent={changePercent} />}
          </div>
        )}
        {loading ? (
          <div className="h-[350px] flex items-center justify-center"><div className="animate-pulse w-full h-full bg-[#F8FAFC] rounded-xl" /></div>
        ) : renderChart()}
      </div>

      {/* Enhanced Stats with Period Comparison */}
      {stats.count > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4" data-testid="chart-stats">
          <CompareStatBox label="Average" current={stats.avg} previous={prevStats.avg} unit={vital?.unit} changePercent={changePercent} />
          <CompareStatBox label="Minimum" current={stats.min} previous={prevStats.min} unit={vital?.unit} />
          <CompareStatBox label="Maximum" current={stats.max} previous={prevStats.max} unit={vital?.unit} />
          <CompareStatBox label="Readings" current={stats.count} previous={prevStats.count} unit="entries" />
        </div>
      )}

      <p className="text-xs text-[#64748B] text-center mt-4">
        Charts are for informational tracking only. Consult your healthcare provider for medical advice.
      </p>
    </div>
  );
}

function CompareStatBox({ label, current, previous, unit, changePercent: overrideChange }) {
  let change = overrideChange;
  if (change == null && previous != null && previous !== 0 && current != null) {
    change = Math.round(((current - previous) / previous) * 100 * 10) / 10;
  }
  const isPositive = change > 0;
  const isNegative = change < 0;

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-4" data-testid={`stat-${label.toLowerCase()}`}>
      <p className="text-xs text-[#64748B] uppercase tracking-wide">{label}</p>
      <div className="flex items-end gap-1.5 mt-1">
        <p className="text-xl font-semibold text-[#0F172A] tabular-nums" style={{ fontFamily: 'Outfit' }}>{current}</p>
        <span className="text-xs font-normal text-[#64748B] pb-0.5">{unit}</span>
      </div>
      {previous != null && (
        <div className="flex items-center gap-1.5 mt-1.5">
          <span className="text-[10px] text-[#94A3B8]">Prev: {previous}</span>
          {change != null && change !== 0 && (
            <span className={`inline-flex items-center gap-0.5 text-[10px] font-semibold rounded-full px-1.5 py-0.5 ${isPositive ? 'bg-red-50 text-red-500' : isNegative ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-50 text-slate-500'}`}>
              {isPositive ? <ArrowUp weight="bold" className="w-2 h-2" /> : isNegative ? <ArrowDown weight="bold" className="w-2 h-2" /> : null}
              {Math.abs(change)}%
            </span>
          )}
        </div>
      )}
    </div>
  );
}
