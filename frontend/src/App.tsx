import { useState } from 'react';
import {
  ShieldCheckIcon,
  DocumentArrowUpIcon,
  ChartBarSquareIcon,
  ServerStackIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  DocumentMagnifyingGlassIcon
} from '@heroicons/react/24/outline';

// Mock service for visual demo
const SentinelApp = () => {
  const [activeTab, setActiveTab] = useState('reconcile');
  const [isReconciling, setIsReconciling] = useState(false);

  const stats = [
    { name: 'Total Exposure', value: '$12,450.00', icon: ExclamationCircleIcon, change: '+12%', changeType: 'increase' },
    { name: 'Ghost Flags', value: '42', icon: ShieldCheckIcon, change: '10', changeType: 'increase' },
    { name: 'Matched Transactions', value: '891', icon: CheckCircleIcon, change: '98%', changeType: 'positive' },
    { name: 'Graph Nodes', value: '2,491', icon: ServerStackIcon, change: '+5%', changeType: 'increase' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-blue-500 selection:text-white">
      {/* Sidebar / Navigation */}
      <div className="flex">
        <aside className="w-64 border-r border-slate-800 h-screen sticky top-0 p-6 flex flex-col bg-slate-900/50 backdrop-blur-xl">
          <div className="flex items-center gap-3 mb-10 group">
            <div className="p-2 bg-blue-500/10 rounded-xl border border-blue-500/20 group-hover:border-blue-500/40 transition-all duration-300">
              <img src="/logo.png" alt="Sentinel Logo" className="w-8 h-8 object-contain" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
              SENTINEL
            </h1>
          </div>

          <nav className="flex-1 space-y-2">
            {[
              { id: 'reconcile', name: 'Reconciliation', icon: DocumentArrowUpIcon },
              { id: 'graph', name: 'Graph Topology', icon: ChartBarSquareIcon },
              { id: 'reports', name: 'Evidence Reports', icon: DocumentMagnifyingGlassIcon },
              { id: 'mcp-status', name: 'Bifrost MCP', icon: ServerStackIcon },
            ].map((item: any) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${activeTab === item.id
                  ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
              >
                {item.id === 'reconcile' && <DocumentArrowUpIcon className="w-5 h-5" />}
                {item.id === 'graph' && <ChartBarSquareIcon className="w-5 h-5" />}
                {item.id === 'reports' && <DocumentMagnifyingGlassIcon className="w-5 h-5" />}
                {item.id === 'mcp-status' && <ServerStackIcon className="w-5 h-5" />}
                {item.name}
              </button>
            ))}
          </nav>

          <div className="mt-auto pt-6 border-t border-slate-800">
            <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center text-xs font-bold text-white uppercase shadow-lg shadow-blue-500/20">
                JD
              </div>
              <div className="text-xs">
                <p className="font-semibold">Jane Auditor</p>
                <p className="text-slate-500 uppercase tracking-widest leading-none mt-1" style={{ fontSize: '0.6rem' }}>Admin Role</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8 overflow-y-auto">
          <header className="flex justify-between items-center mb-10">
            <div>
              <h2 className="text-3xl font-bold text-white tracking-tight">
                {activeTab === 'reconcile' && "Ghost Detection Pipeline"}
                {activeTab === 'graph' && "Transaction Topologies"}
                {activeTab === 'reports' && "Archived Evidence"}
                {activeTab === 'mcp-status' && "Bifrost Connectivity"}
              </h2>
              <p className="text-slate-500 mt-2">March 4, 2026 — Sentinel Substrate Active</p>
            </div>
            <div className="flex gap-4">
              <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-sm font-medium transition-colors">
                Support
              </button>
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-500/20 rounded-lg text-sm font-medium transition-all duration-300">
                System Refresh
              </button>
            </div>
          </header>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
            {stats.map((stat) => (
              <div key={stat.name} className="p-6 bg-slate-900 border border-slate-800 rounded-2xl hover:border-blue-500/30 transition-all duration-300 group">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-slate-800 rounded-xl text-blue-400 group-hover:scale-110 transition-transform duration-300">
                    <stat.icon className="w-6 h-6" />
                  </div>
                  <span className={`text-xs font-bold px-2 py-1 rounded-full ${stat.changeType === 'increase' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-blue-500/10 text-blue-500'
                    }`}>
                    {stat.change}
                  </span>
                </div>
                <p className="text-slate-400 text-sm font-medium mb-1">{stat.name}</p>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Tab Views */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl shadow-black/50">
            {activeTab === 'reconcile' && (
              <div className="p-10 text-center flex flex-col items-center justify-center min-h-[400px]">
                <div className="mb-6 p-4 bg-blue-500/5 border border-dashed border-blue-500/20 rounded-3xl group hover:border-blue-500/40 transition-all duration-500 cursor-pointer w-full max-w-md">
                  <DocumentArrowUpIcon className="w-16 h-16 mx-auto mb-4 text-blue-400/50 group-hover:text-blue-400 transition-colors duration-500" />
                  <h3 className="text-xl font-bold mb-2">Ingest Ghost Substrates</h3>
                  <p className="text-slate-500 text-sm mb-6">Drop JSON (Invoices), CSV (POs), or XML (PODs) to initiate reconciliation.</p>
                  <button
                    onClick={() => setIsReconciling(true)}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold transition-all shadow-xl shadow-blue-600/20 active:scale-95"
                  >
                    Execute Pipeline
                  </button>
                </div>
                {isReconciling && (
                  <div className="mt-8 flex items-center gap-4 text-sm animate-pulse">
                    <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                    <span className="text-blue-400 font-mono tracking-widest uppercase">Stitching Transactions...</span>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'graph' && (
              <div className="p-10 flex flex-col items-center justify-center min-h-[400px] relative overflow-hidden group">
                <div className="absolute inset-0 opacity-20 pointer-events-none group-hover:opacity-30 transition-opacity duration-1000">
                  <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <path d="M0,50 Q25,20 50,50 T100,50" fill="none" stroke="#3b82f6" strokeWidth="0.5" />
                    <path d="M0,30 Q25,60 50,30 T100,30" fill="none" stroke="#10b981" strokeWidth="0.5" />
                    <circle cx="50" cy="50" r="1" fill="#3b82f6" />
                  </svg>
                </div>
                <ChartBarSquareIcon className="w-16 h-16 mb-4 text-emerald-400/50" />
                <h3 className="text-xl font-bold mb-2">Neo4j Substrate Viewer</h3>
                <p className="text-slate-500 text-sm text-center max-w-sm mb-6">
                  Interactive graph visualization of Invoice-to-PO-to-POD lineages. Bifrost protocol active for natural language querying.
                </p>
                <div className="flex gap-3">
                  <button className="px-6 py-2 bg-emerald-600/20 border border-emerald-600/30 text-emerald-400 rounded-lg hover:bg-emerald-600/30 transition-colors text-sm font-bold">
                    Launch Topology Engine
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'mcp-status' && (
              <div className="p-10 min-h-[400px]">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400">
                    <ServerStackIcon className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">Bifrost MCP Registry</h3>
                    <p className="text-slate-400 text-sm">Active Bridge: {NEO4J_URI}</p>
                  </div>
                </div>

                <div className="space-y-4">
                  {[
                    { tool: 'query_graph', desc: 'Natural Language to Cypher Translation', status: 'ready' },
                    { tool: 'get_graph_schema', desc: 'Metadata/Labels extraction', status: 'ready' },
                    { tool: 'detect_ghosts', desc: 'Legacy detection trigger', status: 'maintenance' },
                  ].map(t => (
                    <div key={t.tool} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl border border-slate-700/50 hover:border-slate-500/50 transition-colors">
                      <div>
                        <code className="text-blue-400 text-sm font-mono">{t.tool}()</code>
                        <p className="text-slate-500 text-xs mt-1">{t.desc}</p>
                      </div>
                      <span className={`text-[10px] uppercase tracking-widest font-bold px-2 py-1 rounded-md ${t.status === 'ready' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                        }`}>
                        {t.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default SentinelApp;
const NEO4J_URI = "bolt://localhost:7687";
