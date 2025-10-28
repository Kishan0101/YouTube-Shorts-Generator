import reflex as rx
from app.states.video_state import VideoState


def nav_item(icon: str, text: str, href: str, is_active: bool) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.icon(icon, class_name="h-5 w-5"),
            rx.el.span(text),
            class_name=rx.cond(
                is_active,
                "flex items-center gap-3 rounded-lg bg-purple-100 px-3 py-2 text-purple-700 transition-all",
                "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900",
            ),
        ),
        href=href,
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("youtube", class_name="h-8 w-8 text-purple-600"),
                    rx.el.span(
                        "YT Shorts Gen",
                        class_name="ml-2 text-xl font-semibold text-gray-800",
                    ),
                    href="/",
                    class_name="flex items-center",
                ),
                class_name="flex h-16 items-center border-b px-6",
            ),
            rx.el.nav(
                nav_item("home", "Dashboard", "/", True),
                nav_item("settings", "Settings", "#", False),
                class_name="flex-1 overflow-auto py-4 px-4 grid items-start gap-1 text-sm font-medium",
            ),
        ),
        class_name="hidden border-r bg-gray-50/40 md:flex md:flex-col w-64",
    )