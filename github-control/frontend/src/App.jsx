import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Terminal,
  FileCode,
  MessageSquare,
  PlusCircle,
  Send,
  Users,
  Clock,
  Lock,
  CheckCircle,
  XCircle,
  Database,
  RefreshCw
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api/github';

export default function App() {
  // Global & Session States
  const [role, setRole] = useState('admin'); // admin, operator, viewer
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [toast, setToast] = useState(null); // { type: 'success'|'error', message: '' }

  // Tab/Active Panel State
  const [activeTab, setActiveTab] = useState('comment'); // comment, issue, pr, commit

  // Form Field States
  const [commentData, setCommentData] = useState({ issueNumber: '', commentText: '' });
  const [issueData, setIssueData] = useState({ title: '', body: '', labels: '' });
  const [prData, setPrData] = useState({ prNumber: '', commentText: '' });
  const [commitData, setCommitData] = useState({ filePath: 'src/custom-update.txt', fileContent: 'System online.', commitMessage: 'Update workspace configs', branch: 'main' });

  // Confirmation Modal State
  const [confirmation, setConfirmation] = useState(null); // null or { command, details, onConfirm }
  const [confirmTextInput, setConfirmTextInput] = useState('');
  const [confirmCheckbox, setConfirmCheckbox] = useState(false);

  // Fetch audit logs from backend on mount
  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/logs`);
      const data = await res.json();
      if (data.success) {
        setLogs(data.logs.reverse()); // Show newest logs first
      }
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  // Display ephemeral feedback toast
  const showToast = (type, message) => {
    setToast({ type, message });
    setTimeout(() => {
      setToast(null);
    }, 5000);
  };

  // Base dispatcher that intercepts actions to show explicit confirmation modal
  const handleActionTrigger = (command, details, onConfirm) => {
    setConfirmTextInput('');
    setConfirmCheckbox(false);
    setConfirmation({
      command,
      details,
      onConfirm: async () => {
        setIsLoading(true);
        try {
          await onConfirm();
          fetchLogs();
        } catch (error) {
          showToast('error', error.message || 'Operation failed.');
        } finally {
          setIsLoading(false);
          setConfirmation(null);
        }
      }
    });
  };

  // 1. Dispatch "comment on GitHub"
  const dispatchComment = async () => {
    if (!commentData.issueNumber || !commentData.commentText) {
      showToast('error', 'Please fill out all comment parameters.');
      return;
    }

    handleActionTrigger(
      'comment on GitHub',
      { type: 'Post Comment', target: `Issue/PR #${commentData.issueNumber}`, preview: commentData.commentText },
      async () => {
        const response = await fetch(`${API_BASE_URL}/comment`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            command: 'comment on GitHub',
            confirmExplicit: true,
            role,
            details: {
              issueNumber: commentData.issueNumber,
              commentText: commentData.commentText
            }
          })
        });
        const result = await response.json();
        if (!result.success) throw new Error(result.message);
        showToast('success', result.message);
        setCommentData({ issueNumber: '', commentText: '' });
      }
    );
  };

  // 2. Dispatch "create issue"
  const dispatchCreateIssue = async () => {
    if (!issueData.title) {
      showToast('error', 'Please input an issue title.');
      return;
    }

    handleActionTrigger(
      'create issue',
      { type: 'Create Issue', target: `Title: ${issueData.title}`, preview: issueData.body || 'No description body provided.' },
      async () => {
        const labelsArr = issueData.labels ? issueData.labels.split(',').map(l => l.trim()) : [];
        const response = await fetch(`${API_BASE_URL}/issue`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            command: 'create issue',
            confirmExplicit: true,
            role,
            details: {
              title: issueData.title,
              body: issueData.body,
              labels: labelsArr
            }
          })
        });
        const result = await response.json();
        if (!result.success) throw new Error(result.message);
        showToast('success', result.message);
        setIssueData({ title: '', body: '', labels: '' });
      }
    );
  };

  // 3. Dispatch "create PR comment"
  const dispatchPRComment = async () => {
    if (!prData.prNumber || !prData.commentText) {
      showToast('error', 'Please fill out all PR comment parameters.');
      return;
    }

    handleActionTrigger(
      'create PR comment',
      { type: 'PR Comment', target: `Pull Request #${prData.prNumber}`, preview: prData.commentText },
      async () => {
        const response = await fetch(`${API_BASE_URL}/pr-comment`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            command: 'create PR comment',
            confirmExplicit: true,
            role,
            details: {
              prNumber: prData.prNumber,
              commentText: prData.commentText
            }
          })
        });
        const result = await response.json();
        if (!result.success) throw new Error(result.message);
        showToast('success', result.message);
        setPrData({ prNumber: '', commentText: '' });
      }
    );
  };

  // 4. Dispatch "push these changes"
  const dispatchPushCommit = async () => {
    if (!commitData.filePath || !commitData.fileContent || !commitData.commitMessage) {
      showToast('error', 'Please fill out all commit parameters.');
      return;
    }

    handleActionTrigger(
      'push these changes',
      { type: 'Push Commit', target: `${commitData.filePath} (${commitData.branch})`, preview: `Message: "${commitData.commitMessage}"` },
      async () => {
        const response = await fetch(`${API_BASE_URL}/commit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            command: 'push these changes',
            confirmExplicit: true,
            role,
            details: {
              filePath: commitData.filePath,
              fileContent: commitData.fileContent,
              commitMessage: commitData.commitMessage,
              branch: commitData.branch
            }
          })
        });
        const result = await response.json();
        if (!result.success) throw new Error(result.message);
        showToast('success', result.message);
      }
    );
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans select-none antialiased selection:bg-rose-500 selection:text-white">

      {/* Dynamic Toast Feedback Overlay */}
      {toast && (
        <div className={`fixed top-6 right-6 z-50 flex items-center gap-3 px-6 py-4 rounded-xl border backdrop-blur-md shadow-2xl transition-all duration-300 transform scale-100 ${toast.type === 'success'
            ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300 shadow-emerald-950/50'
            : 'bg-rose-950/80 border-rose-500 text-rose-300 shadow-rose-950/50'
          }`}>
          {toast.type === 'success' ? <CheckCircle size={20} className="text-emerald-400" /> : <XCircle size={20} className="text-rose-400" />}
          <span className="text-sm font-semibold tracking-wide">{toast.message}</span>
        </div>
      )}

      {/* Strict Confirmation Warning Modal Overlay */}
      {confirmation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md px-4">
          <div className="bg-slate-900 border border-rose-500/30 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl shadow-rose-950/20 animate-in fade-in zoom-in duration-200">

            {/* Modal Header Warning Alert Banner */}
            <div className="bg-gradient-to-r from-rose-900/50 to-orange-900/30 border-b border-rose-500/20 px-6 py-5 flex items-center gap-4">
              <div className="p-2 bg-rose-500/10 rounded-lg text-rose-400 animate-pulse">
                <ShieldAlert size={28} />
              </div>
              <div>
                <h3 className="font-bold text-lg text-rose-100 tracking-wider">MANUAL CONTROL CONFIRMATION</h3>
                <p className="text-xs text-rose-400 uppercase font-semibold tracking-widest mt-0.5">Strict Security Gate Required</p>
              </div>
            </div>

            {/* Modal Body & Arguments Details */}
            <div className="p-6 space-y-5">
              <div className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="flex justify-between text-xs font-mono text-slate-400">
                  <span>ACTION TYPE:</span>
                  <span className="text-rose-400 font-bold uppercase">{confirmation.details.type}</span>
                </div>
                <div className="flex justify-between text-xs font-mono text-slate-400">
                  <span>EXPLICIT COMMAND:</span>
                  <span className="text-amber-400 font-semibold">"{confirmation.command}"</span>
                </div>
                <div className="flex justify-between text-xs font-mono text-slate-400">
                  <span>TARGET RESOURCE:</span>
                  <span className="text-slate-200 font-medium">{confirmation.details.target}</span>
                </div>
                <div className="border-t border-slate-900 pt-2 mt-2">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest block mb-1">Payload Content / Parameters Preview:</span>
                  <pre className="text-xs font-mono bg-slate-950 p-3 rounded-lg overflow-x-auto text-slate-300 max-h-32 border border-slate-900">
                    {confirmation.details.preview}
                  </pre>
                </div>
              </div>

              {/* Mandatory User Gate inputs */}
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                    Verify Command Action (Type <span className="text-rose-400 font-mono">"Yes"</span>):
                  </label>
                  <input
                    type="text"
                    value={confirmTextInput}
                    onChange={(e) => setConfirmTextInput(e.target.value)}
                    placeholder='Type "Yes" here'
                    className="w-full bg-slate-950 border border-slate-800 focus:border-rose-500/50 rounded-xl px-4 py-3 text-sm font-semibold text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-rose-500/30 transition-all font-mono"
                  />
                </div>

                <label className="flex items-start gap-3 p-3 bg-slate-950/30 hover:bg-slate-950/60 rounded-xl border border-slate-800/40 cursor-pointer transition-colors select-none">
                  <input
                    type="checkbox"
                    checked={confirmCheckbox}
                    onChange={(e) => setConfirmCheckbox(e.target.checked)}
                    className="mt-1 accent-rose-500 rounded cursor-pointer"
                  />
                  <div className="space-y-0.5">
                    <span className="text-xs font-bold text-slate-200 uppercase tracking-wide">Confirm Manual Execution</span>
                    <p className="text-[10px] text-slate-400 leading-relaxed">
                      I explicitly authorize the platform to dispatch this request to the GitHub REST API. This action is 100% manual.
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="bg-slate-950/80 px-6 py-4 border-t border-slate-900 flex justify-end gap-3">
              <button
                onClick={() => setConfirmation(null)}
                className="px-4 py-2.5 rounded-xl border border-slate-800 text-slate-400 hover:text-slate-100 hover:bg-slate-900 text-xs font-bold uppercase tracking-wider transition-all"
              >
                Cancel
              </button>
              <button
                disabled={confirmTextInput !== 'Yes' || !confirmCheckbox}
                onClick={confirmation.onConfirm}
                className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 disabled:text-slate-500 text-white text-xs font-bold uppercase tracking-widest shadow-lg shadow-rose-950/20 disabled:shadow-none transition-all flex items-center gap-2 cursor-pointer disabled:cursor-not-allowed"
              >
                <Send size={14} />
                Confirm & Execute
              </button>
            </div>

          </div>
        </div>
      )}

      {/* Cyberpunk Header Layout */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40 px-6 py-4 flex items-center justify-between shadow-lg shadow-slate-950/20">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 shadow-inner">
            <Terminal size={22} className="animate-pulse" />
          </div>
          <div>
            <h1 className="text-sm font-black tracking-wider uppercase text-slate-100">ANTIGRAVITY AI</h1>
            <p className="text-[10px] font-bold text-rose-400 tracking-widest uppercase mt-0.5">Strict Manual-First GitHub Control</p>
          </div>
        </div>

        {/* Global Security Controls & Role Manager */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-slate-900/60 border border-slate-800 rounded-xl p-1.5 pr-3">
            <div className="p-1.5 bg-slate-950/80 border border-slate-800 rounded-lg text-slate-400 flex items-center gap-1.5">
              <Users size={14} />
              <span className="text-[9px] font-black uppercase tracking-widest">Active Role:</span>
            </div>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="bg-transparent text-xs font-bold tracking-wide text-rose-400 focus:outline-none cursor-pointer pl-1 capitalize"
            >
              <option value="admin" className="bg-slate-950 text-slate-100">Administrator</option>
              <option value="operator" className="bg-slate-950 text-slate-100">Operator</option>
              <option value="viewer" className="bg-slate-950 text-slate-100">Viewer (Read-Only)</option>
            </select>
          </div>

          <div className="hidden md:flex items-center gap-1.5 px-3 py-2 bg-emerald-950/30 border border-emerald-500/20 rounded-xl text-emerald-400 text-xs font-mono font-semibold">
            <span className="h-1.5 w-1.5 bg-emerald-400 rounded-full animate-ping"></span>
            MANUAL SECURE GATE ACTIVE
          </div>
        </div>
      </header>

      {/* Main Grid Layout Dashboard */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden">

        {/* Left Side Column: Action Workspace panels (7 columns) */}
        <section className="lg:col-span-7 flex flex-col gap-6">
          <div className="bg-slate-900/40 border border-slate-900/80 backdrop-blur-md rounded-2xl p-6 flex flex-col flex-1 shadow-2xl relative overflow-hidden">

            {/* Tab navigation headers */}
            <div className="flex border-b border-slate-950 pb-4 mb-6 gap-2 overflow-x-auto">
              <button
                onClick={() => setActiveTab('comment')}
                className={`px-4 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2 border cursor-pointer ${activeTab === 'comment'
                    ? 'bg-rose-950/20 border-rose-500/30 text-rose-300 shadow-inner'
                    : 'bg-slate-950/30 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
              >
                <MessageSquare size={14} />
                Post Comment
              </button>

              <button
                onClick={() => setActiveTab('issue')}
                className={`px-4 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2 border cursor-pointer ${activeTab === 'issue'
                    ? 'bg-rose-950/20 border-rose-500/30 text-rose-300 shadow-inner'
                    : 'bg-slate-950/30 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
              >
                <PlusCircle size={14} />
                Create Issue
              </button>

              <button
                onClick={() => setActiveTab('pr')}
                className={`px-4 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2 border cursor-pointer ${activeTab === 'pr'
                    ? 'bg-rose-950/20 border-rose-500/30 text-rose-300 shadow-inner'
                    : 'bg-slate-950/30 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
              >
                <MessageSquare size={14} />
                PR Comment
              </button>

              <button
                onClick={() => setActiveTab('commit')}
                className={`px-4 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2 border cursor-pointer ${activeTab === 'commit'
                    ? 'bg-rose-950/20 border-rose-500/30 text-rose-300 shadow-inner'
                    : 'bg-slate-950/30 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
              >
                <FileCode size={14} />
                Push Changes
              </button>
            </div>

            {/* Tab Panels Contents */}
            <div className="flex-1 flex flex-col justify-between">

              {/* TAB 1: Post Comment Panel */}
              {activeTab === 'comment' && (
                <div className="space-y-5 animate-in fade-in duration-200">
                  <div className="space-y-1">
                    <h2 className="text-base font-bold text-slate-200 uppercase tracking-wider">Comment Workspace</h2>
                    <p className="text-xs text-slate-400">Post a comment directly to a specific Issue or PR thread.</p>
                  </div>

                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="md:col-span-1 space-y-1.5">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Issue/PR #:</label>
                        <input
                          type="number"
                          value={commentData.issueNumber}
                          onChange={(e) => setCommentData({ ...commentData, issueNumber: e.target.value })}
                          placeholder="e.g. 1"
                          className="w-full bg-slate-950/50 border border-slate-850 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20 font-mono"
                        />
                      </div>
                      <div className="md:col-span-3 space-y-1.5">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Explicit Command Required:</label>
                        <input
                          type="text"
                          readOnly
                          value="comment on GitHub"
                          className="w-full bg-slate-950 border border-slate-900 rounded-xl px-4 py-3 text-xs font-mono text-amber-500/80 cursor-not-allowed select-none"
                        />
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Comment Markdown Text:</label>
                      <textarea
                        rows={6}
                        value={commentData.commentText}
                        onChange={(e) => setCommentData({ ...commentData, commentText: e.target.value })}
                        placeholder="Type comments here..."
                        className="w-full bg-slate-950/50 border border-slate-855 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20 font-mono resize-none leading-relaxed"
                      />
                    </div>
                  </div>

                  <button
                    disabled={isLoading}
                    onClick={dispatchComment}
                    className="w-full bg-rose-600 hover:bg-rose-500 disabled:bg-slate-850 text-white font-bold py-3.5 rounded-xl text-xs uppercase tracking-widest shadow-lg shadow-rose-950/20 cursor-pointer disabled:cursor-not-allowed transition-all mt-4"
                  >
                    {isLoading ? 'Processing...' : 'Execute manual action'}
                  </button>
                </div>
              )}

              {/* TAB 2: Create Issue Panel */}
              {activeTab === 'issue' && (
                <div className="space-y-5 animate-in fade-in duration-200">
                  <div className="space-y-1">
                    <h2 className="text-base font-bold text-slate-200 uppercase tracking-wider">Create Issue Workspace</h2>
                    <p className="text-xs text-slate-400">Open a new ticket issue on your GitHub repository tracker.</p>
                  </div>

                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="md:col-span-2 space-y-1.5">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Issue Title:</label>
                        <input
                          type="text"
                          value={issueData.title}
                          onChange={(e) => setIssueData({ ...issueData, title: e.target.value })}
                          placeholder="e.g. Broken authentication routing"
                          className="w-full bg-slate-950/50 border border-slate-850 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20"
                        />
                      </div>
                      <div className="md:col-span-2 space-y-1.5">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Explicit Command Required:</label>
                        <input
                          type="text"
                          readOnly
                          value="create issue"
                          className="w-full bg-slate-950 border border-slate-900 rounded-xl px-4 py-3 text-xs font-mono text-amber-500/80 cursor-not-allowed select-none"
                        />
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Labels (Comma Separated):</label>
                      <input
                        type="text"
                        value={issueData.labels}
                        onChange={(e) => setIssueData({ ...issueData, labels: e.target.value })}
                        placeholder="bug, high-priority, backend"
                        className="w-full bg-slate-950/50 border border-slate-850 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20 font-mono"
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Issue Body Description:</label>
                      <textarea
                        rows={4}
                        value={issueData.body}
                        onChange={(e) => setIssueData({ ...issueData, body: e.target.value })}
                        placeholder="Provide detailed reproduction steps..."
                        className="w-full bg-slate-950/50 border border-slate-855 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20 font-mono resize-none leading-relaxed"
                      />
                    </div>
                  </div>

                  <button
                    disabled={isLoading}
                    onClick={dispatchCreateIssue}
                    className="w-full bg-rose-600 hover:bg-rose-500 disabled:bg-slate-850 text-white font-bold py-3.5 rounded-xl text-xs uppercase tracking-widest shadow-lg shadow-rose-950/20 cursor-pointer disabled:cursor-not-allowed transition-all mt-4"
                  >
                    {isLoading ? 'Processing...' : 'Execute manual action'}
                  </button>
                </div>
              )}

              {/* TAB 3: PR Comment Panel */}
              {activeTab === 'pr' && (
                <div className="space-y-5 animate-in fade-in duration-200">
                  <div className="space-y-1">
                    <h2 className="text-base font-bold text-slate-200 uppercase tracking-wider">PR Comment Workspace</h2>
                    <p className="text-xs text-slate-400">Add operational comments or feedback on open Pull Requests.</p>
                  </div>

                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="md:col-span-1 space-y-1.5">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">PR Number (#):</label>
                        <input
                          type="number"
                          value={prData.prNumber}
                          onChange={(e) => setPrData({ ...prData, prNumber: e.target.value })}
                          placeholder="e.g. 12"
                          className="w-full bg-slate-950/50 border border-slate-850 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20 font-mono"
                        />
                      </div>
                      <div className="md:col-span-3 space-y-1.5">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Explicit Command Required:</label>
                        <input
                          type="text"
                          readOnly
                          value="create PR comment"
                          className="w-full bg-slate-950 border border-slate-900 rounded-xl px-4 py-3 text-xs font-mono text-amber-500/80 cursor-not-allowed select-none"
                        />
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">PR Comment Markdown:</label>
                      <textarea
                        rows={6}
                        value={prData.commentText}
                        onChange={(e) => setPrData({ ...prData, commentText: e.target.value })}
                        placeholder="Type Pull Request comment details..."
                        className="w-full bg-slate-950/50 border border-slate-855 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20 font-mono resize-none leading-relaxed"
                      />
                    </div>
                  </div>

                  <button
                    disabled={isLoading}
                    onClick={dispatchPRComment}
                    className="w-full bg-rose-600 hover:bg-rose-500 disabled:bg-slate-850 text-white font-bold py-3.5 rounded-xl text-xs uppercase tracking-widest shadow-lg shadow-rose-950/20 cursor-pointer disabled:cursor-not-allowed transition-all mt-4"
                  >
                    {isLoading ? 'Processing...' : 'Execute manual action'}
                  </button>
                </div>
              )}

              {/* TAB 4: Push Commit Panel */}
              {activeTab === 'commit' && (
                <div className="space-y-5 animate-in fade-in duration-200">
                  <div className="space-y-1">
                    <h2 className="text-base font-bold text-slate-200 uppercase tracking-wider">Push Changes Workspace</h2>
                    <p className="text-xs text-slate-400">Push updates directly to a specific repository path via the REST Commit APIs.</p>
                  </div>

                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-1.5">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">File Path:</label>
                        <input
                          type="text"
                          value={commitData.filePath}
                          onChange={(e) => setCommitData({ ...commitData, filePath: e.target.value })}
                          placeholder="src/custom-update.txt"
                          className="w-full bg-slate-950/50 border border-slate-850 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20 font-mono"
                        />
                      </div>
                      <div className="space-y-1.5">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Target Branch:</label>
                        <input
                          type="text"
                          value={commitData.branch}
                          onChange={(e) => setCommitData({ ...commitData, branch: e.target.value })}
                          placeholder="main"
                          className="w-full bg-slate-950/50 border border-slate-850 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20 font-mono"
                        />
                      </div>
                      <div className="space-y-1.5">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Explicit Command Required:</label>
                        <input
                          type="text"
                          readOnly
                          value="push these changes"
                          className="w-full bg-slate-950 border border-slate-900 rounded-xl px-4 py-3 text-xs font-mono text-amber-500/80 cursor-not-allowed select-none"
                        />
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Commit Message:</label>
                      <input
                        type="text"
                        value={commitData.commitMessage}
                        onChange={(e) => setCommitData({ ...commitData, commitMessage: e.target.value })}
                        placeholder="Integrate security checkpoints"
                        className="w-full bg-slate-950/50 border border-slate-850 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20"
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">File Content String:</label>
                      <textarea
                        rows={3}
                        value={commitData.fileContent}
                        onChange={(e) => setCommitData({ ...commitData, fileContent: e.target.value })}
                        placeholder="Input raw contents to write..."
                        className="w-full bg-slate-950/50 border border-slate-855 focus:border-rose-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-650 focus:outline-none focus:ring-1 focus:ring-rose-500/20 font-mono resize-none leading-relaxed"
                      />
                    </div>
                  </div>

                  <button
                    disabled={isLoading}
                    onClick={dispatchPushCommit}
                    className="w-full bg-rose-600 hover:bg-rose-500 disabled:bg-slate-850 text-white font-bold py-3.5 rounded-xl text-xs uppercase tracking-widest shadow-lg shadow-rose-950/20 cursor-pointer disabled:cursor-not-allowed transition-all mt-4"
                  >
                    {isLoading ? 'Processing...' : 'Execute manual action'}
                  </button>
                </div>
              )}

            </div>
          </div>
        </section>

        {/* Right Side Column: Real-Time Audit Logs Trail (5 columns) */}
        <section className="lg:col-span-5 flex flex-col gap-6">
          <div className="bg-slate-900/40 border border-slate-900/80 backdrop-blur-md rounded-2xl p-6 flex flex-col h-[650px] shadow-2xl relative">

            {/* Sidebar header */}
            <div className="flex items-center justify-between border-b border-slate-950 pb-4 mb-4">
              <div className="flex items-center gap-2 text-slate-200">
                <Database size={16} className="text-rose-400" />
                <h2 className="text-xs font-black tracking-widest uppercase">SECURITY AUDIT MONITOR</h2>
              </div>
              <button
                onClick={fetchLogs}
                className="p-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-400 hover:text-slate-100 hover:border-slate-700 transition-all cursor-pointer flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider"
              >
                <RefreshCw size={12} />
                Sync
              </button>
            </div>

            {/* Structured Log entries list */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-1 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
              {logs.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-2 border border-slate-950/30 rounded-xl bg-slate-950/10">
                  <Clock size={36} className="text-slate-700 animate-pulse" />
                  <p className="text-xs font-semibold text-slate-500 tracking-wider">NO RECENT ACTION TRAILS FOUND</p>
                  <p className="text-[10px] text-slate-650 max-w-xs">Audit trails will load dynamically here once manual confirmation checkpoints execute.</p>
                </div>
              ) : (
                logs.map((log, index) => (
                  <div
                    key={index}
                    className={`border rounded-xl p-3.5 space-y-2.5 transition-all bg-slate-950/50 ${!log.success
                        ? 'border-rose-500/20 shadow-inner'
                        : log.actionType.startsWith('BLOCKED')
                          ? 'border-amber-500/25'
                          : 'border-slate-850'
                      }`}
                  >
                    {/* Log Entry Title Line */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {log.success ? (
                          <span className="h-2 w-2 bg-emerald-400 rounded-full shadow-lg shadow-emerald-400/50"></span>
                        ) : (
                          <span className="h-2 w-2 bg-rose-500 rounded-full shadow-lg shadow-rose-500/50 animate-ping"></span>
                        )}
                        <span className="text-[10px] font-bold font-mono tracking-wide uppercase text-slate-200">
                          {log.actionType}
                        </span>
                      </div>

                      {/* Success/Error Badges */}
                      <span className={`text-[8px] font-black uppercase px-2 py-0.5 rounded tracking-widest ${log.success
                          ? 'bg-emerald-950/50 border border-emerald-500/20 text-emerald-400'
                          : 'bg-rose-950/50 border border-rose-500/20 text-rose-400'
                        }`}>
                        {log.success ? 'Success' : 'Rejected'}
                      </span>
                    </div>

                    {/* Metadata items list */}
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[10px] font-mono border-t border-slate-950 pt-2.5">
                      <div className="flex flex-col">
                        <span className="text-slate-500 text-[8px] uppercase tracking-wider">OPERATOR ROLE:</span>
                        <span className="text-slate-300 font-semibold uppercase">{log.operator}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-slate-500 text-[8px] uppercase tracking-wider">AFFECTED REPO:</span>
                        <span className="text-slate-300 font-semibold truncate max-w-[150px]">{log.repository}</span>
                      </div>
                      <div className="flex flex-col col-span-2">
                        <span className="text-slate-500 text-[8px] uppercase tracking-wider">TIMESTAMP:</span>
                        <span className="text-slate-350 text-[9px]">{new Date(log.timestamp).toLocaleString()}</span>
                      </div>
                    </div>

                    {/* Error logs detail */}
                    {!log.success && log.error && (
                      <div className="bg-rose-950/20 border border-rose-950/50 p-2.5 rounded-lg text-[10px] font-mono text-rose-300 flex items-start gap-2">
                        <Lock size={12} className="text-rose-400 mt-0.5 shrink-0" />
                        <span className="leading-normal">{log.error}</span>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* Logs warning summary footer */}
            <div className="bg-slate-950/60 border border-slate-900 p-3 rounded-xl flex items-center gap-3 text-[10px] text-slate-400 mt-4 leading-normal">
              <Lock size={16} className="text-rose-500/80 shrink-0" />
              <span>
                Actions trigger only after verifying exact explicit strings and role qualifications. All failures are logged permanently.
              </span>
            </div>

          </div>
        </section>

      </main>

      {/* Cyberpunk Status Footer bar */}
      <footer className="border-t border-slate-900 bg-slate-950/80 backdrop-blur-md px-6 py-3 flex flex-col md:flex-row items-center justify-between text-[10px] text-slate-500 font-mono gap-2">
        <span>© 2026 ANTIGRAVITY SECURITY MECHANISMS • SECURE INTEGRITY LAYER</span>
        <div className="flex items-center gap-4">
          <span>HOST: localhost:3000</span>
          <span>TARGET BRANCH: MAIN</span>
          <span className="text-rose-400 font-bold uppercase">STRICT MANUAL-FIRST ROUTING V1.0</span>
        </div>
      </footer>

    </div>
  );
}
