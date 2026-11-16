import { createContext } from "react";

export interface SessionContextValue {
    // null while logged out or until the backend has confirmed the session
    sessionId: string | null;
}

export const SessionContext = createContext<SessionContextValue>({
    sessionId: null,
});
