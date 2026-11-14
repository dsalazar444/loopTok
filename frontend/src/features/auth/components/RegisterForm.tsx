import { useState, type SubmitEvent } from "react";
import { Link, useNavigate } from "react-router";
import {
    ArrowLeft,
    AtSign,
    Eye,
    EyeOff,
    LockKeyhole,
    Play,
    UserRound,
} from "lucide-react";

import { registerUser } from "../api/authApi";
import { validateRegistration } from "../validation/registerValidation";
import type {
    RegisterErrors,
    RegisterField,
    RegisterRequest,
} from "../types";

import styles from "./styles/RegisterForm.module.css";

const initialValues: RegisterRequest = {
    fullName: "",
    username: "",
    password: "",
};

export function RegisterForm() {
    const navigate = useNavigate();

    const [values, setValues] = useState<RegisterRequest>(
        initialValues,
    );
    const [errors, setErrors] = useState<RegisterErrors>({});
    const [serverError, setServerError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    function updateField(
        field: RegisterField,
        value: string,
    ) {
        setValues((previous) => ({
            ...previous,
            [field]: value,
        }));

        setErrors((previous) => ({
            ...previous,
            [field]: undefined,
        }));

        setServerError("");
    }

    async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
        event.preventDefault();

        if (isSubmitting) return;

        setServerError("");

        const normalizedValues: RegisterRequest = {
            fullName: values.fullName.trim().replace(/\s+/g, " "),
            username: values.username.trim().toLowerCase(),
            password: values.password,
        };

        const validationErrors = validateRegistration(normalizedValues);

        setErrors(validationErrors);

        if (Object.keys(validationErrors).length > 0) {
            return;
        }

        setIsSubmitting(true);

        try {
            await registerUser(normalizedValues);

            navigate("/login", {
                replace: true,
                state: {
                    registrationSuccess: true,
                },
            });
        } catch (error) {
            setServerError(
                error instanceof Error
                    ? error.message
                    : "Ocurrió un error inesperado.",
            );
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <main className={styles.page}>
            <div className={styles.container}>
                <Link
                    to="/"
                    className={styles.backLink}
                    aria-label="Volver al inicio"
                >
                    <ArrowLeft size={26} />
                </Link>

                <header className={styles.header}>
                    <Play
                        className={styles.logo}
                        size={54}
                        strokeWidth={4}
                        aria-hidden="true"
                    />

                    <h1>Registrarse</h1>
                    <p>
                        Crea tu cuenta para comenzar
                        <br />
                        a ver contenido
                    </p>
                </header>

                <form
                    className={styles.form}
                    onSubmit={handleSubmit}
                    noValidate
                >
                    <div className={styles.field}>
                        <div className={styles.inputWrapper}>
                            <UserRound size={23} aria-hidden="true" />

                            <input
                                id="fullName"
                                name="fullName"
                                type="text"
                                placeholder="Nombre completo"
                                aria-label="Nombre completo"
                                autoComplete="name"
                                maxLength={100}
                                required
                                aria-invalid={Boolean(errors.fullName)}
                                aria-describedby={
                                    errors.fullName ? "fullNameError" : undefined
                                }
                                value={values.fullName}
                                onChange={(event) =>
                                    updateField("fullName", event.target.value)
                                }
                            />
                        </div>

                        {errors.fullName && (
                            <p id="fullNameError" className={styles.fieldError}>
                                {errors.fullName}
                            </p>
                        )}
                    </div>

                    <div className={styles.field}>
                        <div className={styles.inputWrapper}>
                            <AtSign size={23} aria-hidden="true" />

                            <input
                                id="username"
                                name="username"
                                type="text"
                                placeholder="Usuario"
                                aria-label="Usuario"
                                autoComplete="username"
                                maxLength={30}
                                required
                                aria-invalid={Boolean(errors.username)}
                                aria-describedby={
                                    errors.username ? "usernameError" : undefined
                                }
                                value={values.username}
                                onChange={(event) =>
                                    updateField("username", event.target.value)
                                }
                            />
                        </div>

                        {errors.username && (
                            <p id="usernameError" className={styles.fieldError}>
                                {errors.username}
                            </p>
                        )}
                    </div>

                    <div className={styles.field}>
                        <div className={styles.inputWrapper}>
                            <LockKeyhole size={23} aria-hidden="true" />

                            <input
                                id="password"
                                name="password"
                                type={showPassword ? "text" : "password"}
                                placeholder="Contraseña"
                                aria-label="Contraseña"
                                autoComplete="new-password"
                                maxLength={128}
                                required
                                aria-invalid={Boolean(errors.password)}
                                aria-describedby={
                                    errors.password ? "passwordError" : undefined
                                }
                                value={values.password}
                                onChange={(event) =>
                                    updateField("password", event.target.value)
                                }
                            />

                            <button
                                type="button"
                                className={styles.visibilityButton}
                                onClick={() =>
                                    setShowPassword((previous) => !previous)
                                }
                                aria-label={
                                    showPassword
                                        ? "Ocultar contraseña"
                                        : "Mostrar contraseña"
                                }
                                aria-pressed={showPassword}
                            >
                                {showPassword ? (
                                    <EyeOff size={22} />
                                ) : (
                                    <Eye size={22} />
                                )}
                            </button>
                        </div>

                        {errors.password && (
                            <p id="passwordError" className={styles.fieldError}>
                                {errors.password}
                            </p>
                        )}
                    </div>

                    {serverError && (
                        <p className={styles.serverError} role="alert">
                            {serverError}
                        </p>
                    )}

                    <button
                        className={styles.submitButton}
                        type="submit"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? "Creando cuenta..." : "Crear cuenta"}
                    </button>
                </form>

                <div className={styles.loginPrompt}>
                    <p>¿Ya tienes una cuenta?</p>
                    <Link to="/login">Iniciar sesión</Link>
                </div>
            </div>
        </main>
    );
}
