import { Link } from "react-router";
import { useAuth } from "../features/auth/context/AuthContext";

export function HomePlaceholder() {
    return (
        <div style={{ padding: "32px", color: "white" }}>
            <h1>LoopTok</h1>
            <p>Home page is not implemented yet.</p>
            <Link to="/register" style={{ color: "#32c9f5" }}>
                Register
            </Link>
        </div>
    );
}

// export function LoginPlaceholder() {
//     const location = useLocation();
//     const navigate = useNavigate();
//     const { login } = useAuth();

//     const state = location.state as {
//         registrationSuccess?: boolean;
//         from?: string;
//     } | null;

//     // temporal: simula sesión hasta que exista POST /auth/login
//     const simulateLogin = () => {
//         login({
//             id: "dev",
//             fullName: "Usuario Demo",
//             username: "demo",
//             createdAt: new Date().toISOString(),
//         });
//         navigate(state?.from ?? "/", { replace: true });
//     };

//     return (
//         <main style={{ padding: "32px", color: "white" }}>
//             <h1>Login</h1>

//             {state?.registrationSuccess && (
//                 <p role="status">
//                     Cuenta creada correctamente. Ya puedes iniciar sesión.
//                 </p>
//             )}

//             <p>Login page is not implemented yet.</p>

//             <button type="button" onClick={simulateLogin}>
//                 Entrar (simulado)
//             </button>

//             <p>
//                 <Link to="/register" style={{ color: "#32c9f5" }}>
//                     Register
//                 </Link>
//             </p>
//         </main>
//     );
// }

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
