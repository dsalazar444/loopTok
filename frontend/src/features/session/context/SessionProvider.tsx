import { useEffect, useMemo, useState, type ReactNode } from "react";

import { useAuth } from "../../auth/context/AuthContext";
import { ApiError } from "../../../shared/api/httpClient";
import { endSession, sendHeartbeat, startSession } from "../api/sessionApi";
import { newSessionId } from "../utils/newSessionId";
import { SessionContext } from "./SessionContext";

const HEARTBEAT_INTERVAL_MS = 60_000;

type Status = "idle" | "starting" | "ready";

// A session starts when the user logs in and ends on logout. Everything lives in memory,
// like the login itself: a reload starts a new session and the backend closes the old one
// after SESSION_INACTIVITY_MINUTES without heartbeats.
export function SessionProvider({ children }: { children: ReactNode }) {
    const { token, isAuthenticated } = useAuth();

    const [started, setStarted] = useState<{
        token: string;
        id: string;
    } | null>(null);

    useEffect(() => {
        if (!isAuthenticated || !token) return;

        let cancelled = false;
        let running = false;
        let status: Status = "idle";
        let activeId: string | null = null;
        let interval: number | undefined;

        const begin = () => {
            const id = newSessionId();

            activeId = id;
            status = "starting";

            startSession(id, token)
                .then(() => {
                    if (cancelled || activeId !== id) return;

                    status = "ready";
                    setStarted({ token, id });
                })
                .catch(() => {
                    // network or server error: the next heartbeat tick tries to start again
                    if (activeId === id) status = "idle";
                });
        };

        const beat = () => {
            if (status === "starting") return;

            if (status === "idle" || activeId === null) {
                begin();
                return;
            }

            sendHeartbeat(activeId, token).catch((error: unknown) => {
                // 409: ended or expired, 404: unknown. Either way the client needs a new session
                if (
                    error instanceof ApiError &&
                    (error.status === 404 || error.status === 409)
                ) {
                    begin();
                }
            });
        };

        const stopTimer = () => {
            window.clearInterval(interval);
            interval = undefined;
        };

        // the heartbeat only runs while the tab is visible, so a tab left in the
        // background counts as inactive
        const startTimer = () => {
            stopTimer();
            interval = window.setInterval(beat, HEARTBEAT_INTERVAL_MS);
        };

        const handleVisibility = () => {
            if (!running) return;

            if (document.visibilityState === "visible") {
                beat();
                startTimer();
            } else {
                stopTimer();
            }
        };

        // pagehide also fires on reload, so it only sends a last heartbeat, never "end":
        // the exact moment the user left is recorded without closing the session by mistake
        const handlePageHide = () => {
            if (status === "ready" && activeId !== null) {
                sendHeartbeat(activeId, token, true).catch(() => {});
            }
        };

        // React StrictMode runs effects twice in development. Delaying the start by one
        // tick lets the first run be cancelled before it sends anything.
        const startTimeout = window.setTimeout(() => {
            running = true;
            begin();

            if (document.visibilityState === "visible") {
                startTimer();
            }
        }, 0);

        document.addEventListener("visibilitychange", handleVisibility);
        window.addEventListener("pagehide", handlePageHide);

        // runs on logout, on a new login (token change) and on unmount, with the token
        // of this session, which is already cleared from the auth state on logout
        return () => {
            cancelled = true;
            window.clearTimeout(startTimeout);
            stopTimer();
            document.removeEventListener("visibilitychange", handleVisibility);
            window.removeEventListener("pagehide", handlePageHide);

            if (activeId !== null) {
                endSession(activeId, token, true).catch(() => {});
            }
        };
    }, [isAuthenticated, token]);

    // a confirmed session of an old login is never exposed
    const sessionId =
        started !== null && started.token === token ? started.id : null;

    const value = useMemo(() => ({ sessionId }), [sessionId]);

    return (
        <SessionContext.Provider value={value}>
            {children}
        </SessionContext.Provider>
    );
}
