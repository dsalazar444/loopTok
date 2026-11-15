export interface RegisterRequest {
  fullName: string;
  username: string;
  password: string;
}

// representa la entidad del usuario como vive en el front, y como 
// lo devolverá el backend. Por eso no hay contraseña 
export interface User {
  id: string; // id en bd
  fullName: string;
  username: string;
  createdAt: string;
}

export type RegisterField = keyof RegisterRequest;

export type RegisterErrors = Partial<
  Record<RegisterField, string>
>;

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
}

export interface AuthUser {
  id: string;
  fullName: string;
  username: string;
  createdAt: string;
}

export interface AuthState {
  token: string | null;
  user: AuthUser | null;
  expiresAt: number | null;
}
