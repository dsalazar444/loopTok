import { Link, useLocation } from "react-router";

export function HomePlaceholder() {
    return (
        <main style={{ padding: "32px", color: "white" }}>
            <h1>LoopTok</h1>
            <p>Home page is not implemented yet.</p>
            <Link to="/register" style={{ color: "#32c9f5" }}>
                Register
            </Link>
        </main>
    );
}

export function LoginPlaceholder() {
    const location = useLocation();

    const registrationSuccess = (
        location.state as {
            registrationSuccess?: boolean;
        } | null
    )?.registrationSuccess;

    return (
        <main style={{ padding: "32px", color: "white" }}>
            <h1>Login</h1>

            {registrationSuccess && (
                <p role="status">
                    Cuenta creada correctamente. Ya puedes iniciar sesión.
                </p>
            )}

            <p>Login page is not implemented yet.</p>

            <Link to="/register" style={{ color: "#32c9f5" }}>
                Register
            </Link>
        </main>
    );
}
