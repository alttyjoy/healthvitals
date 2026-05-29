import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { VITAL_MAP, getVitalStatus, getStatusColor } from '@/lib/vitals';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { CaretLeft, CaretRight, FloppyDisk, Note } from '@phosphor-icons/react';

function getDatesInRange(start, count) {
  const dates = [];
  for (let i = 0; i < count; i++) {
    const d = new Date(start);
    d.setDate(d.getDate() + i);
    dates.push(d.toISOString().split('T')[0]);
  }
  return dates;
}

function formatDateShort(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return { day: d.toLocaleDateString('en', { weekday: 'short' }), date: d.getDate(), month: d.toLocaleDateString('en', { month: 'short' }) };
}

export default function DailyTracker() {
  const { user } = useAuth();
  const [enabledVitals, setEnabledVitals] = useState([]);
  const [entries, setEntries] = useState({});
  const [localValues, setLocalValues] = useState({});
  const [dateOffset, setDateOffset] = useState(0);
  const [daysToShow] = useState(7);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const startDate = new Date();
  startDate.setDate(startDate.getDate() - (daysToShow - 1) + dateOffset * daysToShow);
  const dates = getDatesInRange(startDate, daysToShow);
  const today = new Date().toISOString().split('T')[0];

  const dateStart = dates[0];
  const dateEnd = dates[dates.length - 1];

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [vitalsRes, entriesRes] = await Promise.all([
        api.get('/vitals/enabled'),
        api.get(`/entries?start_date=${dateStart}&end_date=${dateEnd}`)
      ]);
      setEnabledVitals(vitalsRes.data.enabled_vitals || []);
      const entryMap = {};
      (entriesRes.data || []).forEach(e => {
        entryMap[`${e.vital_key}_${e.date}`] = e;
      });
      setEntries(entryMap);
      // Init local values from entries
      const lv = {};
      (entriesRes.data || []).forEach(e => {
        lv[`${e.vital_key}_${e.date}`] = String(e.value ?? '');
        if (e.value2 != null) lv[`${e.vital_key}_${e.date}_v2`] = String(e.value2);
      });
      setLocalValues(lv);
    } catch (e) { console.error('Failed to load tracker data:', e); }
    finally { setLoading(false); }
  }, [dateStart, dateEnd]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleValueChange = (vitalKey, date, value, isV2 = false) => {
    const key = isV2 ? `${vitalKey}_${date}_v2` : `${vitalKey}_${date}`;
    setLocalValues(prev => ({ ...prev, [key]: value }));
  };

  const handleBlur = async (vitalKey, date) => {
    const key = `${vitalKey}_${date}`;
    const val = localValues[key];
    const val2 = localValues[`${key}_v2`];
    if (val === '' || val === undefined) return;
    const numVal = parseFloat(val);
    if (isNaN(numVal)) return;
    try {
      await api.post('/entries', {
        vital_key: vitalKey, date, value: numVal,
        value2: val2 ? parseFloat(val2) : null
      });
      setEntries(prev => ({ ...prev, [key]: { vital_key: vitalKey, date, value: numVal, value2: val2 ? parseFloat(val2) : null } }));
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Failed to save');
    }
  };

  const handleSaveAll = async () => {
    setSaving(true);
    const entriesToSave = [];
    enabledVitals.forEach(vk => {
      dates.forEach(date => {
        const val = localValues[`${vk}_${date}`];
        if (val && !isNaN(parseFloat(val))) {
          entriesToSave.push({
            vital_key: vk, date, value: parseFloat(val),
            value2: localValues[`${vk}_${date}_v2`] ? parseFloat(localValues[`${vk}_${date}_v2`]) : null
          });
        }
      });
    });
    try {
      const res = await api.post('/entries/bulk', { entries: entriesToSave });
      toast.success(`Saved ${res.data.saved} entries`);
      loadData();
    } catch (e) {
      toast.error('Failed to save entries');
    } finally { setSaving(false); }
  };

  if (loading) return (
    <div className="space-y-4 animate-pulse">
      <div className="h-10 bg-[#E2E8F0] rounded-xl w-48" />
      <div className="h-[400px] bg-[#E2E8F0] rounded-2xl" />
    </div>
  );

  return (
    <div className="max-w-full space-y-6 animate-fade-in-up" data-testid="daily-tracker">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Daily Tracker</h1>
          <p className="text-sm text-[#64748B]">Enter your health vitals for each day</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-white border border-[#E2E8F0] rounded-xl px-1 py-1">
            <Button variant="ghost" size="icon" onClick={() => setDateOffset(prev => prev - 1)} className="h-8 w-8 rounded-lg" data-testid="tracker-prev-week">
              <CaretLeft className="w-4 h-4" />
            </Button>
            <span className="text-xs text-[#64748B] px-2 min-w-[120px] text-center">
              {new Date(dates[0] + 'T00:00:00').toLocaleDateString('en', { month: 'short', day: 'numeric' })} - {new Date(dates[dates.length - 1] + 'T00:00:00').toLocaleDateString('en', { month: 'short', day: 'numeric' })}
            </span>
            <Button variant="ghost" size="icon" onClick={() => setDateOffset(prev => prev + 1)} disabled={dateOffset >= 0} className="h-8 w-8 rounded-lg" data-testid="tracker-next-week">
              <CaretRight className="w-4 h-4" />
            </Button>
          </div>
          <Button onClick={handleSaveAll} disabled={saving} className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-5" data-testid="tracker-save-all-btn">
            <FloppyDisk className="w-4 h-4 mr-2" /> {saving ? 'Saving...' : 'Save All'}
          </Button>
        </div>
      </div>

      {enabledVitals.length === 0 ? (
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-12 text-center">
          <Note weight="duotone" className="w-12 h-12 text-[#64748B] mx-auto mb-4" />
          <h3 className="text-lg font-medium text-[#0F172A] mb-2" style={{ fontFamily: 'Outfit' }}>No Vitals Enabled</h3>
          <p className="text-sm text-[#64748B] mb-4">Go to Settings to enable the vitals you want to track.</p>
        </div>
      ) : (
        <div className="bg-white border border-[#E2E8F0] rounded-2xl overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
          <div className="overflow-x-auto">
            <table className="tracker-table w-full text-sm" data-testid="tracker-table">
              <thead>
                <tr>
                  <th className="sticky left-0 z-20 bg-[#F8FAFC] px-6 py-4 text-left text-xs font-semibold text-[#0F172A] tracking-wide uppercase border-b border-r border-[#E2E8F0] min-w-[180px]">
                    Vital
                  </th>
                  {dates.map(date => {
                    const f = formatDateShort(date);
                    const isToday = date === today;
                    return (
                      <th key={date} className={`px-4 py-3 text-center border-b border-[#E2E8F0] min-w-[100px] ${isToday ? 'bg-[#0EA5E9]/5' : 'bg-[#F8FAFC]'}`}>
                        <div className="text-xs text-[#64748B]">{f.day}</div>
                        <div className={`text-base font-medium ${isToday ? 'text-[#0EA5E9]' : 'text-[#0F172A]'}`}>{f.date}</div>
                        <div className="text-xs text-[#64748B]">{f.month}</div>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {enabledVitals.map(vk => {
                  const vital = VITAL_MAP[vk];
                  if (!vital) return null;
                  const isDualValue = vital.hasDualValue;
                  return (
                    <tr key={vk} className="hover:bg-[#F8FAFC]/50 transition-colors">
                      <td className="sticky left-0 z-10 bg-white px-6 py-3 border-b border-r border-[#E2E8F0]">
                        <div className="flex items-center gap-2">
                          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: vital.color }} />
                          <div>
                            <div className="font-medium text-[#0F172A] text-sm">{vital.name}</div>
                            <div className="text-xs text-[#64748B]">{vital.unit}</div>
                          </div>
                        </div>
                      </td>
                      {dates.map(date => {
                        const key = `${vk}_${date}`;
                        const val = localValues[key] ?? '';
                        const numVal = val ? parseFloat(val) : null;
                        const status = numVal != null ? getVitalStatus(vk, numVal) : 'none';
                        const isToday = date === today;
                        return (
                          <td key={date} className={`px-2 py-2 border-b border-[#E2E8F0] text-center ${isToday ? 'bg-[#0EA5E9]/[0.02]' : ''}`}>
                            {isDualValue ? (
                              <div className="flex items-center gap-1 justify-center">
                                <input
                                  type="number" placeholder="Sys" value={val}
                                  onChange={e => handleValueChange(vk, date, e.target.value)}
                                  onBlur={() => handleBlur(vk, date)}
                                  data-testid={`entry-${vk}-${date}-sys`}
                                  className={`vital-input w-[50px] status-${status}`}
                                />
                                <span className="text-[#64748B] text-xs">/</span>
                                <input
                                  type="number" placeholder="Dia" value={localValues[`${key}_v2`] ?? ''}
                                  onChange={e => handleValueChange(vk, date, e.target.value, true)}
                                  onBlur={() => handleBlur(vk, date)}
                                  data-testid={`entry-${vk}-${date}-dia`}
                                  className="vital-input w-[50px]"
                                />
                              </div>
                            ) : (
                              <input
                                type="number" placeholder="—" value={val}
                                onChange={e => handleValueChange(vk, date, e.target.value)}
                                onBlur={() => handleBlur(vk, date)}
                                data-testid={`entry-${vk}-${date}`}
                                className={`vital-input status-${status}`}
                                step={vital.unit === 'hours' ? '0.5' : '1'}
                              />
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {/* Legend */}
          <div className="px-6 py-3 border-t border-[#E2E8F0] flex flex-wrap items-center gap-4 text-xs text-[#64748B]">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" /> Normal</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#E9C46A]" /> Warning</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]" /> Critical</span>
            <span className="ml-auto">Values auto-save on blur. Use Save All for bulk save.</span>
          </div>
        </div>
      )}
    </div>
  );
}
