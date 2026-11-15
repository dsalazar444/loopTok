import {
    Navigate,
    Route,
    Routes,
} from "react-router";
import { ProtectedRoute } from "../features/auth/components/ProtectedRoute";
import { RegisterForm } from "../features/auth/components/RegisterForm";
import { VideoFeed } from "../features/feed/components/VideoFeed";
import { MainLayout } from "./MainLayout";
import { LoginPlaceholder, ProfilePlaceholder } from "./placeholders";

export function AppRouter() {
    return (
        <Routes>
            <Route path="/register" element={<RegisterForm />} />
            <Route path="/login" element={<LoginPlaceholder />} />

            <Route element={<MainLayout />}>
                <Route path="/" element={<VideoFeed />} />

                <Route element={<ProtectedRoute />}>
                    <Route path="/profile" element={<ProfilePlaceholder />} />
                </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}
