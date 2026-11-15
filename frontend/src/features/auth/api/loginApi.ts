import { apiRequest } from "../../../shared/api/httpClient";

import type {
    AuthUser,
    LoginRequest,
    TokenResponse,
} from "../types";

export function loginUser(
    credentials: LoginRequest,
): Promise<TokenResponse> {
    return apiRequest<TokenResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify(credentials),
    });
}

export function getCurrentUser(
    token: string,
): Promise<AuthUser> {
    return apiRequest<AuthUser>("/users/me", {
        method: "GET",
        token,
    });
}
