"""command-line entry point for filewall"""

import argparse
import os

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(prog="filewall", description="Super simple web-gallery for a mounted folder")
    parser.add_argument("--host", default="0.0.0.0", help="Interface to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000, help="Port for the server (default: 5000)")
    parser.add_argument("--data-dir", help="Folder shown in the gallery (default: data/ inside the package)")
    parser.add_argument("--base-path", help="Public base path when hosting under a subdirectory")
    parser.add_argument("--login-user", help="Enable login with this username (requires --login-pw)")
    parser.add_argument("--login-pw", help="Password for the login user (requires --login-user)")
    parser.add_argument("--login-timeout", type=int, help="Session idle timeout in minutes (default: 60)")
    parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes (development only)")
    args = parser.parse_args()

    if bool(args.login_user) != bool(args.login_pw):
        parser.error("--login-user and --login-pw must be provided together")

    # the app reads its configuration from the environment on import, so cli
    # options must be exported before uvicorn loads "filewall.app:app"
    if args.data_dir is not None:
        os.environ["DATA_DIR"] = args.data_dir
    if args.base_path is not None:
        os.environ["BASE_PATH"] = args.base_path
    if args.login_user and args.login_pw:
        os.environ["LOGIN"] = "true"
        os.environ["LOGIN_USER"] = args.login_user
        os.environ["LOGIN_PW"] = args.login_pw
        if args.login_timeout is not None:
            os.environ["LOGIN_TIMEOUT"] = str(args.login_timeout)

    uvicorn.run("filewall.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
