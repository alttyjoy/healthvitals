import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export default function AuthCallback() {
  const navigate = useNavigate();
  const { loginWithGoogle } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Use ref to prevent double-processing under StrictMode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const hash = window.location.hash;
    const match = hash.match(/session_id=([^&]+)/);
    if (!match) {
      navigate('/login', { replace: true });
      return;
    }
    const sessionId = match[1];

    // Clear the hash immediately
    window.history.replaceState(null, '', window.location.pathname);

    loginWithGoogle(sessionId)
      .then(() => {
        navigate('/dashboard', { replace: true });
      })
      .catch((err) => {
        console.error('Google auth failed:', err?.response?.data?.detail || err?.message);
        navigate('/login', { replace: true, state: { error: 'Google sign-in failed. Please try again.' } });
      });
  }, [loginWithGoogle, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC]">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-[#0EA5E9] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-sm text-[#64748B]">Signing you in...</p>
      </div>
    </div>
  );
}
