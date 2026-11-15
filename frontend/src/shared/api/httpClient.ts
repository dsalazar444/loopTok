const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export class ApiError extends Error {
    readonly status: number;

    constructor(
        status: number,
        message: string,
    ) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

interface ApiRequestOptions extends RequestInit {
    token?: string;
}

function getErrorMessage(data: unknown): string {
    if (
        typeof data === "object" &&
        data !== null &&
        "detail" in data &&
        typeof data.detail === "string"
    ) {
        return data.detail;
    }

    return "An unexpected error occurred.";
}

export async function apiRequest<T>(
    endpoint: string,
    options: ApiRequestOptions = {},
): Promise<T> {
    const { token, headers, ...requestOptions } = options;

    const requestHeaders = new Headers(headers);

    if (requestOptions.body !== undefined) {
        requestHeaders.set("Content-Type", "application/json");
    }

    if (token) {
        requestHeaders.set("Authorization", `Bearer ${token}`);
    }

    let response: Response;

    try {
        response = await fetch(
            `${API_BASE_URL}${endpoint}`,
            {
                ...requestOptions,
                headers: requestHeaders,
            },
        );
    } catch {
        throw new ApiError(
            0,
            "Unable to connect to the server.",
        );
    }

    const data: unknown = await response.json().catch(
        () => null,
    );

    if (!response.ok) {
        throw new ApiError(
            response.status,
            getErrorMessage(data),
        );
    }

    return data as T;
}