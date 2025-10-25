'use client';

import { useState } from 'react';
import { Send } from 'lucide-react';

/**
 * ChatPanel - Human-Citizen Communication Interface
 *
 * Horizontal citizen selector with large REAL profile pictures (branding)
 * Mock chat interface for testing layout
 * Clicking citizen switches the graph view
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 */

interface Citizen {
  id: string;
  name: string;
  frame: number;
  isActive: boolean;
  color: string;
}

interface ChatPanelProps {
  onSelectCitizen?: (citizenId: string) => void;
  activeCitizenId?: string;
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
  { id: 'felix', name: 'Felix', frame: 15797, isActive: true, color: '#3b82f6' },
  { id: 'luca', name: 'Luca', frame: 16144, isActive: true, color: '#8b5cf6' },
  { id: 'atlas', name: 'Atlas', frame: 16893, isActive: true, color: '#10b981' },
  { id: 'ada', name: 'Ada', frame: 16317, isActive: true, color: '#f59e0b' },
  { id: 'mind_protocol', name: 'Protocol', frame: 9936, isActive: false, color: '#ec4899' },
  { id: 'iris', name: 'Iris', frame: 16224, isActive: true, color: '#06b6d4' },
  { id: 'victor', name: 'Victor', frame: 16056, isActive: true, color: '#eab308' },
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

export function ChatPanel({ onSelectCitizen, activeCitizenId }: ChatPanelProps) {
  const [selectedCitizenId, setSelectedCitizenId] = useState<string>(activeCitizenId || 'felix');
  const [messageInput, setMessageInput] = useState('');

  const selectedCitizen = MOCK_CITIZENS.find(c => c.id === selectedCitizenId);
  const messages = MOCK_MESSAGES[selectedCitizenId] || [];

  const handleCitizenClick = (citizenId: string) => {
    setSelectedCitizenId(citizenId);
    // Switch graph view
    if (onSelectCitizen) {
      onSelectCitizen(citizenId);
    }
  };

  const handleSend = () => {
    if (messageInput.trim()) {
      // TODO: Actual message sending logic
      console.log('Sending message:', messageInput);
      setMessageInput('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-zinc-900 border-l border-observatory-cyan/20 font-sans">
      {/* Horizontal Citizen Selector Strip */}
      <div className="flex items-center gap-2 px-3 py-3 border-b border-observatory-cyan/20 bg-zinc-900">
        {MOCK_CITIZENS.map(citizen => (
          <button
            key={citizen.id}
            onClick={() => handleCitizenClick(citizen.id)}
            className={`
              relative flex flex-col items-center gap-1 p-2 rounded-lg transition-all
              ${selectedCitizenId === citizen.id
                ? 'bg-observatory-cyan/20 ring-2 ring-observatory-cyan shadow-lg shadow-observatory-cyan/20'
                : 'bg-zinc-800/50 hover:bg-zinc-700/50 hover:ring-1 hover:ring-observatory-cyan/40'
              }
            `}
            title={`${citizen.name} - Frame ${citizen.frame.toLocaleString()}`}
          >
            {/* Large Avatar (80px for branding) - REAL PROFILE PICTURE */}
            <div
              className={`
                relative w-20 h-20 rounded-full overflow-hidden
                ${selectedCitizenId === citizen.id ? 'ring-2 ring-white/20' : ''}
              `}
            >
              <img
                src={`/citizens/${citizen.id}/avatar.png`}
                alt={`${citizen.name} avatar`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  // Fallback to colored circle with initial if image fails
                  e.currentTarget.style.display = 'none';
                  const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                  if (fallback) fallback.style.display = 'flex';
                }}
              />
              {/* Fallback for missing images */}
              <div
                className="w-full h-full flex items-center justify-center text-2xl font-bold text-white"
                style={{
                  background: `linear-gradient(135deg, ${citizen.color}, ${citizen.color}80)`,
                  display: 'none'
                }}
              >
                {citizen.name[0]}
              </div>

              {/* Activity Indicator */}
              {citizen.isActive && (
                <span
                  className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full animate-pulse ring-2 ring-zinc-900"
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
              {citizen.frame.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')}
            </span>
          </button>
        ))}
      </div>

      {/* Messages Area (no redundant header - citizen already highlighted in selector) */}
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
                <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0">
                  <img
                    src={`/citizens/${selectedCitizenId}/avatar.png`}
                    alt={`${selectedCitizen?.name} avatar`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'flex';
                    }}
                  />
                  <div
                    className="w-full h-full flex items-center justify-center text-sm font-bold text-white"
                    style={{
                      background: `linear-gradient(135deg, ${selectedCitizen?.color}60, ${selectedCitizen?.color}30)`,
                      display: 'none'
                    }}
                  >
                    {selectedCitizen?.name[0]}
                  </div>
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

      {/* Message Input - Multi-line (Shift+Enter for new line, Enter to send) */}
      <div className="px-4 py-3 border-t border-observatory-cyan/20 bg-zinc-900">
        <div className="flex items-end gap-2">
          <textarea
            value={messageInput}
            onChange={(e) => setMessageInput(e.target.value)}
            onKeyDown={(e) => {
              // Enter without Shift = send
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
              // Shift+Enter = new line (default textarea behavior)
            }}
            placeholder={`Message ${selectedCitizen?.name}... (Shift+Enter for new line)`}
            rows={3}
            className="
              flex-1 px-4 py-2 rounded-lg resize-none font-sans
              bg-zinc-800/50 border border-zinc-700/50
              text-sm text-observatory-text
              placeholder:text-observatory-text/40
              focus:outline-none focus:ring-2 focus:ring-observatory-cyan/50 focus:border-observatory-cyan/50
              transition-all
              max-h-[120px] overflow-y-auto
            "
            style={{
              minHeight: '72px',
              maxHeight: '120px' // ~5 lines max
            }}
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
