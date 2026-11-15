import { NavLink, Outlet } from "react-router";
import { useAuth } from "../features/auth/context/AuthContext";
import styles from "./MainLayout.module.css";

const iconProps = {
    width: 24,
    height: 24,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 2,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": true,
} as const;

function HomeIcon() {
    return (
        <svg {...iconProps}>
            <path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z" />
        </svg>
    );
}

function LoginIcon() {
    return (
        <svg {...iconProps}>
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3" />
        </svg>
    );
}

function ProfileIcon() {
    return (
        <svg {...iconProps}>
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21a8 8 0 0 1 16 0" />
        </svg>
    );
}

export function MainLayout() {
    const { user } = useAuth();

    const linkClass = ({ isActive }: { isActive: boolean }) =>
        isActive ? `${styles.navLink} ${styles.active}` : styles.navLink;

    return (
        <div className={styles.shell}>
            <main className={styles.content}>
                <Outlet />
            </main>

            <nav className={styles.nav} aria-label="Principal">
                <NavLink to="/" end className={linkClass}>
                    <HomeIcon />
                    <span>Home</span>
                </NavLink>

                {user ? (
                    <NavLink to="/profile" className={linkClass}>
                        <ProfileIcon />
                        <span>Perfil</span>
                    </NavLink>
                ) : (
                    <NavLink to="/login" className={linkClass}>
                        <LoginIcon />
                        <span>Ingresar</span>
                    </NavLink>
                )}
            </nav>
        </div>
    );
}
