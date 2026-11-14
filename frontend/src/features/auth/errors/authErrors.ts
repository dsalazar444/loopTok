import {
    HTTP_ERROR_MESSAGES,
    HTTP_STATUS,
} from "../../../lib/errors/httpErrors";

export const AUTH_ERROR_MESSAGES = {
    USERNAME_TAKEN: "Este nombre de usuario ya está en uso.",
    INVALID_REGISTRATION_DATA: "Los datos proporcionados no son válidos.",
    REGISTRATION_FAILED: "No fue posible crear la cuenta. Inténtalo nuevamente.",
} as const;

export function getRegistrationErrorMessage(
    status: number,
): string {
    switch (status) {
        case HTTP_STATUS.CONFLICT:
            return AUTH_ERROR_MESSAGES.USERNAME_TAKEN;

        case HTTP_STATUS.BAD_REQUEST:
        case HTTP_STATUS.UNPROCESSABLE_CONTENT:
            return AUTH_ERROR_MESSAGES.INVALID_REGISTRATION_DATA;

        case HTTP_STATUS.INTERNAL_SERVER_ERROR:
            return HTTP_ERROR_MESSAGES.SERVER;

        default:
            return AUTH_ERROR_MESSAGES.REGISTRATION_FAILED;
    }
}
