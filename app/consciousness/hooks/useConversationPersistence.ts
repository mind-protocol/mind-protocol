/**
 * useConversationPersistence - Hook for auto-saving chat conversations to graph
 *
 * Tracks conversation messages and automatically persists them to the graph
 * after a certain number of messages or on manual save.
 *
 * Author: Atlas (Infrastructure Engineer)
 * Created: 2025-10-26
 */

import { useCallback, useRef } from 'react';
import { ConversationService, type ConversationMessage } from '../services/conversationService';

interface UseConversationPersistenceOptions {
  citizenId: string;
  /**
   * Auto-save after this many new messages (default: 5)
   * Set to 0 to disable auto-save
   */
  autoSaveThreshold?: number;
}

export function useConversationPersistence({
  citizenId,
  autoSaveThreshold = 5,
}: UseConversationPersistenceOptions) {
  // Track messages for this conversation
  const messagesRef = useRef<ConversationMessage[]>([]);
  const messageCountRef = useRef(0);

  /**
   * Add a message to the conversation history
   */
  const addMessage = useCallback(
    (role: 'human' | 'assistant', content: string) => {
      messagesRef.current.push({ role, content });
      messageCountRef.current++;

      // Auto-save if threshold reached
      if (autoSaveThreshold > 0 && messageCountRef.current >= autoSaveThreshold) {
        saveConversation().catch(error => {
          console.error('Failed to auto-save conversation:', error);
        });
      }
    },
    [autoSaveThreshold]
  );

  /**
   * Manually save the conversation to the graph
   */
  const saveConversation = useCallback(async () => {
    if (messagesRef.current.length === 0) {
      console.log('No messages to save');
      return null;
    }

    try {
      const conversationId = await ConversationService.saveConversation(
        citizenId,
        messagesRef.current
      );

      console.log(`Conversation saved: ${conversationId}`);

      // Reset counter after save (but keep messages for potential future saves)
      messageCountRef.current = 0;

      return conversationId;
    } catch (error) {
      console.error('Failed to save conversation:', error);
      throw error;
    }
  }, [citizenId]);

  /**
   * Clear conversation history (e.g., when starting fresh conversation)
   */
  const clearConversation = useCallback(() => {
    messagesRef.current = [];
    messageCountRef.current = 0;
  }, []);

  return {
    addMessage,
    saveConversation,
    clearConversation,
    messageCount: messageCountRef.current,
  };
}
