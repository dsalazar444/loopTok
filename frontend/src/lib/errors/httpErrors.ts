export const HTTP_STATUS = {
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    CONFLICT: 409,
    UNPROCESSABLE_CONTENT: 422,
    INTERNAL_SERVER_ERROR: 500,
} as const;

export const HTTP_ERROR_MESSAGES = {
    DEFAULT: "Ocurrió un error inesperado.",
    NETWORK: "No se pudo conectar con el servidor.",
    SERVER: "El servidor no está disponible. Inténtalo más tarde.",
} as const;
