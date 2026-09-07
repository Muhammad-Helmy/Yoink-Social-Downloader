/**
 * Yoink Social — Frontend Internationalization (i18n)
 * Supported: en (English - Default), id (Indonesian), es (Spanish)
 */

const I18N = {
  currentLang: "en",

  translations: {
    en: {
      // Brand & Navigation
      platforms: "PLATFORMS",
      system: "SYSTEM",
      active_tasks: "Active Tasks",
      history: "History",
      settings: "Settings",
      about: "About",
      made_by: "Made by",

      // Platform Header & Input
      open_folder: "Open Folder",
      paste: "Paste",
      clear: "Clear",
      analyze_media: "Analyze Media",
      analyzing: "Analyzing...",

      // Active Downloads & History
      no_active_downloads: "No downloads currently in progress.",
      active_download_title: "Active Media Download",
      history_title: "Download History",
      history_desc: "Showing up to your last 10 completed downloads.",
      no_history: "No downloaded files yet. Completed items will appear here.",
      clear_history: "Clear History",
      open_file: "Open File",
      open_folder_action: "Folder",
      toggle_logs: "Toggle Logs Panel",
      queue_title: "Universal Execution Queue",
      in_queue: "In Queue",
      waiting_turn: "Waiting for turn in queue...",
      queue_pos: "Queue #{pos}",
      cancel_queue: "Remove",
      private_modal_title: "🔒 Private Content Notice",
      private_modal_desc: "This media is located in a private group or private account and cannot be accessed publicly without private authentication. Please try another public post or video link.",
      understood: "Understood, Try Another Link",

      platforms_info: {
        youtube: {
          title: "YouTube Downloader",
          sub: "Download videos in maximum available resolution or extract pristine MP3 audio.",
          placeholder: "Paste YouTube video or shorts link here..."
        },
        tiktok: {
          title: "TikTok Downloader",
          sub: "Download TikTok HD videos (no-watermark prioritized), audio, or photo slides.",
          placeholder: "Paste TikTok video link (vt.tiktok.com or tiktok.com/@...) here..."
        },
        instagram: {
          title: "Instagram Downloader",
          sub: "Download Reels, feed videos, photo posts, and carousels in top quality.",
          placeholder: "Paste Instagram post or reels link here..."
        },
        facebook: {
          title: "Facebook Downloader",
          sub: "Download public Facebook videos, reels, and photos in highest quality.",
          placeholder: "Paste Facebook video or post link here..."
        }
      },

      // Preview & Options
      format_label: "Media Format:",
      format_video: "Video (MP4)",
      format_audio: "Audio (MP3)",
      format_image: "Images (JPG/PNG)",
      quality_label: "Resolution Quality:",
      quality_hint_video: "Highest stream available directly from platform servers without re-encoding.",
      quality_hint_audio: "Extract high-bitrate MP3 audio (192-320 kbps) via FFmpeg.",
      quality_hint_image: "Download original high-resolution photos/carousel.",
      download_now: "Download Now",

      // Progress & Finished
      downloading_stream: "Downloading media stream...",
      cancel: "Cancel",
      speed: "Speed",
      eta_remaining: "ETA",
      download_complete_title: "Download Successfully Saved!",
      open_file: "Open File",

      // Settings
      settings_title: "Settings & Preferences",
      language_section: "Display Language",
      language_desc: "Choose the interface and log notification language.",
      hardware_section: "Hardware Acceleration (GPU NVENC)",
      hardware_desc: "Utilize NVIDIA GPU hardware encoder for ultra-fast processing.",
      hw_auto: "Auto (Recommended — Uses NVIDIA NVENC if detected)",
      hw_gpu: "GPU (Force NVIDIA NVENC)",
      hw_cpu: "CPU (Standard Software Processing)",
      hw_detected: "Detected Hardware:",
      hw_nvenc_ready: "NVIDIA NVENC Hardware Acceleration Ready",
      hw_cpu_only: "Software CPU Mode",
      download_locations: "Default Download Locations",
      download_locations_desc: "Set separate destination folders for each supported platform.",
      change: "Change",
      open: "Open",
      extractor_maint: "Extractor Maintenance (yt-dlp)",
      extractor_desc: "Platforms regularly update their internal layouts. Keep yt-dlp up to date.",
      installed_version: "Installed yt-dlp version:",
      check_updates: "Check for Updates",
      update_now: "Update Now",

      // About
      about_title: "Yoink Social",
      about_version: "Version 1.0 (Windows x64)",
      about_creator: "Crafted specifically for personal use by Heru.",
      quality_reality_title: "Realistic Quality Disclosure",
      quality_reality_text1: "All media on YouTube, TikTok, Instagram, and Facebook is already compressed (H.264/H.265/VP9) by platform servers upon upload. Raw uncompressed files do not exist on CDNs.",
      quality_reality_text2: "Yoink Social Promise: This app downloads the highest quality stream directly available from server CDNs without additional re-encoding or compression.",
      defender_title: "Windows Defender Notice",
      defender_text: "Because this app is tailored for personal use without a commercial code-signing certificate, Windows SmartScreen may show a prompt on first launch.",
      defender_step1: "1. Click More info.",
      defender_step2: "2. Click Run anyway.",

      // Logs & Footer
      log_title: "Activity Logs & System Status",
      copy: "Copy",
      clean: "Clear",
      messages_count: "messages",
      system_normal: "System Normal • Hardware Ready",
      made_by_heru: "Yoink Social v1.0 • Made by Heru"
    },

    id: {
      platforms: "PLATFORM",
      system: "SISTEM",
      active_tasks: "Tugas Aktif",
      history: "Riwayat",
      settings: "Pengaturan",
      about: "Tentang",
      made_by: "Dibuat oleh",

      open_folder: "Buka Folder",
      paste: "Tempel",
      clear: "Bersihkan",
      analyze_media: "Analisis Video",
      analyzing: "Menganalisis...",

      no_active_downloads: "Tidak ada unduhan yang sedang berjalan.",
      active_download_title: "Unduhan Media Berjalan",
      history_title: "Riwayat Unduhan",
      history_desc: "Menampilkan hingga 10 berkas yang baru saja selesai diunduh.",
      no_history: "Belum ada berkas unduhan. Unduhan yang selesai akan muncul di sini.",
      clear_history: "Hapus Riwayat",
      open_file: "Buka File",
      open_folder_action: "Folder",
      toggle_logs: "Buka/Tutup Panel Log",
      queue_title: "Antrean Unduhan Universal",
      in_queue: "Dalam Antrean",
      waiting_turn: "Menunggu giliran eksekusi antrean...",
      queue_pos: "Antrean #{pos}",
      cancel_queue: "Batal",
      private_modal_title: "🔒 Konten Grup / Profil Privat",
      private_modal_desc: "Konten media ini berada di dalam grup atau akun privat Facebook dan tidak dapat diakses secara publik. Silakan gunakan link postingan atau video publik lainnya.",
      understood: "Mengerti, Coba Link Lain",

      platforms_info: {
        youtube: {
          title: "YouTube Downloader",
          sub: "Unduh video resolusi maksimal atau ekstrak audio MP3 sejernih sumber.",
          placeholder: "Tempel link video atau shorts YouTube di sini..."
        },
        tiktok: {
          title: "TikTok Downloader",
          sub: "Unduh video TikTok HD (prioritas tanpa watermark), audio, atau foto slide.",
          placeholder: "Tempel link video TikTok (vt.tiktok.com atau tiktok.com/@...) di sini..."
        },
        instagram: {
          title: "Instagram Downloader",
          sub: "Unduh Reels, video Feed, postingan foto, dan carousel kualitas terbaik.",
          placeholder: "Tempel link Reels atau postingan Instagram di sini..."
        },
        facebook: {
          title: "Facebook Downloader",
          sub: "Unduh video Reels, video publik, dan foto Facebook resolusi maksimal.",
          placeholder: "Tempel link video atau postingan Facebook di sini..."
        }
      },

      format_label: "Format Media:",
      format_video: "Video (MP4)",
      format_audio: "Audio (MP3)",
      format_image: "Gambar (JPG/PNG)",
      quality_label: "Kualitas Resolusi:",
      quality_hint_video: "Kualitas tertinggi yang tersedia langsung di server tanpa re-encode.",
      quality_hint_audio: "Ekstrak audio MP3 berkualitas tinggi (192-320 kbps) via FFmpeg.",
      quality_hint_image: "Unduh foto atau carousel resolusi original.",
      download_now: "Mulai Mengunduh",

      downloading_stream: "Mengunduh stream media...",
      cancel: "Batalkan",
      speed: "Kecepatan",
      eta_remaining: "Sisa",
      download_complete_title: "Unduhan Berhasil Disimpan!",
      open_file: "Buka File",

      settings_title: "Pengaturan & Preferensi",
      language_section: "Bahasa Tampilan",
      language_desc: "Pilih bahasa antarmuka dan notifikasi log sistem.",
      hardware_section: "Akselerasi Hardware (GPU NVENC)",
      hardware_desc: "Gunakan encoder hardware NVIDIA GPU untuk pemrosesan super cepat.",
      hw_auto: "Otomatis (Rekomendasi — Gunakan NVIDIA NVENC jika terdeteksi)",
      hw_gpu: "GPU (Paksa NVIDIA NVENC)",
      hw_cpu: "CPU (Pemrosesan Standar Software)",
      hw_detected: "Perangkat Terdeteksi:",
      hw_nvenc_ready: "Akselerasi Hardware NVIDIA NVENC Aktif",
      hw_cpu_only: "Mode Standar CPU",
      download_locations: "Lokasi Folder Unduhan Default",
      download_locations_desc: "Atur folder tujuan penyimpanan terpisah untuk setiap platform.",
      change: "Ubah",
      open: "Buka",
      extractor_maint: "Pemeliharaan Extractor (yt-dlp)",
      extractor_desc: "Platform sosial media rutin mengubah struktur halaman. Pastikan extractor selalu mutakhir.",
      installed_version: "Versi yt-dlp terpasang:",
      check_updates: "Cek Update yt-dlp",
      update_now: "Update Sekarang",

      about_title: "Yoink Social",
      about_version: "Versi 1.0 (Windows x64)",
      about_creator: "Dirancang khusus untuk kebutuhan personal oleh Heru.",
      quality_reality_title: "Batasan Realistis Kualitas Media",
      quality_reality_text1: "Semua media di YouTube, TikTok, Instagram, dan Facebook sudah dikompresi (H.264/H.265/VP9) oleh server saat diunggah. Tidak ada file uncompressed mentah di server.",
      quality_reality_text2: "Komitmen Yoink Social: Mengunduh stream kualitas tertinggi yang tersedia langsung di server CDN tanpa re-encode atau kompresi tambahan.",
      defender_title: "Panduan Keamanan Windows Defender",
      defender_text: "Karena aplikasi ini dibuat untuk penggunaan pribadi tanpa sertifikat digital berbayar, Windows SmartScreen mungkin menampilkan pemberitahuan saat pertama kali dibuka.",
      defender_step1: "1. Klik tautan More info (Informasi selengkapnya).",
      defender_step2: "2. Klik tombol Run anyway (Tetap jalankan).",

      log_title: "Log Aktivitas & Status Sistem",
      copy: "Salin",
      clean: "Bersihkan",
      messages_count: "pesan",
      system_normal: "Sistem Normal • Hardware Siap",
      made_by_heru: "Yoink Social v1.0 • Made by Heru"
    },

    es: {
      platforms: "PLATAFORMAS",
      system: "SISTEMA",
      active_tasks: "Tareas Activas",
      history: "Historial",
      settings: "Ajustes",
      about: "Acerca de",
      made_by: "Hecho por",

      open_folder: "Abrir Carpeta",
      paste: "Pegar",
      clear: "Limpiar",
      analyze_media: "Analizar Medios",
      analyzing: "Analizando...",

      no_active_downloads: "No hay descargas activas en curso.",
      active_download_title: "Descarga de Medios Activa",
      history_title: "Historial de Descargas",
      history_desc: "Mostrando hasta las últimas 10 descargas completadas.",
      no_history: "Aún no hay archivos descargados. Los elementos completados aparecerán aquí.",
      clear_history: "Borrar Historial",
      open_file: "Abrir Archivo",
      open_folder_action: "Carpeta",
      toggle_logs: "Alternar Panel de Registro",
      queue_title: "Cola Universal de Descargas",
      in_queue: "En Cola",
      waiting_turn: "Esperando turno en la cola...",
      queue_pos: "Cola #{pos}",
      cancel_queue: "Quitar",
      private_modal_title: "🔒 Aviso de Contenido Privado",
      private_modal_desc: "Este medio de Facebook se encuentra dentro de un grupo privado o cuenta privada y no se puede acceder públicamente. Pruebe con otro enlace público.",
      understood: "Entendido, Probar Otro Enlace",

      platforms_info: {
        youtube: {
          title: "YouTube Downloader",
          sub: "Descargue videos en la máxima resolución disponible o extraiga audio MP3 nítido.",
          placeholder: "Pegue el enlace de YouTube aquí..."
        },
        tiktok: {
          title: "TikTok Downloader",
          sub: "Descargue videos de TikTok HD (sin marca de agua), audio o fotos.",
          placeholder: "Pegue el enlace de TikTok aquí..."
        },
        instagram: {
          title: "Instagram Downloader",
          sub: "Descargue Reels, videos, publicaciones de fotos y carruseles en alta calidad.",
          placeholder: "Pegue el enlace de Instagram aquí..."
        },
        facebook: {
          title: "Facebook Downloader",
          sub: "Descargue videos públicos, reels y fotos de Facebook en máxima resolución.",
          placeholder: "Pegue el enlace de Facebook aquí..."
        }
      },

      format_label: "Formato de Medios:",
      format_video: "Video (MP4)",
      format_audio: "Audio (MP3)",
      format_image: "Imágenes (JPG/PNG)",
      quality_label: "Calidad de Resolución:",
      quality_hint_video: "Máxima calidad disponible directamente desde los servidores sin recodificación.",
      quality_hint_audio: "Extraiga audio MP3 de alta calidad (192-320 kbps) mediante FFmpeg.",
      quality_hint_image: "Descargue fotos o carruseles originales de alta resolución.",
      download_now: "Descargar Ahora",

      downloading_stream: "Descargando medios...",
      cancel: "Cancelar",
      speed: "Velocidad",
      eta_remaining: "Restante",
      download_complete_title: "¡Descarga Guardada con Éxito!",
      open_file: "Abrir Archivo",

      settings_title: "Ajustes y Preferencias",
      language_section: "Idioma de Interfaz",
      language_desc: "Seleccione el idioma de la interfaz y los registros.",
      hardware_section: "Aceleración de Hardware (GPU NVENC)",
      hardware_desc: "Utilice el codificador de hardware NVIDIA GPU para un procesamiento ultra rápido.",
      hw_auto: "Automático (Recomendado — Usa NVIDIA NVENC si está disponible)",
      hw_gpu: "GPU (Forzar NVIDIA NVENC)",
      hw_cpu: "CPU (Modo Estándar por Software)",
      hw_detected: "Hardware Detectado:",
      hw_nvenc_ready: "Aceleración NVIDIA NVENC Lista",
      hw_cpu_only: "Modo CPU Estándar",
      download_locations: "Ubicaciones de Descarga Predeterminadas",
      download_locations_desc: "Configure carpetas de destino separadas para cada plataforma.",
      change: "Cambiar",
      open: "Abrir",
      extractor_maint: "Mantenimiento del Extractor (yt-dlp)",
      extractor_desc: "Mantenga actualizado el extractor de medios para compatibilidad constante.",
      installed_version: "Versión de yt-dlp instalada:",
      check_updates: "Buscar Actualizaciones",
      update_now: "Actualizar Ahora",

      about_title: "Yoink Social",
      about_version: "Versión 1.0 (Windows x64)",
      about_creator: "Diseñado especialmente para uso personal por Heru.",
      quality_reality_title: "Aviso de Calidad Real",
      quality_reality_text1: "Todos los medios en las redes sociales ya están comprimidos por los servidores al subirse.",
      quality_reality_text2: "Promesa de Yoink Social: Descarga la transmisión de mayor calidad disponible directamente del servidor sin pérdida adicional.",
      defender_title: "Aviso de Windows Defender",
      defender_text: "Al ser una aplicación personal sin certificado comercial, Windows SmartScreen puede mostrar una advertencia en la primera apertura.",
      defender_step1: "1. Haga clic en Más información.",
      defender_step2: "2. Haga clic en Ejecutar de todos modos.",

      log_title: "Registro de Actividad y Estado del Sistema",
      copy: "Copiar",
      clean: "Limpiar",
      messages_count: "mensajes",
      system_normal: "Sistema Normal • Hardware Listo",
      made_by_heru: "Yoink Social v1.0 • Hecho por Heru"
    }
  },

  t(key) {
    const lang = this.currentLang || "en";
    const dict = this.translations[lang] || this.translations["en"];
    return dict[key] !== undefined ? dict[key] : (this.translations["en"][key] || key);
  },

  setLanguage(lang) {
    if (this.translations[lang]) {
      this.currentLang = lang;
    }
  }
};
