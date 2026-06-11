import React, { useState } from 'react';
import axios from 'axios';

export default function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [step, setStep] = useState('input'); // 'input' | 'scanning' | 'report'
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState('');
  const [currentProgressText, setCurrentProgressText] = useState('Initializing agent modules...');

  const handleScan = async (e) => {
    e.preventDefault();
    if (!repoUrl) return;

    setError('');
    setStep('scanning');
    
    const progressSteps = [
      "Connecting to GitHub via Context Protocol Server...",
      "Downloading repository file manifests...",
      "Mapping directory tree patterns...",
      "Streaming code blocks to Gemini reasoning engine...",
      "Compiling final threat diagnostics report..."
    ];

    progressSteps.forEach((text, index) => {
      setTimeout(() => {
        setCurrentProgressText(text);
      }, (index + 1) * 1100);
    });

    try {
      const response = await axios.post('http://localhost:8000/api/scans/scan', {
        repo_url: repoUrl
      });

      setTimeout(() => {
        setScanResult(response.data);
        setStep('report');
      }, progressSteps.length * 1150);

    } catch (err) {
      setError(err.response?.data?.detail || "Failed to complete security sweep. Verify backend server status.");
      setStep('input');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500 selection:text-slate-950 font-sans antialiased">
      
      {/* BACKGROUND GLOWS */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-[128px] pointer-events-none" />

      {/* HEADER NAV */}
      <header className="border-b border-slate-900 bg-slate-950/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center font-black text-slate-950 shadow-lg shadow-cyan-500/20 font-mono text-sm">
              CS
            </div>
            <span className="font-mono text-sm font-bold tracking-widest uppercase bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
              CYBERSHIELD <span className="text-cyan-400 font-black">//</span> AGENT
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[11px] font-mono tracking-wider uppercase text-slate-400">SOC Node Node-01 Active</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12 relative z-10">
        
        {/* VIEW 1: INPUT GATEWAY */}
        {step === 'input' && (
          <div className="max-w-2xl mx-auto my-12 space-y-8">
            <div className="text-center space-y-3">
              <span className="px-3 py-1 text-xs font-mono bg-blue-950/40 text-blue-400 border border-blue-900/40 rounded-full inline-block tracking-wider uppercase">
                Automated AI Audit Matrix
              </span>
              <h1 className="text-4xl font-black tracking-tight sm:text-5xl bg-gradient-to-r from-slate-50 via-slate-200 to-slate-400 bg-clip-text text-transparent">
                Scan Code Repositories For Vulnerabilities.
              </h1>
              <p className="text-slate-400 text-base max-w-lg mx-auto">
                Leverages deep Gemini context models and GitHub connectors to audit code pipelines for secrets, leaks, and exploits instantly.
              </p>
            </div>

            <form onSubmit={handleScan} className="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl backdrop-blur-sm space-y-4 shadow-xl">
              <div className="space-y-2">
                <label className="block text-xs font-mono font-semibold uppercase tracking-wider text-slate-400">Target Repository URL</label>
                <input
                  type="url"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/username/project-repository"
                  className="w-full px-4 py-3.5 bg-slate-950/80 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/80 focus:ring-1 focus:ring-cyan-500/30 transition-all font-mono text-sm"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full py-3.5 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-slate-950 font-bold tracking-wide uppercase rounded-xl shadow-lg shadow-cyan-500/10 hover:shadow-cyan-400/20 active:scale-[0.99] transition-all text-xs font-mono"
              >
                Execute Agent Run Sequence
              </button>
            </form>

            {error && (
              <div className="p-4 bg-red-950/20 border border-red-900/40 rounded-xl text-sm text-red-400 flex items-center gap-3 font-mono">
                <span>⚠️ SYSTEM WARNING: {error}</span>
              </div>
            )}
          </div>
        )}

        {/* VIEW 2: TACTICAL LOAD SCREEN */}
        {step === 'scanning' && (
          <div className="max-w-md mx-auto my-24 text-center space-y-6">
            <div className="relative w-20 h-20 mx-auto">
              <div className="absolute inset-0 border-4 border-cyan-500/20 rounded-full" />
              <div className="absolute inset-0 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin" />
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-bold font-mono tracking-tight text-slate-200">Processing Security Request</h2>
              <p className="text-sm font-mono text-cyan-400 h-5 transition-all">{currentProgressText}</p>
            </div>
          </div>
        )}

        {/* VIEW 3: LIVE SEC DASHBOARD */}
        {step === 'report' && scanResult && (
          <div className="space-y-8">
            
            {/* AUDIT SUMMARY HEADER CONTROLS PANEL */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* TARGET DETAILS */}
              <div className="lg:col-span-2 p-6 bg-slate-900/30 border border-slate-900 rounded-2xl flex flex-col justify-between gap-4">
                <div>
                  <span className="px-2 py-0.5 text-[10px] font-mono font-bold tracking-wider uppercase bg-blue-950 text-blue-400 border border-blue-900/50 rounded">
                    Target Profile
                  </span>
                  <h2 className="text-3xl font-black tracking-tight text-slate-100 mt-2 font-mono">
                    {scanResult.owner} <span className="text-slate-600">/</span> {scanResult.repo}
                  </h2>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-900/60 font-mono text-xs text-slate-400">
                  <div>Engine: <span className="text-slate-200 font-semibold">{scanResult.repository?.language || "N/A"}</span></div>
                  <div>Branch: <span className="text-slate-200 font-semibold">{scanResult.repository?.default_branch || "main"}</span></div>
                  <div>Forks: <span className="text-slate-200 font-semibold">{scanResult.repository?.forks_count || 0}</span></div>
                  <div>Stars: <span className="text-slate-200 font-semibold">{scanResult.repository?.stargazers_count || 0}</span></div>
                </div>
              </div>

              {/* LIVE COUNTERS SUMMARY WIDGET */}
              <div className="p-6 bg-slate-900/20 border border-slate-900 rounded-2xl space-y-4">
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 block">Threat Matrix Distribution</span>
                <div className="grid grid-cols-4 gap-2 text-center">
                  <div className="p-2 bg-red-950/40 border border-red-900/30 rounded-lg">
                    <div className="text-xl font-bold font-mono text-red-500">{scanResult.findings_summary?.high || 0}</div>
                    <div className="text-[9px] font-mono text-slate-500 uppercase font-semibold">High</div>
                  </div>
                  <div className="p-2 bg-amber-950/30 border border-amber-900/20 rounded-lg">
                    <div className="text-xl font-bold font-mono text-amber-500">{scanResult.findings_summary?.medium || 0}</div>
                    <div className="text-[9px] font-mono text-slate-500 uppercase font-semibold">Med</div>
                  </div>
                  <div className="p-2 bg-blue-950/30 border border-blue-900/20 rounded-lg">
                    <div className="text-xl font-bold font-mono text-blue-400">{scanResult.findings_summary?.low || 0}</div>
                    <div className="text-[9px] font-mono text-slate-500 uppercase font-semibold">Low</div>
                  </div>
                  <div className="p-2 bg-slate-900 border border-slate-800 rounded-lg">
                    <div className="text-xl font-bold font-mono text-slate-400">{scanResult.findings_summary?.info || 0}</div>
                    <div className="text-[9px] font-mono text-slate-500 uppercase font-semibold">Info</div>
                  </div>
                </div>
              </div>

            </div>

            {/* AI SYSTEM STATUS ALERTS */}
            {scanResult.ai_analysis_status !== 'success' && scanResult.ai_analysis_error && (
              <div className="p-4 bg-amber-950/20 border border-amber-900/40 rounded-xl font-mono text-xs text-amber-400">
                ⚠️ AI MODULE NOTE: {scanResult.ai_analysis_error}
              </div>
            )}

            {/* MAIN DATA BLOCK LAYOUT */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              
              {/* SIDEBAR: REPOSITORY ROOT DISCOVERY TREE */}
              <div className="space-y-4 lg:col-span-1">
                <h3 className="text-xs font-mono font-bold tracking-widest text-slate-400 uppercase border-b border-slate-900 pb-2">
                  📂 Explored Manifest Tree
                </h3>
                <div className="bg-slate-950/40 border border-slate-900 p-4 rounded-xl max-h-96 overflow-y-auto space-y-2 font-mono text-xs">
                  {scanResult.root_contents?.map((item, index) => (
                    <div key={index} className="flex items-center justify-between text-slate-400 p-1.5 hover:bg-slate-900/50 rounded transition-all">
                      <span className="truncate">
                        {item.type === 'dir' ? '📁' : '📄'} {item.name}
                      </span>
                      <span className="text-[9px] text-slate-600 bg-slate-900 px-1.5 py-0.5 rounded uppercase">
                        {item.type}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* CONTENT AREA: RENDERED FINDINGS LIST */}
              <div className="space-y-6 lg:col-span-3">
                <div className="flex items-center justify-between border-b border-slate-900 pb-2">
                  <h3 className="text-xs font-mono font-bold tracking-widest text-slate-300 uppercase">
                    ⚡ Threat Registry Registry Log
                  </h3>
                  <span className="text-xs font-mono text-slate-500">
                    Aggregated Findings: {scanResult.findings?.length || 0}
                  </span>
                </div>

                {scanResult.findings?.length === 0 ? (
                  <div className="text-center py-12 bg-slate-900/10 border border-dashed border-slate-900 rounded-2xl font-mono text-sm text-slate-500">
                    ✨ Clean audit report. No critical vulnerabilities identified.
                  </div>
                ) : (
                  scanResult.findings?.map((finding, idx) => (
                    <div key={idx} className="bg-slate-900/20 border border-slate-900 hover:border-slate-800/60 rounded-xl overflow-hidden transition-all shadow-md">
                      
                      {/* FINDING HEAD STATBAR */}
                      <div className="p-4 bg-slate-900/40 border-b border-slate-900 flex items-center justify-between gap-4">
                        <div className="flex items-center gap-3">
                          <span className={`px-2 py-0.5 text-[9px] font-black font-mono tracking-wider uppercase border rounded ${
                            finding.severity === 'high' 
                              ? 'bg-red-950 text-red-400 border-red-900/60' 
                              : finding.severity === 'medium'
                              ? 'bg-amber-950 text-amber-400 border-amber-900/60'
                              : 'bg-blue-950 text-blue-400 border-blue-900/60'
                          }`}>
                            {finding.severity}
                          </span>
                          <strong className="text-sm font-bold font-mono tracking-tight text-slate-100">{finding.title}</strong>
                        </div>
                        <span className="text-[10px] font-mono tracking-wider px-2 py-0.5 rounded bg-slate-950 border border-slate-900 text-slate-500 uppercase">
                          Engine: {finding.source}
                        </span>
                      </div>

                      {/* FINDING BODY */}
                      <div className="p-5 space-y-4 font-mono text-xs">
                        <div className="text-slate-400 leading-relaxed">
                          <span className="text-[10px] font-bold text-slate-600 block uppercase tracking-wider mb-1">Audit Log Context</span>
                          {finding.description}
                        </div>

                        {finding.remediation && (
                          <div className="p-4 bg-slate-950/80 border border-slate-900 rounded-lg leading-relaxed text-slate-300">
                            <span className="font-bold text-cyan-400 block text-[10px] uppercase tracking-wider mb-1">🔧 Suggested Mitigation Strategy</span>
                            {finding.remediation}
                          </div>
                        )}
                      </div>

                    </div>
                  ))
                )}
              </div>

            </div>

            {/* BACK BUTTON */}
            <div className="pt-4">
              <button
                onClick={() => setStep('input')}
                className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-xs font-mono font-bold uppercase tracking-wider transition-all"
              >
                ← Clear Node Memory & Scan New Registry
              </button>
            </div>

          </div>
        )}
        {/* PLACE THIS DIRECTLY ABOVE YOUR CLOSING </main> TAG WHEN step === 'input' */}
{step === 'input' && (
  <div className="max-w-4xl mx-auto mt-16 space-y-4">
    <h3 className="text-xs font-mono font-bold tracking-widest text-slate-400 uppercase border-b border-slate-900 pb-2">
      📜 Recent Enterprise Scan Registries
    </h3>
    <div className="bg-slate-900/20 border border-slate-900 rounded-xl overflow-hidden divide-y divide-slate-900 font-mono text-xs text-slate-300">
      <div className="p-4 bg-slate-900/40 grid grid-cols-3 font-bold text-slate-400 uppercase tracking-wider text-[10px]">
        <div>Target Repository</div>
        <div>Primary Engine</div>
        <div className="text-right">Threat Distribution</div>
      </div>
      
      {/* Sample loop element showing how data maps from your new database collections */}
      <div className="p-4 grid grid-cols-3 items-center hover:bg-slate-900/40 transition-all">
        <div className="truncate font-semibold text-slate-200">
          github.com/fastapi/fastapi
        </div>
        <div><span className="text-cyan-400">Python</span> (master)</div>
        <div className="text-right space-x-2">
          <span className="bg-red-950 text-red-400 px-1.5 py-0.5 rounded border border-red-900/40 text-[10px]">2 High</span>
          <span className="bg-amber-950 text-amber-400 px-1.5 py-0.5 rounded border border-amber-900/40 text-[10px]">4 Med</span>
        </div>
      </div>
    </div>
  </div>
)}

      </main>
    </div>
  );
}