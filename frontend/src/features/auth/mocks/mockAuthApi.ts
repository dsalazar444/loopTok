import type { RegisterRequest, User } from "../types";
import { AUTH_ERROR_MESSAGES } from "../errors/authErrors";


const registeredUsernames = new Set<string>();

export async function mockRegister(
    request: RegisterRequest,
): Promise<User> {
    await new Promise<void>((resolve) => {
        setTimeout(resolve, 400);
    });

    const username = request.username.toLowerCase();

    if (registeredUsernames.has(username)) {
        throw new Error(AUTH_ERROR_MESSAGES.USERNAME_TAKEN);
    }

    registeredUsernames.add(username);

    return {
        id: crypto.randomUUID(),
        fullName: request.fullName,
        username,
        createdAt: new Date().toISOString(),
    };
}
