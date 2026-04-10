import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api, { formatApiError } from '@/lib/api';
import { VITAL_MAP } from '@/lib/vitals';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Heartbeat, Lock, Warning } from '@phosphor-icons/react';

const CHART_COLORS = ['#2D4A3E', '#D96C4E', '#8CB369', '#E9C46A', '#F4A261', '#A3B18A'];

export default function SharedReportView() {
  const { token } = useParams();
  const [report, setReport] = useState(null);
  const [needsPassword, setNeedsPassword] = useState(false);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadReport(); }, [token]);

  const loadReport = async () => {
    try {
      const { data } = await api.get(`/shared-reports/view/${token}`);
      if (data.requires_password) {
        setNeedsPassword(true);
        setReport(data);
      } else {
        setReport(data);
        setNeedsPassword(false);
      }
    } catch (err) {
      setError(formatApiError(err));
    } finally { setLoading(false); }
  };

  const unlockReport = async () => {
    setError('');
    try {
      const { data } = await api.post(`/shared-reports/view/${token}`, { password });
      setReport(data);
      setNeedsPassword(false);
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-[#FAFAF9]">
      <div className="animate-pulse flex flex-col items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-[#2D4A3E]/20" />
        <div className="h-3 w-32 bg-[#EAE7E1] rounded" />
      </div>
    </div>
  );

  if (error && !needsPassword) return (
    <div className="min-h-screen flex items-center justify-center bg-[#FAFAF9] px-4">
      <div className="bg-white border border-[#EAE7E1] rounded-2xl p-8 max-w-md text-center">
        <Warning weight="duotone" className="w-12 h-12 text-[#D96C4E] mx-auto mb-4" />
        <h2 className="text-xl font-medium text-[#2C2C2A] mb-2" style={{ fontFamily: 'Outfit' }}>Report Unavailable</h2>
        <p className="text-sm text-[#6E6E6A]">{error}</p>
      </div>
    </div>
  );

  if (needsPassword) return (
    <div className="min-h-screen flex items-center justify-center bg-[#FAFAF9] px-4">
      <div className="bg-white border border-[#EAE7E1] rounded-2xl p-8 max-w-md w-full" data-testid="shared-report-password">
        <div className="text-center mb-6">
          <Lock weight="duotone" className="w-12 h-12 text-[#2D4A3E] mx-auto mb-3" />
          <h2 className="text-xl font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>Password Protected</h2>
          <p className="text-sm text-[#6E6E6A] mt-1">This report requires a password to view</p>
        </div>
        {error && <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg mb-4">{error}</div>}
        <Input type="password" value={password} onChange={e => setPassword(e.target.value)}
          placeholder="Enter password" data-testid="shared-report-password-input"
          onKeyDown={e => e.key === 'Enter' && unlockReport()}
          className="rounded-xl border-[#EAE7E1] bg-[#FAFAF9] mb-4" />
        <Button onClick={unlockReport} className="w-full rounded-full bg-[#2D4A3E] hover:bg-[#1E332A] text-white" data-testid="shared-report-unlock-btn">
          Unlock Report
        </Button>
      </div>
    </div>
  );

  if (!report?.entries) return null;

  // Group entries by vital
  const vitalGroups = {};
  report.entries.forEach(e => {
    if (!vitalGroups[e.vital_key]) vitalGroups[e.vital_key] = [];
    vitalGroups[e.vital_key].push({ date: e.date, value: e.value, value2: e.value2 });
  });

  return (
    <div className="min-h-screen bg-[#FAFAF9] py-12 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Heartbeat weight="duotone" className="w-7 h-7 text-[#2D4A3E]" />
            <span className="text-lg font-semibold text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
          </div>
          <h1 className="text-2xl font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>
            Health Report for {report.user_name}
          </h1>
          <p className="text-sm text-[#6E6E6A] mt-1">{report.start_date} to {report.end_date}</p>
        </div>

        {Object.entries(vitalGroups).map(([vk, entries], idx) => {
          const vital = VITAL_MAP[vk] || { name: vk, unit: '', chartType: 'line', color: CHART_COLORS[0] };
          const data = entries.map(e => ({
            date: new Date(e.date + 'T00:00:00').toLocaleDateString('en', { month: 'short', day: 'numeric' }),
            value: e.value, value2: e.value2,
          }));
          const values = entries.map(e => e.value).filter(v => v != null);
          const avg = values.length ? (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1) : '—';
          return (
            <div key={vk} className="bg-white border border-[#EAE7E1] rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: vital.color || CHART_COLORS[idx % CHART_COLORS.length] }} />
                <h2 className="text-lg font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>{vital.name}</h2>
                <Badge className="bg-[#FAFAF9] text-[#6E6E6A] border border-[#EAE7E1] text-xs">{vital.unit}</Badge>
                <span className="ml-auto text-sm text-[#6E6E6A]">Avg: <strong className="text-[#2C2C2A]">{avg}</strong></span>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                {vital.chartType === 'bar' ? (
                  <BarChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#EAE7E1" />
                    <XAxis dataKey="date" fontSize={10} tick={{ fill: '#6E6E6A' }} /><YAxis fontSize={10} tick={{ fill: '#6E6E6A' }} />
                    <Tooltip /><Bar dataKey="value" fill={vital.color || CHART_COLORS[idx % CHART_COLORS.length]} radius={[4,4,0,0]} /></BarChart>
                ) : vital.chartType === 'dual_line' ? (
                  <LineChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#EAE7E1" />
                    <XAxis dataKey="date" fontSize={10} tick={{ fill: '#6E6E6A' }} /><YAxis fontSize={10} tick={{ fill: '#6E6E6A' }} />
                    <Tooltip /><Legend />
                    <Line type="monotone" dataKey="value" name="Systolic" stroke={CHART_COLORS[0]} strokeWidth={2} dot={{ r: 2 }} />
                    <Line type="monotone" dataKey="value2" name="Diastolic" stroke={CHART_COLORS[1]} strokeWidth={2} dot={{ r: 2 }} /></LineChart>
                ) : (
                  <LineChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#EAE7E1" />
                    <XAxis dataKey="date" fontSize={10} tick={{ fill: '#6E6E6A' }} /><YAxis fontSize={10} tick={{ fill: '#6E6E6A' }} />
                    <Tooltip /><Line type="monotone" dataKey="value" stroke={vital.color || CHART_COLORS[idx % CHART_COLORS.length]} strokeWidth={2} dot={{ r: 2 }} /></LineChart>
                )}
              </ResponsiveContainer>
            </div>
          );
        })}

        <p className="text-xs text-center text-[#6E6E6A]">
          Generated by VitalTrack. For informational tracking only. Not a medical device.
        </p>
      </div>
    </div>
  );
}
