import { HTTP_ERROR_MESSAGES } from "../errors/httpErrors";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export class ApiError extends Error {
    readonly status: number;

    constructor(status: number, message: string) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

interface ApiRequestOptions extends RequestInit {
    token?: string;
}

function getErrorMessage(data: unknown): string {
    if (typeof data === "object" && data !== null) {
        if ("message" in data && typeof data.message === "string") {
            return data.message;
        }

        if ("detail" in data && typeof data.detail === "string") {
            return data.detail;
        }
    }

    return HTTP_ERROR_MESSAGES.DEFAULT;
}

export async function apiRequest<T>(
    endpoint: string,
    options: ApiRequestOptions = {},
): Promise<T> {
    if (!API_BASE_URL) {
        throw new Error("La configuración de la API no está definida.");
    }

    const { token, headers, ...requestOptions } = options;

    const requestHeaders = new Headers(headers);

    if (requestOptions.body !== undefined && !requestHeaders.has("Content-Type")) {
        requestHeaders.set("Content-Type", "application/json");
    }

    if (token) {
        requestHeaders.set("Authorization", `Bearer ${token}`);
    }

    let response: Response;

    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...requestOptions,
            headers: requestHeaders,
        });
    } catch {
        throw new ApiError(0, HTTP_ERROR_MESSAGES.NETWORK);
    }

    if (response.status === 204) {
        return undefined as T;
    }

    const data: unknown = await response.json().catch(() => null);

    if (!response.ok) {
        throw new ApiError(
            response.status,
            getErrorMessage(data),
        );
    }

    return data as T;
}
