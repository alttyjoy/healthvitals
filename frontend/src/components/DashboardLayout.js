import { Outlet, NavLink, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { useState } from 'react';
import {
  ChartLine, Heartbeat, Table, FileArrowDown, CreditCard,
  Gear, ShieldCheck, List, X, SignOut, House
} from '@phosphor-icons/react';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: House },
  { to: '/tracker', label: 'Daily Tracker', icon: Table },
  { to: '/charts', label: 'Charts & Trends', icon: ChartLine },
  { to: '/reports', label: 'Reports', icon: FileArrowDown },
  { to: '/billing', label: 'Billing', icon: CreditCard },
  { to: '/settings', label: 'Settings', icon: Gear },
];

const adminItems = [
  { to: '/admin', label: 'Admin Panel', icon: ShieldCheck },
];

function SidebarContent({ user, onLogout, onClose }) {
  const isAdmin = ['admin', 'super_admin'].includes(user?.role);
  return (
    <div className="flex flex-col h-full">
      <div className="p-6 border-b border-[#EAE7E1]">
        <Link to="/" className="flex items-center gap-2.5" onClick={onClose}>
          <Heartbeat weight="duotone" className="w-7 h-7 text-[#2D4A3E]" />
          <span className="text-lg font-semibold text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
        </Link>
      </div>
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onClose}
            data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-[#2D4A3E] text-white'
                  : 'text-[#6E6E6A] hover:bg-[#EAE7E1] hover:text-[#2C2C2A]'
              }`
            }
          >
            <item.icon weight="duotone" className="w-5 h-5" />
            {item.label}
          </NavLink>
        ))}
        {isAdmin && (
          <>
            <div className="pt-4 pb-2 px-4">
              <span className="text-xs tracking-[0.15em] uppercase text-[#2D4A3E] font-semibold">Admin</span>
            </div>
            {adminItems.map(item => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-[#2D4A3E] text-white'
                      : 'text-[#6E6E6A] hover:bg-[#EAE7E1] hover:text-[#2C2C2A]'
                  }`
                }
              >
                <item.icon weight="duotone" className="w-5 h-5" />
                {item.label}
              </NavLink>
            ))}
          </>
        )}
      </nav>
      <div className="p-4 border-t border-[#EAE7E1]">
        <div className="flex items-center gap-3 px-4 py-2 mb-2">
          <div className="w-8 h-8 rounded-full bg-[#2D4A3E] flex items-center justify-center text-white text-xs font-medium">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-[#2C2C2A] truncate">{user?.name}</div>
            <div className="text-xs text-[#6E6E6A] truncate">{user?.plan?.toUpperCase()} Plan</div>
          </div>
        </div>
        <button
          onClick={onLogout}
          data-testid="sidebar-logout-btn"
          className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-[#6E6E6A] hover:bg-red-50 hover:text-red-600 transition-all w-full"
        >
          <SignOut weight="duotone" className="w-5 h-5" />
          Sign Out
        </button>
      </div>
    </div>
  );
}

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="flex h-screen bg-[#FAFAF9]">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-64 flex-shrink-0 border-r border-[#EAE7E1] bg-white flex-col">
        <SidebarContent user={user} onLogout={handleLogout} onClose={() => {}} />
      </aside>
      {/* Mobile Header + Sidebar */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="md:hidden flex items-center justify-between px-4 py-3 border-b border-[#EAE7E1] bg-white">
          <Link to="/" className="flex items-center gap-2">
            <Heartbeat weight="duotone" className="w-6 h-6 text-[#2D4A3E]" />
            <span className="text-base font-semibold" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
          </Link>
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" data-testid="mobile-menu-btn">
                <List className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 w-64">
              <SidebarContent user={user} onLogout={handleLogout} onClose={() => setMobileOpen(false)} />
            </SheetContent>
          </Sheet>
        </header>
        <main className="flex-1 overflow-auto p-6 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
