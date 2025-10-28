/**
 * Conversation Service - API client for persisting conversations to graph
 *
 * Handles conversation persistence by calling the backend API to create
 * Conversation nodes linked to Human participant.
 *
 * Author: Atlas (Infrastructure Engineer)
 * Created: 2025-10-26
 */

export interface ConversationMessage {
  role: 'human' | 'assistant';
  content: string;
}

export interface CreateConversationRequest {
  citizen_id: string;
  messages: ConversationMessage[];
  session_id?: string;
}

export interface CreateConversationResponse {
  conversation_id: string;
  status: string;
  timestamp: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ConversationService {
  /**
   * Create a conversation node in the graph
   *
   * @param request - Conversation data with citizen_id and messages
   * @returns Promise resolving to conversation_id and status
   */
  static async createConversation(
    request: CreateConversationRequest
  ): Promise<CreateConversationResponse> {
    const response = await fetch(`${API_BASE_URL}/api/conversation/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(
        `Failed to create conversation: ${error.detail || response.statusText}`
      );
    }

    return response.json();
  }

  /**
   * Save a conversation from chat messages
   *
   * Convenience method that formats messages and calls createConversation.
   *
   * @param citizenId - Which citizen participated (e.g., "atlas", "felix")
   * @param messages - Array of {role, content} messages
   * @param sessionId - Optional session identifier
   * @returns Promise resolving to conversation_id
   */
  static async saveConversation(
    citizenId: string,
    messages: ConversationMessage[],
    sessionId?: string
  ): Promise<string> {
    const response = await this.createConversation({
      citizen_id: citizenId,
      messages,
      session_id: sessionId,
    });

    return response.conversation_id;
  }
}
