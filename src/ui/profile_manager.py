from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk

from src.config.models import GameProfile
from src.config.profiles import ProfileManager


class ProfileListFrame(ctk.CTkFrame):
    def __init__(self, master, profile_manager: ProfileManager, on_load: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.profile_manager = profile_manager
        self.on_load = on_load
        self.selected_name: Optional[str] = None

        self.list_label = ctk.CTkLabel(self, text="Saved Profiles", font=("", 14, "bold"))
        self.list_label.pack(pady=(0, 5))

        self.listbox = ctk.CTkScrollableFrame(self, height=200)
        self.listbox.pack(fill="both", expand=True, pady=(0, 10))

        self.empty_label = ctk.CTkLabel(
            self,
            text="No saved profiles yet.\nConfigure your first game and click Save As.",
            text_color="gray",
        )

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x")

        self.load_btn = ctk.CTkButton(btn_frame, text="Load", command=self._on_load, state="disabled")
        self.load_btn.pack(side="left", padx=2, pady=2)

        self.rename_btn = ctk.CTkButton(btn_frame, text="Rename", command=self._on_rename, state="disabled")
        self.rename_btn.pack(side="left", padx=2, pady=2)

        self.delete_btn = ctk.CTkButton(btn_frame, text="Delete", command=self._on_delete, state="disabled")
        self.delete_btn.pack(side="left", padx=2, pady=2)

        self.dup_btn = ctk.CTkButton(btn_frame, text="Duplicate", command=self._on_duplicate, state="disabled")
        self.dup_btn.pack(side="left", padx=2, pady=2)

        self.export_btn = ctk.CTkButton(btn_frame, text="Export", command=self._on_export, state="disabled")
        self.export_btn.pack(side="left", padx=2, pady=2)

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(5, 0))

        self.save_btn = ctk.CTkButton(bottom_frame, text="Save Current As...", command=self._on_save_as)
        self.save_btn.pack(side="left", padx=2)

        self.import_btn = ctk.CTkButton(bottom_frame, text="Import", command=self._on_import)
        self.import_btn.pack(side="left", padx=2)

        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=(5, 0))

        self.refresh()

    def refresh(self):
        for widget in self.listbox.winfo_children():
            widget.destroy()

        names = self.profile_manager.profile_names
        if not names:
            self.empty_label.pack(pady=20)
            self.load_btn.configure(state="disabled")
            self.rename_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            self.dup_btn.configure(state="disabled")
            self.export_btn.configure(state="disabled")
            return

        self.empty_label.pack_forget()
        for name in names:
            is_loaded = name == self.profile_manager.last_loaded_name
            btn = ctk.CTkButton(
                self.listbox,
                text=f"{'✓ ' if is_loaded else ''}{name}",
                anchor="w",
                fg_color="transparent" if not is_loaded else None,
                border_width=0,
                command=lambda n=name: self._select(n),
            )
            btn.pack(fill="x", pady=1)
        self.error_label.configure(text="")

    def _select(self, name: str):
        self.selected_name = name
        self.load_btn.configure(state="normal")
        self.rename_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")
        self.dup_btn.configure(state="normal")
        self.export_btn.configure(state="normal")
        self.error_label.configure(text="")

    def _on_load(self):
        if not self.selected_name:
            return
        try:
            profile = self.profile_manager.load(self.selected_name)
            if self.on_load:
                self.on_load(profile)
            self.refresh()
        except ValueError as e:
            self.error_label.configure(text=str(e))

    def _on_save_as(self):
        SaveAsDialog(
            master=self.winfo_toplevel(),
            profile_manager=self.profile_manager,
            current_config=None,
            on_save=lambda p: self.refresh(),
        )

    def _on_rename(self):
        if not self.selected_name:
            return
        RenameDialog(
            master=self.winfo_toplevel(),
            profile_manager=self.profile_manager,
            old_name=self.selected_name,
            on_rename=lambda: self.refresh(),
        )

    def _on_delete(self):
        if not self.selected_name:
            return
        name = self.selected_name
        ConfirmDialog(
            master=self.winfo_toplevel(),
            title="Delete Profile",
            message=f"Delete '{name}'? This cannot be undone.",
            on_confirm=lambda: (
                self.profile_manager.delete(name),
                self.refresh(),
            ),
        )

    def _on_duplicate(self):
        if not self.selected_name:
            return
        try:
            self.profile_manager.duplicate(self.selected_name)
            self.refresh()
        except FileNotFoundError as e:
            self.error_label.configure(text=str(e))

    def _on_export(self):
        if not self.selected_name:
            return
        file_path = ctk.filedialog.asksaveasfilename(
            title="Export Profile",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"{self.selected_name}.json",
        )
        if file_path:
            try:
                self.profile_manager.export(self.selected_name, file_path)
                self.error_label.configure(text=f"Exported to {Path(file_path).name}", text_color="green")
            except FileNotFoundError as e:
                self.error_label.configure(text=str(e))

    def _on_import(self):
        file_path = ctk.filedialog.askopenfilename(
            title="Import Profile",
            filetypes=[("JSON files", "*.json")],
        )
        if file_path:
            try:
                name = self.profile_manager.import_(file_path)
                self.error_label.configure(text=f"Imported '{name}'", text_color="green")
                self.refresh()
            except ValueError as e:
                self.error_label.configure(text=str(e))


class SaveAsDialog(ctk.CTkToplevel):
    def __init__(self, master, profile_manager: ProfileManager, current_config: Optional[GameProfile], on_save: Callable):
        super().__init__(master)
        self.profile_manager = profile_manager
        self.current_config = current_config
        self.on_save = on_save

        self.title("Save Profile As")
        self.geometry("400x200")
        self.resizable(False, False)

        self.entry_label = ctk.CTkLabel(self, text="Profile name:")
        self.entry_label.pack(pady=(20, 5))

        self.name_entry = ctk.CTkEntry(self, width=300)
        self.name_entry.pack(pady=(0, 10))
        if current_config:
            self.name_entry.insert(0, current_config.name)

        self.warning_label = ctk.CTkLabel(self, text="", text_color="orange")
        self.warning_label.pack(pady=(0, 5))

        self.name_entry.bind("<KeyRelease>", self._check_overwrite)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(10, 0))

        self.save_btn = ctk.CTkButton(btn_frame, text="Save", command=self._on_save)
        self.save_btn.pack(side="left", padx=5)

        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy)
        self.cancel_btn.pack(side="left", padx=5)

        self.grab_set()

    def _check_overwrite(self, event=None):
        name = self.name_entry.get().strip()
        if name and self.profile_manager.confirm_overwrite(name):
            self.warning_label.configure(text=f"'{name}' already exists. Saving will overwrite it.")
        else:
            self.warning_label.configure(text="")

    def _on_save(self):
        name = self.name_entry.get().strip()
        if not name:
            self.warning_label.configure(text="Name is required", text_color="red")
            return

        if self.current_config:
            self.profile_manager.save(name, self.current_config)
        else:
            fake_config = GameProfile(name=name)
            self.profile_manager.save(name, fake_config)

        self.on_save(name)
        self.destroy()


class RenameDialog(ctk.CTkToplevel):
    def __init__(self, master, profile_manager: ProfileManager, old_name: str, on_rename: Callable):
        super().__init__(master)
        self.profile_manager = profile_manager
        self.old_name = old_name
        self.on_rename = on_rename

        self.title("Rename Profile")
        self.geometry("400x150")
        self.resizable(False, False)

        ctk.CTkLabel(self, text=f"Rename '{old_name}' to:").pack(pady=(20, 5))

        self.name_entry = ctk.CTkEntry(self, width=300)
        self.name_entry.insert(0, old_name)
        self.name_entry.pack(pady=(0, 10))

        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=(0, 5))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(btn_frame, text="Rename", command=self._on_rename).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        self.grab_set()

    def _on_rename(self):
        new_name = self.name_entry.get().strip()
        if not new_name:
            self.error_label.configure(text="Name is required")
            return
        try:
            self.profile_manager.rename(self.old_name, new_name)
            self.on_rename()
            self.destroy()
        except (FileNotFoundError, FileExistsError) as e:
            self.error_label.configure(text=str(e))


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, message: str, on_confirm: Callable):
        super().__init__(master)
        self.title(title)
        self.geometry("350x150")
        self.resizable(False, False)

        ctk.CTkLabel(self, text=message, wraplength=300).pack(pady=(20, 15))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(btn_frame, text="Confirm", command=self._confirm).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        self.on_confirm = on_confirm
        self.grab_set()

    def _confirm(self):
        self.on_confirm()
        self.destroy()
