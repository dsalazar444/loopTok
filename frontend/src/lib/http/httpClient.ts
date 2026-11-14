import { HTTP_ERROR_MESSAGES } from "../errors/httpErrors";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const ACCESS_TOKEN_KEY = "looptok.accessToken";

export class HttpError extends Error {
    readonly status: number;

    constructor(status: number, message: string) {
        super(message);
        this.status = status;
    }
}

// shared fetch wrapper: base URL, JSON body and bearer token in one place
export async function httpRequest<T>(
    path: string,
    options: RequestInit = {},
): Promise<T> {
    if (!API_BASE_URL) {
        throw new Error("La configuración de la API no está definida.");
    }

    const headers = new Headers(options.headers);
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);

    if (options.body) {
        headers.set("Content-Type", "application/json");
    }

    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    let response: Response;

    try {
        response = await fetch(`${API_BASE_URL}${path}`, {
            ...options,
            headers,
        });
    } catch {
        throw new Error(HTTP_ERROR_MESSAGES.NETWORK);
    }

    if (!response.ok) {
        throw new HttpError(response.status, HTTP_ERROR_MESSAGES.DEFAULT);
    }

    // 204 has no body to parse
    if (response.status === 204) {
        return undefined as T;
    }

    return (await response.json()) as T;
}
