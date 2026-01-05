import React, { useState, useEffect, useRef } from 'react'
import UploadForm from './components/UploadForm'
import JobList from './components/JobList'
import JobDetails from './components/JobDetails'
import './App.css'

function App() {
  // --- OG AUTHOR'S STATE & LOGIC ---
  const [selectedJobId, setSelectedJobId] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleUploadSuccess = (jobId) => {
    setSelectedJobId(jobId)
    setRefreshTrigger(prev => prev + 1)
  }

  // --- YOUR CHATBOT LOGIC ---
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Neural Engine initialized. How can I assist with your resume deployment?' }
  ]);
  const [input, setInput] = useState("");
  const socket = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket - Using jobId 1 as default for now
    socket.current = new WebSocket("ws://localhost:8000/ws/chat/1");
    socket.current.onmessage = (event) => {
      setMessages((prev) => [...prev, { role: 'ai', content: event.data }]);
    };
    return () => {
      if (socket.current) socket.current.close();
    };
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = (e) => {
    e.preventDefault();
    if (input.trim() && socket.current) {
      socket.current.send(input);
      setMessages((prev) => [...prev, { role: 'user', content: input }]);
      setInput("");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* HEADER SECTION (OG Author's) */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Resume Processing Pipeline
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Upload resumes, process with AI, and generate deployable portfolios
          </p>
        </div>
      </header>

      {/* MAIN CONTENT AREA (OG Author's Layout) */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column: Upload & Job List */}
          <div className="lg:col-span-1 space-y-6">
            <UploadForm onUploadSuccess={handleUploadSuccess} />
            <JobList 
              selectedJobId={selectedJobId}
              onSelectJob={setSelectedJobId}
              refreshTrigger={refreshTrigger}
            />
          </div>

          {/* Right Column: Job Details */}
          <div className="lg:col-span-2">
            {selectedJobId ? (
              <JobDetails 
                jobId={selectedJobId}
                onRefresh={() => setRefreshTrigger(prev => prev + 1)}
              />
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                Select a job from the list to view processing details
              </div>
            )}
          </div>
        </div>
      </main>

      {/* --- FLOATING CHATBOT (Your Feature) --- */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
        {isChatOpen && (
          <div className="mb-4 w-80 md:w-96 h-[500px] bg-slate-900/95 border border-white/10 rounded-2xl backdrop-blur-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
            {/* Chat Header */}
            <div className="p-4 border-b border-white/5 bg-white/5 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-blue-400">Neural_Assistant_v1</span>
              </div>
              <button onClick={() => setIsChatOpen(false)} className="text-slate-500 hover:text-white transition-colors">✕</button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-slate-700">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed ${
                    msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-none shadow-[0_0_15px_rgba(37,99,235,0.2)]' 
                    : 'bg-slate-800/50 text-slate-200 border border-white/5 rounded-bl-none backdrop-blur-md'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              <div ref={scrollRef} />
            </div>

            {/* Chat Input */}
            <form onSubmit={sendMessage} className="p-4 border-t border-white/5 bg-slate-950/50">
              <input 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Query system..."
                className="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all placeholder:text-slate-600"
              />
            </form>
          </div>
        )}

        {/* Floating Toggle Button */}
        <button 
          onClick={() => setIsChatOpen(!isChatOpen)}
          className="w-14 h-14 bg-blue-600 hover:bg-blue-500 rounded-full flex items-center justify-center shadow-[0_0_30px_rgba(37,99,235,0.4)] hover:shadow-[0_0_40px_rgba(37,99,235,0.6)] transition-all active:scale-90 group"
        >
          {isChatOpen ? (
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
          ) : (
            <div className="relative">
               <svg className="w-6 h-6 text-white group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
               <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-blue-400 rounded-full border-2 border-blue-600"></span>
            </div>
          )}
        </button>
      </div>
    </div>
  )
}

export default App