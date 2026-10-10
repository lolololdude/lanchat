#!/usr/bin/env python3
"""lanchat - minimal terminal chat between two machines on the same network.

Usage:
  lanchat                      interactive menu
  lanchat host [port]          wait for a connection (default port 5000)
  lanchat connect IP[:PORT]    connect to a host
  lanchat connect IP PORT

In chat: type a message and press Enter. Type /quit to leave.
"""
import os
import socket
import sys
import threading

DEFAULT_PORT = 5000
__version__ = "1.0.0"

# Enable ANSI escape codes on Windows terminals
if os.name == "nt":
    os.system("")

stop = threading.Event()


def local_ips():
    """Best-effort list of this machine's LAN addresses."""
    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))  # no packets are actually sent
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    ips.discard("127.0.0.1")
    return sorted(ips) or ["127.0.0.1"]


def parse_port(text):
    port = int(text)
    if not 1 <= port <= 65535:
        raise ValueError
    return port


def receiver(conn, peer_name):
    """Print incoming lines until the peer disconnects."""
    try:
        with conn.makefile("r", encoding="utf-8", errors="replace", newline="\n") as f:
            for line in f:
                msg = line.rstrip("\r\n")
                # clear the current input line, print message, redraw prompt
                sys.stdout.write(f"\r\033[K{peer_name}: {msg}\n> ")
                sys.stdout.flush()
    except OSError:
        pass
    if not stop.is_set():
        sys.stdout.write(f"\r\033[K* {peer_name} disconnected. Press Enter to exit.\n")
        sys.stdout.flush()
    stop.set()


def chat(conn, my_name):
    # exchange names (first line each way)
    conn.sendall((my_name + "\n").encode("utf-8"))
    f = conn.makefile("r", encoding="utf-8", errors="replace", newline="\n")
    peer_name = (f.readline().strip() or "peer")[:32]
    f.close()
    print(f"* Connected with {peer_name}. Type /quit to leave.\n")

    threading.Thread(target=receiver, args=(conn, peer_name), daemon=True).start()
    try:
        while not stop.is_set():
            try:
                text = input("> ")
            except EOFError:
                break
            if stop.is_set():
                break
            if text.strip() == "/quit":
                break
            if not text:
                continue
            conn.sendall((text + "\n").encode("utf-8"))
    except (KeyboardInterrupt, OSError):
        pass
    finally:
        stop.set()
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        conn.close()
        print("\n* Chat ended.")


def host(port, name):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("0.0.0.0", port))
    except OSError as e:
        sys.exit(f"Could not listen on port {port}: {e}")
    srv.listen(1)
    print(f"Waiting for a connection on port {port}")
    print("Tell the other person to connect to one of:")
    for ip in local_ips():
        print(f"  {ip}:{port}")
    print("(Ctrl+C to cancel)")
    try:
        conn, addr = srv.accept()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    finally:
        srv.close()
    print(f"* Incoming connection from {addr[0]}")
    chat(conn, name)


def connect(ip, port, name):
    print(f"Connecting to {ip}:{port} ...")
    try:
        conn = socket.create_connection((ip, port), timeout=10)
    except (OSError, socket.timeout) as e:
        sys.exit(f"Could not connect: {e}")
    conn.settimeout(None)
    chat(conn, name)


def ask_name():
    default = os.environ.get("USER") or os.environ.get("USERNAME") or "me"
    try:
        n = input(f"Your name [{default}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit()
    return (n or default)[:32]


def split_addr(text):
    if ":" in text:
        ip, p = text.rsplit(":", 1)
        return ip, parse_port(p)
    return text, DEFAULT_PORT


def interactive():
    print(f"lanchat {__version__}\n  1) Host (wait for someone)\n  2) Connect to someone")
    try:
        choice = input("Choose 1 or 2: ").strip()
        if choice == "1":
            p = input(f"Port [{DEFAULT_PORT}]: ").strip()
            port = parse_port(p) if p else DEFAULT_PORT
            host(port, ask_name())
        elif choice == "2":
            ip = input("IP address: ").strip()
            p = input(f"Port [{DEFAULT_PORT}]: ").strip()
            port = parse_port(p) if p else DEFAULT_PORT
            connect(ip, port, ask_name())
        else:
            sys.exit("Invalid choice.")
    except ValueError:
        sys.exit("Invalid port (must be 1-65535).")
    except (EOFError, KeyboardInterrupt):
        print()


def main():
    args = sys.argv[1:]
    if not args:
        return interactive()
    if args[0] in ("-h", "--help", "help"):
        print(__doc__)
        return
    if args[0] in ("-v", "--version"):
        print(__version__)
        return
    try:
        if args[0] == "host":
            port = parse_port(args[1]) if len(args) > 1 else DEFAULT_PORT
            host(port, ask_name())
        elif args[0] == "connect" and len(args) >= 2:
            if len(args) >= 3:
                ip, port = args[1], parse_port(args[2])
            else:
                ip, port = split_addr(args[1])
            connect(ip, port, ask_name())
        else:
            print(__doc__)
    except ValueError:
        sys.exit("Invalid port (must be 1-65535).")


if __name__ == "__main__":
    main()
