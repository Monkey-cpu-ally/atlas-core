use std::fs;
use std::path::Path;

const FALLBACK_ICON: &[u8] = &[
    137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82,
    0, 0, 0, 32, 0, 0, 0, 32, 8, 6, 0, 0, 0, 115, 122, 122, 244,
    0, 0, 0, 49, 73, 68, 65, 84, 120, 218, 237, 206, 49, 1, 0, 48,
    8, 0, 32, 93, 1, 11, 120, 219, 191, 225, 140, 225, 3, 9, 200,
    234, 249, 113, 232, 197, 49, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 129, 5, 58, 196, 1, 144, 106, 80, 251, 201, 0, 0,
    0, 0, 73, 69, 78, 68, 174, 66, 96, 130,
];

fn ensure_icon() {
    let icon_path = Path::new("icons/icon.png");
    if icon_path.exists() {
        return;
    }

    if let Some(parent) = icon_path.parent() {
        fs::create_dir_all(parent).expect("failed to create Tauri icon directory");
    }
    fs::write(icon_path, FALLBACK_ICON).expect("failed to write fallback Tauri icon");
}

fn main() {
    ensure_icon();
    tauri_build::build()
}
