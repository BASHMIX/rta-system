from typing import Optional

import customtkinter as ctk

from src.config.models import GameProfile, OBSWebSocketConfig
from src.config.profiles import ProfileManager
from src.ui.profile_manager import ProfileListFrame


class RTAApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RTA System - Save & Load Configs")
        self.geometry("900x600")

        self.profile_manager = ProfileManager()
        self.current_profile: Optional[GameProfile] = None
        self.current_obs_ws: OBSWebSocketConfig = OBSWebSocketConfig()

        self.profile_frame = ProfileListFrame(
            self,
            profile_manager=self.profile_manager,
            on_load=self._on_profile_loaded,
        )
        self.profile_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.main_area = ctk.CTkFrame(self)
        self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(self.main_area, text="Ready", font=("", 12))
        self.status_label.pack(pady=20)

        self._auto_load_last_profile()

    def _auto_load_last_profile(self):
        last_name = self.profile_manager.last_loaded_name
        if last_name:
            try:
                profile = self.profile_manager.load(last_name)
                self._apply_profile(profile)
                self.status_label.configure(text=f"Auto-loaded profile: {last_name}")
            except (FileNotFoundError, ValueError):
                self.status_label.configure(text="No saved profiles found")

    def _on_profile_loaded(self, profile: GameProfile):
        if self.current_profile:
            diff = self.profile_manager.check_obs_credential_diff(
                profile.name, self.current_obs_ws
            )
            if diff:
                self._ask_obs_reconnect(profile)
            else:
                self._apply_profile(profile)
        else:
            self._apply_profile(profile)

    def _ask_obs_reconnect(self, profile: GameProfile):
        dialog = ctk.CTkToplevel(self)
        dialog.title("OBS Credentials Changed")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=(
                f"Profile '{profile.name}' has different OBS WebSocket "
                f"settings. Reconnect to OBS?"
            ),
            wraplength=350,
        ).pack(pady=(20, 15))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()

        def on_reconnect():
            dialog.destroy()
            self.status_label.configure(
                text=f"Loaded '{profile.name}' — OBS reconnection needed"
            )
            self._apply_profile(profile)

        def on_keep():
            dialog.destroy()
            self._apply_profile(profile)

        ctk.CTkButton(btn_frame, text="Reconnect", command=on_reconnect).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Keep Current", command=on_keep).pack(side="left", padx=5)

    def _apply_profile(self, profile: GameProfile):
        self.current_profile = profile
        self.current_obs_ws = profile.system.obs_websocket
        self.status_label.configure(text=f"Loaded: {profile.name}")


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = RTAApp()
    app.mainloop()


if __name__ == "__main__":
    main()
