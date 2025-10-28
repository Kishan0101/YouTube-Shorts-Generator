import reflex as rx
from app.components.sidebar import sidebar
from app.components.dashboard import dashboard
from app.states.video_state import VideoState


def index() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            dashboard(),
            class_name="flex-1 w-full min-h-screen bg-gray-100/30 overflow-y-auto",
        ),
        class_name="flex min-h-screen w-full font-['Raleway'] bg-gray-50",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, title="YT Shorts Generator")