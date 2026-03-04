import { useState } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Lock, User, RefreshCcw, ArrowRight } from 'lucide-react';

interface LoginProps {
    onLogin: (token: string) => void;
    apiBase: string;
}

export default function LoginPage({ onLogin, apiBase }: LoginProps) {
    const [username, setUsername] = useState('admin');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const resp = await fetch(`${apiBase}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!resp.ok) {
                throw new Error("Invalid credentials");
            }

            const data = await resp.json();
            onLogin(data.access_token);
        } catch (err: any) {
            setError(err.message || "Login failed");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Decor */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 -left-12 w-96 h-96 bg-blue-500/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-1/4 -right-12 w-96 h-96 bg-emerald-500/10 blur-[120px] rounded-full" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md relative"
            >
                <div className="glass-panel p-10 rounded-[32px] border border-slate-800/50 shadow-2xl backdrop-blur-xl">
                    <div className="flex flex-col items-center mb-10">
                        <div className="p-4 bg-blue-500/10 rounded-2xl border border-blue-500/20 mb-6 shadow-glow">
                            <ShieldCheck className="text-blue-500 w-10 h-10" />
                        </div>
                        <h1 className="text-3xl font-bold text-white tracking-tight">Sentinel OS</h1>
                        <p className="text-slate-500 text-sm mt-2 font-medium">Liquid Enterprise Forensics v2.0</p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Identity</label>
                            <div className="relative group">
                                <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-500 transition-colors" size={18} />
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="w-full bg-slate-900 border border-slate-800 rounded-xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-blue-500/50 transition-all font-medium"
                                    placeholder="Username"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Access Key</label>
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-500 transition-colors" size={18} />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-slate-900 border border-slate-800 rounded-xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-blue-500/50 transition-all font-medium"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        {error && (
                            <motion.div
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs font-bold flex items-center gap-2"
                            >
                                <Lock size={14} /> {error}
                            </motion.div>
                        )}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full btn-primary h-14 text-sm font-bold flex items-center justify-center gap-2 group relative overflow-hidden active:scale-95 transition-transform"
                        >
                            {isLoading ? (
                                <RefreshCcw className="animate-spin" size={20} />
                            ) : (
                                <>
                                    AUTHORIZE ACCESS
                                    <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-8 pt-6 border-t border-slate-800/50 text-center">
                        <p className="text-[10px] text-slate-600 font-bold uppercase tracking-widest">
                            Secured by Talos Cryptography
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
