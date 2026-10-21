const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Character = {
  id: number;
  name: string;
  level: number;
  race_id: number;
  class_id: number;
  background_id: number;
  race: { id: number; name: string };
  character_class: { id: number; name: string };
  background: { id: number; name: string };
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
};

export type AuthToken = {
  access_token: string;
  token_type: string;
  expires_in: number;
};

export type User = {
  id: number;
  email: string;
  nickname: string;
  role: string;
  created_at: string;
};

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, options);

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message =
      body?.detail ?? `Помилка запиту: ${response.status}`;

    throw new Error(
      typeof message === "string" ? message : JSON.stringify(message),
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function login(
  email: string,
  password: string,
): Promise<AuthToken> {
  const body = new URLSearchParams({ username: email, password });

  return request<AuthToken>("/users/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });
}

export function getMe(token: string) {
  return request<User>("/users/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function register(
  email: string,
  nickname: string,
  password: string,
) {
  return request("/users/registration", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, nickname, password }),
  });
}

export function getCharacters(token: string) {
  return request<Character[]>("/characters", {
    headers: { Authorization: `Bearer ${token}` },
  });
}


export type Race = {
  id: number;
  name: string;
  description?: string | null;
  speed?: number | null;
};

export type CharacterClassEntry = {
  id: number;
  name: string;
  description?: string | null;
  primary_ability?: string | null;
  hit_die?: string | null;
};

export type Background = {
  id: number;
  name: string;
  description?: string | null;
  skill_proficiencies?: string[] | null;
};

export function getRaces() {
  return request<Race[]>("/races");
}

export function getClasses() {
  return request<CharacterClassEntry[]>("/classes");
}

export function getBackgrounds() {
  return request<Background[]>("/backgrounds");
}


export type CharacterCreate = {
  name: string
  race_id: number
  class_id: number
  background_id: number
  level: number
  strength: number
  dexterity: number
  constitution: number
  intelligence: number
  wisdom: number
  charisma: number
}

export function createCharacter(token: string, data: CharacterCreate) {
  return request<Character>('/characters', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  })
}

export type CharacterUpdate = Partial<CharacterCreate>

export function updateCharacter(
  token: string,
  characterId: number,
  data: CharacterUpdate,
) {
  return request<Character>(`/characters/${characterId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  })
}

export function deleteCharacter(
  token: string,
  characterId: number,
) {
  return request<void>(`/characters/${characterId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}


export type CharacterExportStatus = {
  task_id: string
  character_id: number
  status: 'PENDING' | 'STARTED' | 'RETRY' | 'SUCCESS' | 'FAILURE'
  created_at: string
  updated_at: string
  error: string | null
}

type CharacterExportRequest = {
  task_id: string
  status: string
}

export async function requestCharacterExport(
  token: string,
  characterId: number,
): Promise<CharacterExportRequest> {
  return request<CharacterExportRequest>(
    `/characters/${characterId}/export`,
    {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    },
  )
}

export async function getCharacterExportStatus(
  token: string,
  taskId: string,
): Promise<CharacterExportStatus> {
  return request<CharacterExportStatus>(
    `/characters/exports/${encodeURIComponent(taskId)}`,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  )
}

export async function downloadCharacterExport(
  token: string,
  taskId: string,
): Promise<Blob> {
  const response = await fetch(
    `${API_URL}/characters/exports/${encodeURIComponent(taskId)}/download`,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  )

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const message = body?.detail ?? `Не вдалося завантажити PDF (${response.status})`
    throw new Error(
      typeof message === 'string' ? message : JSON.stringify(message),
    )
  }

  return response.blob()
}


export type Spell = {
  id: number
  name: string
  level: number
  school: string
  casting_time: string
  spell_range: string
  duration: string
  description: string
}

export type SpellListResponse = {
  items: Spell[]
  total: number
  limit: number
  offset: number
}

export type SpellFilters = {
  search?: string
  level?: number
  school?: string
  limit?: number
  offset?: number
}

export function getSpells(filters: SpellFilters = {}) {
  const params = new URLSearchParams()

  if (filters.search?.trim()) {
    params.set('search', filters.search.trim())
  }

  if (filters.level !== undefined) {
    params.set('level', String(filters.level))
  }

  if (filters.school) {
    params.set('school', filters.school)
  }

  params.set('limit', String(filters.limit ?? 50))
  params.set('offset', String(filters.offset ?? 0))

  return request<SpellListResponse>(`/spells?${params.toString()}`)
}

export function getSpellSchools() {
  return request<string[]>('/spells/schools')
}
  