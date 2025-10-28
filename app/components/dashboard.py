import reflex as rx
from app.states.video_state import VideoState, Video, Clip
from app.states.analysis_state import AnalysisState


def video_input_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Create New Project", class_name="text-lg font-semibold text-gray-900"
            ),
            rx.el.p(
                "Enter a YouTube video link to get started.",
                class_name="text-sm text-gray-500 mt-1",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.input(
                placeholder="https://www.youtube.com/watch?v=...",
                on_change=VideoState.set_video_url,
                class_name="flex-grow bg-white border border-gray-300 rounded-l-lg px-4 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-shadow duration-200",
                default_value=VideoState.video_url,
            ),
            rx.el.button(
                rx.cond(
                    VideoState.is_loading,
                    rx.spinner(color="white", size="1"),
                    rx.el.span("Import Video"),
                ),
                on_click=VideoState.add_video,
                disabled=VideoState.is_loading,
                class_name="bg-purple-600 text-white px-6 py-2 rounded-r-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-colors duration-200 disabled:bg-purple-300 disabled:cursor-not-allowed",
            ),
            class_name="flex w-full",
        ),
        rx.cond(
            VideoState.error,
            rx.el.div(
                rx.icon("badge_alert", class_name="h-4 w-4 mr-2"),
                rx.el.span(VideoState.error),
                class_name="flex items-center text-sm text-red-600 mt-2",
            ),
            None,
        ),
        class_name="bg-white p-6 rounded-lg shadow-[0px_1px_3px_rgba(0,0,0,0.12)] border border-gray-200/50",
    )


def project_card(project: Video) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.image(
                src=project["thumbnail"],
                alt=project["title"],
                class_name="w-full h-40 object-cover rounded-t-lg",
            ),
            rx.el.div(
                rx.match(
                    project["status"],
                    (
                        "downloading",
                        rx.el.div(
                            rx.el.div(
                                class_name=f"bg-purple-600 h-1.5 rounded-full transition-all duration-300",
                                style={"width": f"{project['progress']}%"},
                            ),
                            class_name="w-full bg-gray-200 rounded-full h-1.5 mb-2",
                        ),
                    ),
                    (
                        "processing",
                        rx.el.div(
                            rx.el.div(
                                class_name="w-full bg-purple-200 rounded-full h-1.5 animate-pulse"
                            ),
                            class_name="w-full bg-gray-200 rounded-full h-1.5 mb-2",
                        ),
                    ),
                    rx.el.div(),
                ),
                class_name="absolute top-0 left-0 w-full",
            ),
            class_name="relative",
        ),
        rx.el.div(
            rx.el.h3(
                project["title"], class_name="font-semibold text-gray-800 truncate"
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("clock", class_name="h-4 w-4 text-gray-500"),
                    rx.el.span(
                        project["duration_str"], class_name="text-sm text-gray-600"
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.span(
                    project["status"].capitalize(),
                    class_name=rx.match(
                        project["status"],
                        (
                            "pending",
                            "text-xs font-medium bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full",
                        ),
                        (
                            "downloading",
                            "text-xs font-medium bg-blue-100 text-blue-800 px-2 py-1 rounded-full",
                        ),
                        (
                            "analyzing",
                            "text-xs font-medium bg-purple-100 text-purple-800 px-2 py-1 rounded-full",
                        ),
                        (
                            "complete",
                            "text-xs font-medium bg-green-100 text-green-800 px-2 py-1 rounded-full",
                        ),
                        (
                            "error",
                            "text-xs font-medium bg-red-100 text-red-800 px-2 py-1 rounded-full",
                        ),
                        "text-xs font-medium bg-gray-100 text-gray-800 px-2 py-1 rounded-full",
                    ),
                ),
                class_name="flex items-center justify-between mt-3",
            ),
            rx.cond(
                project["error_message"],
                rx.el.p(
                    project["error_message"],
                    class_name="text-xs text-red-600 mt-2 truncate",
                ),
                None,
            ),
            class_name="p-4",
        ),
        rx.cond(
            (project["status"] == "complete") & (project["file_path"] != None),
            rx.el.div(
                rx.el.button(
                    rx.cond(
                        VideoState.processing_video_id == project["id"],
                        rx.spinner(color="white", size="1"),
                        rx.el.span("Analyze"),
                    ),
                    on_click=lambda: AnalysisState.analyze_video(project["id"]),
                    disabled=VideoState.processing_video_id != None,
                    class_name="w-full bg-purple-600 text-white text-sm font-semibold py-2 rounded-b-lg hover:bg-purple-700 transition-colors duration-200 disabled:bg-purple-300",
                )
            ),
            None,
        ),
        class_name="bg-white rounded-lg shadow-[0px_1px_3px_rgba(0,0,0,0.12)] overflow-hidden border border-gray-200/50 hover:shadow-[0px_4px_8px_rgba(0,0,0,0.15)] transition-shadow duration-300",
    )


def clip_card(clip: Clip, index: int) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    f"Clip #{index + 1}", class_name="font-semibold text-purple-700"
                ),
                rx.el.div(
                    rx.icon("star", class_name="h-4 w-4 text-yellow-500"),
                    rx.el.span(
                        f"{clip['score']:.2f}",
                        class_name="text-sm font-bold text-gray-800",
                    ),
                    class_name="flex items-center gap-1 bg-yellow-100 px-2 py-1 rounded-full",
                ),
                class_name="flex justify-between items-center mb-2",
            ),
            rx.el.p(clip["text"], class_name="text-sm text-gray-600 line-clamp-2 mb-3"),
            rx.el.div(
                rx.el.div(
                    rx.icon("clock", class_name="h-4 w-4 text-gray-500"),
                    rx.el.span(
                        clip["duration_str"], class_name="text-xs text-gray-500"
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.button(
                    rx.icon("scissors", class_name="h-4 w-4 mr-2"),
                    "Generate Short",
                    class_name="text-xs bg-purple-500 text-white px-3 py-1 rounded-md hover:bg-purple-600 transition-colors",
                ),
                class_name="flex justify-between items-center",
            ),
            class_name="p-4 bg-white rounded-lg border border-gray-200 shadow-sm",
        )
    )


def project_list() -> rx.Component:
    return rx.el.div(
        rx.el.h2("My Projects", class_name="text-lg font-semibold text-gray-900 mb-4"),
        rx.cond(
            VideoState.has_projects,
            rx.el.div(
                rx.foreach(
                    VideoState.formatted_video_projects,
                    lambda p: rx.el.div(
                        project_card(p),
                        rx.cond(
                            p["clips"].length() > 0,
                            rx.el.div(
                                rx.el.h3(
                                    "Generated Clips",
                                    class_name="font-semibold text-md text-gray-800 mt-4 mb-2 px-1",
                                ),
                                rx.el.div(
                                    rx.foreach(p["clips"], clip_card),
                                    class_name="space-y-3",
                                ),
                                class_name="mt-4",
                            ),
                            None,
                        ),
                    ),
                ),
                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6",
            ),
            rx.el.div(
                rx.icon("video-off", class_name="h-12 w-12 text-gray-400 mx-auto"),
                rx.el.h3(
                    "No Projects Yet",
                    class_name="mt-4 text-sm font-medium text-gray-900",
                ),
                rx.el.p(
                    "Import a video to get started.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center py-16 border-2 border-dashed border-gray-300 rounded-lg",
            ),
        ),
    )


def dashboard() -> rx.Component:
    return rx.el.div(
        video_input_card(),
        rx.el.div(class_name="my-8"),
        project_list(),
        class_name="p-6 md:p-8",
    )