import { createContext, useContext, useState, type ReactNode } from "react";
import type { User } from "./types";

// shortcut: sesión simulada en localStorage, reemplazar por token + GET /users/me cuando exista el login real
const STORAGE_KEY = "looptok.user";

interface AuthContextValue {
    user: User | null;
    login: (user: User) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function loadUser(): User | null {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? (JSON.parse(raw) as User) : null;
    } catch {
        return null;
    }
}

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(loadUser);

    const login = (next: User) => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        setUser(next);
    };

    const logout = () => {
        localStorage.removeItem(STORAGE_KEY);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
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
