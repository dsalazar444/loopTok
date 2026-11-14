import { Navigate, Outlet, useLocation } from "react-router";
import { useAuth } from "../AuthContext";

export function ProtectedRoute() {
    const { user } = useAuth();
    const location = useLocation();

    if (!user) {
        // "from" permite volver a la página pedida después de iniciar sesión
        return <Navigate to="/login" replace state={{ from: location.pathname }} />;
    }

    return <Outlet />;
}
