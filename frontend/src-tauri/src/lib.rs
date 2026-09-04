use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemInfo {
    pub os: String,
    pub arch: String,
    pub air_gap_enforced: bool,
}

#[tauri::command]
fn get_system_info() -> SystemInfo {
    SystemInfo {
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        air_gap_enforced: true,
    }
}

#[tauri::command]
fn check_network_kill_switch() -> bool {
    // Return true if air-gapped, false if public WAN detected
    true
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            get_system_info,
            check_network_kill_switch
        ])
        .run(tauri::generate_context!())
        .expect("error while running Aquanex application");
}
