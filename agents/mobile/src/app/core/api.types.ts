// Mirrors frontend/web/src/app/core/api.types.ts.
// In a future iteration this becomes a shared library under
// `libs/api-types/` consumed by both web and mobile.

export interface UserPublic {
  id: string;
  email: string;
  display_name: string;
  role: 'owner' | 'admin' | 'member' | 'guest';
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: 'Bearer';
  expires_in: number;
  user: UserPublic;
}

export interface MfaChallenge {
  mfa_required: true;
  challenge_token: string;
  allowed_methods: string[];
  expires_in: number;
}

export type LoginResponse = TokenPair | MfaChallenge;

export interface MemoryItemPublic {
  id: string;
  user_id: string;
  kind: string;
  content: string;
  summary: string | null;
  source: string | null;
  metadata: Record<string, string | number | boolean> | null;
  created_at: string;
  updated_at: string;
}

export interface BackendInfo { name: string; model: string; is_local: boolean; }
export interface BackendsResponse { backends: BackendInfo[]; default: string; }

export interface OllamaModel {
  name: string;
  size: number;
  parameter_size: string | null;
  family: string | null;
  quantization_level: string | null;
  modified_at: string | null;
}
export interface OllamaModelsResponse {
  base_url: string;
  reachable: boolean;
  models: OllamaModel[];
  error: string | null;
}

export type StreamEventType = 'start' | 'chunk' | 'sources' | 'tool_call' | 'error' | 'end';
export interface StreamEvent {
  type: StreamEventType;
  turn_id: string;
  sequence: number;
  content?: string | null;
  metadata?: Record<string, string | number | boolean>;
}
