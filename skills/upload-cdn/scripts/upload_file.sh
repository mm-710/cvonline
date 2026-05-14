#!/bin/bash
set -euo pipefail
#
# upload-file.sh - Upload a file to CDN and return the URL
#
# Usage:
#   bash upload-file.sh <file_path>                 # 上传到内网（默认）
#   bash upload-file.sh --public <file_path>        # 上传到外网
#   bash upload-file.sh --type <mime> <file_path>   # 指定 MIME 类型
#
# Options:
#   --public          上传到外网 CDN（type=7），默认上传到内网（type=2）
#   --type <mime>     指定文件 MIME 类型，默认自动检测
#   -h, --help        显示帮助信息
#
# Output:
#   成功时输出 CDN URL
#   失败时以非零状态码退出并输出错误信息
#
# Examples:
#   bash upload-file.sh ~/Documents/report.pdf
#   bash upload-file.sh --public ~/Pictures/screenshot.png
#   bash upload-file.sh --type application/json ~/config.json
#

set -e

# =============================================================================
# Constants
# =============================================================================

UPLOAD_API_URL="https://design-out.staging.kuaishou.com/private-api/common/upload-file"

# Upload type:
#   2 = 内网 (internal, default)
#   7 = 外网 (public)
UPLOAD_TYPE="2"

# =============================================================================
# Functions
# =============================================================================

print_usage() {
    echo "Usage: $0 [OPTIONS] <file_path>"
    echo ""
    echo "Upload a file to CDN and return the URL."
    echo ""
    echo "Options:"
    echo "  --public            Upload to public CDN (外网), default is internal (内网)"
    echo "  --type <mime_type>  Specify MIME type (auto-detected by default)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 ~/Documents/report.pdf"
    echo "  $0 --public ~/Pictures/screenshot.png"
    echo "  $0 --type application/json ~/config.json"
    echo "  $0 --public --type application/zip ~/archive.zip"
    echo ""
    echo "Supported file types (auto-detected):"
    echo "  Images:     .png .jpg .jpeg .gif .webp .svg .ico"
    echo "  Documents:  .pdf .doc .docx .xls .xlsx .ppt .pptx"
    echo "  Archives:   .zip .tar.gz .tar .gz .rar"
    echo "  Text:       .txt .md .json .yaml .yml .xml .csv .log"
    echo "  Code:       .js .ts .py .sh .html .css"
    echo "  Others:     auto-detected as application/octet-stream"
}

cleanup() {
    # Nothing to clean up for direct file upload
    :
}

# Detect MIME type based on file extension
detect_mime_type() {
    local file="$1"
    local ext="${file##*.}"
    ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

    case "$ext" in
        # Images
        png)  echo "image/png" ;;
        jpg|jpeg) echo "image/jpeg" ;;
        gif)  echo "image/gif" ;;
        webp) echo "image/webp" ;;
        svg)  echo "image/svg+xml" ;;
        ico)  echo "image/x-icon" ;;
        bmp)  echo "image/bmp" ;;
        # Documents
        pdf)  echo "application/pdf" ;;
        doc)  echo "application/msword" ;;
        docx) echo "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ;;
        xls)  echo "application/vnd.ms-excel" ;;
        xlsx) echo "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ;;
        ppt)  echo "application/vnd.ms-powerpoint" ;;
        pptx) echo "application/vnd.openxmlformats-officedocument.presentationml.presentation" ;;
        # Archives
        zip)  echo "application/zip" ;;
        tar)  echo "application/x-tar" ;;
        gz)   echo "application/gzip" ;;
        rar)  echo "application/x-rar-compressed" ;;
        # Text / Code
        txt)  echo "text/plain" ;;
        md)   echo "text/markdown" ;;
        json) echo "application/json" ;;
        yaml|yml) echo "application/x-yaml" ;;
        xml)  echo "application/xml" ;;
        csv)  echo "text/csv" ;;
        html|htm) echo "text/html" ;;
        css)  echo "text/css" ;;
        js)   echo "application/javascript" ;;
        ts)   echo "application/typescript" ;;
        py)   echo "text/x-python" ;;
        sh)   echo "application/x-sh" ;;
        log)  echo "text/plain" ;;
        # Default
        *)    echo "application/octet-stream" ;;
    esac
}

# Format file size to human readable
format_size() {
    local size="$1"
    if [[ $size -lt 1024 ]]; then
        echo "${size} B"
    elif [[ $size -lt $((1024 * 1024)) ]]; then
        echo "$((size / 1024)) KB"
    else
        echo "$((size / 1024 / 1024)) MB"
    fi
}

# =============================================================================
# Main
# =============================================================================

trap cleanup EXIT

# Parse arguments
FILE_PATH=""
IS_PUBLIC="false"
MIME_TYPE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --public)
            IS_PUBLIC="true"
            UPLOAD_TYPE="7"
            shift
            ;;
        --type)
            if [[ -z "$2" ]]; then
                echo "Error: --type requires a MIME type argument" >&2
                exit 1
            fi
            MIME_TYPE="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        -*)
            echo "Error: Unknown option: $1" >&2
            print_usage
            exit 1
            ;;
        *)
            if [[ -z "$FILE_PATH" ]]; then
                FILE_PATH="$1"
            else
                echo "Error: Multiple file paths provided. Only one file can be uploaded at a time." >&2
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate file path
if [[ -z "$FILE_PATH" ]]; then
    echo "Error: No file path provided" >&2
    print_usage
    exit 1
fi

# Expand ~ to home directory
FILE_PATH="${FILE_PATH/#\~/$HOME}"

# Check if file exists
if [[ ! -f "$FILE_PATH" ]]; then
    echo "Error: File not found: $FILE_PATH" >&2
    exit 1
fi

# Get file info
FILE_NAME=$(basename "$FILE_PATH")
FILE_SIZE=$(wc -c < "$FILE_PATH" | tr -d ' ')
FILE_SIZE_HUMAN=$(format_size "$FILE_SIZE")

# Auto-detect MIME type if not specified
if [[ -z "$MIME_TYPE" ]]; then
    MIME_TYPE=$(detect_mime_type "$FILE_PATH")
fi

# Print upload info
echo "============================================================"
echo "File Upload"
echo "============================================================"
echo ""
echo "[1/2] Preparing upload..."
echo "      File:     $FILE_NAME"
echo "      Size:     $FILE_SIZE_HUMAN"
echo "      Type:     $MIME_TYPE"
echo "      Path:     $FILE_PATH"
if [[ "$IS_PUBLIC" == "true" ]]; then
    echo "      Target:   外网 (public CDN)"
else
    echo "      Target:   内网 (internal CDN)"
fi
echo ""
echo "[2/2] Uploading to CDN..."

# Upload using curl
RESPONSE=$(curl -s -X POST "$UPLOAD_API_URL" \
    -F "file=@${FILE_PATH};type=${MIME_TYPE}" \
    -F "uploadType=$UPLOAD_TYPE")

# Check curl exit code
if [[ $? -ne 0 ]]; then
    echo "Error: Network request failed. Please check your connection." >&2
    exit 1
fi

# Parse response
CODE=$(echo "$RESPONSE" | grep -o '"code":[0-9]*' | grep -o '[0-9]*')
CDN_URL=$(echo "$RESPONSE" | grep -o '"data":"[^"]*"' | sed 's/"data":"//;s/"$//')

# Handle upload error
if [[ "$CODE" != "1" ]]; then
    ERROR_MSG=$(echo "$RESPONSE" | grep -o '"errorMsg":"[^"]*"' | sed 's/"errorMsg":"//;s/"$//')
    if [[ -n "$ERROR_MSG" ]]; then
        echo "Error: Upload failed - $ERROR_MSG" >&2
    else
        echo "Error: Upload failed (code: $CODE)" >&2
        echo "       Full response: $RESPONSE" >&2
    fi
    exit 1
fi

# Handle missing URL
if [[ -z "$CDN_URL" ]]; then
    echo "Error: Upload succeeded but no URL returned." >&2
    echo "       Full response: $RESPONSE" >&2
    exit 1
fi

# Print success result
echo "      Upload successful!"
echo ""
echo "============================================================"
echo "Upload Complete!"
echo "============================================================"
echo ""
echo "File:    $FILE_NAME"
echo "CDN URL: $CDN_URL"
echo ""
if [[ "$IS_PUBLIC" == "true" ]]; then
    echo "Note: This file is on public CDN and accessible to anyone."
else
    echo "Note: This file is on internal CDN (内网). Use --public for external access."
fi
echo "============================================================"

# Output CDN URL as the last line for easy parsing
echo ""
echo '<a href="'$CDN_URL'" target="_blank">🔗 点击这里访问</a>'
