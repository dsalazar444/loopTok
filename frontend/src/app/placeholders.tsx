import { useAuth } from "../features/auth/context/AuthContext";

export function ProfilePlaceholder() {
    const { user, logout } = useAuth();

    return (
        <div style={{ padding: "32px", color: "white" }}>
            <h1>Perfil</h1>
            <p>@{user?.username}</p>
            <button type="button" onClick={logout}>
                Cerrar sesión
            </button>
        </div>
    );
}
