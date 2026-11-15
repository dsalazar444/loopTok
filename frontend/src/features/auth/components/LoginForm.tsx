
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { ApiError } from "../../../shared/api/httpClient";

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
        <section className={styles.container}>
            <div className={styles.header}>
                <div className={styles.logo}>▶</div>

                <h1>Bienvenido a LoopTok</h1>
                <p>Inicia sesión para continuar explorando.</p>
            </div>

            <form
                className={styles.form}
                onSubmit={handleSubmit}
                noValidate
            >
                <div className={styles.field}>
                    <label htmlFor="login-username">
                        Nombre de usuario
                    </label>

                    <input
                        id="login-username"
                        name="username"
                        type="text"
                        autoComplete="username"
                        value={username}
                        onChange={(event) =>
                            setUsername(event.target.value)
                        }
                        placeholder="Tu nombre de usuario"
                        disabled={isLoading}
                        required
                    />
                </div>

                <div className={styles.field}>
                    <label htmlFor="login-password">
                        Contraseña
                    </label>

                    <div className={styles.passwordWrapper}>
                        <input
                            id="login-password"
                            name="password"
                            type={showPassword ? "text" : "password"}
                            autoComplete="current-password"
                            value={password}
                            onChange={(event) =>
                                setPassword(event.target.value)
                            }
                            placeholder="Tu contraseña"
                            disabled={isLoading}
                            required
                        />

                        <button
                            type="button"
                            className={styles.visibilityButton}
                            onClick={() =>
                                setShowPassword((current) => !current)
                            }
                            aria-label={
                                showPassword
                                    ? "Ocultar contraseña"
                                    : "Mostrar contraseña"
                            }
                            aria-pressed={showPassword}
                        >
                            {showPassword ? "Ocultar" : "Mostrar"}
                        </button>
                    </div>
                </div>

                {error && (
                    <p className={styles.error} role="alert">
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

            <p className={styles.footer}>
                ¿No tienes cuenta?{" "}
                <Link
                    to="/register"
                    className={styles.registerButton}
                >
                    Regístrate
                </Link>
            </p>
        </section>
    );
}
