import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import api, { formatApiError } from '@/lib/api';
import { VITAL_TYPES, VITAL_MAP } from '@/lib/vitals';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import { FileArrowDown, FileCsv, FilePdf, Calendar } from '@phosphor-icons/react';

export default function Reports() {
  const { user } = useAuth();
  const [selectedVitals, setSelectedVitals] = useState([]);
  const [startDate, setStartDate] = useState(() => new Date(Date.now() - 30 * 86400000).toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [format, setFormat] = useState('csv');
  const [exporting, setExporting] = useState(false);

  const enabledVitals = user?.enabled_vitals || [];
  const plan = user?.plan || 'free';
  const canPdf = plan !== 'free';

  const toggleVital = (vk) => {
    setSelectedVitals(prev => prev.includes(vk) ? prev.filter(v => v !== vk) : [...prev, vk]);
  };

  const selectAll = () => {
    setSelectedVitals(prev => prev.length === enabledVitals.length ? [] : [...enabledVitals]);
  };

  const handleExport = async () => {
    if (selectedVitals.length === 0) { toast.error('Select at least one vital'); return; }
    setExporting(true);
    try {
      const response = await api.post('/exports/generate', {
        vital_keys: selectedVitals, start_date: startDate, end_date: endDate, format
      }, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `vitals_${startDate}_${endDate}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success(`${format.toUpperCase()} exported successfully`);
    } catch (err) {
      toast.error(formatApiError(err) || 'Export failed');
    } finally { setExporting(false); }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in-up" data-testid="reports-page">
      <div>
        <h1 className="text-2xl font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Reports & Export</h1>
        <p className="text-sm text-[#64748B]">Export your health data as CSV or PDF</p>
      </div>

      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
        {/* Date Range */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-[#0F172A] mb-3">Date Range</h3>
          <div className="flex flex-wrap gap-3 items-center">
            <div className="flex items-center gap-2">
              <Calendar weight="duotone" className="w-4 h-4 text-[#64748B]" />
              <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)}
                data-testid="report-start-date"
                className="px-3 py-2 text-sm rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] focus:ring-2 focus:ring-[#0EA5E9]/20 focus:border-[#0EA5E9] outline-none" />
            </div>
            <span className="text-[#64748B] text-sm">to</span>
            <div className="flex items-center gap-2">
              <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)}
                data-testid="report-end-date"
                className="px-3 py-2 text-sm rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] focus:ring-2 focus:ring-[#0EA5E9]/20 focus:border-[#0EA5E9] outline-none" />
            </div>
          </div>
        </div>

        {/* Vital Selection */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-[#0F172A]">Select Vitals</h3>
            <Button variant="ghost" size="sm" onClick={selectAll} className="text-xs text-[#0EA5E9]" data-testid="report-select-all">
              {selectedVitals.length === enabledVitals.length ? 'Deselect All' : 'Select All'}
            </Button>
          </div>
          {enabledVitals.length === 0 ? (
            <p className="text-sm text-[#64748B]">Enable vitals in Settings to export data.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {enabledVitals.map(vk => {
                const vital = VITAL_MAP[vk];
                if (!vital) return null;
                return (
                  <label key={vk} className="flex items-center gap-3 p-3 rounded-xl border border-[#E2E8F0] hover:bg-[#F8FAFC] cursor-pointer transition-colors">
                    <Checkbox checked={selectedVitals.includes(vk)} onCheckedChange={() => toggleVital(vk)} data-testid={`report-vital-${vk}`} />
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: vital.color }} />
                      <span className="text-sm text-[#0F172A]">{vital.name}</span>
                    </div>
                  </label>
                );
              })}
            </div>
          )}
        </div>

        {/* Format Selection */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-[#0F172A] mb-3">Export Format</h3>
          <div className="flex gap-3">
            <button onClick={() => setFormat('csv')} data-testid="report-format-csv"
              className={`flex items-center gap-2 px-5 py-3 rounded-xl border text-sm font-medium transition-all ${format === 'csv' ? 'border-[#0EA5E9] bg-[#0EA5E9]/5 text-[#0EA5E9]' : 'border-[#E2E8F0] text-[#64748B] hover:bg-[#F8FAFC]'}`}>
              <FileCsv weight="duotone" className="w-5 h-5" /> CSV
            </button>
            <button onClick={() => canPdf ? setFormat('pdf') : toast.info('PDF export requires Standard or Premium plan')}
              data-testid="report-format-pdf"
              className={`flex items-center gap-2 px-5 py-3 rounded-xl border text-sm font-medium transition-all ${!canPdf ? 'opacity-50 cursor-not-allowed' : ''} ${format === 'pdf' ? 'border-[#0EA5E9] bg-[#0EA5E9]/5 text-[#0EA5E9]' : 'border-[#E2E8F0] text-[#64748B] hover:bg-[#F8FAFC]'}`}>
              <FilePdf weight="duotone" className="w-5 h-5" /> PDF
              {!canPdf && <Badge className="bg-[#E2E8F0] text-[#64748B] text-[10px] border-0 ml-1">Upgrade</Badge>}
            </button>
          </div>
        </div>

        <Button onClick={handleExport} disabled={exporting || selectedVitals.length === 0}
          data-testid="report-export-btn"
          className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-8 py-3">
          <FileArrowDown className="w-4 h-4 mr-2" />
          {exporting ? 'Exporting...' : `Export ${format.toUpperCase()}`}
        </Button>
      </div>
    </div>
  );
}
