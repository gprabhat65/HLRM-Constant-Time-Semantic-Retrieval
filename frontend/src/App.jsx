import React, { useState, useEffect } from 'react';
import { Search, Server, FileText, RefreshCw, Upload, Database } from 'lucide-react';
import api from './api';

function App() {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showAdmin, setShowAdmin] = useState(false);

    // Admin Stats
    const [stats, setStats] = useState({ files_present: 0, knowledge_entries: 0 });
    const [uploadStatus, setUploadStatus] = useState('');

    const handleQuery = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setResponse(null);
        try {
            const res = await api.post('/query', { query });
            setResponse(res.data);
        } catch (err) {
            console.error(err);
            setResponse({
                answer: "Error connecting to server.",
                domain: "",
                source: "System",
                latency_ms: 0,
                found: false
            });
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const res = await api.get('/admin/status');
            setStats(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            await api.post('/admin/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setUploadStatus(`Uploaded ${file.name}`);
            fetchStats();
        } catch (err) {
            setUploadStatus('Upload failed');
        }
    };

    const handleCompile = async () => {
        setUploadStatus('Compiling knowledge store...');
        try {
            const res = await api.post('/admin/compile');
            setUploadStatus(`Compiled ${res.data.entries_compiled} entries`);
            fetchStats();
        } catch (err) {
            setUploadStatus('Compilation failed');
        }
    };

    const handleReload = async () => {
        try {
            await api.post('/admin/reload');
            setUploadStatus('Runtime store reloaded');
            fetchStats();
        } catch (err) {
            setUploadStatus('Reload failed');
        }
    };

    useEffect(() => {
        if (showAdmin) fetchStats();
    }, [showAdmin]);

    return (
        <div className="min-h-screen flex flex-col font-sans text-slate-800 bg-slate-50">
            {/* Header */}
            <header className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center sticky top-0 z-10 shadow-sm">
                <div className="flex items-center gap-2 text-indigo-600">
                    <Database size={24} />
                    <h1 className="text-xl font-bold tracking-tight">HLRM Query System</h1>
                </div>
                <button
                    onClick={() => setShowAdmin(!showAdmin)}
                    className="text-sm font-medium text-slate-500 hover:text-indigo-600 flex items-center gap-2 px-3 py-2 rounded-md hover:bg-slate-100 transition-colors"
                >
                    <Server size={18} />
                    {showAdmin ? 'Hide Admin' : 'Admin Panel'}
                </button>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex flex-col md:flex-row max-w-7xl mx-auto w-full p-6 gap-8">

                {/* User Query Section */}
                <section className="flex-1 flex flex-col items-center justify-start pt-10">
                    <div className="w-full max-w-2xl text-center mb-8">
                        <h2 className="text-3xl font-extrabold text-slate-900 mb-3">
                            Instant Knowledge Retrieval
                        </h2>
                        <p className="text-slate-500">
                            Deterministic O(1) Access to Verified Institutional Data
                        </p>
                    </div>

                    <form onSubmit={handleQuery} className="w-full max-w-2xl relative mb-8">
                        <div className="relative group">
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Ask a question..."
                                className="w-full pl-5 pr-14 py-4 rounded-xl border border-slate-200 shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-lg transition-all group-hover:shadow-md"
                            />
                            <button
                                type="submit"
                                disabled={loading}
                                className="absolute right-2 top-2 bottom-2 bg-indigo-600 text-white rounded-lg px-4 hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center justify-center"
                            >
                                {loading ? <RefreshCw className="animate-spin" size={20} /> : <Search size={20} />}
                            </button>
                        </div>
                    </form>

                    {/* Response Card */}
                    {response && (
                        <div className="w-full max-w-2xl bg-white rounded-xl shadow-lg border border-slate-100 overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
                            <div className="h-1 w-full bg-indigo-500" />
                            <div className="p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <span className="px-2 py-1 rounded text-xs font-bold bg-green-100 text-green-700">
                                        Verified
                                    </span>
                                    <div className="text-xs text-slate-400 font-mono">
                                        {response.latency_ms} ms
                                    </div>
                                </div>

                                <p className="text-lg text-slate-800 leading-relaxed mb-6">
                                    {response.answer}
                                </p>

                                {response.source && (
                                    <div className="pt-4 border-t border-slate-100 flex items-center gap-2 text-sm text-slate-500">
                                        <FileText size={16} />
                                        <span>
                                            Source: <span className="font-medium text-slate-700">{response.source}</span>
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </section>

                {/* Admin Panel */}
                {showAdmin && (
                    <aside className="w-full md:w-80 bg-white rounded-xl shadow-lg border border-slate-200 p-6 h-fit animate-in slide-in-from-right-4 duration-300">
                        <h3 className="font-bold text-lg mb-4 flex items-center gap-2 border-b pb-2">
                            <Server size={20} className="text-indigo-600" /> System Admin
                        </h3>

                        <div className="space-y-6">
                            {/* Stats */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-slate-50 p-3 rounded-lg text-center border">
                                    <div className="text-2xl font-bold">{stats.files_present}</div>
                                    <div className="text-xs text-slate-500 uppercase">Files</div>
                                </div>
                                <div className="bg-slate-50 p-3 rounded-lg text-center border">
                                    <div className="text-2xl font-bold">{stats.knowledge_entries}</div>
                                    <div className="text-xs text-slate-500 uppercase">Entries</div>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="space-y-3">
                                <input type="file" onChange={handleUpload} className="hidden" id="file-upload" />
                                <label
                                    htmlFor="file-upload"
                                    className="w-full flex items-center justify-center gap-2 bg-slate-100 hover:bg-slate-200 py-2 rounded-lg cursor-pointer text-sm font-medium"
                                >
                                    <Upload size={16} /> Upload Document
                                </label>

                                <button
                                    onClick={handleCompile}
                                    className="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white py-2 rounded-lg"
                                >
                                    <Database size={16} /> Compile Knowledge
                                </button>

                                <button
                                    onClick={handleReload}
                                    className="w-full flex items-center justify-center gap-2 border py-2 rounded-lg"
                                >
                                    <RefreshCw size={16} /> Reload Runtime
                                </button>
                            </div>

                            {/* Status */}
                            {uploadStatus && (
                                <div className="bg-slate-50 p-3 rounded text-xs font-mono border break-words">
                                    <span className="mr-1">&gt;</span>{uploadStatus}
                                </div>
                            )}
                        </div>
                    </aside>
                )}
            </main>
        </div>
    );
}

export default App;
