import argparse
import logging
import paramiko
import socket
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

def connect_ssh(args, username, key):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=args.host,
            username=username,
            pkey=key,
            timeout=5,
            banner_timeout=5,
            allow_agent=False,
            look_for_keys=False,
        )
        print(f"[+] Valid username found: {username}")
        return True
    except (paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException,
            socket.error, Exception) as e:
        if args.debug:
            logger.debug(f"[{username}] Error: {e}")
        return False
    finally:
        client.close()

def load_key(key_path):
    try:
        return paramiko.RSAKey.from_private_key_file(key_path)
    except paramiko.PasswordRequiredException:
        logger.critical("[-] The private key is encrypted and requires a passphrase.")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Threaded SSH username enumeration using a private key")
    parser.add_argument("--host", required=True, help="Target SSH host")
    parser.add_argument("--key", required=True, help="Path to private key file")
    parser.add_argument("--userlist", required=True, help="Path to username list")
    parser.add_argument("--threads", type=int, default=5, help="Number of threads (default: 5)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if args.debug else logging.CRITICAL
    )

    key = load_key(args.key)

    with open(args.userlist, "r") as f:
        usernames = [line.strip() for line in f if line.strip()]

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        list(tqdm(executor.map(lambda user: connect_ssh(args, user, key), usernames),
                  total=len(usernames), desc="Enumerating"))

if __name__ == "__main__":
    main()

