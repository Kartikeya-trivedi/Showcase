import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 selection:bg-blue-500/30 overflow-x-hidden">
      
      {/* 1. TECH TEXTURE: The Engineering Grid */}
      <div className="fixed inset-0 z-0 opacity-20 pointer-events-none" 
           style={{ backgroundImage: `linear-gradient(#1e293b 1px, transparent 1px), linear-gradient(90deg, #1e293b 1px, transparent 1px)`, 
           backgroundSize: '40px 40px' }}>
      </div>

      {/* 2. BACKGROUND GLOWS: For that AI depth */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] rounded-full bg-blue-600/10 blur-[120px]" />
        <div className="absolute bottom-[10%] right-[10%] w-[30%] h-[30%] rounded-full bg-indigo-600/10 blur-[120px]" />
      </div>

      <main className="relative z-10 container mx-auto px-6 py-20 flex flex-col items-center">
        
        {/* 3. HEADER: Gemini Pulse Indicator */}
        <div className="text-center mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold tracking-widest uppercase">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            Gemini-1.5-Flash Engine Active
          </div>
          <h1 className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-slate-500 tracking-tight">
            Showcase Intelligence
          </h1>
          <p className="text-slate-400 text-lg max-w-xl mx-auto font-light">
            Deploy your professional identity. Our neural engine parses your experience into a high-performance portfolio.
          </p>
        </div>

        {/* 4. THE CONSOLE: Senior Metadata Bar */}
        <div className="w-full max-w-2xl flex items-center justify-between px-6 py-2 bg-slate-900/80 border-x border-t border-white/10 rounded-t-2xl backdrop-blur-md">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/20 border border-red-500/40" />
            <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/20 border border-yellow-500/40" />
            <div className="w-2.5 h-2.5 rounded-full bg-green-500/20 border border-green-500/40" />
          </div>
          <span className="text-[10px] font-mono text-slate-500 uppercase tracking-[0.2em]">system_v.0.9.18</span>
        </div>

        {/* 5. UPLOAD AREA: With the Scan Line */}
        <div className="w-full max-w-2xl bg-slate-900/40 border border-white/10 rounded-b-3xl p-8 backdrop-blur-xl shadow-2xl transition-all hover:bg-slate-900/60">
          <div className="relative border-2 border-dashed border-slate-800 rounded-2xl p-12 flex flex-col items-center transition-all hover:border-blue-500/30 group overflow-hidden">
            
            {/* The Moving Scan Line */}
            <div className="absolute inset-0 w-full h-24 bg-gradient-to-b from-transparent via-blue-500/5 to-transparent animate-scan pointer-events-none" />
            
            <div className="w-16 h-16 bg-blue-600/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-all duration-500 border border-blue-500/20">
              <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            
            <h3 className="text-xl font-medium mb-2 tracking-tight">Initialize Resume Analysis</h3>
            <p className="text-slate-500 text-sm mb-8 font-mono">DRAG_AND_DROP_SOURCE_FILE</p>
            
            <button className="relative px-10 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-[0_0_30px_rgba(37,99,235,0.2)] transition-all active:scale-95 group/btn">
              <span className="relative z-10 flex items-center gap-2">
                UPLOAD DATA <span className="text-blue-200 group-hover/btn:translate-x-1 transition-transform">→</span>
              </span>
            </button>
          </div>

          {/* 6. LIVE FEED: Technical Stats */}
          <div className="mt-8 grid grid-cols-3 gap-4 border-t border-white/5 pt-8">
            {[
              { label: 'Latency', value: '142ms' },
              { label: 'Neural_Load', value: '0.04%' },
              { label: 'Node_Status', value: 'v24.LTS' }
            ].map((stat, i) => (
              <div key={i} className="text-center group">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1 group-hover:text-blue-400 transition-colors">{stat.label}</p>
                <p className="text-xs font-mono text-slate-300">{stat.value}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;