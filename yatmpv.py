#!/usr/bin/env python3
import os
import platform
import mpv
from asyncio.tasks import current_task
from textual import on, events, binding
from textual.screen import Screen
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Label, Button, Header, Input
from textual.containers import VerticalScroll

class LeaveConfirm(Screen):
    """a screen to confirm leave"""

    def compose(self) -> ComposeResult:
        yield Label("Are you sure want to leave?")
        yield Button("Yes", id="leave_confirm")
        yield Button("No", id="leave_cancel")
    
    @on(Button.Pressed, "#leave_confirm")
    def leave(self) -> None: 
        self.app.exit()

    @on(Button.Pressed, "#leave_cancel")
    def leave_cancel(self) -> None: 
        self.dismiss()

class PlayerApp(App[None]):
    CSS = """Screen {
    layout: vertical;
    padding: 2;
    }

    Label {
    width: 100%;
		content-align: center bottom;
    text-style: bold;
    }

    Button {
    width: 100%;
		margin: 1 2;
    }"""
    BINDINGS = [ 
        Binding("down", "focus_next"), 
        Binding("up", "focus_previous"),
        Binding("left", "seek_forward"),
        Binding("right", "seek_backward"),
        Binding("space", "pause_play"),
        Binding("ctrl+q", "push_screen('Leave')")
    ]
    
    playing = False
    
    def action_seek_forward(self) -> None:
        current_time = self.player.time_pos or 0
        self.player.time_pos = current_time + 5

    def action_seek_backward(self) -> None:
        current_time = self.player.time_pos or 0
        self.player.time_pos = current_time - 5

    def on_mount(self) -> None: 
        self.player = mpv.MPV(ytdl=True, loop_file='inf') 
        self.install_screen(LeaveConfirm(), name="Leave")

    def compose(self) -> ComposeResult:
        yield Label(f"welcome to yatmpv!")
        yield Label(f"now playing:", id="now_playing")
        yield Input(placeholder="Search for mp3...")
        with VerticalScroll():
            for filename in os.listdir("."):
                yield Button(filename)
        yield Footer()
   
    def on_input_changed(self, event: Input.Changed) -> None:
        """filters tracks by input"""
        search_text = event.value.lower()
        all_buttons = self.query(Button)
        for button in all_buttons:
            button_text = str(button.label).lower()
            if search_text in button_text:
                button.styles.display = "block"
            else:
                button.styles.display = "none"

    def update_nowplaying(self, track_name: str) -> None:
        """update 'now_playing' label"""
        self.query_one("#now_playing", Label).update(f"Now playing: {track_name}")
        self.track = track_name

    def on_button_pressed(self, event: Button.Pressed) -> None: 
        """togggle track"""
        track_name = str(event.button.label)
        if self.playing and getattr(self, 'track', None) == track_name:
            self.playing = False
            self.player.stop()
            self.update_nowplaying("None")
        else:
            self.playing = True
            self.player.play(track_name)
            self.update_nowplaying(track_name)

    def action_pause_play(self) -> None:
        """toggle pause"""
        if hasattr(self, 'player'):
            self.player.pause = not self.player.pause

    def on_unmount(self) -> None:
        """terminates player after unmount"""
        if hasattr(self, 'player'):
            self.player.terminate()

if __name__ == "__main__":
    osname = platform.system()
    if osname == "Linux":
        home = os.environ["HOME"]
        music_dir = os.path.join(home, "Music")
        os.chdir(music_dir)
    elif osname == "Windows":
        user_profile = os.environ["USERPROFILE"]
        music_dir = os.path.join(user_profile, "Music")
        os.chdir(music_dir)
    elif osname == "Darwin":
        home = os.environ["HOME"]
        music_dir = os.path.join(home, "Music")
        os.chdir(music_dir)
    PlayerApp().run()
