"""
Windows volume control utilities using pycaw.
Provides functions to mute/unmute and get/set volume state.
"""

from ctypes import POINTER, cast
from typing import Any, Optional

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Cache the volume interface to avoid COM cleanup issues
_cached_volume_interface: Optional[Any] = None


def get_volume_interface() -> Any:
    """Get the audio endpoint volume interface (cached to avoid COM cleanup errors)."""
    global _cached_volume_interface
    if _cached_volume_interface is not None:
        return _cached_volume_interface

    devices = AudioUtilities.GetSpeakers()
    # Handle both old and new pycaw API
    if hasattr(devices, "Activate"):
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    else:
        # Newer pycaw returns AudioDevice wrapper, need to get underlying device
        interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    _cached_volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
    return _cached_volume_interface


def get_mute_state() -> bool:
    """Check if the system audio is currently muted."""
    volume = get_volume_interface()
    return volume.GetMute() == 1


def set_mute_state(mute: bool) -> None:
    """Set the system mute state."""
    volume = get_volume_interface()
    volume.SetMute(1 if mute else 0, None)


class VolumeMuter:
    """
    Context manager to temporarily mute the PC volume during recording.
    Restores the previous mute state when exiting.
    """

    def __init__(self):
        self._was_muted: bool = False

    def __enter__(self):
        """Mute the volume, remembering if it was already muted."""
        self._was_muted = get_mute_state()
        if not self._was_muted:
            set_mute_state(True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore the previous mute state."""
        if not self._was_muted:
            set_mute_state(False)
        return False
