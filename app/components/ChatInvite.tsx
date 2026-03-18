'use client';

import { useState, useRef } from 'react';

interface ChatInviteProps {
  citizenName: string;
  citizenHandle: string;
}

export default function ChatInvite({ citizenName, citizenHandle }: ChatInviteProps) {
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [hasRecording, setHasRecording] = useState(false);
  const [showVocalMessage, setShowVocalMessage] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const initial = citizenName.charAt(0).toUpperCase();

  function handleSendText(e: React.FormEvent) {
    e.preventDefault();
    const text = message.trim();
    if (!text) return;

    const prefixed = `[@${citizenHandle}] ${text}`;
    const encoded = encodeURIComponent(prefixed);
    window.trackEvent?.('chat_click', { citizen: citizenHandle });
    window.open(`https://wa.me/?text=${encoded}`, '_blank');
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = () => {
        // Voice data captured — placeholder for future implementation
      };

      recorder.onstop = () => {
        // Clean up the stream tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
        setIsRecording(false);
        setHasRecording(true);
      };

      recorder.start();
      setIsRecording(true);
      setHasRecording(false);
      setShowVocalMessage(false);
    } catch {
      // Microphone access denied or unavailable
      setShowVocalMessage(true);
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  }

  function handleSendVocal() {
    setShowVocalMessage(true);
    setHasRecording(false);
  }

  function cancelRecording() {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    setHasRecording(false);
    setIsRecording(false);
    setShowVocalMessage(false);
  }

  return (
    <div className="bg-[#1a1a3e] rounded-xl border border-white/10 overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10">
        <div className="w-9 h-9 rounded-full bg-[#a78bfa]/20 flex items-center justify-center text-[#a78bfa] font-bold text-sm shrink-0">
          {initial}
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-white truncate">{citizenName}</p>
          <p className="text-xs text-white/40">@{citizenHandle}</p>
        </div>
        <span className="ml-auto text-[#25D366] text-xs flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-[#25D366] inline-block" />
          En ligne
        </span>
      </div>

      {/* Chat body */}
      <div className="px-5 py-5 space-y-4">
        {/* Default citizen prompt */}
        <div className="flex items-start gap-3">
          <div className="w-7 h-7 rounded-full bg-[#a78bfa]/20 flex items-center justify-center text-[#a78bfa] font-bold text-xs shrink-0 mt-0.5">
            {initial}
          </div>
          <div className="bg-white/5 rounded-xl rounded-tl-none px-4 py-3 max-w-[85%]">
            <p className="text-sm text-white/80">Envoie-moi un message, je suis l&agrave;</p>
          </div>
        </div>

        {/* Vocal placeholder message */}
        {showVocalMessage && (
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-full bg-[#a78bfa]/20 flex items-center justify-center text-[#a78bfa] font-bold text-xs shrink-0 mt-0.5">
              {initial}
            </div>
            <div className="bg-[#a78bfa]/10 rounded-xl rounded-tl-none px-4 py-3 max-w-[85%]">
              <p className="text-sm text-[#c4b5fd]">Les vocaux arrivent bient&ocirc;t</p>
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="px-4 pb-4">
        {/* Recording state */}
        {isRecording && (
          <div className="flex items-center gap-3 mb-3 px-3 py-2.5 bg-red-500/10 border border-red-500/20 rounded-lg">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
            <span className="text-sm text-red-400 flex-1">Enregistrement en cours...</span>
            <button
              onClick={stopRecording}
              className="text-xs text-white/60 hover:text-white transition px-2 py-1 rounded bg-white/10"
            >
              Arr&ecirc;ter
            </button>
            <button
              onClick={cancelRecording}
              className="text-xs text-red-400 hover:text-red-300 transition px-2 py-1"
            >
              Annuler
            </button>
          </div>
        )}

        {/* Send vocal button after recording */}
        {hasRecording && !isRecording && (
          <div className="flex items-center gap-2 mb-3">
            <button
              onClick={handleSendVocal}
              className="flex-1 bg-[#a78bfa] text-white text-sm font-semibold py-2.5 rounded-lg hover:bg-[#8b5cf6] transition"
            >
              Envoyer le vocal
            </button>
            <button
              onClick={cancelRecording}
              className="text-sm text-white/40 hover:text-white/70 transition px-3 py-2.5"
            >
              Annuler
            </button>
          </div>
        )}

        {/* Text input + buttons */}
        {!isRecording && !hasRecording && (
          <form onSubmit={handleSendText} className="flex items-center gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={`Message pour ${citizenName}...`}
              className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white placeholder-white/30 focus:outline-none focus:border-[#a78bfa]/50 transition"
            />
            <button
              type="button"
              onClick={startRecording}
              title="Enregistrer un vocal"
              className="w-10 h-10 flex items-center justify-center rounded-lg bg-white/5 border border-white/10 text-white/50 hover:text-[#a78bfa] hover:border-[#a78bfa]/30 transition shrink-0"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" y1="19" x2="12" y2="23" />
                <line x1="8" y1="23" x2="16" y2="23" />
              </svg>
            </button>
            <button
              type="submit"
              disabled={!message.trim()}
              className="w-10 h-10 flex items-center justify-center rounded-lg bg-[#a78bfa] text-white hover:bg-[#8b5cf6] transition disabled:opacity-30 disabled:cursor-not-allowed shrink-0"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </form>
        )}

        <p className="text-[10px] text-white/20 text-center mt-3">
          Via WhatsApp &middot; Mind Protocol
        </p>
      </div>
    </div>
  );
}
