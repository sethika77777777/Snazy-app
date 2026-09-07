"""Snazy, a compact Flet game-performance dashboard."""

from __future__ import annotations

from dataclasses import dataclass
import subprocess

import flet as ft


@dataclass(frozen=True)
class GameProfile:
    name: str
    icon: str


GAMES = [
	GameProfile("Apex Legends", "A"),
	GameProfile("Free Fire", "F"),
	GameProfile("Free Fire MAX", "F"),
	GameProfile("Call of Duty", "C"),
	GameProfile("Mobile Legends", "M"),
	GameProfile("PUBG Mobile", "P"),
]

GAME_PACKAGES = {
    "Apex Legends": "com.ea.gp.apexlegendsmobilefps",
    "Free Fire": "com.dts.freefireth",
    "Free Fire MAX": "com.dts.freefiremax",
    "Call of Duty": "com.activision.callofduty.shooter",
    "Mobile Legends": "com.mobile.legends",
    "PUBG Mobile": "com.tencent.ig",
}

BG = "#08090A"
PANEL = "#141618"
PANEL_LIGHT = "#1B1E21"
TEXT = "#F2F4F5"
MUTED = "#858B90"
ACCENT = "#F05A32"
GREEN = "#32C47B"
GLASS = "#CC141618"
GLASS_BORDER = "#3AFFFFFF"


def installed_packages() -> set[str] | None:
    """Read Android user packages, or return None outside Android."""
    try:
        result = subprocess.run(
            ["pm", "list", "packages", "-3"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    return {
        line.removeprefix("package:").strip()
        for line in result.stdout.splitlines()
        if line.removeprefix("package:").strip()
    }


def discover_installed_apps() -> list[str]:
    """Return selectable app names and keep WhatsApp available in the list."""
    fallback = ["Discord", "Spotify", "WhatsApp", "YouTube", "Instagram", "Chrome"]
    packages = installed_packages()
    if packages is None:
        return fallback

    package_names = []
    for package in packages:
        if package == "com.whatsapp":
            package_names.append("WhatsApp")
        else:
            package_names.append(package.rsplit(".", 1)[-1].replace("_", " ").title())
    return sorted(set(package_names + ["WhatsApp"])) or fallback


def launch_game(game_name: str) -> bool:
    """Launch a supported Android game when its package is installed."""
    package = GAME_PACKAGES.get(game_name)
    packages = installed_packages()
    if not package or packages is None or package not in packages:
        return False
    try:
        result = subprocess.run(
            ["monkey", "-p", package, "1"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def main(page: ft.Page) -> None:
    page.title = "Snazy"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    selected_game = {"name": "Apex Legends"}
    frozen = {"value": False}
    boosting = {"value": False}
    installed_apps = discover_installed_apps()
    active_apps = {name for name in installed_apps if name in {"Discord", "Spotify"}}

    game_title = ft.Text(selected_game["name"], size=22, weight=ft.FontWeight.BOLD, color=TEXT)
    freeze_button = ft.FilledButton(
        "○  Freeze background apps",
        height=46,
        style=ft.ButtonStyle(bgcolor=PANEL_LIGHT, color=TEXT, shape=ft.RoundedRectangleBorder(radius=10)),
    )
    boost_button = ft.FilledButton(
        "BOOST NOW",
        height=58,
        style=ft.ButtonStyle(bgcolor=ACCENT, color="white", shape=ft.RoundedRectangleBorder(radius=12)),
    )

    def panel(content: ft.Control, padding: int = 14) -> ft.Container:
        return ft.Container(
            content=content,
            padding=padding,
            bgcolor=GLASS,
            border=ft.Border.all(1, GLASS_BORDER),
            border_radius=16,
            blur=ft.Blur(10, 10),
        )

    def close_dialog(dialog: ft.AlertDialog) -> None:
        dialog.open = False
        page.update()

    def choose_game(profile: GameProfile, dialog: ft.AlertDialog) -> None:
        selected_game["name"] = profile.name
        game_title.value = profile.name
        close_dialog(dialog)

    def show_game_picker(_: ft.ControlEvent) -> None:
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("SELECT YOUR GAME", color=TEXT, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Container(content=ft.Text(profile.icon, color=ACCENT, weight=ft.FontWeight.BOLD), width=32, alignment=ft.Alignment.CENTER),
                        title=ft.Text(profile.name, color=TEXT),
                        trailing=ft.Text("SELECT", color=ACCENT, weight=ft.FontWeight.BOLD),
                        on_click=lambda _, item=profile: choose_game(item, dialog),
                    )
                    for profile in GAMES
                ],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=PANEL,
        )
        page.show_dialog(dialog)

    def toggle_freeze(_: ft.ControlEvent) -> None:
        frozen["value"] = not frozen["value"]
        freeze_button.text = "●  Background apps frozen" if frozen["value"] else "○  Freeze background apps"
        freeze_button.style.bgcolor = "#164D35" if frozen["value"] else PANEL_LIGHT
        page.update()

    def show_ignored(_: ft.ControlEvent) -> None:
        def update_app(event: ft.ControlEvent) -> None:
            if event.control.value:
                active_apps.add(event.control.label)
            else:
                active_apps.discard(event.control.label)

        def save_apps(_: ft.ControlEvent) -> None:
            active_count.value = f"⚙  Apps that stay active   {len(active_apps)}"
            close_dialog(dialog)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("KEEP ACTIVE", color=TEXT, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    ft.Text("Choose installed apps to keep active.", color=MUTED),
                    *[
                        ft.Checkbox(
                            label=name,
                            value=name in active_apps,
                            fill_color=ACCENT,
                            on_change=update_app,
                        )
                        for name in installed_apps
                    ],
                ],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[ft.TextButton("DONE", on_click=save_apps)],
            bgcolor=PANEL,
        )
        page.show_dialog(dialog)

    def start_boost(_: ft.ControlEvent) -> None:
        boosting["value"] = True
        boost_button.text = f"BOOST ACTIVE  •  {selected_game['name'].upper()}"
        boost_button.style.bgcolor = "#164D35"
        page.update()
        if not launch_game(selected_game["name"]):
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("GAME NOT INSTALLED", color=TEXT, weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    f"You did not install {selected_game['name']} on this device.",
                    color=MUTED,
                ),
                actions=[ft.TextButton("OK", on_click=lambda _: close_dialog(dialog))],
                bgcolor=PANEL,
            )
            page.show_dialog(dialog)

    def restore(_: ft.ControlEvent) -> None:
        boosting["value"] = False
        frozen["value"] = False
        freeze_button.text = "○  Freeze background apps"
        freeze_button.style.bgcolor = PANEL_LIGHT
        boost_button.text = "BOOST NOW"
        boost_button.style.bgcolor = ACCENT
        page.update()

    freeze_button.on_click = toggle_freeze
    boost_button.on_click = start_boost
    active_count = ft.Text(f"⚙  Apps that stay active   {len(active_apps)}", size=14, color=TEXT)

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("SNAZY", size=26, weight=ft.FontWeight.BOLD, color=TEXT),
                                    ft.Text("GAME PERFORMANCE", size=10, weight=ft.FontWeight.BOLD, color=ACCENT),
                                ],
                                spacing=0,
                            ),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text("●  READY", size=11, weight=ft.FontWeight.BOLD, color=GREEN),
                                bgcolor="#10251B",
                                padding=ft.Padding(left=12, top=9, right=12, bottom=9),
                                border_radius=20,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    panel(
                        ft.Column(
                            [
                                ft.Text("ACTIVE GAME", size=10, weight=ft.FontWeight.BOLD, color=ACCENT),
                                ft.Row(
                                    [
                                        game_title,
                                        ft.Container(expand=True),
                                        ft.OutlinedButton("CHANGE", on_click=show_game_picker, style=ft.ButtonStyle(color=TEXT)),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                ft.Text("Balanced profile • low memory mode", size=11, color=MUTED),
                            ],
                            spacing=5,
                        ),
                    ),
                    ft.Text("BOOST SETTINGS", size=10, weight=ft.FontWeight.BOLD, color=ACCENT),
                    panel(
                        ft.Column(
                            [
                                freeze_button,
                                ft.FilledButton(
                                    content=active_count,
                                    height=46,
                                    on_click=show_ignored,
                                    style=ft.ButtonStyle(bgcolor=PANEL_LIGHT, color=TEXT, shape=ft.RoundedRectangleBorder(radius=10)),
                                ),
                                ft.Row(
                                    [
                                        ft.Text("Graphics backend", size=12, color=TEXT),
                                        ft.Container(expand=True),
                                        ft.Dropdown(
                                            value="Auto (best)",
                                            options=[ft.dropdown.Option("Auto (best)"), ft.dropdown.Option("Vulkan"), ft.dropdown.Option("OpenGL ES")],
                                            width=145,
                                            text_size=12,
                                            border_color="#34383B",
                                            bgcolor=PANEL_LIGHT,
                                        ),
                                    ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=9,
                        ),
                    ),
                    boost_button,
                    ft.Container(expand=True, height=30),
                    ft.OutlinedButton("↺  RESTORE NORMAL", on_click=restore, height=44, style=ft.ButtonStyle(color=TEXT)),
                    ft.Text("SNAZY  •  by @sethika dv", size=10, color="#555B60"),
                ],
                width=min(page.width - 30, 520) if page.width else 520,
                spacing=12,
            ),
            padding=ft.Padding(left=16, top=18, right=16, bottom=14),
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.run(main)
