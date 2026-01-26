import React from 'react';

interface SplashScreenProps {
  status?: string;
}

const SplashScreen: React.FC<SplashScreenProps> = ({ status = 'Initializing Core Systems...' }) => {
  return (
    <div
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-slate-950 overflow-hidden"
      aria-busy="true"
      aria-label="Application Loading"
    >
      {/* Background Decorative Elements */}
      <div className="absolute top-1/4 -left-20 w-80 h-80 bg-blue-600/10 blur-[120px] rounded-full animate-pulse" />
      <div className="absolute bottom-1/4 -right-20 w-80 h-80 bg-indigo-600/10 blur-[120px] rounded-full animate-pulse delay-700" />

      {/* Logo Section */}
      <div className="relative group mb-12 animate-in fade-in zoom-in duration-1000">
        <div className="w-32 h-32 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-[2rem] flex items-center justify-center shadow-2xl shadow-blue-600/30 overflow-hidden border border-white/20 relative z-10 backdrop-blur-xl">
          <div className="absolute inset-0 bg-white/5 mix-blend-overlay" />
          <img
            src="/logo.png"
            alt="peopleOS Logo"
            className="w-[85%] h-[85%] object-contain scale-110 group-hover:scale-100 transition-transform duration-700 brightness-110 drop-shadow-lg"
          />
        </div>
        {/* Animated Rings */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 border border-blue-500/20 rounded-full animate-ping opacity-20" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-56 h-56 border border-indigo-500/10 rounded-full animate-pulse opacity-10" />
      </div>

      {/* Brand Identity */}
      <div className="text-center space-y-3 z-10 animate-in slide-in-from-bottom-4 fade-in duration-1000 delay-300 fill-mode-both">
        <h1 className="text-5xl font-black text-white tracking-tighter uppercase">
          people <span className="text-blue-500 italic">OS</span>
        </h1>
        <div className="flex items-center justify-center gap-3">
          <span className="w-8 h-[2px] bg-gradient-to-r from-transparent to-blue-500" />
          <span className="text-[10px] font-black text-blue-400/60 uppercase tracking-[0.8em]">
            e Bussiness Suite
          </span>
          <span className="w-8 h-[2px] bg-gradient-to-l from-transparent to-blue-500" />
        </div>
      </div>

      {/* Loading Progress */}
      <div className="mt-16 w-64 space-y-6 z-10 animate-in fade-in duration-1000 delay-700 fill-mode-both">
        <div className="h-[3px] w-full bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-600 via-indigo-400 to-blue-600 w-full animate-shimmer"
            style={{ backgroundSize: '200% 100%' }}
          />
        </div>

        <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest text-center animate-pulse">
          {status}
        </p>
      </div>

      {/* Version Tag */}
      <div className="absolute bottom-10 text-[9px] font-bold text-slate-700 uppercase tracking-[0.3em]">
        v2026.01 • Core Protocol Active
      </div>

      <style>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite linear;
        }
      `}</style>
    </div>
  );
};

export default SplashScreen;
