import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import LoginPage from './Login';
import {
  ShieldCheck,
  UploadCloud,
  LayoutDashboard,
  Network,
  History,
  AlertTriangle,
  ArrowUpRight,
  Search,
  CheckCircle2,
  RefreshCcw,
  Settings,
  Database,
  Terminal,
  BarChart3
} from 'lucide-react';

// --- Types ---
interface MetricRow {
  [key: string]: any;
}

interface DashboardMetrics {
  exposure_by_vendor?: MetricRow[];
  leakage_by_type?: MetricRow[];
  highest_risk_skus?: MetricRow[];
  match_performance?: MetricRow[];
  phantom_line_audit?: MetricRow[];
  error?: string;
}

// --- Components ---

const GlassCard = ({ children, title, className = "" }: { children: React.ReactNode, title?: string, className?: string }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className={`glass-card p-6 rounded-2xl ${className}`}
  >
    {title && <h3 className="text-lg font-bold mb-6 flex items-center gap-2">{title}</h3>}
    {children}
  </motion.div>
);

const StatCard = ({ label, value, icon: Icon, color = "blue", subValue = "" }: any) => {
  const colorMap: { [key: string]: string } = {
    blue: "text-blue-400 bg-blue-500/10 shadow-blue-500/5",
    emerald: "text-emerald-400 bg-emerald-500/10 shadow-emerald-500/5",
    rose: "text-rose-400 bg-rose-500/10 shadow-rose-500/5",
    purple: "text-purple-400 bg-purple-500/10 shadow-purple-500/5"
  };
  const glowMap: { [key: string]: string } = {
    blue: "bg-blue-500/5 group-hover:bg-blue-500/10",
    emerald: "bg-emerald-500/5 group-hover:bg-emerald-500/10",
    rose: "bg-rose-500/5 group-hover:bg-rose-500/10",
    purple: "bg-purple-500/5 group-hover:bg-purple-500/10"
  };
  const badgeMap: { [key: string]: string } = {
    blue: "bg-blue-500/10 text-blue-500",
    emerald: "bg-emerald-500/10 text-emerald-500",
    rose: "bg-rose-500/10 text-rose-500",
    purple: "bg-purple-500/10 text-purple-500"
  };

  return (
    <GlassCard className="group relative overflow-hidden">
      <div className={`absolute top-0 right-0 w-24 h-24 blur-3xl -mr-12 -mt-12 transition-all duration-500 ${glowMap[color]}`} />
      <div className="flex justify-between items-start mb-4">
        <div className={`p-3 rounded-xl ${colorMap[color]}`}>
          <Icon size={20} />
        </div>
        {subValue && <span className={`text-[10px] font-bold px-2 py-1 rounded-md ${badgeMap[color]}`}>{subValue}</span>}
      </div>
      <div>
        <p className="stat-label">{label}</p>
        <p className="text-2xl font-bold tracking-tight text-white">{value}</p>
      </div>
    </GlassCard>
  );
};

// --- Main App ---

export default function SentinelApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(localStorage.getItem('sentinel_token'));
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isReconciling, setIsReconciling] = useState(false);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState<any>(null);
  const [isQuerying, setIsQuerying] = useState(false);
  const [uploadFiles, setUploadFiles] = useState<{ [key: string]: File | null }>({
    invoice: null,
    po: null,
    pod: null
  });

  const [config, setConfig] = useState({
    apiBase: "https://localhost:8000",
    neo4jUri: "bolt://neo4j:7687",
    neo4jUser: "neo4j",
    neo4jPass: "sentinel_neo4j"
  });

  useEffect(() => {
    if (token) {
      localStorage.setItem('sentinel_token', token);
      setIsAuthenticated(true);
      refreshMetrics();
    } else {
      localStorage.removeItem('sentinel_token');
      setIsAuthenticated(false);
    }
  }, [token]);

  const handleLogin = (newToken: string) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    setToken(null);
  };

  const refreshMetrics = async () => {
    if (!token) return;
    try {
      const resp = await fetch(`${config.apiBase}/dashboard/metrics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          neo4j_uri: config.neo4jUri,
          neo4j_user: config.neo4jUser,
          neo4j_pass: config.neo4jPass
        })
      });
      if (resp.status === 401) handleLogout();
      const data = await resp.json();
      setMetrics(data);
    } catch (e) {
      console.error("Metrics fetch failed", e);
    }
  };

  const handleReconcile = async () => {
    if (!uploadFiles.invoice || !uploadFiles.po || !uploadFiles.pod) {
      alert("Please select all three base documents (Invoice, PO, POD) for reconciliation.");
      return;
    }

    setIsReconciling(true);
    const formData = new FormData();
    formData.append("files", uploadFiles.invoice);
    formData.append("files", uploadFiles.po);
    formData.append("files", uploadFiles.pod);

    try {
      const resp = await fetch(`${config.apiBase}/reconcile/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      const result = await resp.json();
      console.log("Reconcile Success", result);
      refreshMetrics();
      setActiveTab('dashboard');
    } catch (e) {
      alert("Reconciliation failed. Check console.");
    } finally {
      setIsReconciling(false);
    }
  };

  const handleQuery = async () => {
    if (!query) return;
    setIsQuerying(true);
    try {
      const resp = await fetch(`${config.apiBase}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          question: query,
          neo4j_uri: config.neo4jUri,
          neo4j_user: config.neo4jUser,
          neo4j_pass: config.neo4jPass
        })
      });
      const data = await resp.json();
      setQueryResult(data);
    } catch (e) {
      setQueryResult({ error: "Query engine failed." });
    } finally {
      setIsQuerying(false);
    }
  };

  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} apiBase={config.apiBase} />;
  }

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 selection:bg-blue-500/30">
      {/* Sidebar */}
      <aside className="w-72 glass-panel m-4 rounded-3xl p-6 flex flex-col">
        <div className="flex items-center gap-3 mb-10 pl-2">
          <div className="p-2.5 bg-blue-500/10 rounded-xl border border-blue-500/20 group cursor-pointer hover:border-blue-500/40 transition-all">
            <ShieldCheck className="text-blue-500 group-hover:scale-110 transition-transform" />
          </div>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-500 bg-clip-text text-transparent">
            SENTINEL
          </span>
        </div>

        <nav className="space-y-2 flex-1">
          {[
            { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
            { id: 'ingest', name: 'Data Ingestor', icon: UploadCloud },
            { id: 'graph', name: 'NLQ Substrate', icon: Network },
            { id: 'settings', name: 'Substrate Config', icon: Settings },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === item.id
                ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20 shadow-sm shadow-blue-500/5'
                : 'text-slate-500 hover:text-slate-300 hover:bg-slate-900/50'
                }`}
            >
              <item.icon size={18} />
              {item.name}
            </button>
          ))}
        </nav>

        <div className="pt-6 border-t border-slate-800/50">
          <div className="p-4 bg-slate-900/50 rounded-2xl border border-slate-800/50 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-emerald-500 p-0.5">
              <div className="w-full h-full bg-slate-950 rounded-[11px] flex items-center justify-center font-bold text-xs">
                CA
              </div>
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-bold truncate">Chief Auditor</p>
              <button
                onClick={handleLogout}
                className="text-[10px] text-rose-500 font-bold uppercase tracking-tighter hover:text-rose-400 transition-colors"
              >
                Disconnect Session
              </button>
            </div>
            <Settings size={16} className="text-slate-600 hover:text-white cursor-pointer transition-colors" />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8 relative">
        <header className="flex justify-between items-center mb-10">
          <div>
            <h2 className="text-4xl font-bold tracking-tight text-white mb-2">
              {activeTab === 'dashboard' && "System Intelligence"}
              {activeTab === 'ingest' && "Data Ingestion"}
              {activeTab === 'graph' && "Liquid Knowledge Engine"}
              {activeTab === 'settings' && "Substrate Connectivity"}
            </h2>
            <div className="flex items-center gap-4 text-slate-500 text-sm">
              <span className="flex items-center gap-1.5"><Database size={14} /> {config.neo4jUri}</span>
              <span className="w-1 h-1 rounded-full bg-slate-800"></span>
              <span>March 4, 11:28 AM</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button onClick={refreshMetrics} className="p-2.5 bg-slate-900 border border-slate-800 rounded-xl text-slate-400 hover:text-white hover:border-slate-700 transition-all">
              <RefreshCcw size={18} />
            </button>
            <button className="btn-primary flex items-center gap-2">
              <ArrowUpRight size={18} /> Export Package
            </button>
          </div>
        </header>

        <AnimatePresence mode="wait">
          {activeTab === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard label="Total Recoverable" value={`$${metrics?.leakage_by_type?.reduce((acc, row) => acc + (row.TotalValueUSD || 0), 0).toLocaleString() || '0'}`} icon={AlertTriangle} color="rose" subValue="+12% VS LAST PKG" />
                <StatCard label="Resolved Flags" value={metrics?.match_performance?.reduce((acc, row) => acc + (row.ResolutionCount || 0), 0).toString() || '0'} icon={CheckCircle2} color="emerald" subValue="98.2% CONFIDENCE" />
                <StatCard label="Substrate Nodes" value="12.4k" icon={Network} color="blue" subValue="LIQUID READ ACTIVE" />
                <StatCard label="Processing Speed" value="2.4ms" icon={BarChart3} color="purple" subValue="SUB-SECOND MATCH" />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <GlassCard>
                  <h3 className="text-lg font-bold mb-6 flex items-center gap-2"><BarChart3 size={20} className="text-blue-500" /> Leakage Categories</h3>
                  <div className="space-y-6">
                    {metrics?.leakage_by_type?.map((item: any) => (
                      <div key={item.LeakageCategory}>
                        <div className="flex justify-between text-sm mb-2">
                          <span className="font-semibold text-slate-300">{item.LeakageCategory.replace('_', ' ')}</span>
                          <span className="font-mono text-emerald-400 font-bold">${item.TotalValueUSD.toLocaleString()}</span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${(item.TotalValueUSD / 20000) * 100}%` }}
                            className="h-full bg-blue-500 rounded-full"
                          />
                        </div>
                      </div>
                    ))}
                    {!metrics?.leakage_by_type && <p className="text-slate-600 italic">No anomaly data found in current substrate.</p>}
                  </div>
                </GlassCard>

                <GlassCard>
                  <h3 className="text-lg font-bold mb-6 flex items-center gap-2"><AlertTriangle size={20} className="text-rose-500" /> High Risk Vendors</h3>
                  <div className="space-y-4">
                    {metrics?.exposure_by_vendor?.map((item: any) => (
                      <div key={item.Vendor} className="flex items-center justify-between p-4 bg-slate-950/50 rounded-xl border border-slate-800/50 hover:border-slate-700 transition-all cursor-default">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-500 border border-rose-500/20">
                            <AlertTriangle size={14} />
                          </div>
                          <div>
                            <p className="text-sm font-bold">{item.Vendor}</p>
                            <p className="text-[10px] text-slate-500 font-bold uppercase">{item.ImpactedInvoices} Invoices Impacted</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-mono font-bold text-white">${item.TotalFinancialExposureUSD.toLocaleString()}</p>
                          <p className="text-[10px] text-rose-400 font-bold uppercase">{item.TotalAnomalies} Flags</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              </div>
            </motion.div>
          )}

          {activeTab === 'ingest' && (
            <motion.div
              key="ingest"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="max-w-4xl space-y-8"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  { id: 'invoice', label: 'Invoices', ext: '.json', icon: LayoutDashboard },
                  { id: 'po', label: 'Purchase Orders', ext: '.csv', icon: File },
                  { id: 'pod', label: 'Proof of Delivery', ext: '.xml', icon: CheckCircle2 }
                ].map((type: any) => (
                  <label key={type.id} className="cursor-pointer group">
                    <input
                      type="file"
                      className="hidden"
                      onChange={(e) => setUploadFiles(prev => ({ ...prev, [type.id]: e.target.files?.[0] || null }))}
                    />
                    <div className={`p-8 rounded-3xl border-2 border-dashed transition-all flex flex-col items-center justify-center min-h-[220px] ${uploadFiles[type.id]
                      ? 'bg-emerald-500/5 border-emerald-500/20'
                      : 'bg-slate-900 border-slate-800 group-hover:bg-slate-900 group-hover:border-blue-500/40'
                      }`}>
                      <div className={`p-4 rounded-2xl mb-4 transition-all ${uploadFiles[type.id] ? 'bg-emerald-500/10 text-emerald-500' : 'bg-slate-800 text-slate-500 group-hover:text-blue-400 group-hover:bg-blue-500/10'
                        }`}>
                        {uploadFiles[type.id] ? <CheckCircle2 size={32} /> : <type.icon size={32} />}
                      </div>
                      <p className="text-sm font-bold text-slate-300 text-center">{uploadFiles[type.id] ? uploadFiles[type.id]?.name : `Upload ${type.label}`}</p>
                      <p className="text-[10px] text-slate-500 font-bold uppercase mt-2">{type.ext} only</p>
                    </div>
                  </label>
                ))}
              </div>

              <div className="flex justify-center pt-8">
                <button
                  onClick={handleReconcile}
                  disabled={isReconciling}
                  className="btn-primary h-16 px-12 text-lg flex items-center gap-3 relative overflow-hidden"
                >
                  <AnimatePresence mode="wait">
                    {isReconciling ? (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-3"
                      >
                        <RefreshCcw className="animate-spin" /> RUNNING ALIGNMENT...
                      </motion.div>
                    ) : (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-3"
                      >
                        <UploadCloud /> INITIATE RECONCILIATION
                      </motion.div>
                    )}
                  </AnimatePresence>
                </button>
              </div>
            </motion.div>
          )}

          {activeTab === 'graph' && (
            <motion.div
              key="graph"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              <GlassCard className="p-2!">
                <div className="flex gap-2 p-2">
                  <div className="flex-1 relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                    <input
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
                      placeholder="Ask the Substrate (e.g., 'Show me all anomalies for high-risk vendors')"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl py-4 pl-12 pr-4 text-sm focus:outline-none focus:border-blue-500/50 transition-all font-medium"
                    />
                  </div>
                  <button
                    onClick={handleQuery}
                    disabled={isQuerying}
                    className="btn-primary px-8"
                  >
                    {isQuerying ? <RefreshCcw className="animate-spin" /> : <Terminal size={18} />}
                  </button>
                </div>
              </GlassCard>

              {queryResult && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  <div className="flex items-center gap-2 px-2">
                    <Terminal size={14} className="text-emerald-500" />
                    <code className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Query Result Output</code>
                  </div>
                  <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden min-h-[400px]">
                    <div className="p-4 bg-slate-800/30 border-b border-slate-800/50 flex items-center justify-between">
                      <div className="flex gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-rose-500/50" />
                        <div className="w-2.5 h-2.5 rounded-full bg-amber-500/50" />
                        <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/50" />
                      </div>
                      <span className="text-[10px] text-slate-500 font-bold font-mono lowercase">sentinel_knowledge_base.json</span>
                    </div>
                    <pre className="p-8 text-xs font-mono text-emerald-400 overflow-auto max-h-[500px]">
                      {JSON.stringify(queryResult, null, 2)}
                    </pre>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}

          {activeTab === 'settings' && (
            <motion.div
              key="settings"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="max-w-xl space-y-6"
            >
              <GlassCard>
                <h3 className="text-xl font-bold mb-6">Service Connectivity</h3>
                <div className="space-y-4">
                  <div>
                    <label className="stat-label">Sentinel API Base URL</label>
                    <input
                      value={config.apiBase}
                      onChange={(e) => setConfig({ ...config, apiBase: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm font-mono"
                    />
                  </div>
                  <div>
                    <label className="stat-label">Neo4j Bolt URI</label>
                    <input
                      value={config.neo4jUri}
                      onChange={(e) => setConfig({ ...config, neo4jUri: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm font-mono"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="stat-label">Neo4j Username</label>
                      <input
                        value={config.neo4jUser}
                        onChange={(e) => setConfig({ ...config, neo4jUser: e.target.value })}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm font-mono"
                      />
                    </div>
                    <div>
                      <label className="stat-label">Neo4j Password</label>
                      <input
                        type="password"
                        value={config.neo4jPass}
                        onChange={(e) => setConfig({ ...config, neo4jPass: e.target.value })}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm font-mono"
                      />
                    </div>
                  </div>
                </div>
              </GlassCard>
              <button
                onClick={refreshMetrics}
                className="btn-primary w-full"
              >
                Validate Connectivity
              </button>
            </motion.div>
          )}

          {activeTab === 'history' && (
            <motion.div
              key="history"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="flex items-center justify-center min-h-[400px] text-slate-600"
            >
              <div className="text-center">
                <History size={48} className="mx-auto mb-4 opacity-10" />
                <p className="text-sm font-bold uppercase tracking-tighter">Archival services initializing...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Connection Indicator */}
      <div className="fixed bottom-8 right-8 flex items-center gap-3 px-4 py-2 bg-slate-900 border border-slate-800 rounded-full shadow-2xl">
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse-glow" />
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none">Substrate Sync Active</span>
      </div>
    </div>
  );
}

// Dummy Icon mapping fix
const File = ({ size, className }: any) => <AlertTriangle size={size} className={className} />;
