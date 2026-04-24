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
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import {
  Users, ChartLine, CreditCard, FileArrowDown, MagnifyingGlass, ShieldCheck, Envelope, Article, Trash, PencilSimple, Plus, Bell, Clock
} from '@phosphor-icons/react';

export default function AdminPanel() {
  const [tab, setTab] = useState('overview');
  const [dashboard, setDashboard] = useState(null);
  const [users, setUsers] = useState([]);
  const [usersTotal, setUsersTotal] = useState(0);
  const [analytics, setAnalytics] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  // User CRUD
  const [editingUser, setEditingUser] = useState(null);
  const [userForm, setUserForm] = useState({ name: '', email: '', password: '', role: 'user', plan: 'free' });
  const [userSaving, setUserSaving] = useState(false);
  // SMTP
  const [smtp, setSmtp] = useState({ smtp_host: '', smtp_port: 587, smtp_username: '', smtp_password: '', smtp_from_email: '', smtp_from_name: '', smtp_use_tls: true });
  const [smtpSaving, setSmtpSaving] = useState(false);
  const [smtpLoaded, setSmtpLoaded] = useState(false);
  // Content Management
  const [contentPages, setContentPages] = useState([]);
  const [contentLoaded, setContentLoaded] = useState(false);
  const [editingPage, setEditingPage] = useState(null);
  const [pageForm, setPageForm] = useState({ key: '', title: '', content: '', page_type: 'legal', published: true });
  const [pageSaving, setPageSaving] = useState(false);
  // Reminder settings
  const [reminderSettings, setReminderSettings] = useState({ enabled: false, time: '09:00' });
  const [reminderLoaded, setReminderLoaded] = useState(false);
  const [reminderSaving, setReminderSaving] = useState(false);

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

  const openAddUser = () => {
    setEditingUser({ isNew: true });
    setUserForm({ name: '', email: '', password: '', role: 'user', plan: 'free' });
  };

  const openEditUser = (u) => {
    setEditingUser(u);
    setUserForm({ name: u.name || '', email: u.email || '', password: '', role: u.role || 'user', plan: u.plan || 'free' });
  };

  const saveUser = async () => {
    setUserSaving(true);
    try {
      if (editingUser?.isNew) {
        if (!userForm.email || !userForm.password) { toast.error('Email and password are required'); setUserSaving(false); return; }
        await api.post('/admin/users', userForm);
        toast.success('User created');
      } else {
        const updates = { name: userForm.name, role: userForm.role, plan: userForm.plan };
        await api.put(`/admin/users/${editingUser.id}`, updates);
        toast.success('User updated');
      }
      setEditingUser(null);
      searchUsers();
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setUserSaving(false); }
  };

  const deleteUser = async (userId, email) => {
    if (!window.confirm(`Delete user ${email}? This will remove all their data.`)) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      toast.success('User deleted');
      searchUsers();
    } catch (err) { toast.error(formatApiError(err)); }
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

  // Content management
  const loadContentPages = async () => {
    try {
      const { data } = await api.get('/admin/content-pages');
      setContentPages(data.pages || []);
      setContentLoaded(true);
    } catch (e) { console.error(e); }
  };

  const savePage = async () => {
    if (!pageForm.key || !pageForm.title || !pageForm.content) { toast.error('All fields are required'); return; }
    setPageSaving(true);
    try {
      if (editingPage && !editingPage.builtin) {
        await api.put(`/admin/content-pages/${editingPage.key}`, pageForm);
      } else {
        await api.post('/admin/content-pages', pageForm);
      }
      toast.success('Page saved');
      setEditingPage(null);
      setPageForm({ key: '', title: '', content: '', page_type: 'legal', published: true });
      loadContentPages();
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setPageSaving(false); }
  };

  const deletePage = async (key) => {
    try {
      await api.delete(`/admin/content-pages/${key}`);
      toast.success('Page deleted');
      loadContentPages();
    } catch (err) { toast.error(formatApiError(err)); }
  };

  // Reminder settings
  const loadReminderSettings = async () => {
    try {
      const { data } = await api.get('/admin/reminder-settings');
      setReminderSettings({ enabled: data.enabled || false, time: data.time || '09:00' });
      setReminderLoaded(true);
    } catch (e) { console.error(e); }
  };

  const saveReminderSettings = async () => {
    setReminderSaving(true);
    try {
      await api.put('/admin/reminder-settings', reminderSettings);
      toast.success(`Reminders ${reminderSettings.enabled ? 'enabled' : 'disabled'}`);
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setReminderSaving(false); }
  };

  const triggerReminders = async () => {
    try {
      await api.post('/admin/send-reminders');
      toast.success('Reminder check completed');
    } catch (err) { toast.error(formatApiError(err)); }
  };

  useEffect(() => { if (tab === 'analytics' && !analytics) loadAnalytics(); }, [tab]);
  useEffect(() => { if (tab === 'settings' && !smtpLoaded) { loadSmtp(); loadReminderSettings(); } }, [tab, smtpLoaded]);
  useEffect(() => { if (tab === 'content' && !contentLoaded) loadContentPages(); }, [tab, contentLoaded]);

  if (loading) return (
    <div className="space-y-4 animate-pulse">{[1,2,3,4].map(i => <div key={i} className="h-24 bg-[#E2E8F0] rounded-2xl" />)}</div>
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fade-in-up" data-testid="admin-panel">
      <div className="flex items-center gap-3">
        <ShieldCheck weight="duotone" className="w-7 h-7 text-[#0EA5E9]" />
        <div>
          <h1 className="text-2xl font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Admin Panel</h1>
          <p className="text-sm text-[#64748B]">Manage users, plans, and platform analytics</p>
        </div>
      </div>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="bg-white border border-[#E2E8F0] rounded-xl p-1 flex-wrap">
          <TabsTrigger value="overview" data-testid="admin-tab-overview" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Overview</TabsTrigger>
          <TabsTrigger value="users" data-testid="admin-tab-users" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Users</TabsTrigger>
          <TabsTrigger value="analytics" data-testid="admin-tab-analytics" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Analytics</TabsTrigger>
          <TabsTrigger value="content" data-testid="admin-tab-content" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Content</TabsTrigger>
          <TabsTrigger value="settings" data-testid="admin-tab-settings" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Settings</TabsTrigger>
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
                <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5">
                  <p className="text-xs text-[#64748B] uppercase tracking-wide mb-2">Plan Distribution</p>
                  <div className="space-y-3">
                    <PlanBar label="Free" count={dashboard.free_users} total={dashboard.total_users} color="#64748B" />
                    <PlanBar label="Standard" count={dashboard.standard_users} total={dashboard.total_users} color="#0EA5E9" />
                    <PlanBar label="Premium" count={dashboard.premium_users} total={dashboard.total_users} color="#EF4444" />
                  </div>
                </div>
                <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 md:col-span-2">
                  <p className="text-xs text-[#64748B] uppercase tracking-wide mb-3">Most Tracked Vitals</p>
                  <div className="space-y-2">
                    {Object.entries(dashboard.vital_usage || {}).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([key, count]) => (
                      <div key={key} className="flex items-center justify-between py-1">
                        <span className="text-sm text-[#0F172A]">{VITAL_MAP[key]?.name || key}</span>
                        <Badge className="bg-[#F8FAFC] text-[#64748B] border border-[#E2E8F0] text-xs">{count} entries</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5">
                <p className="text-xs text-[#64748B] uppercase tracking-wide mb-1">Revenue Metrics</p>
                <div className="grid grid-cols-2 gap-4 mt-3">
                  <div><p className="text-2xl font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>₹{dashboard.mrr?.toLocaleString()}</p><p className="text-xs text-[#64748B]">Monthly Recurring Revenue</p></div>
                  <div><p className="text-2xl font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>₹{dashboard.arr?.toLocaleString()}</p><p className="text-xs text-[#64748B]">Annual Recurring Revenue</p></div>
                </div>
              </div>
            </>
          )}
        </TabsContent>

        {/* Users */}
        <TabsContent value="users" className="space-y-4 mt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1 max-w-md">
              <MagnifyingGlass className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
              <Input value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && searchUsers()}
                placeholder="Search by name or email..." data-testid="admin-user-search"
                className="pl-10 rounded-xl border-[#E2E8F0] bg-white" />
            </div>
            <div className="flex gap-2">
              <Button onClick={searchUsers} className="rounded-xl bg-[#0EA5E9] text-white" data-testid="admin-user-search-btn">Search</Button>
              <Button onClick={openAddUser} className="rounded-xl bg-[#10B981] hover:bg-[#4a7049] text-white" data-testid="admin-add-user-btn">
                <Plus className="w-4 h-4 mr-1" /> Add User
              </Button>
            </div>
          </div>
          <p className="text-sm text-[#64748B]">{usersTotal} users total</p>
          <div className="bg-white border border-[#E2E8F0] rounded-2xl overflow-hidden overflow-x-auto">
            <table className="w-full text-sm" data-testid="admin-users-table">
              <thead>
                <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0]">
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">User</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">Plan</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">Role</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide hidden sm:table-cell">Vitals</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide hidden sm:table-cell">Joined</th>
                  <th className="text-right px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} className="border-b border-[#E2E8F0] hover:bg-[#F8FAFC] transition-colors">
                    <td className="px-5 py-3">
                      <div className="font-medium text-[#0F172A]">{u.name}</div>
                      <div className="text-xs text-[#64748B]">{u.email}</div>
                    </td>
                    <td className="px-5 py-3">
                      <Badge className={`border-0 text-xs ${u.plan === 'premium' ? 'bg-[#EF4444]/10 text-[#EF4444]' : u.plan === 'standard' ? 'bg-[#0EA5E9]/10 text-[#0EA5E9]' : 'bg-[#E2E8F0] text-[#64748B]'}`}>
                        {u.plan}
                      </Badge>
                    </td>
                    <td className="px-5 py-3">
                      <Badge className={`border-0 text-xs ${u.role === 'super_admin' ? 'bg-[#EF4444]/10 text-[#EF4444]' : 'bg-[#E2E8F0] text-[#64748B]'}`}>
                        {u.role === 'super_admin' ? 'Admin' : 'User'}
                      </Badge>
                    </td>
                    <td className="px-5 py-3 text-[#64748B] hidden sm:table-cell">{u.enabled_vitals?.length || 0}</td>
                    <td className="px-5 py-3 text-[#64748B] text-xs hidden sm:table-cell">{u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</td>
                    <td className="px-5 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button variant="ghost" size="icon" className="h-8 w-8" data-testid={`edit-user-${u.id}`}
                          onClick={() => openEditUser(u)}>
                          <PencilSimple className="w-4 h-4 text-[#64748B]" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8" data-testid={`delete-user-${u.id}`}
                          onClick={() => deleteUser(u.id, u.email)}>
                          <Trash className="w-4 h-4 text-[#EF4444]" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Add/Edit User Dialog */}
          <Dialog open={!!editingUser} onOpenChange={(open) => { if (!open) setEditingUser(null); }}>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle style={{ fontFamily: 'Outfit' }}>
                  {editingUser?.isNew ? 'Add New User' : `Edit: ${editingUser?.name || editingUser?.email || ''}`}
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label className="text-sm">Name</Label>
                  <Input value={userForm.name} onChange={e => setUserForm(f => ({ ...f, name: e.target.value }))}
                    placeholder="Full name" data-testid="user-name-input"
                    className="mt-1 rounded-xl border-[#E2E8F0]" />
                </div>
                <div>
                  <Label className="text-sm">Email</Label>
                  <Input value={userForm.email} onChange={e => setUserForm(f => ({ ...f, email: e.target.value }))}
                    placeholder="user@example.com" disabled={editingUser && !editingUser.isNew} data-testid="user-email-input"
                    className="mt-1 rounded-xl border-[#E2E8F0]" />
                </div>
                {editingUser?.isNew && (
                  <div>
                    <Label className="text-sm">Password</Label>
                    <Input type="password" value={userForm.password} onChange={e => setUserForm(f => ({ ...f, password: e.target.value }))}
                      placeholder="Min 6 characters" data-testid="user-password-input"
                      className="mt-1 rounded-xl border-[#E2E8F0]" />
                  </div>
                )}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm">Role</Label>
                    <Select value={userForm.role} onValueChange={v => setUserForm(f => ({ ...f, role: v }))}>
                      <SelectTrigger className="mt-1 rounded-xl border-[#E2E8F0]" data-testid="user-role-select"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="user">User</SelectItem>
                        <SelectItem value="super_admin">Admin</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-sm">Plan</Label>
                    <Select value={userForm.plan} onValueChange={v => setUserForm(f => ({ ...f, plan: v }))}>
                      <SelectTrigger className="mt-1 rounded-xl border-[#E2E8F0]" data-testid="user-plan-select"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="free">Free</SelectItem>
                        <SelectItem value="standard">Standard</SelectItem>
                        <SelectItem value="premium">Premium</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <Button variant="outline" onClick={() => setEditingUser(null)} className="rounded-full border-[#E2E8F0]">Cancel</Button>
                  <Button onClick={saveUser} disabled={userSaving} data-testid="save-user-btn"
                    className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6">
                    {userSaving ? 'Saving...' : editingUser?.isNew ? 'Create User' : 'Save Changes'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </TabsContent>

        {/* Analytics */}
        <TabsContent value="analytics" className="space-y-6 mt-4">
          {analytics ? (
            <>
              <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6">
                <h3 className="text-base font-medium text-[#0F172A] mb-4" style={{ fontFamily: 'Outfit' }}>Daily Entries (Last 30 Days)</h3>
                {analytics.daily_entries?.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={analytics.daily_entries}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                      <XAxis dataKey="date" fontSize={10} tick={{ fill: '#64748B' }} tickFormatter={v => v.slice(5)} />
                      <YAxis fontSize={10} tick={{ fill: '#64748B' }} />
                      <Tooltip contentStyle={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: 12 }} />
                      <Bar dataKey="count" fill="#0EA5E9" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : <p className="text-sm text-[#64748B] text-center py-8">No entry data yet</p>}
              </div>
              <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6">
                <h3 className="text-base font-medium text-[#0F172A] mb-4" style={{ fontFamily: 'Outfit' }}>Recent Audit Logs</h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {(analytics.audit_logs || []).map((log, i) => (
                    <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-[#F8FAFC] text-sm">
                      <span className="text-[#0F172A]">{log.action}</span>
                      <span className="text-xs text-[#64748B]">{log.created_at ? new Date(log.created_at).toLocaleString() : ''}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="animate-pulse space-y-4">{[1,2].map(i => <div key={i} className="h-64 bg-[#E2E8F0] rounded-2xl" />)}</div>
          )}
        </TabsContent>

        {/* Content Management */}
        <TabsContent value="content" className="space-y-6 mt-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Article weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
              <h3 className="text-base font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Content Pages</h3>
            </div>
            <Button onClick={() => { setEditingPage({ isNew: true }); setPageForm({ key: '', title: '', content: '', page_type: 'legal', published: true }); }}
              data-testid="admin-add-page-btn" className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-4 text-sm">
              <Plus className="w-4 h-4 mr-1" /> Add Page
            </Button>
          </div>
          <div className="bg-white border border-[#E2E8F0] rounded-2xl overflow-hidden">
            <table className="w-full text-sm" data-testid="admin-content-table">
              <thead>
                <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0]">
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">Title</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide hidden sm:table-cell">Key</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide hidden sm:table-cell">Type</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">Status</th>
                  <th className="text-right px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">Actions</th>
                </tr>
              </thead>
              <tbody>
                {contentPages.map(page => (
                  <tr key={page.key} className="border-b border-[#E2E8F0] hover:bg-[#F8FAFC]">
                    <td className="px-5 py-3 font-medium text-[#0F172A]">{page.title}</td>
                    <td className="px-5 py-3 text-[#64748B] hidden sm:table-cell">/page/{page.key}</td>
                    <td className="px-5 py-3 hidden sm:table-cell">
                      <Badge className="bg-[#E2E8F0] text-[#64748B] border-0 text-xs">{page.page_type || 'legal'}</Badge>
                    </td>
                    <td className="px-5 py-3">
                      <Badge className={`border-0 text-xs ${page.published !== false ? 'bg-[#10B981]/10 text-[#10B981]' : 'bg-[#EF4444]/10 text-[#EF4444]'}`}>
                        {page.published !== false ? 'Published' : 'Draft'}
                      </Badge>
                    </td>
                    <td className="px-5 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button variant="ghost" size="icon" className="h-8 w-8"
                          data-testid={`edit-page-${page.key}`}
                          onClick={() => {
                            setEditingPage(page);
                            setPageForm({ key: page.key, title: page.title, content: page.content || '', page_type: page.page_type || 'legal', published: page.published !== false });
                          }}>
                          <PencilSimple className="w-4 h-4 text-[#64748B]" />
                        </Button>
                        {!page.builtin && (
                          <Button variant="ghost" size="icon" className="h-8 w-8" data-testid={`delete-page-${page.key}`}
                            onClick={() => deletePage(page.key)}>
                            <Trash className="w-4 h-4 text-[#EF4444]" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {contentPages.length === 0 && (
                  <tr><td colSpan={5} className="px-5 py-8 text-center text-[#64748B]">No content pages yet</td></tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Edit/Create Page Dialog */}
          <Dialog open={!!editingPage} onOpenChange={(open) => { if (!open) setEditingPage(null); }}>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle style={{ fontFamily: 'Outfit' }}>
                  {editingPage?.isNew ? 'Create New Page' : `Edit: ${editingPage?.title || ''}`}
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm">Page Key (URL slug)</Label>
                    <Input value={pageForm.key} onChange={e => setPageForm(f => ({ ...f, key: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') }))}
                      placeholder="my-page" disabled={editingPage && !editingPage.isNew} data-testid="page-key-input"
                      className="mt-1 rounded-xl border-[#E2E8F0]" />
                  </div>
                  <div>
                    <Label className="text-sm">Title</Label>
                    <Input value={pageForm.title} onChange={e => setPageForm(f => ({ ...f, title: e.target.value }))}
                      placeholder="Page Title" data-testid="page-title-input"
                      className="mt-1 rounded-xl border-[#E2E8F0]" />
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm">Type</Label>
                    <Select value={pageForm.page_type} onValueChange={v => setPageForm(f => ({ ...f, page_type: v }))}>
                      <SelectTrigger className="mt-1 rounded-xl border-[#E2E8F0]" data-testid="page-type-select"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="legal">Legal</SelectItem>
                        <SelectItem value="blog">Blog</SelectItem>
                        <SelectItem value="custom">Custom</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-end gap-3 pb-1">
                    <Switch checked={pageForm.published} onCheckedChange={v => setPageForm(f => ({ ...f, published: v }))} data-testid="page-published-toggle" />
                    <Label className="text-sm">Published</Label>
                  </div>
                </div>
                <div>
                  <Label className="text-sm">Content (Markdown)</Label>
                  <Textarea value={pageForm.content} onChange={e => setPageForm(f => ({ ...f, content: e.target.value }))}
                    placeholder="Write page content in markdown..." rows={12} data-testid="page-content-textarea"
                    className="mt-1 rounded-xl border-[#E2E8F0] font-mono text-sm" />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setEditingPage(null)} className="rounded-full border-[#E2E8F0]">Cancel</Button>
                  <Button onClick={savePage} disabled={pageSaving} data-testid="save-page-btn"
                    className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6">
                    {pageSaving ? 'Saving...' : 'Save Page'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </TabsContent>

        {/* Settings (SMTP + Reminders) */}
        <TabsContent value="settings" className="space-y-6 mt-4">
          {/* Reminder Settings */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6" data-testid="admin-reminder-settings">
            <div className="flex items-center gap-3 mb-5">
              <Bell weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
              <div>
                <h3 className="text-base font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Email Reminders</h3>
                <p className="text-xs text-[#64748B]">Send daily email reminders to users who haven't logged vitals</p>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <div className="flex items-center gap-3">
                <Switch checked={reminderSettings.enabled} onCheckedChange={v => setReminderSettings(s => ({ ...s, enabled: v }))} data-testid="reminder-enabled-toggle" />
                <Label className="text-sm text-[#0F172A]">Enable daily reminders</Label>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-[#64748B]" />
                <Input type="time" value={reminderSettings.time} onChange={e => setReminderSettings(s => ({ ...s, time: e.target.value }))}
                  className="rounded-xl border-[#E2E8F0] w-32" data-testid="reminder-time-input" />
              </div>
            </div>
            <div className="flex items-center gap-2 mt-4 pt-4 border-t border-[#E2E8F0]">
              <Button onClick={saveReminderSettings} disabled={reminderSaving} data-testid="save-reminder-btn"
                className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6 text-sm">
                {reminderSaving ? 'Saving...' : 'Save Schedule'}
              </Button>
              <Button variant="outline" onClick={triggerReminders} data-testid="trigger-reminders-btn"
                className="rounded-full border-[#E2E8F0] text-sm">
                Send Now
              </Button>
            </div>
          </div>

          {/* SMTP Config */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6" data-testid="admin-smtp-form">
            <div className="flex items-center gap-3 mb-5">
              <Envelope weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
              <div>
                <h3 className="text-base font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>SMTP Configuration</h3>
                <p className="text-xs text-[#64748B]">Configure email settings for reminders and notifications</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm text-[#0F172A]">SMTP Host</Label>
                <Input value={smtp.smtp_host || ''} onChange={e => setSmtp(s => ({ ...s, smtp_host: e.target.value }))}
                  placeholder="smtp.gmail.com" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-host" />
              </div>
              <div>
                <Label className="text-sm text-[#0F172A]">SMTP Port</Label>
                <Input type="number" value={smtp.smtp_port || ''} onChange={e => setSmtp(s => ({ ...s, smtp_port: parseInt(e.target.value) || 0 }))}
                  placeholder="587" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-port" />
              </div>
              <div>
                <Label className="text-sm text-[#0F172A]">Username</Label>
                <Input value={smtp.smtp_username || ''} onChange={e => setSmtp(s => ({ ...s, smtp_username: e.target.value }))}
                  placeholder="your@email.com" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-username" />
              </div>
              <div>
                <Label className="text-sm text-[#0F172A]">Password</Label>
                <Input type="password" value={smtp.smtp_password || ''} onChange={e => setSmtp(s => ({ ...s, smtp_password: e.target.value }))}
                  placeholder="App password or SMTP password" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-password" />
              </div>
              <div>
                <Label className="text-sm text-[#0F172A]">From Email</Label>
                <Input value={smtp.smtp_from_email || ''} onChange={e => setSmtp(s => ({ ...s, smtp_from_email: e.target.value }))}
                  placeholder="noreply@vitaltrack.in" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-from-email" />
              </div>
              <div>
                <Label className="text-sm text-[#0F172A]">From Name</Label>
                <Input value={smtp.smtp_from_name || ''} onChange={e => setSmtp(s => ({ ...s, smtp_from_name: e.target.value }))}
                  placeholder="VitalTrack" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-from-name" />
              </div>
            </div>
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-[#E2E8F0]">
              <div className="flex items-center gap-3">
                <Switch checked={smtp.smtp_use_tls !== false} onCheckedChange={v => setSmtp(s => ({ ...s, smtp_use_tls: v }))} data-testid="smtp-tls-toggle" />
                <Label className="text-sm text-[#0F172A]">Use TLS</Label>
              </div>
              <Button onClick={saveSmtp} disabled={smtpSaving} data-testid="smtp-save-btn"
                className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6">
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
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5">
      <div className="flex items-center gap-2 mb-2">
        <Icon weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
        <span className="text-xs text-[#64748B] uppercase tracking-wide">{label}</span>
      </div>
      <p className="text-2xl font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>{value}</p>
    </div>
  );
}

function PlanBar({ label, count, total, color }) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-[#0F172A]">{label}</span>
        <span className="text-[#64748B]">{count}</span>
      </div>
      <div className="h-2 bg-[#F8FAFC] rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}
