import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { VITAL_TYPES, VITAL_MAP, getVitalStatus, getStatusColor } from '@/lib/vitals';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  ChartLine, Table, ArrowRight, Warning, CheckCircle, Info, Plus, Lightning
} from '@phosphor-icons/react';

export default function Dashboard() {
  const { user } = useAuth();
  const [insights, setInsights] = useState([]);
  const [recentEntries, setRecentEntries] = useState([]);
  const [enabledVitals, setEnabledVitals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString().split('T')[0];
      const [insightsRes, entriesRes, vitalsRes] = await Promise.all([
        api.get('/insights').catch(() => ({ data: { insights: [] } })),
        api.get(`/entries?start_date=${weekAgo}&end_date=${today}`).catch(() => ({ data: [] })),
        api.get('/vitals/enabled').catch(() => ({ data: { enabled_vitals: [] } })),
      ]);
      setInsights(insightsRes.data.insights || []);
      setRecentEntries(entriesRes.data || []);
      setEnabledVitals(vitalsRes.data.enabled_vitals || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const todayEntries = recentEntries.filter(e => e.date === new Date().toISOString().split('T')[0]);
  const insightIcons = { warning: Warning, success: CheckCircle, info: Info };

  if (loading) return (
    <div className="space-y-6 animate-pulse">
      {[1,2,3].map(i => <div key={i} className="h-32 bg-[#E2E8F0] rounded-2xl" />)}
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in-up" data-testid="user-dashboard">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>
          Welcome back, {user?.name?.split(' ')[0]}
        </h1>
        <p className="text-sm text-[#64748B] mt-1">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Active Vitals" value={enabledVitals.length} sub={`of ${VITAL_MAP[Object.keys(VITAL_MAP)[0]] ? VITAL_TYPES.length : 12} available`} />
        <StatCard label="Today's Entries" value={todayEntries.length} sub={`of ${enabledVitals.length} expected`} />
        <StatCard label="This Week" value={recentEntries.length} sub="total entries" />
        <StatCard label="Plan" value={user?.plan?.charAt(0).toUpperCase() + user?.plan?.slice(1)} sub={
          <Link to="/billing" className="text-[#0EA5E9] hover:underline text-xs">Manage</Link>
        } />
      </div>

      {/* Setup prompt if no vitals enabled */}
      {enabledVitals.length === 0 && (
        <div className="bg-[#0EA5E9] rounded-2xl p-8 text-white">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center flex-shrink-0">
              <Plus weight="bold" className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-medium mb-1" style={{ fontFamily: 'Outfit' }}>Get Started</h3>
              <p className="text-white/70 text-sm mb-4">Enable vitals you want to track. Your {user?.plan} plan allows up to {user?.plan === 'free' ? 2 : user?.plan === 'standard' ? 6 : 12} vitals.</p>
              <Link to="/settings">
                <Button className="rounded-full bg-white text-[#0EA5E9] hover:bg-white/90 px-6" data-testid="enable-vitals-btn">
                  Enable Vitals <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Insights */}
        <div className="lg:col-span-2 bg-white border border-[#E2E8F0] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Health Insights</h2>
            <Badge className="bg-[#0EA5E9]/10 text-[#0EA5E9] border-0 text-xs">This Week</Badge>
          </div>
          {insights.length === 0 ? (
            <p className="text-sm text-[#64748B] py-8 text-center">Start tracking to see insights</p>
          ) : (
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {insights.map((ins, i) => {
                const Icon = insightIcons[ins.type] || Info;
                const colors = { warning: 'text-amber-600 bg-amber-50', success: 'text-green-600 bg-green-50', info: 'text-blue-600 bg-blue-50' };
                return (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-lg hover:bg-[#F8FAFC] transition-colors">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${colors[ins.type] || colors.info}`}>
                      <Icon weight="duotone" className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-sm text-[#0F172A]">{ins.message}</p>
                      <p className="text-xs text-[#64748B] mt-0.5">{VITAL_MAP[ins.vital_key]?.name}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="space-y-4">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6">
            <h2 className="text-lg font-medium text-[#0F172A] mb-4" style={{ fontFamily: 'Outfit' }}>Quick Actions</h2>
            <div className="space-y-2">
              <Link to="/tracker" data-testid="quick-action-tracker">
                <Button variant="outline" className="w-full justify-start rounded-xl border-[#E2E8F0] text-[#0F172A] hover:bg-[#F8FAFC] py-3">
                  <Table weight="duotone" className="w-5 h-5 mr-3 text-[#0EA5E9]" /> Log Today's Vitals
                </Button>
              </Link>
              <Link to="/charts" data-testid="quick-action-charts">
                <Button variant="outline" className="w-full justify-start rounded-xl border-[#E2E8F0] text-[#0F172A] hover:bg-[#F8FAFC] py-3">
                  <ChartLine weight="duotone" className="w-5 h-5 mr-3 text-[#0EA5E9]" /> View Trends
                </Button>
              </Link>
              <Link to="/reports" data-testid="quick-action-reports">
                <Button variant="outline" className="w-full justify-start rounded-xl border-[#E2E8F0] text-[#0F172A] hover:bg-[#F8FAFC] py-3">
                  <Lightning weight="duotone" className="w-5 h-5 mr-3 text-[#0EA5E9]" /> Export Report
                </Button>
              </Link>
            </div>
          </div>
          {/* Enabled Vitals */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6">
            <h2 className="text-lg font-medium text-[#0F172A] mb-4" style={{ fontFamily: 'Outfit' }}>Your Vitals</h2>
            {enabledVitals.length === 0 ? (
              <p className="text-sm text-[#64748B]">No vitals enabled yet</p>
            ) : (
              <div className="space-y-2">
                {enabledVitals.map(vk => {
                  const vital = VITAL_MAP[vk];
                  if (!vital) return null;
                  const todayEntry = todayEntries.find(e => e.vital_key === vk);
                  const status = todayEntry ? getVitalStatus(vk, todayEntry.value) : 'none';
                  return (
                    <div key={vk} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-[#F8FAFC]">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: todayEntry ? getStatusColor(status) : '#D4D4D0' }} />
                        <span className="text-sm text-[#0F172A]">{vital.name}</span>
                      </div>
                      <span className="text-sm font-medium" style={{ color: todayEntry ? getStatusColor(status) : '#64748B' }}>
                        {todayEntry ? `${todayEntry.value} ${vital.unit}` : '—'}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
      <p className="text-xs text-[#64748B] tracking-wide uppercase">{label}</p>
      <p className="text-2xl font-semibold text-[#0F172A] mt-1" style={{ fontFamily: 'Outfit' }}>{value}</p>
      <div className="text-xs text-[#64748B] mt-1">{sub}</div>
    </div>
  );
}
