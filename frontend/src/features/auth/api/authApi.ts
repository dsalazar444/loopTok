import { mockRegister } from "../mocks/mockAuthApi";
import { getRegistrationErrorMessage } from "../errors/authErrors";
import { HTTP_ERROR_MESSAGES } from "../../../shared/errors/httpErrors";
import type { RegisterRequest, User } from "../types";

const useMockData = import.meta.env.VITE_USE_MOCK_DATA === "true";
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

export async function registerUser(request: RegisterRequest): Promise<User> {
    if (useMockData) {
        return mockRegister(request);
    }

    if (!apiBaseUrl) {
        throw new Error("La configuración de la API no está definida.");
    }

    let response: Response;

    try {
        response = await fetch(`${apiBaseUrl}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(request),
        });
    } catch {
        throw new Error(HTTP_ERROR_MESSAGES.NETWORK);
    }

    if (!response.ok) {
        throw new Error(
            getRegistrationErrorMessage(response.status),
        );
    }

    return (await response.json()) as User;
}
