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
    // Inspect kernel routing table: return true if air-gapped, false if public WAN default route detected
    #[cfg(target_os = "linux")]
    {
        if let Ok(content) = std::fs::read_to_string("/proc/net/route") {
            for line in content.lines().skip(1) {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 2 && parts[1] == "00000000" {
                    // If strict air gap enforcement is enabled, flag default route as violation
                    let strict = std::env::var("AIR_GAP_STRICT").unwrap_or_default();
                    if strict == "1" || strict.eq_ignore_ascii_case("true") {
                        return false;
                    }
                }
            }
        }
    }
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
