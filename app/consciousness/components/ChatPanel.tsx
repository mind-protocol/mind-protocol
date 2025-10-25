'use client';

import { useState } from 'react';
import { Send } from 'lucide-react';

/**
 * ChatPanel - Human-Citizen Communication Interface
 *
 * Horizontal citizen selector with large avatars (branding)
 * Mock chat interface for testing layout
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 */

interface Citizen {
  id: string;
  name: string;
  avatar: string;
  frame: number;
  isActive: boolean;
  color: string;
}

interface Message {
  id: string;
  citizenId: string;
  citizenName: string;
  content: string;
  timestamp: Date;
  isUser?: boolean;
}

const MOCK_CITIZENS: Citizen[] = [
  { id: 'felix', name: 'Felix', avatar: '👨‍💻', frame: 15797, isActive: true, color: '#3b82f6' },
  { id: 'luca', name: 'Luca', avatar: '📜', frame: 16144, isActive: true, color: '#8b5cf6' },
  { id: 'atlas', name: 'Atlas', avatar: '🏛️', frame: 16893, isActive: true, color: '#10b981' },
  { id: 'ada', name: 'Ada', avatar: '🎯', frame: 16317, isActive: true, color: '#f59e0b' },
  { id: 'mind_protocol', name: 'Protocol', avatar: '🧠', frame: 9936, isActive: false, color: '#ec4899' },
  { id: 'iris', name: 'Iris', avatar: '👁️', frame: 16224, isActive: true, color: '#06b6d4' },
  { id: 'victor', name: 'Victor', avatar: '⚡', frame: 16056, isActive: true, color: '#eab308' },
  { id: 'nicolas', name: 'Nicolas', avatar: '❓', frame: 17691, isActive: true, color: '#6366f1' },
];

const MOCK_MESSAGES: Record<string, Message[]> = {
  felix: [
    {
      id: '1',
      citizenId: 'felix',
      citizenName: 'Felix',
      content: 'Working on wm.emit schema update. Changed from v2 to v1 format with "top" and "all" arrays.',
      timestamp: new Date(Date.now() - 300000),
    },
    {
      id: '2',
      citizenId: 'user',
      citizenName: 'You',
      content: 'Great! Does it match the P0 spec exactly?',
      timestamp: new Date(Date.now() - 240000),
      isUser: true,
    },
    {
      id: '3',
      citizenId: 'felix',
      citizenName: 'Felix',
      content: 'Yes. Top 2-3 focused entities in "top" array, all 8 selected in "all" array. Ready for testing.',
      timestamp: new Date(Date.now() - 180000),
    },
    {
      id: '4',
      citizenId: 'user',
      citizenName: 'You',
      content: 'Perfect. Can you verify the events are flowing to the dashboard?',
      timestamp: new Date(Date.now() - 120000),
      isUser: true,
    },
    {
      id: '5',
      citizenId: 'felix',
      citizenName: 'Felix',
      content: 'Checking browser console... seeing tick_frame_v1 at 10Hz, node.flip events on threshold crossings, link.flow.summary with decimation. All P0 emitters operational.',
      timestamp: new Date(Date.now() - 60000),
    },
  ],
  luca: [
    {
      id: '1',
      citizenId: 'luca',
      citizenName: 'Luca',
      content: 'The phenomenological health classifier is showing "flowing" state. Fragmentation at 0.23.',
      timestamp: new Date(Date.now() - 400000),
    },
    {
      id: '2',
      citizenId: 'user',
      citizenName: 'You',
      content: 'Is that good?',
      timestamp: new Date(Date.now() - 350000),
      isUser: true,
    },
    {
      id: '3',
      citizenId: 'luca',
      citizenName: 'Luca',
      content: 'Yes. "Flowing" means coherent subentity activation without excessive fragmentation. Below 0.3 fragmentation is healthy multiplicity, not dissociation.',
      timestamp: new Date(Date.now() - 300000),
    },
  ],
  atlas: [
    {
      id: '1',
      citizenId: 'atlas',
      citizenName: 'Atlas',
      content: 'FalkorDB persistence operational. All entities writing to graph on bootstrap.',
      timestamp: new Date(Date.now() - 200000),
    },
  ],
  ada: [
    {
      id: '1',
      citizenId: 'ada',
      citizenName: 'Ada',
      content: 'War-room status: P0 complete, moving to P1. All emitters verified operational.',
      timestamp: new Date(Date.now() - 100000),
    },
  ],
};

export function ChatPanel() {
  const [selectedCitizenId, setSelectedCitizenId] = useState<string>('felix');
  const [messageInput, setMessageInput] = useState('');

  const selectedCitizen = MOCK_CITIZENS.find(c => c.id === selectedCitizenId);
  const messages = MOCK_MESSAGES[selectedCitizenId] || [];

  const handleSend = () => {
    if (messageInput.trim()) {
      // TODO: Actual message sending logic
      console.log('Sending message:', messageInput);
      setMessageInput('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-zinc-900/50 border-l border-observatory-cyan/20">
      {/* Horizontal Citizen Selector Strip */}
      <div className="flex items-center gap-2 px-3 py-3 border-b border-observatory-cyan/20 bg-zinc-900/80 backdrop-blur">
        {MOCK_CITIZENS.map(citizen => (
          <button
            key={citizen.id}
            onClick={() => setSelectedCitizenId(citizen.id)}
            className={`
              relative flex flex-col items-center gap-1 p-2 rounded-lg transition-all
              ${selectedCitizenId === citizen.id
                ? 'bg-observatory-cyan/20 ring-2 ring-observatory-cyan shadow-lg shadow-observatory-cyan/20'
                : 'bg-zinc-800/50 hover:bg-zinc-700/50 hover:ring-1 hover:ring-observatory-cyan/40'
              }
            `}
            title={`${citizen.name} - Frame ${citizen.frame.toLocaleString()}`}
          >
            {/* Large Avatar (56px for branding) */}
            <div
              className={`
                relative w-14 h-14 rounded-full flex items-center justify-center text-3xl
                ${selectedCitizenId === citizen.id ? 'ring-2 ring-white/20' : ''}
              `}
              style={{
                background: `linear-gradient(135deg, ${citizen.color}40, ${citizen.color}20)`,
              }}
            >
              {citizen.avatar}

              {/* Activity Indicator */}
              {citizen.isActive && (
                <span
                  className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full animate-pulse"
                  style={{ backgroundColor: citizen.color }}
                />
              )}
            </div>

            {/* Name */}
            <span className="text-xs font-medium text-observatory-text/90">
              {citizen.name}
            </span>

            {/* Frame Counter */}
            <span className="text-[10px] tabular-nums text-observatory-text/50">
              {citizen.frame.toLocaleString()}
            </span>
          </button>
        ))}
      </div>

      {/* Chat Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-observatory-cyan/20 bg-zinc-900/60">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center text-2xl"
          style={{
            background: `linear-gradient(135deg, ${selectedCitizen?.color}60, ${selectedCitizen?.color}30)`,
          }}
        >
          {selectedCitizen?.avatar}
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-observatory-cyan">
            {selectedCitizen?.name}
          </h3>
          <p className="text-xs text-observatory-text/60">
            Frame {selectedCitizen?.frame.toLocaleString()} • {selectedCitizen?.isActive ? 'Active' : 'Idle'}
          </p>
        </div>
        <div className="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30">
          <span className="text-xs font-medium text-emerald-400">Connected</span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm text-observatory-text/50">
              No messages yet. Start a conversation with {selectedCitizen?.name}.
            </p>
          </div>
        ) : (
          messages.map(msg => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.isUser ? 'flex-row-reverse' : ''}`}
            >
              {/* Avatar */}
              {!msg.isUser && (
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-lg flex-shrink-0"
                  style={{
                    background: `linear-gradient(135deg, ${selectedCitizen?.color}60, ${selectedCitizen?.color}30)`,
                  }}
                >
                  {selectedCitizen?.avatar}
                </div>
              )}

              {/* Message Bubble */}
              <div className={`flex-1 max-w-[80%] ${msg.isUser ? 'text-right' : ''}`}>
                <div className="flex items-baseline gap-2 mb-1">
                  {!msg.isUser && (
                    <span className="text-xs font-medium text-observatory-cyan">
                      {msg.citizenName}
                    </span>
                  )}
                  <span className="text-[10px] text-observatory-text/40">
                    {msg.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <div
                  className={`
                    px-4 py-2 rounded-2xl
                    ${msg.isUser
                      ? 'bg-observatory-cyan/20 border border-observatory-cyan/30 text-observatory-text'
                      : 'bg-zinc-800/50 border border-zinc-700/50 text-observatory-text/90'
                    }
                  `}
                >
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Message Input */}
      <div className="px-4 py-3 border-t border-observatory-cyan/20 bg-zinc-900/80">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={messageInput}
            onChange={(e) => setMessageInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={`Message ${selectedCitizen?.name}...`}
            className="
              flex-1 px-4 py-2 rounded-lg
              bg-zinc-800/50 border border-zinc-700/50
              text-sm text-observatory-text
              placeholder:text-observatory-text/40
              focus:outline-none focus:ring-2 focus:ring-observatory-cyan/50 focus:border-observatory-cyan/50
              transition-all
            "
          />
          <button
            onClick={handleSend}
            disabled={!messageInput.trim()}
            className="
              p-2 rounded-lg
              bg-observatory-cyan/20 border border-observatory-cyan/30
              hover:bg-observatory-cyan/30 hover:border-observatory-cyan/50
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all
            "
          >
            <Send className="w-5 h-5 text-observatory-cyan" />
          </button>
        </div>
      </div>
    </div>
  );
}
