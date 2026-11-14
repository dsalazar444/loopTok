import {
    Navigate,
    Route,
    Routes,
} from "react-router";
import { ProtectedRoute } from "../features/auth/components/ProtectedRoute";
import { RegisterForm } from "../features/auth/components/RegisterForm";
import { MainLayout } from "./MainLayout";
import { HomePlaceholder, LoginPlaceholder, ProfilePlaceholder } from "./placeholders";

export function AppRouter() {
    return (
        <Routes>
            <Route path="/register" element={<RegisterForm />} />
            <Route path="/login" element={<LoginPlaceholder />} />

            <Route element={<MainLayout />}>
                <Route path="/" element={<HomePlaceholder />} />

                <Route element={<ProtectedRoute />}>
                    <Route path="/profile" element={<ProfilePlaceholder />} />
                </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}
