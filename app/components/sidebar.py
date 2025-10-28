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
            rx.el.div(
                rx.el.nav(
                    nav_item("home", "Dashboard", "/", True),
                    nav_item("settings", "Settings", "#", False),
                    class_name="grid items-start gap-1 text-sm font-medium",
                ),
                rx.el.div(
                    rx.upload.root(
                        rx.el.div(
                            rx.icon("cloud_upload", class_name="h-5 w-5 text-gray-500"),
                            rx.el.p(
                                "Upload Cookies File",
                                class_name="text-sm text-gray-600",
                            ),
                            rx.cond(
                                VideoState.cookie_file_path,
                                rx.el.span(
                                    VideoState.cookie_file_path.split("/")[-1],
                                    class_name="text-xs text-purple-600 mt-1 truncate",
                                ),
                                None,
                            ),
                            class_name="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors",
                        ),
                        id="cookie_upload",
                        on_drop=VideoState.handle_cookie_upload,
                        border="none",
                        padding="0",
                        background="transparent",
                    ),
                    class_name="mt-auto p-4",
                ),
                class_name="flex-1 overflow-auto py-4 px-4 flex flex-col",
            ),
        ),
        class_name="hidden border-r bg-gray-50/40 md:flex md:flex-col w-64",
    )