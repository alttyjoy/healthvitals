import { useState, useEffect } from 'react';
import api, { formatApiError } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Article, Trash, PencilSimple, Plus } from '@phosphor-icons/react';

export function ContentManagement() {
  const [contentPages, setContentPages] = useState([]);
  const [editingPage, setEditingPage] = useState(null);
  const [pageForm, setPageForm] = useState({ key: '', title: '', content: '', page_type: 'legal', published: true });
  const [pageSaving, setPageSaving] = useState(false);

  useEffect(() => { loadContentPages(); }, []);

  const loadContentPages = async () => {
    try { const { data } = await api.get('/admin/content-pages'); setContentPages(data.pages || []); }
    catch (e) { console.error('Load content pages:', e?.message); }
  };

  const savePage = async () => {
    if (!pageForm.key || !pageForm.title || !pageForm.content) { toast.error('All fields are required'); return; }
    setPageSaving(true);
    try {
      if (editingPage?.isNew) { await api.post('/admin/content-pages', pageForm); }
      else { await api.put(`/admin/content-pages/${editingPage.key}`, pageForm); }
      toast.success('Page saved');
      setEditingPage(null);
      loadContentPages();
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setPageSaving(false); }
  };

  const deletePage = async (key) => {
    try { await api.delete(`/admin/content-pages/${key}`); toast.success('Page deleted'); loadContentPages(); }
    catch (err) { toast.error(formatApiError(err)); }
  };

  return (
    <div className="space-y-6">
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
                <td className="px-5 py-3 hidden sm:table-cell"><Badge className="bg-[#E2E8F0] text-[#64748B] border-0 text-xs">{page.page_type || 'legal'}</Badge></td>
                <td className="px-5 py-3"><Badge className={`border-0 text-xs ${page.published !== false ? 'bg-[#10B981]/10 text-[#10B981]' : 'bg-[#EF4444]/10 text-[#EF4444]'}`}>{page.published !== false ? 'Published' : 'Draft'}</Badge></td>
                <td className="px-5 py-3 text-right">
                  <div className="flex items-center justify-end gap-1">
                    <Button variant="ghost" size="icon" className="h-8 w-8" data-testid={`edit-page-${page.key}`}
                      onClick={() => { setEditingPage(page); setPageForm({ key: page.key, title: page.title, content: page.content || '', page_type: page.page_type || 'legal', published: page.published !== false }); }}>
                      <PencilSimple className="w-4 h-4 text-[#64748B]" />
                    </Button>
                    {!page.builtin && <Button variant="ghost" size="icon" className="h-8 w-8" data-testid={`delete-page-${page.key}`} onClick={() => deletePage(page.key)}><Trash className="w-4 h-4 text-[#EF4444]" /></Button>}
                  </div>
                </td>
              </tr>
            ))}
            {contentPages.length === 0 && <tr><td colSpan={5} className="px-5 py-8 text-center text-[#64748B]">No content pages yet</td></tr>}
          </tbody>
        </table>
      </div>
      <Dialog open={!!editingPage} onOpenChange={(open) => { if (!open) setEditingPage(null); }}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle style={{ fontFamily: 'Outfit' }}>{editingPage?.isNew ? 'Create New Page' : `Edit: ${editingPage?.title || ''}`}</DialogTitle></DialogHeader>
          <div className="space-y-4 mt-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div><Label className="text-sm">Page Key (URL slug)</Label><Input value={pageForm.key} onChange={e => setPageForm(f => ({ ...f, key: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') }))} placeholder="my-page" disabled={editingPage && !editingPage.isNew} data-testid="page-key-input" className="mt-1 rounded-xl border-[#E2E8F0]" /></div>
              <div><Label className="text-sm">Title</Label><Input value={pageForm.title} onChange={e => setPageForm(f => ({ ...f, title: e.target.value }))} placeholder="Page Title" data-testid="page-title-input" className="mt-1 rounded-xl border-[#E2E8F0]" /></div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm">Type</Label>
                <Select value={pageForm.page_type} onValueChange={v => setPageForm(f => ({ ...f, page_type: v }))}>
                  <SelectTrigger className="mt-1 rounded-xl border-[#E2E8F0]" data-testid="page-type-select"><SelectValue /></SelectTrigger>
                  <SelectContent><SelectItem value="legal">Legal</SelectItem><SelectItem value="blog">Blog</SelectItem><SelectItem value="custom">Custom</SelectItem></SelectContent>
                </Select>
              </div>
              <div className="flex items-end gap-3 pb-1">
                <Switch checked={pageForm.published} onCheckedChange={v => setPageForm(f => ({ ...f, published: v }))} data-testid="page-published-toggle" />
                <Label className="text-sm">Published</Label>
              </div>
            </div>
            <div><Label className="text-sm">Content (Markdown)</Label><Textarea value={pageForm.content} onChange={e => setPageForm(f => ({ ...f, content: e.target.value }))} placeholder="Write page content in markdown..." rows={12} data-testid="page-content-textarea" className="mt-1 rounded-xl border-[#E2E8F0] font-mono text-sm" /></div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setEditingPage(null)} className="rounded-full border-[#E2E8F0]">Cancel</Button>
              <Button onClick={savePage} disabled={pageSaving} data-testid="save-page-btn" className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6">{pageSaving ? 'Saving...' : 'Save Page'}</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
