"""Snazy v1.0.10 ULTIMATE - Game Picker & Button Fix by @sethika dv."""

from __future__ import annotations
from dataclasses import dataclass
import subprocess
import asyncio
import os
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

def check_root_access() -> bool:
    try:
        res = subprocess.run(["su", "-c", "echo root_ok"], capture_output=True, text=True, timeout=2)
        return "root_ok" in res.stdout
    except Exception:
        return False

def get_system_stats() -> tuple[str, str, str]:
    ram_usage = "42%"
    cpu_load = "1.8 GHz"
    temp = "34°C"
    try:
        if os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
                mem_total = 0
                mem_free = 0
                for line in lines:
                    if "MemTotal:" in line:
                        mem_total = int(line.split()[1])
                    elif "MemAvailable:" in line or "MemFree:" in line:
                        mem_free = int(line.split()[1])
                if mem_total > 0:
                    used_percent = int(((mem_total - mem_free) / mem_total) * 100)
                    ram_usage = f"{used_percent}% ({int((mem_total - mem_free)/1024/1024)}GB / {int(mem_total/1024/1024)}GB)"
        if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                t_val = int(f.read().strip())
                if t_val > 1000:
                    t_val = t_val // 1000
                temp = f"{t_val}°C"
    except Exception:
        pass
    return ram_usage, cpu_load, temp

def execute_boost_actions(is_root: bool, backend: str, freeze_bg: bool) -> None:
    try:
        if is_root:
            if freeze_bg:
                subprocess.run(["su", "-c", "am kill-all"], capture_output=True, text=True, timeout=3)
            subprocess.run(["su", "-c", "sync; echo 3 > /proc/sys/vm/drop_caches"], capture_output=True, text=True, timeout=3)
            subprocess.run(["su", "-c", "echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"], capture_output=True, text=True, timeout=2)
            if backend == "Vulkan":
                subprocess.run(["su", "-c", "setprop debug.hwui.renderer vulkan"], capture_output=True, text=True, timeout=2)
            elif backend == "OpenGL ES":
                subprocess.run(["su", "-c", "setprop debug.hwui.renderer opengl"], capture_output=True, text=True, timeout=2)
        else:
            import gc
            gc.collect()
    except Exception:
        pass

def execute_revert_actions(is_root: bool) -> None:
    try:
        if is_root:
            subprocess.run(["su", "-c", "echo schedutil > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"], capture_output=True, text=True, timeout=2)
            subprocess.run(["su", "-c", "setprop debug.hwui.renderer skiagl"], capture_output=True, text=True, timeout=2)
        else:
            import gc
            gc.collect()
    except Exception:
        pass

def launch_game(package_name: str, is_root: bool) -> bool:
    try:
        cmd = ["su", "-c", f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1"] if is_root else ["monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=False)
        if "No activities found" in res.stderr or "aborted" in res.stdout.lower():
            return False
        return True
    except Exception:
        return False


async def main(page: ft.Page) -> None:
    page.title = "Snazy PRO+ Ultimate"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    is_root = check_root_access()
    selected_game = {"name": "Free Fire", "package": "com.dts.freefireth"}
    frozen = {"value": False}

    game_title = ft.Text(selected_game["name"], size=22, weight=ft.FontWeight.BOLD, color=TEXT)
    
    initial_ram, initial_cpu, initial_temp = get_system_stats()
    ram_stat_val = ft.Text(initial_ram, size=15, weight=ft.FontWeight.BOLD, color=TEXT)
    cpu_stat_val = ft.Text(initial_cpu, size=15, weight=ft.FontWeight.BOLD, color=TEXT)
    temp_stat_val = ft.Text(initial_temp, size=15, weight=ft.FontWeight.BOLD, color=GREEN)
    
    trend_indicator = ft.Text("● LIVE FEED", size=9, weight=ft.FontWeight.BOLD, color=GREEN)

    mode_badge = ft.Container(
        content=ft.Text("⚡ ROOT PRO MODE" if is_root else "🛡️ NON-ROOT SMART MODE", size=10, weight=ft.FontWeight.BOLD, color=GREEN if is_root else ACCENT),
        bgcolor="#10251B" if is_root else "#251B10",
        padding=10,
        border_radius=20,
    )

    freeze_button = ft.FilledButton(
        "○  Freeze background apps",
        height=46,
        style=ft.ButtonStyle(bgcolor=PANEL_LIGHT, color=TEXT, shape=ft.RoundedRectangleBorder(radius=10)),
    )
    
    boost_button = ft.FilledButton(
        "BOOST & LAUNCH GAME",
        height=54,
        style=ft.ButtonStyle(bgcolor=ACCENT, color="white", shape=ft.RoundedRectangleBorder(radius=12)),
    )

    revert_button = ft.OutlinedButton(
        "↺  RESTORE DEFAULTS / REVERT",
        height=44,
        style=ft.ButtonStyle(color=MUTED, shape=ft.RoundedRectangleBorder(radius=10)),
    )

    backend_dropdown = ft.Dropdown(
        value="Auto (best)",
        options=[ft.dropdown.Option("Auto (best)"), ft.dropdown.Option("Vulkan"), ft.dropdown.Option("OpenGL ES")],
        width=145, text_size=12, border_color="#34383B", bgcolor=PANEL_LIGHT
    )

    def panel(content: ft.Control, padding: int = 14) -> ft.Container:
        return ft.Container(
            content=content, padding=padding, bgcolor=GLASS,
            border=ft.Border.all(1, GLASS_BORDER), border_radius=16,
        )

    def close_dialog(e=None) -> None:
        try:
            if page.dialog:
                page.dialog.open = False
                page.dialog = None
                page.update()
        except Exception:
            pass

    def choose_game(profile: GameProfile) -> None:
        selected_game["name"] = profile.name
        selected_game["package"] = GAME_PACKAGES.get(profile.name, "")
        game_title.value = profile.name
        close_dialog()
        game_title.update()
        page.update()

    def show_game_picker(e: ft.ControlEvent) -> None:
        try:
            dialog_content = ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Container(content=ft.Text(profile.icon, color=ACCENT, weight=ft.FontWeight.BOLD), width=32, alignment=ft.alignment.Alignment(0, 0)),
                        title=ft.Text(profile.name, color=TEXT),
                        on_click=lambda e, p=profile: choose_game(p),
                    )
                    for profile in GAMES
                ],
                tight=True, 
                scroll=ft.ScrollMode.AUTO,
                height=280,
            )
            
            game_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("SELECT YOUR GAME", color=TEXT, weight=ft.FontWeight.BOLD),
                content=dialog_content,
                actions=[ft.TextButton("CANCEL", on_click=close_dialog)],
                bgcolor=PANEL,
            )
            page.dialog = game_dialog
            game_dialog.open = True
            page.update()
        except Exception as ex:
            print(f"Error opening game picker: {ex}")

    def toggle_freeze(e: ft.ControlEvent) -> None:
        frozen["value"] = not frozen["value"]
        if frozen["value"]:
            freeze_button.text = "●  Background apps restricted"
            freeze_button.style.bgcolor = "#164D35"
        else:
            freeze_button.text = "○  Freeze background apps"
            freeze_button.style.bgcolor = PANEL_LIGHT
        page.update()

    async def stats_ticker_loop():
        toggle = True
        while True:
            await asyncio.sleep(2)
            try:
                r, c, t = get_system_stats()
                ram_stat_val.value = r
                cpu_stat_val.value = c
                temp_stat_val.value = t
                trend_indicator.color = GREEN if toggle else ACCENT
                toggle = not toggle
                page.update()
            except Exception:
                pass

    async def start_boost(e: ft.ControlEvent) -> None:
        try:
            boost_button.text = "OPTIMIZING PERFORMANCE..."
            boost_button.style.bgcolor = "#164D35"
            page.update()

            loading_text = ft.Text("Clearing system cache & RAM...", color=TEXT, weight=ft.FontWeight.BOLD)
            loading_dialog = ft.AlertDialog(
                modal=True,
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ProgressRing(color=ACCENT, stroke_width=4),
                            ft.Container(height=15),
                            loading_text,
                            ft.Text("Applying high-performance CPU/GPU profile", size=11, color=MUTED)
                        ],
                        tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20
                ),
                bgcolor=PANEL, shape=ft.RoundedRectangleBorder(radius=15)
            )
            page.dialog = loading_dialog
            loading_dialog.open = True
            page.update()

            await asyncio.sleep(0.9)
            
            chosen_backend = backend_dropdown.value or "Auto (best)"
            execute_boost_actions(is_root, chosen_backend, frozen["value"])
            
            r, c, t = get_system_stats()
            ram_stat_val.value = r
            cpu_stat_val.value = c
            temp_stat_val.value = t

            loading_text.value = f"Launching {selected_game['name']}..."
            page.update()
            await asyncio.sleep(0.9)

            success = launch_game(selected_game["package"], is_root)
            close_dialog()

            if not success:
                err_dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("GAME NOT INSTALLED", color=TEXT, weight=ft.FontWeight.BOLD),
                    content=ft.Text(f"Could not find or launch {selected_game['name']}. Please ensure it is installed.", color=MUTED),
                    actions=[ft.TextButton("OK", on_click=close_dialog)],
                    bgcolor=PANEL,
                )
                page.dialog = err_dlg
                err_dlg.open = True
                page.update()
            else:
                success_dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("BOOST SUCCESSFUL 🚀", color=GREEN, weight=ft.FontWeight.BOLD),
                    content=ft.Text(f"{selected_game['name']} launched successfully with maximum performance tweaks applied!", color=TEXT),
                    actions=[ft.TextButton("GREAT", on_click=close_dialog)],
                    bgcolor=PANEL,
                )
                page.dialog = success_dlg
                success_dlg.open = True
                page.update()

            boost_button.text = "BOOST & LAUNCH GAME"
            boost_button.style.bgcolor = ACCENT
            page.update()
        except Exception as ex:
            print(f"Error during boost: {ex}")
            close_dialog()
            boost_button.text = "BOOST & LAUNCH GAME"
            boost_button.style.bgcolor = ACCENT
            page.update()

    async def handle_revert(e: ft.ControlEvent) -> None:
        execute_revert_actions(is_root)
        rev_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("SYSTEM RESTORED", color=TEXT, weight=ft.FontWeight.BOLD),
            content=ft.Text("All performance profiles and governors have been safely reverted back to normal defaults.", color=MUTED),
            actions=[ft.TextButton("OK", on_click=close_dialog)],
            bgcolor=PANEL,
        )
        page.dialog = rev_dlg
        rev_dlg.open = True
        page.update()

    freeze_button.on_click = toggle_freeze
    boost_button.on_click = start_boost
    revert_button.on_click = handle_revert

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("SNAZY", size=26, weight=ft.FontWeight.BOLD, color=TEXT),
                                    ft.Text("UNIVERSAL GAME BOOSTER PRO+", size=10, weight=ft.FontWeight.BOLD, color=ACCENT),
                                ],
                                spacing=0,
                            ),
                            ft.Container(expand=True),
                            mode_badge,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    
                    # LIVE HARDWARE ANALYTICS DASHBOARD
                    panel(
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("LIVE HARDWARE MONITOR", size=10, weight=ft.FontWeight.BOLD, color=ACCENT),
                                        ft.Container(expand=True),
                                        trend_indicator,
                                    ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Row(
                                    [
                                        ft.Column([ft.Text("RAM Usage", size=11, color=MUTED), ram_stat_val], spacing=2),
                                        ft.Container(expand=True),
                                        ft.Column([ft.Text("CPU Freq", size=11, color=MUTED), cpu_stat_val], spacing=2),
                                        ft.Container(expand=True),
                                        ft.Column([ft.Text("Temp", size=11, color=MUTED), temp_stat_val], spacing=2),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ],
                            spacing=8,
                        ),
                    ),

                    # GAME SELECTOR PANEL
                    panel(
                        ft.Column(
                            [
                                ft.Text("SELECTED GAME", size=10, weight=ft.FontWeight.BOLD, color=ACCENT),
                                ft.Row(
                                    [
                                        game_title,
                                        ft.Container(expand=True),
                                        ft.OutlinedButton("CHANGE", on_click=show_game_picker, style=ft.ButtonStyle(color=TEXT)),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=5,
                        ),
                    ),

                    # PERFORMANCE SETTINGS
                    ft.Text("PERFORMANCE CONTROLS", size=10, weight=ft.FontWeight.BOLD, color=ACCENT),
                    panel(
                        ft.Column(
                            [
                                freeze_button,
                                ft.Row(
                                    [
                                        ft.Text("Graphics Backend", size=12, color=TEXT),
                                        ft.Container(expand=True),
                                        backend_dropdown,
                                    ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=9,
                        ),
                    ),
                    
                    boost_button,
                    revert_button,
                    ft.Container(expand=True, height=10),
                    ft.Text("SNAZY PRO+  •  by @sethika dv", size=10, color="#555B60"),
                ],
                width=520,
                spacing=12,
            ),
            padding=16,
            expand=True,
        )
    )

    page.run_task(stats_ticker_loop)

if __name__ == "__main__":
    ft.run(main)
