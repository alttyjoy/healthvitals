import { useState, useEffect } from 'react';
import api, { formatApiError } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { MagnifyingGlass, Trash, PencilSimple, Plus } from '@phosphor-icons/react';

export function UserManagement({ users, usersTotal, onRefresh }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [editingUser, setEditingUser] = useState(null);
  const [userForm, setUserForm] = useState({ name: '', email: '', password: '', role: 'user', plan: 'free' });
  const [userSaving, setUserSaving] = useState(false);
  const [localUsers, setLocalUsers] = useState(users);
  const [localTotal, setLocalTotal] = useState(usersTotal);

  useEffect(() => { setLocalUsers(users); setLocalTotal(usersTotal); }, [users, usersTotal]);

  const searchUsers = async () => {
    try {
      const res = await api.get(`/admin/users?search=${searchQuery}`);
      setLocalUsers(res.data.users || []);
      setLocalTotal(res.data.total || 0);
    } catch (e) { console.error('Search failed:', e?.message); }
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
        await api.put(`/admin/users/${editingUser.id}`, { name: userForm.name, role: userForm.role, plan: userForm.plan });
        toast.success('User updated');
      }
      setEditingUser(null);
      searchUsers();
      onRefresh?.();
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setUserSaving(false); }
  };

  const deleteUser = async (userId, email) => {
    if (!window.confirm(`Delete user ${email}? This will remove all their data.`)) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      toast.success('User deleted');
      searchUsers();
      onRefresh?.();
    } catch (err) { toast.error(formatApiError(err)); }
  };

  return (
    <div className="space-y-4">
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
      <p className="text-sm text-[#64748B]">{localTotal} users total</p>
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
            {localUsers.map(u => (
              <tr key={u.id} className="border-b border-[#E2E8F0] hover:bg-[#F8FAFC] transition-colors">
                <td className="px-5 py-3">
                  <div className="font-medium text-[#0F172A]">{u.name}</div>
                  <div className="text-xs text-[#64748B]">{u.email}</div>
                </td>
                <td className="px-5 py-3">
                  <Badge className={`border-0 text-xs ${u.plan === 'premium' ? 'bg-[#EF4444]/10 text-[#EF4444]' : u.plan === 'standard' ? 'bg-[#0EA5E9]/10 text-[#0EA5E9]' : 'bg-[#E2E8F0] text-[#64748B]'}`}>{u.plan}</Badge>
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
                    <Button variant="ghost" size="icon" className="h-8 w-8" data-testid={`edit-user-${u.id}`} onClick={() => openEditUser(u)}>
                      <PencilSimple className="w-4 h-4 text-[#64748B]" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8" data-testid={`delete-user-${u.id}`} onClick={() => deleteUser(u.id, u.email)}>
                      <Trash className="w-4 h-4 text-[#EF4444]" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
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
              <Input value={userForm.name} onChange={e => setUserForm(f => ({ ...f, name: e.target.value }))} placeholder="Full name" data-testid="user-name-input" className="mt-1 rounded-xl border-[#E2E8F0]" />
            </div>
            <div>
              <Label className="text-sm">Email</Label>
              <Input value={userForm.email} onChange={e => setUserForm(f => ({ ...f, email: e.target.value }))} placeholder="user@example.com" disabled={editingUser && !editingUser.isNew} data-testid="user-email-input" className="mt-1 rounded-xl border-[#E2E8F0]" />
            </div>
            {editingUser?.isNew && (
              <div>
                <Label className="text-sm">Password</Label>
                <Input type="password" value={userForm.password} onChange={e => setUserForm(f => ({ ...f, password: e.target.value }))} placeholder="Min 6 characters" data-testid="user-password-input" className="mt-1 rounded-xl border-[#E2E8F0]" />
              </div>
            )}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-sm">Role</Label>
                <Select value={userForm.role} onValueChange={v => setUserForm(f => ({ ...f, role: v }))}>
                  <SelectTrigger className="mt-1 rounded-xl border-[#E2E8F0]" data-testid="user-role-select"><SelectValue /></SelectTrigger>
                  <SelectContent><SelectItem value="user">User</SelectItem><SelectItem value="super_admin">Admin</SelectItem></SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-sm">Plan</Label>
                <Select value={userForm.plan} onValueChange={v => setUserForm(f => ({ ...f, plan: v }))}>
                  <SelectTrigger className="mt-1 rounded-xl border-[#E2E8F0]" data-testid="user-plan-select"><SelectValue /></SelectTrigger>
                  <SelectContent><SelectItem value="free">Free</SelectItem><SelectItem value="standard">Standard</SelectItem><SelectItem value="premium">Premium</SelectItem></SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setEditingUser(null)} className="rounded-full border-[#E2E8F0]">Cancel</Button>
              <Button onClick={saveUser} disabled={userSaving} data-testid="save-user-btn" className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6">
                {userSaving ? 'Saving...' : editingUser?.isNew ? 'Create User' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
