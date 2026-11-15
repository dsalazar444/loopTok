import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { ApiError } from "../../../shared/api/httpClient";
import { Play } from "lucide-react";

import styles from "./styles/LoginForm.module.css";

export function LoginForm() {
    const navigate = useNavigate();
    const { login } = useAuth();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function handleSubmit(
        event: FormEvent<HTMLFormElement>,
    ) {
        event.preventDefault();

        if (isLoading) return;

        setError(null);

        const normalizedUsername = username.trim();

        if (!normalizedUsername || !password) {
            setError("Completa todos los campos.");
            return;
        }

        setIsLoading(true);

        try {
            await login({
                username: normalizedUsername,
                password,
            });

            navigate("/", { replace: true });
        } catch (error: unknown) {
            if (error instanceof ApiError) {
                switch (error.status) {
                    case 401:
                        setError("Usuario o contraseña incorrectos.");
                        break;
                    case 0:
                        setError("No se pudo conectar con el servidor.");
                        break;
                    case 422:
                        setError("Revisa los datos ingresados.");
                        break;
                    default:
                        setError(
                            "No se pudo iniciar sesión. Inténtalo de nuevo.",
                        );
                }
            } else {
                setError("Ocurrió un error inesperado.");
            }
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <main className={styles.page}>
            <section className={styles.container}>
                <Link
                    to="/"
                    className={styles.backButton}
                    aria-label="Volver al inicio"
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        aria-hidden="true"
                    >
                        <path d="M19 12H5" />
                        <path d="m12 19-7-7 7-7" />
                    </svg>
                </Link>

                <div className={styles.header}>
                    <Play
                        className={styles.logo}
                        size={54}
                        strokeWidth={4}
                        aria-hidden="true"
                    />

                    <h1>Iniciar sesión</h1>
                    <p>
                        Ingresa a tu cuenta para seguir
                        <br />
                        explorando
                    </p>
                </div>

                <form
                    className={styles.form}
                    onSubmit={handleSubmit}
                    noValidate
                >
                    <div className={styles.field}>
                        <label
                            className={styles.srOnly}
                            htmlFor="login-username"
                        >
                            Usuario
                        </label>

                        <div className={styles.inputWrapper}>
                            <svg
                                className={styles.inputIcon}
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.7"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                aria-hidden="true"
                            >
                                <circle cx="12" cy="7" r="4" />
                                <path d="M4.5 21v-2a7.5 7.5 0 0 1 15 0v2" />
                            </svg>

                            <input
                                id="login-username"
                                name="username"
                                type="text"
                                autoComplete="username"
                                value={username}
                                onChange={(event) =>
                                    setUsername(event.target.value)
                                }
                                placeholder="Usuario"
                                disabled={isLoading}
                                required
                            />
                        </div>
                    </div>

                    <div className={styles.field}>
                        <label
                            className={styles.srOnly}
                            htmlFor="login-password"
                        >
                            Contraseña
                        </label>

                        <div className={styles.inputWrapper}>
                            <svg
                                className={styles.inputIcon}
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.7"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                aria-hidden="true"
                            >
                                <rect
                                    x="4"
                                    y="10"
                                    width="16"
                                    height="11"
                                    rx="2"
                                />
                                <path d="M8 10V7a4 4 0 0 1 8 0v3" />
                                <path d="M12 14.5v2" />
                            </svg>

                            <input
                                id="login-password"
                                name="password"
                                type={
                                    showPassword
                                        ? "text"
                                        : "password"
                                }
                                autoComplete="current-password"
                                value={password}
                                onChange={(event) =>
                                    setPassword(event.target.value)
                                }
                                placeholder="Contraseña"
                                disabled={isLoading}
                                required
                            />

                            <button
                                type="button"
                                className={styles.visibilityButton}
                                onClick={() =>
                                    setShowPassword(
                                        (current) => !current,
                                    )
                                }
                                aria-label={
                                    showPassword
                                        ? "Ocultar contraseña"
                                        : "Mostrar contraseña"
                                }
                                aria-pressed={showPassword}
                            >
                                {showPassword ? (
                                    <svg
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="1.7"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        aria-hidden="true"
                                    >
                                        <path d="M3 3l18 18" />
                                        <path d="M10.6 5.1A10.7 10.7 0 0 1 12 5c5.5 0 9.5 7 9.5 7a16 16 0 0 1-3.2 3.8" />
                                        <path d="M6.2 6.2C3.7 8.1 2.5 12 2.5 12s4 7 9.5 7a9.4 9.4 0 0 0 4.2-1" />
                                        <path d="M10 10a2.8 2.8 0 0 0 4 4" />
                                    </svg>
                                ) : (
                                    <svg
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="1.7"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        aria-hidden="true"
                                    >
                                        <path d="M2.5 12s4-7 9.5-7 9.5 7 9.5 7-4 7-9.5 7S2.5 12 2.5 12Z" />
                                        <circle cx="12" cy="12" r="3" />
                                    </svg>
                                )}
                            </button>
                        </div>
                    </div>

                    {error && (
                        <p
                            className={styles.error}
                            role="alert"
                        >
                            {error}
                        </p>
                    )}

                    <button
                        className={styles.submitButton}
                        type="submit"
                        disabled={isLoading}
                    >
                        {isLoading
                            ? "Iniciando sesión..."
                            : "Iniciar sesión"}
                    </button>
                </form>

                <div className={styles.footer}>
                    <p>¿No tienes una cuenta?</p>

                    <Link
                        to="/register"
                        className={styles.registerButton}
                    >
                        Registrarte
                    </Link>
                </div>
            </section>
        </main>
    );
}
