'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Send } from 'lucide-react';
import { useConversationPersistence } from '../hooks/useConversationPersistence';
import { useWebSocket } from '../hooks/useWebSocket';
import { WebSocketState } from '../hooks/websocket-types';

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

type MessageStatus = 'pending' | 'accepted' | 'rejected';

interface Message {
  id: string;
  citizenId: string;
  citizenName: string;
  content: string;
  timestamp: Date;
  isUser?: boolean;
  stimulusId?: string;
  status?: MessageStatus;
  errorReason?: string;
}

const STATIC_CITIZENS: Citizen[] = [
  { id: 'mind-protocol_felix', name: 'Felix', frame: 15797, isActive: true, color: '#3b82f6' },
  { id: 'mind-protocol_luca', name: 'Luca', frame: 16144, isActive: true, color: '#8b5cf6' },
  { id: 'mind-protocol_atlas', name: 'Atlas', frame: 16893, isActive: true, color: '#10b981' },
  { id: 'mind-protocol_ada', name: 'Ada', frame: 16317, isActive: true, color: '#f59e0b' },
  { id: 'mind-protocol', name: 'Protocol', frame: 9936, isActive: false, color: '#ec4899' },
  { id: 'mind-protocol_iris', name: 'Iris', frame: 16224, isActive: true, color: '#06b6d4' },
  { id: 'mind-protocol_victor', name: 'Victor', frame: 16056, isActive: true, color: '#eab308' },
];

const COLOR_PALETTE = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899', '#06b6d4', '#eab308'];

const STATIC_COLOR_LOOKUP = STATIC_CITIZENS.reduce<Record<string, string>>((acc, citizen) => {
  acc[citizen.id] = citizen.color;
  return acc;
}, {});

const STATUS_LABEL: Record<MessageStatus, string> = {
  pending: 'sending…',
  accepted: 'delivered',
  rejected: 'rejected',
};

export function ChatPanel({ onSelectCitizen, activeCitizenId }: ChatPanelProps) {
  const defaultCitizen = activeCitizenId && STATIC_CITIZENS.some(c => c.id === activeCitizenId)
    ? activeCitizenId
    : STATIC_CITIZENS[0]?.id ?? 'felix';

  const [selectedCitizenId, setSelectedCitizenId] = useState<string>(defaultCitizen);
  const [messageInput, setMessageInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [messages, setMessages] = useState<Record<string, Message[]>>({});
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
  const responsesCursorRef = useRef(0);

  const {
    injectStimulus,
    citizenResponses,
    lastInjectAck,
    connectionState,
    hierarchySnapshot
  } = useWebSocket();

  const citizens = useMemo<Citizen[]>(() => {
    if (hierarchySnapshot?.citizens?.length) {
      return hierarchySnapshot.citizens.map((citizen, idx) => ({
        id: citizen.id,
        name: citizen.label ?? citizen.id,
        frame: 0,
        isActive: citizen.status === 'ready' || citizen.status === 'busy',
        color: STATIC_COLOR_LOOKUP[citizen.id] ?? COLOR_PALETTE[idx % COLOR_PALETTE.length]
      }));
    }
    return STATIC_CITIZENS;
  }, [hierarchySnapshot]);

  const { addMessage } = useConversationPersistence({
    citizenId: selectedCitizenId,
    autoSaveThreshold: 5,
  });

  const selectedCitizen = useMemo(
    () => citizens.find(c => c.id === selectedCitizenId),
    [citizens, selectedCitizenId]
  );

  const currentMessages = messages[selectedCitizenId] ?? [];
  const isConnected = connectionState === WebSocketState.CONNECTED;

  const appendMessage = useCallback((citizenId: string, message: Message) => {
    setMessages(prev => {
      const existing = prev[citizenId] ?? [];
      return {
        ...prev,
        [citizenId]: [...existing, message]
      };
    });
  }, []);

  useEffect(() => {
    if (!citizens.length) return;
    if (!citizens.find(c => c.id === selectedCitizenId)) {
      setSelectedCitizenId(citizens[0].id);
    }
  }, [citizens, selectedCitizenId]);

  // Collect citizen.responses from the shared bus singleton
  useEffect(() => {
    if (!citizenResponses.length) return;

    const startIdx = responsesCursorRef.current;
    if (startIdx >= citizenResponses.length) {
      return;
    }

    const fresh = citizenResponses.slice(startIdx);
    responsesCursorRef.current = citizenResponses.length;

    fresh.forEach(response => {
      if (!response?.citizenId || !response.content) {
        return;
      }

      const responder = citizens.find(c => c.id === response.citizenId);
      appendMessage(response.citizenId, {
        id: `response_${response.citizenId}_${response.timestamp}`,
        citizenId: response.citizenId,
        citizenName: responder?.name ?? response.citizenId,
        content: response.content,
        timestamp: new Date(response.timestamp || Date.now()),
        isUser: false
      });

      if (response.citizenId === selectedCitizenId) {
        setIsWaitingForResponse(false);
      }
    });
  }, [appendMessage, citizenResponses, selectedCitizenId, citizens]);

  // Track delivery acknowledgements for UI feedback
  useEffect(() => {
    if (!lastInjectAck) return;

    setMessages(prev => {
      let didChange = false;
      const next: Record<string, Message[]> = {};

      for (const [citizenId, list] of Object.entries(prev)) {
        const updated = list.map(msg => {
          if (msg.stimulusId === lastInjectAck.id) {
            didChange = true;
            return {
              ...msg,
              status: lastInjectAck.status,
              errorReason: lastInjectAck.reason
            };
          }
          return msg;
        });
        next[citizenId] = updated;
      }

      return didChange ? next : prev;
    });

    if (lastInjectAck.status === 'rejected') {
      setSendError(lastInjectAck.reason ?? 'Stimulus rejected by membrane');
      setIsWaitingForResponse(false);
    } else if (lastInjectAck.status === 'accepted') {
      setSendError(null);
    }
  }, [lastInjectAck]);

  const handleCitizenClick = (citizenId: string) => {
    setSelectedCitizenId(citizenId);
    if (onSelectCitizen) {
      onSelectCitizen(citizenId);
    }
  };

  const handleSend = async () => {
    const trimmed = messageInput.trim();
    if (!trimmed || isSending) return;

    setIsSending(true);
    setSendError(null);
    setMessageInput('');

    try {
      const stimulusId = injectStimulus({
        channel: 'ui.action.user_prompt',
        dedupe_key: `chat:${selectedCitizenId}:${trimmed.slice(0, 64)}`,
        intent_merge_key: `chat:${selectedCitizenId}`,
        origin_chain: ['ui:chat', `citizen:${selectedCitizenId}`],
        payload: {
          text: trimmed,
          citizen_id: selectedCitizenId
        }
      });

      appendMessage(selectedCitizenId, {
        id: `user_${stimulusId}`,
        citizenId: selectedCitizenId,
        citizenName: 'You',
        content: trimmed,
        timestamp: new Date(),
        isUser: true,
        stimulusId,
        status: 'pending'
      });

      addMessage('human', trimmed);
      setIsWaitingForResponse(true);
    } catch (err) {
      console.error('[ChatPanel] Failed to inject stimulus', err);
      setSendError(err instanceof Error ? err.message : 'Failed to send message');
      setMessageInput(trimmed);
      setIsWaitingForResponse(false);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="fixed top-16 right-0 bottom-0 w-[26rem] max-w-full z-30 consciousness-panel border-l border-observatory-cyan/20 flex flex-col font-sans overflow-hidden bg-zinc-900/90">
      <div className="flex items-center gap-2 px-3 py-3 border-b border-observatory-cyan/20 bg-zinc-900">
        {STATIC_CITIZENS.map(citizen => (
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
            title={`${citizen.name} • Frame ${citizen.frame}`}
          >
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
                  e.currentTarget.style.display = 'none';
                  const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                  if (fallback) fallback.style.display = 'flex';
                }}
              />
              <div
                className="w-full h-full flex items-center justify-center text-2xl font-bold text-white"
                style={{
                  background: `linear-gradient(135deg, ${citizen.color}, ${citizen.color}80)`,
                  display: 'none'
                }}
              >
                {citizen.name[0]}
              </div>

              {citizen.isActive && (
                <span
                  className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full animate-pulse ring-2 ring-zinc-900"
                  style={{ backgroundColor: citizen.color }}
                />
              )}
            </div>

            <span className="text-xs font-medium text-observatory-text/90">
              {citizen.name}
            </span>
            <span className="text-[10px] tabular-nums text-observatory-text/50">
              {citizen.frame}
            </span>
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {currentMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm text-observatory-text/50">
              No messages yet. Start a conversation with {selectedCitizen?.name ?? 'the citizen'}.
            </p>
          </div>
        ) : (
          <>
            {currentMessages.map(msg => {
              const citizenColor = citizens.find(c => c.id === msg.citizenId)?.color ?? '#4b5563';
              return (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${msg.isUser ? 'flex-row-reverse' : ''}`}
                >
                  {!msg.isUser && (
                    <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0">
                      <img
                        src={`/citizens/${msg.citizenId}/avatar.png`}
                        alt={`${msg.citizenName} avatar`}
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
                          background: `linear-gradient(135deg, ${citizenColor}60, ${citizenColor}30)`,
                          display: 'none'
                        }}
                      >
                        {msg.citizenName[0] ?? '?'}
                      </div>
                    </div>
                  )}

                  <div className={`flex-1 max-w-[80%] ${msg.isUser ? 'text-right' : ''}`}>
                    <div className="flex items-baseline gap-2 mb-1 justify-between">
                      <span className="text-xs font-medium text-observatory-cyan">
                        {msg.isUser ? 'You' : msg.citizenName}
                      </span>
                      <span className="text-[10px] text-observatory-text/40">
                        {msg.timestamp.toISOString().slice(11, 19)}
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
                      <p className="text-sm leading-relaxed whitespace-pre-line">{msg.content}</p>
                      {msg.isUser && msg.status && (
                        <p className="mt-1 text-[10px] uppercase tracking-wide text-observatory-text/50">
                          {STATUS_LABEL[msg.status]}
                          {msg.status === 'rejected' && msg.errorReason ? ` – ${msg.errorReason}` : ''}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {isWaitingForResponse && (
              <div className="flex gap-3 animate-pulse">
                <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0 opacity-60">
                  <img
                    src={`/citizens/${selectedCitizenId}/avatar.png`}
                    alt={`${selectedCitizen?.name ?? 'Citizen'} avatar`}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1 max-w-[80%]">
                  <div className="flex items-baseline gap-2 mb-1">
                    <span className="text-xs font-medium text-observatory-cyan/70">
                      {selectedCitizen?.name ?? 'Citizen'}
                    </span>
                    <span className="text-[10px] text-observatory-text/40">
                      thinking…
                    </span>
                  </div>
                  <div className="px-4 py-2 rounded-2xl bg-zinc-800/30 border border-zinc-700/30">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 rounded-full bg-observatory-cyan/50 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 rounded-full bg-observatory-cyan/50 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 rounded-full bg-observatory-cyan/50 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <div className="px-4 py-3 border-t border-observatory-cyan/20 bg-zinc-900">
        {sendError && (
          <div className="mb-2 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs">
            ⚠️ {sendError}
          </div>
        )}

        <div className="flex items-end gap-2">
          <textarea
            value={messageInput}
            onChange={(e) => setMessageInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder={
              isConnected
                ? `Message ${selectedCitizen?.name ?? 'the citizen'}... (Shift+Enter for new line)`
                : 'Connecting to membrane...'
            }
            rows={3}
            disabled={isSending || !isConnected}
            className="
              flex-1 px-4 py-2 rounded-lg resize-none font-sans
              bg-zinc-800/50 border border-zinc-700/50
              text-sm text-observatory-text
              placeholder:text-observatory-text/40
              focus:outline-none focus:ring-2 focus:ring-observatory-cyan/50 focus:border-observatory-cyan/50
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all
              max-h-[120px] overflow-y-auto
            "
            style={{ minHeight: '72px', maxHeight: '120px' }}
          />
          <button
            onClick={handleSend}
            disabled={!messageInput.trim() || isSending || !isConnected}
            className="
              p-2 rounded-lg
              bg-observatory-cyan/20 border border-observatory-cyan/30
              hover:bg-observatory-cyan/30 hover:border-observatory-cyan/50
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all
            "
            title={
              !isConnected
                ? 'Membrane connection unavailable'
                : isSending
                  ? 'Sending...'
                  : 'Send message'
            }
          >
            {isSending ? (
              <div className="w-5 h-5 border-2 border-observatory-cyan/30 border-t-observatory-cyan rounded-full animate-spin" />
            ) : (
              <Send className="w-5 h-5 text-observatory-cyan" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
