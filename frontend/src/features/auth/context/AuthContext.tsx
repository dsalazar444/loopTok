import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useState,
    type ReactNode,
} from "react";

import type { AuthUser, LoginRequest } from "../types";
import { loginUser, getCurrentUser } from "../api/loginApi";
import { apiRequest, ApiError } from "../../../shared/api/httpClient";

interface AuthContextValue {
    user: AuthUser | null;
    token: string | null;
    isAuthenticated: boolean;
    login: (credentials: LoginRequest) => Promise<void>;
    logout: () => void;
    authenticatedRequest: <T>(
        endpoint: string,
        options?: RequestInit,
    ) => Promise<T>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [expiresAt, setExpiresAt] = useState<number | null>(null);

    const logout = useCallback(() => {
        setUser(null);
        setToken(null);
        setExpiresAt(null);
    }, []);

    const login = useCallback(async (credentials: LoginRequest) => {
        const response = await loginUser(credentials);

        const currentUser = await getCurrentUser(
            response.access_token,
        );

        setToken(response.access_token);
        setUser(currentUser);
        setExpiresAt(
            Date.now() + response.expires_in * 1000,
        );
    }, []);

    useEffect(() => {
        if (expiresAt === null) return;

        const remainingTime = expiresAt - Date.now();

        if (remainingTime <= 0) {
            logout();
            return;
        }

        const timeout = window.setTimeout(logout, remainingTime);

        return () => window.clearTimeout(timeout);
    }, [expiresAt, logout]);

    const authenticatedRequest = useCallback(
        async <T,>(
            endpoint: string,
            options: RequestInit = {},
        ): Promise<T> => {
            if (
                !token ||
                expiresAt === null ||
                Date.now() >= expiresAt
            ) {
                logout();
                throw new ApiError(401, "Session expired.");
            }

            try {
                return await apiRequest<T>(endpoint, {
                    ...options,
                    token,
                });
            } catch (error) {
                if (
                    error instanceof ApiError &&
                    error.status === 401
                ) {
                    logout();
                }

                throw error;
            }
        },
        [token, expiresAt, logout],
    );

    const isAuthenticated =
        user !== null &&
        token !== null &&
        expiresAt !== null &&
        Date.now() < expiresAt;

    const value = useMemo<AuthContextValue>(
        () => ({
            user,
            token,
            isAuthenticated,
            login,
            logout,
            authenticatedRequest,
        }),
        [
            user,
            token,
            isAuthenticated,
            login,
            logout,
            authenticatedRequest,
        ],
    );

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth(): AuthContextValue {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error("useAuth must be used inside AuthProvider.");
    }

    return context;
}
