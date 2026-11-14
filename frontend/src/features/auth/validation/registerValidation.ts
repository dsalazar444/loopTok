import type {
    RegisterErrors,
    RegisterRequest,
} from "../types";

const USERNAME_PATTERN = /^[a-zA-Z0-9._]+$/;
const FULL_NAME_PATTERN = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/;

export function validateRegistration(
    values: RegisterRequest,
): RegisterErrors {
    const errors: RegisterErrors = {};

    const fullName = values.fullName.trim();
    const username = values.username.trim();

    if (fullName.length < 2 || fullName.length > 100) {
        errors.fullName =
            "El nombre debe tener entre 2 y 100 caracteres";
    } else if (!FULL_NAME_PATTERN.test(fullName)) {
        errors.fullName =
            "El nombre solo puede contener letras y espacios.";
    }

    if (username.length < 3 || username.length > 30) {
        errors.username =
            "El usuario debe tener entre 3 y 30 caracteres.";
    } else if (!USERNAME_PATTERN.test(username)) {
        errors.username =
            "Solo puedes usar letras, números, puntos o guiones bajos.";
    }

    if (values.password.length < 8 || values.password.length > 128) {
        errors.password =
            "La contraseña debe tener entre 8 y 128 caracteres";
    }

    return errors;
}
