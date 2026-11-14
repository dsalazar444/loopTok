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
