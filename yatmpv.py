#!/usr/bin/env python3
import os
import platform
import sys
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
        self.app.exit() #exits app after pressing "yes" button

    @on(Button.Pressed, "#leave_cancel")
    def leave_cancel(self) -> None: 
        self.dismiss() #hides screen after pressing "no" button

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
        Binding("ctrl+q", "push_screen('Leave')"),
    ]
    
    playing = False
    
    def action_seek_forward(self) -> None:
        """fast-forwarding track"""
        current_time = self.player.time_pos or 0 # current time of track to fast-forward it
        self.player.time_pos = current_time + 5 # fast-forwarding track

    def action_seek_backward(self) -> None:
        """rewinds track"""
        current_time = self.player.time_pos or 0 # current time of track to rewind it
        self.player.time_pos = current_time - 5 # rewinds track

    def on_mount(self) -> None:
        arg = sys.argv[1] if len(sys.argv) > 1 else "default"
        if arg == "Default":
            self.player = mpv.MPV(loop_file='inf', config=True) # instantiates player object with enabled loop_file option
        elif arg == "Nonloop":
            self.player = mpv.MPV(loop_file='no', config=True) # instantiates player object with disabled loop_file option
        elif arg == "Nonconf":
            self.player = mpv.MPV(loop_file='inf', config=False) # instantiates player object with disabled config
        elif arg == "Noopt":
            self.player = mpv.MPV() # instanties player object without any options
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
        search_text = event.value.lower() # saves input to search case-insensitive
        all_buttons = self.query(Button) 
        for button in all_buttons:
            button_text = str(button.label).lower()
            if search_text in button_text:
                button.styles.display = "block" # Keeps button visible if it's label matches woth query
            else:
                button.styles.display = "none" # Hides button if it's label doesn't match the query 

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
            self.update_nowplaying("None") # sets the "now_playing" label to "None" when player stoped
        else:
            self.playing = True
            self.player.play(track_name)
            self.update_nowplaying(track_name) # sets "now_playing" label to track name

    def action_pause_play(self) -> None:
        """toggle pause"""
        if hasattr(self, 'player'):
            self.player.pause = not self.player.pause

    def on_unmount(self) -> None:
        """terminates player after unmount"""
        if hasattr(self, 'player'):
            self.player.terminate() 

if __name__ == "__main__":
    osname = platform.system() # detects OS to get music directory
    if osname == "Linux": # gets music directory on linux
        home = os.environ["HOME"]
        music_dir = os.path.join(home, "Music")
    elif osname == "Windows": # gets music directory on windows
        user_profile = os.environ["USERPROFILE"] 
        music_dir = os.path.join(user_profile, "Music") 
    elif osname == "Darwin": # gets music directory on MacOS
        home = os.environ["HOME"]
        music_dir = os.path.join(home, "Music")
    os.chdir(music_dir) # moves to music directory
    PlayerApp().run()
