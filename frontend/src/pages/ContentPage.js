import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '@/lib/api';
import { Heartbeat, ArrowLeft } from '@phosphor-icons/react';

export default function ContentPage() {
  const { pageKey } = useParams();
  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/content/${pageKey}`).then(res => setPage(res.data)).catch(() => setPage(null)).finally(() => setLoading(false));
  }, [pageKey]);

  if (loading) return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
      <div className="animate-pulse w-full max-w-3xl px-6"><div className="h-8 bg-[#E2E8F0] rounded w-48 mb-6" />{[1,2,3,4].map(i => <div key={i} className="h-4 bg-[#E2E8F0] rounded mb-3 w-full" />)}</div>
    </div>
  );

  if (!page) return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
      <div className="text-center"><p className="text-[#64748B]">Page not found</p><Link to="/" className="text-[#0EA5E9] underline text-sm mt-2 block">Go Home</Link></div>
    </div>
  );

  // Simple markdown-to-HTML renderer
  const renderContent = (md) => {
    return md
      .replace(/^### (.*$)/gim, '<h3 class="text-lg font-medium text-[#0F172A] mt-6 mb-2" style="font-family:Outfit">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-xl font-medium text-[#0F172A] mt-8 mb-3" style="font-family:Outfit">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-3xl font-medium text-[#0F172A] mb-4" style="font-family:Outfit">$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-[#0F172A]">$1</strong>')
      .replace(/^- (.*$)/gim, '<li class="text-sm text-[#64748B] ml-4 mb-1 list-disc">$1</li>')
      .replace(/^\d+\. (.*$)/gim, '<li class="text-sm text-[#64748B] ml-4 mb-1 list-decimal">$1</li>')
      .replace(/\n\n/g, '<br/><br/>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <nav className="fixed top-0 w-full z-50 glass-nav border-b border-[#E2E8F0]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-12 flex items-center justify-between h-14 sm:h-16">
          <Link to="/" className="flex items-center gap-2">
            <Heartbeat weight="duotone" className="w-6 h-6 sm:w-7 sm:h-7 text-[#0EA5E9]" />
            <span className="text-base sm:text-lg font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
          </Link>
          <Link to="/" className="flex items-center gap-1.5 text-sm text-[#64748B] hover:text-[#0F172A]">
            <ArrowLeft className="w-4 h-4" /> Back
          </Link>
        </div>
      </nav>
      <div className="pt-20 sm:pt-28 pb-12 sm:pb-16 px-4 sm:px-6 md:px-12 max-w-3xl mx-auto">
        <div className="bg-white border border-[#E2E8F0] rounded-xl sm:rounded-2xl p-5 sm:p-8 md:p-12 shadow-[0_8px_30px_rgb(0,0,0,0.04)]"
          data-testid={`content-page-${pageKey}`}
          dangerouslySetInnerHTML={{ __html: renderContent(page.content) }} />
      </div>
    </div>
  );
}
