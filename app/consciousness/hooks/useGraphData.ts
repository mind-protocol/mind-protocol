export interface Node {
  id: string;
  node_id?: string;
  labels?: string[];
  node_type?: string;
  text?: string;
  energy?: number;
  energy_runtime?: number;
  theta?: number;
  confidence?: number;
  entity_activations?: Record<string, { energy: number; last_activated?: number }>;
  last_active?: number;
  last_traversal_time?: number;
  last_traversed_by?: string;
  traversal_count?: number;
  created_at?: number;
  last_modified?: number;
  base_weight?: number;
  reinforcement_weight?: number;
  weight?: number;
  log_weight?: number;
  scope?: string;
  properties?: Record<string, any>;
  delta_energy?: number;
  x?: number;
  y?: number;
  economyOverlay?: {
    balance?: number;
    spent60s?: number;
    budgetRemain?: number;
    softCap?: number;
    kEcon?: number;
    ubcNextEta?: string;
    lastSigAt?: number;
    lastUbcAt?: number;
  };
}

export interface Link {
  id: string;
  source: string | Node;
  target: string | Node;
  type: string;
  strength?: number;
  weight?: number;
  last_traversed?: number;
  created_at?: number;
  energy?: number;
  confidence?: number;
  scope?: string;
  properties?: Record<string, any>;
  sub_entity_valences?: Record<string, number>;
  sub_entity_emotion_vectors?: Record<string, Record<string, number>>;
  entity_activations?: Record<string, { energy: number }>;
  flow?: number;
}

export interface Subentity {
  subentity_id: string;
  name?: string;
  kind?: string;
  energy?: number;
  threshold?: number;
  activation_level?: string;
  member_count?: number;
  members?: string[]; // Array of node IDs that are MEMBER_OF this SubEntity
  quality?: number;
  stability?: string;
  properties?: Record<string, any>;
}

export interface Operation {
  type: string;
  node_id?: string;
  link_id?: string;
  subentity_id?: string;
  timestamp: number;
  data?: any;
}

export interface GraphOption {
  id: string;
  name: string;
  ecosystem: string;
  organization?: string;
  citizen?: string;
  slug?: string;
  legacyId?: string;
}

export interface AvailableGraphs {
  citizens: GraphOption[];
  organizations: GraphOption[];
  ecosystems: GraphOption[];
}

export type GraphType = 'ecosystem' | 'organization' | 'citizen';

const FALLBACK_ECOSYSTEM_SLUG = 'consciousness-infrastructure';
const FALLBACK_ORGANIZATION_SLUG = 'mind-protocol';

export const normalizeSlug = (value: string | undefined, fallback: string) => {
  if (!value) return fallback;
  return value
    .toLowerCase()
    .trim()
    .replace(/[\s_]+/g, '-');
};

export const DEFAULT_ECOSYSTEM_SLUG = normalizeSlug(
  process.env.NEXT_PUBLIC_PRIMARY_ECOSYSTEM,
  FALLBACK_ECOSYSTEM_SLUG
);

export const DEFAULT_ORGANIZATION_SLUG = normalizeSlug(
  process.env.NEXT_PUBLIC_PRIMARY_ORGANIZATION,
  FALLBACK_ORGANIZATION_SLUG
);
