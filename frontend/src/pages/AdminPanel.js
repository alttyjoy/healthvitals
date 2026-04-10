import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { formatApiError } from '@/lib/api';
import { toast } from 'sonner';
import { VITAL_MAP } from '@/lib/vitals';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import {
  Users, ChartLine, CreditCard, FileArrowDown, MagnifyingGlass, ShieldCheck, Envelope
} from '@phosphor-icons/react';

export default function AdminPanel() {
  const [tab, setTab] = useState('overview');
  const [dashboard, setDashboard] = useState(null);
  const [users, setUsers] = useState([]);
  const [usersTotal, setUsersTotal] = useState(0);
  const [analytics, setAnalytics] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  // SMTP
  const [smtp, setSmtp] = useState({ smtp_host: '', smtp_port: 587, smtp_username: '', smtp_password: '', smtp_from_email: '', smtp_from_name: '', smtp_use_tls: true });
  const [smtpSaving, setSmtpSaving] = useState(false);
  const [smtpLoaded, setSmtpLoaded] = useState(false);

  useEffect(() => { loadDashboard(); }, []);

  const loadDashboard = async () => {
    try {
      const [dashRes, usersRes] = await Promise.all([
        api.get('/admin/dashboard'),
        api.get('/admin/users?limit=20'),
      ]);
      setDashboard(dashRes.data);
      setUsers(usersRes.data.users || []);
      setUsersTotal(usersRes.data.total || 0);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const loadAnalytics = async () => {
    try {
      const res = await api.get('/admin/analytics');
      setAnalytics(res.data);
    } catch (e) { console.error(e); }
  };

  const searchUsers = async () => {
    try {
      const res = await api.get(`/admin/users?search=${searchQuery}`);
      setUsers(res.data.users || []);
      setUsersTotal(res.data.total || 0);
    } catch (e) { console.error(e); }
  };

  const loadSmtp = async () => {
    try {
      const { data } = await api.get('/admin/smtp-settings');
      setSmtp(prev => ({ ...prev, ...data }));
      setSmtpLoaded(true);
    } catch (e) { console.error(e); }
  };

  const saveSmtp = async () => {
    setSmtpSaving(true);
    try {
      await api.put('/admin/smtp-settings', smtp);
      toast.success('SMTP settings saved');
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setSmtpSaving(false); }
  };

  useEffect(() => { if (tab === 'analytics' && !analytics) loadAnalytics(); }, [tab]);
  useEffect(() => { if (tab === 'settings' && !smtpLoaded) loadSmtp(); }, [tab, smtpLoaded]);

  if (loading) return (
    <div className="space-y-4 animate-pulse">{[1,2,3,4].map(i => <div key={i} className="h-24 bg-[#EAE7E1] rounded-2xl" />)}</div>
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fade-in-up" data-testid="admin-panel">
      <div className="flex items-center gap-3">
        <ShieldCheck weight="duotone" className="w-7 h-7 text-[#2D4A3E]" />
        <div>
          <h1 className="text-2xl font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>Admin Panel</h1>
          <p className="text-sm text-[#6E6E6A]">Manage users, plans, and platform analytics</p>
        </div>
      </div>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="bg-white border border-[#EAE7E1] rounded-xl p-1">
          <TabsTrigger value="overview" data-testid="admin-tab-overview" className="rounded-lg data-[state=active]:bg-[#2D4A3E] data-[state=active]:text-white">Overview</TabsTrigger>
          <TabsTrigger value="users" data-testid="admin-tab-users" className="rounded-lg data-[state=active]:bg-[#2D4A3E] data-[state=active]:text-white">Users</TabsTrigger>
          <TabsTrigger value="analytics" data-testid="admin-tab-analytics" className="rounded-lg data-[state=active]:bg-[#2D4A3E] data-[state=active]:text-white">Analytics</TabsTrigger>
          <TabsTrigger value="settings" data-testid="admin-tab-settings" className="rounded-lg data-[state=active]:bg-[#2D4A3E] data-[state=active]:text-white">Settings</TabsTrigger>
        </TabsList>

        {/* Overview */}
        <TabsContent value="overview" className="space-y-6 mt-4">
          {dashboard && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <AdminStat icon={Users} label="Total Users" value={dashboard.total_users} />
                <AdminStat icon={CreditCard} label="MRR" value={`₹${dashboard.mrr?.toLocaleString()}`} />
                <AdminStat icon={ChartLine} label="Total Entries" value={dashboard.total_entries?.toLocaleString()} />
                <AdminStat icon={FileArrowDown} label="Exports" value={dashboard.total_exports} />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white border border-[#EAE7E1] rounded-2xl p-5">
                  <p className="text-xs text-[#6E6E6A] uppercase tracking-wide mb-2">Plan Distribution</p>
                  <div className="space-y-3">
                    <PlanBar label="Free" count={dashboard.free_users} total={dashboard.total_users} color="#6E6E6A" />
                    <PlanBar label="Standard" count={dashboard.standard_users} total={dashboard.total_users} color="#2D4A3E" />
                    <PlanBar label="Premium" count={dashboard.premium_users} total={dashboard.total_users} color="#D96C4E" />
                  </div>
                </div>
                <div className="bg-white border border-[#EAE7E1] rounded-2xl p-5 md:col-span-2">
                  <p className="text-xs text-[#6E6E6A] uppercase tracking-wide mb-3">Most Tracked Vitals</p>
                  <div className="space-y-2">
                    {Object.entries(dashboard.vital_usage || {}).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([key, count]) => (
                      <div key={key} className="flex items-center justify-between py-1">
                        <span className="text-sm text-[#2C2C2A]">{VITAL_MAP[key]?.name || key}</span>
                        <Badge className="bg-[#FAFAF9] text-[#6E6E6A] border border-[#EAE7E1] text-xs">{count} entries</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="bg-white border border-[#EAE7E1] rounded-2xl p-5">
                <p className="text-xs text-[#6E6E6A] uppercase tracking-wide mb-1">Revenue Metrics</p>
                <div className="grid grid-cols-2 gap-4 mt-3">
                  <div><p className="text-2xl font-semibold text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>₹{dashboard.mrr?.toLocaleString()}</p><p className="text-xs text-[#6E6E6A]">Monthly Recurring Revenue</p></div>
                  <div><p className="text-2xl font-semibold text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>₹{dashboard.arr?.toLocaleString()}</p><p className="text-xs text-[#6E6E6A]">Annual Recurring Revenue</p></div>
                </div>
              </div>
            </>
          )}
        </TabsContent>

        {/* Users */}
        <TabsContent value="users" className="space-y-4 mt-4">
          <div className="flex gap-3">
            <div className="relative flex-1 max-w-md">
              <MagnifyingGlass className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6E6E6A]" />
              <Input value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && searchUsers()}
                placeholder="Search by name or email..." data-testid="admin-user-search"
                className="pl-10 rounded-xl border-[#EAE7E1] bg-white" />
            </div>
            <Button onClick={searchUsers} className="rounded-xl bg-[#2D4A3E] text-white" data-testid="admin-user-search-btn">Search</Button>
          </div>
          <p className="text-sm text-[#6E6E6A]">{usersTotal} users total</p>
          <div className="bg-white border border-[#EAE7E1] rounded-2xl overflow-hidden">
            <table className="w-full text-sm" data-testid="admin-users-table">
              <thead>
                <tr className="bg-[#FAFAF9] border-b border-[#EAE7E1]">
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#2C2C2A] uppercase tracking-wide">User</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#2C2C2A] uppercase tracking-wide">Plan</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#2C2C2A] uppercase tracking-wide">Role</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#2C2C2A] uppercase tracking-wide">Vitals</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#2C2C2A] uppercase tracking-wide">Joined</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} className="border-b border-[#EAE7E1] hover:bg-[#FAFAF9] transition-colors">
                    <td className="px-5 py-3">
                      <div className="font-medium text-[#2C2C2A]">{u.name}</div>
                      <div className="text-xs text-[#6E6E6A]">{u.email}</div>
                    </td>
                    <td className="px-5 py-3">
                      <Badge className={`border-0 text-xs ${u.plan === 'premium' ? 'bg-[#D96C4E]/10 text-[#D96C4E]' : u.plan === 'standard' ? 'bg-[#2D4A3E]/10 text-[#2D4A3E]' : 'bg-[#EAE7E1] text-[#6E6E6A]'}`}>
                        {u.plan}
                      </Badge>
                    </td>
                    <td className="px-5 py-3 text-[#6E6E6A]">{u.role}</td>
                    <td className="px-5 py-3 text-[#6E6E6A]">{u.enabled_vitals?.length || 0}</td>
                    <td className="px-5 py-3 text-[#6E6E6A] text-xs">{u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        {/* Analytics */}
        <TabsContent value="analytics" className="space-y-6 mt-4">
          {analytics ? (
            <>
              <div className="bg-white border border-[#EAE7E1] rounded-2xl p-6">
                <h3 className="text-base font-medium text-[#2C2C2A] mb-4" style={{ fontFamily: 'Outfit' }}>Daily Entries (Last 30 Days)</h3>
                {analytics.daily_entries?.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={analytics.daily_entries}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#EAE7E1" />
                      <XAxis dataKey="date" fontSize={10} tick={{ fill: '#6E6E6A' }} tickFormatter={v => v.slice(5)} />
                      <YAxis fontSize={10} tick={{ fill: '#6E6E6A' }} />
                      <Tooltip contentStyle={{ background: 'white', border: '1px solid #EAE7E1', borderRadius: 12 }} />
                      <Bar dataKey="count" fill="#2D4A3E" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : <p className="text-sm text-[#6E6E6A] text-center py-8">No entry data yet</p>}
              </div>
              <div className="bg-white border border-[#EAE7E1] rounded-2xl p-6">
                <h3 className="text-base font-medium text-[#2C2C2A] mb-4" style={{ fontFamily: 'Outfit' }}>Recent Audit Logs</h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {(analytics.audit_logs || []).map((log, i) => (
                    <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-[#FAFAF9] text-sm">
                      <span className="text-[#2C2C2A]">{log.action}</span>
                      <span className="text-xs text-[#6E6E6A]">{log.created_at ? new Date(log.created_at).toLocaleString() : ''}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="animate-pulse space-y-4">{[1,2].map(i => <div key={i} className="h-64 bg-[#EAE7E1] rounded-2xl" />)}</div>
          )}
        </TabsContent>

        {/* Settings (SMTP) */}
        <TabsContent value="settings" className="space-y-6 mt-4">
          <div className="bg-white border border-[#EAE7E1] rounded-2xl p-6" data-testid="admin-smtp-form">
            <div className="flex items-center gap-3 mb-5">
              <Envelope weight="duotone" className="w-5 h-5 text-[#2D4A3E]" />
              <div>
                <h3 className="text-base font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>SMTP Configuration</h3>
                <p className="text-xs text-[#6E6E6A]">Configure email settings for reminders and notifications</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm text-[#2C2C2A]">SMTP Host</Label>
                <Input value={smtp.smtp_host || ''} onChange={e => setSmtp(s => ({ ...s, smtp_host: e.target.value }))}
                  placeholder="smtp.gmail.com" className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9]" data-testid="smtp-host" />
              </div>
              <div>
                <Label className="text-sm text-[#2C2C2A]">SMTP Port</Label>
                <Input type="number" value={smtp.smtp_port || ''} onChange={e => setSmtp(s => ({ ...s, smtp_port: parseInt(e.target.value) || 0 }))}
                  placeholder="587" className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9]" data-testid="smtp-port" />
              </div>
              <div>
                <Label className="text-sm text-[#2C2C2A]">Username</Label>
                <Input value={smtp.smtp_username || ''} onChange={e => setSmtp(s => ({ ...s, smtp_username: e.target.value }))}
                  placeholder="your@email.com" className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9]" data-testid="smtp-username" />
              </div>
              <div>
                <Label className="text-sm text-[#2C2C2A]">Password</Label>
                <Input type="password" value={smtp.smtp_password || ''} onChange={e => setSmtp(s => ({ ...s, smtp_password: e.target.value }))}
                  placeholder="App password or SMTP password" className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9]" data-testid="smtp-password" />
              </div>
              <div>
                <Label className="text-sm text-[#2C2C2A]">From Email</Label>
                <Input value={smtp.smtp_from_email || ''} onChange={e => setSmtp(s => ({ ...s, smtp_from_email: e.target.value }))}
                  placeholder="noreply@vitaltrack.in" className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9]" data-testid="smtp-from-email" />
              </div>
              <div>
                <Label className="text-sm text-[#2C2C2A]">From Name</Label>
                <Input value={smtp.smtp_from_name || ''} onChange={e => setSmtp(s => ({ ...s, smtp_from_name: e.target.value }))}
                  placeholder="VitalTrack" className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9]" data-testid="smtp-from-name" />
              </div>
            </div>
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-[#EAE7E1]">
              <div className="flex items-center gap-3">
                <Switch checked={smtp.smtp_use_tls !== false} onCheckedChange={v => setSmtp(s => ({ ...s, smtp_use_tls: v }))} data-testid="smtp-tls-toggle" />
                <Label className="text-sm text-[#2C2C2A]">Use TLS</Label>
              </div>
              <Button onClick={saveSmtp} disabled={smtpSaving} data-testid="smtp-save-btn"
                className="rounded-full bg-[#2D4A3E] hover:bg-[#1E332A] text-white px-6">
                {smtpSaving ? 'Saving...' : 'Save SMTP Settings'}
              </Button>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function AdminStat({ icon: Icon, label, value }) {
  return (
    <div className="bg-white border border-[#EAE7E1] rounded-2xl p-5">
      <div className="flex items-center gap-2 mb-2">
        <Icon weight="duotone" className="w-5 h-5 text-[#2D4A3E]" />
        <span className="text-xs text-[#6E6E6A] uppercase tracking-wide">{label}</span>
      </div>
      <p className="text-2xl font-semibold text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>{value}</p>
    </div>
  );
}

function PlanBar({ label, count, total, color }) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-[#2C2C2A]">{label}</span>
        <span className="text-[#6E6E6A]">{count}</span>
      </div>
      <div className="h-2 bg-[#FAFAF9] rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}
