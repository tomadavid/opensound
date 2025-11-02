import socket
import json

"""
    send mpv commands via socket
"""

def mpv_command(cmd, socket_path):
    with socket.socket(socket.AF_UNIX) as client:
        client.connect(socket_path)
        client.sendall(json.dumps(cmd).encode() + b"\n")

def pause_mpv(socket_path): mpv_command({"command": ["cycle", "pause"]}, socket_path)
def forward_mpv(socket_path): mpv_command({"command": ["seek", 10, "relative"]}, socket_path)
def back_mpv(socket_path): mpv_command({"command": ["seek", -10, "relative"]}, socket_path)
def stop_mpv(socket_path): mpv_command({"command": ["quit"]}, socket_path)