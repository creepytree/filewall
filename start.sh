#!/bin/bash

cd "$(dirname "$0")"

# default vals
DATA_DIR_ARG="${DATA_DIR:-}"
BASE_PATH_ARG="${BASE_PATH:-}"
LOGIN_USER_ARG="${LOGIN_USER:-}"
LOGIN_PW_ARG="${LOGIN_PW:-}"
LOGIN_TIMEOUT_ARG="${LOGIN_TIMEOUT:-}"

usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --data-dir PATH     Folder shown in the gallery"
    echo "  -b, --base-path PATH    Public base path for hosting under a subdirectory"
    echo "  -u, --login-user USER   Enable login with this username"
    echo "  -w, --login-pw PW       Password for the login user"
    echo "  -t, --login-timeout MIN Session idle timeout in minutes (default: 60)"
    echo "      --help              Show this help message"
    echo ""
    echo "Run without options to start filewall without login."
}

# args
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--data-dir)
            DATA_DIR_ARG="$2"
            shift 2
            ;;
        -b|--base-path)
            BASE_PATH_ARG="$2"
            shift 2
            ;;
        -u|--login-user)
            LOGIN_USER_ARG="$2"
            shift 2
            ;;
        -w|--login-pw)
            LOGIN_PW_ARG="$2"
            shift 2
            ;;
        -t|--login-timeout)
            LOGIN_TIMEOUT_ARG="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

if [ -n "$DATA_DIR_ARG" ]; then
    export DATA_DIR="$DATA_DIR_ARG"
fi

if [ -n "$BASE_PATH_ARG" ]; then
    export BASE_PATH="$BASE_PATH_ARG"
fi

# default debug, overriden by LOG_LEVEL
export LOG_LEVEL="${LOG_LEVEL:-DEBUG}"

# enable login if user and pw
if [ -n "$LOGIN_USER_ARG" ] && [ -n "$LOGIN_PW_ARG" ]; then
    export LOGIN="true"
    export LOGIN_USER="$LOGIN_USER_ARG"
    export LOGIN_PW="$LOGIN_PW_ARG"
    if [ -n "$LOGIN_TIMEOUT_ARG" ]; then
        export LOGIN_TIMEOUT="$LOGIN_TIMEOUT_ARG"
    fi
elif [ -n "$LOGIN_USER_ARG" ] || [ -n "$LOGIN_PW_ARG" ]; then
    echo "Error: --login-user and --login-pw must be provided together"
    exit 1
fi

echo "Starting filewall"
if [ -n "$DATA_DIR" ]; then
    echo "Data dir: $DATA_DIR"
fi
if [ -n "$BASE_PATH" ]; then
    echo "Base path: $BASE_PATH"
fi
if [ "$LOGIN" = "true" ]; then
    echo "Login: enabled (user: $LOGIN_USER)"
fi
echo ""

# create venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
else
    source venv/bin/activate
fi

pip install -e .

exec filewall --host 0.0.0.0 --port 5000
