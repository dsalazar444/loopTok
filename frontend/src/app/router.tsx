import {
    Navigate,
    Route,
    Routes,
} from "react-router";
import { RegisterForm } from "../features/auth/components/RegisterForm";
import { HomePlaceholder, LoginPlaceholder } from "./placeholders";

export function AppRouter() {
    return (
        <Routes>
            <Route path="/" element={<HomePlaceholder />} />
            <Route path="/register" element={<RegisterForm />} />
            <Route path="/login" element={<LoginPlaceholder />} />
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}
