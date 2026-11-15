import { useEffect, useRef, useState } from "react";

import styles from "./styles/NotInterestedMenu.module.css";

interface NotInterestedMenuProps {
    onSelect: () => void;
}

export function NotInterestedMenu({ onSelect }: NotInterestedMenuProps) {
    const [isOpen, setIsOpen] = useState(false);
    const wrapperRef = useRef<HTMLDivElement>(null);

    // Close the menu on outside click or Escape
    useEffect(() => {
        if (!isOpen) return;

        const handlePointerDown = (event: PointerEvent) => {
            if (!wrapperRef.current?.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === "Escape") {
                setIsOpen(false);
            }
        };

        document.addEventListener("pointerdown", handlePointerDown);
        document.addEventListener("keydown", handleKeyDown);

        return () => {
            document.removeEventListener("pointerdown", handlePointerDown);
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [isOpen]);

    return (
        <div className={styles.wrapper} ref={wrapperRef}>
            <button
                type="button"
                className={`${styles.trigger} ${isOpen ? styles.open : ""}`}
                onClick={() => setIsOpen((previous) => !previous)}
                aria-haspopup="menu"
                aria-expanded={isOpen}
                aria-label="Más opciones"
            >
                <svg
                    viewBox="0 0 24 24"
                    width="24"
                    height="24"
                    aria-hidden="true"
                    fill="currentColor"
                >
                    <circle cx="12" cy="5" r="1.8" />
                    <circle cx="12" cy="12" r="1.8" />
                    <circle cx="12" cy="19" r="1.8" />
                </svg>
            </button>

            {isOpen && (
                <div className={styles.menu} role="menu">
                    <button
                        type="button"
                        role="menuitem"
                        className={styles.item}
                        onClick={() => {
                            setIsOpen(false);
                            onSelect();
                        }}
                    >
                        <svg
                            viewBox="0 0 24 24"
                            width="22"
                            height="22"
                            aria-hidden="true"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                        >
                            <circle cx="12" cy="12" r="9" />
                            <line x1="5.6" y1="5.6" x2="18.4" y2="18.4" />
                        </svg>
                        No me interesa
                    </button>
                </div>
            )}
        </div>
    );
}
