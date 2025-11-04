/**
 * Node Type Emoji Mappings
 *
 * Complete emoji reference for all 33 Mind Protocol node types
 * Based on: docs/NODE_TYPE_EMOJIS.md
 */

// All Mind Protocol node types
export const NODE_EMOJIS: Record<string, string> = {
  // U3_ Types (Universal L1-L3) - 6 types
  'U3_Community': '👥',
  'U3_Deal': '🤝',
  'U3_Pattern': '🔄',
  'U3_Practice': '📖',
  'U3_Relationship': '🔗',
  'U3_Risk': '⚠️',

  // U4_ Types (Universal L1-L4) - 16 types
  'U4_Agent': '🤖',
  'U4_Assessment': '📊',
  'U4_Attestation': '✅',
  'U4_Code_Artifact': '📄',
  'U4_Decision': '🎯',
  'U4_Doc_View': '📰',
  'U4_Event': '⚡',
  'U4_Goal': '🎯',
  'U4_Knowledge_Object': '💡',
  'U4_Measurement': '📈',
  'U4_Metric': '📏',
  'U4_Public_Presence': '🌐',
  'U4_Smart_Contract': '📜',
  'U4_Subentity': '🧩',
  'U4_Wallet_Address': '💰',
  'U4_Work_Item': '✏️',

  // L4_ Types (Protocol Law) - 11 types
  'L4_Autonomy_Tier': '🔰',
  'L4_Capability': '🔓',
  'L4_Conformance_Result': '✔️',
  'L4_Conformance_Suite': '🧪',
  'L4_Envelope_Schema': '✉️',
  'L4_Event_Schema': '📋',
  'L4_Governance_Policy': '⚖️',
  'L4_Schema_Bundle': '📦',
  'L4_Signature_Suite': '🔐',
  'L4_Topic_Namespace': '🏷️',
  'L4_Type_Index': '📚',
};

// Agent type specializations (U4_Agent subtypes)
export const AGENT_TYPE_EMOJIS: Record<string, string> = {
  'human': '👤',
  'citizen': '🧠',
  'org': '🏛️',
  'dao': '🏦',
  'external_system': '🔌',
};

// Citizen role emojis (specialized U4_Agent citizens)
export const CITIZEN_ROLE_EMOJIS: Record<string, string> = {
  'scout': '🔍',      // Emma - finding opportunities
  'harbor': '⚓',     // Rafael - managing relationships
  'architect': '🏗️',  // Aïcha - designing systems
  'forge': '🔨',      // Daniel - building features
  'gauge': '📏',      // Sofia - quality control
  'facet': '💎',      // Maya - frontend polish
  'pulse': '💗',      // Priya - operations heartbeat
};

// Assessment domain emojis (U4_Assessment subtypes)
export const ASSESSMENT_DOMAIN_EMOJIS: Record<string, string> = {
  'reputation': '⭐',
  'psychology': '🧠',
  'performance': '📊',
  'security': '🔒',
  'compliance': '✅',
};

// Event kind emojis (U4_Event subtypes)
export const EVENT_KIND_EMOJIS: Record<string, string> = {
  'percept': '👁️',
  'mission': '🎯',
  'market': '💹',
  'incident': '🚨',
  'publish': '📢',
  'trade': '💱',
  'governance': '🏛️',
  'healthcheck': '💚',
  'decision_record': '📝',
};

// Work type emojis (U4_Work_Item subtypes)
export const WORK_TYPE_EMOJIS: Record<string, string> = {
  'task': '✏️',
  'milestone': '🏁',
  'bug': '🐛',
  'ticket': '🎫',
  'mission': '🚀',
};

// Pattern valence emojis (U3_Pattern subtypes)
export const PATTERN_VALENCE_EMOJIS: Record<string, string> = {
  'positive': '✨',
  'negative': '⚠️',
  'neutral': '⚪',
};

// Deal state emojis (U3_Deal subtypes)
export const DEAL_STATE_EMOJIS: Record<string, string> = {
  'Proposed': '💭',
  'Confirmed': '✅',
  'Settled': '💰',
  'Rejected': '❌',
};

// Universal status emojis
export const STATUS_EMOJIS: Record<string, string> = {
  'active': '🟢',
  'suspended': '🟡',
  'archived': '⚫',
  'deprecated': '🔴',
  'draft': '📝',
};

// Level fallbacks (when type unknown) - Mind Protocol spec
export const LEVEL_EMOJIS: Record<string, string> = {
  'L1': '👤', // Personal/Citizen
  'L2': '🏛️', // Organizational
  'L3': '🌍', // Ecosystem
  'L4': '⚖️', // Protocol
};

/**
 * Get emoji for a node (hierarchical fallback)
 *
 * Priority:
 * 1. Citizen role (if labels include 'citizen' + role field exists)
 * 2. Agent type (if type_name is U4_Agent + agent_type field exists)
 * 3. Assessment domain (if type_name is U4_Assessment + domain field exists)
 * 4. Event kind (if type_name is U4_Event + event_kind field exists)
 * 5. Work type (if type_name is U4_Work_Item + work_type field exists)
 * 6. Node type_name
 * 7. Layer fallback
 * 8. Default circle
 */
export function getNodeEmoji(node: {
  type_name?: string;
  labels?: string[];
  role?: string;
  agent_type?: string;
  domain?: string;
  event_kind?: string;
  work_type?: string;
  level?: string;
}): string {
  // 1. Check for citizen role (highest priority for our use case)
  if (node.labels?.includes('citizen') && node.role) {
    return CITIZEN_ROLE_EMOJIS[node.role] || '🤖';
  }

  // 2. Check for agent type
  if (node.type_name === 'U4_Agent' && node.agent_type) {
    return AGENT_TYPE_EMOJIS[node.agent_type] || '🤖';
  }

  // 3. Check for assessment domain
  if (node.type_name === 'U4_Assessment' && node.domain) {
    return ASSESSMENT_DOMAIN_EMOJIS[node.domain] || '📊';
  }

  // 4. Check for event kind
  if (node.type_name === 'U4_Event' && node.event_kind) {
    return EVENT_KIND_EMOJIS[node.event_kind] || '⚡';
  }

  // 5. Check for work type
  if (node.type_name === 'U4_Work_Item' && node.work_type) {
    return WORK_TYPE_EMOJIS[node.work_type] || '✏️';
  }

  // 6. Check for general node type
  if (node.type_name && NODE_EMOJIS[node.type_name]) {
    return NODE_EMOJIS[node.type_name];
  }

  // 7. Level fallback
  if (node.level !== undefined && LEVEL_EMOJIS[node.level]) {
    return LEVEL_EMOJIS[node.level];
  }

  // 8. Default
  return '◯';
}

/**
 * Get human-readable type name
 */
export function getNodeTypeName(node: {
  type_name?: string;
  labels?: string[];
  agent_type?: string;
}): string {
  // Check for citizen
  if (node.labels?.includes('citizen')) {
    return 'U4_Agent (Citizen)';
  }

  // Check for organization
  if (node.labels?.includes('organization')) {
    return 'U4_Agent (Organization)';
  }

  // Check for specific agent type
  if (node.type_name === 'U4_Agent' && node.agent_type) {
    return `U4_Agent (${node.agent_type})`;
  }

  // Check for protocol/schema labels
  if (node.labels?.includes('protocol')) {
    return 'L4_Governance_Policy';
  }
  if (node.labels?.includes('schema')) {
    return 'L4_Event_Schema';
  }
  if (node.labels?.includes('knowledge')) {
    return 'U4_Knowledge_Object';
  }

  // Return type_name or unknown
  return node.type_name || 'Unknown';
}
