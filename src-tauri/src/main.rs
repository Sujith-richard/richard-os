#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
fn main() {
    // Start the Richard OS API server before opening the UI (desktop-style)
    #[cfg(target_os = "linux")]
    let _ = std::process::Command::new("sh")
        .arg("-c")
        .arg("cd .. && (.venv/bin/python3 -m uvicorn scripts.server:app --port 8000 >/tmp/richard-api.log 2>&1 &)")
        .spawn();
    #[cfg(target_os = "windows")]
    let _ = std::process::Command::new("cmd")
        .args(&["/C", "cd .. && .venv\\Scripts\\python.exe -m uvicorn scripts.server:app --port 8000"])
        .spawn();
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running Richard OS Studio");
}
